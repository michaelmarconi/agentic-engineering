"""Run the seeded-defect review experiment.

Each run copies the corpus product into a fresh workspace, places one case's spec, and runs one
arm's review loop on it, saving every report and the cost of every Claude call:

  A  today's loop: the spec-reviewer agent on Sonnet, fix, review again, up to --cap reviews
  B  three lens reviewers in parallel, then a verifier, all Sonnet; same fix loop and cap
  C  today's loop with the reviewer on Opus
  D  one full review, one fix, then a confirm check of the fixes (arms/confirm.md), no second review

Usage: python3 run.py --out results/<name> [--arms A,B,C] [--cases seeded-01,clean-01] [--runs 3]
"""

import argparse
import json
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CORPUS = HERE / "corpus"
ARMS_DIR = HERE / "arms"
RUBRIC = REPO / "skills" / "spec" / "references" / "rubric.md"
REVIEWER = REPO / "agents" / "spec-reviewer.md"
RUBRIC_IN_WS = ".sdlc/rubric.md"

READ_TOOLS = ["Read", "Glob", "Grep"]
LENSES = ["rubric", "consistency", "misreading"]


def strip_frontmatter(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()


def claude(prompt, cwd, model, tools, system, log, role, edit=False, timeout=1200):
    """One non-interactive Claude call; returns its final text and appends its cost to log."""
    cmd = [
        "claude", "-p", prompt, "--model", model, "--output-format", "json",
        "--tools", ",".join(tools), "--allowedTools", ",".join(tools),
        "--append-system-prompt", system,
        "--strict-mcp-config", "--no-session-persistence", "--setting-sources", "",
    ]
    if edit:
        cmd += ["--permission-mode", "acceptEdits"]
    for attempt in range(3):
        start = time.time()
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            data = {"is_error": True, "result": proc.stdout[-2000:] + proc.stderr[-2000:]}
        if not data.get("is_error"):
            break
        time.sleep(5 * (attempt + 1))
    entry = {
        "role": role, "model": model, "attempts": attempt + 1,
        "cost_usd": data.get("total_cost_usd", 0), "seconds": round(time.time() - start, 1),
        "error": bool(data.get("is_error")),
    }
    with open(log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return data.get("result") or ""


def passed(report):
    return re.search(r"^\s*Result:\s*\**\s*PASS", report, re.M) is not None


def workspace(case, run_dir):
    ws = run_dir / "ws"
    if ws.exists():
        shutil.rmtree(ws)
    shutil.copytree(CORPUS / "product", ws)
    (ws / ".sdlc").mkdir()
    shutil.copy(RUBRIC, ws / RUBRIC_IN_WS)
    meta = json.loads((CORPUS / "cases" / case / "case.json").read_text())
    target = ws / meta["spec_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(CORPUS / "cases" / case / "spec.md", target)
    return ws, meta["spec_path"]


def review_single(ws, spec, model, log, rnd, run_dir):
    system = strip_frontmatter(REVIEWER.read_text()).replace(
        "${CLAUDE_PLUGIN_ROOT}/skills/spec/references/rubric.md", RUBRIC_IN_WS)
    return claude(f"Review the spec at {spec}.", ws, model, READ_TOOLS, system, log, "reviewer")


def review_lenses(ws, spec, model, log, rnd, run_dir):
    common = (ARMS_DIR / "lens-common.md").read_text().replace("RUBRIC_PATH", RUBRIC_IN_WS)

    def lens(name):
        system = common + "\n" + (ARMS_DIR / f"lens-{name}.md").read_text()
        return claude(f"Review the spec at {spec}.", ws, model, READ_TOOLS, system, log,
                      f"lens-{name}")

    with ThreadPoolExecutor(len(LENSES)) as pool:
        outputs = list(pool.map(lens, LENSES))
    raw = "\n\n".join(outputs)
    (run_dir / f"round-{rnd}-lenses.md").write_text(raw)
    findings = ws / ".sdlc" / "findings.md"
    findings.write_text(raw)
    system = (ARMS_DIR / "verifier.md").read_text().replace("RUBRIC_PATH", RUBRIC_IN_WS)
    prompt = f"Verify the findings at .sdlc/findings.md about the spec at {spec}."
    report = claude(prompt, ws, model, READ_TOOLS, system, log, "verifier")
    findings.unlink()
    return report


ARMS = {
    "A": (review_single, "sonnet"),
    "B": (review_lenses, "sonnet"),
    "C": (review_single, "opus"),
    "D": (review_single, "sonnet"),
}


def fix(ws, spec, log, report):
    (ws / ".sdlc" / "report.md").write_text(report)
    system = (ARMS_DIR / "fixer.md").read_text().replace("REPORT_PATH", ".sdlc/report.md") \
        .replace("SPEC_PATH", spec).replace("RUBRIC_PATH", RUBRIC_IN_WS)
    claude("Fix the spec as the review report says.", ws, "sonnet",
           ["Read", "Edit", "Glob", "Grep"], system, log, "fixer", edit=True)


def sequence(ws, spec, log, run_dir):
    """Arm D: one full review, one fix, one confirm check; never a second review."""
    report = review_single(ws, spec, "sonnet", log, 1, run_dir)
    (run_dir / "round-1-report.md").write_text(report)
    if passed(report):
        return [report]
    shutil.copy(ws / spec, ws / ".sdlc" / "before.md")
    fix(ws, spec, log, report)
    shutil.copy(ws / spec, run_dir / "spec-after-round-1.md")
    system = (ARMS_DIR / "confirm.md").read_text().replace("RUBRIC_PATH", RUBRIC_IN_WS)
    confirm = claude(f"Confirm the fixes to the spec at {spec}.", ws, "sonnet", READ_TOOLS,
                     system, log, "confirm")
    (run_dir / "round-2-confirm.md").write_text(confirm)
    return [report, confirm]


def run_one(out, case, arm, n, cap):
    run_dir = out / "runs" / case / arm / str(n)
    if (run_dir / "meta.json").exists():
        return
    run_dir.mkdir(parents=True, exist_ok=True)
    log = run_dir / "calls.jsonl"
    log.write_text("")
    ws, spec = workspace(case, run_dir)
    review, model = ARMS[arm]
    reports = []
    if arm == "D":
        reports = sequence(ws, spec, log, run_dir)
    for rnd in range(1, cap + 1 if arm != "D" else 1):
        report = review(ws, spec, model, log, rnd, run_dir)
        (run_dir / f"round-{rnd}-report.md").write_text(report)
        reports.append(report)
        if passed(report) or rnd == cap:
            break
        fix(ws, spec, log, report)
        (ws / ".sdlc" / "report.md").unlink()
        shutil.copy(ws / spec, run_dir / f"spec-after-round-{rnd}.md")
    shutil.copy(ws / spec, run_dir / "final-spec.md")
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    meta = {
        "case": case, "arm": arm, "run": n, "rounds": len(reports),
        "final_pass": passed(reports[-1]),
        "cost_usd": round(sum(c["cost_usd"] for c in calls), 4),
        "review_cost_usd": round(sum(c["cost_usd"] for c in calls if c["role"] != "fixer"), 4),
        "calls": len(calls), "errors": sum(c["error"] for c in calls),
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--arms", default="A,B,C")
    parser.add_argument("--cases", default="all")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--cap", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    cases = sorted(p.name for p in (CORPUS / "cases").iterdir()) if args.cases == "all" \
        else args.cases.split(",")
    jobs = [(c, a, n) for n in range(1, args.runs + 1) for c in cases for a in args.arms.split(",")]
    with ThreadPoolExecutor(args.jobs) as pool:
        for future in [pool.submit(run_one, out, c, a, n, args.cap) for c, a, n in jobs]:
            future.result()


if __name__ == "__main__":
    main()

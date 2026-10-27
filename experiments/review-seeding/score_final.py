"""Judge the spec each run ends with, rather than the reports along the way.

For every planted defect, a Sonnet judge says whether the final spec still has it (a defect the
spec now carries as an open question counts as handled). An Opus judge, a different model from the
Sonnet reviewer and fixer, counts problems the edits introduced. Verdicts are cached in each run's
final.json.

Usage: python3 score_final.py --out results/<name> [--arms A,D] [--jobs 8]
"""

import argparse
import json
import re
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"

PRESENT = """Below is a spec, then one problem that an earlier version of it had. Does this spec still
have that problem? It is handled if the spec now fixes it, or carries it as an open question for
the person to decide. Answer PRESENT or HANDLED on the first line, then one sentence of reason.

<spec>
{spec}
</spec>

<problem>
Where it was: "{quote}"
What: {description}
</problem>"""

BROKEN = """Below are two versions of a spec: BEFORE, and AFTER someone edited it to fix review
findings. Spec rules are in RULES. List the problems in AFTER that the edits introduced: a sentence
added or changed that breaks a rule, contradicts the rest of the spec, or can be read two ways, or
behaviour the edits invented that nobody asked for. Ignore problems already in BEFORE. Put the
number of introduced problems alone on the first line, then list them.

<rules>
{rules}
</rules>

<before>
{before}
</before>

<after>
{after}
</after>"""


def ask(prompt, model):
    for _ in range(3):
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--output-format", "json", "--tools", "",
             "--strict-mcp-config", "--no-session-persistence", "--setting-sources", ""],
            cwd="/tmp", capture_output=True, text=True, timeout=900)
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue
        if not data.get("is_error"):
            return data.get("result", "").strip()
    return ""


def final_spec(run_dir, case):
    saved = run_dir / "final-spec.md"
    if saved.exists():
        return saved.read_text()
    spec_path = json.loads((CORPUS / "cases" / case / "case.json").read_text())["spec_path"]
    return (run_dir / "ws" / spec_path).read_text()


def judge_run(run_dir):
    cache = run_dir / "final.json"
    if cache.exists():
        return json.loads(cache.read_text())
    meta = json.loads((run_dir / "meta.json").read_text())
    case = meta["case"]
    defects = json.loads((CORPUS / "cases" / case / "case.json").read_text())["defects"]
    before = (CORPUS / "cases" / case / "spec.md").read_text()
    after = final_spec(run_dir, case)
    result = {"present": {}}
    for d in defects:
        answer = ask(PRESENT.format(spec=after, quote=d["quote"], description=d["description"]),
                     "sonnet")
        result["present"][d["id"]] = answer.upper().startswith("PRESENT")
    if after.strip() == before.strip():
        result["introduced"] = 0
    else:
        rules = (HERE.parent.parent / "skills/spec/references/rubric.md").read_text()
        first = ask(BROKEN.format(rules=rules, before=before, after=after), "opus").splitlines()
        result["introduced"] = int(re.sub(r"\D", "", first[0]) or 0) if first else None
    cache.write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--arms", default="A,D")
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    arms = args.arms.split(",")
    runs = sorted(p.parent for p in out.glob("runs/*/*/*/meta.json") if p.parent.parent.name in arms)
    with ThreadPoolExecutor(args.jobs) as pool:
        judged = list(pool.map(judge_run, runs))
    left, total, introduced, passes, cost, n = (defaultdict(int) for _ in range(6))
    for run_dir, j in zip(runs, judged):
        meta = json.loads((run_dir / "meta.json").read_text())
        arm = meta["arm"]
        n[arm] += 1
        left[arm] += sum(j["present"].values())
        total[arm] += len(j["present"])
        introduced[arm] += j["introduced"] or 0
        passes[arm] += meta["final_pass"]
        cost[arm] += meta["review_cost_usd"]
    lines = ["| Measure | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    lines.append("| Planted defects still in the final spec | "
                 + " | ".join(f"{left[a]}/{total[a]}" for a in arms) + " |")
    lines.append("| Problems introduced by edits, per run | "
                 + " | ".join(f"{introduced[a] / n[a]:.1f}" for a in arms) + " |")
    lines.append("| Runs ending in a pass | " + " | ".join(f"{passes[a]}/{n[a]}" for a in arms) + " |")
    lines.append("| Review cost per run, USD | "
                 + " | ".join(f"{cost[a] / n[a]:.2f}" for a in arms) + " |")
    table = "\n".join(lines)
    (out / "final-summary.md").write_text(table + "\n")
    print(table)


if __name__ == "__main__":
    main()

"""Run the review relay experiment: does the correction checker get the review exactly?

  inject  hooks save the reviewer's report and the reviewed text, and add them to the checker's
          request; the drafting agent passes only the document's path
  paste   the drafting agent copies the report and the reviewed text into the request itself

A mode may name the drafting agent's model after a hyphen, such as paste-opus; the default is
Sonnet. The reviewer and checker always run on Sonnet.

Each run copies the seeding corpus product into a fresh workspace, places one case's spec, and
has a Sonnet drafting agent (claude -p with the prototype plugin in plugin/) review, correct and
check it. The plugin's hook logs every hand-over to logs/<session>.jsonl in its data folder.

Usage: python3 run.py --out results/<name> [--modes inject,paste] [--runs 3] [--jobs 6]
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent / "review-seeding" / "corpus"
PLUGIN = HERE / "plugin"
DATA = Path.home() / ".claude" / "plugins" / "data" / "relay-inline"


def run_one(out, case, mode, n):
    run_dir = out / "runs" / case / mode / str(n)
    if (run_dir / "meta.json").exists():
        return
    run_dir.mkdir(parents=True, exist_ok=True)
    meta = json.loads((CORPUS / "cases" / case / "case.json").read_text())
    spec = meta["spec_path"]
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "ws"
        shutil.copytree(CORPUS / "product", ws)
        (ws / spec).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(CORPUS / "cases" / case / "spec.md", ws / spec)
        relay, _, model = mode.partition("-")
        prompt = (HERE / f"drafter-{'hook' if relay == 'inject' else 'paste'}.md").read_text() \
            .replace("SPEC_PATH", spec)
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_REMOTE_SESSION_ID")}
        env["RELAY_MODE"] = relay
        session_arg = str(uuid.uuid4())
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", model or "sonnet", "--plugin-dir", str(PLUGIN),
             "--output-format", "json", "--permission-mode", "acceptEdits",
             "--allowedTools", "Read,Edit,Glob,Grep,Agent", "--strict-mcp-config",
             "--setting-sources", "", "--session-id", session_arg],
            cwd=ws, capture_output=True, text=True, env=env, timeout=1800)
        shutil.copy(ws / spec, run_dir / "final-spec.md")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"is_error": True, "result": proc.stdout[-2000:] + proc.stderr[-2000:]}
    session = data.get("session_id")
    log = DATA / "logs" / f"{session}.jsonl"
    if session and log.exists():
        shutil.copy(log, run_dir / "relay-log.jsonl")
    (run_dir / "result.md").write_text(data.get("result") or "")
    meta = {"case": case, "mode": mode, "run": n, "session": session,
            "error": bool(data.get("is_error")), "cost_usd": data.get("total_cost_usd", 0)}
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--modes", default="inject,paste")
    parser.add_argument("--cases", default="all")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    cases = sorted(p.name for p in (CORPUS / "cases").iterdir()) if args.cases == "all" \
        else args.cases.split(",")
    jobs = [(c, m, n) for n in range(1, args.runs + 1) for c in cases for m in args.modes.split(",")]
    with ThreadPoolExecutor(args.jobs) as pool:
        for future in [pool.submit(run_one, out, c, m, n) for c, m, n in jobs]:
            future.result()


if __name__ == "__main__":
    main()

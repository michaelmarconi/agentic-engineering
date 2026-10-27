"""Score the review relay experiment: did the checker receive the report and the reviewed text exactly?

For every run, compares what reached the correction checker with the originals the hook saved:
the reviewer's report as it returned it, and the spec as it stood when reviewed. Writes
results/<name>/summary.md and score.json.

Usage: python3 score.py --out results/<name>
"""

import argparse
import difflib
import json
import re
from collections import defaultdict
from pathlib import Path

HARNESS_NOTE = re.compile(r"\A<tools-used-before-summary>.*?</tools-used-before-summary>\n?", re.S)


def between(text, start, end):
    i = text.find(start)
    if i < 0:
        return None
    i = text.find("\n", i) + 1
    j = text.find(end, i)
    return text[i:j] if j >= 0 else None


def compare(original, copy):
    if copy is None:
        return {"present": False, "exact": False, "same_but_spacing": False, "similarity": 0.0,
                "lines_lost": None, "lines_added": None}
    a, b = original.strip(), copy.strip()
    squash = lambda s: re.sub(r"\s+", " ", s).strip()
    a_lines = [l.strip() for l in a.splitlines() if l.strip()]
    b_lines = [l.strip() for l in b.splitlines() if l.strip()]
    return {
        "present": True,
        "exact": a == b,
        "same_but_spacing": squash(a) == squash(b),
        "similarity": round(difflib.SequenceMatcher(None, a, b, autojunk=False).ratio(), 4),
        "lines_lost": sum(1 for l in a_lines if l not in set(b_lines)),
        "lines_added": sum(1 for l in b_lines if l not in set(a_lines)),
    }


def score_run(run_dir):
    meta = json.loads((run_dir / "meta.json").read_text())
    log = run_dir / "relay-log.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    by = defaultdict(list)
    for e in events:
        by[e["event"]].append(e)
    row = dict(meta, checker_calls=len(by["checker-start"]), reviews=len(by["review-start"]))
    if not by["review-start"] or not by["review-end"] or not by["checker-start"]:
        row["complete"] = False
        return row
    row["complete"] = True
    text = by["review-start"][-1]["text"]
    report = HARNESS_NOTE.sub("", by["review-end"][-1]["report"])
    start = by["checker-start"][0]
    prompt = start.get("injected_prompt") or start.get("original_prompt") or ""
    sent_report = between(prompt, "=== REVIEW REPORT ===", "=== END REVIEW REPORT ===")
    sent_text = between(prompt, "=== DOCUMENT AS REVIEWED", "=== END DOCUMENT ===")
    if sent_report is not None:
        sent_report = HARNESS_NOTE.sub("", sent_report)
    row["report"] = compare(report, sent_report)
    row["document"] = compare(text, sent_text)
    ends = by["checker-end"]
    verdict = re.search(r"Result:\s*\**\s*(PASS|FAIL)", ends[0]["report"]) if ends else None
    row["checker_result"] = verdict.group(1) if verdict else None
    return row


def summarise(rows, mode):
    rs = [r for r in rows if r["mode"] == mode]
    done = [r for r in rs if r.get("complete")]
    lines = [f"### {mode}", "", f"- Runs: {len(rs)}, complete: {len(done)}"]
    for part in ["report", "document"]:
        ok = [r[part] for r in done]
        if not ok:
            continue
        lines += [
            f"- {part.capitalize()} reached the checker: {sum(o['present'] for o in ok)}/{len(ok)}",
            f"  - exactly: {sum(o['exact'] for o in ok)}/{len(ok)}",
            f"  - same apart from spacing: {sum(o['same_but_spacing'] for o in ok)}/{len(ok)}",
            f"  - runs with lines lost: {sum(1 for o in ok if o['lines_lost'])}/{len(ok)}, "
            f"lines lost in all: {sum(o['lines_lost'] or 0 for o in ok)}",
            f"  - runs with lines added or changed: {sum(1 for o in ok if o['lines_added'])}/{len(ok)}",
            f"  - lowest similarity: {min(o['similarity'] for o in ok):.3f}",
        ]
    lines += [
        f"- Checker passed: {sum(1 for r in done if r.get('checker_result') == 'PASS')}/{len(done)}",
        f"- Runs that started the checker more than once: {sum(1 for r in rs if r['checker_calls'] > 1)}",
        f"- Cost per run (list prices, relative): ${sum(r['cost_usd'] for r in rs) / max(len(rs), 1):.2f}",
        "",
    ]
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    rows = [score_run(p.parent) for p in sorted((out / "runs").glob("*/*/*/meta.json"))]
    (out / "score.json").write_text(json.dumps(rows, indent=2))
    modes = sorted({r["mode"] for r in rows})
    text = ["# Review relay results", ""]
    for mode in modes:
        text += summarise(rows, mode)
    (out / "summary.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()

"""Judge and summarise a seeded-defect run.

For every run and every planted defect, a Sonnet judge answers one question: does what reached the
fixer point out this defect? It is asked about the first round's report and about all rounds'
reports together (and, for arm B, about the lens findings before the verifier). For the clean
cases, it counts the problems the first report claims. Verdicts are cached in each run's
judge.json, so scoring again costs nothing.

Usage: python3 score.py --out results/<name> [--jobs 8]
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

CAUGHT = """Below is a review of a spec, possibly several rounds of it, followed by one known problem
with the spec. Answer whether the review points out that problem: the same underlying problem
counts even in different words, as a failed check, an other finding, a decision for the person or
an open question. A review that only mentions the same sentence for a different reason does not
count. Answer YES or NO on the first line, then one sentence of reason.

<review>
{review}
</review>

<problem>
Where: "{quote}"
What: {description}
</problem>"""

COUNT = """Below is a review of a spec. Count the distinct problems it claims the spec has: failed
checks, other findings and decisions it says need the person. Do not count suggestions, dropped
findings or passing checks. Answer with the number alone on the first line.

<review>
{review}
</review>"""


def ask(prompt):
    for _ in range(3):
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", "sonnet", "--output-format", "json", "--tools", "",
             "--strict-mcp-config", "--no-session-persistence", "--setting-sources", ""],
            cwd="/tmp", capture_output=True, text=True, timeout=600)
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue
        if not data.get("is_error"):
            return data.get("result", "").strip()
    return ""


def reports(run_dir, pattern):
    files = sorted(run_dir.glob(pattern), key=lambda p: int(re.search(r"round-(\d+)", p.name)[1]))
    return "\n\n".join(f"## {p.stem}\n\n{p.read_text()}" for p in files)


def judge_run(run_dir):
    cache = run_dir / "judge.json"
    if cache.exists():
        return json.loads(cache.read_text())
    meta = json.loads((run_dir / "meta.json").read_text())
    defects = json.loads((CORPUS / "cases" / meta["case"] / "case.json").read_text())["defects"]
    views = {"first": (run_dir / "round-1-report.md").read_text(),
             "all": reports(run_dir, "round-*-report.md")}
    if meta["arm"] == "B":
        views["lenses"] = reports(run_dir, "round-*-lenses.md")
    verdicts = {}
    for d in defects:
        for view, text in views.items():
            answer = ask(CAUGHT.format(review=text, quote=d["quote"], description=d["description"]))
            verdicts[f"{d['id']}|{view}"] = answer.upper().startswith("YES")
    result = {"verdicts": verdicts}
    if not defects:
        first = ask(COUNT.format(review=views["first"])).splitlines()
        result["claimed"] = int(re.sub(r"\D", "", first[0]) or 0) if first else None
    cache.write_text(json.dumps(result, indent=2))
    return result


def pct(hits, total):
    return f"{100 * hits / total:.0f}% ({hits}/{total})" if total else "n/a"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    runs = sorted(p.parent for p in out.glob("runs/*/*/*/meta.json"))
    with ThreadPoolExecutor(args.jobs) as pool:
        judged = list(pool.map(judge_run, runs))

    stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    money = defaultdict(list)
    rounds = defaultdict(list)
    claimed = defaultdict(list)
    for run_dir, j in zip(runs, judged):
        meta = json.loads((run_dir / "meta.json").read_text())
        arm = meta["arm"]
        money[arm].append(meta["review_cost_usd"])
        rounds[arm].append(meta["rounds"])
        if "claimed" in j:
            claimed[arm].append(j["claimed"])
        defects = json.loads((CORPUS / "cases" / meta["case"] / "case.json").read_text())["defects"]
        for d in defects:
            for view in ("first", "all", "lenses"):
                key = f"{d['id']}|{view}"
                if key not in j["verdicts"]:
                    continue
                for group in (f"{view}", f"{view}|{d['subtlety']}", f"{view}|type:{d['type']}"):
                    stats[arm][group][0] += j["verdicts"][key]
                    stats[arm][group][1] += 1

    arms = sorted(stats)
    lines = ["| Measure | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    groups = ["all", "all|obvious", "all|subtle", "first", "lenses"]
    names = {"all": "Caught, all rounds", "all|obvious": "  obvious", "all|subtle": "  subtle",
             "first": "Caught in round 1", "lenses": "Found by lenses before verifier"}
    for g in groups:
        lines.append(f"| {names[g]} | " + " | ".join(pct(*stats[a][g]) for a in arms) + " |")
    for g in sorted({g for a in arms for g in stats[a] if g.startswith("all|type:")}):
        lines.append(f"| {g[9:]} | " + " | ".join(pct(*stats[a][g]) for a in arms) + " |")
    avg = lambda xs: sum(xs) / len(xs) if xs else 0
    lines.append("| Review cost per run, USD | " + " | ".join(f"{avg(money[a]):.2f}" for a in arms) + " |")
    lines.append("| Rounds per run | " + " | ".join(f"{avg(rounds[a]):.1f}" for a in arms) + " |")
    lines.append("| Problems claimed on clean specs, round 1 | "
                 + " | ".join(f"{avg(claimed[a]):.1f}" for a in arms) + " |")
    table = "\n".join(lines)
    (out / "summary.md").write_text(table + "\n")
    print(table)


if __name__ == "__main__":
    main()

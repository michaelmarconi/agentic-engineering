#!/usr/bin/env python3
"""Start and end a /verify run: check the repository is committed, note the commit, list the specs'
requirements, and write the report file.

/verify runs `start` before it agrees with the person what to check, and `report` once every agent
has reported. Neither changes anything in the repository.

start [<spec path> ...] --data <folder> --session <id> [--project <folder>]
    Refuses while anything is uncommitted, with the same check /build makes (scripts/uncommitted.py),
    since the report must name the version of the product it checked. Otherwise notes the commit
    checked out, clears what the verify hook (scripts/verify_relay.py) kept of an earlier run in this
    session, and lists each spec named, or every spec under docs/specs/
    when none is: its path, its status as the status hook reads it (scripts/status_check.py),
    whether it is `👍 Accepted`, whether it still heads its requirements `### Requirement: <name>`, as
    specs written for an earlier version of the plugin did (old_layout), and its numbered requirements, each with how many examples it holds
    (its `| Example | ... |` tables). A path may be relative to the repository or full. It refuses a
    path that is missing or is not a *.spec.md under docs/specs/, and a plan, saying to give
    the specs it names instead. Prints JSON: root (the
    repository's full path), commit, and specs [{path, status, accepted, old_layout, requirements
    [{number, name, examples}]}].

report --scope <what was checked> --commit <commit> --data <folder> --session <id> [--project <folder>]
    Writes the run's report file (ADRs 0033 and 0034) with scripts/run_report.py, outside the
    repository, and clears what the hook kept. Claude's own sections arrive on stdin as Markdown
    under the report's `## ` headings. The script fills the rest: "Commit checked", the commit
    `start` printed, given as --commit; "What each agent reported", each verifier's and verify-checker's report word for
    word, by spec; and "The repository after the run", which says whether that commit is still
    checked out and lists every file that differs from the commit, such as a lock file the product
    rewrote, a change committed during the run or a helper an agent left behind; files .gitignore
    names are left out. Prints the file's path first, then each heading and each copied report with its
    length, and the file as written. It refuses a commit the repository does not have.

Exit codes: 0 done; 1 refused or failed, with the reason on stderr and nothing on stdout.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

# The plugin's scripts/ folder holds the status hook, the verify hook and the shared checks.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import run_report  # noqa: E402
import uncommitted  # noqa: E402
import verify_relay  # noqa: E402
from status_check import (ACCEPTED, REQUIREMENT_HEADING, SPEC_STATUSES, headings_allowed,  # noqa: E402
                          lifecycle_status, old_layout, section)

EXAMPLE_TABLE = re.compile(r"^\s*\|\s*Example\s*\|", re.IGNORECASE)
AGENT_NAMES = {"verifier": "Verifier", "verify-checker": "Verify-checker"}


class Refused(Exception):
    """The command can't do what was asked; the reason says why."""


def git(project, *args):
    try:
        return subprocess.run(["git", "-C", project, *args], capture_output=True, encoding="utf-8",
                              errors="surrogateescape")
    except OSError as error:
        raise Refused(f"git could not be run ({error})")


def root_of(project):
    found = git(project, "rev-parse", "--show-toplevel")
    if found.returncode != 0:
        raise Refused(f"{project} is not in a git repository ({found.stderr.strip()})")
    return os.path.realpath(found.stdout.strip())


def head(root):
    found = git(root, "rev-parse", "--verify", "-q", "HEAD")
    if found.returncode != 0:
        raise Refused("this branch has no commits yet, so there is no version to check")
    return found.stdout.strip()


def relative(root, path):
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    if not full.startswith(root + os.sep):
        raise Refused(f"{path} is not inside the repository {root}")
    return os.path.relpath(full, root).replace(os.sep, "/")


def is_spec(path):
    parts = path.split("/")
    return [p.lower() for p in parts[:2]] == ["docs", "specs"] and parts[-1].lower().endswith(".spec.md")


def requirements(text):
    """[{number, name, examples}] for the spec's numbered requirements, in order."""
    body = section(text, "Requirements") or []
    allowed = headings_allowed(body)
    found = []
    for line, is_heading in zip(body, allowed):
        match = REQUIREMENT_HEADING.match(line) if is_heading else None
        if match:
            number = int(re.match(r"^###\s+(\d+)", line).group(1))
            found.append({"number": number, "name": match.group(1), "examples": 0})
        elif found and is_heading and EXAMPLE_TABLE.match(line):
            found[-1]["examples"] += 1
    return found


def all_specs(root):
    folder = os.path.join(root, "docs", "specs")
    found = []
    for here, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        found += [relative(root, os.path.join(here, name)) for name in sorted(files) if name.lower().endswith(".spec.md")]
    return found


def describe(root, path):
    parts = path.split("/")
    if [p.lower() for p in parts[:2]] == ["docs", "plans"]:
        raise Refused(f"{path} is a plan: give the specs its Specs section names, and check only the "
                      "requirements it lists under them")
    if not is_spec(path):
        raise Refused(f"{path} is not a spec: a spec is a *.spec.md file under docs/specs/")
    try:
        with open(os.path.join(root, path), encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as error:
        raise Refused(f"can't read {path} ({getattr(error, 'strerror', None) or error})")
    status = lifecycle_status(text, SPEC_STATUSES)
    return {"path": path, "status": status, "accepted": status == ACCEPTED, "old_layout": old_layout(text),
            "requirements": requirements(text)}


def start(project, specs, data, session):
    root = root_of(project)
    commit = head(root)
    try:
        entries, _ = uncommitted.check(root)
    except uncommitted.NotARepository as error:
        raise Refused(str(error))
    if entries:
        raise Refused("these changes are not committed, so the report could not say which version of the "
                      "product it checked; commit or stash them, then run again:\n" + "\n".join(entries))
    paths = [relative(root, p) for p in specs] if specs else all_specs(root)
    listed = [describe(root, p) for p in paths]
    verify_relay.clear(data, session)
    return {"root": root, "commit": commit, "specs": listed}


def shown(root, path):
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    return os.path.relpath(full, root).replace(os.sep, "/") if full.startswith(root + os.sep) else path


def after_the_run(root, commit):
    """Whether `commit` is still checked out, and every file that differs from it now: tracked files
    changed, added or deleted, in the working tree or by commits made during the run, and new files
    git does not ignore."""
    now = head(root)
    lines = [f"The commit checked, {commit}, is still checked out." if now == commit else
             f"The commit checked out now is {now}, not {commit}: the verdicts are for {commit}."]
    changed = git(root, "diff", "--name-status", "--no-renames", commit)
    if changed.returncode != 0:
        raise Refused(f"git diff failed ({changed.stderr.strip()})")
    try:
        entries, _ = uncommitted.check(root)
    except uncommitted.NotARepository as error:
        raise Refused(str(error))
    found = [line.replace("\t", " ", 1) for line in changed.stdout.splitlines() if line.strip()]
    found += [entry for entry in entries if entry.startswith("??")]
    if found:
        lines += ["", f"These files differ from {commit}, with git's letter for each change "
                      "(M changed, A added, D deleted, ?? new and not ignored):", ""]
        lines += [f"- `{entry}`" for entry in found]
    else:
        lines += ["", "No tracked file changed and no new file appeared during the run, leaving out "
                      "files the repository's .gitignore names."]
    return "\n".join(lines) + "\n"


def copied(root, commit, kept):
    agents = sorted((r for r in kept if r["agent"] in AGENT_NAMES),
                    key=lambda r: (shown(root, r["document"]), r["agent"] != "verifier"))
    return {
        "Commit checked": [("The commit noted when the run started", commit + "\n")],
        "What each agent reported": [(f"{AGENT_NAMES[r['agent']]}: {shown(root, r['document'])}", r["text"])
                                     for r in agents],
        "The repository after the run": [("Checked by the script", after_the_run(root, commit))],
    }


def report(project, scope, commit, data, session, own_text, now):
    root = root_of(project)
    found = git(root, "rev-parse", "--verify", "-q", f"{commit}^{{commit}}")
    if not commit or found.returncode != 0:
        raise Refused(f"no commit '{commit}' in this repository: give the commit `start` printed")
    commit = found.stdout.strip()
    try:
        own = run_report.parse("verify", own_text)
        _, lines = run_report.write("verify", scope, root, data, own,
                                    copied(root, commit, verify_relay.reports(data, session)),
                                    date=now.date().isoformat())
    except run_report.ReportError as error:
        raise Refused(str(error))
    verify_relay.clear(data, session)
    return lines


def parse_now(value):
    if value is None:
        return datetime.datetime.now(datetime.timezone.utc)
    try:
        moment = datetime.datetime.fromisoformat(value)
    except ValueError:
        raise Refused(f"can't read --now '{value}'; write it as 2026-11-16T12:00:00+00:00")
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog=__doc__.split("\n\n", 1)[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    start_parser = commands.add_parser(
        "start", help="refuse uncommitted changes, note the commit and list the specs' requirements",
        description="Refuse while anything is uncommitted; otherwise note the commit, clear the kept reports of "
                    "an earlier run in this session, and list each spec named, or every spec, with its status "
                    "and requirements. Output: JSON with root, commit and specs [{path, status, accepted, old_layout, "
                    "requirements [{number, name, examples}]}]. Exit codes: 0 done; 1 refused, with the reason "
                    "on stderr.")
    start_parser.add_argument("specs", nargs="*", help="the specs to list (default: every spec under docs/specs/)")
    report_parser = commands.add_parser(
        "report", help="write the run's report file",
        description="Write the run's report file outside the repository, from Claude's sections on stdin "
                    "(Markdown under the report's `## ` headings), the commit `start` printed, the reports the "
                    "verify hook kept, copied word for word, and what changed in the repository during the run; "
                    "then clear the kept reports. Output: the file's path on the first line, then each heading "
                    "and each copied report with its length. Exit codes: 0 written; 1 refused, with the reason "
                    "on stderr.")
    report_parser.add_argument("--scope", required=True,
                               help="a few words naming what was checked, for the file's name, such as the spec's name")
    report_parser.add_argument("--commit", required=True, help="the commit `start` printed")
    report_parser.add_argument("--now", help="the report's date, in ISO 8601; for tests (default: now)")
    for sub in (start_parser, report_parser):
        sub.add_argument("--data", required=True, help='the plugin\'s data folder: "${CLAUDE_PLUGIN_DATA}"')
        sub.add_argument("--session", required=True, help='the session\'s id: "${CLAUDE_SESSION_ID}"')
        sub.add_argument("--project", default=".", help="the repository's folder (default: the current folder)")
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            out = start(args.project, args.specs, args.data, args.session)
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            lines = report(args.project, args.scope, args.commit, args.data, args.session, sys.stdin.read(), parse_now(args.now))
            print("\n".join(lines))
    except Refused as error:
        print(f"verify {args.command}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

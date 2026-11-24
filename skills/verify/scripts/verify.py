#!/usr/bin/env python3
"""Start and end a /verify run: check the repository is committed, note the commit, list the specs'
requirements, and write the report file.

/verify runs `start` before it agrees with the person what to check, and `report` once every agent
has reported. Neither changes anything in the repository.

start [<spec path> ...] [--scratchpad <folder>] --session <id> [--project <folder>]
    Refuses while anything is uncommitted, with the same check /build makes (scripts/uncommitted.py),
    since the report must name the version of the product it checked. Otherwise notes the commit
    checked out, clears what the verify hook (scripts/agent_relay.py) kept of an earlier run in this
    session, and lists each spec named, or every spec under docs/specs/
    when none is: its path, its status as the status hook reads it (scripts/status_check.py),
    whether it is `Accepted 👍`, whether it still heads its requirements `### Requirement: <name>`, as
    specs written for an earlier version of the plugin did (old_layout), and its numbered requirements, each with how many examples it holds
    (its `| Example | ... |` tables). A path may be relative to the repository or full. It refuses a
    path that is missing or is not a *.spec.md under docs/specs/, and a plan, saying to give
    the specs it names instead. Prints JSON: root (the
    repository's full path), commit, and specs [{path, status, accepted, old_layout, requirements
    [{number, name, examples}]}].

report --scope <what was checked> --commit <commit> [--scratchpad <folder>] --session <id> [--project <folder>]
    Writes the run's report file (ADRs 0051, 0034, 0058 and 0059) with scripts/run_report.py, in the
    session's scratchpad, and clears what the hook kept. Claude's own sections, "What needs doing"
    and "Caveats", arrive on stdin as Markdown under those `## ` headings. The script lays out the
    rest from each verifier's and verify-checker's report, which must keep the shape their agent
    definitions give: a title naming --scope; a header naming each spec, the commit `start`
    printed, given as --commit, and how the verifier started the product; "Result", a line of counts
    and one table with a row per example (a disputed verdict is one the checker rejected, and every
    example is not checked when the checker did not report or reported an `Error:`; a verifier's
    `Error:` gives each requirement its request named one not checked row); "Details", each
    example's entries from both agents, word for word under one heading; "The repository after the
    run", which says whether that commit is still checked out and lists every file that differs
    from the commit, such as a lock file the product rewrote, a change committed during the run or
    a helper an agent left behind, leaving out files .gitignore names; and "Commands", each agent's
    commands in a collapsed block. When `origin` is on GitHub, the spec, each requirement and each
    example link to the spec at the commit checked; otherwise they give their line in the spec.
    Prints the file's path first, then each heading and each section it filled with its length,
    and the file as written. It refuses a commit the repository does not have, and an agent report
    it cannot read, naming the agent and the line, or whose examples differ from the other agent's.

Exit codes: 0 done; 1 refused or failed, with the reason on stderr and nothing on stdout.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse

# The plugin's scripts/ folder holds the status hook, the verify hook and the shared checks.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import plugin_folder  # noqa: E402
import run_report  # noqa: E402
import uncommitted  # noqa: E402
import agent_relay  # noqa: E402
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
    agent_relay.clear(data, session, "verify")
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


VERDICTS = {"verifier": ("pass", "fail", "not checked"), "verify-checker": ("confirmed", "rejected")}
RESULTS = {"pass": "✅ Pass", "fail": "❌ Fail", "not checked": "⚠️ Not checked", "disputed": "⚠️ Disputed"}
REQUIREMENT_LINE = re.compile(r"^(\d+)\.\s+(\S.*?)\s*$")
EXAMPLE_LINE = re.compile(r"^-\s+(\S.*?):\s*([A-Za-z][A-Za-z ]*?)\s*\.?\s*$")
LABEL = re.compile(r"^(\s*)- (Did|Saw|Why):(\s)")
GITHUB = re.compile(r"^(?:https?://(?:[^@/]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
                    r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")
NO_LINKS = "Links to the spec were left out because the repository's `origin` is not on GitHub."


def github_repository(url):
    """The https address of a GitHub repository for a remote's URL in its usual forms, or None."""
    match = GITHUB.match((url or "").strip())
    return f"https://github.com/{match.group(1)}/{match.group(2)}" if match else None


def anchor(heading):
    """The anchor GitHub gives a Markdown heading: lowercase, every character that is not a letter,
    digit, space, hyphen or underscore dropped, then each space made a hyphen."""
    text = re.sub(r"^#+\s*", "", heading.strip()).lower()
    return "".join(c for c in text if c.isalnum() or c in " -_").replace(" ", "-")


def plain(name):
    return re.sub(r"\s+", " ", name.strip().strip("`\"'“”‘’").strip()).lower()


def spec_places(root, commit, path):
    """{number: (heading line, heading, {example name: line})} from the spec as it is at `commit`."""
    shown_at = git(root, "show", f"{commit}:{path}")
    if shown_at.returncode != 0:
        return {}
    places, current, allowed_lines = {}, None, shown_at.stdout.splitlines()
    for number, (line, ok) in enumerate(zip(allowed_lines, headings_allowed(allowed_lines)), 1):
        heading = re.match(r"^###\s+(\d+)\.\s+\S", line) if ok else None
        if heading:
            current = int(heading.group(1))
            places[current] = (number, line, {})
            continue
        if ok and re.match(r"^#{1,3}\s", line):
            current = None
            continue
        example = re.match(r"^\s*\|\s*Example\s*\|\s*(.*?)\s*\|", line, re.IGNORECASE) if ok else None
        if example and current is not None:
            places[current][2].setdefault(plain(example.group(1)), number)
    return places


class Links:
    """How the report names the spec, a requirement and an example: GitHub links at the commit
    checked (ADR 0059), or plain names with their line in the spec."""

    def __init__(self, root, commit):
        remote = git(root, "remote", "get-url", "origin")
        self.repository = github_repository(remote.stdout) if remote.returncode == 0 else None
        short = git(root, "rev-parse", "--short=7", commit)
        self.short = short.stdout.strip() if short.returncode == 0 else commit[:7]
        self.root, self.commit, self.places = root, commit, {}

    def base(self, path):
        return f"{self.repository}/blob/{self.short}/{urllib.parse.quote(path)}"

    def spec(self, path):
        return f"[{path}]({self.base(path)})" if self.repository else f"`{path}`"

    def _places(self, path):
        if path not in self.places:
            self.places[path] = spec_places(self.root, self.commit, path)
        return self.places[path]

    def requirements(self, path):
        """[(number, name)] for every numbered requirement of the spec at the commit checked."""
        return [(n, re.sub(r"^###\s+\d+\.\s+", "", place[1]).strip()) for n, place in sorted(self._places(path).items())]

    def requirement(self, path, number, name):
        place = self._places(path).get(number)
        if not place:
            return cell(name)
        if self.repository:
            return f"[{cell(name)}]({self.base(path)}#{anchor(place[1])})"
        return f"{cell(name)} (line {place[0]})"

    def example(self, path, number, name):
        line = self._places(path).get(number, (0, "", {}))[2].get(plain(name))
        if not line:
            return cell(name)
        if self.repository:
            return f"[{cell(name)}]({self.base(path)}?plain=1#L{line})"
        return f"{cell(name)} (line {line})"


def cell(text):
    return text.replace("|", "\\|")


def read_agent(agent, text, where):
    """One verify agent's report as {error, started, examples [{number, requirement, name, verdict,
    lines}], commands}, each line as the agent wrote it. Refuses a report it cannot read."""
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines) if line.startswith("Document:")), None)
    if first is None:
        raise Refused(f"the {agent}'s report on {where} has no `Document:` line, so it is not in the report's "
                      "shape: start the agent again with the same request")
    report = {"error": None, "started": None, "examples": [], "commands": []}
    requirement, example, commands = None, None, False
    for number, line in enumerate(lines[first + 1:], first + 2):
        if commands:
            report["commands"].append(line)
            continue
        if not line.strip():
            if example is not None:
                example["lines"].append(line)
            continue
        if line[0].isspace():
            if example is None:
                raise Refused(cannot_read(agent, where, number, line))
            example["lines"].append(line)
            continue
        example = None
        if line.startswith("Error:") and not report["examples"]:
            report["error"] = line[len("Error:"):].strip()
        elif line.startswith("Started:") and agent == "verifier" and requirement is None:
            report["started"] = line[len("Started:"):].strip()
        elif line.rstrip() == "Commands:":
            commands = True
        elif REQUIREMENT_LINE.match(line):
            match = REQUIREMENT_LINE.match(line)
            requirement = (int(match.group(1)), match.group(2))
        elif EXAMPLE_LINE.match(line) and requirement is not None:
            match = EXAMPLE_LINE.match(line)
            verdict = match.group(2).lower()
            if verdict not in VERDICTS[agent]:
                raise Refused(f"the {agent}'s report on {where}, line {number}: unknown verdict '{match.group(2)}'"
                              f" in {line.strip()!r}; the {agent} gives " + ", ".join(VERDICTS[agent])
                              + ": start the agent again with the same request")
            example = {"number": requirement[0], "requirement": requirement[1], "name": match.group(1),
                       "verdict": verdict, "lines": []}
            report["examples"].append(example)
        else:
            raise Refused(cannot_read(agent, where, number, line))
    while report["commands"] and not report["commands"][-1].strip():
        report["commands"].pop()
    seen = set()
    for example in report["examples"]:
        if key(example) in seen:
            raise Refused(f"the {agent}'s report on {where} gives requirement {example['number']}'s example "
                          f"'{example['name']}' twice: start the agent again with the same request")
        seen.add(key(example))
    return report


def cannot_read(agent, where, number, line):
    return (f"the {agent}'s report on {where}, line {number}, fits none of its entries: {line.strip()!r}; "
            "start the agent again with the same request")


def entry(example):
    """An example's lines as the agent wrote them, set flush left, with each label in bold."""
    lines = list(example["lines"])
    while lines and not lines[-1].strip():
        lines.pop()
    indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    shown_lines = []
    for line in lines:
        line = line[indent:]
        labelled = LABEL.sub(r"\1- **\2:**\3", line)
        # A line that is not a labelled bullet stays indented under the bullet before it, so quoted
        # output such as a heading can't become part of the report's own layout.
        shown_lines.append(labelled if labelled != line or not line.strip() else "  " + line)
    return "\n".join(shown_lines)


def key(example):
    return (example["number"], plain(example["name"]))


def spec_results(path, verifier, checker, requested, where, every_requirement=()):
    """[(row, verifier's example or None, checker's example or None)] for one spec, and the notes
    under its table. A row is (number, requirement, example name or None, result)."""
    notes = []
    if verifier is None:
        return [], [f"No verifier reported on {path}."]
    if verifier["error"] is not None:
        rows = [((n, name, None, "not checked"), None, None) for n, name in requested or every_requirement]
        return rows, [f"The verifier checked nothing: {verifier['error']}"]
    theirs = {}
    if checker is None:
        notes.append(f"The checker did not report on {path}, so no verdict stands.")
    elif checker["error"] is not None:
        notes.append(f"The checker checked nothing: {checker['error']}")
        checker = None
    else:
        theirs = {key(e): e for e in checker["examples"]}
        ours = {key(e) for e in verifier["examples"]}
        for missing in [e for e in verifier["examples"] if key(e) not in theirs]:
            raise Refused(f"the verify-checker's report on {where} has no entry for requirement {missing['number']}'s "
                          f"example '{missing['name']}', which the verifier's has: start the checker again")
        for extra in [e for e in checker["examples"] if key(e) not in ours]:
            raise Refused(f"the verify-checker's report on {where} has an entry for requirement {extra['number']}'s "
                          f"example '{extra['name']}', which the verifier's has not: start the checker again")
    rows = []
    for example in verifier["examples"]:
        check = theirs.get(key(example))
        if checker is None:
            result = "not checked"
        elif check["verdict"] == "rejected":
            result = "disputed"
        else:
            result = example["verdict"]
        rows.append(((example["number"], example["requirement"], example["name"], result), example, check))
    return rows, notes


def counts_line(results, rejected, every_spec_checked):
    count = {r: sum(1 for x in results if x == r) for r in ("pass", "fail", "disputed", "not checked")}
    line = (f"**{count['pass']} passed, {count['fail']} failed, {count['disputed']} disputed, "
            f"{count['not checked']} not checked.**")
    if rejected:
        return line + f" The checker rejected {rejected} verdict{'s' if rejected != 1 else ''}."
    return line + (" The checker agreed with every verdict." if results and every_spec_checked else "")


def laid_out(root, commit, scope, kept):
    """(top, {heading: [(title or None, text)]}): the report's title and header, and the sections
    the script writes, from the verify agents' reports (ADR 0058)."""
    links = Links(root, commit)
    by_spec = {}
    for report in kept:
        if report["agent"] in AGENT_NAMES:
            by_spec.setdefault(shown(root, report["document"]), {})[report["agent"]] = report
    paths = sorted(by_spec)
    header = [f"- **Spec:** {links.spec(path)}" for path in paths] + [f"- **Commit:** `{links.short}`"]
    if not links.repository:
        header.append(f"- **Links:** {NO_LINKS}")
    tables, details, commands, every, rejected, unchecked, numbers = [], [], [], [], 0, 0, set()
    for path in paths:
        agents = by_spec[path]
        read = {agent: read_agent(agent, r["text"], path) for agent, r in agents.items()}
        verifier, checker = read.get("verifier"), read.get("verify-checker")
        if verifier and verifier["started"]:
            header.append(f"- **Product:** {verifier['started']}" + (f" ({path})" if len(paths) > 1 else ""))
        requested = (agents.get("verifier") or {}).get("requested") or []
        rows, notes = spec_results(path, verifier, checker, requested, path, links.requirements(path))
        unchecked += bool(checker is None or checker["error"] is not None or verifier is None
                          or verifier["error"] is not None)
        numbers.update(row[0][0] for row in rows)
        table = (["", f"{links.spec(path)}"] if len(paths) > 1 else []) + [
            "", "| # | Requirement | Example | Result |", "|--:|---|---|---|"]
        for (number, requirement, name, result), ours, theirs in rows:
            example = links.example(path, number, name) if name is not None else "—"
            table.append(f"| {number} | {links.requirement(path, number, requirement)} | {example} | {RESULTS[result]} |")
            every.append(result)
            rejected += bool(theirs and theirs["verdict"] == "rejected")
            if ours is None:
                continue
            body = ["**Verifier**", "", entry(ours), ""]
            if theirs is None:
                body += ["**Checker** did not report."]
            else:
                body += [f"**Checker** ({theirs['verdict']})", "", entry(theirs)]
            details.append((f"{number}. {example} — {RESULTS[result]}", "\n".join(body) + "\n"))
        tables += table + ([""] + notes if notes else [])
        for agent in ("verifier", "verify-checker"):
            if read.get(agent) and read[agent]["commands"]:
                listed = "\n".join(read[agent]["commands"])
                fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", listed)), default=0))
                commands.append(f"<details>\n<summary>{AGENT_NAMES[agent]}: {path}</summary>\n\n{fence}text\n"
                                f"{listed}\n{fence}\n\n</details>")
    result = "\n".join([counts_line(every, rejected, unchecked == 0)] + tables) + "\n" if paths else ""
    title = f"# Verify report: {scope}"
    if len(paths) == 1 and numbers:
        listed = [str(n) for n in sorted(numbers)]
        title += (f", requirement {listed[0]}" if len(listed) == 1 else
                  ", requirements " + ", ".join(listed[:-1]) + " and " + listed[-1])
    top = title + "\n\n" + "\n".join(header) + "\n"
    copied = {"Result": [(None, result)] if result else [],
              "Details": details,
              "The repository after the run": [(None, after_the_run(root, commit))],
              "Commands": [(None, "\n\n".join(commands) + "\n")] if commands else []}
    return top, copied


def report(project, scope, commit, data, session, own_text, now):
    root = root_of(project)
    found = git(root, "rev-parse", "--verify", "-q", f"{commit}^{{commit}}")
    if not commit or found.returncode != 0:
        raise Refused(f"no commit '{commit}' in this repository: give the commit `start` printed")
    commit = found.stdout.strip()
    try:
        own = run_report.parse("verify", own_text)
        top, copied = laid_out(root, commit, scope, agent_relay.reports(data, session, "verify"))
        _, lines = run_report.write("verify", scope, root, data, own, copied, date=now.date().isoformat(), top=top)
    except run_report.ReportError as error:
        raise Refused(str(error))
    agent_relay.clear(data, session, "verify")
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
        description="Write the run's report file in the session's scratchpad, from Claude's sections on stdin "
                    "(Markdown under `## What needs doing` and `## Caveats`), the commit `start` printed, and the "
                    "reports the verify hook kept, laid out as a results table, each example's details word for "
                    "word and each agent's commands, with what changed in the repository during the run; then "
                    "clear the kept reports. Output: the file's path on the first line, then each heading and "
                    "each section filled with its length, then the file as written. Exit codes: 0 written; 1 "
                    "refused, such as for an agent report not in its shape, with the reason on stderr.")
    report_parser.add_argument("--scope", required=True,
                               help="a few words naming what was checked, for the file's name, such as the spec's name")
    report_parser.add_argument("--commit", required=True, help="the commit `start` printed")
    report_parser.add_argument("--now", help="the report's date, in ISO 8601; for tests (default: now)")
    for sub in (start_parser, report_parser):
        sub.add_argument("--scratchpad", default="",
                         help="the session's scratchpad folder, as your instructions name it; leave it out when "
                              "they name none, and a private temporary folder is used")
        sub.add_argument("--session", required=True, help='the session\'s id: "${CLAUDE_SESSION_ID}"')
        sub.add_argument("--project", default=".", help="the repository's folder (default: the current folder)")
    args = parser.parse_args(argv)
    try:
        try:
            args.data = plugin_folder.root(args.scratchpad, args.session)
        except plugin_folder.FolderError as error:
            raise Refused(str(error))
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

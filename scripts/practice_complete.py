#!/usr/bin/env python3
"""Say whether a project's releasing or deploying practice holds every item its skill needs.

The practices skill records releasing and deploying in a fixed layout, and the release and
deploy skills act only on a complete one, so all three run this script to agree on what
complete means.

- `docs/practices/releasing.md` needs three `##` headings, each with text under it:
  What may be released, Version and its commit, Publish.
- `docs/practices/deploying.md` needs at least one `## Environment: <name>` section, and each
  such section needs four `###` headings with text under them: Releases allowed, Deploy, Check,
  Roll back.

Headings match whatever their case. Any other heading is allowed and ignored. A required item
whose text holds "(default)" fails, since a default Claude proposed must not run against real
systems. Lines inside code blocks are never read as headings.
"""

import argparse
import os
import re
import sys

RELEASING = ("What may be released", "Version and its commit", "Publish")
ENVIRONMENT_PARTS = ("Releases allowed", "Deploy", "Check", "Roll back")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
ENVIRONMENT = re.compile(r"^environment:\s*(.*)$", re.IGNORECASE)
DEFAULT = "(default)"


def sections(lines):
    """Return (level, title, body lines) for each heading, the body running to the next heading
    at the same or a higher level."""
    headings = []
    fenced = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        match = None if fenced else HEADING.match(line)
        if match:
            headings.append((i, len(match.group(1)), match.group(2)))
    found = []
    for n, (i, level, title) in enumerate(headings):
        end = len(lines)
        for j, other, _ in headings[n + 1:]:
            if other <= level:
                end = j
                break
        found.append((level, title, lines[i + 1:end]))
    return found


def judge(name, body, label):
    """Return a problem with one required item's text, or None."""
    text = "\n".join(line for line in body if line.strip())
    if not text:
        return f"{label}{name} has nothing under it"
    if DEFAULT in text.lower():
        return f"{label}{name} is a default: a required item must come from the person or the repository"
    return None


def check_items(found, level, names, label, owner):
    problems = []
    by_title = {}
    for lvl, title, body in found:
        if lvl == level:
            by_title.setdefault(title.strip().lower(), body)
    for name in names:
        body = by_title.get(name.lower())
        if body is None:
            problems.append(f"{owner} has no {name}")
        else:
            problem = judge(name, body, label)
            if problem:
                problems.append(problem)
    return problems


def check_releasing(lines):
    return check_items(sections(lines), 2, RELEASING, "", "releasing.md")


def check_deploying(lines):
    problems = []
    environments = 0
    for level, title, body in sections(lines):
        match = ENVIRONMENT.match(title.strip()) if level == 2 else None
        if not match:
            continue
        environments += 1
        name = match.group(1).strip()
        if not name:
            problems.append("an Environment heading has no name")
            continue
        owner = f"Environment: {name}"
        problems += check_items(sections(body), 3, ENVIRONMENT_PARTS, owner + ": ", owner)
    if not environments:
        problems.append("deploying.md has no environment: add a `## Environment: <name>` section")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Prints 'complete' and exits 0 when every required item is there; otherwise prints "
               "one line per missing item and exits 1, including when the file does not exist. "
               "Exits 2 for a file not named releasing.md or deploying.md.")
    parser.add_argument("file", help="path to docs/practices/releasing.md or docs/practices/deploying.md")
    args = parser.parse_args(argv)

    base = os.path.basename(args.file)
    checks = {"releasing.md": check_releasing, "deploying.md": check_deploying}
    if base not in checks:
        print(f"{args.file}: expected releasing.md or deploying.md", file=sys.stderr)
        return 2
    topic = base[:-3]
    if not os.path.isfile(args.file):
        print(f"{base} is not recorded yet: record it with /agentic:practices {topic}")
        return 1
    with open(args.file, encoding="utf-8") as f:
        lines = f.read().splitlines()
    problems = checks[base](lines)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print(f"{base} is complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

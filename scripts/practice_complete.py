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

Headings match whatever their case, and every copy of a repeated heading is checked. Any other
heading is allowed and ignored. Only text counts as something under a heading: a heading below it,
an empty code block or an HTML comment does not. A required item whose text holds "(default)"
fails, since a default Claude proposed must not run against real systems. Lines inside code blocks
and HTML comments are never read as headings.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doc_references  # noqa: E402
import status_check  # noqa: E402

RELEASING = ("What may be released", "Version and its commit", "Publish")
ENVIRONMENT_PARTS = ("Releases allowed", "Deploy", "Check", "Roll back")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ENVIRONMENT = re.compile(r"^environment:\s*(.*)$", re.IGNORECASE)
DEFAULT = "(default)"


def without_comments(lines):
    """The lines with every HTML comment cut out, as the status hook finds them."""
    _, comments = status_check.scan(lines)
    out = list(lines)
    for (first, start), (last, end) in reversed(comments):
        if first == last:
            out[first] = out[first][:start] + out[first][end:]
        else:
            out[first] = out[first][:start]
            for k in range(first + 1, last):
                out[k] = ""
            out[last] = out[last][end:]
    return out


def entries(lines):
    """(heading level or 0, heading title or the line, fenced) for each line but fences and comments."""
    found = []
    for _, line, fenced in doc_references.marked_lines("\n".join(without_comments(lines))):
        match = None if fenced else HEADING.match(line)
        found.append((len(match.group(1)), match.group(2), False) if match else (0, line, fenced))
    return found


def sections(found):
    """Return (level, title, body entries) for each heading, the body running to the next heading
    at the same or a higher level."""
    result = []
    for n, (level, title, _) in enumerate(found):
        if not level:
            continue
        end = len(found)
        for j in range(n + 1, len(found)):
            if found[j][0] and found[j][0] <= level:
                end = j
                break
        result.append((level, title, found[n + 1:end]))
    return result


def judge(name, body, label):
    """Return a problem with one required item's text, or None. Only text counts: a heading below
    it, an empty code block or a comment does not."""
    text = "\n".join(line for level, line, _ in body if not level and line.strip())
    if not text:
        return f"{label}{name} has nothing under it"
    if DEFAULT in text.lower():
        return f"{label}{name} is a default: a required item must come from the person or the repository"
    return None


def check_items(found, level, names, label, owner):
    problems = []
    for name in names:
        copies = [body for lvl, title, body in found if lvl == level and title.strip().lower() == name.lower()]
        if not copies:
            problems.append(f"{owner} has no {name}")
        for body in copies:
            problem = judge(name, body, label)
            if problem and problem not in problems:
                problems.append(problem)
    return problems


def check_releasing(lines):
    return check_items(sections(entries(lines)), 2, RELEASING, "", "releasing.md")


def check_deploying(lines):
    problems = []
    environments = 0
    for level, title, body in sections(entries(lines)):
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
    with open(args.file, encoding="utf-8-sig") as f:
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

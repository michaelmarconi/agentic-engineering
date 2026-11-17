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

For deploying.md, `--environment <name>` judges only that environment, so a gap in another one
never blocks a deploy, while problems of the whole file are still shown. Without it, the script
also lists the environments recorded, so the deploy skill can tell when there is only one.
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


def check_deploying(lines, only=None):
    """Return (problems, environment names). With `only`, judge that environment's section and
    the file-wide problems, and name the environment when it has no section."""
    problems = []
    names = []
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
        if name.lower() not in (n.lower() for n in names):
            names.append(name)
        if only is not None and name.lower() != only.lower():
            continue
        owner = f"Environment: {name}"
        problems += check_items(sections(body), 3, ENVIRONMENT_PARTS, owner + ": ", owner)
    if not environments:
        problems.append("deploying.md has no environment: add a `## Environment: <name>` section")
    elif only is not None and only.lower() not in (n.lower() for n in names):
        problems.append(f"deploying.md has no environment named {only}")
    return problems, names


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Prints that the file is complete and exits 0 when every required item is there; "
               "otherwise prints one line per missing item and exits 1, including when the file "
               "does not exist. For deploying.md it also prints 'Environments recorded:' and the "
               "names, unless --environment names one that is there. Exits 2 for a file not named "
               "releasing.md or deploying.md, or --environment given with releasing.md.")
    parser.add_argument("file", help="path to docs/practices/releasing.md or docs/practices/deploying.md")
    parser.add_argument("--environment", metavar="NAME",
                        help="deploying.md only: judge only this environment's section, plus the "
                             "problems of the whole file (not recorded, no environment, an "
                             "Environment heading with no name); a gap in another environment "
                             "is ignored, and a name with no section is a problem")
    args = parser.parse_args(argv)

    base = os.path.basename(args.file)
    if base not in ("releasing.md", "deploying.md"):
        print(f"{args.file}: expected releasing.md or deploying.md", file=sys.stderr)
        return 2
    if args.environment is not None and base != "deploying.md":
        print("--environment is for deploying.md only", file=sys.stderr)
        return 2
    topic = base[:-3]
    if not os.path.isfile(args.file):
        print(f"{base} is not recorded yet: record it with /agentic:practices {topic}")
        return 1
    with open(args.file, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    names = []
    if base == "releasing.md":
        problems = check_releasing(lines)
    else:
        problems, names = check_deploying(lines, args.environment)
    for problem in problems:
        print(problem)
    known = args.environment is not None and args.environment.lower() in (n.lower() for n in names)
    if names and not known:
        print("Environments recorded: " + ", ".join(names))
    if problems:
        return 1
    if known:
        print(f"Environment: {args.environment} is complete")
    else:
        print(f"{base} is complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check that this repository's Markdown names document statuses by their exact value.

A status is its emoji and its word, such as `🟢 Ready to build`, and outside a status line it is
named in backticks, exactly as the status line has it. Reads every `.md` file under the root,
skipping hidden folders other than `.github`, and skipping `CHANGELOG.md`, whose past entries
stay as written, `evals/` and `evals-failed-check/`, whose prompts quote what a person types and
whose fixtures are documents, and `docs/adrs/`, whose decided records are never edited. A file's frontmatter, where the status line holds the
value bare, is skipped. It reports:

- a code span naming a status by its word with no emoji or the wrong one, such as `Accepted`;
- "Ready to build" outside a code span, since that phrase only ever means the status;
- a status with its emoji outside a code span, since emojis never sit in running prose;
- in a fenced code block, "Ready to build" without its emoji in front.

Draft, Built, Accepted, Rejected and Superseded on their own are ordinary words too, so prose
that names those statuses without backticks is left to the reader.
"""

import argparse
import os
import re
import sys

from doc_references import CODE_SPAN, FENCE, ROOT, markdown_files
from status_check import READY, WORDS, frontmatter, status_of

SKIPPED = {("CHANGELOG.md",), ("evals",), ("evals-failed-check",), ("docs", "adrs")}
EMOJI_VALUE = re.compile("|".join(re.escape(value) for value in WORDS.values()))
LEADING = re.compile(r"^[^A-Za-z]*")


def skipped(relative):
    parts = tuple(relative.split(os.sep))
    return any(parts[:len(skip)] == skip for skip in SKIPPED)


def span_problem(content):
    word = LEADING.sub("", content)
    if word not in WORDS:
        return None
    if status_of(f"---\nstatus: {content}\n---\n") == WORDS[word] and content.startswith(WORDS[word][0]):
        return None
    return f"`{content}` should be `{WORDS[word]}`"


def line_problems(line):
    found = []
    for match in CODE_SPAN.finditer(line):
        wrong = span_problem(match.group(0).strip("`").strip())
        if wrong:
            found.append(wrong)
    prose = CODE_SPAN.sub("", line)
    if EMOJI_VALUE.search(prose):
        found.append(f"'{EMOJI_VALUE.search(prose).group(0)}' should be in backticks")
    elif READY.split(" ", 1)[1] in prose:
        found.append(f"'Ready to build' should be `{READY}`")
    return found


def problems(root):
    root = os.path.abspath(root)
    found = []
    for source in markdown_files(root):
        relative = os.path.relpath(source, root)
        if skipped(relative):
            continue
        try:
            with open(source, encoding="utf-8") as f:
                text = f.read()
        except (OSError, ValueError):
            found.append(f"{relative}: can't be read as UTF-8 text")
            continue
        fence = None
        lines = text.splitlines()
        start = len(frontmatter(text) or []) + 2 if frontmatter(text) is not None else 0
        for number, line in enumerate(lines[start:], start + 1):
            match = FENCE.match(line)
            if fence:
                if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                    fence = None
                elif "Ready to build" in line.replace(READY, ""):
                    found.append(f"{relative}:{number}: 'Ready to build' should be '{READY}'")
                continue
            if match:
                fence = match.group(1)
                continue
            found.extend(f"{relative}:{number}: {wrong}" for wrong in line_problems(line))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Prints one line per problem, as `file:line: problem`, and exits 1 if there is any; "
               "prints nothing and exits 0 otherwise. Its tests run it on this repository, so "
               "`python3 -m unittest discover -s scripts` fails on a misnamed status.")
    parser.add_argument("root", nargs="?", default=ROOT, help="folder to check (default: this repository)")
    args = parser.parse_args(argv)
    found = problems(args.root)
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

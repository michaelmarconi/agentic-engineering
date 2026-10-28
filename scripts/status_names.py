#!/usr/bin/env python3
"""Check that this repository's Markdown names document statuses by their exact value.

A status is its emoji and its word, such as `🟢 Ready to build`, and outside a status line it is
named in backticks, exactly as the status line has it. Reads every `.md` file under the root,
skipping hidden folders other than `.github`, and skipping `CHANGELOG.md`, whose past entries
stay as written, `evals/` and `evals-failed-check/`, whose prompts quote what a person types and
whose fixtures are documents, and `docs/adrs/`, whose decided records are never edited. A file's frontmatter, where the status line holds the
value bare, is skipped. It reports:

- a code span naming a status by its word with no emoji or the wrong one, such as `Accepted`
  or `status: Accepted`;
- "Ready to build" without its emoji in front, anywhere, since that phrase only ever means the
  status, and outside a code span or fenced code block even with it;
- a status with its emoji outside a code span or fenced code block, since emojis never sit in
  running prose.

U+FE0F after an emoji is optional throughout, as it is for the status-check hook.

Draft, Built, Accepted, Rejected and Superseded on their own are ordinary words too, so prose
that names those statuses without backticks is left to the reader.
"""

import argparse
import os
import re
import sys

from doc_references import CODE_SPAN, ROOT, marked_lines, markdown_files
from status_check import READY, VARIATION, WITHOUT_VARIATION, WORDS, frontmatter, meant

SKIPPED = {("CHANGELOG.md",), ("evals",), ("evals-failed-check",), ("docs", "adrs")}
PHRASE = READY.split(" ", 1)[1]
# Statuses compare without U+FE0F, which is optional after an emoji.
EMOJI_VALUE = re.compile("|".join(re.escape(value) for value in WITHOUT_VARIATION))
STATUS_KEY = re.compile(r"status\s*:\s*", re.IGNORECASE)
# A code span may wrap onto the next line of its paragraph.
WRAPPED_SPAN = re.compile(CODE_SPAN.pattern, re.DOTALL)


def skipped(relative):
    parts = tuple(relative.split(os.sep))
    return any(parts[:len(skip)] == skip for skip in SKIPPED)


def loose_phrase(text):
    """True if "Ready to build" appears in `text` without its emoji in front."""
    return PHRASE in EMOJI_VALUE.sub("", text)


def span_problems(content):
    bare = content.replace(VARIATION, "")
    key = STATUS_KEY.match(bare)
    value = bare[key.end():] if key else bare
    full = meant(value, WORDS.values())
    if full and value != full.replace(VARIATION, ""):
        return [f"`{content}` should be `{(key.group(0) if key else '') + full}`"]
    if loose_phrase(bare):
        return [f"`{content}` should name `{READY}`"]
    return []


def paragraph_problems(first, lines):
    """Yield (line number, problem) for a paragraph whose first line is numbered `first`."""
    text = "\n".join(lines)
    for match in WRAPPED_SPAN.finditer(text):
        number = first + text.count("\n", 0, match.start())
        content = " ".join(match.group(0).strip("`").split())
        for wrong in span_problems(content):
            yield number, wrong
    prose = WRAPPED_SPAN.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for offset, line in enumerate(prose.replace(VARIATION, "").split("\n")):
        for value in EMOJI_VALUE.findall(line):
            yield first + offset, f"'{WITHOUT_VARIATION[value]}' should be in backticks"
        for _ in range(EMOJI_VALUE.sub("", line).count(PHRASE)):
            yield first + offset, f"'{PHRASE}' should be `{READY}`"


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
        head = frontmatter(text)
        # The status line in a file's frontmatter holds the value bare, so it is not checked.
        last = len(head) + 2 if head is not None else 0
        paragraphs = []
        for number, line, fenced in marked_lines(text):
            if number <= last:
                continue
            if fenced:
                if loose_phrase(line.replace(VARIATION, "")):
                    found.append(f"{relative}:{number}: '{PHRASE}' should be '{READY}'")
            elif line.strip():
                if paragraphs and paragraphs[-1][0] + len(paragraphs[-1][1]) == number:
                    paragraphs[-1][1].append(line)
                else:
                    paragraphs.append((number, [line]))
        for first, lines in paragraphs:
            found.extend(f"{relative}:{number}: {wrong}" for number, wrong in paragraph_problems(first, lines))
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

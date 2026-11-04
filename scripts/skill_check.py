#!/usr/bin/env python3
"""Check every skill's SKILL.md against the size and naming limits of the Agent Skills
specification (https://agentskills.io/specification), as AGENTS.md rule 3 sets them out.

For each skills/<folder>/SKILL.md under the given plugin root (default: this plugin):

- frontmatter holds `name` and `description`, each on one line;
- `name` is 1-64 lowercase letters, digits and single hyphens, matches its folder and holds
  neither reserved word, "anthropic" or "claude";
- `description` is 1-1,024 characters with no angle brackets;
- the body after the frontmatter is under 500 lines and about 5,000 tokens at most, estimated
  as one token per four characters;
- a skill that runs the review sequence on a document, which it shows by naming the shared
  `sdlc:correction-checker` agent, holds REVIEW_RULE word for word (line breaks may differ), so
  every such skill reviews at the same points, as the lifecycle page's Review process says.
  /build, whose checker is `sdlc:build-correction-checker`, reviews code and is not held to it.

Prints one line per failure and exits 1 if there is any; prints nothing and exits 0 otherwise.
Its tests run it on this plugin, so `python3 -m unittest discover -s scripts` fails on a skill
that breaks a limit.
"""

import argparse
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
RESERVED = ("anthropic", "claude")
MAX_NAME, MAX_DESCRIPTION, MAX_LINES, MAX_TOKENS = 64, 1024, 500, 5000
REVIEWS = "sdlc:correction-checker"
REVIEW_RULE = (
    "While you are walking through questions with the person, do not review after each "
    "answer: run the sequence once when the walk-through ends, either because no questions "
    "are left or because the person stops. A change the person makes or asks for at any other"
    " time is reviewed once it is made."
)


def frontmatter(text):
    """Return (fields, body), or None if the text does not open with a frontmatter block."""
    match = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not key.startswith((" ", "\t")):
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[key.strip()] = value
    return fields, match.group(2)


def problems(folder, text):
    parsed = frontmatter(text)
    if parsed is None:
        return ["no frontmatter"]
    fields, body = parsed
    found = []
    name = fields.get("name", "")
    if not name:
        found.append("name is missing")
    else:
        if len(name) > MAX_NAME:
            found.append(f"name is over {MAX_NAME} characters")
        if not NAME.fullmatch(name):
            found.append("name must be lowercase letters, digits and single hyphens")
        if name != folder:
            found.append(f"name '{name}' does not match its folder '{folder}'")
        if any(word in name for word in RESERVED):
            found.append("name holds a reserved word (anthropic, claude)")
    description = fields.get("description", "")
    if not description:
        found.append("description is missing")
    else:
        if len(description) > MAX_DESCRIPTION:
            found.append(f"description is {len(description):,} characters, over 1,024 characters")
        if "<" in description or ">" in description:
            found.append("description has angle brackets")
    lines = len(body.splitlines())
    if lines >= MAX_LINES:
        found.append(f"body is {lines} lines; it must be under {MAX_LINES} lines")
    tokens = len(body) // 4
    if tokens > MAX_TOKENS:
        found.append(f"body is about {tokens:,} tokens, over about 5,000 tokens")
    if REVIEWS in body and REVIEW_RULE not in " ".join(body.split()):
        found.append("review rule missing: a skill that runs the review sequence must hold "
                     "skill_check.REVIEW_RULE word for word")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", default=ROOT, help="plugin root (default: this plugin)")
    args = parser.parse_args(argv)
    skills = os.path.join(args.root, "skills")
    failed = False
    for folder in sorted(os.listdir(skills)) if os.path.isdir(skills) else []:
        path = os.path.join(skills, folder, "SKILL.md")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            for problem in problems(folder, f.read()):
                print(f"{folder}/SKILL.md: {problem}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

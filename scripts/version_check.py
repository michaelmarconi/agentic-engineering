#!/usr/bin/env python3
"""Check that the newest entry in CHANGELOG.md is for the version in .claude-plugin/plugin.json,
as the Workflow section of AGENTS.md asks: a version bump and its changelog entry land together.

An entry is a level-2 heading, which Keep a Changelog writes as `## [<version>] - <date>`
(https://keepachangelog.com/en/1.1.0/); its version is the bracketed text, or the heading's
first word if it has no brackets. `## [Unreleased]` is not an entry, but any other level-2
heading is, so a mistyped one such as `## [v0.4.0]` or `## 0.4.0` fails rather than being
skipped. Headings inside fenced code blocks don't count. Only the first entry counts, since the
file lists the newest version first.

Whether a change needed a bump at all is a judgement this script can't make.

Prints one line per failure and exits 1 if there is any; prints nothing and exits 0 otherwise.
Its tests run it on this plugin, so `python3 -m unittest discover -s scripts` fails when the
two disagree.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ENTRY = re.compile(r"^##[ \t]+(?:\[([^\]]*)\]|(\S+))", re.M)
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)


def problems(root):
    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    changelog = os.path.join(root, "CHANGELOG.md")
    found = []
    version = None
    if not os.path.isfile(manifest):
        found.append("plugin.json is missing")
    else:
        try:
            with open(manifest, encoding="utf-8") as f:
                fields = json.load(f)
        except (OSError, ValueError):
            fields = None
        if not isinstance(fields, dict):
            found.append("plugin.json is not a JSON object")
        else:
            version = fields.get("version")
            if version is None or version == "":
                found.append("plugin.json has no version")
            elif not isinstance(version, str):
                found.append("plugin.json version is not a string")
                version = None
    newest = None
    if not os.path.isfile(changelog):
        found.append("CHANGELOG.md is missing")
    else:
        try:
            with open(changelog, encoding="utf-8") as f:
                text = FENCE.sub("", f.read())
        except (OSError, ValueError):
            text = None
        if text is None:
            found.append("CHANGELOG.md can't be read as UTF-8 text")
        else:
            headings = [bracketed or word for bracketed, word in ENTRY.findall(text)]
            entries = [h for h in headings if h.strip().lower() != "unreleased"]
            if entries:
                newest = entries[0]
            else:
                found.append("CHANGELOG.md has no version entry")
    if version and newest and version != newest:
        found.append(f"plugin.json is at {version} but the newest CHANGELOG.md entry is {newest}")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", default=ROOT, help="plugin root (default: this plugin)")
    args = parser.parse_args(argv)
    found = problems(args.root)
    for problem in found:
        print(problem)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

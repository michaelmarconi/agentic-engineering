#!/usr/bin/env python3
"""Check that the newest entry in CHANGELOG.md is for the version in .claude-plugin/plugin.json,
as the Workflow section of AGENTS.md asks: a version bump and its changelog entry land together.

An entry is a heading of the form `## [<version>]`, as Keep a Changelog writes them
(https://keepachangelog.com/en/1.1.0/); `## [Unreleased]` is not an entry. Only the first entry
counts, since the file lists the newest version first.

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
ENTRY = re.compile(r"^## \[(\d[^\]]*)\]", re.M)


def problems(root):
    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    changelog = os.path.join(root, "CHANGELOG.md")
    found = []
    version = None
    if not os.path.isfile(manifest):
        found.append("plugin.json is missing")
    else:
        with open(manifest, encoding="utf-8") as f:
            version = json.load(f).get("version")
        if not version:
            found.append("plugin.json has no version")
    newest = None
    if not os.path.isfile(changelog):
        found.append("CHANGELOG.md is missing")
    else:
        with open(changelog, encoding="utf-8") as f:
            match = ENTRY.search(f.read())
        if match:
            newest = match.group(1)
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

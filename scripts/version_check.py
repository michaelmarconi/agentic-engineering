#!/usr/bin/env python3
"""Check that the newest entry in CHANGELOG.md is for the version in .claude-plugin/plugin.json,
as the Workflow section of AGENTS.md asks: a version bump and its changelog entry land together.

The plugin's version must read X.Y.Z (https://semver.org/spec/v2.0.0.html). Every line that
starts with `## `, after any indent, is a changelog heading; `## [Unreleased]` is skipped. The
first other heading is the newest entry and must read exactly `## [X.Y.Z] - YYYY-MM-DD`, as
Keep a Changelog writes them (https://keepachangelog.com/en/1.1.0/), so a mistyped one fails
rather than being skipped. Only that entry is compared, since the file lists the newest
version first.

Whether a change needed a bump at all is a judgement this script can't make.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SEMVER = re.compile(r"\d+\.\d+\.\d+")
HEADING = re.compile(r"\s*## ")
ENTRY = re.compile(r"## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}")
UNRELEASED = re.compile(r"## \[Unreleased\]", re.I)


def manifest_version(root):
    """Return (version, problem); exactly one is None."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(path):
        return None, "plugin.json is missing"
    try:
        with open(path, encoding="utf-8") as f:
            fields = json.load(f)
    except (OSError, ValueError):
        fields = None
    if not isinstance(fields, dict):
        return None, "plugin.json is not a JSON object"
    version = fields.get("version")
    if version is None or version == "":
        return None, "plugin.json has no version"
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        return None, f"plugin.json version must read X.Y.Z, not {version!r}"
    return version, None


def newest_entry(root):
    """Return (version, problem); exactly one is None."""
    path = os.path.join(root, "CHANGELOG.md")
    if not os.path.isfile(path):
        return None, "CHANGELOG.md is missing"
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, ValueError):
        return None, "CHANGELOG.md can't be read as UTF-8 text"
    for line in lines:
        if not HEADING.match(line) or UNRELEASED.fullmatch(line.strip()):
            continue
        match = ENTRY.fullmatch(line)
        if not match:
            return None, (f"the newest CHANGELOG.md heading must read "
                          f"'## [X.Y.Z] - YYYY-MM-DD', not '{line}'")
        return match.group(1), None
    return None, "CHANGELOG.md has no version entry"


def problems(root):
    version, manifest_problem = manifest_version(root)
    newest, changelog_problem = newest_entry(root)
    found = [p for p in (manifest_problem, changelog_problem) if p]
    if version and newest and version != newest:
        found.append(f"plugin.json is at {version} but the newest CHANGELOG.md entry is {newest}")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Prints one line per problem and exits 1 if there is any; prints nothing and "
               "exits 0 otherwise. Its tests run it on this plugin, so `python3 -m unittest "
               "discover -s scripts` fails when the two disagree.")
    parser.add_argument("root", nargs="?", default=ROOT, help="plugin root (default: this plugin)")
    args = parser.parse_args(argv)
    found = problems(args.root)
    for problem in found:
        print(problem)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

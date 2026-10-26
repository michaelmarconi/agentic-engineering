#!/usr/bin/env python3
"""Gather context for, and file, an issue against the sdlc plugin's own repository.

The repository is read from the `repository` field of the plugin's
`.claude-plugin/plugin.json`, found by walking up from this script, so a fork files against
itself.

Commands:
  context   Print the Context lines for an issue: plugin version, Claude Code version, OS.
  file      File an issue whose body is read from standard input. Uses the GitHub CLI
            (`gh`) when it is installed and signed in; otherwise, or if `gh` fails, prints a
            link that opens GitHub's new-issue page already filled in.

Run `issue.py <command> --help` for each command's arguments, output and exit codes.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from urllib.parse import urlencode

LABELS = {"bug": "bug", "improvement": "enhancement"}

# GitHub answers 414 URI Too Long somewhere above this; it does not publish the limit.
MAX_URL = 8000


def run(args, input=None):
    return subprocess.run(args, input=input, capture_output=True, text=True, timeout=60)


def plugin_root():
    path = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(path, ".claude-plugin", "plugin.json")):
        parent = os.path.dirname(path)
        if parent == path:
            raise FileNotFoundError("no .claude-plugin/plugin.json above " + __file__)
        path = parent
    return path


def read_manifest(root):
    with open(os.path.join(root, ".claude-plugin", "plugin.json")) as f:
        return json.load(f)


def repo_slug(repository):
    """Return owner/name for a GitHub repository URL, string or {"url": ...} form."""
    url = repository.get("url", "") if isinstance(repository, dict) else repository or ""
    match = re.match(r"^(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise ValueError("plugin.json repository is not a GitHub repository: %r" % url)
    return match.group(1) + "/" + match.group(2)


def new_issue_link(slug, title, body, label):
    query = urlencode({"title": title, "body": body, "labels": label})
    return "https://github.com/%s/issues/new?%s" % (slug, query)


def claude_version():
    try:
        result = run(["claude", "--version"])
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def context(root):
    manifest = read_manifest(root)
    return "\n".join([
        "- Plugin: %s %s" % (manifest.get("name", "sdlc"), manifest.get("version", "unknown")),
        "- Claude Code: " + claude_version(),
        "- OS: %s %s" % (platform.system(), platform.release()),
    ]) + "\n"


def gh_filed(slug, title, body, label):
    """Try to file with gh; return the new issue's URL, or None if gh can't."""
    if not shutil.which("gh"):
        return None
    try:
        if run(["gh", "auth", "status"]).returncode != 0:
            return None
        result = run(["gh", "issue", "create", "--repo", slug, "--title", title,
                      "--label", label, "--body-file", "-"], input=body)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = result.stdout.strip().splitlines()
    return lines[-1] if result.returncode == 0 and lines else None


def file_issue(root, kind, title, body, link_only=False):
    if not title.strip() or not body.strip():
        print("issue.py: the title and body must not be empty", file=sys.stderr)
        return 2
    slug = repo_slug(read_manifest(root).get("repository"))
    label = LABELS[kind]
    if not link_only:
        url = gh_filed(slug, title, body, label)
        if url:
            print("filed " + url)
            return 0
    link = new_issue_link(slug, title, body, label)
    if len(link) > MAX_URL:
        print("issue.py: the issue is too long to fit in a link (%d characters, limit %d); "
              "shorten the body" % (len(link), MAX_URL), file=sys.stderr)
        return 3
    print("link " + link)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "context",
        help="print the Context lines for an issue",
        description="Print Markdown list lines naming the plugin version, the Claude Code "
                    "version (\"unknown\" if `claude` can't be run) and the OS. Exit code 0.",
    )
    filer = commands.add_parser(
        "file",
        help="file an issue, body on standard input",
        description="File an issue on the plugin's repository with the body read from "
                    "standard input. Prints one line: \"filed <issue URL>\" if gh filed it, or "
                    "\"link <URL>\" for the person to open and submit. Exit codes: 0 done, "
                    "2 bad arguments or empty title/body, 3 no gh and the issue is too long "
                    "for a link.",
    )
    filer.add_argument("--kind", required=True, choices=sorted(LABELS),
                       help="bug or improvement; sets the label (bug or enhancement)")
    filer.add_argument("--title", required=True, help="the issue title")
    filer.add_argument("--link-only", action="store_true",
                       help="never run gh; always print the link")
    args = parser.parse_args(argv)
    root = plugin_root()
    if args.command == "context":
        sys.stdout.write(context(root))
        return 0
    return file_issue(root, args.kind, args.title, sys.stdin.read(), args.link_only)


if __name__ == "__main__":
    sys.exit(main())

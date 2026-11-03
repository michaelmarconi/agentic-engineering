#!/usr/bin/env python3
"""While /build runs, refuse a git commit or push on the repository's default branch.

Claude Code runs this as a PreToolUse hook on Bash. It acts only in a session where /build was
allowed to start (recorded by fresh_session.py). There it refuses a shell command that runs
`git commit` while the default branch is checked out, or `git push` while it is checked out or
naming it as the branch to push to, such as `HEAD:main`. The default branch is the one
`origin/HEAD` names, or `main` or `master` when there is none. Every other command, and every
command outside a build, is left alone.

A commit or push made some other way, such as from a script the command runs, is not seen;
the hand-over script refuses the default branch itself.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys

import fresh_session

REASON = (
    "/build never commits or pushes to the default branch, `{branch}`, so your main line only "
    "changes when you merge. Commit on the build's own branch instead."
)
# Options of git itself that take the next word as their value.
VALUED = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def git_output(cwd, *args):
    try:
        result = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def defaults(cwd):
    remote = git_output(cwd, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    return {remote.split("/", 1)[-1]} if remote else {"main", "master"}


def git_calls(command):
    """Each git subcommand the command runs, with the words after it."""
    calls = []
    for part in re.split(r"&&|\|\||[;|\n&]", command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and "=" in words[0] and not words[0].startswith("-"):
            words = words[1:]
        if not words or words[0].rsplit("/", 1)[-1] != "git":
            continue
        rest = words[1:]
        while rest and rest[0].startswith("-"):
            rest = rest[2:] if rest[0] in VALUED else rest[1:]
        if rest:
            calls.append((rest[0], rest[1:]))
    return calls


def names_branch(words, branches):
    for word in words:
        target = word.split(":", 1)[-1].lstrip("+")
        if target.startswith("refs/heads/"):
            target = target[len("refs/heads/"):]
        if target in branches:
            return True
    return False


def problem(event):
    if event.get("tool_name") != "Bash" or not fresh_session.building(event.get("session_id")):
        return None
    command = str((event.get("tool_input") or {}).get("command") or "")
    calls = [c for c in git_calls(command) if c[0] in ("commit", "push")]
    if not calls:
        return None
    cwd = event.get("cwd") or "."
    branches = defaults(cwd)
    current = git_output(cwd, "symbolic-ref", "--quiet", "--short", "HEAD")
    for name, words in calls:
        if current in branches or (name == "push" and names_branch(words[1:], branches)):
            return REASON.format(branch=sorted(branches)[0] if current not in branches else current)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1] + "\nReads one PreToolUse event as JSON from stdin. "
               "Prints a refusal as JSON, or nothing. Always exits 0.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    reason = problem(event) if isinstance(event, dict) else None
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

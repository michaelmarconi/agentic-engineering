#!/usr/bin/env python3
"""While /build runs, refuse a git commit or push on the repository's default branch.

Claude Code runs this as a PreToolUse hook on Bash. It acts only in a session where /build was
allowed to start (recorded by fresh_session.py). There it refuses a shell command that runs
`git commit` while the default branch is checked out, or `git push` while it is checked out or
naming it as the branch to push to, such as `HEAD:main`, or pushing every branch with `--all` or
`--mirror`. It follows a `git checkout` or `git switch` earlier in the same command. The default branch is the one
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
    """The default branch a push names as its target, or None."""
    for word in (w for w in words if not w.startswith("-")):
        target = word.split(":", 1)[-1].lstrip("+")
        if target.startswith("refs/heads/"):
            target = target[len("refs/heads/"):]
        if target in branches:
            return target
    return None


def switched_to(name, words):
    """The branch a `git checkout` or `git switch` moves to, or None."""
    words = [w for w in words if w != "--"]
    for flag in ("-b", "-B", "-c", "-C", "--orphan"):
        if flag in words and words.index(flag) + 1 < len(words):
            return words[words.index(flag) + 1]
    plain = [w for w in words if not w.startswith("-")]
    return plain[0] if len(plain) == 1 else None


def problem(event):
    if event.get("tool_name") != "Bash" or not fresh_session.building(event.get("session_id")):
        return None
    command = str((event.get("tool_input") or {}).get("command") or "")
    calls = git_calls(command)
    if not any(name in ("commit", "push") for name, _ in calls):
        return None
    cwd = event.get("cwd") or "."
    branches = defaults(cwd)
    # Follow the command's own branch changes, so `git checkout -b x && git commit` is judged on x.
    current = git_output(cwd, "symbolic-ref", "--quiet", "--short", "HEAD")
    for name, words in calls:
        if name in ("checkout", "switch"):
            current = switched_to(name, words) or current
        elif name == "commit" and current in branches:
            return REASON.format(branch=current)
        elif name == "push":
            if current in branches:
                return REASON.format(branch=current)
            if "--all" in words or "--mirror" in words:
                return REASON.format(branch=" or ".join(sorted(branches)))
            named = names_branch(words[1:], branches)
            if named:
                return REASON.format(branch=named)
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

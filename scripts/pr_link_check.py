#!/usr/bin/env python3
"""Refuse a pull request description holding a link longer than 150 characters.

Claude Code runs this as a PreToolUse hook on Bash and on any MCP tool named
`mcp__<server>__create_pull_request` or `mcp__<server>__update_pull_request`, as ADR 0056 decides.
On GitHub, a link address over about 150 characters in a pull request description was seen saved
as code-formatted text rather than as a working link, so the hook refuses the request before it is
sent, lists each long link with its length, and says how to shorten it.

For a GitHub tool it reads the `body` argument. For a shell command that runs `gh pr create` or
`gh pr edit` it reads the whole command, which holds a `--body` value or a here-document, and the
file named by `--body-file` or `-F`, relative to the event's working folder, when it can be read.
A link is any `http` or `https` address, in a Markdown link or bare, measured with its heading
anchor. Every other tool call and command, a request it cannot read, and an unreadable body file
pass.
"""

import argparse
import json
import os
import re
import shlex
import sys

LIMIT = 150
TOOL = re.compile(r"^mcp__.+__(create|update)_pull_request$")
ADDRESS = re.compile(r"""https?://[^\s<>()\[\]{}"'`\\]+""")
TRAILING = ".,;:!?*_~"
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n"}
GH_FALLBACK = re.compile(r"(?:^|[;&|(\n])\s*(?:\S*/)?gh\s+pr\s+(?:create|edit)\b")
BODY_FILE = re.compile(r"(?:--body-file|-F)(?:=|\s+)(\"[^\"]*\"|'[^']*'|\S+)")
TEMPLATE_SENTENCE = (
    "Pin each link to the commit's 7-character id rather than the full one: GitHub can show a link "
    "longer than 150 characters as plain text, and a plugin hook refuses one.")
REASON = (
    "This pull request description holds {count} longer than {limit} characters, which GitHub can "
    "show as plain text instead of a working link:\n{links}\nPin each file link to the commit's "
    "7-character id rather than the full 40-character one; GitHub accepts it in the same place. If "
    "a link is still too long, link the file without its heading anchor and name the heading in "
    "the text. Then try again.")


def long_links(text):
    """Each distinct address in text longer than LIMIT, in order of first appearance."""
    found = []
    for match in ADDRESS.finditer(text):
        address = match.group(0).rstrip(TRAILING)
        if len(address) > LIMIT and address not in found:
            found.append(address)
    return found


def words(command):
    """The command's shell words, with separators such as && as words of their own, or None."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return None


def runs_gh_pr(command, split):
    """Whether the command runs `gh pr create` or `gh pr edit`."""
    if split is None:
        return bool(GH_FALLBACK.search(command))
    for i, word in enumerate(split):
        if (os.path.basename(word) == "gh" and (i == 0 or split[i - 1] in SEPARATORS)
                and split[i + 1:i + 2] == ["pr"] and split[i + 2:i + 3] in (["create"], ["edit"])):
            return True
    return False


def body_files(command, split):
    """The paths named by --body-file or -F, leaving out `-` (standard input)."""
    paths = []
    if split is None:
        paths = [m.group(1).strip("\"'") for m in BODY_FILE.finditer(command)]
    else:
        for i, word in enumerate(split):
            if word in ("--body-file", "-F") and i + 1 < len(split):
                paths.append(split[i + 1])
            elif word.startswith("--body-file="):
                paths.append(word.split("=", 1)[1])
    return [p for p in paths if p and p != "-"]


def read(path, cwd):
    try:
        with open(os.path.join(cwd, os.path.expanduser(path)), encoding="utf-8") as f:
            return f.read()
    except (OSError, ValueError):
        return ""


def description(event):
    """The text to check, or None when the event is not a pull request being created or edited."""
    name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if not isinstance(name, str) or not isinstance(tool_input, dict):
        return None
    if TOOL.match(name):
        body = tool_input.get("body")
        return body if isinstance(body, str) else None
    if name != "Bash":
        return None
    command = tool_input.get("command")
    if not isinstance(command, str):
        return None
    split = words(command)
    if not runs_gh_pr(command, split):
        return None
    cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else "."
    return "\n".join([command] + [read(p, cwd) for p in body_files(command, split)])


def problem(event):
    """The refusal's reason, or None when the request may go ahead."""
    text = description(event) if isinstance(event, dict) else None
    links = long_links(text) if text else []
    if not links:
        return None
    count = "a link" if len(links) == 1 else "%d links" % len(links)
    listed = "\n".join("- %s (%d characters)" % (link, len(link)) for link in links)
    return REASON.format(count=count, limit=LIMIT, links=listed)


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
    reason = problem(event)
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

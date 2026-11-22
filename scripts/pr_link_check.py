#!/usr/bin/env python3
"""Refuse a pull request description that is not written out, or that holds a link over 150 characters.

Claude Code runs this as a PreToolUse hook on Bash and on any MCP tool named
`mcp__<server>__create_pull_request` or `mcp__<server>__update_pull_request`, as ADR 0057 decides.
On GitHub, a link address over about 150 characters in a pull request description was seen saved
as code-formatted text rather than as a working link, so the hook refuses the request before it is
sent, lists each long link with its length, and says how to shorten it.

For a GitHub tool it reads the `body` argument, which is always written out. For a shell command it
reads each `gh pr create` or `gh pr edit` the command runs, on any line and after any variable
settings: that command's own words, which hold a `--body` value, any here-document on its line,
and the file named by `--body-file` or `-F`, found from the event's working folder and any `cd`
before it. Other commands in the same chain are not read. A `gh` description is not written out,
and is refused, when a body file it names cannot be read, when it reads standard input with no
here-document on its line, or when a link in it is built by the shell, such as `$B/docs/...` or
`$(git rev-parse HEAD)`; a `$` elsewhere in the text is left alone. A link is any `http` or `https`
address, in a Markdown link or bare, measured with its heading anchor. Every other tool call and
command passes.
"""

import argparse
import json
import os
import re
import shlex
import sys

LIMIT = 150
TOOL = re.compile(r"^mcp__.+__(create|update)_pull_request$")
ADDRESS = re.compile(r"""https?://[^\s<>\[\]{}"'`\\]+""")
TRAILING = ".,;:!?*_~"
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SHELL_LINK = re.compile(r"\]\(\s*\$|https?://[^\s<>\[\]{}\"'`]*\$")
NOT_WRITTEN_OUT = (
    "The hook could not check this pull request description's links, because the description is "
    "not written out yet: {what}. Write the description file in one command and run gh in the "
    "next, or pass the description inline with every link written out in full, then try again.")
TEMPLATE_SENTENCE = (
    "Pin each link to the commit's 7-character id rather than the full one: GitHub can show a link "
    "longer than 150 characters as plain text, and a plugin hook refuses one.")
REASON = (
    "This pull request description holds {count} longer than {limit} characters, which GitHub can "
    "show as plain text instead of a working link:\n{links}\nPin each file link to the commit's "
    "7-character id rather than the full 40-character one; GitHub accepts it in the same place. If "
    "a link is still too long, link the file without its heading anchor and name the heading in "
    "the text. Then try again.")


def trimmed(address):
    """The address without trailing punctuation or a closing parenthesis it did not open."""
    while True:
        before = address
        address = address.rstrip(TRAILING)
        if address.endswith(")") and address.count("(") < address.count(")"):
            address = address[:-1]
        if address == before:
            return address


def long_links(text):
    """Each distinct address in text longer than LIMIT, in order of first appearance."""
    found = []
    for match in ADDRESS.finditer(text):
        address = trimmed(match.group(0))
        if len(address) > LIMIT and address not in found:
            found.append(address)
    return found


def lines_and_heredocs(command):
    """The command's lines with here-document bodies taken out, and each line's bodies."""
    lines, bodies = [], []
    rows = command.split("\n")
    i = 0
    while i < len(rows):
        line = rows[i]
        i += 1
        held = []
        for match in HEREDOC.finditer(line):
            text = []
            while i < len(rows) and rows[i].strip() != match.group(2):
                text.append(rows[i])
                i += 1
            i += 1
            held.append("\n".join(text))
        lines.append(line)
        bodies.append(held)
    return lines, bodies


def segments(line):
    """The simple commands on one line, split at ;, &, | and && outside quotes."""
    parts, current, quote, escaped = [], [], None, False
    for char in line:
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            quote = None if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char in ";&|":
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return [p for p in parts if p.strip()]


def words(segment):
    """A simple command's words, leaving out variable settings and `env` or `command` in front."""
    try:
        split = shlex.split(segment)
    except ValueError:
        split = segment.split()
    while split and (("=" in split[0] and not split[0].startswith("-"))
                     or split[0] in ("env", "command")):
        split = split[1:]
    return split


def body_files(split):
    """The paths a gh command names by --body-file or -F, leaving out `-` (standard input)."""
    paths = []
    for i, word in enumerate(split):
        if word in ("--body-file", "-F") and i + 1 < len(split):
            paths.append(split[i + 1])
        elif word.startswith("--body-file="):
            paths.append(word.split("=", 1)[1])
    return [p for p in paths if p and p != "-"]


def read(path, folder):
    try:
        path = os.path.expanduser(os.path.expandvars(path))
        with open(os.path.join(folder, path), encoding="utf-8") as f:
            return f.read()
    except (OSError, ValueError):
        return None


def gh_descriptions(command, cwd):
    """For each `gh pr create` or `gh pr edit` the command runs: its text, from its own words, any
    here-document on its line and any body file read from the folder an earlier `cd` moved to, and
    what of it could not be read."""
    found = []
    folder = cwd
    lines, bodies = lines_and_heredocs(command)
    for line, held in zip(lines, bodies):
        for segment in segments(line):
            split = words(segment)
            if not split:
                continue
            if split[0] == "cd" and len(split) > 1:
                folder = os.path.join(folder, os.path.expanduser(os.path.expandvars(split[1])))
            elif (os.path.basename(split[0]) == "gh" and split[1:2] == ["pr"]
                  and split[2:3] in (["create"], ["edit"])):
                texts, missing = [segment] + held, []
                for path in body_files(split):
                    text = read(path, folder)
                    if text is None:
                        missing.append("the body file %s cannot be read" % path)
                    else:
                        texts.append(text)
                if reads_stdin(split) and not held:
                    missing.append("it reads standard input with no here-document")
                found.append(("\n".join(texts), missing))
    return found


def reads_stdin(split):
    for i, word in enumerate(split):
        if (word in ("--body-file", "-F") and split[i + 1:i + 2] == ["-"]) or word == "--body-file=-":
            return True
    return False


def description(event):
    """The text to check and what of it is not written out, or None when the event is not a pull
    request being created or edited."""
    name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if not isinstance(name, str) or not isinstance(tool_input, dict):
        return None
    if TOOL.match(name):
        body = tool_input.get("body")
        return (body, []) if isinstance(body, str) else None
    if name != "Bash":
        return None
    command = tool_input.get("command")
    if not isinstance(command, str):
        return None
    cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else "."
    found = gh_descriptions(command, cwd)
    if not found:
        return None
    text = "\n".join(t for t, _ in found)
    missing = [m for _, ms in found for m in ms]
    if SHELL_LINK.search(text):
        missing.append("a link in it is built by the shell, such as from a variable")
    return text, missing


def problem(event):
    """The refusal's reason, or None when the request may go ahead."""
    found = description(event) if isinstance(event, dict) else None
    if not found:
        return None
    text, missing = found
    if missing:
        return NOT_WRITTEN_OUT.format(what="; ".join(missing))
    links = long_links(text)
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

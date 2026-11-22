#!/usr/bin/env python3
"""Refuse a pull request description that is not written out, or that holds a link over 150 characters.

Claude Code runs this as a PreToolUse hook on Bash and on any MCP tool named
`mcp__<server>__create_pull_request` or `mcp__<server>__update_pull_request`, as ADR 0057 decides.
On GitHub, a link address over about 150 characters in a pull request description was seen saved
as code-formatted text rather than as a working link, so the hook refuses the request before it is
sent, lists each long link with its length, and says how to shorten it.

For a GitHub tool it reads the `body` argument, which is always written out. For a shell command it
reads each `gh pr create` or `gh pr edit` the command runs, on any line and after any variable
settings: its `--body` values, the here-document or here-string that feeds it, and the file named
by `--body-file` or `-F`, found from the event's working folder and any `cd` before it. Other
commands in the same chain are read only for the files they write. A `gh` description is not
written out, and is refused, when the shell would build any of it (a `$NAME`, `${...}`, `$(...)` or
backticks the shell expands), when its body file cannot be read, is named by a variable, sits in a
folder a `cd` hides, or is written by the same command, or when it reads standard input from
anything but its own here-document or here-string. A `$` the shell leaves alone, such as in single
quotes, a quoted here-document, a body file or "$5", is text. A link is any `http` or `https`
address, in a Markdown link or bare, measured with its heading anchor. Every other tool call and
command passes.
"""

import argparse
import json
import os
import re
import sys

LIMIT = 150
TOOL = re.compile(r"^mcp__.+__(create|update)_pull_request$")
ADDRESS = re.compile(r"""https?://[^\s<>\[\]{}"'`\\]+""")
TRAILING = ".,;:!?*_~"
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
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
    """The command's lines with here-document bodies taken out, and each line's bodies in order."""
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


class Word:
    """One shell word: its value with quotes removed, and whether the shell would expand any of it."""

    def __init__(self):
        self.value, self.expands, self.quoted = "", False, False


def tokens(line):
    """The line's words and operators, quote-aware: a Word, or an operator string such as "&&",
    "|", ";", "<", ">", "<<" or "<<<"."""
    out, word, quote, i = [], None, None, 0

    def finish():
        nonlocal word
        if word is not None:
            out.append(word)
            word = None

    while i < len(line):
        char = line[i]
        if quote == "'":
            if char == "'":
                quote = None
            else:
                word.value += char
        elif quote == '"':
            if char == '"':
                quote = None
            elif char == "\\" and i + 1 < len(line):
                i += 1
                word.value += line[i]
            else:
                word.value += char
                if char in "$`":
                    word.expands = True
        elif char in "'\"":
            if word is None:
                word = Word()
            word.quoted = True
            quote = char
        elif char == "\\" and i + 1 < len(line):
            if word is None:
                word = Word()
            i += 1
            word.value += line[i]
        elif char.isspace():
            finish()
        elif char in ";&|<>":
            finish()
            op = char
            while i + 1 < len(line) and line[i + 1] in "&|<>" and len(op) < 3 and (
                    op + line[i + 1]) in ("&&", "||", "<<", "<<<", ">>", ">&", "&>", ">|"):
                i += 1
                op += line[i]
            out.append(op)
        else:
            if word is None:
                word = Word()
            word.value += char
            if char in "$`":
                word.expands = True
        i += 1
    finish()
    return out


SEPARATORS = (";", "&&", "||", "|", "&")
STDIN_PATHS = ("-", "/dev/stdin", "/dev/fd/0", "/proc/self/fd/0")
EXPANSION = re.compile(r"\$[A-Za-z_{(]|`")


def simple_commands(line, held):
    """Each simple command on the line, as (words, separator before it, redirections), with the
    here-documents on the line handed to the commands whose `<<` they follow."""
    held = list(held)
    commands, current, redirects, before = [], [], [], None
    items = tokens(line)
    i = 0
    while i < len(items):
        item = items[i]
        if isinstance(item, str) and item in SEPARATORS:
            commands.append((current, before, redirects))
            current, redirects, before = [], [], item
        elif isinstance(item, str):
            target = items[i + 1] if i + 1 < len(items) and isinstance(items[i + 1], Word) else None
            if item == "<<":
                redirects.append(("<<", held.pop(0) if held else "", target is not None and target.quoted))
            elif target is not None:
                redirects.append((item, target.value, target.expands))
            i += 1
        else:
            current.append(item)
        i += 1
    commands.append((current, before, redirects))
    return [c for c in commands if c[0] or c[2]]


def command_words(words):
    """The words without variable settings and `env` or `command` in front."""
    while words and (("=" in words[0].value and not words[0].value.startswith("-"))
                     or words[0].value in ("env", "command")):
        words = words[1:]
    return words


def is_gh_pr(words):
    values = [w.value for w in words]
    return (bool(values) and os.path.basename(values[0]) == "gh" and values[1:2] == ["pr"]
            and values[2:3] in (["create"], ["edit"]))


def body_args(words):
    """The gh command's --body values (as Words) and --body-file paths (as Words)."""
    bodies, files = [], []
    for i, word in enumerate(words):
        nxt = words[i + 1] if i + 1 < len(words) else None
        if word.value in ("-b", "--body") and nxt is not None:
            bodies.append(nxt)
        elif word.value.startswith("--body="):
            part = Word()
            part.value, part.expands = word.value.split("=", 1)[1], word.expands
            bodies.append(part)
        elif word.value in ("-F", "--body-file") and nxt is not None:
            files.append(nxt)
        elif word.value.startswith("--body-file="):
            part = Word()
            part.value, part.expands = word.value.split("=", 1)[1], word.expands
            files.append(part)
    return bodies, files


def read(path, folder):
    try:
        with open(os.path.join(folder, os.path.expanduser(path)), encoding="utf-8") as f:
            return f.read()
    except (OSError, ValueError):
        return None


def written_files(words, redirects):
    """The files a non-gh command writes, by redirection or `tee`."""
    paths = [target for op, target, _ in redirects if op in (">", ">>", ">|", "&>")]
    values = [w.value for w in words]
    if values and os.path.basename(values[0]) == "tee":
        paths += [v for v in values[1:] if not v.startswith("-")]
    return paths


def gh_descriptions(command, cwd):
    """For each `gh pr create` or `gh pr edit` the command runs: the description's text, from its
    --body values, the here-document or here-string feeding it and its body file, and what of it is
    not written out."""
    found, written = [], set()
    folder, lost = cwd, False
    lines, bodies = lines_and_heredocs(command)
    for line, held in zip(lines, bodies):
        for words, before, redirects in simple_commands(line, held):
            words = command_words(words)
            values = [w.value for w in words]
            if values[:1] == ["cd"]:
                target = words[1] if len(words) > 1 else None
                if target is None:
                    folder = os.path.expanduser("~")
                elif target.expands or target.value == "-":
                    lost = True
                else:
                    folder = os.path.join(folder, os.path.expanduser(target.value))
                continue
            if not is_gh_pr(words):
                written.update(os.path.normpath(os.path.join(folder, p))
                               for p in written_files(words, redirects))
                continue
            texts, missing = [], []
            body_values, files = body_args(words)
            for body in body_values:
                if body.expands and EXPANSION.search(body.value):
                    missing.append("its --body is built by the shell, such as from a variable")
                else:
                    texts.append(body.value)
            stdin = [r for r in redirects if r[0] in ("<", "<<", "<<<")]
            for path in files:
                if path.value in STDIN_PATHS:
                    if before == "|" or any(op == "<" for op, _, _ in stdin):
                        missing.append("it reads standard input from another command or file")
                    elif not any(op in ("<<", "<<<") for op, _, _ in stdin):
                        missing.append("it reads standard input with no here-document")
                    for op, text, flag in stdin:
                        expands = (op == "<<" and not flag) or (op == "<<<" and flag)
                        if expands and EXPANSION.search(text):
                            missing.append("its here-document is built by the shell, such as "
                                           "from a variable")
                        elif op != "<":
                            texts.append(text)
                elif path.expands:
                    missing.append("the body file %s is named by a variable" % path.value)
                elif lost and not os.path.isabs(os.path.expanduser(path.value)):
                    missing.append("the folder an earlier cd moves to cannot be worked out")
                elif os.path.normpath(os.path.join(folder, os.path.expanduser(path.value))) in written:
                    missing.append("the body file %s is written by the same command" % path.value)
                else:
                    text = read(path.value, folder)
                    if text is None:
                        missing.append("the body file %s cannot be read" % path.value)
                    else:
                        texts.append(text)
            found.append(("\n".join(texts), missing))
    return found


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
    return "\n".join(t for t, _ in found), [m for _, ms in found for m in ms]


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

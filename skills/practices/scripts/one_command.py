#!/usr/bin/env python3
"""Check that a step's command is one command, as docs/adrs/0041 defines it.

`/practices` runs this on the commands it is about to record. One command is one line that calls
one program with its arguments, where `{name}` marks a value the skill running the step fills in.
The line is split as a shell would split it, so text inside quotes is left alone, and `#` is never
taken as a comment. It fails when, outside quotes, it holds `;`, `|` or an `&` that is not part of
a redirection such as `2>&1`, since those run more than one command or run one in the background.
It fails too on a line break, an unclosed quote, an empty line, a placeholder written `<name>`
rather than `{name}`, and a shell given a command string, such as `sh -c '...'`, even behind a
prefix such as `FOO=1`, `env` or `sudo`, since that string can hold several commands. Redirections
pass. Whether the command needs no answer from a person and exits 0 on success is not something a
script can tell from its text: the skill judges that.

Give it every command of a run at once, one per line on standard input, such as through a quoted
heredoc (`<<'EOF'`), so no quote inside a command can break the call; each may instead be its own
argument.

Output: one line per command, saying "one command" or why it is not one.

Exit codes: 0 when every command is one command; 1 when any is not; 2 on a usage error, such as no
command given.
"""

import argparse
import re
import shlex
import sys

SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
PREFIXES = {"env", "sudo", "exec", "nohup", "command", "time"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
REDIRECT_AMPERSAND = re.compile(r"[<>]&|&>>?")
ANGLE_PLACEHOLDER = re.compile(r"<[A-Za-z][\w-]*>")


def separator(token):
    """The separator a punctuation token holds, or None for a plain redirection."""
    for mark in ("&&", "||", ";", "|"):
        if mark in token:
            return mark
    if "&" in REDIRECT_AMPERSAND.sub("", token):
        return "&"
    return None


def shell_string(tokens):
    """True when the program, after any prefix, is a shell given -c before its first argument."""
    i = 0
    while i < len(tokens) and (ASSIGNMENT.match(tokens[i]) or tokens[i].rsplit("/", 1)[-1] in PREFIXES):
        i += 1
    if i >= len(tokens) or tokens[i].rsplit("/", 1)[-1] not in SHELLS:
        return False
    for token in tokens[i + 1:]:
        if not token.startswith("-"):
            return False
        if not token.startswith("--") and "c" in token:
            return True
    return False


def problem(command):
    """None when the command is one command; otherwise the reason it is not."""
    if not command.strip():
        return "the command is empty"
    if "\n" in command or "\r" in command:
        return "the command spans more than one line"
    if command.lstrip().startswith("#"):
        return "the command is a comment"
    if ANGLE_PLACEHOLDER.search(command):
        return "the command marks a value as `<name>`; write `{name}` for a value the skill fills in"
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return "the command has an unclosed quote"
    for token in tokens:
        if token and set(token) <= set("();<>|&"):
            mark = separator(token)
            if mark:
                return f"the command holds `{mark}`, so it runs more than one command or runs one in the background"
    if shell_string(tokens):
        return "the command gives a shell a command string, which can hold several commands"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check that each step's command is one command (docs/adrs/0041).",
        epilog="Exit codes: 0 when every command is one command; 1 when any is not; 2 on a usage error.",
    )
    parser.add_argument("commands", nargs="*", metavar="command",
                        help="a command to check, quoted as one argument; with none, read one per line from standard input")
    args = parser.parse_args(argv)
    commands = args.commands or [line for line in sys.stdin.read().splitlines() if line.strip()]
    if not commands:
        parser.error("give at least one command, as an argument or on standard input")
    failed = False
    for command in commands:
        reason = problem(command)
        if reason is None:
            print(f"`{command}`: one command")
        else:
            failed = True
            print(f"`{command}`: not one command: {reason}. Put its steps in an entry of the project's "
                  "runner or scripts folder, and record the one-line command that runs it.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

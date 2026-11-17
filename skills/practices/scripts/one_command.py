#!/usr/bin/env python3
"""Check that a step's command can be recorded as it is, as docs/adrs/0044 defines it.

`/practices` runs this on the commands it is about to record. A recorded command is one line that
calls one named entry point, a command runner entry, a script or a tool's standard command, with
nothing but values written `{name}`, which the skill running the step fills in.

The line is split as a shell would split it, so text inside quotes is left alone, and `#` is never
taken as a comment. It is not one command when, outside quotes, it holds `;`, `|` or an `&` that is
not part of a redirection such as `2>&1`, since those run more than one command or run one in the
background. Nor is it on a line break, an unclosed quote, an empty line, a placeholder written
`<name>` rather than `{name}`, or a shell given a command string, such as `sh -c '...'`, even behind
a prefix such as `FOO=1`, `env` or `sudo`, since that string can hold several commands.
Redirections pass.

A command that is one command can still carry arguments of its own: anything after the program
and its subcommand word, or two words after `run` or `compose`, such as `npm run build` or
`docker compose up`, that is not a `{name}` value, alone or as `NAME={name}`; any `NAME=value`
setting or prefix such as `sudo`, `env` or `time` before the program; and a redirection's file. A
word shaped like a subcommand, such as `tests` in `pytest tests`, passes, so the skill still judges
whether it is the tool's own word or a name the project chose. Those are the project's own choices, which belong
in a script, unless the tool's documentation gives them as its usual arguments, such as `./...` in
`go test ./...`: the script lists them and the skill judges. Whether the command needs no answer
from a person and exits 0 on success is not something a script can tell from its text either.

Give it every command of a run at once, one per line on standard input, such as through a quoted
heredoc (`<<'EOF'`), so no quote inside a command can break the call; each may instead be its own
argument.

Output: one line per command, saying "named entry point", why it is not one command, or which
arguments are its own.

Exit codes: 0 when every command is a named entry point with only `{name}` values; 1 when any is
not one command; 3 when none fails that way but some carry arguments of their own; 2 on a usage
error, such as no command given.
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
PLACEHOLDER_WORD = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=)?\{[A-Za-z][\w-]*\}$")
SUBCOMMAND = re.compile(r"^[A-Za-z][A-Za-z0-9:_-]*$")
TWO_WORD_SUBCOMMANDS = {"run", "compose"}


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


def tokens_of(command):
    """The command's words as a shell would split them, keeping punctuation such as `>&` apart."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def punctuation(token):
    return bool(token) and set(token) <= set("();<>|&")


def fills_in(word):
    """True when the word is only a `{name}` value, alone or as a `NAME={name}` setting."""
    return bool(PLACEHOLDER_WORD.match(word))


def own_arguments(command):
    """The arguments a one-line command carries beyond a named entry point and `{name}` values.

    Call only on a command `problem` passes.
    """
    words = []
    tokens = tokens_of(command)
    for i, token in enumerate(tokens):
        if punctuation(token):
            continue
        before = tokens[i - 1] if i > 0 else ""
        after = tokens[i + 1] if i + 1 < len(tokens) else ""
        if token.isdigit() and (punctuation(after) or before.endswith("&")):
            continue  # a file descriptor in a redirection, such as the 2 and 1 of 2>&1
        words.append(token)
    found = []
    while words and (ASSIGNMENT.match(words[0]) or words[0].rsplit("/", 1)[-1] in PREFIXES):
        word = words.pop(0)
        if not fills_in(word):
            found.append(word)
    rest = words[1:]
    if rest and SUBCOMMAND.match(rest[0]):
        first = rest.pop(0)
        if first in TWO_WORD_SUBCOMMANDS and rest and SUBCOMMAND.match(rest[0]):
            rest.pop(0)
    found.extend(word for word in rest if not fills_in(word))
    return found


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
    try:
        tokens = tokens_of(command)
    except ValueError:
        return "the command has an unclosed quote"
    for token in tokens:
        if punctuation(token):
            mark = separator(token)
            if mark:
                return f"the command holds `{mark}`, so it runs more than one command or runs one in the background"
    if shell_string(tokens):
        return "the command gives a shell a command string, which can hold several commands"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check that each step's command can be recorded as it is (docs/adrs/0044).",
        epilog="Exit codes: 0 when every command is a named entry point with only {name} values; 1 when "
               "any is not one command; 3 when none fails that way but some carry arguments of their "
               "own; 2 on a usage error.",
    )
    parser.add_argument("commands", nargs="*", metavar="command",
                        help="a command to check, quoted as one argument; with none, read one per line from standard input")
    args = parser.parse_args(argv)
    commands = args.commands or [line for line in sys.stdin.read().splitlines() if line.strip()]
    if not commands:
        parser.error("give at least one command, as an argument or on standard input")
    failed = own = False
    for command in commands:
        reason = problem(command)
        if reason is not None:
            failed = True
            print(f"`{command}`: not one command: {reason}. Put its steps in a script in the project's "
                  "scripts folder, and record the command that runs it.")
            continue
        extra = own_arguments(command)
        if extra:
            own = True
            listed = ", ".join(f"`{word}`" for word in extra)
            print(f"`{command}`: has arguments of its own: {listed}. Unless the tool's documentation gives "
                  "them as its usual arguments, put the command in a script in the project's scripts "
                  "folder, and record the command that runs it.")
        else:
            print(f"`{command}`: named entry point")
    return 1 if failed else 3 if own else 0


if __name__ == "__main__":
    sys.exit(main())

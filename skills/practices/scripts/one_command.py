#!/usr/bin/env python3
"""Check that a step's command is one command, as docs/adrs/0041 defines it.

`/practices` runs this on each command before recording it. One command is one line that calls
one program with its arguments, where `{name}` marks a value the skill running the step fills in.
The line is split as a shell would split it, so text inside quotes is left alone, and it fails
when, outside quotes, it holds `&&`, `||`, `;`, `|` or `&`, which run more than one command or run
one in the background. It also fails on a line break, an unclosed quote and an empty line.
It fails too when the program is a shell given a command string, such as `sh -c '...'`, since that
string can hold several commands. Redirections such as `> out.txt` or `2>&1` pass. Whether the
command needs no answer from a person and exits 0 on success is not something a script can tell
from its text: the skill judges that.

Give it every command of a run at once, each as its own argument, so it is run only once.

Output: one line per command, saying "one command" or why it is not one.

Exit codes: 0 when every command is one command; 1 when any is not; 2 on a usage error.
"""

import argparse
import shlex
import sys

SEPARATORS = {"&&", "||", ";", "|", "&", "|&", ";;"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}


def problem(command):
    """None when the command is one command; otherwise the reason it is not."""
    if not command.strip():
        return "the command is empty"
    if "\n" in command or "\r" in command:
        return "the command spans more than one line"
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return "the command has an unclosed quote"
    for token in tokens:
        if token in SEPARATORS:
            return f"the command holds `{token}`, so it runs more than one command or runs one in the background"
    program = tokens[0].rsplit("/", 1)[-1]
    if program in SHELLS and any(t.startswith("-") and not t.startswith("--") and "c" in t for t in tokens[1:]):
        return "the command gives a shell a command string, which can hold several commands"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check that each step's command is one command (docs/adrs/0041).",
        epilog="Exit codes: 0 when every command is one command; 1 when any is not; 2 on a usage error.",
    )
    parser.add_argument("commands", nargs="+", metavar="command",
                        help="a command to check, quoted as one argument; give several to check them all")
    args = parser.parse_args(argv)
    failed = False
    for command in args.commands:
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

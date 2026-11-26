#!/usr/bin/env python3
"""Run before writing a requirement's code: check its new tests fail, then repeat the practices
and the build's rules.

`/build` runs this from the repository after writing each requirement's tests, before
committing them. Give it the command that runs one test file, with `{file}` where the path goes,
and the test files written or changed.

It refuses when:
- a file named is not new or changed since the last commit;
- anything else is uncommitted, such as code written before its tests;
- any file named passes when run: its tests already pass, so they cannot show the code works.

Output: the last lines of each file's output, and, for each refusal, why. A failure must come
from the behaviour not being there yet, not from a file that cannot load: read each one. Then,
whatever the result, the `## Practices` sections of the repository's AGENTS.md and CLAUDE.md and
the build skill's `## Rules that hold for the whole build`, so a long build has them fresh at
every requirement: what was read at the start carries less weight as the conversation grows.
With --plan and --step, the output starts with the line steps.py gives that step, "Step N of M:
<requirement>", so the build's progress list can be brought up to date (docs/adrs/0063).

Exit codes: 0 when every file named fails; 1 when they are refused; 2 on a usage error, such as
--plan without --step or a step the plan does not have, when the command cannot run (exit 126
or 127), or when the folder is not in a git work tree.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import uncommitted  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steps  # noqa: E402

TAIL = 15
SKILL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")
PRACTICES_FILES = ("AGENTS.md", "CLAUDE.md")


def section(path, heading):
    """The level-two section of a Markdown file headed `## <heading>`, up to the next heading of
    level one or two outside a code block, or None when the file or the heading is missing."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return None
    found, fenced = [], False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,2} ", line):
            if found:
                break
            if line.rstrip(" \t#") == "## " + heading:
                found.append(line)
                continue
        if found:
            found.append(line)
    return "\n".join(found).strip() or None


def reminders(root):
    """The practices and the build's rules, to print after every result."""
    parts, seen = [], set()
    for name in PRACTICES_FILES:
        practices = section(os.path.join(root, name), "Practices")
        if practices and practices not in seen:
            seen.add(practices)
            parts.append(f"From {name}:\n\n{practices}")
    rules = section(SKILL, "Rules that hold for the whole build")
    if rules:
        parts.append(f"From the build skill:\n\n{rules}")
    if not parts:
        return ""
    return ("\nKeep to these while you build this requirement:\n\n" + "\n\n".join(parts))


def run(command, path, root):
    """Run the command on one file, from the top of the repository: (exit code, last lines)."""
    result = subprocess.run(command.replace("{file}", shlex.quote(path)), shell=True, cwd=root,
                            capture_output=True, encoding="utf-8", errors="replace")
    return result.returncode, (result.stdout + result.stderr).strip().splitlines()[-TAIL:]


def indented(lines):
    return "\n".join("    " + line for line in lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--command", required=True,
                        help="command that runs one test file, with {file} for its path")
    parser.add_argument("files", nargs="*",
                        help="the new or changed test files, from the top of the repository, "
                             "from the current folder, or absolute")
    parser.add_argument("--plan", help="the plan's path, to name the step with --step")
    parser.add_argument("--step", type=int,
                        help="the requirement's number in the list steps.py prints for the plan")
    args = parser.parse_args(argv)
    if (args.plan is None) != (args.step is None):
        print("--plan and --step go together: give both, or neither.")
        return 2
    if args.plan is not None:
        try:
            step = steps.line(args.plan, args.step)
        except steps.Refused as reason:
            print(reason)
            return 2
    if not args.files:
        print("Name the new or changed test files.")
        return 2
    if "{file}" not in args.command:
        print("The command needs {file} where the test file's path goes.")
        return 2
    try:
        entries, _ = uncommitted.check(".")
        root = uncommitted.git(".", "rev-parse", "--show-toplevel").stdout.strip()
    except uncommitted.NotARepository as error:
        print(error)
        return 2
    if args.plan is not None:
        print(step)
    changed = {entry[3:] for entry in entries}
    files = []
    for path in args.files:
        relative = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
        if relative not in changed and os.path.normpath(path) in changed:
            relative = os.path.normpath(path)
        files.append(relative)
    refusals = [f"{path} is not a new or changed file: name only tests written now."
                for path in files if path not in changed]
    others = sorted(changed - set(files))
    if others:
        refusals.append("Uncommitted besides the tests: " + ", ".join(others)
                        + ". Code must wait until its tests are committed.")
    for path in (path for path in files if path in changed):
        status, tail = run(args.command, path, root)
        if status in (126, 127):
            print(f"The command could not run on {path} (exit {status}):\n{indented(tail)}")
            return 2
        if status == 0:
            refusals.append(f"{path}: its tests already pass, so they cannot show the code works.\n"
                            + indented(tail))
        else:
            print(f"{path} fails. Check the failure comes from the missing behaviour:\n"
                  + indented(tail))
    if refusals:
        print("Refused:")
        for refusal in refusals:
            print("- " + refusal)
    else:
        print("Accepted: every new test file fails.")
    reminder = reminders(root)
    if reminder:
        print(reminder)
    return 1 if refusals else 0


if __name__ == "__main__":
    sys.exit(main())

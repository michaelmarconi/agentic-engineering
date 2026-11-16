#!/usr/bin/env python3
"""Check that a requirement's new tests fail, before any code makes them pass.

`/build` runs this from the repository after writing each requirement's tests, before
committing them. Give it the command that runs one test file, with `{file}` where the path goes,
and the test files written or changed.

It refuses when:
- a file named is not new or changed since the last commit;
- anything else is uncommitted, such as code written before its tests;
- any file named passes when run: its tests already pass, so they cannot show the code works.

Output: what it checked and, for each refusal, why, with the last lines of a passing file's
output.

Exit codes: 0 when every file named fails; 1 when they are refused; 2 on a usage error,
or when the folder is not in a git work tree.
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uncommitted  # noqa: E402

TAIL = 15


def changed_paths(repo):
    entries, _ = uncommitted.check(repo)
    return [entry[3:] for entry in entries]


def run(command, path, root):
    result = subprocess.run(command.replace("{file}", path), shell=True, cwd=root,
                            capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip().splitlines()[-TAIL:]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--command", required=True,
                        help="command that runs one test file, with {file} for its path")
    parser.add_argument("files", nargs="*", help="the new or changed test files, from the top of the repository")
    args = parser.parse_args(argv)
    if not args.files:
        print("Name the new or changed test files.")
        return 2
    if "{file}" not in args.command:
        print("The command needs {file} where the test file's path goes.")
        return 2
    try:
        top = uncommitted.git(".", "rev-parse", "--show-toplevel")
        if top.returncode != 0:
            raise uncommitted.NotARepository("not in a git work tree")
        root = top.stdout.strip()
        changed = changed_paths(root)
    except uncommitted.NotARepository as error:
        print(error)
        return 2
    files = [os.path.normpath(path) for path in args.files]
    refusals = []
    for path in files:
        if path not in changed:
            refusals.append(f"{path} is not a new or changed file: hand over only tests written now.")
    others = [path for path in changed if path not in files]
    if others:
        refusals.append("Uncommitted besides the tests: " + ", ".join(others)
                        + ". Code must wait until its tests are committed.")
    for path in files:
        if path not in changed:
            continue
        status, tail = run(args.command, path, root)
        if status == 0:
            refusals.append(f"{path}: its tests already pass, so they cannot show the code works.\n"
                            + "\n".join("    " + line for line in tail))
        else:
            print(f"{path} fails, as it should.")
    if refusals:
        print("Refused:")
        for refusal in refusals:
            print("- " + refusal)
        return 1
    print("Accepted: every new test file fails.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""List what is uncommitted in a repository, so `/build` starts only when nothing is.

`/build` runs this before it starts. It lists every entry `git status` reports: changed, staged
and untracked files. It leaves out untracked entries that are stand-ins for the null device
(`/dev/null`): on Linux, Claude Code's sandbox puts one in place of each file it protects, such
as `.bashrc`, `.gitconfig`, `.mcp.json` or `.claude/settings.json`, and git sees them as untracked
files. A project's own files are never the null device, and a tracked file is always listed.
hand_over.py uses the same check to keep the stand-ins out of the build's commit.

Output: "Nothing is uncommitted." or "Uncommitted:" followed by one line per entry, as
`git status --short` writes it; when stand-ins were left out, a last line says how many.

Exit codes: 0 when nothing is uncommitted; 1 when something is; 2 when the folder is not in a git
work tree or git can't be run.
"""

import argparse
import os
import stat
import subprocess
import sys


class NotARepository(Exception):
    pass


def lstat_of(path):
    return os.lstat(path)


def is_stand_in(path, null_rdev):
    """Whether the file at `path` is the null device, as the sandbox's stand-ins are."""
    try:
        info = lstat_of(path)
    except OSError:
        return False
    return stat.S_ISCHR(info.st_mode) and info.st_rdev == null_rdev


def git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                              encoding="utf-8", errors="surrogateescape")
    except OSError as error:
        raise NotARepository(f"git could not be run ({error})")


def check(repo):
    """(entries, stand_ins): the uncommitted entries, as `git status --short` writes them, and the
    paths, from the top of the work tree, of the untracked stand-ins left out."""
    top = git(repo, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise NotARepository(f"{repo} is not in a git work tree ({top.stderr.strip()})")
    root = top.stdout.strip()
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if status.returncode != 0:
        raise NotARepository(f"git status failed in {root} ({status.stderr.strip()})")
    null_rdev = os.stat(os.devnull).st_rdev
    fields = status.stdout.split("\0")
    entries, stand_ins = [], []
    i = 0
    while i < len(fields):
        field = fields[i]
        i += 1
        if not field:
            continue
        code, path = field[:2], field[3:]
        if "R" in code or "C" in code:
            i += 1  # a rename or copy is followed by the path it came from
        if code == "??" and is_stand_in(os.path.join(root, path), null_rdev):
            stand_ins.append(path)
        else:
            entries.append(f"{code} {path}")
    return entries, stand_ins


def report(entries, stand_ins):
    lines = ["Uncommitted:", *entries] if entries else ["Nothing is uncommitted."]
    if stand_ins:
        lines.append(f"Left out {len(stand_ins)} untracked stand-in{'s' if len(stand_ins) != 1 else ''} "
                     "for the null device, which Claude Code's sandbox puts in place.")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="the repository (default: the current directory)")
    args = parser.parse_args(argv)
    try:
        entries, stand_ins = check(os.path.abspath(args.repo))
    except NotARepository as error:
        print(f"Refused: {error}.")
        return 2
    print("\n".join(report(entries, stand_ins)))
    return 1 if entries else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Find the git repository a hook works in, the same way for every hook, as docs/adrs/0046 decides.

A hook that acts on a file finds its repository by going up from that file to the nearest folder
holding `.git`, as a folder or a file, so worktrees and submodules count. A relative path is read
from the folder given (the hook event's `cwd`, the folder Claude's shell is in), or else from the
session folder: $CLAUDE_PROJECT_DIR, or the current directory if that is unset. A path that exists
only when read from the session folder is read from there, since the shell may have moved. A file in no
repository uses the session folder instead. The whole repository is one project, so a session
started in a subfolder, such as one app of a monorepo, still judges every path from the
repository's top. A hook with no file looks at the top of the repository holding the session
folder or, when that is in no repository, in the session folder and the repositories directly
inside it, as in a Claude project thread, whose session folder holds each repository one level
down.

Every path is made real, links followed, so two spellings of one folder always agree.

The hooks import it; run on its own, it only prints this help.
"""

import argparse
import os
import sys


def session_folder():
    """The folder Claude Code was started in."""
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def full_path(path, base=None, fallback=True):
    """The path made full and real: a relative one is read from `base`, else the session folder.

    The shell may have moved into a subfolder since, so a relative path that exists only when read
    from the session folder is read from there, unless `fallback` is False, as for a folder a
    request names outright."""
    if os.path.isabs(path):
        return os.path.realpath(path)
    first = os.path.join(base or session_folder(), path)
    if (base and fallback and not os.path.exists(first)
            and os.path.exists(os.path.join(session_folder(), path))):
        first = os.path.join(session_folder(), path)
    return os.path.realpath(first)


def top(path, base=None):
    """The top folder of the git repository holding the path, or None when it is in none."""
    folder = os.path.dirname(full_path(path, base))
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def repository_of(path, base=None):
    """The repository holding the path, or the session folder when it is in none."""
    return top(path, base) or session_folder()


def relative_parts(path, base=None):
    """The path's parts relative to its repository, such as ['docs', 'plans', 'x.md']."""
    relative = os.path.relpath(full_path(path, base), repository_of(path, base))
    return os.path.normpath(relative).split(os.sep)


def session_folders():
    """For a hook with no file: the top of the repository holding the session folder, or, when it
    is in no repository, the session folder, then each repository directly inside it."""
    session = session_folder()
    repository = top(os.path.join(session, "x"))
    if repository:
        return [repository]
    try:
        names = sorted(os.listdir(session))
    except OSError:
        names = []
    inside = [os.path.join(session, name) for name in names
              if os.path.isdir(os.path.join(session, name))
              and os.path.exists(os.path.join(session, name, ".git"))]
    return [session] + inside


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                     epilog=__doc__.split("\n\n", 1)[1] + "\nExit code: always 0.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

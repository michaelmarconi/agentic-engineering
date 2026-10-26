#!/usr/bin/env python3
"""Give Claude the lifecycle map at the start of a session.

Claude Code runs this as a SessionStart hook and adds whatever it prints to Claude's context.
It prints the plugin's context/sdlc.md only when the project uses the lifecycle, that is, when
it has docs/brief.md or a spec under docs/specs/ whose frontmatter has a lifecycle status.
Anywhere else it prints nothing, so installing the plugin costs other projects nothing.
"""

import argparse
import os
import sys

from status_check import STATUSES, status_of

MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "context", "sdlc.md")


def uses_lifecycle(project):
    if os.path.isfile(os.path.join(project, "docs", "brief.md")):
        return True
    for folder, _, files in os.walk(os.path.join(project, "docs", "specs")):
        for name in files:
            if name.endswith(".spec.md"):
                try:
                    with open(os.path.join(folder, name), encoding="utf-8") as f:
                        if status_of(f.read()) in STATUSES:
                            return True
                except (OSError, UnicodeDecodeError):
                    pass
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The project is $CLAUDE_PROJECT_DIR, or the current directory if that is unset. "
            "Output: the map on stdout, or nothing. Exit code: always 0, so a session never "
            "fails to start because of this hook."
        ),
    )
    parser.parse_args(argv)
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if uses_lifecycle(project):
        try:
            with open(MAP, encoding="utf-8") as f:
                sys.stdout.write(f.read())
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

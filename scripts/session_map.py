#!/usr/bin/env python3
"""Give Claude the lifecycle rules at the start of a session.

Claude Code runs this as a SessionStart hook. It gives Claude the plugin's docs/lifecycle.md only
when the project uses the lifecycle, that is, when it has docs/brief.md or a spec under
docs/specs/ whose frontmatter has a lifecycle status.

In any other project it prints nothing, so installing the plugin costs other projects nothing.

On Python 3.6, in any project, it also warns the person, because the plugin's other
scripts use calls that Python 3.6 lacks and would fail.
"""

import argparse
import json
import os
import sys

from status_check import SPEC_STATUSES, STATUSES, lifecycle_status

# A spec counts with a status specs had before, too, so its project still gets the rules that say
# how to bring it up to date.
KNOWN = SPEC_STATUSES + STATUSES

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MAP = os.path.join(ROOT, "docs", "lifecycle.md")

MINIMUM = (3, 7)


def version_warning():
    """The warning to give on a Python too old for the plugin, or None."""
    if tuple(sys.version_info[:2]) >= MINIMUM:
        return None
    needed = ".".join(str(part) for part in MINIMUM)
    found = ".".join(str(part) for part in sys.version_info[:3])
    return (f"The sdlc plugin needs Python {needed} or later, but python3 here is {found}, so "
            f"its checks will fail. Install a newer Python 3 as python3.")


def uses_lifecycle(project):
    if os.path.isfile(os.path.join(project, "docs", "brief.md")):
        return True
    for folder, _, files in os.walk(os.path.join(project, "docs", "specs")):
        for name in files:
            if name.endswith(".spec.md"):
                try:
                    with open(os.path.join(folder, name), encoding="utf-8") as f:
                        if lifecycle_status(f.read(), KNOWN) in KNOWN:
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
            "Output: nothing, or a SessionStart JSON object on stdout whose additionalContext "
            "holds the map and any warning about the Python version, which also goes in "
            "systemMessage. Exit code: always 0, so a session never fails to start because of "
            "this hook."
        ),
    )
    parser.parse_args(argv)
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    warning = version_warning()
    parts = [warning] if warning else []
    if uses_lifecycle(project):
        try:
            with open(MAP, encoding="utf-8") as f:
                parts.append(f.read())
        except OSError:
            pass
    if not parts:
        return 0
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                  "additionalContext": "\n\n".join(parts)}}
    if warning:
        out["systemMessage"] = warning
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

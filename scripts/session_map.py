#!/usr/bin/env python3
"""Give Claude the lifecycle map at the start of a session, and report unsaved settings.

Claude Code runs this as a SessionStart hook. It gives Claude the plugin's context/sdlc.md only
when the project uses the lifecycle, that is, when it has docs/brief.md or a spec under
docs/specs/ whose frontmatter has a lifecycle status.

It also checks every setting declared under userConfig in the plugin's plugin.json. Claude Code
passes a saved setting to hooks as CLAUDE_PLUGIN_OPTION_<KEY> and into skill text, but never
applies the declared default, so a setting nobody saved leaves skills without a value. Each
unsaved setting is reported in every session, in every project, until it is saved, both to the
person and to Claude.

With nothing to report it prints nothing, so installing the plugin costs other projects nothing.
"""

import argparse
import json
import os
import sys

from status_check import STATUSES, status_of

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MAP = os.path.join(ROOT, "context", "sdlc.md")
MANIFEST = os.path.join(ROOT, ".claude-plugin", "plugin.json")


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


def unsaved_settings(environ):
    """Return (key, title, default) for each declared setting that has no saved value."""
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        return []
    return [
        (key, option.get("title", key), option.get("default"))
        for key, option in manifest.get("userConfig", {}).items()
        if not environ.get("CLAUDE_PLUGIN_OPTION_" + key.upper())
    ]


def notice(unsaved):
    settings = ", ".join(
        f"{title} (suggested: {default})" if default is not None else title
        for _, title, default in unsaved
    )
    return (f"The sdlc plugin has settings that are not saved yet: {settings}. Skills that need "
            "them will stop and ask. To save them, run /plugin configure sdlc@sdlc, type a value "
            "next to each one, then choose Save configuration; the boxes start empty, so "
            "leaving one empty saves nothing.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The project is $CLAUDE_PROJECT_DIR, or the current directory if that is unset. "
            "Output: nothing, or a SessionStart JSON object on stdout whose additionalContext "
            "holds the map and any unsaved-settings notice, and whose systemMessage shows that "
            "notice to the person. Exit code: always 0, so a session never fails to start "
            "because of this hook."
        ),
    )
    parser.parse_args(argv)
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    context = []
    output = {}
    if uses_lifecycle(project):
        try:
            with open(MAP, encoding="utf-8") as f:
                context.append(f.read())
        except OSError:
            pass
    unsaved = unsaved_settings(os.environ)
    if unsaved:
        output["systemMessage"] = notice(unsaved)
        context.append(output["systemMessage"] + " If the person asks for one of these skills "
                       "before saving them, tell them so first.")
    if context:
        output["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(context),
        }
        print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())

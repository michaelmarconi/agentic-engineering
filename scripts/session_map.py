#!/usr/bin/env python3
"""Give Claude the lifecycle rules at the start of a session, and report unsaved settings.

Claude Code runs this as a SessionStart hook. It gives Claude the plugin's docs/lifecycle.md only
when the project uses the lifecycle, that is, when it has docs/brief.md or a spec under
docs/specs/ whose frontmatter has a lifecycle status.

It also checks every setting declared under userConfig in the plugin's plugin.json. Claude Code
passes a saved setting to hooks as CLAUDE_PLUGIN_OPTION_<KEY> and into skill text, but never
applies the declared default, so a setting nobody saved leaves skills without a value. Each
unsaved setting is reported in every session, in every project, until it is saved, both to the
person and to Claude.

With nothing to report it prints nothing, so once its settings are saved, installing the plugin
costs other projects nothing.
"""

import argparse
import json
import os
import sys

from status_check import STATUSES, status_of

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MAP = os.path.join(ROOT, "docs", "lifecycle.md")
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
    options = manifest.get("userConfig") if isinstance(manifest, dict) else None
    if not isinstance(options, dict):
        return []
    return [
        (key, option.get("title", key), option.get("default"))
        for key, option in options.items()
        if isinstance(option, dict) and not environ.get("CLAUDE_PLUGIN_OPTION_" + key.upper())
    ]


def notice(unsaved):
    names = " and ".join(f"'{title}'" for _, title, _ in unsaved)
    if len(unsaved) == 1:
        default = unsaved[0][2]
        setting, it = "setting is", "it"
        hint = f" ({default} is suggested)" if default is not None else ""
    else:
        setting, it = "settings are", "them"
        hint = ", ".join(f"{title} {default}" for _, title, default in unsaved if default is not None)
        hint = f" (suggested: {hint})" if hint else ""
    return (f"sdlc: the {names} config {setting} not set. Run /plugin configure sdlc@sdlc to "
            f"set {it}{hint}, then /reload-plugins to reload this plugin.")


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
        context.append(output["systemMessage"])
    if context:
        output["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(context),
        }
        print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())

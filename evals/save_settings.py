#!/usr/bin/env python3
"""Save the plugin's settings for an eval run, as a person would with /plugin configure.

Claude Code applies only saved settings, and `claude plugin eval` gives each run its own empty
config folder, next to its home folder, and loads the plugin as sdlc@inline. Each case's
place-files.sh runs this, so the skills see the same values as a person who saved the defaults.
The defaults are read from plugin.json, their only home. A case whose graders depend on a value
passes it as KEY=VALUE, so a change to the default does not change what the case tests.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "..", ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
    manifest = json.load(f)
options = {key: option["default"] for key, option in manifest.get("userConfig", {}).items()
           if "default" in option}
for pair in sys.argv[1:]:
    key, _, value = pair.partition("=")
    if key not in manifest.get("userConfig", {}):
        sys.exit(f"save_settings.py: no setting named {key!r} in plugin.json")
    options[key] = json.loads(value)

path = os.path.join(os.environ["HOME"], "..", "config", "settings.json")
settings = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
settings.setdefault("pluginConfigs", {})[manifest["name"] + "@inline"] = {"options": options}
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

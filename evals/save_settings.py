#!/usr/bin/env python3
"""Save every plugin setting's default for the eval run, as a person would with /plugin configure.

Claude Code applies only saved settings, and `claude plugin eval` gives each run its own empty
config folder, next to its home folder, and loads the plugin as sdlc@inline. Each case's
place-files.sh runs this, so the skills see the same values a person who saved the defaults
would. The defaults are read from plugin.json, their only home.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "..", ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
    manifest = json.load(f)
options = {key: option["default"] for key, option in manifest.get("userConfig", {}).items()}

path = os.path.join(os.environ["HOME"], "..", "config", "settings.json")
settings = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
settings.setdefault("pluginConfigs", {})[manifest["name"] + "@inline"] = {"options": options}
with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

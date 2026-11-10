"""Guard the plugin's name: `agentic`, listed by this repository's catalog `sdlc`, which keeps a
rename entry so installs made under the old name `sdlc` move to the new one (ADR 0029).

The search below is also the check that the rename is complete: outside the places that keep
history, nothing still names the old prefix or "the sdlc plugin".
"""

import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = re.compile(r"sdlc:|sdlc plugin")
# The status comment line that earlier templates copied into people's documents. Nothing checks
# it, so documents that carry it keep working; the test fixtures that stand in for them keep it too.
OLD_TEMPLATE_LINE = "the sdlc plugin's skills, which check each change"
# History, and the words people use for the plugin: they keep saying sdlc, and the feedback skill's
# description says "formerly sdlc" so it still triggers.
KEPT = ("docs/adrs/", "CHANGELOG.md", "scripts/test_plugin_name.py")


def load(path):
    with open(os.path.join(ROOT, path)) as f:
        return json.load(f)


class PluginName(unittest.TestCase):
    def test_plugin_is_named_agentic(self):
        self.assertEqual(load(".claude-plugin/plugin.json")["name"], "agentic")

    def test_catalog_keeps_old_name_and_maps_it(self):
        catalog = load(".claude-plugin/marketplace.json")
        self.assertEqual(catalog["name"], "sdlc")
        self.assertEqual([(p["name"], p["source"]) for p in catalog["plugins"]], [("agentic", ".")])
        self.assertEqual(catalog["renames"], {"sdlc": "agentic"})

    def test_nothing_names_the_old_prefix(self):
        found = []
        for folder, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for name in files:
                path = os.path.relpath(os.path.join(folder, name), ROOT)
                if path.startswith(KEPT):
                    continue
                try:
                    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                        lines = f.read().splitlines()
                except UnicodeDecodeError:
                    continue
                for number, line in enumerate(lines, 1):
                    if OLD.search(line.replace(OLD_TEMPLATE_LINE, "")):
                        if path.startswith(("evals/", "evals-failed-check/")) and path.endswith("prompt.md"):
                            continue  # a person's own words about the plugin
                        found.append(f"{path}:{number}: {line.strip()}")
        self.assertEqual(found, [], "\n".join(found))


if __name__ == "__main__":
    unittest.main()

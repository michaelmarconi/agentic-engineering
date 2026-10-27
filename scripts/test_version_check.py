import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "version_check.py")


def changelog(*versions):
    entries = "".join(f"## [{v}] - 2026-10-27\n\n### Added\n\n- Something.\n\n" for v in versions)
    return f"# Changelog\n\nIntro.\n\n{entries}"


class VersionCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def manifest(self, version="0.4.0"):
        path = os.path.join(self.tmp.name, ".claude-plugin", "plugin.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fields = {"name": "sdlc"} if version is None else {"name": "sdlc", "version": version}
        with open(path, "w") as f:
            json.dump(fields, f)

    def log(self, text):
        with open(os.path.join(self.tmp.name, "CHANGELOG.md"), "w") as f:
            f.write(text)

    def check(self, root=None):
        return subprocess.run([sys.executable, SCRIPT, root or self.tmp.name],
                              capture_output=True, text=True)

    def assertFails(self, needle):
        done = self.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(needle, done.stdout)

    def test_matching_newest_entry_passes_silently(self):
        self.manifest("0.4.0")
        self.log(changelog("0.4.0", "0.3.0"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_plugins_own_changelog_matches(self):
        done = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_bump_without_entry_fails(self):
        self.manifest("0.4.0")
        self.log(changelog("0.3.0"))
        self.assertFails("plugin.json is at 0.4.0 but the newest CHANGELOG.md entry is 0.3.0")

    def test_entry_without_bump_fails(self):
        self.manifest("0.3.0")
        self.log(changelog("0.4.0", "0.3.0"))
        self.assertFails("plugin.json is at 0.3.0 but the newest CHANGELOG.md entry is 0.4.0")

    def test_unreleased_heading_is_not_an_entry(self):
        self.manifest("0.4.0")
        self.log(changelog("0.4.0").replace("Intro.\n\n", "Intro.\n\n## [Unreleased]\n\n"))
        self.assertEqual(self.check().returncode, 0)

    def test_mistyped_newest_heading_is_not_skipped(self):
        self.manifest("0.3.0")
        self.log(changelog("v0.4.0", "0.3.0"))
        self.assertFails("plugin.json is at 0.3.0 but the newest CHANGELOG.md entry is v0.4.0")

    def test_unbracketed_newest_heading_is_not_skipped(self):
        self.manifest("0.3.0")
        self.log(changelog("0.3.0").replace("Intro.\n\n", "Intro.\n\n## 0.4.0 - 2026-10-28\n\n"))
        self.assertFails("plugin.json is at 0.3.0 but the newest CHANGELOG.md entry is 0.4.0")

    def test_heading_in_code_block_is_not_an_entry(self):
        self.manifest("0.4.0")
        self.log(changelog("0.4.0").replace("Intro.\n\n", "Intro.\n\n```\n## [9.9.9]\n```\n\n"))
        self.assertEqual(self.check().returncode, 0)

    def test_unreadable_changelog_fails(self):
        self.manifest()
        with open(os.path.join(self.tmp.name, "CHANGELOG.md"), "wb") as f:
            f.write(b"## [0.4.0] \xff\n")
        self.assertFails("CHANGELOG.md can't be read as UTF-8 text")

    def test_falsy_non_string_version_fails(self):
        self.manifest(0)
        self.log(changelog("0"))
        self.assertFails("plugin.json version is not a string")

    def test_malformed_manifest_fails(self):
        self.manifest()
        with open(os.path.join(self.tmp.name, ".claude-plugin", "plugin.json"), "w") as f:
            f.write("{not json")
        self.log(changelog("0.4.0"))
        self.assertFails("plugin.json is not a JSON object")

    def test_non_string_version_fails(self):
        self.manifest(1)
        self.log(changelog("1"))
        self.assertFails("plugin.json version is not a string")

    def test_missing_changelog_fails(self):
        self.manifest()
        self.assertFails("CHANGELOG.md is missing")

    def test_changelog_without_entries_fails(self):
        self.manifest()
        self.log("# Changelog\n\nNothing yet.\n")
        self.assertFails("CHANGELOG.md has no version entry")

    def test_manifest_without_version_fails(self):
        self.manifest(None)
        self.log(changelog("0.4.0"))
        self.assertFails("plugin.json has no version")

    def test_missing_manifest_fails(self):
        self.log(changelog("0.4.0"))
        self.assertFails("plugin.json is missing")

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("CHANGELOG.md", done.stdout)


if __name__ == "__main__":
    unittest.main()

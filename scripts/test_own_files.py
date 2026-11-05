import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "own_files.py")


class OwnFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plugin = os.path.join(self.tmp.name, "plugin")
        self.rubric = os.path.join(self.plugin, "skills", "spec", "references", "rubric.md")
        # The hook's temporary folder, so tests never depend on what the real one holds.
        self.temporary = os.path.join(self.tmp.name, "temporary")
        os.makedirs(self.temporary)
        self.fallback = os.path.join(self.temporary, f"sdlc-audits-{os.getuid()}")
        os.makedirs(os.path.dirname(self.rubric))
        with open(self.rubric, "w") as f:
            f.write("rubric\n")

    def run_hook(self, tool, tool_input, raw=None, root=None):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root if root is not None else self.plugin)
        env["CLAUDE_PLUGIN_DATA"] = os.path.join(self.tmp.name, "data")
        env["TMPDIR"] = self.temporary
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
        done = subprocess.run([sys.executable, SCRIPT], input=raw if raw is not None else json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout) if done.stdout.strip() else None

    def assert_allowed(self, out):
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_reading_a_plugin_file_is_allowed(self):
        self.assert_allowed(self.run_hook("Read", {"file_path": self.rubric}))

    def test_searching_inside_the_plugin_is_allowed(self):
        self.assert_allowed(self.run_hook("Grep", {"pattern": "x", "path": os.path.join(self.plugin, "skills")}))
        self.assert_allowed(self.run_hook("Glob", {"pattern": "*.md", "path": self.plugin}))

    def test_a_file_outside_the_plugin_is_left_to_the_person(self):
        outside = os.path.join(self.tmp.name, "project", "secret.md")
        self.assertIsNone(self.run_hook("Read", {"file_path": outside}))

    def test_a_folder_whose_name_only_starts_like_the_plugin_is_outside_it(self):
        self.assertIsNone(self.run_hook("Read", {"file_path": self.plugin + "-other/x.md"}))

    def test_climbing_out_of_the_plugin_is_outside_it(self):
        path = os.path.join(self.plugin, "skills", "..", "..", "secret.md")
        self.assertIsNone(self.run_hook("Read", {"file_path": path}))

    def test_a_link_inside_the_plugin_that_points_out_is_outside_it(self):
        target = os.path.join(self.tmp.name, "secret.md")
        open(target, "w").close()
        link = os.path.join(self.plugin, "link.md")
        os.symlink(target, link)
        self.assertIsNone(self.run_hook("Read", {"file_path": link}))

    def test_a_search_with_no_path_is_left_to_the_person(self):
        self.assertIsNone(self.run_hook("Grep", {"pattern": "x"}))

    def test_other_tools_are_left_alone(self):
        self.assertIsNone(self.run_hook("Write", {"file_path": self.rubric, "content": "x"}))
        self.assertIsNone(self.run_hook("Bash", {"command": "cat " + self.rubric}))

    def test_without_a_plugin_root_nothing_is_allowed(self):
        self.assertIsNone(self.run_hook("Read", {"file_path": self.rubric}, root=""))

    def test_unreadable_input_is_ignored(self):
        self.assertIsNone(self.run_hook("Read", {}, raw="not json"))
        self.assertIsNone(self.run_hook("Read", {}, raw=json.dumps({"tool_name": "Read"})))

    def test_reading_an_audit_diff_file_in_its_temporary_folder_is_allowed(self):
        os.makedirs(self.fallback, mode=0o700)
        self.assert_allowed(self.run_hook("Read", {"file_path": os.path.join(self.fallback, "0123456789ab-x", "diff.patch")}))

    def test_a_temporary_fallback_that_is_a_link_is_left_to_the_person(self):
        target = os.path.join(self.tmp.name, "home")
        os.makedirs(target)
        os.symlink(target, self.fallback)
        self.assertIsNone(self.run_hook("Read", {"file_path": os.path.join(self.fallback, "secret")}))

    def test_a_temporary_fallback_others_can_open_is_left_to_the_person(self):
        os.makedirs(self.fallback, mode=0o755)
        os.chmod(self.fallback, 0o755)
        self.assertIsNone(self.run_hook("Read", {"file_path": os.path.join(self.fallback, "x")}))

    def test_other_temporary_folders_and_the_data_folder_are_left_to_the_person(self):
        os.makedirs(self.fallback, mode=0o700)
        self.assertIsNone(self.run_hook("Read", {"file_path": os.path.join(self.fallback, "..", "secret.md")}))
        self.assertIsNone(self.run_hook("Read", {"file_path": os.path.join(self.temporary, "sdlc-audits-other", "x")}))
        self.assertIsNone(self.run_hook("Read", {"file_path": os.path.join(self.tmp.name, "data", "audits", "x")}))

    def test_help_describes_the_hook(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("PreToolUse", done.stdout)


if __name__ == "__main__":
    unittest.main()

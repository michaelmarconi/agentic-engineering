import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "failed_check_evals.py")
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import failed_check_evals  # noqa: E402


class FailedCheckEvals(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plugin = os.path.join(self.tmp.name, "plugin")
        self.put("agents/correction-checker.md", "real checker\n")
        self.put("agents/spec-reviewer.md", "reviewer\n")
        self.put("skills/spec/SKILL.md", "skill\n")
        self.put("evals/spec-normal/prompt.md", "normal case\n")
        self.put("evals/results/old.json", "{}")
        self.put("evals-failed-check/failing-correction-checker.md", "fake checker\n")
        self.put("evals-failed-check/spec-stops-on-failed-check/prompt.md", "stop case\n")
        self.put(".git/HEAD", "ref\n")

    def put(self, path, text):
        full = os.path.join(self.plugin, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def read(self, root, path):
        with open(os.path.join(root, path)) as f:
            return f.read()

    def build(self):
        copy = os.path.join(self.tmp.name, "copy")
        failed_check_evals.build_copy(self.plugin, copy)
        return copy

    def test_copy_has_the_fake_checker_in_place_of_the_real_one(self):
        copy = self.build()
        self.assertEqual(self.read(copy, "agents/correction-checker.md"), "fake checker\n")
        self.assertEqual(self.read(copy, "agents/spec-reviewer.md"), "reviewer\n")
        self.assertEqual(self.read(copy, "skills/spec/SKILL.md"), "skill\n")

    def test_copy_runs_only_the_failed_check_cases(self):
        copy = self.build()
        self.assertEqual(self.read(copy, "evals/spec-stops-on-failed-check/prompt.md"), "stop case\n")
        self.assertFalse(os.path.exists(os.path.join(copy, "evals", "spec-normal")))
        self.assertFalse(os.path.exists(os.path.join(copy, "evals", "failing-correction-checker.md")))

    def test_copy_leaves_out_git_and_old_results(self):
        copy = self.build()
        self.assertFalse(os.path.exists(os.path.join(copy, ".git")))
        self.assertFalse(os.path.exists(os.path.join(copy, "evals", "results")))

    def test_the_plugin_itself_is_untouched(self):
        self.build()
        self.assertEqual(self.read(self.plugin, "agents/correction-checker.md"), "real checker\n")
        self.assertTrue(os.path.exists(os.path.join(self.plugin, "evals", "spec-normal")))

    def test_this_repository_has_a_fake_checker_named_like_the_real_one(self):
        text = self.read(ROOT, "evals-failed-check/failing-correction-checker.md")
        self.assertIn("\nname: correction-checker\n", text)

    def test_help_describes_the_command(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("claude plugin eval", done.stdout)


if __name__ == "__main__":
    unittest.main()

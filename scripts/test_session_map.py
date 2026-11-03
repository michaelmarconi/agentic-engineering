import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "session_map.py")
MAP = os.path.join(HERE, "..", "docs", "lifecycle.md")


class SessionMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_map(self, *args):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.tmp.name)
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, env=env)

    def output(self):
        done = self.run_map()
        self.assertEqual(done.returncode, 0)
        return json.loads(done.stdout)

    def test_silent_in_repo_without_lifecycle_documents(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        done = self.run_map()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def put(self, relative, text=""):
        path = os.path.join(self.tmp.name, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def test_silent_with_folders_other_projects_also_use(self):
        for folder in ["docs/specs", "docs/plans", "docs/adrs"]:
            os.makedirs(os.path.join(self.tmp.name, folder))
        self.put("docs/specs/login.spec.md", "# Login\n")
        self.assertEqual(self.run_map().stdout, "")

    def test_prints_map_when_a_spec_has_a_lifecycle_status(self):
        with open(MAP) as f:
            expected = f.read()
        self.put("docs/specs/billing/invoice.spec.md", "---\nstatus: 📝 Draft\n---\n# Invoice\n")
        out = self.output()
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertEqual(out["hookSpecificOutput"]["additionalContext"], expected)
        self.assertNotIn("systemMessage", out)

    def test_prints_map_for_a_spec_written_before_the_emoji(self):
        self.put("docs/specs/invoice.spec.md", "---\nstatus: Accepted\n---\n# Invoice\n")
        self.assertIn("hookSpecificOutput", self.output())

    def test_prints_map_for_a_spec_with_a_status_specs_had_before(self):
        for value in ("🟢 Ready to build", "✅ Built"):
            self.put("docs/specs/invoice.spec.md", f"---\nstatus: {value}\n---\n# Invoice\n")
            self.assertIn("hookSpecificOutput", self.output(), value)

    def test_prints_map_when_brief_exists(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        open(os.path.join(self.tmp.name, "docs", "brief.md"), "w").close()
        self.assertIn("/sdlc:", self.output()["hookSpecificOutput"]["additionalContext"])

    def test_help(self):
        done = self.run_map("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


if __name__ == "__main__":
    unittest.main()

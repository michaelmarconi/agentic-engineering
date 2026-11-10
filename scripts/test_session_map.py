import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "session_map.py")
MAP = os.path.join(HERE, "..", "docs", "lifecycle.md")

sys.path.insert(0, HERE)
import session_map  # noqa: E402


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
        self.assertIn("/agentic:", self.output()["hookSpecificOutput"]["additionalContext"])

    def test_help(self):
        done = self.run_map("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


class OldPython(unittest.TestCase):
    """On a Python older than 3.7 the plugin's checks crash, so the hook warns the person."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_main(self, version):
        out = StringIO()
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.tmp.name)
        with mock.patch.object(session_map.sys, "version_info", version), \
                mock.patch.dict(os.environ, env), redirect_stdout(out):
            code = session_map.main([])
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_warns_the_person_and_claude_on_python_3_6(self):
        out = json.loads(self.run_main((3, 6, 8, "final", 0)))
        warning = out["systemMessage"]
        self.assertIn("Python 3.7 or later", warning)
        self.assertIn("3.6.8", warning)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn(warning, out["hookSpecificOutput"]["additionalContext"])

    def test_warns_even_in_a_project_without_lifecycle_documents(self):
        self.assertIn("systemMessage", json.loads(self.run_main((3, 6, 8, "final", 0))))

    def test_warns_and_still_gives_the_map_in_a_lifecycle_project(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        open(os.path.join(self.tmp.name, "docs", "brief.md"), "w").close()
        with open(MAP, encoding="utf-8") as f:
            expected = f.read()
        out = json.loads(self.run_main((3, 6, 8, "final", 0)))
        self.assertIn("systemMessage", out)
        self.assertIn(expected, out["hookSpecificOutput"]["additionalContext"])

    def test_silent_on_python_3_7(self):
        self.assertEqual(self.run_main((3, 7, 0, "final", 0)), "")


if __name__ == "__main__":
    unittest.main()

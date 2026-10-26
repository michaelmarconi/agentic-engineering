import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "session_map.py")
MAP = os.path.join(HERE, "..", "context", "sdlc.md")


class SessionMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_map(self, *args):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.tmp.name)
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, env=env)

    def test_silent_in_repo_without_lifecycle_documents(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        done = self.run_map()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_prints_map_when_a_lifecycle_folder_exists(self):
        with open(MAP) as f:
            expected = f.read()
        for marker in ["docs/specs", "docs/plans", "docs/decisions"]:
            with self.subTest(marker=marker):
                path = os.path.join(self.tmp.name, marker)
                os.makedirs(path)
                done = self.run_map()
                self.assertEqual(done.returncode, 0)
                self.assertEqual(done.stdout, expected)
                os.rmdir(path)

    def test_prints_map_when_brief_exists(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        open(os.path.join(self.tmp.name, "docs", "brief.md"), "w").close()
        self.assertIn("/sdlc:", self.run_map().stdout)

    def test_help(self):
        done = self.run_map("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


if __name__ == "__main__":
    unittest.main()

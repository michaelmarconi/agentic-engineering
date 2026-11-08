"""Tests for adr.py, run against ADRs written to temporary folders."""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "adr.py")
sys.path.insert(0, HERE)
import adr  # noqa: E402


def text(background="What forces it.", detail="None."):
    return (
        "---\nstatus: 📝 Draft\ndate: 2026-11-08\n---\n\n# Keep sessions in Redis\n\n"
        "## Question\n\nWhere do sessions live?\n\n"
        "## Decision\n\nChosen: keep sessions in Redis, because it is fast.\n\n"
        f"## Background\n\n{background}\n\n## Open questions\n\nNone.\n\n"
        f"## Technical detail\n\n{detail}\n"
    )


class Words(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "0001-session-data-storage.md")

    def put(self, content):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)

    def words(self, *args):
        return subprocess.run([sys.executable, SCRIPT, "words", *args], capture_output=True, text=True)

    def test_short_plain_part_passes(self):
        self.put(text())
        done = self.words(self.path)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"{adr.plain_words(text(), adr.ADR_DETAIL)} words", done.stdout)
        self.assertIn("500", done.stdout)

    def test_technical_detail_is_not_counted(self):
        self.put(text(detail=" ".join(["word"] * 900)))
        self.assertEqual(self.words(self.path).returncode, 0)

    def test_long_plain_part_fails(self):
        self.put(text(background=" ".join(["word"] * 520)))
        done = self.words(self.path)
        self.assertEqual(done.returncode, 1)
        self.assertIn("over", done.stdout)
        self.assertIn("Technical detail", done.stdout)

    def test_unreadable_adr(self):
        done = self.words(os.path.join(self.tmp.name, "missing.md"))
        self.assertEqual(done.returncode, 1)
        self.assertIn("can't read", done.stderr)

    def test_help(self):
        done = self.words("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("Exit codes", done.stdout)


if __name__ == "__main__":
    unittest.main()

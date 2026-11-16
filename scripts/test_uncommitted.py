"""Tests for uncommitted.py, run against throwaway git repositories made in each test.

A stand-in is a character device that is the null device. Making one needs root, so these tests
put an ordinary file where a stand-in would be and make the script's `lstat_of` say that the path
is the null device.
"""

import io
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uncommitted  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class FakeStat:
    def __init__(self, mode, rdev):
        self.st_mode, self.st_rdev = mode, rdev


def null_device():
    return FakeStat(stat.S_IFCHR | 0o666, os.stat(os.devnull).st_rdev)


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.dir)
        self.git("init", "-q", "-b", "main")
        self.put("README.md", "Hello\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Start")
        self.stand_ins = set()
        patch = mock.patch.object(uncommitted, "lstat_of", self.lstat)
        patch.start()
        self.addCleanup(patch.stop)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, env=ENV, check=True,
                              capture_output=True, text=True).stdout

    def put(self, path, text=""):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def stand_in(self, path):
        """An ordinary file that the script is told is the null device."""
        self.put(path)
        self.stand_ins.add(os.path.join(self.dir, path))

    def lstat(self, path):
        return null_device() if path in self.stand_ins else os.lstat(path)

    def check(self):
        return uncommitted.check(self.dir)

    def main(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = uncommitted.main(["--repo", self.dir, *args])
        return code, out.getvalue()


class Check(Repo):
    def test_clean_repository(self):
        self.assertEqual(self.check(), ([], []))

    def test_untracked_file_is_uncommitted(self):
        self.put("notes.txt", "mine\n")
        self.assertEqual(self.check(), (["?? notes.txt"], []))

    def test_changed_and_staged_files_are_uncommitted(self):
        self.put("README.md", "Changed\n")
        self.put("new.txt", "new\n")
        self.git("add", "new.txt")
        self.assertEqual(sorted(self.check()[0]), [" M README.md", "A  new.txt"])

    def test_stand_ins_are_left_out(self):
        self.stand_in(".bashrc")
        self.stand_in(".claude/settings.json")
        self.assertEqual(self.check(), ([], [".bashrc", ".claude/settings.json"]))

    def test_real_file_beside_stand_ins_is_kept(self):
        self.stand_in(".gitconfig")
        self.put(".claude/skills/mine/SKILL.md", "mine\n")
        self.assertEqual(self.check(), (["?? .claude/skills/mine/SKILL.md"], [".gitconfig"]))

    def test_other_character_device_is_kept(self):
        self.put("tty")
        other = FakeStat(stat.S_IFCHR | 0o666, os.stat(os.devnull).st_rdev + 1)
        with mock.patch.object(uncommitted, "lstat_of", lambda p: other if p.endswith("tty") else os.lstat(p)):
            self.assertEqual(self.check(), (["?? tty"], []))

    def test_changed_tracked_file_is_never_a_stand_in(self):
        self.put("README.md", "Changed\n")
        self.stand_ins.add(os.path.join(self.dir, "README.md"))
        self.assertEqual(self.check(), ([" M README.md"], []))

    def test_rename_keeps_its_new_path(self):
        self.git("mv", "README.md", "READ.md")
        self.assertEqual(self.check(), (["R  READ.md"], []))

    def test_rename_in_the_work_tree_keeps_its_new_path(self):
        self.git("mv", "README.md", "READ.md")
        self.git("reset", "-q")
        self.git("add", "-N", "READ.md")
        entries, _ = self.check()
        self.assertIn(" R READ.md", entries)
        self.assertFalse([e for e in entries if "README" in e and not e.startswith(" D")])

    def test_from_a_subfolder_paths_are_from_the_top(self):
        self.stand_in(".bashrc")
        self.put("src/new.py", "x\n")
        os.makedirs(os.path.join(self.dir, "src"), exist_ok=True)
        self.assertEqual(uncommitted.check(os.path.join(self.dir, "src")), (["?? src/new.py"], [".bashrc"]))

    def test_name_that_is_not_utf_8(self):
        name = os.fsdecode(b"caf\xe9.txt")
        try:
            open(os.path.join(self.dir, name), "w").close()
        except (OSError, UnicodeEncodeError):
            self.skipTest("this file system refuses names that are not UTF-8")
        entries, _ = self.check()
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0].startswith("?? caf"))

    def test_path_with_a_space(self):
        self.put("my notes.txt", "x\n")
        self.assertEqual(self.check(), (["?? my notes.txt"], []))


class Main(Repo):
    def test_clean_exits_0(self):
        code, out = self.main()
        self.assertEqual(code, 0)
        self.assertEqual(out, "Nothing is uncommitted.\n")

    def test_uncommitted_exits_1_and_lists_each(self):
        self.put("notes.txt", "mine\n")
        code, out = self.main()
        self.assertEqual(code, 1)
        self.assertEqual(out, "Uncommitted:\n?? notes.txt\n")

    def test_stand_ins_are_counted(self):
        self.stand_in(".bashrc")
        self.stand_in(".mcp.json")
        code, out = self.main()
        self.assertEqual(code, 0)
        self.assertEqual(out, "Nothing is uncommitted.\nLeft out 2 untracked stand-ins for the "
                              "null device, which Claude Code's sandbox puts in place.\n")

    def test_uncommitted_and_stand_ins_together(self):
        self.stand_in(".bashrc")
        self.put("notes.txt", "mine\n")
        code, out = self.main()
        self.assertEqual(code, 1)
        self.assertEqual(out, "Uncommitted:\n?? notes.txt\nLeft out 1 untracked stand-in for the "
                              "null device, which Claude Code's sandbox puts in place.\n")

    def test_git_missing_exits_2(self):
        with mock.patch.object(uncommitted.subprocess, "run", side_effect=FileNotFoundError("git")):
            code, out = self.main()
        self.assertEqual(code, 2)
        self.assertIn("git could not be run", out)

    def test_not_a_repository_exits_2(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = uncommitted.main(["--repo", self.tmp.name])
        self.assertEqual(code, 2)
        self.assertTrue(out.getvalue().startswith("Refused: "))

    def test_help_names_exit_codes(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit):
            uncommitted.main(["--help"])
        self.assertIn("Exit codes", out.getvalue())


if __name__ == "__main__":
    unittest.main()

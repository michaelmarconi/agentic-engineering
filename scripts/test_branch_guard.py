"""Tests for branch_guard.py, against throwaway git repositories made in each test."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import branch_guard  # noqa: E402
import fresh_session  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class Guard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")
        self.repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.repo)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": self.data})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.git("init", "-q", "-b", "main")
        self.git("commit", "-q", "--allow-empty", "-m", "Start")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True, capture_output=True)

    def build_running(self, session="s1"):
        fresh_session.save(session, {"fresh": True, "messages": 1, "building": True})

    def bash(self, command, session="s1"):
        event = {"hook_event_name": "PreToolUse", "session_id": session, "cwd": self.repo,
                 "tool_name": "Bash", "tool_input": {"command": command}}
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            self.assertEqual(branch_guard.main([]), 0)
        text = out.getvalue().strip()
        return json.loads(text)["hookSpecificOutput"] if text else None

    def assert_refused(self, result):
        self.assertIsNotNone(result)
        self.assertEqual(result["permissionDecision"], "deny")
        self.assertIn("default branch", result["permissionDecisionReason"])


class DuringABuild(Guard):
    def setUp(self):
        super().setUp()
        self.build_running()

    def test_commit_on_the_default_branch_refused(self):
        self.assert_refused(self.bash("git add -A && git commit -m 'Build the thing'"))

    def test_push_on_the_default_branch_refused(self):
        self.assert_refused(self.bash("git push origin"))

    def test_commit_with_options_before_it_refused(self):
        self.assert_refused(self.bash(f"git -C {self.repo} commit -m x"))

    def test_push_to_the_default_branch_from_another_refused(self):
        self.git("checkout", "-q", "-b", "build/thing")
        self.assert_refused(self.bash("git push origin HEAD:main"))
        self.assert_refused(self.bash("git push origin main"))
        self.assert_refused(self.bash("git push origin build/thing:refs/heads/main"))

    def test_remote_default_branch_used(self):
        self.git("checkout", "-q", "-b", "trunk")
        self.git("update-ref", "refs/remotes/origin/trunk", "HEAD")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.assert_refused(self.bash("git commit -m x"))

    def test_commit_and_push_on_the_build_branch_allowed(self):
        self.git("checkout", "-q", "-b", "build/thing")
        self.assertIsNone(self.bash("git commit -m x && git push -u origin build/thing"))

    def test_other_commands_allowed(self):
        self.assertIsNone(self.bash("git status && python3 -m unittest"))
        self.assertIsNone(self.bash("git log --format=%s | grep commit"))


class NoBuild(Guard):
    def test_commit_on_the_default_branch_allowed(self):
        self.assertIsNone(self.bash("git commit -m x"))

    def test_another_session_building_does_not_count(self):
        self.build_running("other")
        self.assertIsNone(self.bash("git commit -m x"))


if __name__ == "__main__":
    unittest.main()

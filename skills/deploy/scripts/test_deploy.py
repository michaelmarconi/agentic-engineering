"""Tests for deploy.py. Preflight runs against throwaway git repositories made in each test. The
check's repeats are driven by a fake clock and a fake pause, so no test depends on real time
(AGENTS.md rule 5); for the same reason, a try that hangs until its time limit is not tested."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deploy  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class Preflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.dir)
        self.old_env = dict(os.environ)
        os.environ.update(ENV)
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, self.old_env)
        self.git("init", "-q", "-b", "main")
        self.first = self.change("README.md", "Start")
        bare = os.path.join(self.tmp.name, "origin.git")
        self.git("init", "-q", "--bare", bare)
        self.git("remote", "add", "origin", bare)
        self.git("push", "-q", "origin", "main")
        self.git("remote", "set-head", "origin", "main")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def change(self, path, message):
        with open(os.path.join(self.dir, path), "a", encoding="utf-8") as f:
            f.write(message + "\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def preflight(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = deploy.main(["--repo", self.dir, "preflight", *args])
        return code, out.getvalue()

    def test_clean_commit_on_the_remote_passes(self):
        code, out = self.preflight("--commit", self.first, "--branch", "main", "--checked-out")
        self.assertEqual(code, 0, out)
        self.assertIn("The commit may be deployed.", out)
        self.assertIn(f"Commit: {self.first}", out)
        self.assertNotIn("default branch", out)

    def test_short_name_is_given_in_full(self):
        code, out = self.preflight("--commit", "HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn(f"Commit: {self.first}", out)

    def test_uncommitted_work_refused(self):
        with open(os.path.join(self.dir, "notes.txt"), "w") as f:
            f.write("draft\n")
        code, out = self.preflight("--commit", self.first)
        self.assertEqual(code, 1, out)
        self.assertIn("uncommitted", out)

    def test_commit_not_on_the_remote_refused(self):
        local = self.change("a.txt", "Local only")
        code, out = self.preflight("--commit", local)
        self.assertEqual(code, 1, out)
        self.assertIn("not on the remote", out)

    def test_commit_on_the_remote_but_not_on_the_allowed_branch_refused(self):
        self.git("checkout", "-q", "-b", "feature")
        other = self.change("a.txt", "Feature work")
        self.git("push", "-q", "origin", "feature")
        code, out = self.preflight("--commit", other)
        self.assertEqual(code, 0, out)
        code, out = self.preflight("--commit", other, "--branch", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("not on origin/main", out)

    def test_unknown_allowed_branch_refused(self):
        code, out = self.preflight("--commit", self.first, "--branch", "nope")
        self.assertEqual(code, 1, out)
        self.assertIn("origin/nope", out)

    def test_commit_not_checked_out_refused(self):
        self.change("a.txt", "Later")
        self.git("push", "-q", "origin", "main")
        code, out = self.preflight("--commit", self.first, "--checked-out")
        self.assertEqual(code, 1, out)
        self.assertIn("not the one checked out", out)
        code, out = self.preflight("--commit", self.first)
        self.assertEqual(code, 0, out)

    def test_not_on_the_default_branch_said_plainly(self):
        self.git("checkout", "-q", "-b", "hotfix")
        fix = self.change("a.txt", "Hotfix")
        self.git("push", "-q", "origin", "hotfix")
        code, out = self.preflight("--commit", fix, "--branch", "hotfix")
        self.assertEqual(code, 0, out)
        self.assertIn("not on the default branch (main)", out)

    def test_unknown_default_branch_said_plainly(self):
        self.git("remote", "set-head", "origin", "--delete")
        code, out = self.preflight("--commit", self.first)
        self.assertEqual(code, 0, out)
        self.assertIn("default branch is not known here", out)

    def test_unknown_commit(self):
        code, out = self.preflight("--commit", "no-such-commit")
        self.assertEqual(code, 2, out)
        self.assertIn("no commit named no-such-commit", out)


class FakeTime:
    """A clock that moves only when paused, so the check's repeats never wait for real."""

    def __init__(self):
        self.now = 0.0
        self.pauses = []

    def clock(self):
        return self.now

    def pause(self, seconds):
        self.pauses.append(seconds)
        self.now += seconds


class Check(unittest.TestCase):
    def check(self, results, wait, every=5):
        time = FakeTime()
        tries = []

        def run(command, timeout):
            tries.append(timeout)
            return results[min(len(tries), len(results)) - 1]

        code, lines = deploy.check("probe", wait, every, run=run, clock=time.clock, pause=time.pause)
        return code, "\n".join(lines), tries, time

    def test_passes_first_try(self):
        code, out, tries, time = self.check([(0, "ok")], wait=60)
        self.assertEqual(code, 0)
        self.assertEqual(len(tries), 1)
        self.assertEqual(time.pauses, [])
        self.assertIn("Try 1: exit 0", out)
        self.assertIn("The check passed.", out)
        self.assertIn("ok", out)

    def test_passes_on_a_later_try(self):
        code, out, tries, time = self.check([(1, "down"), (1, "down"), (0, "up")], wait=60)
        self.assertEqual(code, 0)
        self.assertEqual(len(tries), 3)
        self.assertEqual(time.pauses, [5, 5])
        self.assertIn("Try 2: exit 1", out)
        self.assertIn("Try 3: exit 0", out)
        self.assertIn("up", out)
        self.assertNotIn("down", out)

    def test_never_passes_before_the_wait_runs_out(self):
        code, out, tries, time = self.check([(1, "still down")], wait=12)
        self.assertEqual(code, 1)
        self.assertEqual(len(tries), 3)
        self.assertLessEqual(sum(time.pauses), 12)
        self.assertIn("did not pass within 12 seconds", out)
        self.assertIn("still down", out)

    def test_wait_zero_runs_once(self):
        code, out, tries, time = self.check([(1, "down"), (0, "up")], wait=0)
        self.assertEqual(code, 1)
        self.assertEqual(len(tries), 1)
        self.assertEqual(time.pauses, [])

    def test_each_try_is_limited_to_the_time_left(self):
        _, _, tries, _ = self.check([(1, "")], wait=300, every=100)
        self.assertEqual(tries[:3], [300, 200, 100])
        self.assertTrue(all(t >= deploy.SHORTEST_TRY for t in tries))

    def test_a_command_that_cannot_start_is_not_repeated(self):
        code, out, tries, _ = self.check([(None, "could not be started: no such file")], wait=60)
        self.assertEqual(code, 1)
        self.assertEqual(len(tries), 1)
        self.assertIn("could not be started", out)


class RealCommand(unittest.TestCase):
    def run_check(self, *command):
        out = io.StringIO()
        with redirect_stdout(out):
            code = deploy.main(["check", "--wait", "0", "--", *command])
        return code, out.getvalue()

    def test_a_shell_command_line_passes(self):
        code, out = self.run_check(f'"{sys.executable}" -c "print(\'serving\')"')
        self.assertEqual(code, 0, out)
        self.assertIn("serving", out)

    def test_a_failing_command_fails(self):
        code, out = self.run_check(sys.executable, "-c", "import sys; print('broken'); sys.exit(3)")
        self.assertEqual(code, 1, out)
        self.assertIn("Try 1: exit 3", out)
        self.assertIn("broken", out)

    def test_a_program_that_does_not_exist(self):
        code, out = self.run_check("no-such-program-for-deploy-tests", "--flag")
        self.assertEqual(code, 1, out)
        self.assertIn("could not be started", out)

    def test_a_shell_command_not_found_fails(self):
        code, out = self.run_check("no-such-program-for-deploy-tests --flag")
        self.assertEqual(code, 1, out)
        self.assertIn("Try 1: exit 127", out)

    def test_every_must_be_more_than_zero(self):
        with self.assertRaises(SystemExit) as raised, redirect_stdout(io.StringIO()):
            deploy.main(["check", "--wait", "10", "--every", "0", "--", "true"])
        self.assertEqual(raised.exception.code, 2)

    def test_no_command_is_wrong_use(self):
        with self.assertRaises(SystemExit) as raised, redirect_stdout(io.StringIO()):
            deploy.main(["check", "--wait", "0"])
        self.assertEqual(raised.exception.code, 2)


class Help(unittest.TestCase):
    def test_help_covers_both_commands_and_exit_codes(self):
        done = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy.py"),
                               "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        for word in ("preflight", "check", "--wait", "--checked-out", "Exit codes"):
            self.assertIn(word, done.stdout)


if __name__ == "__main__":
    unittest.main()

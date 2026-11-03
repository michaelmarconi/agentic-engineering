"""Tests for hand_over.py, run against throwaway git repositories made in each test."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hand_over  # noqa: E402

PLAN = "docs/plans/2026-11-03-thing.md"

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def plan(status="🟢 Ready to build"):
    return f"---\nstatus: {status}\n---\n\n# Thing\n\n## Plan\n\nDo the thing.\n"


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.dir)
        self.git("init", "-q", "-b", "main")
        self.put(PLAN, plan())
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Start")
        self.bare = self.add_origin()
        self.git("push", "-q", "origin", "main")
        self.git("remote", "set-head", "origin", "main")
        self.git("checkout", "-q", "-b", "build/thing")
        self.old_env = dict(os.environ)
        os.environ.update(ENV)
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, self.old_env)

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.dir, env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, path):
        with open(os.path.join(self.dir, path), encoding="utf-8") as f:
            return f.read()

    def add_origin(self):
        bare = os.path.join(self.tmp.name, "origin.git")
        self.git("init", "-q", "--bare", bare, cwd=self.tmp.name)
        self.git("remote", "add", "origin", bare)
        return bare

    def run_it(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = hand_over.main(["--repo", self.dir, "--plan", PLAN, "--message", "Build the thing", *args])
        return code, out.getvalue()

    def subjects(self):
        return self.git("log", "--format=%s").splitlines()


class Commit(Repo):
    def test_work_committed_with_the_message(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertEqual(self.subjects()[0], "Build the thing")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertIn("build/thing", out)

    def test_nothing_to_commit_said_so(self):
        code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertEqual(self.subjects(), ["Start"])
        self.assertIn("nothing new to commit", out)

    def test_refused_on_the_default_branch(self):
        self.git("checkout", "-q", "main")
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it()
        self.assertEqual(code, 2)
        self.assertEqual(self.subjects(), ["Start"])
        self.assertIn("default branch", out)

    def test_refused_on_the_remote_default_branch(self):
        self.git("checkout", "-q", "-b", "trunk")
        self.git("push", "-q", "origin", "trunk")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        code, out = self.run_it()
        self.assertEqual(code, 2)
        self.assertIn("trunk", out)

    def test_refused_without_a_branch(self):
        self.git("checkout", "-q", "--detach")
        code, out = self.run_it()
        self.assertEqual(code, 2)
        self.assertIn("branch", out)


class Built(Repo):
    def test_reviews_passed_marks_the_plan_built(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 0)
        self.assertIn("status: ✅ Built\n", self.read(PLAN))
        self.assertEqual(self.subjects()[:2], ["Mark the plan 2026-11-03-thing.md as built", "Build the thing"])
        self.assertIn("✅ Built", out)

    def test_plan_left_ready_without_passing_reviews(self):
        code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertIn("status: 🟢 Ready to build\n", self.read(PLAN))
        self.assertIn("🟢 Ready to build", out)

    def test_only_a_ready_plan_is_marked_built(self):
        self.put(PLAN, plan("📝 Draft"))
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 1)
        self.assertIn("status: 📝 Draft\n", self.read(PLAN))
        self.assertIn("📝 Draft", out)

    def test_ready_written_before_the_emoji_counts(self):
        self.put(PLAN, plan("Ready to build"))
        code, _ = self.run_it("--reviews-passed")
        self.assertEqual(code, 0)
        self.assertIn("status: ✅ Built\n", self.read(PLAN))

    def test_only_the_status_line_changes(self):
        before = self.read(PLAN)
        self.run_it("--reviews-passed")
        self.assertEqual(self.read(PLAN), before.replace("🟢 Ready to build", "✅ Built"))

    def test_missing_plan_refused(self):
        os.remove(os.path.join(self.dir, PLAN))
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 2)
        self.assertIn(PLAN, out)


class Push(Repo):
    def test_pushed_to_origin(self):
        bare = self.bare
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 0)
        self.assertEqual(self.git("rev-parse", "build/thing", cwd=bare), self.git("rev-parse", "HEAD"))
        self.assertIn("pushed", out)

    def test_refused_without_an_origin(self):
        self.git("remote", "remove", "origin")
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 2)
        self.assertEqual(self.subjects(), ["Start"])
        self.assertIn("status: 🟢 Ready to build\n", self.read(PLAN))
        self.assertIn("no remote named `origin`", out)

    def test_refused_without_the_remote_default_branch(self):
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        code, out = self.run_it()
        self.assertEqual(code, 2)
        self.assertEqual(self.subjects(), ["Start"])
        self.assertIn("git remote set-head origin -a", out)

    def test_failed_push_reported(self):
        self.git("remote", "set-url", "origin", os.path.join(self.tmp.name, "missing.git"))
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertEqual(self.subjects()[0], "Build the thing")
        self.assertIn("push failed", out)


class Help(unittest.TestCase):
    def test_help(self):
        result = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_over.py"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--reviews-passed", result.stdout)


if __name__ == "__main__":
    unittest.main()

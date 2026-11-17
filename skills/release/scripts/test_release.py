"""Tests for release.py, run against throwaway git repositories made in each test."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class Repo(unittest.TestCase):
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

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.dir, env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "a", encoding="utf-8") as f:
            f.write(text)

    def change(self, path, message):
        self.put(path, message + "\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run_it(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = release.main(["--repo", self.dir, *args])
        return code, out.getvalue()

    def notes(self, *args):
        code, out = self.run_it("notes", *args)
        self.assertEqual(code, 0, out)
        return json.loads(out)


class Notes(Repo):
    def test_notes_since_the_last_release(self):
        self.change("a.txt", "Build export\n\nRelease-note: You can now export your mail as CSV.")
        last = self.git("rev-parse", "HEAD")
        built = self.change("b.txt", "Build search\n\nRelease-note: You can search your mail.")
        found = self.notes("--since", last)
        self.assertEqual(found["notes"], [{"commit": built, "note": "You can search your mail."}])
        self.assertEqual(found["without_notes"], [])

    def test_every_commit_when_there_was_no_earlier_release(self):
        one = self.change("a.txt", "Build export\n\nRelease-note: You can export.")
        found = self.notes()
        self.assertEqual([n["commit"] for n in found["notes"]], [one])
        self.assertEqual([c["commit"] for c in found["without_notes"]], [self.first])

    def test_several_notes_in_one_commit_in_order(self):
        self.change("a.txt", "Build\n\nRelease-note: First.\nRelease-note: Second.")
        found = self.notes("--since", self.first)
        self.assertEqual([n["note"] for n in found["notes"]], ["First.", "Second."])

    def test_note_inside_a_squash_merge_body_is_found(self):
        self.change("a.txt", "Export (#12)\n\n* Build export\n\nRelease-note: You can export.\n\n"
                             "* Mark the plan built\n\nCo-authored-by: Someone <s@example.com>")
        found = self.notes("--since", self.first)
        self.assertEqual([n["note"] for n in found["notes"]], ["You can export."])

    def test_notes_from_a_merged_branch_are_found_once(self):
        self.git("checkout", "-q", "-b", "build/export")
        built = self.change("a.txt", "Build export\n\nRelease-note: You can export.")
        self.git("checkout", "-q", "main")
        self.change("c.txt", "Other work on main")
        self.git("merge", "-q", "--no-ff", "-m", "Merge build/export", "build/export")
        found = self.notes("--since", self.first)
        self.assertEqual(found["notes"], [{"commit": built, "note": "You can export."}])
        self.assertEqual([c["subject"] for c in found["without_notes"]], ["Other work on main"])

    def test_the_same_note_twice_is_given_once(self):
        # A build run again on its branch hands over again, with the same note.
        self.change("a.txt", "Build\n\nRelease-note: You can export.")
        self.change("b.txt", "Build again\n\nRelease-note: You can export.")
        found = self.notes("--since", self.first)
        self.assertEqual([n["note"] for n in found["notes"]], ["You can export."])

    def test_commits_without_a_note_listed_with_their_subject(self):
        quick = self.change("a.txt", "Correct a typo in the help text")
        found = self.notes("--since", self.first)
        self.assertEqual(found["without_notes"], [{"commit": quick, "subject": "Correct a typo in the help text"}])

    def test_a_commit_that_changed_no_files_and_has_no_note_is_left_out(self):
        self.git("commit", "-q", "--allow-empty", "-m", "Nothing")
        self.assertEqual(self.notes("--since", self.first)["without_notes"], [])

    def test_label_in_any_case_and_with_spaces(self):
        self.change("a.txt", "Build\n\n  release-note:   You can export.  ")
        self.assertEqual([n["note"] for n in self.notes("--since", self.first)["notes"]], ["You can export."])

    def test_a_label_with_no_text_is_not_a_note(self):
        self.change("a.txt", "Build\n\nRelease-note:")
        found = self.notes("--since", self.first)
        self.assertEqual(found["notes"], [])
        self.assertEqual(len(found["without_notes"]), 1)

    def test_up_to_a_given_commit(self):
        one = self.change("a.txt", "One\n\nRelease-note: One.")
        self.change("b.txt", "Two\n\nRelease-note: Two.")
        found = self.notes("--since", self.first, "--to", one)
        self.assertEqual([n["note"] for n in found["notes"]], ["One."])

    def test_unknown_commit_refused(self):
        code, out = self.run_it("notes", "--since", "no-such-commit")
        self.assertEqual(code, 2)
        self.assertIn("no-such-commit", out)

    def test_last_release_not_before_the_commit_refused(self):
        self.git("checkout", "-q", "-b", "side")
        side = self.change("s.txt", "Side")
        self.git("checkout", "-q", "main")
        code, out = self.run_it("notes", "--since", side)
        self.assertEqual(code, 2)
        self.assertIn("not before", out)


class PublishCheck(Repo):
    def setUp(self):
        super().setUp()
        self.bare = os.path.join(self.tmp.name, "origin.git")
        self.git("init", "-q", "--bare", self.bare, cwd=self.tmp.name)
        self.git("remote", "add", "origin", self.bare)
        self.git("push", "-q", "origin", "main")
        self.git("remote", "set-head", "origin", "main")

    def check(self, *args):
        return self.run_it("publish-check", *args)

    def test_merged_commit_on_the_allowed_branch_passes(self):
        code, out = self.check("--commit", "HEAD", "--branch", "main")
        self.assertEqual(code, 0, out)
        self.assertIn(self.first, out)
        self.assertIn("may be published", out)

    def test_older_commit_on_the_branch_passes_and_later_commits_are_named(self):
        later = self.change("a.txt", "Later work")
        self.git("push", "-q", "origin", "main")
        code, out = self.check("--commit", self.first, "--branch", "main")
        self.assertEqual(code, 0, out)
        self.assertIn(later[:12], out)
        self.assertIn("newer", out)

    def test_commit_not_on_the_remote_branch_refused(self):
        self.change("a.txt", "Not pushed")
        code, out = self.check("--commit", "HEAD", "--branch", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("not on origin/main", out)

    def test_commit_only_on_another_branch_refused(self):
        self.git("checkout", "-q", "-b", "release/1.4.0")
        self.change("v.txt", "Release 1.4.0")
        self.git("push", "-q", "origin", "release/1.4.0")
        code, out = self.check("--commit", "HEAD", "--branch", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("not on origin/main", out)

    def test_uncommitted_work_refused(self):
        self.put("a.txt", "loose\n")
        code, out = self.check("--commit", "HEAD", "--branch", "main")
        self.assertEqual(code, 1, out)
        self.assertIn("uncommitted", out)

    def test_not_the_default_branch_said_plainly(self):
        self.git("checkout", "-q", "-b", "stable")
        self.git("push", "-q", "origin", "stable")
        code, out = self.check("--commit", "HEAD", "--branch", "stable")
        self.assertEqual(code, 0, out)
        self.assertIn("not the default branch", out)

    def test_unknown_branch_refused(self):
        code, out = self.check("--commit", "HEAD", "--branch", "nope")
        self.assertEqual(code, 1, out)
        self.assertIn("origin/nope", out)

    def test_unknown_commit(self):
        code, out = self.check("--commit", "no-such-commit", "--branch", "main")
        self.assertEqual(code, 2, out)


class Help(unittest.TestCase):
    def test_help(self):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "release.py")
        done = subprocess.run([sys.executable, script, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("notes", done.stdout)
        self.assertIn("publish-check", done.stdout)


if __name__ == "__main__":
    unittest.main()

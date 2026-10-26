"""Tests for issue.py."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issue  # noqa: E402


def make_plugin(root, repository="https://github.com/acme/tools", version="1.2.3"):
    os.makedirs(os.path.join(root, ".claude-plugin"))
    manifest = {"name": "sdlc", "version": version}
    if repository is not None:
        manifest["repository"] = repository
    with open(os.path.join(root, ".claude-plugin", "plugin.json"), "w") as f:
        json.dump(manifest, f)


def done(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class RepoSlugTest(unittest.TestCase):
    def test_https_url(self):
        self.assertEqual(issue.repo_slug("https://github.com/acme/tools"), "acme/tools")

    def test_trailing_git_and_slash(self):
        self.assertEqual(issue.repo_slug("https://github.com/acme/tools.git/"), "acme/tools")

    def test_ssh_url(self):
        self.assertEqual(issue.repo_slug("git@github.com:acme/tools.git"), "acme/tools")

    def test_object_form(self):
        self.assertEqual(
            issue.repo_slug({"type": "git", "url": "https://github.com/acme/tools"}), "acme/tools"
        )

    def test_not_github(self):
        with self.assertRaises(ValueError):
            issue.repo_slug("https://gitlab.com/acme/tools")


class ManifestTest(unittest.TestCase):
    def test_reads_plugin_json(self):
        with tempfile.TemporaryDirectory() as root:
            make_plugin(root)
            self.assertEqual(issue.read_manifest(root)["version"], "1.2.3")

    def test_finds_root_from_script(self):
        here = os.path.dirname(os.path.abspath(__file__))
        root = issue.plugin_root()
        self.assertTrue(os.path.isfile(os.path.join(root, ".claude-plugin", "plugin.json")))
        self.assertTrue(here.startswith(root))


class LinkTest(unittest.TestCase):
    def test_carries_title_body_and_label(self):
        url = issue.new_issue_link("acme/tools", "Spec skill names a library", "Body & more", "bug")
        parsed = urlparse(url)
        self.assertEqual(parsed.netloc, "github.com")
        self.assertEqual(parsed.path, "/acme/tools/issues/new")
        query = parse_qs(parsed.query)
        self.assertEqual(query["title"], ["Spec skill names a library"])
        self.assertEqual(query["body"], ["Body & more"])
        self.assertEqual(query["labels"], ["bug"])

    def test_label_for_each_kind(self):
        self.assertEqual(issue.LABELS, {"bug": "bug", "improvement": "enhancement"})


class ContextTest(unittest.TestCase):
    def test_lists_versions(self):
        with tempfile.TemporaryDirectory() as root:
            make_plugin(root)
            with mock.patch.object(issue, "run", return_value=done(0, "2.1.0 (Claude Code)\n")):
                text = issue.context(root)
        self.assertIn("- Plugin: sdlc 1.2.3", text)
        self.assertIn("- Claude Code: 2.1.0 (Claude Code)", text)
        self.assertIn("- OS: ", text)

    def test_claude_version_unknown_when_missing(self):
        with tempfile.TemporaryDirectory() as root:
            make_plugin(root)
            with mock.patch.object(issue, "run", side_effect=OSError):
                text = issue.context(root)
        self.assertIn("- Claude Code: unknown", text)


class FileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        make_plugin(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, *, gh=True, auth=0, create=None, link_only=False, body="## What happened\n"):
        calls = []

        def fake_run(args, input=None):
            calls.append((args, input))
            if args[:3] == ["gh", "auth", "status"]:
                return done(auth)
            if args[:3] == ["gh", "issue", "create"]:
                return create or done(0, "https://github.com/acme/tools/issues/7\n")
            raise AssertionError(args)

        out = io.StringIO()
        with mock.patch.object(issue, "run", side_effect=fake_run), \
                mock.patch.object(issue.shutil, "which", return_value="/bin/gh" if gh else None), \
                mock.patch("sys.stdout", out):
            code = issue.file_issue(self.root, "bug", "A title", body, link_only)
        return code, out.getvalue(), calls

    def test_files_with_gh_when_signed_in(self):
        code, out, calls = self.file()
        self.assertEqual(code, 0)
        self.assertEqual(out, "filed https://github.com/acme/tools/issues/7\n")
        args, stdin = calls[-1]
        self.assertEqual(
            args,
            ["gh", "issue", "create", "--repo", "acme/tools", "--title", "A title",
             "--label", "bug", "--body-file", "-"],
        )
        self.assertEqual(stdin, "## What happened\n")

    def test_link_when_gh_missing(self):
        code, out, calls = self.file(gh=False)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("link https://github.com/acme/tools/issues/new?"))
        self.assertEqual(calls, [])

    def test_link_when_gh_signed_out(self):
        code, out, calls = self.file(auth=1)
        self.assertTrue(out.startswith("link "))
        self.assertEqual(len(calls), 1)

    def test_link_when_gh_create_fails(self):
        code, out, _ = self.file(create=done(1, "", "label not found"))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("link "))

    def test_link_only_never_runs_gh(self):
        code, out, calls = self.file(link_only=True)
        self.assertTrue(out.startswith("link "))
        self.assertEqual(calls, [])

    def test_too_long_for_link(self):
        code, out, _ = self.file(gh=False, body="x" * issue.MAX_URL)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")

    def test_empty_body_refused(self):
        code, _, calls = self.file(body="  \n")
        self.assertEqual(code, 2)
        self.assertEqual(calls, [])


class MainTest(unittest.TestCase):
    def test_file_reads_body_from_stdin(self):
        with mock.patch.object(issue, "file_issue", return_value=0) as file_issue, \
                mock.patch("sys.stdin", io.StringIO("the body")):
            code = issue.main(["file", "--kind", "improvement", "--title", "T", "--link-only"])
        self.assertEqual(code, 0)
        self.assertEqual(file_issue.call_args.args[1:], ("improvement", "T", "the body", True))

    def test_unknown_kind_is_usage_error(self):
        with self.assertRaises(SystemExit) as raised, mock.patch("sys.stderr", io.StringIO()):
            issue.main(["file", "--kind", "question", "--title", "T"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

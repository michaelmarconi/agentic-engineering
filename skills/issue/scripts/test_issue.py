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
    os.makedirs(os.path.join(root, ".github", "ISSUE_TEMPLATE"))
    for kind, label in (("bug", "bug"), ("improvement", "[enhancement]")):
        with open(os.path.join(root, ".github", "ISSUE_TEMPLATE", kind + ".md"), "w") as f:
            f.write("---\nname: %s\nlabels: %s\n---\n\n## Context\n" % (kind, label))


def stdin_bytes(data):
    return io.TextIOWrapper(io.BytesIO(data), encoding="utf-8")


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
        url = issue.new_issue_link("acme/tools", "Spec skill names a library", "Body & more", ["bug"])
        parsed = urlparse(url)
        self.assertEqual(parsed.netloc, "github.com")
        self.assertEqual(parsed.path, "/acme/tools/issues/new")
        query = parse_qs(parsed.query)
        self.assertEqual(query["title"], ["Spec skill names a library"])
        self.assertEqual(query["body"], ["Body & more"])
        self.assertEqual(query["labels"], ["bug"])

    def test_labels_come_from_template(self):
        with tempfile.TemporaryDirectory() as root:
            make_plugin(root)
            self.assertEqual(issue.template_labels(root, "bug"), ["bug"])
            self.assertEqual(issue.template_labels(root, "improvement"), ["enhancement"])

    def test_plugin_templates_set_labels(self):
        root = issue.plugin_root()
        self.assertEqual(issue.template_labels(root, "bug"), ["bug"])
        self.assertEqual(issue.template_labels(root, "improvement"), ["enhancement"])

    def labels(self, frontmatter, body=""):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, ".github", "ISSUE_TEMPLATE")
            os.makedirs(path)
            with open(os.path.join(path, "bug.md"), "w") as f:
                f.write("---\nname: Bug\n" + frontmatter + "---\n" + body)
            return issue.template_labels(root, "bug")

    def test_label_forms(self):
        self.assertEqual(self.labels("labels: [bug, 'triage']\n"), ["bug", "triage"])
        self.assertEqual(self.labels("labels: bug, triage\n"), ["bug", "triage"])
        self.assertEqual(self.labels('labels: "bug"\n'), ["bug"])

    def test_comment_after_label(self):
        self.assertEqual(self.labels("labels: bug  # triage later\n"), ["bug"])

    def test_no_label_is_an_error(self):
        for frontmatter in ("labels: []\n", 'labels: ""\n', ""):
            with self.assertRaises(ValueError):
                self.labels(frontmatter, "labels: bug\n")


class ContextTest(unittest.TestCase):
    def test_lists_versions(self):
        with tempfile.TemporaryDirectory() as root:
            make_plugin(root)
            with mock.patch.object(issue, "run", return_value=done(0, "2.1.0 (Claude Code)\n")), \
                    mock.patch.object(issue, "os_name", return_value="macOS 15.1"):
                text = issue.context(root)
        self.assertEqual(
            text, "- Plugin: sdlc 1.2.3\n- Claude Code: 2.1.0 (Claude Code)\n- OS: macOS 15.1\n"
        )

    def test_claude_version_unknown_when_missing(self):
        with mock.patch.object(issue, "run", side_effect=OSError):
            self.assertEqual(issue.claude_version(), "unknown")


class OsNameTest(unittest.TestCase):
    def test_macos_by_product_version(self):
        with mock.patch.object(issue.platform, "system", return_value="Darwin"), \
                mock.patch.object(issue.platform, "mac_ver", return_value=("15.1", "", "")):
            self.assertEqual(issue.os_name(), "macOS 15.1")

    def test_linux_by_distribution_not_kernel(self):
        with mock.patch.object(issue.platform, "system", return_value="Linux"), \
                mock.patch.object(issue.platform, "release", return_value="5.15-acmecorp"), \
                mock.patch.object(issue.platform, "freedesktop_os_release", create=True,
                                  return_value={"PRETTY_NAME": "Acme Workstation",
                                                "ID": "ubuntu", "VERSION_ID": "24.04"}):
            self.assertEqual(issue.os_name(), "Linux ubuntu 24.04")

    def test_linux_unknown_distribution_not_named(self):
        with mock.patch.object(issue.platform, "system", return_value="Linux"), \
                mock.patch.object(issue.platform, "freedesktop_os_release", create=True,
                                  return_value={"ID": "acmecorp-linux", "VERSION_ID": "7"}):
            self.assertEqual(issue.os_name(), "Linux")

    def test_linux_without_os_release(self):
        with mock.patch.object(issue.platform, "system", return_value="Linux"), \
                mock.patch.object(issue.platform, "freedesktop_os_release", create=True,
                                  side_effect=OSError):
            self.assertEqual(issue.os_name(), "Linux")


class ParseDraftTest(unittest.TestCase):
    def test_first_line_is_title(self):
        self.assertEqual(
            issue.parse_draft("A `title` with $HOME\n\n## What happened\nIt broke.\n"),
            ("A `title` with $HOME", "## What happened\nIt broke.\n"),
        )

    def test_windows_line_endings(self):
        self.assertEqual(issue.parse_draft("T\r\n\r\nbody\r\n"), ("T", "body\n"))

    def test_heading_or_label_line_is_no_title(self):
        for first in ("# A title", "Title: A title", "**Title:** A title", "*Title:* A title",
                      "__A title__", "> A title", "Subject: A title", "Kind: bug", "",
                      "\ufeffKind: bug"):
            self.assertEqual(issue.parse_draft(first + "\n\nbody")[0], "", first)

    def test_titles_starting_with_symbols_kept(self):
        for title in ("/spec names a library", "*.spec.md files in subfolders are ignored",
                      "_private names leak", "#include paths break /spec"):
            self.assertEqual(issue.parse_draft(title + "\n\nb")[0], title)

    def test_byte_order_mark_dropped(self):
        self.assertEqual(issue.parse_draft("\ufeffT\n\nb"), ("T", "b\n"))


class FileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        make_plugin(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, *, signed_in="jane", create=None, login="jane", labeller=True,
             draft="A title\n\n## What happened\n"):
        calls = []

        def fake_run(args, input=None):
            calls.append((args, input))
            if isinstance(create, BaseException):
                raise create
            return create or done(0, "Creating issue\nhttps://github.com/acme/tools/issues/7\n")

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(issue, "run", side_effect=fake_run), \
                mock.patch.object(issue, "gh_login", return_value=signed_in) as gh_login, \
                mock.patch.object(issue, "can_label", return_value=labeller), \
                mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
            code = issue.file_issue(self.root, "bug", draft, login)
        self.gh_login_called = gh_login.called
        return code, out.getvalue(), calls, err.getvalue()

    def test_files_with_gh_on_github_com(self):
        code, out, calls, _ = self.file()
        self.assertEqual(code, 0)
        self.assertEqual(out, "filed https://github.com/acme/tools/issues/7\n")
        args, stdin = calls[-1]
        self.assertEqual(
            args,
            ["gh", "issue", "create", "--repo", "github.com/acme/tools", "--title", "A title",
             "--label", "bug", "--body-file", "-"],
        )
        self.assertEqual(stdin, "## What happened\n")

    def test_no_label_when_account_may_not_label(self):
        _, _, calls, _ = self.file(labeller=False)
        self.assertNotIn("--label", calls[-1][0])

    def test_login_case_ignored(self):
        code, out, _, _ = self.file(signed_in="Jane")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("filed "))

    def test_link_when_gh_cannot_start(self):
        code, out, _, err = self.file(create=OSError("gh not found"))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("link "))
        self.assertIn("gh not found", err)

    def test_refuses_another_account(self):
        code, out, calls, err = self.file(signed_in="jane-work")
        self.assertEqual(code, 2)
        self.assertEqual((out, calls), ("", []))
        self.assertIn("jane-work", err)

    def test_link_when_gh_no_longer_signed_in(self):
        code, out, calls, err = self.file(signed_in=None)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("link https://github.com/acme/tools/issues/new?"))
        self.assertEqual(calls, [])
        self.assertIn("couldn't confirm", err)

    def test_link_only_never_runs_gh(self):
        code, out, calls, _ = self.file(login=None)
        self.assertTrue(out.startswith("link "))
        self.assertEqual(calls, [])
        self.assertFalse(self.gh_login_called)

    def test_unsure_when_gh_create_fails(self):
        # gh may report an error after GitHub created the issue, so a link could duplicate it.
        code, out, _, err = self.file(create=done(1, "", "connection reset"))
        self.assertEqual(code, 4)
        self.assertEqual(out, "")
        self.assertIn("connection reset", err)
        self.assertIn("https://github.com/acme/tools/issues", err)

    def test_link_when_github_refuses(self):
        code, out, _, err = self.file(create=done(1, "", "HTTP 403: Resource not accessible"))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("link "))
        self.assertIn("refused", err)

    def test_unsure_when_gh_times_out(self):
        code, out, _, _ = self.file(create=subprocess.TimeoutExpired("gh", 60))
        self.assertEqual((code, out), (4, ""))

    def test_unsure_when_gh_prints_no_url(self):
        code, out, _, _ = self.file(create=done(0, ""))
        self.assertEqual((code, out), (4, ""))

    def test_too_long_for_link(self):
        code, out, _, _ = self.file(login=None, draft="T\n\n" + "x" * issue.MAX_URL)
        self.assertEqual((code, out), (3, ""))

    def test_over_github_limits_refused_before_gh(self):
        for draft in ("T\n\n" + "x" * (issue.MAX_BODY + 1), "T" * 257 + "\n\nbody"):
            code, out, calls, _ = self.file(draft=draft)
            self.assertEqual((code, calls), (3, []))

    def test_missing_body_refused(self):
        code, _, calls, _ = self.file(draft="Only a title\n")
        self.assertEqual((code, calls), (2, []))


class CanLabelTest(unittest.TestCase):
    def test_triage_permission(self):
        for stdout, expected in (("true\n", True), ("false\n", False)):
            with mock.patch.object(issue, "run", return_value=done(0, stdout)):
                self.assertEqual(issue.can_label("acme/tools"), expected)

    def test_no_when_api_fails(self):
        with mock.patch.object(issue, "run", return_value=done(1, "", "404")):
            self.assertFalse(issue.can_label("acme/tools"))


class GhLoginTest(unittest.TestCase):
    def gh_login(self, gh=True, api=None):
        def fake_run(args, input=None):
            self.assertEqual(args[:4], ["gh", "api", "--hostname", "github.com"])
            return api or done(0, "jane\n")

        with mock.patch.object(issue, "run", side_effect=fake_run), \
                mock.patch.object(issue.shutil, "which", return_value="/bin/gh" if gh else None):
            return issue.gh_login()

    def test_login_when_signed_in(self):
        self.assertEqual(self.gh_login(), "jane")

    def test_none_when_gh_cannot_file(self):
        self.assertIsNone(self.gh_login(gh=False))
        self.assertIsNone(self.gh_login(api=done(4, "", "not logged in")))
        self.assertIsNone(self.gh_login(api=done(1, "", "403")))

    def test_account_prints_route(self):
        for login, line in (("jane", "gh jane\n"), (None, "link\n")):
            with mock.patch.object(issue, "gh_login", return_value=login), \
                    mock.patch("sys.stdout", io.StringIO()) as out:
                self.assertEqual(issue.main(["account"]), 0)
            self.assertEqual(out.getvalue(), line)


class MainTest(unittest.TestCase):
    def test_file_reads_draft_from_stdin(self):
        with mock.patch.object(issue, "file_issue", return_value=0) as file_issue, \
                mock.patch("sys.stdin", stdin_bytes("T\n\nthe body".encode())):
            code = issue.main(["file", "--kind", "improvement", "--as", "jane"])
        self.assertEqual(code, 0)
        self.assertEqual(file_issue.call_args.args[1:], ("improvement", "T\n\nthe body", "jane"))

    def test_file_needs_a_route(self):
        with self.assertRaises(SystemExit) as raised, mock.patch("sys.stderr", io.StringIO()):
            issue.main(["file", "--kind", "bug"])
        self.assertEqual(raised.exception.code, 2)

    def test_non_utf8_draft_is_usage_error(self):
        with mock.patch("sys.stdin", stdin_bytes(b"T\n\n\xff\xfe")), \
                mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(issue.main(["file", "--kind", "bug", "--link-only"]), 2)

    def test_bad_repository_exits_1(self):
        with mock.patch.object(issue, "file_issue", side_effect=ValueError("not GitHub")), \
                mock.patch("sys.stdin", stdin_bytes(b"T\n\nb")), \
                mock.patch("sys.stderr", io.StringIO()) as err:
            code = issue.main(["file", "--kind", "bug", "--link-only"])
        self.assertEqual(code, 1)
        self.assertIn("not GitHub", err.getvalue())

    def test_unknown_kind_is_usage_error(self):
        with self.assertRaises(SystemExit) as raised, mock.patch("sys.stderr", io.StringIO()):
            issue.main(["file", "--kind", "question", "--link-only"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

"""Tests for verify.py, run against throwaway git repositories made in each test."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify  # noqa: E402
import verify_relay  # noqa: E402  (verify.py puts the plugin's scripts/ on the path)

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

SPEC = """---
type: Spec
status: {status}
date: 2026-11-10
---

# Mail pull

## Story

The owner wants mail pulled so they can read it offline.

## Requirements

### 1. Pull new mail

When the owner runs a pull, the system SHALL fetch each new message.

| Example | New mail |
|---|---|
| Given | two new messages on the server |
| When | the owner runs a pull |
| Then | both are stored |

| Example | No new mail |
|---|---|
| Given | no new messages |
| When | the owner runs a pull |
| Then | nothing is stored |

#### How we'll check

Test.

### 2. Report the count

When a pull ends, the system SHALL print how many messages it fetched.

| Example | Count |
|---|---|
| Given | two new messages |
| When | the owner runs a pull |
| Then | it prints 2 |

#### How we'll check

Test.

## Open questions

- None.
"""


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = os.path.join(self.tmp.name, "repo")
        self.data = os.path.join(self.tmp.name, "data")
        os.makedirs(self.repo)
        self.git("init", "-q", "-b", "main")
        self.put("docs/specs/mail-pull.spec.md", SPEC.format(status="👍 Accepted"))
        self.put("docs/specs/send.spec.md", SPEC.format(status="📝 Draft"))
        self.put("src/app.py", "print('hi')\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, *args], env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def run_script(self, *argv, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = verify.main(list(argv))
        finally:
            sys.stdin = old
        return code, out.getvalue(), err.getvalue()

    def start(self, *specs):
        return self.run_script("start", *specs, "--project", self.repo, "--data", self.data, "--session", "s1")

    def report(self, own, scope="mail-pull", commit=None):
        commit = commit or self.git("rev-parse", "HEAD")
        return self.run_script("report", "--scope", scope, "--commit", commit, "--project", self.repo, "--data", self.data,
                               "--session", "s1", "--now", "2026-11-16T10:00:00+00:00", stdin=own)


class Start(Repo):
    def test_notes_the_commit(self):
        code, out, _ = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["commit"], self.git("rev-parse", "HEAD"))
        self.assertEqual(result["root"], os.path.realpath(self.repo))

    def test_lists_requirements_with_their_examples(self):
        _, out, _ = self.start("docs/specs/mail-pull.spec.md")
        spec = json.loads(out)["specs"][0]
        self.assertEqual(spec["path"], "docs/specs/mail-pull.spec.md")
        self.assertTrue(spec["accepted"])
        self.assertEqual(spec["requirements"], [{"number": 1, "name": "Pull new mail", "examples": 2},
                                                {"number": 2, "name": "Report the count", "examples": 1}])

    def test_spec_not_accepted_is_listed_with_its_status(self):
        _, out, _ = self.start("docs/specs/send.spec.md")
        spec = json.loads(out)["specs"][0]
        self.assertFalse(spec["accepted"])
        self.assertEqual(spec["status"], "📝 Draft")

    def test_every_spec_when_none_named(self):
        _, out, _ = self.start()
        self.assertEqual([s["path"] for s in json.loads(out)["specs"]],
                         ["docs/specs/mail-pull.spec.md", "docs/specs/send.spec.md"])

    def test_full_path_is_read_relative_to_the_repository(self):
        _, out, _ = self.start(os.path.join(self.repo, "docs/specs/mail-pull.spec.md"))
        self.assertEqual(json.loads(out)["specs"][0]["path"], "docs/specs/mail-pull.spec.md")

    def test_missing_spec_refused(self):
        code, out, err = self.start("docs/specs/nope.spec.md")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("docs/specs/nope.spec.md", err)

    def test_a_file_that_is_not_a_spec_refused(self):
        code, _, err = self.start("src/app.py")
        self.assertEqual(code, 1)
        self.assertIn("not a spec", err)

    def test_uncommitted_changes_refused(self):
        self.put("src/app.py", "print('changed')\n")
        code, out, err = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("src/app.py", err)

    def test_untracked_file_refused(self):
        self.put("notes.txt", "x\n")
        code, _, err = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(code, 1)
        self.assertIn("notes.txt", err)

    def test_not_a_repository_refused(self):
        code, _, err = self.run_script("start", "--project", self.tmp.name, "--data", self.data, "--session", "s1")
        self.assertEqual(code, 1)
        self.assertIn("git", err)

    def test_clears_an_earlier_runs_reports(self):
        path = verify_relay.record_path(self.data, "s1")
        os.makedirs(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"reports": {"verifier|x|": {"agent": "verifier", "document": "x", "kind": "", "text": "old"}}}, f)
        self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(verify_relay.reports(self.data, "s1"), [])


class Report(Repo):
    def keep(self, agent, document, text):
        path = verify_relay.record_path(self.data, "s1")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record = verify_relay.load(path)
        record["reports"][f"{agent}|{document}|"] = {"agent": agent, "document": document, "kind": "", "text": text}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f)

    def written(self, out):
        path = out.splitlines()[0][len("Report written: "):]
        with open(path, encoding="utf-8") as f:
            return path, f.read()

    def test_report_holds_every_heading_in_order(self):
        self.start("docs/specs/mail-pull.spec.md")
        code, out, err = self.report("## Overall result\n\nAll passed.\n")
        self.assertEqual(code, 0, err)
        path, text = self.written(out)
        self.assertTrue(path.endswith("2026-11-16-verify-mail-pull.md"))
        positions = [text.index(f"## {h}\n") for h in verify.run_report.HEADINGS["verify"]]
        self.assertEqual(positions, sorted(positions))

    def test_commit_checked_is_the_one_start_printed(self):
        _, started, _ = self.start("docs/specs/mail-pull.spec.md")
        commit = json.loads(started)["commit"]
        _, out, _ = self.report("## Overall result\n\nAll passed.\n", commit=commit[:8])
        _, text = self.written(out)
        section = text.split("## Commit checked\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn(commit, section)

    def test_each_agents_report_copied_word_for_word(self):
        self.start("docs/specs/mail-pull.spec.md")
        verifier = "Document: docs/specs/mail-pull.spec.md\n\n1.1 pass\n  Evidence: `pull` printed \"2\"\n"
        checker = "Document: docs/specs/mail-pull.spec.md\n\n- 1.1: confirmed\n"
        self.keep("verify-checker", os.path.join(self.repo, "docs/specs/mail-pull.spec.md"), checker)
        self.keep("verifier", os.path.join(self.repo, "docs/specs/mail-pull.spec.md"), verifier)
        _, out, _ = self.report("## Overall result\n\nAll passed.\n")
        _, text = self.written(out)
        agents = text.split("## What each agent reported\n", 1)[1].split("\n## The repository", 1)[0]
        self.assertIn(verifier, agents)
        self.assertIn(checker, agents)
        self.assertLess(agents.index("### Verifier: docs/specs/mail-pull.spec.md"),
                        agents.index("### Verify-checker: docs/specs/mail-pull.spec.md"))

    def test_clean_repository_said(self):
        self.start("docs/specs/mail-pull.spec.md")
        _, out, _ = self.report("## Overall result\n\nAll passed.\n")
        _, text = self.written(out)
        after = text.split("## The repository after the run\n", 1)[1]
        self.assertIn("No file in the repository changed during the run.", after)
        self.assertIn("still checked out", after)

    def test_file_changed_during_the_run_listed(self):
        self.start("docs/specs/mail-pull.spec.md")
        self.put("src/app.py", "print('touched')\n")
        self.put("tool.sh", "echo\n")
        _, out, _ = self.report("## Overall result\n\nAll passed.\n")
        _, text = self.written(out)
        after = text.split("## The repository after the run\n", 1)[1]
        self.assertIn("src/app.py", after)
        self.assertIn("tool.sh", after)

    def test_new_commit_during_the_run_said(self):
        _, started, _ = self.start("docs/specs/mail-pull.spec.md")
        self.put("src/app.py", "print('new')\n")
        self.commit()
        _, out, _ = self.report("## Overall result\n\nAll passed.\n", commit=json.loads(started)["commit"])
        _, text = self.written(out)
        after = text.split("## The repository after the run\n", 1)[1]
        self.assertIn(self.git("rev-parse", "HEAD"), after)
        self.assertNotIn("still checked out", after)

    def test_claude_cannot_write_the_scripts_sections(self):
        self.start("docs/specs/mail-pull.spec.md")
        code, out, err = self.report("## Commit checked\n\nabc\n")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("filled by the script", err)

    def test_unknown_commit_refused(self):
        code, out, err = self.report("## Overall result\n\nAll passed.\n", commit="deadbeef")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("deadbeef", err)

    def test_report_clears_kept_reports(self):
        self.start("docs/specs/mail-pull.spec.md")
        self.keep("verifier", "docs/specs/mail-pull.spec.md", "x")
        self.report("## Overall result\n\nAll passed.\n")
        self.assertEqual(verify_relay.reports(self.data, "s1"), [])


class Help(unittest.TestCase):
    def test_help_names_both_commands(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit):
            verify.main(["--help"])
        self.assertIn("start", out.getvalue())
        self.assertIn("report", out.getvalue())


if __name__ == "__main__":
    unittest.main()

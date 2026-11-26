"""Tests for hand_over.py, run against throwaway git repositories made in each test."""

import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hand_over  # noqa: E402
import run_report  # noqa: E402
import build_relay  # noqa: E402
import uncommitted  # noqa: E402

PLAN = "docs/plans/2026-11-03-thing.md"
TODAY = "2026-11-10"  # the script's "today" in these tests; never read from the clock
NOTE = "You can now do the thing."

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def plan(status="Ready to build 🟢", date="2026-11-04"):
    dated = f"date: {date}\n" if date else ""
    return f"---\nstatus: {status}\n{dated}---\n\n# Thing\n\n## Plan\n\nDo the thing.\n"


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.dir)
        os.makedirs(os.path.join(self.tmp.name, "s1", "scratchpad"))
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
        today = mock.patch.object(hand_over, "today", return_value=TODAY)
        today.start()
        self.addCleanup(today.stop)

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

    def run_it(self, *args, own="", notes=(NOTE,)):
        out = io.StringIO()
        self.data = os.path.join(self.tmp.name, "s1", "scratchpad", "agentic")
        with redirect_stdout(out), mock.patch("sys.stdin", io.StringIO(own)):
            code = hand_over.main(["--repo", self.dir, "--plan", PLAN, "--message", "Build the thing",
                                   "--scratchpad", os.path.dirname(self.data), "--session", "s1", "--report", "-",
                                   *(() if notes is None else [x for n in notes for x in ("--release-note", n)]),
                                   *args])
        return code, out.getvalue()

    def report_file(self, out):
        line = next(line for line in out.splitlines() if line.startswith("Report written: "))
        with open(line[len("Report written: "):], encoding="utf-8") as f:
            return line[len("Report written: "):], f.read()

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
        self.assertEqual(self.subjects()[1:], ["Start"])
        self.assertIn("nothing new to commit", out)

    def test_sandbox_stand_ins_left_out_of_the_commit(self):
        # Git can't add the sandbox's stand-ins, and one failing file stops `git add -A` adding
        # anything. Ordinary files stand in for them here, as in test_uncommitted.py.
        self.put(".bashrc", "")
        self.put(".claude/settings.json", "")
        self.put("src/thing.py", "print('thing')\n")
        stand_ins = {os.path.join(self.dir, ".bashrc"), os.path.join(self.dir, ".claude/settings.json")}
        null = os.stat(os.devnull)
        fake = type("Stat", (), {"st_mode": stat.S_IFCHR | 0o666, "st_rdev": null.st_rdev})
        real = uncommitted.lstat_of
        with mock.patch.object(uncommitted, "lstat_of", lambda p: fake if p in stand_ins else real(p)):
            code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertEqual(self.subjects()[0], "Build the thing")
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD"), "src/thing.py")

    def test_failed_add_reported(self):
        self.put("src/thing.py", "print('thing')\n")
        failing = subprocess.CompletedProcess([], 128, "", "fatal: adding files failed")
        real = hand_over.git
        with mock.patch.object(hand_over, "git", lambda repo, *a: failing if a[0] == "add" else real(repo, *a)):
            code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertEqual(self.subjects(), ["Start"])
        self.assertIn("fatal: adding files failed", out)

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
        self.assertIn("status: Built ✅\n", self.read(PLAN))
        self.assertEqual(self.subjects()[:2], ["Mark the plan 2026-11-03-thing.md as built", "Build the thing"])
        self.assertIn("Built ✅", out)

    def test_plan_left_ready_without_passing_reviews(self):
        code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertIn("status: Ready to build 🟢\n", self.read(PLAN))
        self.assertIn("Ready to build 🟢", out)

    def test_draft_plan_without_passing_reviews_says_it_is_not_ready(self):
        self.put(PLAN, plan("Draft 📝"))
        code, out = self.run_it()
        self.assertEqual(code, 0)
        self.assertIn("status: Draft 📝\n", self.read(PLAN))
        self.assertIn("stays `Draft 📝`, because it is not `Ready to build 🟢`", out)
        self.assertNotIn("reviews have not all passed", out)

    def test_only_a_ready_plan_is_marked_built(self):
        self.put(PLAN, plan("Draft 📝"))
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 1)
        self.assertIn("status: Draft 📝\n", self.read(PLAN))
        self.assertIn("Draft 📝", out)

    def test_ready_written_before_the_emoji_counts(self):
        self.put(PLAN, plan("Ready to build"))
        code, _ = self.run_it("--reviews-passed")
        self.assertEqual(code, 0)
        self.assertIn("status: Built ✅\n", self.read(PLAN))

    def test_ready_written_with_the_emoji_first_counts(self):
        for old in ("🟢 Ready to build", "🟢\ufe0f Ready to build"):
            self.put(PLAN, plan(old))
            code, _ = self.run_it("--reviews-passed")
            self.assertEqual(code, 0, old)
            self.assertIn("status: Built ✅\n", self.read(PLAN))

    def test_only_the_status_and_date_lines_change(self):
        before = self.read(PLAN)
        self.run_it("--reviews-passed")
        self.assertEqual(self.read(PLAN), before.replace("Ready to build 🟢", "Built ✅").replace(
            "date: 2026-11-04", f"date: {TODAY}"))

    def test_built_plan_dated_today(self):
        self.run_it("--reviews-passed")
        self.assertIn(f"status: Built ✅\ndate: {TODAY}\n", self.read(PLAN))

    def test_plan_from_before_dates_gains_todays_date_under_its_status(self):
        self.put(PLAN, plan(date=None))
        code, _ = self.run_it("--reviews-passed")
        self.assertEqual(code, 0)
        self.assertEqual(self.read(PLAN), plan("Built ✅", date=TODAY))

    def test_date_with_a_comment_keeps_it(self):
        self.put(PLAN, plan(date="2026-11-04  # status day"))
        self.run_it("--reviews-passed")
        self.assertIn(f"date: {TODAY}  # status day\n", self.read(PLAN))

    def built_from(self, line):
        self.put(PLAN, plan(date=None).replace("---\n\n#", f"{line}\n---\n\n#"))
        self.run_it("--reviews-passed")
        return self.read(PLAN)

    def test_date_key_in_another_case_replaced_not_doubled(self):
        text = self.built_from("Date: 2026-11-04")
        self.assertIn(f"Date: {TODAY}\n", text)
        self.assertEqual(text.lower().count("date"), 1)

    def test_date_key_with_a_space_replaced_not_doubled(self):
        text = self.built_from("date : 2026-11-04")
        self.assertIn(f"date : {TODAY}\n", text)
        self.assertEqual(text.lower().count("date"), 1)

    def test_date_left_alone_when_not_built(self):
        self.run_it()
        self.assertIn("date: 2026-11-04\n", self.read(PLAN))

    def test_date_outside_the_frontmatter_left_alone(self):
        self.put(PLAN, plan(date=None) + "\ndate: 2026-01-01\n")
        self.run_it("--reviews-passed")
        text = self.read(PLAN)
        self.assertIn(f"status: Built ✅\ndate: {TODAY}\n", text)
        self.assertTrue(text.endswith("\ndate: 2026-01-01\n"))

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
        self.assertIn("status: Ready to build 🟢\n", self.read(PLAN))
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


class Report(Repo):
    """The build's report file (ADRs 0051 and 0034)."""

    def keep(self, plan_path, reports):
        record = {"commit": "abc", "repository": self.dir, "plan": plan_path, "reports": reports, "started": {}}
        path = build_relay.record_path("s1", os.path.join(self.tmp.name, "s1", "scratchpad", "agentic"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f)

    def test_own_sections_and_script_output_written(self):
        code, out = self.run_it(own="## What was built\n\nThe thing.\n\n## Choices\n\n- Named it thing.\n")
        self.assertEqual(code, 0, out)
        path, text = self.report_file(out)
        self.assertTrue(path.endswith(f"reports/repo/{TODAY}-build-2026-11-03-thing.md"), path)
        self.assertIn("## What was built\n\nThe thing.", text)
        script = text[text.index("## The hand-over script's report"):text.index("## Left for you to check")]
        self.assertIn("Branch: build/thing", script)
        self.assertIn("Push: pushed build/thing to origin.", script)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_kept_reviews_copied_word_for_word(self):
        reports = {"code": '[{"summary": "x"}]', "security": "No issues.\n", "plan": "Result: PASS\n| 1 | pass |",
                   "check": "Result: PASS"}
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), reports)
        _, out = self.run_it()
        _, text = self.report_file(out)
        reviews = text[text.index("## What each review found"):text.index("## The hand-over script's report")]
        for title, part in (("Code review", "code"), ("Security review", "security"),
                            ("Build review", "plan"), ("Correction check", "check")):
            self.assertIn(f"### {title}\n\n{reports[part]}", reviews)

    def test_another_plans_reviews_not_copied(self):
        self.keep(os.path.realpath(os.path.join(self.dir, "docs/plans/other.md")), {"code": "theirs"})
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertNotIn("theirs", text)
        self.assertIn("No report kept.", text)

    def test_kept_reviews_stay_while_their_check_leaves_findings_open(self):
        # A check after the person's answers needs them again (docs/adrs/0060).
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), {"code": "earlier round", "check": "Result: FAIL"})
        self.run_it()
        self.put("src/more.py", "print('more')\n")
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertIn("earlier round", text)

    def test_kept_reviews_without_a_check_cleared_once_copied(self):
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), {"code": "earlier round"})
        self.run_it()
        self.put("src/more.py", "print('more')\n")
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertNotIn("earlier round", text)

    def test_kept_reviews_of_a_build_before_sign_off_cleared_once_copied(self):
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), {"code": "earlier round", "check": "Result: FAIL"})
        self.run_it(own="## What was built\n\nThe thing.\n\n## Built before sign-off\n\nThe plan is Draft.\n")
        self.put("src/more.py", "print('more')\n")
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertNotIn("earlier round", text)

    def test_kept_reviews_cleared_once_the_plan_is_built(self):
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), {"code": "earlier round"})
        self.run_it("--reviews-passed")
        self.put("src/more.py", "print('more')\n")
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertNotIn("earlier round", text)

    def test_missing_check_says_no_report_kept(self):
        self.keep(os.path.realpath(os.path.join(self.dir, PLAN)), {"code": "c", "security": "s", "plan": "p"})
        _, out = self.run_it()
        _, text = self.report_file(out)
        self.assertIn("### Correction check\n\nNo report kept.", text)

    def test_refused_hand_over_still_writes_the_file(self):
        self.git("checkout", "-q", "main")
        code, out = self.run_it(own="## What was built\n\nNothing: refused.\n")
        self.assertEqual(code, 2)
        _, text = self.report_file(out)
        self.assertIn("Refused:", text)

    def test_unknown_heading_refused_before_any_git_step(self):
        self.put("work.txt", "new")
        code, out = self.run_it(own="## My own heading\n\ntext\n")
        self.assertEqual(code, 2)
        self.assertIn("My own heading", out)
        self.assertNotIn("Report written", out)
        self.assertIn("work.txt", self.git("status", "--porcelain"))

    def test_claude_cannot_write_the_script_report(self):
        code, out = self.run_it(own="## The hand-over script's report\n\nAll pushed.\n")
        self.assertEqual(code, 2)


CHECK = """Result: FAIL

Corrections:
- "Date format": left for the person, the code uses ISO dates
- "Empty input file": not made, it still writes an empty report
- "Test order": made, the test now comes first

Broken by a correction:
- None.

Suggestions:
- Tidy the names.
"""
FINDINGS = ['- "Date format": left for the person, the code uses ISO dates',
            '- "Empty input file": not made, it still writes an empty report']
OUTSIDE = '- "Page count off by one" in src/parser.ts:88: medium'
PASSED_OUTSIDE = f"""Result: PASS

Corrections:
- "Test order": made

Broken by a correction:
- None.

Outside this build:
{OUTSIDE}

Suggestions:
- None.
"""


class OpenFindings(Repo):
    """Accepting a build as it stands after its correction check failed (docs/adrs/0038)."""

    def setUp(self):
        super().setUp()
        self.data = os.path.join(self.tmp.name, "s1", "scratchpad", "agentic")
        self.put("src/thing.py", "print('thing')\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Build the thing")

    def failed_report(self, check=CHECK, head=None, own=None, date="2026-11-09", plan_path=PLAN):
        head = head or self.git("rev-parse", "HEAD")
        output = f"Branch: build/thing\nPlan: {plan_path} stays `Ready to build 🟢`, because the reviews " \
                 f"have not all passed.\nPush: pushed build/thing to origin.\nHead: {head}"
        copied = {"What each review found": [("Code review", "[]"), ("Build review", "Result: FAIL"),
                                             ("Correction check", check)],
                  "The hand-over script's report": [("Output", output)]}
        return run_report.write("build", "2026-11-03-thing", self.dir, self.data, own or {}, copied, date=date)[0]

    def run_open(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = hand_over.main(["--repo", self.dir, "--plan", PLAN, "--scratchpad", os.path.dirname(self.data),
                                   "--session", "s1", "--open-findings"])
        return code, out.getvalue()

    def run_accept(self, own="## What was built\n\nAccepted as it stands.\n", *extra):
        out = io.StringIO()
        with redirect_stdout(out), mock.patch("sys.stdin", io.StringIO(own)):
            code = hand_over.main(["--repo", self.dir, "--plan", PLAN, "--scratchpad", os.path.dirname(self.data), "--session", "s1",
                                   "--report", "-", "--accept-open-findings", "--release-note", NOTE, *extra])
        return code, out.getvalue()

    def reports(self):
        return run_report.reports("build", "2026-11-03-thing", self.dir, self.data)

    def test_report_in_another_sessions_scratchpad_is_not_found(self):
        other = os.path.join(self.tmp.name, "s0", "scratchpad", "agentic")
        run_report.write("build", "2026-11-03-thing", self.dir, other, {}, {
            "What each review found": [("Correction check", CHECK)]}, date="2026-11-09")
        code, out = self.run_open()
        self.assertEqual(code, 3)
        self.assertIn("No build report for this plan was found in this session", out)

    def test_mistyped_scratchpad_refused_before_anything_changes(self):
        self.failed_report()
        before = self.git("rev-parse", "HEAD")
        out = io.StringIO()
        with redirect_stdout(out), mock.patch("sys.stdin", io.StringIO("")):
            code = hand_over.main(["--repo", self.dir, "--plan", PLAN, "--session", "s1", "--report", "-",
                                   "--scratchpad", os.path.join(self.tmp.name, "s1-scratchpad"),
                                   "--accept-open-findings", "--release-note", NOTE])
        self.assertEqual(code, 2)
        self.assertIn("does not exist", out.getvalue())
        self.assertEqual(self.git("rev-parse", "HEAD"), before)

    def assert_refused(self, reason):
        before = (self.subjects(), self.read(PLAN), self.reports())
        code, out = self.run_open()
        self.assertEqual(code, 3, out)
        self.assertIn(reason, out)
        code, out = self.run_accept()
        self.assertEqual(code, 2, out)
        self.assertIn(reason, out)
        self.assertIn("Nothing was changed", out)
        self.assertEqual((self.subjects(), self.read(PLAN), self.reports()), before)

    def test_open_findings_listed_with_the_report(self):
        path = self.failed_report()
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        for finding in FINDINGS:
            self.assertIn(finding, out)
        self.assertNotIn("Test order", out)
        self.assertIn(path, out)
        self.assertEqual(self.reports(), [path])
        self.assertEqual(self.subjects()[0], "Build the thing")

    def test_broken_by_a_correction_listed(self):
        self.failed_report(check=CHECK.replace("- None.", "- src/thing.py:1: prints twice"))
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        self.assertIn("- src/thing.py:1: prints twice", out)

    def test_accept_marks_built_and_lists_findings_in_the_commit(self):
        self.failed_report()
        code, out = self.run_accept()
        self.assertEqual(code, 0, out)
        self.assertIn("status: Built ✅", self.read(PLAN))
        self.assertIn(f"date: {TODAY}", self.read(PLAN))
        message = self.git("log", "-1", "--format=%B")
        self.assertTrue(message.startswith("Mark the plan 2026-11-03-thing.md as built\n\n"), message)
        self.assertIn("Left open by the person, without further review:\n\n" + "\n".join(FINDINGS),
                      message)
        self.assertIn("The person's answers:\n\nAccepted as it stands.", message)
        self.assertTrue(message.rstrip().endswith(f"\n\nRelease-note: {NOTE}"), message)
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD"), PLAN)
        self.assertEqual(self.git("rev-parse", "HEAD"),
                         self.git("rev-parse", "build/thing", cwd=self.bare))
        path, text = self.report_file(out)
        self.assertEqual(self.reports()[0], path)
        self.assertIn("Accepted as it stands.", text)
        self.assertIn("### Correction check\n\nNo review: the person accepted the build as it stands.", text)
        self.assertIn(FINDINGS[0], run_report.section("build", text, "The hand-over script's report"))

    def test_newest_report_counts(self):
        self.failed_report(date="2026-11-08")
        self.failed_report(check="Result: PASS\n")
        self.assert_refused("passed with nothing left open")

    def test_no_report(self):
        self.assert_refused("No build report")

    def test_check_passed(self):
        self.failed_report(check="Result: PASS\n\nCorrections:\n- a: made\n")
        self.assert_refused("passed with nothing left open")

    def test_no_check_kept(self):
        self.failed_report(check="No report kept.")
        self.assert_refused("has no correction check")

    def test_outside_findings_listed_apart(self):
        # docs/adrs/0061: findings in code the build did not change are shown apart.
        self.failed_report(check=CHECK.replace("Suggestions:", f"Outside this build:\n{OUTSIDE}\n\nSuggestions:"))
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        own, outside = out.split("Outside this build:\n")
        for finding in FINDINGS:
            self.assertIn(finding, own)
        self.assertEqual(outside.strip(), OUTSIDE)

    def test_a_passed_check_with_outside_findings_can_be_accepted(self):
        self.failed_report(check=PASSED_OUTSIDE)
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        self.assertIn(OUTSIDE, out)
        code, out = self.run_accept("## What was built\n\nCarried on past the older finding.\n")
        self.assertEqual(code, 0, out)
        self.assertIn("status: Built ✅", self.read(PLAN))
        message = self.git("log", "-1", "--format=%B")
        self.assertIn(f"Outside this build, left open:\n\n{OUTSIDE}", message)
        self.assertNotIn("Left open by the person", message)

    def test_a_later_failed_check_can_be_accepted(self):
        # The person's fixes and a check of only what changed, then a hand-over at the new commit.
        self.failed_report(date="2026-11-08")
        self.put("src/more.py", "print('more')\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Drop the test the person chose to drop")
        self.failed_report(check=CHECK.replace("not made, it still", "not made again, it still"))
        code, out = self.run_accept()
        self.assertEqual(code, 0, out)
        self.assertIn("not made again", self.git("log", "-1", "--format=%B"))

    def test_branch_changed_since(self):
        self.failed_report()
        self.put("src/more.py", "print('more')\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "More")
        self.assert_refused("changed since")

    def test_uncommitted_work(self):
        self.failed_report()
        self.put("src/more.py", "print('more')\n")
        self.assert_refused("uncommitted")

    def test_built_before_sign_off(self):
        self.failed_report(own={"Built before sign-off": "The plan was Draft."})
        self.assert_refused("before sign-off")

    def test_plan_not_ready(self):
        self.failed_report()
        self.put(PLAN, plan(status="Draft 📝"))
        self.git("commit", "-qam", "Draft again")
        self.failed_report(date="2026-11-10")
        self.assert_refused("not `Ready to build 🟢`")

    def test_nothing_listed(self):
        self.failed_report(check="Result: FAIL\n\nCorrections:\n- a: made\n\nBroken by a correction:\n- None.\n")
        self.assert_refused("lists no open finding")

    def test_report_of_another_plan(self):
        self.failed_report(plan_path="docs/plans/other.md")
        self.assert_refused("No build report")

    def test_report_of_a_plan_whose_name_ends_in_a_number_passed_over(self):
        mine = self.failed_report(date="2026-11-08")
        other = run_report.write("build", "2026-11-03-thing-2", self.dir, self.data, {},
                                 {"The hand-over script's report": [("Output", "Plan: docs/plans/2026-11-03-thing-2.md stays")]},
                                 date="2026-11-09")[0]
        self.assertIn(other, self.reports())
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        self.assertIn(mine, out)

    def test_other_list_styles_and_wrapped_items(self):
        check = ("Result: FAIL\n\nCorrections:\n* \"A\": not made, it still\nraises a traceback\n"
                 "1. \"B\" — Not made\n- \"C\": made\n+ \"D\": left for the person\n\n"
                 "**Broken by a correction:**\n- src/a.py:1: broken\n\nSuggestions:\n- \"E\": not made\n")
        self.failed_report(check=check)
        code, out = self.run_open()
        self.assertEqual(code, 0, out)
        listed = out.split("\n", 1)[1]
        self.assertEqual(listed.strip().splitlines(),
                         ['* "A": not made, it still', "raises a traceback", '1. "B" — Not made',
                          '+ "D": left for the person', "- src/a.py:1: broken"])

    def test_failed_commit_leaves_the_plan_ready_and_pushes_nothing(self):
        self.failed_report()
        with mock.patch.object(hand_over, "commit", return_value=False):
            code, out = self.run_accept()
        self.assertEqual(code, 1, out)
        self.assertIn("status: Ready to build 🟢", self.read(PLAN))
        self.assertNotIn("Push:", out)
        self.assertEqual(len(self.reports()), 1)

    def test_not_with_reviews_passed(self):
        self.failed_report()
        with mock.patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit) as raised:
            self.run_accept("", "--reviews-passed")
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("status: Ready to build 🟢", self.read(PLAN))


class ReleaseNotes(Repo):
    """Each hand-over leaves its release notes in the message of the last commit it makes
    (docs/adrs/0043)."""

    def message(self, rev="HEAD"):
        return self.git("log", "-1", "--format=%B", rev)

    def test_work_commit_carries_the_note_when_the_reviews_have_not_passed(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.message(), f"Build the thing\n\nRelease-note: {NOTE}")

    def test_built_commit_carries_the_note_and_the_work_commit_does_not(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.message(), f"Mark the plan 2026-11-03-thing.md as built\n\nRelease-note: {NOTE}")
        self.assertEqual(self.message("HEAD~1"), "Build the thing")

    def test_one_line_per_note(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it(notes=("You can export.", "Exports are faster."))
        self.assertEqual(code, 0, out)
        self.assertTrue(self.message().endswith("\n\nRelease-note: You can export.\nRelease-note: Exports are faster."))

    def test_note_given_with_its_label_not_labelled_twice(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it(notes=(f"Release-note: {NOTE}",))
        self.assertEqual(code, 0, out)
        self.assertEqual(self.message(), f"Build the thing\n\nRelease-note: {NOTE}")

    def test_nothing_to_commit_records_the_notes_in_a_commit_of_their_own(self):
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.message(), f"Record the release notes of the plan 2026-11-03-thing.md\n\n"
                                         f"Release-note: {NOTE}")
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD"), "")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "build/thing", cwd=self.bare))

    def test_reviews_passed_on_a_plan_not_ready_with_nothing_to_commit_keeps_the_notes(self):
        self.put(PLAN, plan("Draft 📝"))
        self.git("commit", "-qam", "Draft plan")
        code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 1, out)
        self.assertEqual(self.message(), f"Record the release notes of the plan 2026-11-03-thing.md\n\n"
                                         f"Release-note: {NOTE}")

    def test_notes_kept_when_the_built_commit_fails(self):
        self.put("src/thing.py", "print('thing')\n")
        real = hand_over.commit
        calls = []

        def failing_built(repo, message, lines, allow_empty=False):
            calls.append(message)
            if message.startswith("Mark the plan"):
                lines.append("Commit failed: stand-in")
                return False
            return real(repo, message, lines, allow_empty)

        with mock.patch.object(hand_over, "commit", failing_built):
            code, out = self.run_it("--reviews-passed")
        self.assertEqual(code, 1, out)
        self.assertIn(f"Release-note: {NOTE}", self.message())

    def test_same_notes_already_on_the_branch_not_recorded_again(self):
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        first = self.git("rev-parse", "HEAD")
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.git("rev-parse", "HEAD"), first)
        self.assertIn("already on the branch", out)

    def test_missing_note_refused_before_anything_changes(self):
        self.put("src/thing.py", "print('thing')\n")
        with mock.patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit) as raised:
            self.run_it(notes=None)
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(self.subjects(), ["Start"])

    def test_empty_or_several_line_note_refused_before_anything_changes(self):
        self.put("src/thing.py", "print('thing')\n")
        for bad in ("", "   ", "Release-note:", "First line\nsecond line"):
            code, out = self.run_it(notes=(bad,))
            self.assertEqual(code, 2, out)
            self.assertIn("release note", out)
            self.assertIn("Nothing was changed", out)
            self.assertEqual(self.subjects(), ["Start"])


class Head(Repo):
    def test_hand_over_names_the_head_commit(self):
        self.put("src/thing.py", "print('thing')\n")
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        _, text = self.report_file(out)
        self.assertIn(f"Head: {self.git('rev-parse', 'HEAD')}", text)


class Help(unittest.TestCase):
    def test_help(self):
        result = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_over.py"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--reviews-passed", result.stdout)
        self.assertIn("--open-findings", result.stdout)
        self.assertIn("--accept-open-findings", result.stdout)


if __name__ == "__main__":
    unittest.main()

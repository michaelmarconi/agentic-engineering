"""Tests for pr_link_check.py, the hook that refuses pull request descriptions with long links."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pr_link_check  # noqa: E402

BASE = "https://github.com/owner/repo/blob/"
FULL_ID = "0123456789abcdef0123456789abcdef01234567"


def link_of(length):
    """A GitHub file link exactly `length` characters long."""
    stem = BASE + "abc1234/docs/specs/example.spec.md#"
    return stem + "a" * (length - len(stem))


LONG = link_of(151)
LIMIT = link_of(150)


def mcp(body, tool="mcp__github__create_pull_request"):
    return {"tool_name": tool, "tool_input": {"title": "T", "body": body}}


def bash(command, cwd="."):
    return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}


class GitHubTool(unittest.TestCase):
    def test_create_with_a_long_link_is_refused_naming_it_and_its_length(self):
        reason = pr_link_check.problem(mcp("Plan: [plan](%s)" % LONG))
        self.assertIsNotNone(reason)
        self.assertIn(LONG, reason)
        self.assertIn("151", reason)
        self.assertIn("7-character", reason)

    def test_update_with_a_long_link_is_refused(self):
        self.assertIsNotNone(pr_link_check.problem(
            mcp("[x](%s)" % LONG, tool="mcp__github__update_pull_request")))

    def test_any_server_name_is_checked(self):
        self.assertIsNotNone(pr_link_check.problem(
            mcp("[x](%s)" % LONG, tool="mcp__plugin_github_github__create_pull_request")))

    def test_a_link_of_150_characters_passes(self):
        self.assertIsNone(pr_link_check.problem(mcp("[x](%s)" % LIMIT)))

    def test_short_links_pass(self):
        self.assertIsNone(pr_link_check.problem(
            mcp("See [plan](%sabc1234/docs/plans/p.md) and https://example.com." % BASE)))

    def test_a_short_link_with_a_full_commit_id_passes(self):
        self.assertIsNone(pr_link_check.problem(mcp("[a](%s%s/docs/adrs/0001-a.md)" % (BASE, FULL_ID))))

    def test_parentheses_inside_an_address_are_measured(self):
        link = BASE + "abc1234/docs/a(b).md#" + "c" * 130
        reason = pr_link_check.problem(mcp("[x](%s) and (see %s)" % (link, link)))
        self.assertIn("- %s (%d characters)" % (link, len(link)), reason)

    def test_a_bare_long_address_is_refused(self):
        self.assertIsNotNone(pr_link_check.problem(mcp("Plan: %s\n" % LONG)))

    def test_a_long_link_in_a_reference_definition_is_refused(self):
        self.assertIsNotNone(pr_link_check.problem(mcp("See [plan].\n\n[plan]: %s\n" % LONG)))

    def test_every_long_link_is_listed_once(self):
        other = link_of(160).replace("#a", "#b")
        reason = pr_link_check.problem(mcp("[a](%s) [b](%s) [c](%s)" % (LONG, other, LONG)))
        self.assertEqual(reason.count(LONG), 1)
        self.assertIn(other, reason)
        self.assertIn("160", reason)

    def test_an_empty_or_missing_body_passes(self):
        self.assertIsNone(pr_link_check.problem({"tool_name": "mcp__github__create_pull_request",
                                                 "tool_input": {"title": "T"}}))

    def test_other_tools_pass(self):
        self.assertIsNone(pr_link_check.problem(mcp(LONG, tool="mcp__github__add_issue_comment")))
        self.assertIsNone(pr_link_check.problem({"tool_name": "Write",
                                                 "tool_input": {"content": LONG}}))


class GhCommand(unittest.TestCase):
    def test_create_with_a_long_link_in_the_body_is_refused(self):
        self.assertIsNotNone(pr_link_check.problem(
            bash('gh pr create --title T --body "[plan](%s)"' % LONG)))

    def test_edit_with_a_long_link_is_refused(self):
        self.assertIsNotNone(pr_link_check.problem(bash("gh pr edit 3 -b '%s'" % LONG)))

    def test_a_here_document_body_is_read(self):
        command = "gh pr create --title T --body-file - <<'EOF'\n[plan](%s)\nEOF" % LONG
        self.assertIsNotNone(pr_link_check.problem(bash(command)))

    def test_a_body_file_is_read_from_the_working_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "body.md"), "w") as f:
                f.write("[plan](%s)\n" % LONG)
            self.assertIsNotNone(pr_link_check.problem(
                bash("gh pr create -t T --body-file body.md", cwd=folder)))
            self.assertIsNotNone(pr_link_check.problem(
                bash("gh pr create -t T -F body.md", cwd=folder)))
            self.assertIsNotNone(pr_link_check.problem(
                bash("gh pr create -t T --body-file=body.md", cwd=folder)))

    def test_an_unreadable_body_file_passes(self):
        self.assertIsNone(pr_link_check.problem(bash("gh pr create -t T --body-file missing.md")))

    def test_a_gh_run_by_path_is_checked(self):
        self.assertIsNotNone(pr_link_check.problem(bash("./bin/gh pr create -b '%s'" % LONG)))

    def test_a_gh_after_other_commands_is_checked(self):
        self.assertIsNotNone(pr_link_check.problem(
            bash("git push -u origin x && gh pr create -b '%s'" % LONG)))

    def test_short_links_pass(self):
        self.assertIsNone(pr_link_check.problem(
            bash('gh pr create --title T --body "[plan](%sabc1234/p.md)"' % BASE)))

    def test_a_gh_on_a_later_line_is_checked(self):
        self.assertIsNotNone(pr_link_check.problem(
            bash("git push -u origin x\ngh pr create -b '%s'" % LONG)))

    def test_a_gh_after_variable_settings_or_env_is_checked(self):
        self.assertIsNotNone(pr_link_check.problem(bash("GH_REPO=o/r gh pr create -b '%s'" % LONG)))
        self.assertIsNotNone(pr_link_check.problem(bash("env GH_REPO=o/r gh pr edit 3 -b '%s'" % LONG)))

    def test_other_commands_in_the_chain_are_not_read(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "msg.txt"), "w") as f:
                f.write(LONG)
            self.assertIsNone(pr_link_check.problem(
                bash("git commit -F msg.txt && gh pr create -b short", cwd=folder)))
        self.assertIsNone(pr_link_check.problem(bash("git push %s && gh pr create -b short" % LONG)))

    def test_a_body_file_after_cd_or_named_by_a_variable_is_read(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "sub"))
            with open(os.path.join(folder, "sub", "body.md"), "w") as f:
                f.write("[plan](%s)\n" % LONG)
            self.assertIsNotNone(pr_link_check.problem(
                bash("cd sub && gh pr create -F body.md", cwd=folder)))
            with mock.patch.dict(os.environ, {"BODY_DIR": os.path.join(folder, "sub")}):
                self.assertIsNotNone(pr_link_check.problem(
                    bash('gh pr create -F "$BODY_DIR/body.md"')))

    def test_quoted_text_naming_gh_is_not_a_gh_call(self):
        command = "echo \"done; gh pr create later\" > notes.txt <<'EOF'\ndon't %s\nEOF" % LONG
        self.assertIsNone(pr_link_check.problem(bash(command)))

    def test_a_here_document_with_an_apostrophe_is_read(self):
        command = "gh pr create -t T -F - <<'EOF'\nIt's done: [plan](%s)\nEOF" % LONG
        self.assertIsNotNone(pr_link_check.problem(bash(command)))

    def test_other_commands_pass(self):
        self.assertIsNone(pr_link_check.problem(bash("git commit -m '%s'" % LONG)))
        self.assertIsNone(pr_link_check.problem(bash("gh issue create -b '%s'" % LONG)))
        self.assertIsNone(pr_link_check.problem(bash("gh pr view 3 && echo %s" % LONG[:40])))
        self.assertIsNone(pr_link_check.problem(bash("echo 'gh pr create' > notes.txt; echo %s" % LONG)))


class Main(unittest.TestCase):
    def run_main(self, stdin):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(stdin)), redirect_stdout(out):
            code = pr_link_check.main([])
        return code, out.getvalue()

    def test_a_refusal_is_printed_as_a_deny_decision(self):
        code, out = self.run_main(json.dumps(mcp("[x](%s)" % LONG)))
        self.assertEqual(code, 0)
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn(LONG, decision["permissionDecisionReason"])

    def test_a_passing_request_prints_nothing(self):
        self.assertEqual(self.run_main(json.dumps(mcp("short"))), (0, ""))

    def test_a_malformed_event_prints_nothing(self):
        self.assertEqual(self.run_main("not json"), (0, ""))
        self.assertEqual(self.run_main("[1, 2]"), (0, ""))
        self.assertEqual(self.run_main(json.dumps({"tool_name": "Bash", "tool_input": "x"})), (0, ""))


class Registered(unittest.TestCase):
    def test_hooks_json_runs_the_check_before_bash_and_pull_request_tools(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "hooks", "hooks.json")) as f:
            entries = json.load(f)["hooks"]["PreToolUse"]
        matchers = [e["matcher"] for e in entries
                    if any("pr_link_check.py" in h["command"] for h in e["hooks"])]
        self.assertEqual(matchers, ["Bash|mcp__.*__(create|update)_pull_request"])


class Templates(unittest.TestCase):
    def test_both_templates_say_to_use_the_short_commit_id(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path in (".github/pull_request_template.md",
                     "skills/practices/assets/pull_request_template.md"):
            with open(os.path.join(root, path)) as f:
                self.assertIn(pr_link_check.TEMPLATE_SENTENCE, " ".join(f.read().split()), path)


if __name__ == "__main__":
    unittest.main()

"""Tests for build_relay.py, fed recorded hook inputs, against a throwaway git repository."""

import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_relay  # noqa: E402
import fresh_session  # noqa: E402

PLAN = "docs/plans/2026-11-03-thing.md"
ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class Relay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.repo)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": os.path.join(self.tmp.name, "data"),
                                               "CLAUDE_PROJECT_DIR": self.repo})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.git("init", "-q", "-b", "main")
        self.commit("Start")
        fresh_session.save("s1", {"fresh": True, "messages": 1, "building": True})
        self.calls = 0

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def hook(self, event, session="s1"):
        event = dict(event, session_id=session)
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            self.assertEqual(build_relay.main([]), 0)
        text = out.getvalue().strip()
        return json.loads(text)["hookSpecificOutput"] if text else None

    def agent(self, agent, prompt, report, session="s1"):
        self.calls += 1
        call = f"call{self.calls}"
        tool_input = {"subagent_type": agent, "prompt": prompt}
        before = self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": call,
                            "tool_input": tool_input}, session)
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": call,
                   "tool_input": tool_input, "tool_response": {"content": [{"type": "text", "text": report}]}},
                  session)
        return before

    def plan_review(self, report="Result: FAIL\nplan finding", session="s1"):
        return self.agent("agentic:build-reviewer", f"Document: {PLAN}\nBase: main\nReview this build.", report, session)

    def security_review(self, report="security finding", session="s1"):
        return self.agent("general-purpose", f"Document: {PLAN}\nRun /security-review and report.", report, session)

    def code_review(self, report='[{"summary": "code finding"}]', session="s1"):
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Skill",
                   "tool_input": {"skill": "code-review", "args": "medium main...HEAD"},
                   "tool_response": {"success": True, "result": report}}, session)

    def all_reviews(self, session="s1"):
        self.code_review(session=session)
        self.security_review(session=session)
        self.plan_review(session=session)

    def check(self, session="s1"):
        return self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": "check",
                          "tool_input": {"subagent_type": "agentic:build-correction-checker",
                                         "prompt": f"Document: {PLAN}\nCheck the corrections."}}, session)


class Checker(Relay):
    def test_reports_and_reviewed_commit_attached(self):
        reviewed = self.git("rev-parse", "HEAD")
        self.code_review()
        self.security_review()
        self.plan_review()
        self.commit("Correct the findings")
        result = self.check()
        self.assertEqual(result["permissionDecision"], "allow")
        prompt = result["updatedInput"]["prompt"]
        self.assertIn("code finding", prompt)
        self.assertIn("security finding", prompt)
        self.assertIn("plan finding", prompt)
        self.assertIn(f"Reviewed commit: {reviewed}", prompt)
        self.assertIn("rubric.md", prompt)

    def test_refused_without_the_security_review(self):
        self.code_review()
        self.plan_review()
        self.commit("Correct")
        result = self.check()
        self.assertEqual(result["permissionDecision"], "deny")
        self.assertIn("security review", result["permissionDecisionReason"])
        self.assertIn("show the person", result["permissionDecisionReason"])

    def test_refused_without_the_code_review(self):
        self.security_review()
        self.plan_review()
        self.commit("Correct")
        self.assertIn("code review", self.check()["permissionDecisionReason"])

    def test_refused_without_the_plan_review(self):
        self.code_review()
        self.security_review()
        self.commit("Correct")
        result = self.check()
        self.assertEqual(result["permissionDecision"], "deny")
        self.assertIn("build review", result["permissionDecisionReason"])

    def test_refused_when_nothing_was_committed_since(self):
        self.all_reviews()
        result = self.check()
        self.assertEqual(result["permissionDecision"], "deny")
        self.assertIn("commit", result["permissionDecisionReason"])

    def test_later_reviews_replace_earlier_ones_of_another_commit(self):
        self.plan_review("old plan finding")
        self.commit("More work")
        self.code_review()
        self.security_review()
        self.plan_review("new plan finding")
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("new plan finding", prompt)
        self.assertNotIn("old plan finding", prompt)

    def test_refused_without_document_line(self):
        result = self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent",
                            "tool_input": {"subagent_type": "agentic:build-correction-checker", "prompt": "Check."}})
        self.assertEqual(result["permissionDecision"], "deny")


class Corrections(Relay):
    def test_security_agent_without_a_type_counted(self):
        self.code_review()
        self.agent("", f"Document: {PLAN}\nRun /security-review and report.", "security finding")
        self.plan_review()
        self.commit("Correct")
        self.assertIn("security finding", self.check()["updatedInput"]["prompt"])

    def test_empty_code_review_result_not_kept(self):
        self.code_review(report="")
        self.security_review()
        self.plan_review()
        self.commit("Correct")
        self.assertIn("code review", self.check()["permissionDecisionReason"])

    def test_reports_handed_back_are_attached(self):
        # In a Claude project thread the report comes in handbackReport; content only points to it.
        pointer = "This agent's report was delivered to you as a message (its SubagentHandback call)."
        self.code_review()
        for agent, prompt, report in [
                ("general-purpose", f"Document: {PLAN}\nRun /security-review and report.", "security finding"),
                ("agentic:build-reviewer", f"Document: {PLAN}\nBase: main\nReview this build.", "plan finding")]:
            tool_input = {"subagent_type": agent, "prompt": prompt}
            self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": agent,
                       "tool_input": tool_input})
            self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": agent,
                       "tool_input": tool_input,
                       "tool_response": {"handback": "send", "handbackReport": {"text": report},
                                         "content": [{"type": "text", "text": pointer}]}})
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("security finding", prompt)
        self.assertIn("plan finding", prompt)
        self.assertNotIn("SubagentHandback", prompt)

    def launch(self, agent, prompt, agent_id, session="s1", **extra):
        """Start a review that Claude Code runs in the background: its tool result is a launch notice."""
        self.calls += 1
        call = f"call{self.calls}"
        tool_input = dict({"subagent_type": agent, "prompt": prompt}, **extra)
        before = self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": call,
                            "tool_input": tool_input}, session)
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": call,
                   "tool_input": tool_input,
                   "tool_response": {"isAsync": True, "status": "async_launched", "agentId": agent_id}},
                  session)
        return before, call

    def stopped(self, agent, agent_id, report, session="s1"):
        return self.hook({"hook_event_name": "SubagentStop", "agent_id": agent_id, "agent_type": agent,
                          "stop_hook_active": False, "last_assistant_message": report}, session)

    SECURITY = ("general-purpose", f"Document: {PLAN}\nRun /security-review and report.")
    REVIEW = ("agentic:build-reviewer", f"Document: {PLAN}\nBase: main\nReview this build.")

    def test_reports_of_background_reviews_are_attached(self):
        self.code_review()
        self.assertIsNone(self.launch(*self.SECURITY, "a1")[0])
        self.assertIsNone(self.launch(*self.REVIEW, "a2")[0])
        self.assertIsNone(self.stopped("general-purpose", "a1", "security finding"))
        self.assertIsNone(self.stopped("agentic:build-reviewer", "a2", "plan finding"))
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("=== SECURITY REVIEW REPORT ===\nsecurity finding\n", prompt)
        self.assertIn("=== BUILD REVIEW REPORT ===\nplan finding\n", prompt)

    def test_a_background_report_counts_when_the_agent_stops_before_its_launch_is_seen(self):
        self.code_review()
        calls = []
        for (agent, prompt), agent_id, report in ((self.SECURITY, "a1", "security finding"),
                                                  (self.REVIEW, "a2", "plan finding")):
            self.calls += 1
            call = f"call{self.calls}"
            tool_input = {"subagent_type": agent, "prompt": prompt}
            self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": call,
                       "tool_input": tool_input})
            self.stopped(agent, agent_id, report)
            calls.append((call, tool_input, agent_id))
        for call, tool_input, agent_id in calls:
            self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": call,
                       "tool_input": tool_input,
                       "tool_response": {"status": "async_launched", "agentId": agent_id}})
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("security finding", prompt)
        self.assertIn("plan finding", prompt)

    def test_a_launch_notice_alone_is_no_report(self):
        self.code_review()
        self.launch(*self.SECURITY, "a1")
        self.launch(*self.REVIEW, "a2")
        self.commit("Correct")
        self.assertEqual(self.check()["permissionDecision"], "deny")

    def test_an_agent_the_relay_never_saw_start_changes_nothing(self):
        self.all_reviews()
        self.stopped("agentic:build-reviewer", "a9", "another report")
        self.stopped("general-purpose", "a8", "another report")
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertNotIn("another report", prompt)
        self.assertIn("plan finding", prompt)

    def test_a_stop_outside_a_build_saves_nothing(self):
        fresh_session.save("s2", {"fresh": True, "messages": 1})
        self.stopped("agentic:build-reviewer", "a1", "plan finding", session="s2")
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "data", "builds", "s2.json")))

    def test_an_agent_that_stops_again_has_its_last_report_kept(self):
        self.code_review()
        self.launch(*self.SECURITY, "a1")
        self.launch(*self.REVIEW, "a2")
        self.stopped("general-purpose", "a1", "an early line")
        self.stopped("general-purpose", "a1", "security finding")
        self.stopped("agentic:build-reviewer", "a2", "plan finding")
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("security finding", prompt)
        self.assertNotIn("an early line", prompt)

    # In auto mode an agent ends by calling SubagentHandback: its SubagentStop then has no last
    # message, and the hand-back may not be in its transcript yet.

    def hand_back(self, agent, agent_id, report, session="s1"):
        return self.hook({"hook_event_name": "PostToolUse", "agent_id": agent_id, "agent_type": agent,
                          "tool_name": "SubagentHandback", "tool_use_id": f"handback-{agent_id}",
                          "tool_input": {"message": report},
                          "tool_response": {"success": True, "message": "Report delivered to your caller."}},
                         session)

    def stopped_after_hand_back(self, agent, agent_id, session="s1"):
        return self.hook({"hook_event_name": "SubagentStop", "agent_id": agent_id, "agent_type": agent,
                          "stop_hook_active": False,
                          "agent_transcript_path": os.path.join(self.tmp.name, "not-yet.jsonl")}, session)

    def test_reports_handed_back_by_background_reviews_are_attached(self):
        self.code_review()
        self.launch(*self.SECURITY, "a1")
        self.launch(*self.REVIEW, "a2")
        for agent, agent_id, report in (("general-purpose", "a1", "security finding"),
                                        ("agentic:build-reviewer", "a2", "plan finding")):
            self.assertIsNone(self.hand_back(agent, agent_id, report))
            self.assertIsNone(self.stopped_after_hand_back(agent, agent_id))
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("=== SECURITY REVIEW REPORT ===\nsecurity finding\n", prompt)
        self.assertIn("=== BUILD REVIEW REPORT ===\nplan finding\n", prompt)

    def test_a_line_left_after_a_hand_back_does_not_replace_the_report(self):
        self.code_review()
        self.launch(*self.SECURITY, "a1")
        self.launch(*self.REVIEW, "a2")
        self.hand_back("general-purpose", "a1", "security finding")
        self.stopped("general-purpose", "a1", "Handing back my report.")
        self.hand_back("agentic:build-reviewer", "a2", "plan finding")
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("security finding", prompt)
        self.assertNotIn("Handing back", prompt)

    def test_a_report_handed_back_before_its_launch_is_seen_counts(self):
        self.code_review()
        calls = []
        for (agent, prompt), agent_id, report in ((self.SECURITY, "a1", "security finding"),
                                                  (self.REVIEW, "a2", "plan finding")):
            self.calls += 1
            call = f"call{self.calls}"
            tool_input = {"subagent_type": agent, "prompt": prompt}
            self.hook({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": call,
                       "tool_input": tool_input})
            self.hand_back(agent, agent_id, report)
            self.stopped(agent, agent_id, "Handing back my report.")
            calls.append((call, tool_input, agent_id))
        for call, tool_input, agent_id in calls:
            self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": call,
                       "tool_input": tool_input,
                       "tool_response": {"status": "async_launched", "agentId": agent_id}})
        self.commit("Correct")
        prompt = self.check()["updatedInput"]["prompt"]
        self.assertIn("security finding", prompt)
        self.assertIn("plan finding", prompt)
        self.assertNotIn("Handing back", prompt)

    def test_agents_no_review_waits_for_are_not_held(self):
        self.all_reviews()
        self.stopped("general-purpose", "a9", "an implementer's summary")
        with open(build_relay.record_path("s1"), encoding="utf-8") as f:
            self.assertNotIn("implementer", f.read())

    def test_review_asked_to_run_in_the_background_is_allowed(self):
        self.code_review()
        self.assertIsNone(self.launch(*self.SECURITY, "a1", run_in_background=True)[0])
        self.assertIsNone(self.launch(*self.REVIEW, "a2", run_in_background=True)[0])
        self.stopped("general-purpose", "a1", "security finding")
        self.stopped("agentic:build-reviewer", "a2", "plan finding")
        self.commit("Correct")
        self.assertEqual(self.check()["permissionDecision"], "allow")

    def test_one_correction_check_only(self):
        self.all_reviews()
        self.commit("Correct")
        self.assertEqual(self.check()["permissionDecision"], "allow")
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": "check",
                   "tool_input": {"subagent_type": "agentic:build-correction-checker",
                                  "prompt": f"Document: {PLAN}\nCheck the corrections."},
                   "tool_response": {"content": [{"type": "text", "text": "Result: FAIL"}]}})
        self.commit("Correct again")
        self.assertEqual(self.check()["permissionDecision"], "deny")


class LeftAlone(Relay):
    def test_reviews_outside_a_build_not_kept(self):
        fresh_session.save("s2", {"fresh": True, "messages": 1})
        self.all_reviews(session="s2")
        self.commit("Correct")
        self.assertEqual(self.check(session="s2")["permissionDecision"], "deny")

    def test_other_agents_left_alone(self):
        self.assertIsNone(self.agent("Explore", "Find the code", "found"))
        self.assertIsNone(self.agent("general-purpose", f"Document: {PLAN}\nDo something else.", "x"))

    def test_reports_survive_the_session_ending_so_a_resumed_build_can_check_them(self):
        # Issue #37: `claude --resume`, or a restarted container, brings the same session back.
        self.all_reviews()
        self.hook({"hook_event_name": "SessionEnd"})
        self.commit("Correct")
        self.assertEqual(self.check()["permissionDecision"], "allow")

    def test_saving_reports_deletes_another_sessions_once_they_are_a_month_old(self):
        fresh_session.save("old", {"fresh": True, "messages": 1, "building": True})
        self.plan_review(session="old")
        builds = os.path.join(self.tmp.name, "data", "builds")
        month = time.time() - 31 * 24 * 60 * 60
        for name in os.listdir(builds):
            os.utime(os.path.join(builds, name), (month, month))
        self.plan_review()
        self.assertEqual(sorted(os.listdir(builds)), ["s1.json", "s1.json.lock"])

    def test_bad_input_ignored(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("nope")), redirect_stdout(out):
            self.assertEqual(build_relay.main([]), 0)
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()

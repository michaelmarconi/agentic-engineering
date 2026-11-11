"""Tests for subagent_report.py, fed SubagentStop inputs and transcripts shaped as Claude Code's."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subagent_report  # noqa: E402


def stop(**fields):
    return dict({"hook_event_name": "SubagentStop", "session_id": "s1", "agent_id": "a1",
                 "agent_type": "agentic:spec-reviewer"}, **fields)


def assistant(*blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def handback(message):
    return {"type": "tool_use", "id": "toolu_1", "name": "SubagentHandback", "input": {"message": message}}


def handed(message="Result: PASS\n", success=True, **fields):
    """The PostToolUse event of an agent's own SubagentHandback call, as Claude Code 2.1.322 sends it."""
    return dict({"hook_event_name": "PostToolUse", "session_id": "s1", "agent_id": "a1",
                 "agent_type": "agentic:spec-reviewer", "tool_name": "SubagentHandback",
                 "tool_use_id": "toolu_9", "tool_input": {"message": message},
                 "tool_response": {"success": success, "message": "Report delivered to your caller."}},
                **fields)


class HandBack(unittest.TestCase):
    def test_the_report_is_the_hand_back_calls_message(self):
        self.assertEqual(subagent_report.handed_back_report(handed()), "Result: PASS\n")
        self.assertEqual(subagent_report.report(handed()), "Result: PASS\n")

    def test_a_hand_back_that_was_not_sent_is_no_report(self):
        self.assertIsNone(subagent_report.handed_back_report(handed(success=False)))

    def test_other_events_are_not_hand_backs(self):
        for event in (stop(last_assistant_message="x"), handed(tool_name="Agent"),
                      handed(hook_event_name="PreToolUse"), handed(agent_id=None), handed(agent_id=""),
                      handed(tool_input={"message": 5}), handed(tool_input="x"), handed(message="  ")):
            with self.subTest(event=event):
                self.assertIsNone(subagent_report.handed_back_report(event))

    def test_an_agent_finishes_on_a_stop_or_a_hand_back(self):
        self.assertTrue(subagent_report.finished(stop()))
        self.assertTrue(subagent_report.finished(handed()))
        self.assertFalse(subagent_report.finished(handed(success=False)))
        self.assertFalse(subagent_report.finished({"hook_event_name": "PostToolUse", "tool_name": "Agent"}))


class Report(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def transcript(self, *entries, raw=None):
        path = os.path.join(self.tmp.name, "agent-a1.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(raw if raw is not None else "".join(json.dumps(e) + "\n" for e in entries))
        return path

    def test_the_report_is_the_agents_last_message(self):
        self.assertEqual(subagent_report.report(stop(last_assistant_message="Result: PASS\n")),
                         "Result: PASS\n")

    def test_a_report_handed_back_is_taken_from_the_transcript(self):
        path = self.transcript(
            assistant({"type": "text", "text": "Reading the spec."}),
            assistant(handback("first hand-back")),
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "toolu_1", "content": "Report delivered."}]}},
            assistant({"type": "thinking", "thinking": "..."}, handback("Result: FAIL\nthe report")))
        self.assertEqual(subagent_report.report(stop(last_assistant_message="",
                                                     agent_transcript_path=path)),
                         "Result: FAIL\nthe report")

    def test_a_hand_back_wins_over_the_last_message(self):
        # In a project thread the agent may write a line before handing its report back.
        path = self.transcript(assistant(handback("the report")))
        self.assertEqual(subagent_report.report(stop(last_assistant_message="Handing back.",
                                                     agent_transcript_path=path)), "the report")

    def test_no_report_when_neither_holds_one(self):
        path = self.transcript(assistant({"type": "text", "text": ""}))
        for event in (stop(), stop(last_assistant_message=""), stop(last_assistant_message=None),
                      stop(last_assistant_message="", agent_transcript_path=path),
                      stop(agent_transcript_path=os.path.join(self.tmp.name, "missing.jsonl")),
                      stop(agent_transcript_path=self.transcript(raw="not json\n{\"type\": 3}\n[]\n")),
                      stop(agent_transcript_path=self.tmp.name), stop(agent_transcript_path=7)):
            with self.subTest(event=event):
                self.assertEqual(subagent_report.report(event), "")

    def test_lines_it_cannot_read_are_skipped(self):
        path = self.transcript(raw="not json\n" + json.dumps(assistant(handback("the report"))) + "\n"
                               + '{"type": "assistant", "message": {"content": "plain"}}\n')
        self.assertEqual(subagent_report.report(stop(agent_transcript_path=path)), "the report")

    def test_a_hand_back_with_no_text_is_skipped(self):
        path = self.transcript(assistant(handback("the report")), assistant(
            {"type": "tool_use", "name": "SubagentHandback", "input": {"message": 5}}))
        self.assertEqual(subagent_report.report(stop(agent_transcript_path=path)), "the report")


if __name__ == "__main__":
    unittest.main()

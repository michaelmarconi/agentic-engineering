"""Tests for verify_relay.py, fed recorded hook inputs."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_relay  # noqa: E402

VERIFIER = ("agentic:verifier", "Document: /r/docs/specs/mail.spec.md\nRepository: /r\nRequirements:\n1. Pull")
CHECKER = ("agentic:verify-checker", "Document: /r/docs/specs/mail.spec.md\nRepository: /r\n"
           "=== VERIFIER REPORT ===\nx\n=== END VERIFIER REPORT ===")
OTHER_SPEC = ("agentic:verifier", "Document: /r/docs/specs/send.spec.md\nRepository: /r\nRequirements:\n2. Send")


class Relay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": self.data})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.calls = 0

    def hook(self, event, session="s1"):
        event = dict(event, session_id=session)
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            self.assertEqual(verify_relay.main([]), 0)
        self.assertEqual(out.getvalue(), "", "the hook never answers")

    def agent(self, kind, report, session="s1", handed_back=False):
        agent, prompt = kind
        self.calls += 1
        response = ({"handback": "send", "handbackReport": {"text": report},
                     "content": [{"type": "text", "text": "delivered as a message"}]}
                    if handed_back else {"content": [{"type": "text", "text": report}]})
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": f"c{self.calls}",
                   "tool_input": {"subagent_type": agent, "prompt": prompt}, "tool_response": response}, session)

    def launch(self, kind, agent_id, session="s1"):
        agent, prompt = kind
        self.calls += 1
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "Agent", "tool_use_id": f"c{self.calls}",
                   "tool_input": {"subagent_type": agent, "prompt": prompt},
                   "tool_response": {"status": "async_launched", "agentId": agent_id}}, session)

    def stopped(self, agent, agent_id, report, session="s1"):
        self.hook({"hook_event_name": "SubagentStop", "agent_id": agent_id, "agent_type": agent,
                   "last_assistant_message": report}, session)

    def hand_back(self, agent, agent_id, report, session="s1"):
        self.hook({"hook_event_name": "PostToolUse", "tool_name": "SubagentHandback", "agent_id": agent_id,
                   "agent_type": agent, "tool_input": {"message": report}, "tool_response": {"success": True}},
                  session)

    def reports(self, session="s1"):
        return verify_relay.reports(self.data, session)



class Keeps(Relay):
    def test_each_agent_kept_by_type_and_spec(self):
        self.agent(VERIFIER, "1.1 pass")
        self.agent(CHECKER, "1.1 confirmed")
        self.agent(OTHER_SPEC, "2.1 fail")
        got = {(r["agent"], r["document"]): r["text"] for r in self.reports()}
        self.assertEqual(got, {
            ("verifier", "/r/docs/specs/mail.spec.md"): "1.1 pass",
            ("verify-checker", "/r/docs/specs/mail.spec.md"): "1.1 confirmed",
            ("verifier", "/r/docs/specs/send.spec.md"): "2.1 fail",
        })

    def test_report_kept_word_for_word(self):
        report = "Result\n\n| a | \"b\" |\n  indented\n"
        self.agent(VERIFIER, report)
        self.assertEqual(self.reports()[0]["text"], report)

    def test_rerun_replaces_earlier_report(self):
        self.agent(VERIFIER, "first")
        self.agent(VERIFIER, "second")
        self.assertEqual([r["text"] for r in self.reports()], ["second"])

    def test_handed_back_report_kept(self):
        self.agent(VERIFIER, "1.1 pass", handed_back=True)
        self.assertEqual(self.reports()[0]["text"], "1.1 pass")

    def test_other_agents_ignored(self):
        self.agent(("general-purpose", "Document: x\nDo something"), "nope")
        self.agent(("agentic:auditor", "Document: x\nRepository: /r"), "nope")
        self.assertEqual(self.reports(), [])

    def test_audit_relay_ignores_verify_agents(self):
        self.agent(VERIFIER, "1.1 pass")
        import audit_relay
        self.assertEqual(audit_relay.reports(self.data, "s1"), [])

    def test_sessions_kept_apart(self):
        self.agent(VERIFIER, "mine", session="s1")
        self.agent(VERIFIER, "theirs", session="s2")
        self.assertEqual([r["text"] for r in self.reports("s1")], ["mine"])

    def test_nothing_saved_without_data_folder(self):
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": ""}):
            self.agent(VERIFIER, "x")
        self.assertFalse(os.path.exists(self.data))

    def test_clear(self):
        self.agent(VERIFIER, "x")
        verify_relay.clear(self.data, "s1")
        self.assertEqual(self.reports(), [])


class Commit(Relay):
    def test_commit_kept_beside_reports(self):
        verify_relay.set_commit(self.data, "s1", "abc123")
        self.agent(VERIFIER, "1.1 pass")
        self.assertEqual(verify_relay.commit(self.data, "s1"), "abc123")
        self.assertEqual([r["text"] for r in self.reports()], ["1.1 pass"])

    def test_no_commit_before_start(self):
        self.assertIsNone(verify_relay.commit(self.data, "s1"))

    def test_clear_forgets_commit(self):
        verify_relay.set_commit(self.data, "s1", "abc123")
        verify_relay.clear(self.data, "s1")
        self.assertIsNone(verify_relay.commit(self.data, "s1"))


class Background(Relay):
    def test_background_report_from_stop(self):
        self.launch(VERIFIER, "a1")
        self.stopped("agentic:verifier", "a1", "1.1 pass")
        self.assertEqual(self.reports()[0]["text"], "1.1 pass")

    def test_stop_before_launch_is_seen(self):
        self.stopped("agentic:verifier", "a1", "1.1 pass")
        self.launch(VERIFIER, "a1")
        self.assertEqual(self.reports()[0]["text"], "1.1 pass")

    def test_hand_back_stays_final(self):
        self.launch(VERIFIER, "a1")
        self.hand_back("agentic:verifier", "a1", "1.1 pass")
        self.stopped("agentic:verifier", "a1", "Handing back my report.")
        self.assertEqual(self.reports()[0]["text"], "1.1 pass")

    def test_hand_back_from_project_thread_before_launch(self):
        self.hand_back("agentic:verify-checker", "a2", "1.1 confirmed")
        self.stopped("agentic:verify-checker", "a2", "Handing back my report.")
        self.launch(CHECKER, "a2")
        self.assertEqual(self.reports()[0]["text"], "1.1 confirmed")

    def test_launch_alone_keeps_nothing(self):
        self.launch(VERIFIER, "a1")
        self.assertEqual(self.reports(), [])


if __name__ == "__main__":
    unittest.main()

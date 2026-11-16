"""Tests for build_session.py, fed recorded hook inputs and sample session records."""

import io
import json
import os
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_session  # noqa: E402


def reply(tokens, sidechain=False, cached=True):
    """One line of a session record: a reply from Claude using `tokens` of context."""
    usage = ({"input_tokens": 5, "cache_read_input_tokens": tokens - 105,
              "cache_creation_input_tokens": 100, "output_tokens": 40}
             if cached else {"input_tokens": tokens, "output_tokens": 40})
    return {"type": "assistant", "isSidechain": sidechain,
            "message": {"role": "assistant", "content": [{"type": "text", "text": "ok"}],
                        "usage": usage}}


def compacted():
    return {"type": "system", "subtype": "compact_boundary", "isSidechain": False,
            "content": "Conversation compacted"}


def person(text):
    return {"type": "user", "isSidechain": False, "message": {"role": "user", "content": text}}


class Hooks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.transcript = os.path.join(self.tmp.name, "session.jsonl")

    def record(self, *lines, raw=None):
        with open(self.transcript, "w", encoding="utf-8") as f:
            if raw is not None:
                f.write(raw)
            for line in lines:
                f.write(json.dumps(line) + "\n")

    def hook(self, event, session="s1"):
        event = dict(event, session_id=session, transcript_path=self.transcript)
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            code = build_session.main([])
        self.assertEqual(code, 0)
        text = out.getvalue().strip()
        return json.loads(text) if text else None

    def start(self, source="startup", session="s1"):
        return self.hook({"hook_event_name": "SessionStart", "source": source}, session)

    def say(self, prompt, session="s1"):
        return self.hook({"hook_event_name": "UserPromptSubmit", "prompt": prompt}, session)

    def skill(self, name="agentic:build", session="s1"):
        return self.hook({"hook_event_name": "PreToolUse", "tool_name": "Skill",
                          "tool_input": {"skill": name, "args": "docs/plans/x.md"}}, session)

    def context(self, result, event):
        """The added context a hook result gives Claude; fails on anything that refuses."""
        self.assertIsNotNone(result)
        self.assertNotIn("decision", result)
        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], event)
        self.assertNotIn("permissionDecision", output)
        return output["additionalContext"]


class Growth(Hooks):
    def growth(self):
        return build_session.growth(self.transcript)

    def test_no_reply_yet_is_zero(self):
        self.record(person("build docs/plans/x.md"))
        self.assertEqual(self.growth(), 0)

    def test_one_reply_is_zero(self):
        self.record(person("hi"), reply(85000))
        self.assertEqual(self.growth(), 0)

    def test_latest_reply_minus_first(self):
        self.record(person("hi"), reply(48000), reply(52000), person("more"), reply(61000))
        self.assertEqual(self.growth(), 13000)

    def test_all_three_input_counts_add_up(self):
        self.record(reply(10000, cached=False), reply(30000))
        self.assertEqual(self.growth(), 20000)

    def test_sub_agent_replies_skipped(self):
        self.record(reply(40000), reply(90000, sidechain=True), reply(45000))
        self.assertEqual(self.growth(), 5000)

    def test_compacted_session_measured_from_its_first_reply_after_compaction(self):
        # Code review: measured from the session's very first reply, conversation added after a
        # compaction could hide below the limit.
        self.record(reply(49000), reply(150000), compacted(), reply(35000), reply(65000))
        self.assertEqual(self.growth(), 30000)

    def test_compaction_with_no_reply_since_is_zero(self):
        self.record(reply(49000), reply(150000), compacted())
        self.assertEqual(self.growth(), 0)

    def test_smaller_than_at_the_start_is_zero(self):
        self.record(reply(40000), reply(30000))
        self.assertEqual(self.growth(), 0)

    def test_missing_record_is_unknown(self):
        self.assertIsNone(self.growth())

    def test_no_path_is_unknown(self):
        self.assertIsNone(build_session.growth(None))

    def test_broken_lines_skipped(self):
        self.record(reply(40000), reply(70000), raw="not json\n[1, 2]\n")
        self.assertEqual(self.growth(), 30000)

    def test_replies_without_usage_skipped(self):
        line = reply(99000)
        del line["message"]["usage"]
        self.record(reply(40000), line, reply(41000))
        self.assertEqual(self.growth(), 1000)


class Skill(Hooks):
    def test_short_session_told_it_is_under_the_limit(self):
        self.record(person("build it"), reply(85000), reply(90000))
        text = self.context(self.skill(), "PreToolUse")
        self.assertIn("5,000 tokens", text)
        self.assertIn("under", text)
        self.assertIn("20,000", text)

    def test_long_session_told_it_is_over_the_limit(self):
        self.record(person("plan it"), reply(50000), reply(81000))
        text = self.context(self.skill(), "PreToolUse")
        self.assertIn("31,000 tokens", text)
        self.assertIn("over", text)

    def test_exactly_the_limit_is_under(self):
        self.record(reply(50000), reply(70000))
        self.assertIn("under", self.context(self.skill(), "PreToolUse"))

    def test_session_with_no_reply_is_under(self):
        self.record(person("build it"))
        text = self.context(self.skill(), "PreToolUse")
        self.assertIn("0 tokens", text)
        self.assertIn("under", text)

    def test_bare_skill_name_measured(self):
        self.record(reply(50000), reply(90000))
        self.assertIn("over", self.context(self.skill("build"), "PreToolUse"))

    def test_other_skills_left_alone(self):
        self.record(reply(50000), reply(90000))
        self.assertIsNone(self.skill("agentic:spec"))
        self.assertIsNone(self.skill("code-review"))

    def test_unreadable_record_said_to_be_unknown(self):
        text = self.context(self.skill(), "PreToolUse")
        self.assertIn("could not be measured", text)
        self.assertNotIn("0 tokens", text)

    def test_never_refused_without_a_data_folder(self):
        self.record(reply(50000), reply(90000))
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": ""}):
            self.context(self.skill(), "PreToolUse")


class Typed(Hooks):
    def test_typed_build_measured_and_never_blocked(self):
        self.record(person("plan"), reply(50000), reply(90000))
        text = self.context(self.say("/agentic:build docs/plans/x.md"), "UserPromptSubmit")
        self.assertIn("40,000 tokens", text)
        self.assertIn("over", text)

    def test_short_name_also_measured(self):
        self.record(reply(50000))
        self.assertIn("under", self.context(self.say("/build docs/plans/x.md"), "UserPromptSubmit"))

    def test_other_messages_left_alone(self):
        self.record(reply(50000), reply(90000))
        self.assertIsNone(self.say("hi"))
        self.assertIsNone(self.say("/agentic:plan docs/specs/x.spec.md"))
        self.assertIsNone(self.say("/builder"))

    def test_a_thread_opened_by_the_coordinator_is_measured_like_any_other(self):
        # Issue #83: the coordinator's opening message is not the person's, which no longer matters.
        self.record(reply(85000), reply(88000))
        self.assertIn("under", self.context(self.skill(), "PreToolUse"))


class Building(Hooks):
    def test_build_started_by_skill_recorded(self):
        self.record(reply(50000), reply(90000))
        self.skill()
        self.assertTrue(build_session.building("s1"))

    def test_build_typed_recorded(self):
        self.say("/agentic:build docs/plans/x.md")
        self.assertTrue(build_session.building("s1"))

    def test_no_build_recorded_otherwise(self):
        self.say("hi")
        self.skill("agentic:spec")
        self.assertFalse(build_session.building("s1"))

    def test_sessions_kept_apart(self):
        self.skill(session="a")
        self.assertFalse(build_session.building("b"))

    def test_the_record_survives_the_session_ending(self):
        # Issue #37: `claude --resume`, or a restarted container, brings the same session back.
        self.skill()
        self.hook({"hook_event_name": "SessionEnd"})
        self.assertTrue(build_session.building("s1"))

    def test_a_resumed_build_is_still_building(self):
        self.skill()
        self.start("resume")
        self.assertTrue(build_session.building("s1"))

    def test_a_restart_that_keeps_the_session_id_is_still_building(self):
        self.skill()
        self.start("startup")
        self.start("compact")
        self.assertTrue(build_session.building("s1"))

    def test_saving_a_record_deletes_another_sessions_once_it_is_a_month_old(self):
        self.skill(session="old")
        sessions = os.path.join(self.tmp.name, "sessions")
        month = time.time() - 31 * 24 * 60 * 60
        os.utime(os.path.join(sessions, "old.json"), (month, month))
        self.skill()
        self.assertEqual(os.listdir(sessions), ["s1.json"])

    def test_session_id_cannot_leave_the_folder(self):
        self.skill(session="../../escape")
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "..", "escape.json")))


class Broken(Hooks):
    def test_bad_input_prints_nothing(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("not json")), redirect_stdout(out):
            self.assertEqual(build_session.main([]), 0)
        self.assertEqual(out.getvalue().strip(), "")

    def test_unknown_event_prints_nothing(self):
        self.assertIsNone(self.hook({"hook_event_name": "Stop"}))


if __name__ == "__main__":
    unittest.main()

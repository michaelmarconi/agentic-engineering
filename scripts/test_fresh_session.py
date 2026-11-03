"""Tests for fresh_session.py, fed recorded hook inputs."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fresh_session  # noqa: E402

THREAD_OPENING = (
    '<wake reason="thread_created"><coordinator-relay><relay from="coordinator">'
    '<cited author="user">please build docs/plans/2026-11-03-thing.md</cited>'
    '<note>Build this plan.</note></relay></coordinator-relay></wake>'
)
THREAD_MESSAGE = (
    '<wake reason="mention"><project><thread><message trigger="true" from="human" trust="principal" '
    'author="Dana">build docs/plans/2026-11-03-thing.md</message></thread></project></wake>'
)
THREAD_EVENT = (
    '<wake reason="external-event"><event source="github" kind="pull_request.closed" from="system" '
    'trust="relay">{}</event></wake>'
)


class Hooks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def hook(self, event, session="s1"):
        event = dict(event, session_id=session)
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            code = fresh_session.main([])
        self.assertEqual(code, 0)
        text = out.getvalue().strip()
        return json.loads(text) if text else None

    def start(self, source="startup", session="s1"):
        return self.hook({"hook_event_name": "SessionStart", "source": source}, session)

    def say(self, prompt, session="s1"):
        return self.hook({"hook_event_name": "UserPromptSubmit", "prompt": prompt}, session)

    def skill(self, name="sdlc:build", session="s1"):
        return self.hook({"hook_event_name": "PreToolUse", "tool_name": "Skill",
                          "tool_input": {"skill": name, "args": "docs/plans/x.md"}}, session)

    def assert_refused_prompt(self, result):
        self.assertIsNotNone(result)
        self.assertEqual(result["decision"], "block")
        self.assertIn("new session", result["reason"])

    def assert_refused_skill(self, result):
        self.assertIsNotNone(result)
        decision = result["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("new session", decision["permissionDecisionReason"])


class Typed(Hooks):
    def test_first_message_starts_build(self):
        self.start()
        self.assertIsNone(self.say("/sdlc:build docs/plans/x.md"))
        self.assertIsNone(self.skill())

    def test_short_name_also_checked(self):
        self.start()
        self.say("hi")
        self.assert_refused_prompt(self.say("/build docs/plans/x.md"))

    def test_later_message_refused(self):
        self.start()
        self.say("hi")
        self.assert_refused_prompt(self.say("/sdlc:build docs/plans/x.md"))

    def test_other_commands_left_alone(self):
        self.start()
        self.say("hi")
        self.assertIsNone(self.say("/sdlc:plan docs/specs/x.spec.md"))
        self.assertIsNone(self.say("/builder"))


class Words(Hooks):
    def test_first_message_in_words_starts_build(self):
        self.start()
        self.say("Please build docs/plans/x.md")
        self.assertIsNone(self.skill())

    def test_later_message_in_words_refused(self):
        self.start()
        self.say("Let's talk about the plan")
        self.say("Now build it")
        self.assert_refused_skill(self.skill())

    def test_other_skills_left_alone(self):
        self.start()
        self.say("hi")
        self.say("write a spec")
        self.assertIsNone(self.skill("sdlc:spec"))
        self.assertIsNone(self.skill("code-review"))

    def test_bare_skill_name_checked(self):
        self.start()
        self.say("hi")
        self.say("build it")
        self.assert_refused_skill(self.skill("build"))


class Sessions(Hooks):
    def test_clear_makes_it_fresh_again(self):
        self.start()
        self.say("hi")
        self.start("clear", session="s2")
        self.say("build docs/plans/x.md", session="s2")
        self.assertIsNone(self.skill(session="s2"))

    def test_resumed_session_refused(self):
        self.start("resume")
        self.say("build docs/plans/x.md")
        self.assert_refused_skill(self.skill())

    def test_unknown_session_refused(self):
        self.say("build docs/plans/x.md", session="never-started")
        self.assert_refused_skill(self.skill(session="never-started"))

    def test_compaction_keeps_the_count(self):
        self.start()
        self.say("build docs/plans/x.md")
        self.start("compact")
        self.assertIsNone(self.skill())

    def test_sessions_kept_apart(self):
        self.start(session="a")
        self.start(session="b")
        self.say("hi", session="a")
        self.say("more", session="a")
        self.say("build it", session="b")
        self.assertIsNone(self.skill(session="b"))

    def test_session_end_forgets_it(self):
        self.start()
        self.hook({"hook_event_name": "SessionEnd"})
        self.assertEqual(os.listdir(os.path.join(self.tmp.name, "sessions")), [])


class Threads(Hooks):
    def test_opening_note_does_not_count(self):
        self.start()
        self.say(THREAD_OPENING)
        self.say(THREAD_MESSAGE)
        self.assertIsNone(self.skill())

    def test_build_from_the_opening_note_alone_refused(self):
        self.start()
        self.say(THREAD_OPENING)
        self.assert_refused_skill(self.skill())

    def test_events_do_not_count(self):
        self.start()
        self.say(THREAD_EVENT)
        self.say(THREAD_MESSAGE)
        self.assertIsNone(self.skill())

    def test_second_message_in_a_thread_refused(self):
        self.start()
        self.say(THREAD_OPENING)
        self.say(THREAD_MESSAGE)
        self.say(THREAD_MESSAGE)
        self.assert_refused_skill(self.skill())


class Broken(Hooks):
    def test_without_a_data_folder_build_refused(self):
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": ""}):
            self.start()
            self.say("build it")
            result = self.skill()
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_bad_input_refuses_build_only(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("not json")), redirect_stdout(out):
            self.assertEqual(fresh_session.main([]), 0)
        self.assertEqual(out.getvalue().strip(), "")

    def test_session_id_cannot_leave_the_folder(self):
        self.start(session="../../escape")
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "..", "escape.json")))


if __name__ == "__main__":
    unittest.main()

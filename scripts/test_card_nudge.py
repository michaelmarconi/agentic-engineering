"""Tests for card_nudge.py, the hook that has a question asked in words also posted on a decision card."""

import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import card_nudge  # noqa: E402

LINE = "Accept, give your own answer, ignore or defer?"
QUESTION = ("**Question 1 of 2: how long a done item can be undone**\n\n"
            "> **Proposed:** a day.\n>\n> **Why:** the brief says so.\n\n"
            "Can a done item be undone after a day?\n\n" + LINE)


def post(text, tool="mcp__hearthbot__post_message"):
    return {"hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": {"text": text}}


def context(out):
    return out["hookSpecificOutput"]["additionalContext"]


class Nudge(unittest.TestCase):
    def test_a_question_ending_with_the_line_is_followed_by_a_card(self):
        out = card_nudge.handle(post(QUESTION))
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("decision card", context(out))

    def test_the_card_names_its_options_exactly_and_recommends_the_proposal(self):
        said = context(card_nudge.handle(post(QUESTION)))
        for option in ('"Accept"', '"Ignore"', '"Defer"'):
            self.assertIn(option, said)
        self.assertIn("exactly", said)
        self.assertIn("recommended", said)

    def test_trailing_space_after_the_line_still_counts(self):
        self.assertIsNotNone(card_nudge.handle(post(QUESTION + "\n\n")))

    def test_any_server_post_message_tool_counts(self):
        self.assertIsNotNone(card_nudge.handle(post(QUESTION, tool="mcp__thread__post_message")))

    def test_a_message_without_the_line_passes(self):
        self.assertIsNone(card_nudge.handle(post("The spec is written and reviewed.")))

    def test_the_line_quoted_mid_message_passes(self):
        self.assertIsNone(card_nudge.handle(post(QUESTION + "\n\nI'll wait for your answer.")))

    def test_other_tools_pass(self):
        self.assertIsNone(card_nudge.handle(post(QUESTION, tool="Write")))
        self.assertIsNone(card_nudge.handle(post(QUESTION, tool="mcp__slack__send_message")))

    def test_a_message_with_no_text_passes(self):
        event = post(QUESTION)
        event["tool_input"] = {}
        self.assertIsNone(card_nudge.handle(event))


class Command(unittest.TestCase):
    def run_hook(self, stdin):
        return subprocess.run([sys.executable, os.path.join(HERE, "card_nudge.py")], input=stdin,
                              capture_output=True, text=True)

    def test_prints_the_nudge_as_json(self):
        done = self.run_hook(json.dumps(post(QUESTION)))
        self.assertEqual(done.returncode, 0)
        self.assertIn("decision card", context(json.loads(done.stdout)))

    def test_prints_nothing_for_a_plain_message(self):
        done = self.run_hook(json.dumps(post("Done.")))
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_bad_input_prints_nothing(self):
        done = self.run_hook("not json")
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_help_names_the_output_and_exit_code(self):
        help_done = subprocess.run([sys.executable, os.path.join(HERE, "card_nudge.py"), "--help"],
                                   capture_output=True, text=True)
        self.assertEqual(help_done.returncode, 0)
        self.assertIn("exits 0", help_done.stdout)


class Registered(unittest.TestCase):
    def test_hooks_file_runs_it_after_a_post_message_tool(self):
        with open(os.path.join(HERE, "..", "hooks", "hooks.json")) as f:
            hooks = json.load(f)["hooks"]["PostToolUse"]
        matchers = [h["matcher"] for h in hooks
                    if any("card_nudge.py" in c["command"] for c in h["hooks"])]
        self.assertEqual(len(matchers), 1)
        self.assertTrue(re.fullmatch(matchers[0], "mcp__hearthbot__post_message"))
        self.assertFalse(re.fullmatch(matchers[0], "Bash"))


if __name__ == "__main__":
    unittest.main()

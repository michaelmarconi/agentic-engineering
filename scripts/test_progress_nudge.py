"""Tests for progress_nudge.py, the hook that prompts a progress update after each helper agent
(docs/adrs/0063)."""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "progress_nudge.py")
sys.path.insert(0, HERE)
import progress_nudge  # noqa: E402

NOTE = ("If you are showing progress, then once this helper agent's report is in, update your "
        "progress list: mark the step it ran as done, with a one-line summary of what it found.")


def event(tool):
    return {"hook_event_name": "PostToolUse", "tool_name": tool,
            "tool_input": {"prompt": "Document: /repo/docs/plans/p.md\nReview this build."}}


def run(payload):
    return subprocess.run([sys.executable, SCRIPT], input=payload, capture_output=True, text=True)


class Nudge(unittest.TestCase):
    def test_each_helper_agent_tool_brings_the_note(self):
        for tool in ("Agent", "Task", "SubagentHandback"):
            out = progress_nudge.handle(event(tool))
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse", tool)
            self.assertEqual(out["hookSpecificOutput"]["additionalContext"], NOTE, tool)

    def test_every_other_tool_passes(self):
        for tool in ("Bash", "Read", "TaskCreate", "TaskUpdate", "TodoWrite", "mcp__hearthbot__post_message",
                     "AgentX", ""):
            self.assertIsNone(progress_nudge.handle(event(tool)), tool)

    def test_another_hook_event_passes(self):
        self.assertIsNone(progress_nudge.handle(dict(event("Agent"), hook_event_name="PreToolUse")))

    def test_the_command_prints_the_note_as_json(self):
        result = run(json.dumps(event("Agent")))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"], NOTE)

    def test_the_command_prints_nothing_for_other_tools_or_bad_input(self):
        for payload in (json.dumps(event("Bash")), "not json", "[]", ""):
            result = run(payload)
            self.assertEqual((result.returncode, result.stdout), (0, ""), payload)

    def test_help_names_what_it_reads_and_prints(self):
        result = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("PostToolUse", result.stdout)
        self.assertIn("exits 0", result.stdout)


class Registered(unittest.TestCase):
    def test_the_hook_runs_after_every_helper_agent(self):
        with open(os.path.join(HERE, "..", "hooks", "hooks.json"), encoding="utf-8") as handle:
            hooks = json.load(handle)["hooks"]["PostToolUse"]
        matchers = [entry["matcher"] for entry in hooks
                    if any("progress_nudge.py" in hook["command"] for hook in entry["hooks"])]
        self.assertEqual(matchers, ["Agent|Task|SubagentHandback"])


if __name__ == "__main__":
    unittest.main()

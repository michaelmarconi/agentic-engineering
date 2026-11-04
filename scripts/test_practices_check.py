import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "practices_check.py")

TOPIC = "docs/practices/testing.md"


def section(lines, heading="## Practices"):
    return heading + "\n" + "".join(f"- line {i}\n" for i in range(lines - 1))


class PracticesCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = self.tmp.name

    def put(self, path, text):
        full = os.path.join(self.project, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def run_hook(self, tool, tool_input, raw=None):
        event = {"hook_event_name": "PreToolUse", "session_id": "s", "cwd": self.project,
                 "tool_name": tool, "tool_input": tool_input}
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.project)
        done = subprocess.run([sys.executable, SCRIPT], input=raw if raw is not None else json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout) if done.stdout.strip() else None

    def write(self, path, content, absolute=False):
        target = os.path.join(self.project, path) if absolute else path
        return self.run_hook("Write", {"file_path": target, "content": content})

    def edit(self, path, old, new, replace_all=False):
        return self.run_hook("Edit", {"file_path": os.path.join(self.project, path),
                                      "old_string": old, "new_string": new, "replace_all": replace_all})

    def assertRefused(self, out, needle):
        self.assertIsNotNone(out)
        decision = out["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn(needle, decision["permissionDecisionReason"])

    # The core: the ## Practices section of AGENTS.md

    def test_a_core_within_50_lines_is_allowed(self):
        self.assertIsNone(self.write("AGENTS.md", "# Agents\n\n" + section(50) + "\n## Other\n", True))

    def test_a_core_over_50_lines_is_refused_with_the_reason(self):
        out = self.write("AGENTS.md", "# Agents\n\n" + section(51) + "\n## Other\n", True)
        self.assertRefused(out, "50")
        self.assertIn("docs/practices/", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_the_core_ends_at_the_next_level_two_heading_and_trailing_blank_lines_do_not_count(self):
        text = section(50) + "\n\n\n" + "## Other\n" + "x\n" * 300
        self.assertIsNone(self.write("AGENTS.md", text, True))

    def test_level_three_headings_are_part_of_the_core(self):
        text = "## Practices\n### Check your work\n" + "- a\n" * 48 + "### Rules\n- b\n"
        self.assertRefused(self.write("AGENTS.md", text, True), "50")

    def test_the_rest_of_agents_md_may_be_any_length(self):
        self.assertIsNone(self.write("AGENTS.md", "# Agents\n" + "x\n" * 500, True))

    def test_an_edit_that_grows_the_core_past_50_lines_is_refused(self):
        self.put("AGENTS.md", section(50))
        self.assertRefused(self.edit("AGENTS.md", "- line 3\n", "- line 3\n- extra\n"), "50")

    def test_a_core_already_too_long_may_be_shortened(self):
        self.put("AGENTS.md", section(60))
        self.assertIsNone(self.edit("AGENTS.md", "- line 3\n", ""))

    def test_a_core_already_too_long_may_be_changed_without_growing(self):
        self.put("AGENTS.md", section(60))
        self.assertIsNone(self.edit("AGENTS.md", "- line 3\n", "- line three\n"))

    def test_a_core_already_too_long_may_not_grow(self):
        self.put("AGENTS.md", section(60))
        self.assertRefused(self.edit("AGENTS.md", "- line 3\n", "- line 3\n- more\n"), "50")

    def test_replace_all_is_applied_to_every_match(self):
        self.put("AGENTS.md", "## Practices\n" + "- x\n" * 26)
        self.assertRefused(self.edit("AGENTS.md", "- x\n", "- x\n- y\n", replace_all=True), "50")

    def test_multi_edit_applies_every_edit_in_order(self):
        self.put("AGENTS.md", section(49))
        out = self.run_hook("MultiEdit", {"file_path": os.path.join(self.project, "AGENTS.md"), "edits": [
            {"old_string": "- line 1\n", "new_string": "- line 1\n- a\n"},
            {"old_string": "- a\n", "new_string": "- a\n- b\n"}]})
        self.assertRefused(out, "50")

    def test_a_nested_agents_md_is_left_alone(self):
        self.assertIsNone(self.write("src/AGENTS.md", section(80), True))

    def test_a_relative_path_names_the_project_file(self):
        self.assertRefused(self.write("AGENTS.md", section(51)), "50")

    # Topic files

    def test_a_topic_file_within_200_lines_is_allowed(self):
        self.assertIsNone(self.write(TOPIC, "x\n" * 200, True))

    def test_a_topic_file_over_200_lines_is_refused(self):
        self.assertRefused(self.write(TOPIC, "x\n" * 201, True), "200")

    def test_a_topic_file_already_too_long_may_be_shortened(self):
        self.put(TOPIC, "x\n" * 210)
        self.assertIsNone(self.write(TOPIC, "x\n" * 205, True))

    def test_files_outside_docs_practices_are_left_alone(self):
        self.assertIsNone(self.write("docs/specs/a.spec.md", "x\n" * 500, True))
        self.assertIsNone(self.write("README.md", "@AGENTS.md\n" + "x\n" * 500, True))

    def test_only_markdown_files_in_docs_practices_are_checked(self):
        self.assertIsNone(self.write("docs/practices/data.json", "x\n" * 500, True))

    # Imports

    def test_an_import_in_the_core_is_refused(self):
        self.assertRefused(self.write("AGENTS.md", "## Practices\n@README.md\n", True), "@")

    def test_an_indented_import_in_a_topic_file_is_refused(self):
        self.assertRefused(self.write(TOPIC, "# Testing\n  @docs/other.md\n", True), "@")

    def test_an_import_outside_the_core_is_left_alone(self):
        self.assertIsNone(self.write("AGENTS.md", "# Agents\n@README.md\n\n## Practices\n- a\n", True))

    def test_an_at_sign_that_names_no_file_or_sits_in_code_is_not_an_import(self):
        text = ("## Practices\n- Ask @alice before merging.\n```\n@decorator\n@docs/x.md\n```\n"
                "- `@types/node` and `@docs/y.md` stay as written.\n- Mail me@example.com.\n")
        self.assertIsNone(self.write("AGENTS.md", text, True))

    def test_an_import_inside_a_line_is_refused(self):
        text = "## Practices\n### Files to read before a task\n- before writing tests: @docs/practices/testing.md\n"
        self.assertRefused(self.write("AGENTS.md", text, True), "@")

    def test_an_import_of_a_file_without_a_folder_inside_a_line_is_refused(self):
        self.assertRefused(self.write(TOPIC, "# Testing\nSee @README.md for more.\n", True), "@")

    def test_an_import_already_there_does_not_block_other_edits(self):
        self.put(TOPIC, "# Testing\n@old.md\n- a\n")
        self.assertIsNone(self.edit(TOPIC, "- a\n", "- b\n"))

    def test_an_edit_that_adds_a_second_import_is_refused(self):
        self.put(TOPIC, "# Testing\n@old.md\n- a\n")
        self.assertRefused(self.edit(TOPIC, "- a\n", "@new.md\n"), "@")

    # Everything else is left alone

    def test_an_edit_whose_text_is_not_found_is_left_to_the_tool(self):
        self.put("AGENTS.md", section(10))
        self.assertIsNone(self.edit("AGENTS.md", "not there", "x\n" * 100))

    def test_other_tools_and_malformed_input_never_block(self):
        self.assertIsNone(self.run_hook("Read", {"file_path": "AGENTS.md"}))
        self.assertIsNone(self.run_hook(None, None, raw="not json"))
        self.assertIsNone(self.run_hook(None, None, raw="[]"))
        self.assertIsNone(self.run_hook("Write", "oops"))

    def test_help_describes_the_hook(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("50", done.stdout)
        self.assertIn("200", done.stdout)


if __name__ == "__main__":
    unittest.main()

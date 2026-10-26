import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "status_check.py")
sys.path.insert(0, HERE)

import status_check  # noqa: E402


def spec(status="Draft", questions="None.", rule="The system SHALL do X."):
    return (
        "---\n"
        "# Change status only through /sdlc:spec and /sdlc:build.\n"
        f"status: {status}\n"
        "---\n\n# Thing\n\n## Problem\n\nP\n\n## Goal\n\nG\n\n## Scope\n\nIn:\n- a\n\n"
        f"## Requirements\n\n### Requirement: X\n\n{rule}\n\n"
        f"## Constraints\n\n- None.\n\n## Open questions\n\n{questions}\n"
    )


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "docs", "specs", "thing.spec.md")

    def put(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            f.write(text)

    def write(self, text, path=None):
        return status_check.check(
            {"tool_name": "Write", "tool_input": {"file_path": path or self.path, "content": text}}
        )

    def edit(self, old, new, replace_all=False):
        return status_check.check(
            {
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": self.path,
                    "old_string": old,
                    "new_string": new,
                    "replace_all": replace_all,
                },
            }
        )


class Parsing(unittest.TestCase):
    def test_status_ignores_comments_and_quotes(self):
        self.assertEqual(status_check.status_of('---\nstatus: "Ready to build"  # x\n---\n'), "Ready to build")

    def test_status_missing_without_frontmatter(self):
        self.assertIsNone(status_check.status_of("status: Draft\n"))

    def test_open_questions_empty_forms(self):
        for body in ["", "None.", "None", "- None.", "_None._"]:
            self.assertFalse(status_check.has_open_questions(spec(questions=body)), body)

    def test_open_questions_present(self):
        self.assertTrue(status_check.has_open_questions(spec(questions="- Who approves?")))

    def test_missing_open_questions_section_counts_as_open(self):
        self.assertTrue(status_check.has_open_questions("---\nstatus: Draft\n---\n# T\n"))


class NewSpec(Workspace):
    def test_new_draft_allowed(self):
        self.assertIsNone(self.write(spec()))

    def test_new_ready_refused(self):
        self.assertIn("Draft", self.write(spec("Ready to build")))

    def test_file_without_lifecycle_status_left_alone(self):
        self.assertIsNone(self.write("# Thing\n"))
        self.assertIsNone(self.write(spec("Approved")))

    def test_new_spec_created_by_edit_checked(self):
        self.assertIsNotNone(self.edit("", spec("Built")))

    def test_byte_order_mark(self):
        self.assertIsNone(self.write("\ufeff" + spec()))

    def test_other_files_ignored(self):
        other = os.path.join(self.tmp.name, "docs", "notes.md")
        self.assertIsNone(self.write("anything", path=other))

    def test_spec_in_subfolder_checked(self):
        sub = os.path.join(self.tmp.name, "docs", "specs", "billing", "invoice.spec.md")
        self.assertIsNotNone(self.write(spec("Built"), path=sub))


class Transitions(Workspace):
    def test_losing_status_refused(self):
        self.put(spec())
        self.assertIn("status", self.edit("status: Draft\n", ""))

    def test_unknown_status_refused(self):
        self.put(spec())
        self.assertIn("Approved", self.edit("status: Draft", "status: Approved"))

    def test_spec_without_status_cannot_skip_draft(self):
        self.put("# Thing\n")
        self.assertIn("Draft", self.write(spec("Ready to build")))

    def test_legacy_file_edit_allowed(self):
        self.put("# Thing\n")
        self.assertIsNone(self.edit("Thing", "Other"))

    def test_status_like_body_line_counts_as_change(self):
        self.put(spec("Built", rule="status: 404"))
        self.assertIn("Draft", self.edit("status: 404", "status: 410"))

    def test_draft_to_ready_without_questions_allowed(self):
        self.put(spec())
        self.assertIsNone(self.edit("status: Draft", "status: Ready to build"))

    def test_draft_to_ready_with_questions_refused(self):
        self.put(spec(questions="- Who approves?"))
        self.assertIn("open questions", self.edit("status: Draft", "status: Ready to build"))

    def test_setting_built_refused(self):
        self.put(spec("Ready to build"))
        self.assertIn("Built", self.edit("status: Ready to build", "status: Built"))

    def test_changing_ready_spec_without_draft_refused(self):
        self.put(spec("Ready to build"))
        self.assertIn("Draft", self.edit("do X", "do Y"))

    def test_changing_built_spec_without_draft_refused(self):
        self.put(spec("Built"))
        self.assertIn("Draft", self.edit("do X", "do Y"))

    def test_changing_built_spec_back_to_draft_allowed(self):
        self.put(spec("Built"))
        self.assertIsNone(self.write(spec("Draft", rule="The system SHALL do Y.")))

    def test_built_to_ready_refused(self):
        self.put(spec("Built"))
        self.assertIsNotNone(self.edit("status: Built", "status: Ready to build"))

    def test_rewriting_ready_spec_unchanged_allowed(self):
        self.put(spec("Ready to build"))
        self.assertIsNone(self.write(spec("Ready to build")))

    def test_draft_edit_allowed(self):
        self.put(spec())
        self.assertIsNone(self.edit("do X", "do Y"))

    def test_edit_that_will_fail_is_left_to_the_tool(self):
        self.put(spec("Built"))
        self.assertIsNone(self.edit("not in the file", "whatever"))

    def test_replace_all(self):
        self.put(spec("Ready to build", rule="X SHALL X."))
        self.assertIsNotNone(self.edit("X", "Z", replace_all=True))

    def test_multiedit(self):
        self.put(spec())
        result = status_check.check(
            {
                "tool_name": "MultiEdit",
                "tool_input": {
                    "file_path": self.path,
                    "edits": [
                        {"old_string": "status: Draft", "new_string": "status: Ready to build"},
                        {"old_string": "questions\n\nNone.", "new_string": "questions\n\n- Who approves?"},
                    ],
                },
            }
        )
        self.assertIn("open questions", result)


class Command(Workspace):
    def run_hook(self, payload):
        return subprocess.run(
            [sys.executable, SCRIPT], input=json.dumps(payload), capture_output=True, text=True
        )

    def test_refusal_exits_2_with_reason_on_stderr(self):
        done = self.run_hook({"tool_name": "Write", "tool_input": {"file_path": self.path, "content": spec("Built")}})
        self.assertEqual(done.returncode, 2)
        self.assertIn("Built", done.stderr)

    def test_allowed_exits_0_silently(self):
        done = self.run_hook({"tool_name": "Write", "tool_input": {"file_path": self.path, "content": spec()}})
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))

    def test_bad_input_does_not_block(self):
        done = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


if __name__ == "__main__":
    unittest.main()

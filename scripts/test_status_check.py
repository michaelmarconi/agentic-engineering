import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "status_check.py")
sys.path.insert(0, HERE)

import status_check  # noqa: E402


def spec(status="📝 Draft", questions="None.", rule="The system SHALL do X."):
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
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
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
        self.assertEqual(status_check.status_of('---\nstatus: "🟢 Ready to build"  # x\n---\n'), "🟢 Ready to build")

    def test_status_missing_without_frontmatter(self):
        self.assertIsNone(status_check.status_of("status: 📝 Draft\n"))

    def test_open_questions_empty_forms(self):
        for body in ["", "None.", "None", "- None.", "_None._"]:
            self.assertFalse(status_check.has_open_questions(spec(questions=body)), body)

    def test_footnotes_after_open_questions_ignored(self):
        self.assertFalse(status_check.has_open_questions(spec() + "\n[^1]: A source.\n"))

    def test_wrapped_footnotes_after_open_questions_ignored(self):
        footnote = "\n[^1]: Settlement file, the nightly list of card payments the processor\n    paid us for.\n"
        self.assertFalse(status_check.has_open_questions(spec() + footnote))

    def test_question_after_wrapped_footnote_counts(self):
        self.assertTrue(status_check.has_open_questions(spec() + "\n[^1]: A source\n    wrapped.\n\n- Who approves?\n"))

    def test_footnote_running_onto_more_lines_ignored(self):
        text = spec() + "\n[^1]: A source that runs\n    onto a second line.\n[^2]: Another.\n"
        self.assertFalse(status_check.has_open_questions(text))

    def test_indented_question_after_a_footnote_still_counts(self):
        text = spec() + "\n[^1]: A source.\n\n  - Who approves?\n"
        self.assertTrue(status_check.has_open_questions(text))

    def test_open_questions_present(self):
        self.assertTrue(status_check.has_open_questions(spec(questions="- Who approves?")))

    def test_missing_open_questions_section_counts_as_open(self):
        self.assertTrue(status_check.has_open_questions("---\nstatus: 📝 Draft\n---\n# T\n"))


class NewSpec(Workspace):
    def test_new_draft_allowed(self):
        self.assertIsNone(self.write(spec()))

    def test_new_accepted_refused(self):
        self.assertIn("Draft", self.write(spec("👍 Accepted")))

    def test_file_without_lifecycle_status_left_alone(self):
        self.assertIsNone(self.write("# Thing\n"))
        self.assertIsNone(self.write(spec("Approved")))

    def test_new_spec_created_by_edit_checked(self):
        self.assertIsNotNone(self.edit("", spec("👍 Accepted")))

    def test_new_spec_with_another_kind_of_status_refused(self):
        for value in ("🟢 Ready to build", "✅ Built", "Built", "❌ Rejected"):
            self.assertIn("Draft", self.write(spec(value)), value)

    def test_byte_order_mark(self):
        self.assertIsNone(self.write("\ufeff" + spec()))

    def test_other_files_ignored(self):
        other = os.path.join(self.tmp.name, "docs", "notes.md")
        self.assertIsNone(self.write("anything", path=other))

    def test_docs_specs_outside_project_root_ignored(self):
        nested = os.path.join(self.tmp.name, "evals", "case", "docs", "specs", "thing.spec.md")
        self.assertIsNone(self.write(spec("✅ Built"), path=nested))

    def test_unreadable_spec_refused(self):
        self.put("")
        with open(self.path, "wb") as f:
            f.write(b"status: \xe9\n")
        self.assertIn("could not read", self.edit("a", "b"))

    def test_spec_in_subfolder_checked(self):
        sub = os.path.join(self.tmp.name, "docs", "specs", "billing", "invoice.spec.md")
        self.assertIsNotNone(self.write(spec("👍 Accepted"), path=sub))


class Transitions(Workspace):
    def test_losing_status_refused(self):
        self.put(spec())
        self.assertIn("status", self.edit("status: 📝 Draft\n", ""))

    def test_unknown_status_refused(self):
        self.put(spec())
        self.assertIn("Approved", self.edit("status: 📝 Draft", "status: Approved"))

    def test_spec_without_status_cannot_skip_draft(self):
        self.put("# Thing\n")
        self.assertIn("Draft", self.write(spec("👍 Accepted")))

    def test_legacy_file_edit_allowed(self):
        self.put("# Thing\n")
        self.assertIsNone(self.edit("Thing", "Other"))

    def test_status_like_body_line_counts_as_change(self):
        self.put(spec("👍 Accepted", rule="status: 404"))
        self.assertIn("Draft", self.edit("status: 404", "status: 410"))

    def test_draft_to_accepted_without_questions_allowed(self):
        self.put(spec())
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_draft_to_accepted_with_other_changes_refused(self):
        self.put(spec())
        self.assertIn("on its own", self.write(spec("👍 Accepted", rule="The system SHALL do Y.")))

    def test_accepted_without_open_questions_section_named_in_refusal(self):
        self.put(spec().split("\n## Open questions")[0])
        self.assertIn("no Open questions section", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_draft_to_accepted_with_questions_refused(self):
        self.put(spec(questions="- Who approves?"))
        self.assertIn("open questions", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_statuses_about_the_software_refused(self):
        self.put(spec())
        for status in ("🟢 Ready to build", "✅ Built"):
            reason = self.edit("status: 📝 Draft", f"status: {status}")
            self.assertIn("`👍 Accepted`", reason)

    def test_changing_accepted_spec_without_draft_refused(self):
        self.put(spec("👍 Accepted"))
        self.assertIn("Draft", self.edit("do X", "do Y"))

    def test_changing_accepted_spec_back_to_draft_allowed(self):
        self.put(spec("👍 Accepted"))
        self.assertIsNone(self.write(spec("📝 Draft", rule="The system SHALL do Y.")))

    def test_rewriting_accepted_spec_unchanged_allowed(self):
        self.put(spec("👍 Accepted"))
        self.assertIsNone(self.write(spec("👍 Accepted")))

    def test_spec_with_a_status_from_before_must_go_back_to_draft(self):
        for status in ("🟢 Ready to build", "✅ Built"):
            self.put(spec(status))
            self.assertIn("Draft", self.edit(f"status: {status}", "status: 👍 Accepted"))
            self.assertIsNone(self.edit(f"status: {status}", "status: 📝 Draft"))

    def test_draft_edit_allowed(self):
        self.put(spec())
        self.assertIsNone(self.edit("do X", "do Y"))

    def test_edit_that_cannot_be_matched_refused_on_lifecycle_spec(self):
        self.put(spec("👍 Accepted").replace("do X", "do ’X’"))
        self.assertIn("exactly", self.edit("do 'X'", "do 'Y'"))

    def test_edit_that_cannot_be_matched_allowed_on_other_files(self):
        self.put("# Thing\n")
        self.assertIsNone(self.edit("not in the file", "whatever"))

    def test_empty_file_filled_by_edit_checked(self):
        self.put("")
        self.assertIsNotNone(self.edit("", spec("👍 Accepted")))

    def test_new_file_by_multiedit_checked(self):
        result = status_check.check(
            {
                "tool_name": "MultiEdit",
                "tool_input": {"file_path": self.path, "edits": [{"old_string": "", "new_string": spec("👍 Accepted")}]},
            }
        )
        self.assertIsNotNone(result)

    def test_second_status_line_refused(self):
        self.put(spec())
        self.assertIn("one", self.edit("status: 📝 Draft", "status: 📝 Draft\nstatus: 👍 Accepted"))

    def test_replace_all(self):
        self.put(spec("👍 Accepted", rule="X SHALL X."))
        self.assertIsNotNone(self.edit("X", "Z", replace_all=True))

    def test_multiedit(self):
        self.put(spec())
        result = status_check.check(
            {
                "tool_name": "MultiEdit",
                "tool_input": {
                    "file_path": self.path,
                    "edits": [
                        {"old_string": "status: 📝 Draft", "new_string": "status: 👍 Accepted"},
                        {"old_string": "questions\n\nNone.", "new_string": "questions\n\n- Who approves?"},
                    ],
                },
            }
        )
        self.assertIsNotNone(result)


def adr(status="📝 Draft", extra="", body="Chosen option: Redis, because it is fast enough.", questions="None."):
    return (
        "---\n"
        f"status: {status}\n"
        "date: 2026-10-27\n"
        f"{extra}"
        "---\n\n# Store sessions in Redis\n\n## Context and Problem Statement\n\nC\n\n"
        "## Considered Options\n\n- Redis\n- Postgres: slower\n\n"
        f"## Decision Outcome\n\n{body}\n\n"
        f"## Open questions\n\n{questions}\n"
    )


class AdrWorkspace(Workspace):
    def setUp(self):
        super().setUp()
        self.path = os.path.join(self.tmp.name, "docs", "adrs", "0001-session-data-storage.md")


class Adr(AdrWorkspace):
    def test_new_draft_allowed(self):
        self.assertIsNone(self.write(adr()))

    def test_new_accepted_refused(self):
        self.assertIn("Draft", self.write(adr("👍 Accepted")))

    def test_proposed_is_not_a_status(self):
        self.put(adr())
        self.assertIn("Proposed", self.edit("status: 📝 Draft", "status: Proposed"))

    def test_losing_status_refused(self):
        self.put(adr())
        self.assertIn("status", self.edit("status: 📝 Draft\n", ""))

    def test_draft_edit_allowed(self):
        self.put(adr())
        self.assertIsNone(self.edit("fast enough", "fast and cheap enough"))

    def test_draft_to_accepted_alone_allowed(self):
        self.put(adr())
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_draft_to_rejected_alone_allowed(self):
        self.put(adr())
        self.assertIsNone(self.edit("status: 📝 Draft", "status: ❌ Rejected"))

    def test_accepting_with_open_questions_refused(self):
        self.put(adr(questions="- How long do sessions last?"))
        self.assertIn("open questions", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_accepting_without_open_questions_section_refused(self):
        self.put(adr().split("\n## Open questions")[0])
        self.assertIn("no Open questions section", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_rejecting_with_open_questions_allowed(self):
        self.put(adr(questions="- How long do sessions last?"))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: ❌ Rejected"))

    def test_accepting_with_other_changes_refused(self):
        self.put(adr())
        self.assertIn("on its own", self.write(adr("👍 Accepted", body="Chosen option: Postgres.")))

    def test_draft_to_superseded_refused(self):
        self.put(adr())
        self.assertIsNotNone(self.edit("status: 📝 Draft", "status: ↪️ Superseded"))

    def test_accepted_is_immutable(self):
        self.put(adr("👍 Accepted"))
        self.assertIn("supersede", self.edit("fast enough", "fast and cheap enough"))

    def test_rejected_is_immutable(self):
        self.put(adr("❌ Rejected"))
        self.assertIsNotNone(self.edit("fast enough", "fast and cheap enough"))

    def test_accepted_back_to_draft_refused(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNotNone(self.edit("status: 👍 Accepted", "status: 📝 Draft"))

    def test_accepted_to_rejected_refused(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNotNone(self.edit("status: 👍 Accepted", "status: ❌ Rejected"))

    def test_rejected_cannot_be_accepted(self):
        self.put(adr("❌ Rejected"))
        self.assertIsNotNone(self.edit("status: ❌ Rejected", "status: 👍 Accepted"))

    def put_replacement(self, status="👍 Accepted", supersedes="0001", number="0002"):
        path = os.path.join(self.tmp.name, "docs", "adrs", f"{number}-session-data-storage.md")
        with open(path, "w") as f:
            f.write(adr(status, extra=f"supersedes: {supersedes}\n"))

    def test_superseding_with_link_allowed(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement()
        self.assertIsNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_superseding_needs_a_four_digit_number(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement()
        self.assertIn("four-digit", self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 2\n"))

    def test_superseding_needs_an_existing_replacement(self):
        self.put(adr("👍 Accepted"))
        self.assertIn("0003", self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0003\n"))

    def test_superseding_needs_an_accepted_replacement(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement(status="📝 Draft")
        self.assertIn("Accepted", self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_replacement_must_name_this_adr(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement(supersedes="0005")
        self.assertIn("supersedes", self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_quoted_number_and_status_accepted(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement(supersedes='"0001"')
        self.assertIsNone(self.edit("status: 👍 Accepted\n", 'status: "↪️ Superseded"\nsuperseded-by: "0002"\n'))

    def test_byte_order_mark_and_crlf(self):
        self.put("\ufeff" + adr("👍 Accepted").replace("\n", "\r\n"))
        self.assertIsNotNone(self.edit("fast enough", "fast and cheap enough"))

    def test_multiedit_accept_with_change_refused(self):
        self.put(adr())
        result = status_check.check({"tool_name": "MultiEdit", "tool_input": {"file_path": self.path, "edits": [
            {"old_string": "status: 📝 Draft", "new_string": "status: 👍 Accepted"},
            {"old_string": "fast enough", "new_string": "cheap"}]}})
        self.assertIsNotNone(result)

    def test_replace_all_on_accepted_refused(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNotNone(self.edit("Redis", "Valkey", replace_all=True))

    def test_new_adr_with_unknown_status_refused(self):
        for value in ("accepted", "Proposed"):
            self.assertIn("Draft", self.write(adr(value)), value)

    def test_status_line_of_decided_adr_is_fixed(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNotNone(self.edit("status: 👍 Accepted", "status: 👍 Accepted # reopened"))

    def test_replacement_may_supersede_several(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement(supersedes="0001, 0004")
        self.assertIsNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_replacement_file_suffix_in_capitals(self):
        self.put(adr("👍 Accepted"))
        with open(os.path.join(self.tmp.name, "docs", "adrs", "0002-x.MD"), "w") as f:
            f.write(adr("👍 Accepted", extra="supersedes: 0001\n"))
        self.assertIsNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_replacement_supersedes_as_a_list(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement(supersedes='["0001"]')
        self.assertIsNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_unknown_status_must_become_draft_first(self):
        self.put(adr("Proposed"))
        self.assertIn("Draft` first", self.edit("status: Proposed", "status: 👍 Accepted"))

    def test_space_before_colon_still_a_status(self):
        self.assertIsNotNone(self.write(adr().replace("status: 📝 Draft", "status : Accepted")))

    def test_two_adrs_with_the_replacement_number_refused(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement()
        with open(os.path.join(self.tmp.name, "docs", "adrs", "0002-other.md"), "w") as f:
            f.write(adr("📝 Draft"))
        self.assertIn("more than one", self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_cannot_supersede_itself(self):
        self.put(adr("👍 Accepted", extra="supersedes: 0001\n"))
        self.assertIsNotNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0001\n"))

    def test_status_key_in_capitals_still_checked(self):
        self.assertIsNotNone(self.write(adr().replace("status: 📝 Draft", "Status: Accepted")))

    def test_subfolder_and_capitals_still_checked(self):
        for rel in (("docs", "adrs", "old", "0009-x.md"), ("docs", "ADRs", "0009-x.md")):
            self.assertIsNotNone(self.write(adr("👍 Accepted"), path=os.path.join(self.tmp.name, *rel)), rel)

    def test_superseding_without_link_refused(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement()
        self.assertIn("superseded-by", self.edit("status: 👍 Accepted", "status: ↪️ Superseded"))

    def test_superseding_with_other_changes_refused(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNotNone(
            self.write(adr("↪️ Superseded", extra="superseded-by: 0002\n", body="Chosen option: Postgres."))
        )

    def test_superseded_is_final(self):
        self.put(adr("↪️ Superseded", extra="superseded-by: 0002\n"))
        self.assertIsNotNone(self.edit("superseded-by: 0002", "superseded-by: 0003"))
        self.assertIsNotNone(self.edit("status: ↪️ Superseded", "status: 👍 Accepted"))

    def test_rewriting_accepted_unchanged_allowed(self):
        self.put(adr("👍 Accepted"))
        self.assertIsNone(self.write(adr("👍 Accepted")))

    def test_new_draft_with_supersedes_allowed(self):
        self.assertIsNone(self.write(adr(extra="supersedes: 0001\n")))

    def test_file_without_status_left_alone(self):
        readme = os.path.join(self.tmp.name, "docs", "adrs", "README.md")
        self.assertIsNone(self.write("# Decisions\n", path=readme))

    def test_spec_statuses_do_not_apply(self):
        self.put(adr())
        self.assertIn("Ready to build", self.edit("status: 📝 Draft", "status: 🟢 Ready to build"))

    def test_nested_docs_adrs_ignored(self):
        nested = os.path.join(self.tmp.name, "evals", "case", "docs", "adrs", "0001-x.md")
        self.assertIsNone(self.write(adr("👍 Accepted"), path=nested))


class Emoji(Workspace):
    """Every status carries its emoji; documents written before that move over in one edit."""

    def test_plain_word_refused_with_the_value_to_write(self):
        self.assertIn("`📝 Draft`", self.write(spec("Draft")))

    def test_wrong_emoji_refused(self):
        self.put(spec())
        self.assertIn("`👍 Accepted`", self.edit("status: 📝 Draft", "status: ✅ Accepted"))

    def test_emoji_without_space_refused(self):
        self.assertIsNotNone(self.write(spec("📝Draft")))

    def test_variation_selector_optional(self):
        self.assertEqual(status_check.status_of("---\nstatus: \u21aa Superseded\n---\n"), "↪️ Superseded")
        self.assertEqual(status_check.status_of("---\nstatus: ✅\ufe0f Built\n---\n"), "✅ Built")

    def test_old_plain_status_moves_over(self):
        self.put(spec("Accepted"))
        self.assertIsNone(self.edit("status: Accepted", "status: 👍 Accepted"))

    def test_old_plain_status_keeps_its_rules(self):
        self.put(spec("Accepted"))
        self.assertIn("Draft", self.write(spec("👍 Accepted", rule="The system SHALL do Y.")))
        self.assertIsNone(self.edit("status: Accepted", "status: 📝 Draft"))

    def test_old_plain_status_must_move_over_when_edited(self):
        self.put(spec("Draft"))
        self.assertIn("`📝 Draft`", self.edit("do X", "do Y"))
        self.assertIsNone(self.write(spec(rule="The system SHALL do Y.")))

    def test_old_plain_word_with_wrong_case_is_not_a_status(self):
        self.put(spec("draft"))
        self.assertIsNone(self.edit("do X", "do Y"))

    def test_lifecycle_status_reads_old_and_new(self):
        statuses = status_check.STATUSES
        self.assertEqual(status_check.lifecycle_status("---\nstatus: Built\n---\n", statuses), "✅ Built")
        self.assertEqual(status_check.lifecycle_status("---\nstatus: ✅ Built\n---\n", statuses), "✅ Built")
        self.assertEqual(status_check.lifecycle_status("---\nstatus: Done\n---\n", statuses), "Done")
        self.assertEqual(status_check.lifecycle_status("---\nstatus: Accepted\n---\n", statuses), "Accepted")

    def test_new_spec_refusal_quotes_what_was_written(self):
        self.assertIn("'Accepted'", self.write(spec("Accepted")))

    def test_lookalike_space_shown(self):
        self.assertIn("\\xa0", self.write(spec("📝\u00a0Draft")))


class AdrEmoji(AdrWorkspace):
    def test_decided_adr_moves_over(self):
        for status in ("Accepted", "Rejected"):
            self.put(adr(status))
            self.assertIsNone(self.edit(f"status: {status}", f"status: {status_check.WORDS[status]}"), status)

    def test_superseded_adr_moves_over(self):
        self.put(adr("Superseded", extra="superseded-by: 0002\n"))
        self.assertIsNone(self.edit("status: Superseded", "status: ↪️ Superseded"))

    def test_moving_over_changes_nothing_else(self):
        self.put(adr("Accepted"))
        self.assertIsNotNone(self.write(adr("👍 Accepted", body="Chosen option: Postgres.")))

    def test_moving_over_adds_nothing_else_to_the_status_line(self):
        self.put(adr("Accepted"))
        self.assertIsNotNone(self.edit("status: Accepted", "status: 👍 Accepted # reopened"))

    def test_moving_over_without_variation_selector(self):
        self.put(adr("Superseded", extra="superseded-by: 0002\n"))
        self.assertIsNone(self.edit("status: Superseded", "status: \u21aa Superseded"))

    def test_moving_over_may_respace_and_quote(self):
        self.put(adr("Accepted  # signed off"))
        self.assertIsNone(self.edit("status: Accepted  # signed off", 'status: "👍 Accepted" # signed off'))

    def test_body_edit_of_old_decided_adr_refused_as_decided(self):
        self.put(adr("Accepted"))
        self.assertIn("never edited", self.edit("fast enough", "fast and cheap enough"))

    def test_body_edit_of_old_accepted_spec_must_return_to_draft(self):
        self.put(adr())
        os.remove(self.path)
        self.path = os.path.join(self.tmp.name, "docs", "specs", "thing.spec.md")
        self.put(spec("Accepted"))
        self.assertIn("back to `📝 Draft`", self.edit("do X", "do Y"))

    def test_adding_the_variation_selector_allowed(self):
        self.put(adr("\u21aa Superseded", extra="superseded-by: 0002\n"))
        self.assertIsNone(self.edit("status: \u21aa Superseded", "status: ↪️ Superseded"))

    def test_number_or_dash_is_not_an_emoji(self):
        self.assertIsNone(status_check.meant("202 Accepted", status_check.ADR_STATUSES))
        self.assertIsNone(status_check.meant("- Draft", status_check.ADR_STATUSES))
        self.assertEqual(status_check.meant("📝Draft", status_check.ADR_STATUSES), "📝 Draft")

    def test_wrong_emoji_on_disk_still_decided(self):
        self.put(adr("✅ Accepted"))
        self.assertIn("never edited", self.edit("fast enough", "fast and cheap enough"))
        self.assertIsNotNone(self.edit("status: ✅ Accepted", "status: 📝 Draft"))

    def test_moving_over_keeps_the_word(self):
        self.put(adr("Accepted"))
        self.assertIsNotNone(self.edit("status: Accepted", "status: ❌ Rejected"))

    def test_old_replacement_can_supersede(self):
        self.put(adr("👍 Accepted"))
        self.put_replacement("Accepted")
        self.assertIsNone(self.edit("status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))

    def test_new_adr_plain_draft_refused(self):
        self.assertIn("`📝 Draft`", self.write(adr("Draft")))

    put_replacement = Adr.put_replacement


def plan(status="📝 Draft", specs=None, adrs="None.", questions="None.", decisions="None."):
    if specs is None:
        specs = "- [Thing](../specs/thing.spec.md)\n  - Requirement: X"
    return (
        "---\n"
        "# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.\n"
        f"status: {status}\n"
        "---\n\n# Thing release\n\n"
        f"## Specs\n\n{specs}\n\n## ADRs\n\n{adrs}\n\n## Decisions\n\n{decisions}\n\n"
        f"## Plan\n\nDo the thing.\n\n## Open questions\n\n{questions}\n"
    )


class PlanWorkspace(Workspace):
    def setUp(self):
        super().setUp()
        self.spec_path = self.path
        self.path = os.path.join(self.tmp.name, "docs", "plans", "2026-10-29-thing-release.md")
        self.put_at(self.spec_path, spec("👍 Accepted"))

    def put_at(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def ready(self, **parts):
        """Put a Draft plan, then set it Ready to build on its own."""
        self.put(plan(**parts))
        return self.edit("status: 📝 Draft", "status: 🟢 Ready to build")


class Plan(PlanWorkspace):
    def test_new_draft_allowed(self):
        self.assertIsNone(self.write(plan()))

    def test_new_ready_refused(self):
        self.assertIn("Draft", self.write(plan("🟢 Ready to build")))

    def test_new_plan_with_another_kind_of_status_refused(self):
        self.assertIn("Draft", self.write(plan("👍 Accepted")))

    def test_losing_status_refused(self):
        self.put(plan())
        self.assertIn("status", self.edit("status: 📝 Draft\n", ""))

    def test_draft_edit_allowed(self):
        self.put(plan())
        self.assertIsNone(self.edit("Do the thing.", "Do the thing well."))

    def test_draft_to_ready_allowed(self):
        self.assertIsNone(self.ready())

    def test_template_frontmatter_with_comment_line_read(self):
        with open(os.path.join(HERE, "..", "skills", "plan", "assets", "template.md"), encoding="utf-8") as f:
            self.assertEqual(status_check.status_of(f.read()), "📝 Draft")

    def test_ready_with_other_changes_refused(self):
        self.put(plan())
        reason = self.write(plan("🟢 Ready to build").replace("Do the thing.", "Do it."))
        self.assertIn("on its own", reason)

    def test_ready_with_open_questions_refused(self):
        self.assertIn("open questions", self.ready(questions="- Which queue?"))

    def test_ready_without_open_questions_section_refused(self):
        self.put(plan().replace("## Open questions\n\nNone.\n", ""))
        self.assertIn("open questions", self.edit("status: 📝 Draft", "status: 🟢 Ready to build"))

    def test_ready_needs_the_spec_to_exist(self):
        reason = self.ready(specs="- [Gone](../specs/gone.spec.md)\n  - Requirement: X")
        self.assertIn("gone.spec.md", reason)

    def test_ready_needs_the_spec_settled(self):
        self.put_at(self.spec_path, spec())
        self.assertIn("Draft", self.ready())

    def test_ready_refused_on_a_spec_with_a_status_from_before(self):
        for status in ("🟢 Ready to build", "✅ Built"):
            self.put_at(self.spec_path, spec(status))
            self.assertIn("`👍 Accepted`", self.ready())

    def test_ready_needs_each_requirement_in_its_spec(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - Requirement: Y")
        self.assertIn("Requirement: Y", reason)

    def test_ready_needs_a_requirement_under_each_spec(self):
        self.assertIn("requirement", self.ready(specs="- [Thing](../specs/thing.spec.md)"))

    def test_ready_needs_something_to_build(self):
        self.assertIn("nothing", self.ready(specs="None."))

    def test_ready_on_an_accepted_adr_alone_allowed(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        self.assertIsNone(self.ready(specs="None.", adrs="- [0003 History](../adrs/0003-history.md)"))

    def test_ready_needs_each_adr_accepted(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr())
        reason = self.ready(adrs="- [0003 History](../adrs/0003-history.md)")
        self.assertIn("0003-history.md", reason)

    def test_ready_needs_each_adr_to_exist(self):
        self.assertIn("0009-gone.md", self.ready(adrs="- [0009 Gone](../adrs/0009-gone.md)"))

    def test_ready_refused_when_another_plan_names_the_requirement(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan())
        self.assertIn("2026-10-01-earlier.md", self.ready())

    def test_a_built_plan_does_not_block_the_requirement(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan("✅ Built"))
        self.assertIsNone(self.ready())

    def test_another_plan_for_another_requirement_allowed(self):
        self.put_at(self.spec_path, spec("👍 Accepted", rule="The system SHALL do X.\n\n### Requirement: Y\n\nThe system SHALL do Y."))
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan(specs="- [Thing](../specs/thing.spec.md)\n  - Requirement: Y"))
        self.assertIsNone(self.ready())

    def test_ready_refused_when_an_adr_line_cannot_be_read(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr())
        reason = self.ready(adrs="- ADR [0003 History](../adrs/0003-history.md)")
        self.assertIn("cannot read", reason)

    def test_ready_refused_when_a_spec_line_cannot_be_read(self):
        specs = "- [Thing](../specs/thing.spec.md)\n  - Requirement: X\n- Spec B: [B](../specs/b.spec.md)\n  - Requirement: B1"
        self.assertIn("cannot read", self.ready(specs=specs))

    def test_ready_refused_when_specs_holds_prose_beside_a_good_adr(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        reason = self.ready(specs="The thing spec, its X part.", adrs="- [0003 History](../adrs/0003-history.md)")
        self.assertIn("cannot read", reason)

    def test_ready_refused_for_a_requirement_before_any_spec(self):
        self.assertIn("cannot read", self.ready(specs="  - Requirement: X"))

    def test_footnote_marks_and_definitions_in_references_are_ignored(self):
        specs = ("- [Thing](../specs/thing.spec.md)[^1]\n  - Requirement: X\n\n"
                 "[^1]: A thing is what the\n    product makes.")
        self.assertIsNone(self.ready(specs=specs))

    def test_template_comments_in_references_are_ignored(self):
        specs = "<!-- Each spec this work builds,\n     over two lines. -->\n- [Thing](../specs/thing.spec.md)\n  - Requirement: X"
        self.assertIsNone(self.ready(specs=specs))

    def test_ready_refused_when_a_spec_link_is_not_a_spec(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan("🟢 Ready to build", specs="None.", adrs="None."))
        reason = self.ready(specs="- [Earlier](2026-10-01-earlier.md)\n  - Requirement: X")
        self.assertIn("not a spec", reason)

    def test_ready_refused_when_an_adr_link_is_not_an_adr(self):
        reason = self.ready(adrs="- [Thing](../specs/thing.spec.md)")
        self.assertIn("not an ADR", reason)

    def test_spec_without_status_named_plainly(self):
        self.put_at(self.spec_path, "# Thing\n")
        self.assertIn("has no status", self.ready())

    def test_setting_built_refused(self):
        self.put(plan("🟢 Ready to build"))
        self.assertIn("build step", self.edit("status: 🟢 Ready to build", "status: ✅ Built"))

    def test_changing_ready_plan_without_draft_refused(self):
        self.put(plan("🟢 Ready to build"))
        self.assertIn("Draft", self.edit("Do the thing.", "Do it."))

    def test_changing_ready_plan_back_to_draft_allowed(self):
        self.put(plan("🟢 Ready to build"))
        self.assertIsNone(self.write(plan().replace("Do the thing.", "Do it.")))

    def test_plain_word_status_refused_with_value_to_write(self):
        self.assertIn("📝 Draft", self.write(plan("Draft")))

    def test_file_in_a_subfolder_of_plans_ignored(self):
        path = os.path.join(self.tmp.name, "docs", "plans", "old", "x.md")
        self.assertIsNone(self.write(plan("🟢 Ready to build"), path=path))

    def test_file_without_status_left_alone(self):
        path = os.path.join(self.tmp.name, "docs", "plans", "README.md")
        self.assertIsNone(self.write("# Notes\n", path=path))


class Command(Workspace):
    def run_hook(self, payload):
        return subprocess.run(
            [sys.executable, SCRIPT], input=json.dumps(payload), capture_output=True, text=True
        )

    def test_refusal_exits_2_with_reason_on_stderr(self):
        done = self.run_hook({"tool_name": "Write", "tool_input": {"file_path": self.path, "content": spec("👍 Accepted")}})
        self.assertEqual(done.returncode, 2)
        self.assertIn("Draft", done.stderr)

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

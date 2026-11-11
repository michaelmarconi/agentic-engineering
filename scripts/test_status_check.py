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


TODAY = "2026-11-10"  # the hook's "today" in these tests; never read from the clock


def dated(date):
    """The frontmatter's `date:` line, or nothing when date is None (a document from before dates)."""
    return f"date: {date}\n" if date else ""


def head(kind):
    """The frontmatter's `type:` line, or nothing when kind is None (a document from before types)."""
    return f"type: {kind}\n" if kind else ""


def spec(status="📝 Draft", questions="None.", rule="The system SHALL do X.", kind="Spec", date=TODAY):
    return (
        "---\n"
        "# Change status only through /agentic:spec and /agentic:build.\n"
        f"{head(kind)}"
        f"status: {status}\n"
        f"{dated(date)}"
        "---\n\n# Thing\n\n## Story\n\nWhen a, someone wants to b, so they can c.\n\n"
        "## In scope\n\n- a\n\n## Out of scope\n\n- b\n\n"
        f"## Requirements\n\n### 1. X\n\n{rule}\n\n#### How we'll check\n\nTest.\n\n"
        f"## Constraints\n\n- None.\n\n## Open questions\n\n{questions}\n"
    )


def old_spec(status="👍 Accepted"):
    """A spec in the layout from before numbered requirements."""
    return (
        "---\n"
        f"status: {status}\n"
        "---\n\n# Thing\n\n## Problem\n\nP\n\n## Goal\n\nG\n\n## Scope\n\nIn:\n- a\n\n"
        "## Requirements\n\n### Requirement: X\n\nThe system SHALL do X.\n\n"
        "## Constraints\n\n- None.\n\n## Open questions\n\nNone.\n"
    )


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        today = mock.patch.object(status_check, "today", return_value=TODAY)
        today.start()
        self.addCleanup(today.stop)
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

    def test_accepting_an_old_layout_spec_refused(self):
        self.put(old_spec("📝 Draft"))
        reason = self.edit("status: 📝 Draft", "status: 👍 Accepted")
        self.assertIn("written for an earlier version of the agentic plugin; rework it with /spec", reason)

    def test_accepting_a_spec_without_a_numbered_requirement_refused(self):
        self.put(spec().replace("### 1. X", "### X"))
        self.assertIn("at least one requirement", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

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


ADR_BODY = "Chosen: keep sessions in Redis, because it is fast enough."


def adr(status="📝 Draft", extra="", body=ADR_BODY,
        questions="None.", background="B", detail="None.", kind="ADR", date=TODAY):
    return (
        "---\n"
        f"{head(kind)}"
        f"status: {status}\n"
        f"{dated(date)}"
        f"{extra}"
        "---\n\n# Store sessions in Redis\n\n## Question\n\nWhere do sessions live?\n\n"
        f"## Decision\n\n{body}\n\n"
        f"## Background\n\n{background}\n\n"
        "## Options\n\n| Option | Outcome | Why |\n| --- | --- | --- |\n"
        "| Redis | Chosen | Fast |\n| Postgres | Rejected | Slower |\n\n"
        "## Consequences\n\n- Good: fast.\n- Bad: one more service.\n\n"
        "## Out of scope\n\nNone.\n\n"
        "## How we'll check\n\nApplies to: code that stores sessions.\n\n1. A test reads a session back.\n\n"
        f"## Open questions\n\n{questions}\n\n"
        f"## Technical detail\n\n{detail}\n"
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

    def test_accepting_with_a_long_plain_part_refused(self):
        self.put(adr(background=" ".join(["word"] * 500)))
        refusal = self.edit("status: 📝 Draft", "status: 👍 Accepted")
        self.assertIn("plain part", refusal)
        self.assertIn("500", refusal)

    def test_technical_detail_is_not_counted(self):
        self.put(adr(detail=" ".join(["word"] * 2000)))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_rejecting_a_long_adr_allowed(self):
        self.put(adr(background=" ".join(["word"] * 500)))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: ❌ Rejected"))

    def test_accepting_without_a_choice_refused(self):
        self.put(adr(body="Not chosen yet; see Open questions."))
        self.assertIn("Chosen:", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_accepting_a_bare_chosen_refused(self):
        self.put(adr(body="Chosen:"))
        self.assertIn("Chosen:", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_accepting_without_a_decision_section_refused(self):
        text = adr().replace("## Decision\n\nChosen: keep sessions in Redis, because it is fast enough.\n\n", "")
        self.put(text)
        self.assertIn("Chosen:", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_bold_chosen_allowed(self):
        self.put(adr(body="**Chosen:** keep sessions in Redis, because it is fast enough."))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_bold_option_name_allowed(self):
        self.put(adr(body="Chosen: **keep sessions in Redis**, because it is fast enough."))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_option_in_code_or_quotes_allowed(self):
        for body in ("Chosen: `Redis`, because it is fast.", 'Chosen: "Redis", because it is fast.'):
            self.put(adr(body=body))
            self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"), body)

    def test_old_layout_draft_told_to_re_lay(self):
        text = adr().replace("## Decision\n\nChosen: keep sessions in Redis,", "## Decision Outcome\n\nChosen option: Redis,")
        self.put(text)
        self.assertIn("layout", self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_rejecting_without_a_choice_allowed(self):
        self.put(adr(body="Not chosen yet; see Open questions."))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: ❌ Rejected"))

    def test_adr_plain_words_stop_at_technical_detail(self):
        text = "---\nstatus: 📝 Draft\n---\n\n# One two\n\n## Question\n\nthree?\n\n## Technical detail\n\nfour five\n"
        self.assertEqual(status_check.plain_words(text, "Technical detail"), 4)

    def test_adr_plain_words_skip_a_diagram(self):
        chart = "\n\n```mermaid\nflowchart LR\n  Sender -->|posts| Endpoint --> Queue\n```"
        plain = adr()
        self.assertEqual(status_check.plain_words(adr(body=ADR_BODY + chart), "Technical detail", "Decision"),
                         status_check.plain_words(plain, "Technical detail", "Decision"))

    def test_adr_plain_words_count_a_diagram_outside_decision(self):
        chart = "\n\n```mermaid\nflowchart LR\n  Sender -->|posts| Endpoint --> Queue\n```"
        self.assertGreater(status_check.plain_words(adr(background="B" + chart), "Technical detail", "Decision"),
                           status_check.plain_words(adr(), "Technical detail", "Decision"))

    def test_adr_plain_words_count_other_code_blocks(self):
        code = "\n\n```python\nprint('one two')\n```"
        self.assertGreater(status_check.plain_words(adr(body=ADR_BODY + code), "Technical detail", "Decision"),
                           status_check.plain_words(adr(), "Technical detail", "Decision"))

    def test_an_unclosed_diagram_is_counted(self):
        text = "# One\n\n## Decision\n\n```mermaid\nflowchart LR\n  two three\n"
        self.assertEqual(status_check.plain_words(text, "Technical detail", "Decision"), 7)

    def test_a_diagram_after_another_block_is_skipped(self):
        text = "# One\n\n## Decision\n\n```\ntwo\n```\n```Mermaid\nflowchart LR\n  a --> b\n```\nthree\n"
        self.assertEqual(status_check.plain_words(text, "Technical detail", "Decision"), 4)

    def test_a_diagram_in_a_comment_is_not_counted_twice(self):
        text = "# One\n\n## Decision\n\n<!--\n```mermaid\nx\n```\n-->\ntwo\n"
        self.assertEqual(status_check.plain_words(text, "Technical detail", "Decision"), 3)

    def test_accepting_with_a_diagram_over_the_limit_allowed(self):
        chart = "\n\n```mermaid\nflowchart LR\n" + "".join(f"  n{i} --> n{i + 1}\n" for i in range(100)) + "```"
        self.put(adr(background=" ".join(["word"] * 400), body=ADR_BODY + chart))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_rejecting_with_open_questions_allowed(self):
        self.put(adr(questions="- How long do sessions last?"))
        self.assertIsNone(self.edit("status: 📝 Draft", "status: ❌ Rejected"))

    def test_accepting_with_other_changes_refused(self):
        self.put(adr())
        self.assertIn("on its own", self.write(adr("👍 Accepted", body="Chosen: keep sessions in Postgres.")))

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
        self.assertIsNotNone(self.write(adr("👍 Accepted", body="Chosen: keep sessions in Postgres.")))

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


def plan(status="📝 Draft", specs=None, adrs="None.", questions="None.", decisions="None.", kind="Plan",
         date=TODAY):
    if specs is None:
        specs = "- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)"
    return (
        "---\n"
        "# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.\n"
        f"{head(kind)}"
        f"status: {status}\n"
        f"{dated(date)}"
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
        reason = self.ready(specs="- [Gone](../specs/gone.spec.md)\n  - [X](../specs/thing.spec.md#1-x)")
        self.assertIn("gone.spec.md", reason)

    def test_ready_needs_the_spec_settled(self):
        self.put_at(self.spec_path, spec())
        self.assertIn("Draft", self.ready())

    def test_ready_refused_on_a_spec_with_a_status_from_before(self):
        for status in ("🟢 Ready to build", "✅ Built"):
            self.put_at(self.spec_path, spec(status))
            self.assertIn("`👍 Accepted`", self.ready())

    def test_ready_needs_each_requirement_in_its_spec(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)")
        self.assertIn("no requirement named 'Y'", reason)

    def test_ready_refused_when_the_plan_gives_the_requirement_number(self):
        for line in ("1. X", "1 X", "1) X"):
            reason = self.ready(specs=f"- [Thing](../specs/thing.spec.md)\n  - [{line}](../specs/thing.spec.md#1-x)")
            self.assertIn("name alone", reason, line)

    def test_ready_refused_on_an_old_layout_spec(self):
        self.put_at(self.spec_path, old_spec())
        reason = self.ready()
        self.assertIn("was written for an earlier version of the agentic plugin", reason)
        self.assertIn("rework it with /spec, accept it again, then sign the plan off again", reason)

    def test_a_requirement_heading_outside_requirements_does_not_count(self):
        text = spec("👍 Accepted").replace("## Constraints\n\n- None.", "## Constraints\n\n### 2. Y\n\n- None.")
        self.put_at(self.spec_path, text)
        self.assertIn("no requirement named 'Y'",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))

    def test_a_requirement_heading_without_a_number_does_not_count(self):
        self.put_at(self.spec_path, spec("👍 Accepted", rule="The system SHALL do X.\n\n### Y\n\nThe system SHALL do Y."))
        self.assertIn("no requirement named 'Y'",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))

    def test_a_requirement_heading_in_a_code_block_does_not_count(self):
        self.put_at(self.spec_path, spec("👍 Accepted", rule="The system SHALL do X.\n\n```\n### 2. Y\n```"))
        self.assertIn("no requirement named 'Y'",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))

    def test_a_requirement_heading_in_a_nested_code_block_does_not_count(self):
        rule = "The system SHALL do X.\n\n~~~markdown\n```\n### 9. Fake\n```\n~~~\n\n### 2. Y\n\nThe system SHALL do Y."
        self.put_at(self.spec_path, spec("👍 Accepted", rule=rule))
        self.assertIsNone(self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))
        self.assertIn("no requirement named 'Fake'",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Fake](../specs/thing.spec.md#9-fake)"))

    def test_a_requirement_heading_in_a_comment_does_not_count(self):
        rule = "The system SHALL do X.\n\n<!--\n### 2. Dropped\n### Requirement: Older\n-->"
        self.put_at(self.spec_path, spec("👍 Accepted", rule=rule))
        self.assertIsNone(self.ready())
        self.assertIn("no requirement named 'Dropped'",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Dropped](../specs/thing.spec.md#2-dropped)"))

    def test_a_leftover_old_heading_blocks_only_a_requirement_it_hides(self):
        text = spec("👍 Accepted").replace("## Constraints", "### Requirement: Y\n\nThe system SHALL do Y.\n\n## Constraints")
        self.put_at(self.spec_path, text)
        self.assertIsNone(self.ready())
        self.assertIn("written for an earlier version",
                      self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))

    def test_requirement_heading_spacing_is_ignored(self):
        self.put_at(self.spec_path, spec("👍 Accepted").replace("### 1. X", "###  12.  X  "))
        self.assertIsNone(self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#12--x)"))

    def test_ready_needs_a_requirement_under_each_spec(self):
        self.assertIn("requirement", self.ready(specs="- [Thing](../specs/thing.spec.md)"))

    def test_ready_needs_something_to_build(self):
        self.assertIn("nothing", self.ready(specs="None."))

    def test_ready_on_an_accepted_adr_alone_allowed(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        self.assertIsNone(self.ready(specs="None.", adrs="| ADR | Decision |\n| --- | --- |\n| [0003](../adrs/0003-history.md) | Store sessions in Redis |"))

    def test_ready_needs_each_adr_accepted(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr())
        reason = self.ready(adrs="| ADR | Decision |\n| --- | --- |\n| [0003](../adrs/0003-history.md) | Store sessions in Redis |")
        self.assertIn("0003-history.md", reason)

    def test_ready_needs_each_adr_to_exist(self):
        self.assertIn("0009-gone.md", self.ready(adrs="| ADR | Decision |\n| --- | --- |\n| [0009](../adrs/0009-gone.md) | Gone |"))

    def test_ready_refused_when_another_plan_names_the_requirement(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan())
        self.assertIn("2026-10-01-earlier.md", self.ready())

    def test_a_built_plan_does_not_block_the_requirement(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan("✅ Built"))
        self.assertIsNone(self.ready())

    def test_another_plan_for_another_requirement_allowed(self):
        self.put_at(self.spec_path, spec("👍 Accepted", rule="The system SHALL do X.\n\n### 2. Y\n\nThe system SHALL do Y."))
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan(specs="- [Thing](../specs/thing.spec.md)\n  - [Y](../specs/thing.spec.md#2-y)"))
        self.assertIsNone(self.ready())

    def test_ready_refused_when_an_adr_line_cannot_be_read(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr())
        reason = self.ready(adrs="- ADR [0003 History](../adrs/0003-history.md)")
        self.assertIn("cannot read", reason)

    def test_ready_refused_when_a_spec_line_cannot_be_read(self):
        specs = "- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)\n- Spec B: [B](../specs/b.spec.md)\n  - [B1](../specs/b.spec.md#1-b1)"
        self.assertIn("cannot read", self.ready(specs=specs))

    def test_ready_refused_when_specs_holds_prose_beside_a_good_adr(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        reason = self.ready(specs="The thing spec, its X part.", adrs="| ADR | Decision |\n| --- | --- |\n| [0003](../adrs/0003-history.md) | Store sessions in Redis |")
        self.assertIn("cannot read", reason)

    def test_ready_refused_for_a_requirement_before_any_spec(self):
        self.assertIn("cannot read", self.ready(specs="  - [X](../specs/thing.spec.md#1-x)"))

    def test_footnote_marks_and_definitions_in_references_are_ignored(self):
        specs = ("- [Thing](../specs/thing.spec.md)[^1]\n  - [X](../specs/thing.spec.md#1-x)\n\n"
                 "[^1]: A thing is what the\n    product makes.")
        self.assertIsNone(self.ready(specs=specs))

    def test_template_comments_in_references_are_ignored(self):
        specs = "<!-- Each spec this work builds,\n     over two lines. -->\n- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)"
        self.assertIsNone(self.ready(specs=specs))

    def test_ready_refused_when_a_spec_link_is_not_a_spec(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan("🟢 Ready to build", specs="None.", adrs="None."))
        reason = self.ready(specs="- [Earlier](2026-10-01-earlier.md)\n  - [X](../specs/thing.spec.md#1-x)")
        self.assertIn("not a spec", reason)

    def test_ready_refused_when_an_adr_link_is_not_an_adr(self):
        reason = self.ready(adrs="| ADR | Decision |\n| --- | --- |\n| [Thing](../specs/thing.spec.md) | Thing |")
        self.assertIn("not an ADR", reason)

    def test_ready_refused_on_the_old_requirement_lines(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - Requirement: X")
        self.assertIn("layout plans had before", reason)
        self.assertIn("  - [<requirement name>](<path>#<heading anchor>)", reason)

    def test_ready_refused_on_the_old_adr_bullets(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        reason = self.ready(adrs="- [0003 Store sessions in Redis](../adrs/0003-history.md)")
        self.assertIn("layout plans had before", reason)
        self.assertIn("| ADR | Decision |", reason)

    def test_ready_refused_on_a_wrong_anchor_naming_the_right_one(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#2-x)")
        self.assertIn("[X](../specs/thing.spec.md#1-x)", reason)

    def test_ready_refused_on_a_requirement_link_without_an_anchor(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md)")
        self.assertIn("#1-x", reason)

    def test_ready_refused_on_a_requirement_link_to_another_file(self):
        reason = self.ready(specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/other.spec.md#1-x)")
        self.assertIn("[X](../specs/thing.spec.md#1-x)", reason)

    def test_ready_refused_when_the_decision_is_not_the_adr_title(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        reason = self.ready(adrs="| ADR | Decision |\n| --- | --- |\n| [0003](../adrs/0003-history.md) | Use Redis |")
        self.assertIn("'Store sessions in Redis'", reason)

    def test_ready_refused_when_the_adr_link_shows_another_number(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        reason = self.ready(adrs="| ADR | Decision |\n| --- | --- |\n| [0004](../adrs/0003-history.md) | Store sessions in Redis |")
        self.assertIn("[0003]", reason)

    def test_footnote_marks_after_new_layout_links_are_ignored(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        self.assertIsNone(self.ready(
            specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)[^1]\n\n[^1]: A thing.",
            adrs="| ADR | Decision |\n| --- | --- |\n| [0003](../adrs/0003-history.md)[^2] | Store sessions in Redis[^3] |"))

    def test_adr_title_read_past_crlf_frontmatter(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"),
                    "\ufeff" + adr("👍 Accepted").replace("\n", "\r\n"))
        self.assertIsNone(self.ready(adrs="| [0003](../adrs/0003-history.md) | Store sessions in Redis |"))

    def test_an_old_layout_plan_still_blocks_a_shared_requirement(self):
        other = os.path.join(self.tmp.name, "docs", "plans", "2026-10-01-earlier.md")
        self.put_at(other, plan(specs="- [Thing](../specs/thing.spec.md)\n  - Requirement: X"))
        self.assertIn("2026-10-01-earlier.md", self.ready())

    def test_adr_table_without_its_header_still_read(self):
        self.put_at(os.path.join(self.tmp.name, "docs", "adrs", "0003-history.md"), adr("👍 Accepted"))
        self.assertIsNone(self.ready(adrs="| [0003](../adrs/0003-history.md) | Store sessions in Redis |"))

    def test_two_specs_each_with_their_requirements(self):
        other = os.path.join(self.tmp.name, "docs", "specs", "b.spec.md")
        self.put_at(other, spec("👍 Accepted").replace("### 1. X", "### 1. B one"))
        specs = ("- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)\n"
                 "- [B](../specs/b.spec.md)\n  - [B one](../specs/b.spec.md#1-b-one)")
        self.assertIsNone(self.ready(specs=specs))


    def test_spec_without_status_named_plainly(self):
        self.put_at(self.spec_path, "# Thing\n")
        self.assertIn("has no status", self.ready())

    def test_setting_built_refused(self):
        self.put(plan("🟢 Ready to build"))
        self.assertIn("hand-over", self.edit("status: 🟢 Ready to build", "status: ✅ Built"))

    def test_built_plan_never_changed(self):
        self.put(plan("✅ Built"))
        self.assertIn("frozen", self.edit("Do the thing.", "Do it."))

    def test_built_plan_never_set_back_to_draft(self):
        self.put(plan("✅ Built"))
        self.assertIn("frozen", self.edit("status: ✅ Built", "status: 📝 Draft"))

    def test_built_plan_from_before_the_emoji_gets_it(self):
        self.put(plan("Built"))
        self.assertIsNone(self.edit("status: Built", "status: ✅ Built"))

    def test_built_plan_never_rewritten(self):
        self.put(plan("✅ Built"))
        self.assertIn("frozen", self.write(plan("📝 Draft")))

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


def record(status="📝 Draft", hypothesis="The library reads our TIFF files.", answer_if="All 20 open.",
           scope="None.", steps="Opens each file once.", risks="None.",
           experiment="Opens each file. Runs: 1.\nCommand: `python3 check.py`", answer="", questions="None.",
           code="```python\n# file: check.py\nprint('ok')\n```", runs="", kind="Spike", date=TODAY):
    return (
        "---\n"
        f"{head(kind)}"
        f"status: {status}\n"
        f"{dated(date)}"
        "---\n\n# The library reads our TIFF files\n\n"
        f"## Hypothesis\n\n{hypothesis}\n\n## Finding\n\n{answer}\n\n## Next steps\n\n\n\n"
        f"## How we'll know\n\n{answer_if}\n\n## Out of scope\n\n{scope}\n\n"
        f"## How the test works\n\n{steps}\n\n## Risks and safeguards\n\n{risks}\n\n"
        "## Results\n\n\n\n## Surprises\n\n\n\n"
        f"## Open questions\n\n{questions}\n\n## Experiment\n\n{experiment}\n\n## Code\n\n{code}\n\n"
        f"## Runs\n\n{runs}"
    )


RUN = "### Run 1\n\n2026-11-04 15:02, Linux, a cloud session, code `a91c03e7b2d4`\n\n```\nok\n```\n"


class SpikeWorkspace(Workspace):
    def setUp(self):
        super().setUp()
        self.path = os.path.join(self.tmp.name, "docs", "spikes", "2026-11-04-tiff-files-open.md")

    def move(self, old, new):
        return self.edit(f"status: {old}", f"status: {new}")


class Spike(SpikeWorkspace):
    def test_new_draft_allowed(self):
        self.assertIsNone(self.write(record()))

    def test_new_record_with_runs_refused(self):
        self.assertIn("Runs", self.write(record(runs=RUN)))

    def test_new_record_not_draft_refused(self):
        for status in ("🟢 Ready to run", "💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            self.assertIn("📝 Draft", self.write(record(status)), status)

    def test_template_comment_in_runs_is_empty(self):
        self.assertIsNone(self.write(record(runs="<!-- Only the run script writes here. -->\n")))

    def test_draft_edits_allowed(self):
        self.put(record())
        self.assertIsNone(self.edit("All 20 open.", "All 20 open, with the right page count."))

    def test_ready_on_its_own_allowed(self):
        self.put(record())
        self.assertIsNone(self.move("📝 Draft", "🟢 Ready to run"))

    def test_ready_with_open_questions_refused(self):
        self.put(record(questions="- Which scanner?"))
        self.assertIn("open questions", self.move("📝 Draft", "🟢 Ready to run"))

    def test_ready_without_open_questions_section_refused(self):
        self.put(record().replace("## Open questions", "## Notes"))
        self.assertIn("no Open questions section", self.move("📝 Draft", "🟢 Ready to run"))

    def test_ready_with_other_changes_refused(self):
        self.put(record())
        self.assertIn("on its own", self.write(record("🟢 Ready to run", answer_if="All 19 open.")))

    def test_draft_cannot_be_finished(self):
        self.put(record())
        for status in ("💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            self.assertIn("cannot go from", self.move("📝 Draft", status), status)

    def test_fixed_parts_of_ready_record_refused(self):
        for part in ("hypothesis", "answer_if", "scope", "steps", "risks", "experiment"):
            self.put(record("🟢 Ready to run"))
            changed = record("🟢 Ready to run", **{part: "Something else."})
            self.assertIn("fixed", self.write(changed), part)

    def test_fixed_parts_change_with_return_to_draft_allowed(self):
        self.put(record("🟢 Ready to run"))
        self.assertIsNone(self.write(record(answer_if="All 19 open.")))

    def test_return_to_draft_after_a_run_refused(self):
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIn("after the first run", self.move("🟢 Ready to run", "📝 Draft"))

    def test_code_and_verdict_of_ready_record_allowed(self):
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIsNone(self.edit("print('ok')", "print('fixed')"))
        self.assertIsNone(self.write(record("🟢 Ready to run", answer="No.", runs=RUN)))

    def test_changing_runs_refused_at_every_status(self):
        for status in ("📝 Draft", "🟢 Ready to run"):
            self.put(record(status))
            self.assertIn("run script", self.write(record(status, runs=RUN)), status)
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIn("run script", self.write(record("🟢 Ready to run", runs=RUN.replace("ok", "fine"))))
        self.assertIn("run script", self.write(record("🟢 Ready to run")))

    def test_headings_inside_run_output_stay_in_runs(self):
        run = "### Run 1\n\nLinux, exit code 0\n\n````\n## Notes\n\nfine\n````\n"
        self.put(record("🟢 Ready to run", runs=run))
        self.assertIn("run script", self.edit("fine", "great"))

    def test_a_comment_mark_inside_run_output_still_counts_as_a_run(self):
        runs = ("### Run 1\n\nLinux\n\n```\n<!-- start\n```\n\n### Run 2\n\nLinux, exit code 0\n\n```\nok\n```\n\n"
                "### Run 3\n\nLinux\n\n```\nend -->\n```\n")
        self.put(record("🟢 Ready to run", runs=runs))
        self.assertIn("run script", self.edit("exit code 0", "exit code 1"))

    def test_a_comment_holding_a_fence_in_runs_is_empty(self):
        self.assertIsNone(self.write(record(runs="<!-- For example:\n```\n### Run 1\n```\n-->\n")))

    def test_an_unclosed_comment_mark_in_runs_is_text(self):
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIn("run script", self.write(record("🟢 Ready to run", runs=RUN + "\n<!--\n")))

    def test_several_comments_on_a_line_are_all_dropped(self):
        for runs, expected in (("a <!-- x --> b <!-- y --> c", "a  b  c"), ("<!-- a\nb --> c <!-- d --> e", "c  e"),
                               ("xx <!-- a --> <!-- b --> tail", "xx   tail")):
            self.assertEqual(status_check.runs(record(runs=runs)), expected, runs)

    def test_cutting_a_comment_never_makes_a_new_one(self):
        self.assertEqual(status_check.runs(record(runs="<!<!---->---->")), "<!---->")
        self.put(record("🟢 Ready to run", runs="<!<!---->-- Run 1 passed -->\n"))
        self.assertIn("run script", self.edit("passed", "FAILED"))

    def test_cutting_a_comment_never_makes_a_fence(self):
        self.assertEqual(status_check.runs(record(runs="<!---->```<!---->")), "```")
        runs = "<!---->```\n\n```\n<!--\n### Run 1\npassed\n-->\n```\n"
        self.put(record("🟢 Ready to run", runs=runs))
        self.assertIn("run script", self.edit("passed", "FAILED"))

    def test_a_heading_inside_a_comment_never_ends_runs(self):
        self.put(record("🟢 Ready to run", runs="<!--\n## x\n-->\n" + RUN))
        self.assertIn("run script", self.edit("```\nok\n```", "```\nfine\n```"))

    def test_confirmed_or_refuted_needs_a_run_that_ran(self):
        not_run = "### Run 1\n\n2026-11-04 15:02, Linux, a cloud session, code `a91c03e7b2d4`, did not run\n\n```\nx\n```\n"
        for status in ("💡 Confirmed", "🚫 Refuted"):
            self.put(record("🟢 Ready to run", runs=not_run))
            self.assertIn("no runs", self.move("🟢 Ready to run", status), status)
        self.put(record("🟢 Ready to run", answer="Not settled: the key was not set.", runs=not_run))
        self.assertIsNone(self.move("🟢 Ready to run", "❔ Not settled"))

    def test_confirmed_or_refuted_needs_a_run(self):
        for status in ("💡 Confirmed", "🚫 Refuted"):
            self.put(record("🟢 Ready to run"))
            self.assertIn("no runs", self.move("🟢 Ready to run", status), status)
        self.put(record("🟢 Ready to run", answer="Not settled: the tool would not install."))
        self.assertIsNone(self.move("🟢 Ready to run", "❔ Not settled"))

    def test_plain_part_over_the_limit_cannot_move_forward(self):
        long = " ".join(["word"] * 600)
        self.put(record(steps=long))
        self.assertIn("plain part", self.move("📝 Draft", "🟢 Ready to run"))
        for status in ("💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            word = status.split(" ", 1)[1]
            self.put(record("🟢 Ready to run", steps=long, answer=f"{word}: it opens.", runs=RUN))
            self.assertIn("plain part", self.move("🟢 Ready to run", status), status)

    def test_a_long_draft_is_allowed(self):
        self.assertIsNone(self.write(record(steps=" ".join(["word"] * 900))))

    def test_experiment_comments_and_table_rules_are_not_counted(self):
        text = record(steps="| a | b |\n|---|---|\n| 1 | 2 |\n<!-- " + "x " * 900 + "-->",
                      experiment=" ".join(["word"] * 900))
        self.assertEqual(status_check.plain_words(text), status_check.plain_words(record(steps="| a | b |\n| 1 | 2 |")))
        self.assertLess(status_check.plain_words(text), 100)

    def test_plain_words_counts_up_to_experiment(self):
        text = "---\nstatus: 📝 Draft\n---\n\n# One two\n\n## Hypothesis\n\nthree four.\n\n## Experiment\n\nfive six\n"
        self.assertEqual(status_check.plain_words(text), 5)
        self.assertEqual(status_check.plain_words(text.replace("## Experiment", "## Notes")), 8)

    def test_plain_words_count_a_diagram(self):
        chart = "\n\n```mermaid\nstateDiagram-v2\n  Waiting --> Open\n```"
        self.assertGreater(status_check.plain_words(record(steps="Opens each file once." + chart)),
                           status_check.plain_words(record()))

    def test_a_heading_in_a_comment_does_not_end_the_plain_part(self):
        text = "# One\n\n<!--\n## Experiment\n-->\n\ntwo three\n\n## Experiment\n\nfour\n"
        self.assertEqual(status_check.plain_words(text), 3)

    def test_finish_on_its_own_allowed(self):
        for status in ("💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            word = status.split(" ", 1)[1]
            self.put(record("🟢 Ready to run", answer=f"{word}: the library opens 20 of 20 files.", runs=RUN))
            self.assertIsNone(self.move("🟢 Ready to run", status), status)

    def test_finding_opens_with_the_status_it_is_given(self):
        self.put(record("🟢 Ready to run", answer="Refuted: the library opens 3 of 20 files.", runs=RUN))
        refusal = self.move("🟢 Ready to run", "💡 Confirmed")
        self.assertIn("Finding", refusal)
        self.assertIn("Confirmed", refusal)
        self.assertIsNone(self.move("🟢 Ready to run", "🚫 Refuted"))

    def test_finding_status_word_may_be_bold_and_any_case(self):
        self.put(record("🟢 Ready to run", answer="**Not settled.** The tool would not install.", runs=RUN))
        self.assertIsNone(self.move("🟢 Ready to run", "❔ Not settled"))

    def test_an_empty_finding_cannot_finish(self):
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIn("Finding", self.move("🟢 Ready to run", "🚫 Refuted"))

    def test_a_long_verdict_is_told_to_shorten_the_verdict_sections(self):
        long = " ".join(["word"] * 600)
        self.put(record("🟢 Ready to run", answer="Confirmed: " + long, runs=RUN))
        refusal = self.move("🟢 Ready to run", "💡 Confirmed")
        self.assertIn("Finding, Next steps, Results or Surprises", refusal)
        self.assertNotIn("into Experiment", refusal)

    def test_finish_with_other_changes_refused(self):
        self.put(record("🟢 Ready to run", runs=RUN))
        self.assertIn("on its own", self.write(record("💡 Confirmed", answer="Confirmed: all 20 open.", runs=RUN)))

    def test_finish_with_open_questions_refused(self):
        self.put(record("🟢 Ready to run", questions="- Is one run enough?", runs=RUN))
        self.assertIn("open questions", self.move("🟢 Ready to run", "💡 Confirmed"))

    def test_finished_record_never_changed(self):
        for status in ("💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            self.put(record(status, answer="No.", runs=RUN))
            self.assertIn("never changed", self.edit("No.", "Yes."), status)
            self.assertIn("never changed", self.move(status, "📝 Draft"), status)

    def test_finished_records_cannot_swap(self):
        self.put(record("💡 Confirmed", answer="No.", runs=RUN))
        self.assertIn("never changed", self.move("💡 Confirmed", "🚫 Refuted"))

    def test_status_word_without_emoji_refused(self):
        self.assertIn("`📝 Draft`", self.write(record("Draft")))
        self.put(record())
        self.assertIn("`🟢 Ready to run`", self.move("📝 Draft", "Ready to run"))

    def test_record_losing_its_status_refused(self):
        self.put(record())
        self.assertIn("needs `status:`", self.write(record().replace("status: 📝 Draft\n", "")))

    def test_other_files_in_spikes_ignored(self):
        self.assertIsNone(self.write("# Notes\n", os.path.join(self.tmp.name, "docs", "spikes", "README.txt")))
        nested = os.path.join(self.tmp.name, "docs", "spikes", "old", "x.md")
        self.assertIsNone(self.write(record("💡 Confirmed", runs=RUN), nested))

    def test_plan_status_on_a_record_refused(self):
        self.put(record())
        self.assertIsNotNone(self.move("📝 Draft", "🟢 Ready to build"))



BRIEF = "---\ntype: Brief\n---\n\n# Ledger\n\nA ledger for small shops.\n\n## Problem\n\nP\n"


class DocumentType(Workspace):
    """Every lifecycle document names its type in its frontmatter; the brief is checked too."""

    def at(self, *parts):
        self.path = os.path.join(self.tmp.name, *parts)

    def test_each_kind_with_its_type_allowed(self):
        for parts, text in [
            (("docs", "specs", "thing.spec.md"), spec()),
            (("docs", "adrs", "0001-session-data-storage.md"), adr()),
            (("docs", "plans", "2026-10-29-thing-release.md"), plan(specs="None.")),
            (("docs", "spikes", "2026-11-04-tiff-files-open.md"), record()),
            (("docs", "brief.md"), BRIEF),
        ]:
            self.at(*parts)
            self.assertIsNone(self.write(text), parts)

    def test_new_document_without_type_refused(self):
        for parts, text, value in [
            (("docs", "specs", "thing.spec.md"), spec(kind=None), "Spec"),
            (("docs", "adrs", "0001-session-data-storage.md"), adr(kind=None), "ADR"),
            (("docs", "plans", "2026-10-29-thing-release.md"), plan(specs="None.", kind=None), "Plan"),
            (("docs", "spikes", "2026-11-04-tiff-files-open.md"), record(kind=None), "Spike"),
            (("docs", "brief.md"), BRIEF.replace("type: Brief\n", ""), "Brief"),
        ]:
            self.at(*parts)
            reason = self.write(text)
            self.assertIsNotNone(reason, parts)
            self.assertIn(f"type: {value}", reason, parts)

    def test_new_brief_without_frontmatter_refused(self):
        self.at("docs", "brief.md")
        self.assertIn("type: Brief", self.write("# Ledger\n\nA ledger.\n"))

    def test_wrong_type_refused(self):
        self.assertIn("type: Spec", self.write(spec(kind="ADR")))
        self.assertIn("type: Spec", self.write(spec(kind="spec")))

    def test_wrong_type_refused_on_an_existing_document(self):
        self.put(spec(kind=None))
        reason = self.edit("status: 📝 Draft", "type: Plan\nstatus: 📝 Draft")
        self.assertIn("type: Spec", reason)

    def test_two_type_lines_refused(self):
        self.assertIn("more than one `type:`", self.write(spec().replace("type: Spec\n", "type: Spec\ntype: Spec\n")))

    def test_existing_document_without_type_may_be_edited(self):
        # Documents from before types gain one on their next edit; the skill adds it, not the hook.
        self.put(spec(kind=None))
        self.assertIsNone(self.edit("do X.", "do Y."))

    def test_brief_from_before_types_may_be_edited(self):
        self.at("docs", "brief.md")
        self.put("# Ledger\n\nA ledger.\n")
        self.assertIsNone(self.edit("A ledger.", "A ledger for shops."))

    def test_other_files_without_status_ignored(self):
        self.at("docs", "plans", "notes.md")
        self.assertIsNone(self.write("# Notes\n"))
        self.at("docs", "briefing.md")
        self.assertIsNone(self.write("# Notes\n"))

    def test_adding_type_counts_as_no_change_when_accepting(self):
        self.put(spec(kind=None))
        self.assertIsNone(self.edit("status: 📝 Draft", "type: Spec\nstatus: 👍 Accepted"))

    def test_adding_type_to_an_accepted_spec_needs_no_return_to_draft(self):
        self.put(spec("👍 Accepted", kind=None))
        self.assertIsNone(self.edit("status: 👍 Accepted", "type: Spec\nstatus: 👍 Accepted"))

    def test_adding_type_to_decided_adrs_allowed(self):
        self.at("docs", "adrs", "0001-session-data-storage.md")
        for status in ("👍 Accepted", "❌ Rejected", "↪️ Superseded"):
            self.put(adr(status, kind=None))
            self.assertIsNone(self.edit(f"status: {status}", f"type: ADR\nstatus: {status}"), status)

    def test_old_accepted_adr_superseded_while_gaining_type(self):
        self.at("docs", "adrs", "0001-session-data-storage.md")
        self.put(adr("👍 Accepted", kind=None))
        replacement = os.path.join(self.tmp.name, "docs", "adrs", "0002-sessions-in-postgres.md")
        with open(replacement, "w") as f:
            f.write(adr("👍 Accepted", extra="supersedes: 0001\n"))
        reason = self.edit("status: 👍 Accepted", "type: ADR\nstatus: ↪️ Superseded\nsuperseded-by: 0002")
        self.assertIsNone(reason)

    def test_adding_type_to_a_built_plan_allowed(self):
        self.at("docs", "plans", "2026-10-29-thing-release.md")
        self.put(plan("✅ Built", kind=None))
        self.assertIsNone(self.edit("status: ✅ Built", "type: Plan\nstatus: ✅ Built"))

    def test_adding_type_to_a_finished_spike_record_allowed(self):
        self.at("docs", "spikes", "2026-11-04-tiff-files-open.md")
        for status in ("💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
            self.put(record(status, kind=None, answer=status.split(" ", 1)[1] + ": all 20 open.", runs=RUN))
            self.assertIsNone(self.edit(f"status: {status}", f"type: Spike\nstatus: {status}"), status)

    def test_finished_spike_record_otherwise_unchanged(self):
        self.at("docs", "spikes", "2026-11-04-tiff-files-open.md")
        self.put(record("💡 Confirmed", answer="Confirmed: all 20 open.", runs=RUN))
        self.assertIsNotNone(self.edit("All 20 open.", "All 21 open."))

    def test_removing_type_refused(self):
        self.put(spec("👍 Accepted"))
        self.assertIn("type: Spec", self.edit("type: Spec\nstatus: 👍 Accepted", "status: 👍 Accepted"))

    def test_removing_type_from_a_decided_adr_refused(self):
        self.at("docs", "adrs", "0001-session-data-storage.md")
        self.put(adr("👍 Accepted"))
        self.assertIn("type: ADR", self.edit("type: ADR\nstatus: 👍 Accepted", "status: 👍 Accepted"))

    def test_rewriting_the_brief_without_its_type_refused(self):
        self.at("docs", "brief.md")
        self.put(BRIEF)
        self.assertIn("type: Brief", self.write(BRIEF.replace("type: Brief\n", "")))

    def test_unreadable_brief_refused(self):
        self.at("docs", "brief.md")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as f:
            f.write(b"\xff\xfe not text")
        self.assertIn("could not read the brief", self.write(BRIEF))

    def test_finished_spike_record_status_gains_its_emoji_with_its_type(self):
        # An old record's status may lack its emoji; the hook asks for it, so adding it with
        # `type:` must not count as changing a final record.
        self.at("docs", "spikes", "2026-11-04-tiff-files-open.md")
        self.put(record("Confirmed", kind=None, answer="Confirmed: all 20 open.", runs=RUN))
        self.assertIsNone(self.edit("status: Confirmed", "type: Spike\nstatus: 💡 Confirmed"))

    def test_finished_spike_record_status_comment_not_changed(self):
        self.at("docs", "spikes", "2026-11-04-tiff-files-open.md")
        self.put(record("💡 Confirmed", answer="Confirmed: all 20 open.", runs=RUN))
        self.assertIsNotNone(self.edit("status: 💡 Confirmed", "status: 💡 Confirmed  # done"))

    def test_type_value_with_comment_or_quotes_read(self):
        self.assertIsNone(self.write(spec(kind='"Spec"  # the document type')))


class DateField(Workspace):
    """Every document with a status records in `date:` the day its status last changed."""

    KINDS = {
        "spec": (("docs", "specs", "thing.spec.md"), spec),
        "ADR": (("docs", "adrs", "0001-session-data-storage.md"), adr),
        "plan": (("docs", "plans", "2026-10-29-thing-release.md"), lambda **kw: plan(specs="None.", **kw)),
        "spike record": (("docs", "spikes", "2026-11-04-tiff-files-open.md"), record),
    }

    def at(self, kind):
        parts, make = self.KINDS[kind]
        self.path = os.path.join(self.tmp.name, *parts)
        return make

    def test_new_document_dated_today_allowed(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.assertIsNone(self.write(make()), kind)

    def test_new_document_without_date_refused(self):
        for kind in self.KINDS:
            make = self.at(kind)
            reason = self.write(make(date=None))
            self.assertIsNotNone(reason, kind)
            self.assertIn(f"date: {TODAY}", reason, kind)

    def test_new_document_dated_another_day_refused(self):
        for kind in self.KINDS:
            make = self.at(kind)
            reason = self.write(make(date="2026-11-09"))
            self.assertIsNotNone(reason, kind)
            self.assertIn(f"date: {TODAY}", reason, kind)

    def test_template_placeholder_refused(self):
        self.assertIn("YYYY-MM-DD", self.write(spec(date="<YYYY-MM-DD>")))

    def test_impossible_date_refused(self):
        self.put(spec(date=None))
        self.assertIn("YYYY-MM-DD", self.edit("status: 📝 Draft", "status: 📝 Draft\ndate: 2026-02-30"))

    def test_two_date_lines_refused(self):
        self.assertIn("more than one `date:`", self.write(spec().replace(f"date: {TODAY}\n", f"date: {TODAY}\ndate: {TODAY}\n")))

    def test_status_change_with_an_old_date_refused(self):
        self.put(spec(date="2026-11-01"))
        reason = self.edit("status: 📝 Draft", "status: 👍 Accepted")
        self.assertIsNotNone(reason)
        self.assertIn(f"date: {TODAY}", reason)

    def test_status_change_setting_todays_date_allowed(self):
        # Setting a status on its own may still change the date line with it.
        self.put(spec(date="2026-11-01"))
        self.assertIsNone(self.edit("status: 📝 Draft\ndate: 2026-11-01", f"status: 👍 Accepted\ndate: {TODAY}"))

    def test_status_change_on_a_document_dated_today_allowed(self):
        self.put(spec())
        self.assertIsNone(self.edit("status: 📝 Draft", "status: 👍 Accepted"))

    def test_accepted_spec_back_to_draft_needs_todays_date(self):
        self.put(spec("👍 Accepted", date="2026-11-01"))
        self.assertIn(f"date: {TODAY}", self.edit("status: 👍 Accepted", "status: 📝 Draft"))
        self.assertIsNone(self.edit("status: 👍 Accepted\ndate: 2026-11-01", f"status: 📝 Draft\ndate: {TODAY}"))

    def test_adr_accept_and_reject_set_todays_date(self):
        self.at("ADR")
        for status in ("👍 Accepted", "❌ Rejected"):
            self.put(adr(date="2026-11-01"))
            self.assertIn(f"date: {TODAY}", self.edit("status: 📝 Draft", f"status: {status}"), status)
            self.assertIsNone(
                self.edit("status: 📝 Draft\ndate: 2026-11-01", f"status: {status}\ndate: {TODAY}"), status)

    def test_superseding_sets_todays_date(self):
        self.at("ADR")
        self.put(adr("👍 Accepted", date="2026-10-01"))
        replacement = os.path.join(self.tmp.name, "docs", "adrs", "0002-sessions-in-postgres.md")
        with open(replacement, "w") as f:
            f.write(adr("👍 Accepted", extra="supersedes: 0001\n"))
        self.assertIn(f"date: {TODAY}", self.edit(
            "status: 👍 Accepted\n", "status: ↪️ Superseded\nsuperseded-by: 0002\n"))
        self.assertIsNone(self.edit(
            "status: 👍 Accepted\ndate: 2026-10-01\n",
            f"status: ↪️ Superseded\ndate: {TODAY}\nsuperseded-by: 0002\n"))

    def test_plan_sign_off_sets_todays_date(self):
        self.at("plan")
        self.put(plan(specs="- [Thing](../specs/thing.spec.md)\n  - [X](../specs/thing.spec.md#1-x)", date="2026-11-01"))
        spec_path = os.path.join(self.tmp.name, "docs", "specs", "thing.spec.md")
        os.makedirs(os.path.dirname(spec_path), exist_ok=True)
        with open(spec_path, "w") as f:
            f.write(spec("👍 Accepted"))
        self.assertIn(f"date: {TODAY}", self.edit("status: 📝 Draft", "status: 🟢 Ready to build"))
        self.assertIsNone(self.edit("status: 📝 Draft\ndate: 2026-11-01", f"status: 🟢 Ready to build\ndate: {TODAY}"))

    def test_spike_move_sets_todays_date(self):
        self.at("spike record")
        self.put(record(date="2026-11-01"))
        self.assertIn(f"date: {TODAY}", self.edit("status: 📝 Draft", "status: 🟢 Ready to run"))
        self.assertIsNone(self.edit("status: 📝 Draft\ndate: 2026-11-01", f"status: 🟢 Ready to run\ndate: {TODAY}"))

    def test_date_change_without_status_change_refused(self):
        self.put(spec(date="2026-11-01"))
        self.assertIn("only with a status change", self.edit("date: 2026-11-01", f"date: {TODAY}"))

    def test_removing_the_date_refused(self):
        self.put(spec(date="2026-11-01"))
        self.assertIn("keep", self.edit("date: 2026-11-01\n", ""))

    def test_content_edit_keeps_an_old_date(self):
        self.put(spec(date="2026-11-01"))
        self.assertIsNone(self.edit("do X.", "do Y."))

    def test_document_from_before_dates_may_be_edited(self):
        self.put(spec(date=None))
        self.assertIsNone(self.edit("do X.", "do Y."))

    def test_status_change_on_a_document_from_before_dates_must_add_today(self):
        self.put(spec(date=None))
        self.assertIn(f"date: {TODAY}", self.edit("status: 📝 Draft", "status: 👍 Accepted"))
        self.assertIsNone(self.edit("status: 📝 Draft", f"status: 👍 Accepted\ndate: {TODAY}"))

    def test_any_real_date_may_be_added_to_a_document_from_before_dates(self):
        # A back-fill may use the day of the last status change, as git records it.
        self.put(spec("👍 Accepted", date=None))
        self.assertIsNone(self.edit("status: 👍 Accepted", "status: 👍 Accepted\ndate: 2026-09-14"))

    def test_date_added_to_decided_and_frozen_documents_allowed(self):
        for kind, status, extra in [
            ("ADR", "👍 Accepted", {}), ("ADR", "❌ Rejected", {}), ("ADR", "↪️ Superseded", {}),
            ("plan", "✅ Built", {}),
            ("spike record", "💡 Confirmed", {"answer": "Confirmed: all 20 open.", "runs": RUN}),
        ]:
            make = self.at(kind)
            self.put(make(status=status, date=None, **extra))
            self.assertIsNone(self.edit(f"status: {status}", f"status: {status}\ndate: 2026-09-14"), status)

    def test_a_date_after_today_refused(self):
        self.put(spec("👍 Accepted", date=None))
        self.assertIn("after today", self.edit("status: 👍 Accepted", "status: 👍 Accepted\ndate: 2099-01-01"))

    def test_date_on_a_decided_adr_never_changed(self):
        self.at("ADR")
        self.put(adr("👍 Accepted", date="2026-10-01"))
        self.assertIsNotNone(self.edit("date: 2026-10-01", f"date: {TODAY}"))

    def test_date_with_quotes_or_comment_read(self):
        self.assertIsNone(self.write(spec(date=f'"{TODAY}"  # the day the status last changed')))

    def test_other_files_without_status_ignored(self):
        self.path = os.path.join(self.tmp.name, "docs", "plans", "notes.md")
        self.assertIsNone(self.write("---\ndate: someday\n---\n# Notes\n"))

    def test_brief_needs_no_date(self):
        self.path = os.path.join(self.tmp.name, "docs", "brief.md")
        self.assertIsNone(self.write(BRIEF))


ENTRY = (
    "### 1. Where the daily tariff copy is kept\n\n"
    "The tariff is copied daily, but where is not yet chosen.\n\n"
    "> **Proposed:** Object storage, one file per day.\n"
    ">\n"
    "> **Why:** The copy is read whole once a day and never queried.\n"
)
SECOND = (
    "### 2. Who may read the copy\n\n"
    "Nobody has said who reads it.\n\n"
    "> **Proposed:** Ask the finance team who needs it.\n"
    "> **Why:** Only they know.\n"
)
OLD_ENTRY = "- Where is the copy kept? Proposed: object storage, since it is read whole."


def layout(questions):
    """What status_check.open_questions_problem() says of a spec holding these open questions."""
    return status_check.open_questions_problem(spec(questions=questions))


class OpenQuestionsShape(unittest.TestCase):
    """Each open question is a numbered heading, its context, then a block quote holding one
    Proposed: line and, after it, one Why: line; "None." means nothing is open (ADR 0030)."""

    def test_none_forms_pass(self):
        for body in ["None.", "- None.", "None", "_None._", "<!-- Each question ... -->\n- None."]:
            self.assertIsNone(layout(body), body)

    def test_entries_in_the_layout_pass(self):
        self.assertIsNone(layout(ENTRY))
        self.assertIsNone(layout(ENTRY + "\n" + SECOND))

    def test_quote_without_blank_line_between_proposed_and_why_passes(self):
        self.assertIsNone(layout(SECOND.replace("### 2.", "### 1.")))

    def test_comment_in_the_section_ignored(self):
        self.assertIsNone(layout("<!-- One entry per question. -->\n" + ENTRY))

    def test_footnotes_after_the_entries_ignored(self):
        self.assertIsNone(status_check.open_questions_problem(spec(questions=ENTRY) + "\n[^1]: A source\n    wrapped.\n"))

    def test_no_section_is_not_this_check(self):
        self.assertIsNone(status_check.open_questions_problem(spec().split("\n## Open questions")[0]))

    def test_old_bullet_layout_refused(self):
        problem = layout(OLD_ENTRY)
        self.assertIn("heading", problem)
        self.assertIn("### 1.", problem)

    def test_text_before_the_first_heading_refused(self):
        self.assertIn("heading", layout("Some notes.\n\n" + ENTRY))

    def test_none_beside_entries_refused(self):
        self.assertIn("heading", layout("None.\n\n" + ENTRY))

    def test_heading_without_a_number_refused(self):
        self.assertIn("### 1.", layout(ENTRY.replace("### 1. ", "### ")))

    def test_numbers_out_of_order_refused(self):
        self.assertIn("number 2", layout(ENTRY + "\n" + SECOND.replace("### 2.", "### 3.")))
        self.assertIn("number 1", layout(ENTRY.replace("### 1.", "### 2.")))

    def test_heading_with_no_title_refused(self):
        self.assertIn("title", layout(ENTRY.replace("### 1. Where the daily tariff copy is kept", "### 1.")))

    def test_entry_without_context_refused(self):
        self.assertIn("context", layout(ENTRY.replace("The tariff is copied daily, but where is not yet chosen.\n\n", "")))

    def test_entry_without_a_quote_refused(self):
        bare = ENTRY.replace("> ", "").replace(">\n", "\n")
        self.assertIn("block quote", layout(bare))

    def test_two_quotes_refused(self):
        self.assertIn("one block quote", layout(ENTRY.replace(">\n> **Why:**", "\n> **Why:**")))

    def test_text_after_the_quote_refused(self):
        self.assertIn("last", layout(ENTRY + "\nMore thoughts.\n"))

    def test_missing_proposed_refused(self):
        self.assertIn("Proposed:", layout(ENTRY.replace("**Proposed:**", "Maybe:")))

    def test_missing_why_refused(self):
        self.assertIn("Why:", layout(ENTRY.replace("**Why:**", "Because")))

    def test_why_before_proposed_refused(self):
        swapped = (
            "### 1. Where the copy is kept\n\nNot chosen.\n\n"
            "> **Why:** It is read whole.\n>\n> **Proposed:** Object storage.\n"
        )
        self.assertIn("after", layout(swapped))

    def test_two_proposals_refused(self):
        twice = ENTRY.replace("> **Why:**", "> **Proposed:** Also keep a table.\n>\n> **Why:**")
        self.assertIn("one `> **Proposed:**`", layout(twice))

    def test_two_reasons_refused(self):
        self.assertIn("one `> **Why:**`", layout(ENTRY + "> **Why:** And it is cheap.\n"))

    def test_refusal_names_the_entry_and_shows_the_layout(self):
        problem = layout(ENTRY.replace("**Why:**", "Because"))
        self.assertIn("entry 1", problem)
        self.assertIn("Where the daily tariff copy is kept", problem)
        self.assertIn(status_check.OPEN_QUESTIONS_LAYOUT, problem)

    def test_wrapped_proposal_without_its_marker_passes(self):
        wrapped = ENTRY.replace("> **Proposed:** Object storage, one file per day.\n",
                                "> **Proposed:** Object storage, one file per day, kept for as long\nas the tariff rules say.\n")
        self.assertIsNone(layout(wrapped))

    def test_quote_like_line_in_a_code_block_is_context(self):
        fenced = ENTRY.replace("The tariff is copied daily, but where is not yet chosen.",
                               "The import prints:\n\n```\n> done\n```")
        self.assertIsNone(layout(fenced))

    def test_quote_in_the_context_passes_when_the_proposal_quote_is_last(self):
        quoted = ENTRY.replace("The tariff is copied daily, but where is not yet chosen.",
                               "> Keep a copy every day.\n\nThe owner asked for this, but not where.")
        self.assertIsNone(layout(quoted))

    def test_proposed_in_an_earlier_quote_refused(self):
        early = ENTRY.replace("The tariff is copied daily, but where is not yet chosen.",
                              "> **Proposed:** A table.\n\nNot chosen.")
        self.assertIn("Proposed:", layout(early))

    def test_rule_after_the_last_entry_passes(self):
        self.assertIsNone(layout(ENTRY + "\n---\n"))

    def test_heading_indented_up_to_three_spaces_passes(self):
        self.assertIsNone(layout(" " + ENTRY))

    def test_heading_inside_a_code_block_is_text(self):
        fenced = ENTRY.replace("The tariff is copied daily, but where is not yet chosen.",
                               "The tariff is copied daily:\n\n```\n### 2. not a heading\n```")
        self.assertIsNone(layout(fenced))


class OpenQuestionsLayout(Workspace):
    """The hook refuses an Open questions section that is new or changed and not in the layout;
    a document written before it may be edited elsewhere (ADR 0030)."""

    KINDS = {
        "spec": (("docs", "specs", "thing.spec.md"), spec),
        "ADR": (("docs", "adrs", "0001-session-data-storage.md"), adr),
        "plan": (("docs", "plans", "2026-10-29-thing-release.md"), lambda **kw: plan(specs="None.", **kw)),
        "spike record": (("docs", "spikes", "2026-11-04-tiff-files-open.md"), record),
        "brief": (("docs", "brief.md"),
                  lambda questions="None.": BRIEF + f"\n## Open questions\n\n{questions}\n"),
    }

    def at(self, kind):
        parts, make = self.KINDS[kind]
        self.path = os.path.join(self.tmp.name, *parts)
        return make

    def test_new_document_in_the_layout_allowed(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.assertIsNone(self.write(make(questions=ENTRY)), kind)

    def test_new_document_in_the_old_layout_refused(self):
        for kind in self.KINDS:
            make = self.at(kind)
            reason = self.write(make(questions=OLD_ENTRY))
            self.assertIsNotNone(reason, kind)
            self.assertIn("Open questions", reason, kind)

    def test_old_layout_document_edited_elsewhere_allowed(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.put(make(questions=OLD_ENTRY))
            text = make(questions=OLD_ENTRY)
            edited = text.replace("\n# ", "\n# Renamed ", 1)
            self.assertIsNone(self.write(edited), kind)

    def test_old_layout_document_whose_questions_change_refused(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.put(make(questions=OLD_ENTRY))
            self.assertIn("heading", self.edit("object storage", "a database"), kind)

    def test_old_layout_relaid_allowed(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.put(make(questions=OLD_ENTRY))
            self.assertIsNone(self.edit(OLD_ENTRY, ENTRY), kind)

    def test_answering_the_last_question_allowed(self):
        for kind in self.KINDS:
            make = self.at(kind)
            self.put(make(questions=ENTRY))
            self.assertIsNone(self.edit(ENTRY, "None.\n"), kind)

    def test_old_layout_document_gaining_a_footnote_allowed(self):
        self.at("spec")
        self.put(spec(questions=OLD_ENTRY))
        self.assertIsNone(self.write(spec(questions=OLD_ENTRY) + "\n[^u]: A term used above.\n"))

    def test_old_layout_document_changing_only_space_or_comments_allowed(self):
        self.at("spec")
        self.put(spec(questions=OLD_ENTRY))
        self.assertIsNone(self.edit(OLD_ENTRY, "<!-- note -->\n" + OLD_ENTRY + "\n"))

    def test_file_without_a_lifecycle_status_left_alone(self):
        self.path = os.path.join(self.tmp.name, "docs", "specs", "notes.spec.md")
        self.assertIsNone(self.write("# Notes\n\n## Open questions\n\n- Anything?\n"))


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
        # An edit that changes no status, so the date is never compared with the real day.
        self.put(spec(date="2026-01-05"))
        content = spec(rule="The system SHALL do Y.", date="2026-01-05")
        done = self.run_hook({"tool_name": "Write", "tool_input": {"file_path": self.path, "content": content}})
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))

    def test_bad_input_does_not_block(self):
        done = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())



class Anchors(unittest.TestCase):
    def test_github_anchor_rules(self):
        cases = {"1. Copy matches iCloud": "1-copy-matches-icloud",
                 "2. Folder 🧪 kept": "2-folder--kept",
                 "3. Don't re-send `HELLO`": "3-dont-re-send-hello",
                 "4. Über-fast_path": "4-über-fast_path",
                 "5. Cafe\u0301 open": "5-cafe\u0301-open"}
        for heading, anchor in cases.items():
            self.assertEqual(status_check.anchor_of(heading), anchor, heading)


if __name__ == "__main__":
    unittest.main()

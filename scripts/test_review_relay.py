import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "review_relay.py")
ROOT = os.path.normpath(os.path.join(HERE, ".."))

SPEC = "docs/specs/booking.spec.md"
REPORT = "Result: FAIL\n\n| Check | Result | Evidence |\n|---|---|---|\n| 2. Story | fail | \"x\" |\n"
DRAFT = "Title: Review stops early\n\nBody line one.\nBody line two.\n"
WORDING = "Result: FAIL\n\nFindings:\n- \"rides along\": rewrite as \"is sent with\"\n"
LANGUAGE = "sdlc:language-checker"


def issue_request(draft, kind="bug"):
    return f"Document: issue draft\nKind: {kind}\n=== DRAFT ===\n{draft}=== END DRAFT ===\n"


class Relay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = os.path.join(self.tmp.name, "project")
        self.data = os.path.join(self.tmp.name, "data")
        os.makedirs(self.project)
        self.session = "s1"

    def put(self, path, text):
        full = os.path.join(self.project, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def run_hook(self, event, raw=None):
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data, CLAUDE_PROJECT_DIR=self.project,
                   CLAUDE_PLUGIN_ROOT=ROOT)
        done = subprocess.run([sys.executable, SCRIPT], input=raw if raw is not None else json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout) if done.stdout.strip() else None

    def agent(self, when, agent, prompt, response=None, session=None, **extra):
        event = {"hook_event_name": when, "session_id": session or self.session, "cwd": self.project,
                 "tool_name": "Agent",
                 "tool_input": dict({"subagent_type": agent, "prompt": prompt,
                                     "description": "a task"}, **extra)}
        if response is not None:
            event["tool_response"] = {"content": [{"type": "text", "text": response}]}
        return self.run_hook(event)

    def review(self, agent="sdlc:spec-reviewer", prompt=f"Document: {SPEC}\nReview this spec.",
               report=REPORT, session=None, wording=WORDING):
        """Run the skill's reviewer, then the language checker unless wording is None."""
        self.assertIsNone(self.agent("PreToolUse", agent, prompt, session=session))
        self.assertIsNone(self.agent("PostToolUse", agent, prompt, response=report, session=session))
        if wording is not None:
            self.language(prompt, wording, session=session)

    def language(self, prompt=f"Document: {SPEC}\nCheck the wording.", wording=WORDING, session=None):
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, prompt, session=session))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, prompt, response=wording, session=session))

    def check(self, prompt=f"Document: {SPEC}\nCheck the corrections.", session=None, **extra):
        return self.agent("PreToolUse", "sdlc:correction-checker", prompt, session=session, **extra)

    def assertAllowed(self, out):
        self.assertIsNotNone(out)
        decision = out["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "allow")
        return decision["updatedInput"]

    def assertRefused(self, out, needle):
        self.assertIsNotNone(out)
        decision = out["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn(needle, decision["permissionDecisionReason"])

    def saved(self):
        folder = os.path.join(self.data, "reviews")
        return [os.path.join(d, f) for d, _, files in os.walk(folder) for f in files]

    # Reviewer start and finish

    def test_checker_gets_the_report_and_the_text_as_reviewed_word_for_word(self):
        self.put(SPEC, "# Booking\n\nAs reviewed.\n")
        self.review()
        self.put(SPEC, "# Booking\n\nCorrected.\n")
        updated = self.assertAllowed(self.check())
        prompt = updated["prompt"]
        self.assertTrue(prompt.startswith(f"Document: {SPEC}\nCheck the corrections."))
        self.assertIn("=== REVIEW REPORT ===\n" + REPORT + "\n=== END REVIEW REPORT ===", prompt)
        self.assertIn(f"=== DOCUMENT AS REVIEWED: {SPEC} ===\n# Booking\n\nAs reviewed.\n\n"
                      "=== END DOCUMENT ===", prompt)
        self.assertNotIn("Corrected.", prompt)

    def test_checker_request_keeps_its_other_fields(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        updated = self.assertAllowed(self.check(model="sonnet"))
        self.assertEqual(updated["subagent_type"], "sdlc:correction-checker")
        self.assertEqual(updated["description"], "a task")
        self.assertEqual(updated["model"], "sonnet")

    def test_checker_is_told_the_rubric_and_files_of_the_skill_that_reviewed(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn(os.path.join(ROOT, "skills", "spec", "references", "rubric.md"), prompt)
        self.assertIn("docs/brief.md", prompt)
        adr = "docs/adrs/0001-use-x.md"
        self.put(adr, "v1\n")
        self.review(agent="sdlc:adr-reviewer", prompt=f"Document: {adr}\nReview this ADR.")
        self.put(adr, "v2\n")
        prompt = self.assertAllowed(self.check(prompt=f"Document: {adr}\nCheck."))["prompt"]
        self.assertIn(os.path.join(ROOT, "skills", "adr", "references", "rubric.md"), prompt)
        self.assertNotIn("spec", prompt.split("=== REVIEW REPORT ===")[1].split("=== END DOCUMENT ===")[1])

    def test_names_without_the_plugin_prefix_work_too(self):
        self.put(SPEC, "v1\n")
        self.review(agent="spec-reviewer")
        self.put(SPEC, "v2\n")
        self.assertAllowed(self.agent("PreToolUse", "correction-checker",
                                      f"Document: {SPEC}\nCheck."))

    def test_absolute_and_relative_paths_name_the_same_document(self):
        self.put(SPEC, "v1\n")
        self.review(prompt=f"Document: {os.path.join(self.project, SPEC)}\nReview.")
        self.put(SPEC, "v2\n")
        self.assertAllowed(self.check())

    def test_reviewer_without_a_document_line_saves_nothing(self):
        self.put(SPEC, "v1\n")
        self.review(prompt=f"Review the spec at {SPEC}.")
        self.assertEqual(self.saved(), [])

    def test_reviewer_of_a_missing_file_saves_nothing(self):
        self.review()
        self.assertEqual(self.saved(), [])

    def test_a_new_review_replaces_the_last_one(self):
        self.put(SPEC, "v1\n")
        self.review(report="first report")
        self.put(SPEC, "v2\n")
        self.review(report="second report")
        self.put(SPEC, "v3\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("second report", prompt)
        self.assertNotIn("first report", prompt)
        self.assertIn("=== DOCUMENT AS REVIEWED: " + SPEC + " ===\nv2\n", prompt)

    def test_two_documents_keep_separate_reviews(self):
        other = "docs/specs/payments.spec.md"
        self.put(SPEC, "booking v1\n")
        self.put(other, "payments v1\n")
        self.review(report="booking report")
        self.review(prompt=f"Document: {other}\nReview.", report="payments report")
        self.put(SPEC, "booking v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("booking report", prompt)
        self.assertNotIn("payments", prompt)

    # The language checker runs beside every reviewer

    def test_checker_gets_the_wording_report_word_for_word_in_its_own_block(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("=== REVIEW REPORT ===\n" + REPORT + "\n=== END REVIEW REPORT ===", prompt)
        self.assertIn("=== WORDING REPORT ===\n" + WORDING + "\n=== END WORDING REPORT ===", prompt)

    def test_checker_is_told_where_the_plain_words_rule_is(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        files = prompt.split("=== FILES TO READ ===")[1]
        self.assertIn(os.path.join(ROOT, "docs", "lifecycle.md"), files)
        self.assertIn("Plain words", files)

    def test_both_reports_count_whichever_starts_or_finishes_first(self):
        review = f"Document: {SPEC}\nReview."
        wording = f"Document: {SPEC}\nCheck the wording."
        orders = [
            [("PreToolUse", LANGUAGE), ("PreToolUse", "sdlc:spec-reviewer"),
             ("PostToolUse", "sdlc:spec-reviewer"), ("PostToolUse", LANGUAGE)],
            [("PreToolUse", "sdlc:spec-reviewer"), ("PreToolUse", LANGUAGE),
             ("PostToolUse", LANGUAGE), ("PostToolUse", "sdlc:spec-reviewer")],
            [("PreToolUse", LANGUAGE), ("PostToolUse", LANGUAGE),
             ("PreToolUse", "sdlc:spec-reviewer"), ("PostToolUse", "sdlc:spec-reviewer")],
        ]
        for n, order in enumerate(orders):
            with self.subTest(order=n):
                session = f"order{n}"
                self.put(SPEC, "v1\n")
                for when, agent in order:
                    prompt = wording if agent == LANGUAGE else review
                    response = None
                    if when == "PostToolUse":
                        response = WORDING if agent == LANGUAGE else REPORT
                    self.assertIsNone(self.agent(when, agent, prompt, response=response, session=session))
                self.put(SPEC, "v2\n")
                prompt = self.assertAllowed(self.check(session=session))["prompt"]
                self.assertIn(REPORT, prompt)
                self.assertIn(WORDING, prompt)
                self.assertIn("=== DOCUMENT AS REVIEWED: " + SPEC + " ===\nv1\n", prompt)

    def test_checker_without_the_wording_report_is_refused(self):
        self.put(SPEC, "v1\n")
        self.review(wording=None)
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "language checker")

    def test_checker_with_only_the_wording_report_is_refused(self):
        self.put(SPEC, "v1\n")
        self.language()
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")

    def test_wording_report_of_another_version_does_not_count(self):
        self.put(SPEC, "v1\n")
        self.review(wording=None)
        self.put(SPEC, "v2\n")
        self.language()
        self.put(SPEC, "v3\n")
        self.assertRefused(self.check(), "No review")

    def test_a_new_review_of_unchanged_text_replaces_both_reports(self):
        self.put(SPEC, "v1\n")
        self.review(report="first report", wording="first wording")
        self.review(report="second report", wording="second wording")
        self.put(SPEC, "v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("second report", prompt)
        self.assertIn("second wording", prompt)
        self.assertNotIn("first", prompt)

    def test_wording_of_an_issue_draft_counts(self):
        self.review(agent="sdlc:issue-reviewer", prompt=issue_request(DRAFT))
        corrected = DRAFT.replace("line two", "line 2")
        prompt = self.assertAllowed(self.check(prompt=issue_request(corrected)))["prompt"]
        self.assertIn("=== WORDING REPORT ===\n" + WORDING, prompt)

    def test_language_checker_names_without_the_plugin_prefix_work_too(self):
        self.put(SPEC, "v1\n")
        self.review(wording=None)
        self.assertIsNone(self.agent("PreToolUse", "language-checker", f"Document: {SPEC}\nGo."))
        self.assertIsNone(self.agent("PostToolUse", "language-checker", f"Document: {SPEC}\nGo.",
                                     response=WORDING))
        self.put(SPEC, "v2\n")
        self.assertAllowed(self.check())

    # /issue: the draft is never on disk

    def test_issue_draft_is_taken_from_the_requests(self):
        self.review(agent="sdlc:issue-reviewer", prompt=issue_request(DRAFT))
        corrected = DRAFT.replace("line two", "line 2")
        prompt = self.assertAllowed(self.check(prompt=issue_request(corrected)))["prompt"]
        self.assertIn("=== DOCUMENT AS REVIEWED: issue draft ===\n" + DRAFT, prompt)
        self.assertIn("=== DRAFT ===\n" + corrected, prompt)
        self.assertIn(os.path.join(ROOT, "skills", "issue", "references", "rubric.md"), prompt)
        self.assertNotIn("docs/brief.md", prompt)

    def test_unchanged_issue_draft_is_refused(self):
        self.review(agent="sdlc:issue-reviewer", prompt=issue_request(DRAFT))
        self.assertRefused(self.check(prompt=issue_request(DRAFT)), "unchanged")

    def test_issue_review_without_a_draft_saves_nothing(self):
        self.review(agent="sdlc:issue-reviewer", prompt="Document: issue draft\nKind: bug\n")
        self.assertEqual(self.saved(), [])

    # When the checker is refused

    def test_checker_without_a_document_line_is_refused(self):
        self.assertRefused(self.check(prompt="Check the corrections."), "Document:")

    def test_checker_with_no_review_on_record_is_refused(self):
        self.put(SPEC, "v1\n")
        self.assertRefused(self.check(), "No review")

    def test_checker_before_the_review_finished_is_refused(self):
        self.put(SPEC, "v1\n")
        self.assertIsNone(self.agent("PreToolUse", "sdlc:spec-reviewer", f"Document: {SPEC}\nReview."))
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")

    def test_checker_after_a_review_with_no_report_is_refused(self):
        self.put(SPEC, "v1\n")
        self.review(report="")
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")

    def test_checker_on_an_unchanged_document_is_refused(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.assertRefused(self.check(), "unchanged")

    def test_review_in_another_session_does_not_count(self):
        self.put(SPEC, "v1\n")
        self.review(session="other")
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")

    # Clearing up

    def test_checker_finishing_deletes_only_its_documents_review(self):
        other = "docs/specs/payments.spec.md"
        self.put(SPEC, "v1\n")
        self.put(other, "p1\n")
        self.review()
        self.review(prompt=f"Document: {other}\nReview.")
        self.put(SPEC, "v2\n")
        self.put(other, "p2\n")
        prompt = f"Document: {SPEC}\nCheck."
        self.assertAllowed(self.check(prompt=prompt))
        self.assertIsNone(self.agent("PostToolUse", "sdlc:correction-checker", prompt, response="Result: PASS"))
        self.assertRefused(self.check(prompt=prompt), "No review")
        self.assertAllowed(self.check(prompt=f"Document: {other}\nCheck."))

    def test_session_end_deletes_that_sessions_reviews_only(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.review(session="other")
        self.assertIsNone(self.run_hook({"hook_event_name": "SessionEnd", "session_id": self.session}))
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")
        self.assertAllowed(self.check(session="other"))

    def test_nothing_is_left_once_the_checker_finishes_and_the_session_ends(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        self.check()
        self.agent("PostToolUse", "sdlc:correction-checker", f"Document: {SPEC}\nCheck.", response="ok")
        self.run_hook({"hook_event_name": "SessionEnd", "session_id": self.session})
        self.assertEqual(self.saved(), [])

    # Everything else is left alone

    def test_other_agents_and_tools_are_left_alone(self):
        self.put(SPEC, "v1\n")
        self.assertIsNone(self.agent("PreToolUse", "general-purpose", f"Document: {SPEC}\nGo."))
        self.assertIsNone(self.run_hook({"hook_event_name": "PreToolUse", "session_id": self.session,
                                         "tool_name": "Bash", "tool_input": {"command": "ls"}}))
        self.assertEqual(self.saved(), [])

    def test_malformed_input_never_blocks(self):
        self.assertIsNone(self.run_hook(None, raw="not json"))
        self.assertIsNone(self.run_hook(None, raw="[]"))
        self.assertIsNone(self.run_hook({"hook_event_name": "PreToolUse", "tool_name": "Agent",
                                         "tool_input": "oops"}))

    def test_help_describes_the_hook(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("correction checker", done.stdout)


if __name__ == "__main__":
    unittest.main()

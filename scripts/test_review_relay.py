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

    def run_hook(self, event, raw=None, data=True):
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data, CLAUDE_PROJECT_DIR=self.project,
                   CLAUDE_PLUGIN_ROOT=ROOT)
        if not data:
            del env["CLAUDE_PLUGIN_DATA"]
        done = subprocess.run([sys.executable, SCRIPT], input=raw if raw is not None else json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout) if done.stdout.strip() else None

    def agent(self, when, agent, prompt, response=None, session=None, call=None, **extra):
        event = {"hook_event_name": when, "session_id": session or self.session, "cwd": self.project,
                 "tool_name": "Agent", "tool_use_id": call or f"{agent}-{prompt}",
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

    def test_a_late_report_from_an_earlier_run_does_not_count(self):
        v1 = f"Document: {SPEC}\nCheck the wording."
        self.put(SPEC, "v1\n")
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, v1, call="old"))
        self.put(SPEC, "v2\n")
        self.assertIsNone(self.agent("PreToolUse", "sdlc:spec-reviewer", v1, call="rev"))
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, v1, call="new"))
        self.assertIsNone(self.agent("PostToolUse", "sdlc:spec-reviewer", v1, response=REPORT, call="rev"))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, v1, response="current wording", call="new"))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, v1, response="stale wording", call="old"))
        self.put(SPEC, "v3\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("current wording", prompt)
        self.assertNotIn("stale wording", prompt)

    def test_refusal_for_a_missing_wording_report_never_asks_for_another_review(self):
        self.put(SPEC, "v1\n")
        self.review(wording=None)
        self.put(SPEC, "v2\n")
        out = self.check()
        self.assertRefused(out, "language checker")
        reason = out["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("show the person", reason)
        self.assertNotIn("Start the language checker", reason)

    def test_a_saved_record_in_another_shape_counts_as_no_review(self):
        self.put(SPEC, "v1\n")
        self.review()
        for path in self.saved():
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"reviewer": "spec-reviewer", "text": "v1\n", "report": "old shape"}, f)
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")
        for path in self.saved():
            with open(path, "w", encoding="utf-8") as f:
                f.write("[1, 2]")
        self.assertIsNone(self.agent("PreToolUse", "sdlc:spec-reviewer", f"Document: {SPEC}\nGo."))
        self.assertRefused(self.check(), "No review")

    def test_wording_of_a_slightly_different_copy_of_the_same_review_still_joins(self):
        # /issue types the draft into both requests; a stray space must not lose the review.
        self.assertIsNone(self.agent("PreToolUse", "sdlc:issue-reviewer", issue_request(DRAFT)))
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, issue_request(DRAFT + " ")))
        self.assertIsNone(self.agent("PostToolUse", "sdlc:issue-reviewer", issue_request(DRAFT), response=REPORT))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, issue_request(DRAFT + " "), response=WORDING))
        corrected = DRAFT.replace("line two", "line 2")
        prompt = self.assertAllowed(self.check(prompt=issue_request(corrected)))["prompt"]
        self.assertIn("=== DOCUMENT AS REVIEWED: issue draft ===\n" + DRAFT, prompt)
        self.assertIn(WORDING, prompt)

    def test_a_second_language_check_during_a_review_leaves_it_alone(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        self.language(prompt=f"Document: {SPEC}\nCheck my wording fixes.", wording="second wording")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn(REPORT, prompt)
        self.assertIn(WORDING, prompt)
        self.assertNotIn("second wording", prompt)

    def test_a_new_review_may_start_with_the_language_checker(self):
        self.put(SPEC, "v1\n")
        self.review(report="first report", wording="first wording")
        self.put(SPEC, "v2\n")
        self.language(prompt=f"Document: {SPEC}\nCheck the wording.", wording="second wording")
        self.review(report="second report", wording=None)
        self.put(SPEC, "v3\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn("second report", prompt)
        self.assertIn("second wording", prompt)
        self.assertNotIn("first", prompt)

    def test_reviewer_or_language_checker_in_the_background_is_refused(self):
        self.put(SPEC, "v1\n")
        for agent in ("sdlc:spec-reviewer", LANGUAGE):
            out = self.agent("PreToolUse", agent, f"Document: {SPEC}\nReview.", run_in_background=True)
            self.assertRefused(out, "foreground")
        self.assertEqual(self.saved(), [])

    def test_without_tool_use_ids_both_reports_still_count(self):
        self.put(SPEC, "v1\n")
        for when, agent, response in [("PreToolUse", "sdlc:spec-reviewer", None),
                                      ("PreToolUse", LANGUAGE, None),
                                      ("PostToolUse", "sdlc:spec-reviewer", REPORT),
                                      ("PostToolUse", LANGUAGE, WORDING)]:
            event = {"hook_event_name": when, "session_id": self.session, "tool_name": "Agent",
                     "tool_input": {"subagent_type": agent, "prompt": f"Document: {SPEC}\nGo."}}
            if response:
                event["tool_response"] = {"content": [{"type": "text", "text": response}]}
            self.assertIsNone(self.run_hook(event))
        self.put(SPEC, "v2\n")
        self.assertAllowed(self.check())

    def test_no_refusal_asks_for_a_second_review(self):
        self.put(SPEC, "v1\n")
        for out in (self.check(), self.check(prompt="Check the corrections.")):
            reason = out["hookSpecificOutput"]["permissionDecisionReason"]
            self.assertNotIn("Run the review", reason)

    def test_a_part_started_again_after_a_run_with_no_report_joins_the_same_review(self):
        self.put(SPEC, "v1\n")
        prompt = f"Document: {SPEC}\nReview."
        self.assertIsNone(self.agent("PreToolUse", "sdlc:spec-reviewer", prompt, call="r1"))
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, prompt, call="l1"))
        self.assertIsNone(self.agent("PostToolUse", "sdlc:spec-reviewer", prompt, response=REPORT, call="r1"))
        # l1 never finishes; it is started again as l2.
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, prompt, call="l2"))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, prompt, response=WORDING, call="l2"))
        self.put(SPEC, "v2\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn(REPORT, prompt)
        self.assertIn(WORDING, prompt)

    def test_the_newest_complete_review_outlasts_later_unfinished_ones(self):
        self.put(SPEC, "v1\n")
        self.review()
        for version in ("v2\n", "v3\n", "v4\n"):
            self.put(SPEC, version)
            self.language(wording="wording of " + version)
        self.put(SPEC, "v5\n")
        prompt = self.assertAllowed(self.check())["prompt"]
        self.assertIn(REPORT, prompt)
        self.assertIn(WORDING, prompt)

    def test_a_saved_review_with_reports_of_the_wrong_type_counts_as_no_review(self):
        self.put(SPEC, "v1\n")
        self.review()
        for path in self.saved():
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"reviews": [{"text": "v1\n", "started": {"a": "reviewer", "b": "language"},
                                        "reports": {"spec-reviewer": 5, "language-checker": ["x"]}}]}, f)
        self.put(SPEC, "v2\n")
        self.assertRefused(self.check(), "No review")

    def test_a_correction_that_only_changes_spacing_still_counts(self):
        # In Markdown a blank line or an indent can be the correction.
        self.put(SPEC, "Intro\n- item\n")
        self.review()
        self.put(SPEC, "Intro\n\n- item\n")
        self.assertAllowed(self.check())

    def test_the_reviewers_copy_of_an_issue_draft_is_the_one_kept(self):
        self.assertIsNone(self.agent("PreToolUse", LANGUAGE, issue_request(DRAFT + " ")))
        self.assertIsNone(self.agent("PreToolUse", "sdlc:issue-reviewer", issue_request(DRAFT)))
        self.assertIsNone(self.agent("PostToolUse", LANGUAGE, issue_request(DRAFT + " "), response=WORDING))
        self.assertIsNone(self.agent("PostToolUse", "sdlc:issue-reviewer", issue_request(DRAFT), response=REPORT))
        self.assertRefused(self.check(prompt=issue_request(DRAFT)), "unchanged")

    def test_a_newer_review_missing_a_report_is_not_covered_by_an_older_one(self):
        self.put(SPEC, "v1\n")
        self.review()
        self.put(SPEC, "v2\n")
        self.review(report="", wording="second wording")
        self.put(SPEC, "v3\n")
        self.assertRefused(self.check(), "No review")

    def test_reports_of_agents_this_version_does_not_know_are_ignored(self):
        self.put(SPEC, "v1\n")
        self.review()
        for path in self.saved():
            with open(path, encoding="utf-8") as f:
                saved = json.load(f)
            saved["reviews"][0]["reports"]["old-reviewer"] = "old"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(saved, f)
        self.put(SPEC, "v2\n")
        self.assertAllowed(self.check())

    def test_a_check_with_nothing_saved_leaves_no_folder_behind(self):
        self.put(SPEC, "v1\n")
        self.check()
        self.agent("PostToolUse", "sdlc:correction-checker", f"Document: {SPEC}\nCheck.", response="ok")
        self.assertFalse(os.path.exists(os.path.join(self.data, "reviews")))

    def test_background_runs_are_left_alone_when_nothing_is_saved(self):
        self.put(SPEC, "v1\n")
        event = {"hook_event_name": "PreToolUse", "session_id": self.session, "tool_name": "Agent",
                 "tool_input": {"subagent_type": LANGUAGE, "prompt": f"Document: {SPEC}\nGo.",
                                "run_in_background": True}}
        self.assertIsNone(self.run_hook(event, data=False))

    def test_a_null_text_block_in_a_reply_never_blocks(self):
        self.put(SPEC, "v1\n")
        self.assertIsNone(self.agent("PreToolUse", "sdlc:spec-reviewer", f"Document: {SPEC}\nGo."))
        event = {"hook_event_name": "PostToolUse", "session_id": self.session, "tool_name": "Agent",
                 "tool_use_id": f"sdlc:spec-reviewer-Document: {SPEC}\nGo.",
                 "tool_input": {"subagent_type": "sdlc:spec-reviewer", "prompt": f"Document: {SPEC}\nGo."},
                 "tool_response": {"content": [{"type": "text", "text": None}]}}
        self.assertIsNone(self.run_hook(event))

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

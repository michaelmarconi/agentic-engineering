import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "skill_check.py")
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from skill_check import (AGENT_RULE, SHELL_AGENT_RULE, ASK_RULE, BUILD_ACCEPT_RULE, BUILD_ASK_RULE, BUILD_PATH_RULE, BUILD_REREAD_RULE, REPORT_RULE, SCRATCHPAD_RULE, ASK_SKILLS, CORRECT_RULES, DOCUMENT_SKILLS, PATH_RULE, PROPOSED_RULE,  # noqa: E402
                         QUESTIONS_RULE, REPORT_RULES, REVIEW_RULE, SHOW_RULE, ANSWER_RULES,
                         SIGNOFF_RULE, STATUS_SKILLS, TYPE_RULE, DATE_RULE, RENAME_RULE, DIAGRAM_SKILLS, DIAGRAM_RULES,
                         diagram_rules, holds, pointer, ending, ANSWERS_ENDING, FAILED_ENDING,
                         REVIEWING_SKILLS, MOVED_RULES, SHOW_HEADING, SHOW_PLACES, OLD_SHOW_RULES)

DESCRIPTION = "Write a thing. Use whenever someone wants a thing."


def lifecycle_page(steps=None, answers=None, failed=None, places=None):
    """A lifecycle page whose Review process section holds the given sentences, by default all,
    followed by a Showing a file to you section holding the given places, by default all."""
    steps = CORRECT_RULES + (PATH_RULE,) if steps is None else steps
    answers = ANSWER_RULES if answers is None else answers
    failed = (REVIEW_RULE,) if failed is None else failed
    places = SHOW_PLACES if places is None else places
    return ("# The lifecycle\n\n## Review process\n\n" + "\n\n".join(steps)
            + f"\n\n### {ANSWERS_ENDING}\n\n" + "\n\n".join(answers)
            + f"\n\n### {FAILED_ENDING}\n\n" + "\n\n".join(failed)
            + f"\n\n{SHOW_HEADING}\n\n" + "\n".join(f"- {place}" for place in places) + "\n")


def skill_md(name="demo", description=DESCRIPTION, body="# Demo\n\nDo the thing.\n"):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}"


class SkillCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def put_agent(self, name, text):
        path = os.path.join(self.tmp.name, "agents", name + ".md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def put(self, folder, text):
        path = os.path.join(self.tmp.name, "skills", folder, "SKILL.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def check(self, root=None):
        # A plugin whose skills point to the lifecycle page needs the page: give it a complete one
        # unless the test wrote its own or is about the page being missing.
        page = os.path.join(self.tmp.name, "docs", "lifecycle.md")
        if root is None and not getattr(self, "no_lifecycle", False) and not os.path.exists(page):
            os.makedirs(os.path.dirname(page), exist_ok=True)
            with open(page, "w") as f:
                f.write(lifecycle_page())
        return subprocess.run([sys.executable, SCRIPT, root or self.tmp.name],
                              capture_output=True, text=True)

    def assertFails(self, needle):
        done = self.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(needle, done.stdout)

    def test_valid_skill_passes_silently(self):
        self.put("demo", skill_md())
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_plugins_own_skills_pass(self):
        done = self.check(ROOT)
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_answer_rules_offer_the_four_choices(self):
        rules = " ".join(ANSWER_RULES)
        for choice in ('"Accept"', '"My own answer"', '"Ignore"', '"Defer"', "ignore or defer?"):
            self.assertIn(choice, rules)

    def test_answer_rules_keep_drafting_questions_out_of_the_document(self):
        rules = " ".join(ANSWER_RULES)
        self.assertIn("While drafting", rules)
        self.assertIn("out of the document", rules)
        self.assertIn("only a deferred one reaches Open questions", rules)

    def test_questions_rule_sends_marked_gaps_to_the_person(self):
        self.assertIn("not chosen or not known yet goes under Needs a person, never as a failure",
                      " ".join(QUESTIONS_RULE.split()))

    # The review sequence is written once, on the lifecycle page (docs/adrs/0053)

    def reviewing(self, folder="feedback", document="Document: feedback draft", extra=""):
        """A reviewing skill's body: its pointer, its request and whatever `extra` adds."""
        rules = f"{ASK_RULE}\n\n" if folder in ASK_SKILLS else ""
        return f"# Demo\n\n{rules}{pointer(folder)}\n\n```\n{document}\nReview this.\n```\n\n{extra}"

    def test_reviewing_skill_with_its_pointer_passes(self):
        self.put("feedback", skill_md(name="feedback", body=self.reviewing()))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_reviewing_skill_without_its_pointer_fails(self):
        self.put("feedback", skill_md(name="feedback", body="# Feedback\n\nReview the draft.\n"))
        self.assertFails("feedback/SKILL.md: review pointer missing")

    def test_pointer_wrapped_across_lines_passes(self):
        body = self.reviewing().replace(" section of ", "\nsection of ")
        self.put("feedback", skill_md(name="feedback", body=body))
        self.assertEqual(self.check().returncode, 0)

    def test_pointer_naming_the_other_ending_fails(self):
        body = f"# Feedback\n\n{pointer('spec')}\n"
        self.put("feedback", skill_md(name="feedback", body=body))
        self.assertFails("feedback/SKILL.md: review pointer missing")

    def test_each_ending_is_a_heading_of_the_review_process(self):
        self.assertEqual(ending("spec"), ANSWERS_ENDING)
        self.assertEqual(ending("practices"), FAILED_ENDING)
        with open(os.path.join(ROOT, "docs", "lifecycle.md"), encoding="utf-8") as f:
            page = f.read()
        review = page[page.index("## Review process\n"):]
        for heading in (ANSWERS_ENDING, FAILED_ENDING):
            self.assertIn(f"\n### {heading}\n", review)
        for folder in REVIEWING_SKILLS:
            self.assertIn(f'its "{ending(folder)}" part', pointer(folder))

    def test_the_reviewing_skills_are_the_document_skills_and_three_more(self):
        self.assertEqual(sorted(REVIEWING_SKILLS),
                         sorted(DOCUMENT_SKILLS + ("practices", "feedback", "release")))

    def test_pointer_reads_the_page_by_its_path_inside_the_plugin(self):
        self.assertIn("`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md`", pointer("spec"))

    def test_every_reviewing_skill_holds_its_pointer(self):
        for folder in REVIEWING_SKILLS:
            with open(os.path.join(ROOT, "skills", folder, "SKILL.md"), encoding="utf-8") as f:
                self.assertTrue(holds(f.read(), pointer(folder)), folder)

    def test_skill_still_holding_a_moved_sentence_fails(self):
        for rule in MOVED_RULES:
            self.put("feedback", skill_md(name="feedback", body=self.reviewing(extra=rule)))
            self.assertFails("feedback/SKILL.md: moved review sentence")

    def test_no_skill_holds_a_moved_sentence(self):
        skills = os.path.join(ROOT, "skills")
        for folder in os.listdir(skills):
            path = os.path.join(skills, folder, "SKILL.md")
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for rule in MOVED_RULES:
                self.assertFalse(holds(text, rule), (folder, rule[:40]))

    def test_every_reviewing_skill_names_its_own_reviewer(self):
        for folder in REVIEWING_SKILLS:
            with open(os.path.join(ROOT, "skills", folder, "SKILL.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn(f"`agentic:{folder}-reviewer`", text, folder)
            self.assertIn("Document: ", text, folder)

    # Every document is shown the same way (ADR 0055), found by the list, not by an agent's name

    def test_reviewing_skill_with_a_file_and_no_show_rule_fails(self):
        body = self.reviewing("practices", "Document: <the practices files' full paths>")
        self.put("practices", skill_md(name="practices", body=body))
        self.assertFails("practices/SKILL.md: show rule missing")

    def test_reviewing_skill_with_a_file_and_the_show_rule_passes(self):
        rule = SHOW_RULE.replace(" section of ", "\nsection of ")
        self.assertNotEqual(rule, SHOW_RULE)
        body = self.reviewing("practices", "Document: <the practices files' full paths>", rule)
        self.put("practices", skill_md(name="practices", body=body))
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_reworded_show_rule_fails(self):
        rule = SHOW_RULE.replace("again after each change", "once")
        self.assertNotEqual(rule, SHOW_RULE)
        body = self.reviewing("practices", "Document: <the practices files' full paths>", rule)
        self.put("practices", skill_md(name="practices", body=body))
        self.assertFails("show rule missing")

    def test_the_first_wording_of_the_show_rule_fails(self):
        old = ("Show the person the document: if the app you run in can show them a file in a viewer, "
               "use it, and show a fresh copy after each change if what it shows is a copy; always "
               "name the document's full path; never send them to a website to read it.")
        body = self.reviewing("practices", "Document: <the practices files' full paths>", old)
        self.put("practices", skill_md(name="practices", body=body))
        self.assertFails("show rule missing")

    def test_a_draft_never_saved_needs_no_show_rule(self):
        self.put("feedback", skill_md(name="feedback", body=self.reviewing()))
        self.assertNotIn("show rule missing", self.check().stdout)

    def test_other_skills_need_no_pointer_or_show_rule(self):
        self.put("demo", skill_md(body="# Demo\n\n```\nDocument: <the demo's full path>\n```\n"))
        self.assertEqual(self.check().returncode, 0)

    def test_the_show_rule_points_to_the_lifecycle_section(self):
        self.assertIn(SHOW_HEADING[3:], SHOW_RULE)
        self.assertIn("docs/lifecycle.md", SHOW_RULE)

    def test_the_report_rule_points_to_the_lifecycle_section(self):
        self.assertIn(SHOW_HEADING[3:], REPORT_RULE)
        self.assertIn("docs/lifecycle.md", REPORT_RULE)

    def test_a_skill_copying_an_old_show_sentence_back_fails(self):
        for old in OLD_SHOW_RULES:
            with self.subTest(old=old[:40]):
                body = self.reviewing("practices", "Document: <the practices files' full paths>", f"{SHOW_RULE}\n\n{old}")
                self.put("practices", skill_md(name="practices", body=body))
                self.assertFails("practices/SKILL.md: old show sentence")

    def test_a_report_skill_holding_the_old_report_wording_fails(self):
        old = [rule for rule in OLD_SHOW_RULES if "report file there" in rule][0]
        self.put("audit", skill_md(name="audit", body=f"# Audit\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n\n{old}\n"))
        self.assertFails("audit/SKILL.md: old show sentence")

    def test_the_three_places_are_named(self):
        text = " ".join(SHOW_PLACES)
        for place in ("Claude Code command line", "Claude Code desktop", "Claude project thread",
                      "/mnt/project-files/", "code-hosting site"):
            self.assertIn(place, text)

    def test_lifecycle_missing_the_show_section_fails(self):
        self.put_lifecycle(self.lifecycle().replace(SHOW_HEADING, "## Showing files"))
        self.assertFails(f'docs/lifecycle.md: no "{SHOW_HEADING}" heading')

    def test_lifecycle_missing_a_place_fails(self):
        for number in range(len(SHOW_PLACES)):
            with self.subTest(number=number):
                places = SHOW_PLACES[:number] + SHOW_PLACES[number + 1:]
                self.put_lifecycle(self.lifecycle(places=places))
                self.assertFails(f"docs/lifecycle.md: show place {number + 1} missing")

    def test_a_page_without_either_section_reports_both(self):
        self.put_lifecycle("# The lifecycle\n\nNothing here.\n")
        done = self.check()
        self.assertIn('no "## Review process" heading', done.stdout)
        self.assertIn(f'no "{SHOW_HEADING}" heading', done.stdout)

    def test_a_place_outside_the_show_section_does_not_count(self):
        text = self.lifecycle(places=SHOW_PLACES[1:]) + f"\n## Later\n\n{SHOW_PLACES[0]}\n"
        self.put_lifecycle(text)
        self.assertFails("docs/lifecycle.md: show place 1 missing")

    def test_no_skill_names_a_place(self):
        skills = os.path.join(ROOT, "skills")
        for name in os.listdir(skills):
            with open(os.path.join(skills, name, "SKILL.md"), encoding="utf-8") as f:
                text = f.read()
            for place in ("/mnt/project-files", "Files pane"):
                self.assertNotIn(place, text, name)

    def test_every_report_skill_holds_the_report_rule(self):
        holding = set()
        skills = os.path.join(ROOT, "skills")
        for name in os.listdir(skills):
            with open(os.path.join(skills, name, "SKILL.md"), encoding="utf-8") as f:
                if holds(f.read(), REPORT_RULE):
                    holding.add(name)
        self.assertEqual(holding, {"audit", "build", "verify"})

    def test_every_document_skill_holds_the_show_rule(self):
        holding = set()
        skills = os.path.join(ROOT, "skills")
        for name in os.listdir(skills):
            with open(os.path.join(skills, name, "SKILL.md"), encoding="utf-8") as f:
                if holds(f.read(), SHOW_RULE):
                    holding.add(name)
        self.assertEqual(holding, {"brief", "spec", "adr", "plan", "spike", "practices"})

    # The Review process section of the lifecycle page

    def lifecycle(self, steps=None, answers=None, failed=None, places=None):
        return lifecycle_page(steps, answers, failed, places)

    def put_lifecycle(self, text):
        path = os.path.join(self.tmp.name, "docs", "lifecycle.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def test_lifecycle_with_every_moved_sentence_passes(self):
        self.put_lifecycle(self.lifecycle())
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_lifecycle_missing_a_shared_step_fails(self):
        self.put_lifecycle(self.lifecycle(steps=CORRECT_RULES[:3] + CORRECT_RULES[4:] + (PATH_RULE,)))
        self.assertFails("docs/lifecycle.md: review step rule 4 missing")

    def test_lifecycle_missing_the_path_rule_fails(self):
        self.put_lifecycle(self.lifecycle(steps=CORRECT_RULES))
        self.assertFails("docs/lifecycle.md: path rule missing")

    def test_lifecycle_missing_an_answer_rule_fails(self):
        self.put_lifecycle(self.lifecycle(answers=ANSWER_RULES[:2] + ANSWER_RULES[3:]))
        self.assertFails("docs/lifecycle.md: answer rule 3 missing")

    def test_answer_rule_under_the_wrong_ending_fails(self):
        self.put_lifecycle(self.lifecycle(answers=ANSWER_RULES[1:], failed=(REVIEW_RULE, ANSWER_RULES[0])))
        self.assertFails("docs/lifecycle.md: answer rule 1 missing")

    def test_lifecycle_missing_the_review_rule_fails(self):
        self.put_lifecycle(self.lifecycle(failed=()))
        self.assertFails("docs/lifecycle.md: review rule missing")

    def test_lifecycle_without_an_ending_heading_fails(self):
        self.put_lifecycle(self.lifecycle().replace(f"### {FAILED_ENDING}", "### Stopping"))
        self.assertFails(f'docs/lifecycle.md: no "### {FAILED_ENDING}" heading')

    def test_lifecycle_without_the_review_process_heading_fails(self):
        self.put_lifecycle(self.lifecycle().replace("## Review process", "## Reviews"))
        self.assertFails('docs/lifecycle.md: no "## Review process" heading')

    def test_a_later_section_does_not_count_as_the_review_process(self):
        text = self.lifecycle(failed=()) + f"\n## Later\n\n{REVIEW_RULE}\n"
        self.put_lifecycle(text)
        self.assertFails("docs/lifecycle.md: review rule missing")

    def test_an_earlier_subheading_of_the_same_name_is_not_the_section(self):
        self.put_lifecycle("# The lifecycle\n\n### Review process\n\nSomething else.\n\n"
                           + self.lifecycle().split("\n\n", 1)[1])
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_a_skill_pointing_to_a_missing_lifecycle_page_fails(self):
        self.no_lifecycle = True
        self.put("practices", skill_md(name="practices", body=f"# Practices\n\n{pointer('practices')}\n"))
        self.assertFails("docs/lifecycle.md missing")

    def test_a_skill_starting_the_correction_checker_must_be_a_reviewing_skill(self):
        self.put("design", skill_md(name="design", body="# Design\n\nStart `agentic:correction-checker`.\n"))
        self.assertFails("design/SKILL.md: starts agentic:correction-checker but is not in REVIEWING_SKILLS")

    def test_reworded_marker_line_fails(self):
        answers = tuple(rule.replace("ignore or defer?", "ignore it or defer it?") for rule in ANSWER_RULES)
        self.put_lifecycle(self.lifecycle(answers=answers))
        self.assertFails("docs/lifecycle.md: answer rule 2 missing")

    def test_agent_given_a_repository_without_the_agent_rule_fails(self):
        self.put_agent("demo-reviewer", "---\nname: demo-reviewer\n---\n\nRead `Document: <path>` and `Repository: <folder>`.\n")
        self.assertFails("agents/demo-reviewer.md: repository rule missing")

    def test_a_document_reviewer_that_loses_the_agent_rule_fails(self):
        self.put_agent("plan-reviewer", "---\nname: plan-reviewer\n---\n\nYou review one plan.\n")
        self.assertFails("agents/plan-reviewer.md: repository rule missing")

    def test_agent_with_the_agent_rule_passes(self):
        rule = AGENT_RULE.replace(" It may ", "\nIt may ")
        self.put_agent("demo-reviewer", f"---\nname: demo-reviewer\n---\n\n{rule}\n")
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_every_agent_started_with_a_document_path_holds_the_agent_rule(self):
        agents = os.path.join(ROOT, "agents")
        holding = set()
        for name in os.listdir(agents):
            with open(os.path.join(agents, name), encoding="utf-8") as f:
                if AGENT_RULE in " ".join(f.read().split()):
                    holding.add(name[:-3])
        self.assertEqual(holding, {"spec-reviewer", "brief-reviewer", "adr-reviewer", "plan-reviewer",
                                   "spike-reviewer", "practices-reviewer", "language-checker",
                                   "correction-checker", "auditor", "audit-checker", "brief-checker"})

    def test_every_agent_that_runs_commands_holds_the_shell_agent_rule(self):
        agents = os.path.join(ROOT, "agents")
        holding = set()
        for name in os.listdir(agents):
            with open(os.path.join(agents, name), encoding="utf-8") as f:
                if SHELL_AGENT_RULE in " ".join(f.read().split()):
                    holding.add(name[:-3])
        self.assertEqual(holding, {"verifier", "verify-checker"})

    def test_verify_agent_without_the_shell_agent_rule_fails(self):
        self.put_agent("verifier", f"---\nname: verifier\n---\n\n{AGENT_RULE}\n")
        self.assertFails("agents/verifier.md: repository rule missing")

    def test_verify_agent_with_the_shell_agent_rule_passes(self):
        self.put_agent("verifier", f"---\nname: verifier\n---\n\n{SHELL_AGENT_RULE}\n")
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_document_skill_without_type_rule_fails(self):
        self.put("spec", skill_md(name="spec"))
        self.assertFails("spec/SKILL.md: type rule missing")

    def test_document_skill_with_type_rule_passes(self):
        body = f"# Spec\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{SIGNOFF_RULE}\n\n{DATE_RULE}\n\n{pointer('spec')}\n"
        self.put("spec", skill_md(name="spec", body=body))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_reworded_type_rule_fails(self):
        rule = TYPE_RULE.replace("never", "seldom")
        self.assertNotEqual(rule, TYPE_RULE)
        self.put("plan", skill_md(name="plan", body=f"# Plan\n\n{rule}\n"))
        self.assertFails("plan/SKILL.md: type rule missing")

    def test_other_skills_need_no_type_rule(self):
        self.put("feedback", skill_md(name="feedback", body=f"# Feedback\n\n{pointer('feedback')}\n"))
        self.put("audit", skill_md(name="audit", body=f"# Audit\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_ACCEPT_RULE}\n\n{BUILD_PATH_RULE}\n\n{BUILD_REREAD_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.put("practices", skill_md(name="practices", body=f"# Practices\n\n{ASK_RULE}\n\n{pointer('practices')}\n"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_the_document_skills_are_the_five_that_write_lifecycle_documents(self):
        self.assertEqual(sorted(DOCUMENT_SKILLS), ["adr", "brief", "plan", "spec", "spike"])

    # Shared review steps, proposed answers and sign-off

    def test_document_skill_without_proposed_rule_fails(self):
        self.put("brief", skill_md(name="brief", body=f"# Brief\n\n{TYPE_RULE}\n"))
        self.assertFails("brief/SKILL.md: proposed rule missing")

    def test_document_skill_without_rename_rule_fails(self):
        body = f"# Spec\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{ASK_RULE}\n\n{SIGNOFF_RULE}\n\n{DATE_RULE}\n"
        self.put("spec", skill_md(name="spec", body=body))
        self.assertFails("spec/SKILL.md: rename rule missing")

    def test_every_document_skill_holds_the_rename_rule(self):
        for name in DOCUMENT_SKILLS:
            with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as f:
                self.assertTrue(holds(f.read(), RENAME_RULE), name)

    def test_proposed_rule_gives_the_layout_the_hook_checks(self):
        for part in ("`### 1.", "`> **Proposed:**`", "`> **Why:**`", "two questions"):
            self.assertIn(part, PROPOSED_RULE)

    def test_asking_skill_without_ask_rule_fails(self):
        self.put("practices", skill_md(name="practices"))
        self.assertFails("practices/SKILL.md: ask rule missing")
        self.put("brief", skill_md(name="brief", body=f"# Brief\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n"))
        self.assertFails("brief/SKILL.md: ask rule missing")

    def test_ask_rule_waits_for_each_answer(self):
        # A question tool or card can return before the person answers (issue #125), so the
        # rule says to end the turn there, and one reply never holds several questions.
        self.assertIn("Ask one question per reply, then end your turn", ASK_RULE)
        self.assertIn("until the person answers it", ASK_RULE)
        self.assertIn("returns at once", ASK_RULE)
        self.assertNotIn("several questions", ASK_RULE)

    def test_reworded_ask_rule_fails(self):
        rule = ASK_RULE.replace("last", "first")
        self.assertNotEqual(rule, ASK_RULE)
        self.put("practices", skill_md(name="practices", body=f"# Practices\n\n{rule}\n"))
        self.assertFails("practices/SKILL.md: ask rule missing")

    def test_spike_without_the_scratchpad_rule_fails(self):
        self.put("spike", skill_md(name="spike", body="# Spike\n"))
        self.assertFails("spike/SKILL.md: scratchpad rule missing")

    def test_reworded_scratchpad_rule_fails(self):
        rule = SCRATCHPAD_RULE.replace("exactly as they write it", "roughly")
        self.assertNotEqual(rule, SCRATCHPAD_RULE)
        self.put("audit", skill_md(name="audit", body=f"# Audit\n\n{REPORT_RULE}\n\n{rule}\n"))
        self.assertFails("audit/SKILL.md: scratchpad rule missing")

    def test_build_without_the_build_ask_rule_fails(self):
        self.put("build", skill_md(name="build"))
        self.assertFails("build/SKILL.md: build-anyway rule missing")

    def test_build_with_the_build_ask_rule_passes(self):
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_ACCEPT_RULE}\n\n{BUILD_PATH_RULE}\n\n{BUILD_REREAD_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_reworded_build_ask_rule_fails(self):
        rule = BUILD_ASK_RULE.replace("Stop and settle them first", "Stop")
        self.assertNotEqual(rule, BUILD_ASK_RULE)
        self.put("build", skill_md(name="build", body=f"# Build\n\n{rule}\n\n{BUILD_PATH_RULE}\n"))
        self.assertFails("build/SKILL.md: build-anyway rule missing")

    # The build asks before accepting a failed correction check (ADR 0038)

    def test_build_without_the_accept_rule_fails(self):
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_PATH_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.assertFails("build/SKILL.md: build accept rule missing")

    def test_reworded_accept_rule_fails(self):
        rule = BUILD_ACCEPT_RULE.replace("or leave it?", "or fix it?")
        self.assertNotEqual(rule, BUILD_ACCEPT_RULE)
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{rule}\n\n{BUILD_PATH_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.assertFails("build/SKILL.md: build accept rule missing")

    # The build's reviews find the plan's repository (ADR 0032)

    def test_build_without_the_build_path_rule_fails(self):
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n"))
        self.assertFails("build/SKILL.md: build path rule missing")

    def test_build_path_rule_wrapped_across_lines_passes(self):
        rule = BUILD_PATH_RULE.replace(" the hook ", "\nthe hook ")
        self.assertNotEqual(rule, BUILD_PATH_RULE)
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_ACCEPT_RULE}\n\n{rule}\n\n{BUILD_REREAD_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    # The build re-reads its practices and rules at each requirement

    def test_build_without_the_reread_rule_fails(self):
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_ACCEPT_RULE}\n\n{BUILD_PATH_RULE}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.assertFails("build/SKILL.md: build re-read rule missing")

    def test_reworded_reread_rule_fails(self):
        rule = BUILD_REREAD_RULE.replace("read them before writing the code", "skim them")
        self.assertNotEqual(rule, BUILD_REREAD_RULE)
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_ACCEPT_RULE}\n\n{BUILD_PATH_RULE}\n\n{rule}\n\n{REPORT_RULE}\n\n{SCRATCHPAD_RULE}\n"))
        self.assertFails("build/SKILL.md: build re-read rule missing")

    # Build and audit end with a report file (ADR 0051)

    def test_build_audit_and_verify_without_the_report_rule_fail(self):
        self.put("build", skill_md(name="build", body=f"# Build\n\n{BUILD_ASK_RULE}\n\n{BUILD_PATH_RULE}\n"))
        self.put("audit", skill_md(name="audit"))
        self.put("verify", skill_md(name="verify"))
        done = self.check()
        self.assertIn("build/SKILL.md: report rule missing", done.stdout)
        self.assertIn("audit/SKILL.md: report rule missing", done.stdout)
        self.assertIn("verify/SKILL.md: report rule missing", done.stdout)

    def test_reworded_report_rule_fails(self):
        rule = REPORT_RULE.replace("never paste", "avoid pasting")
        self.assertNotEqual(rule, REPORT_RULE)
        self.put("audit", skill_md(name="audit", body=f"# Audit\n\n{rule}\n"))
        self.assertFails("audit/SKILL.md: report rule missing")

    def test_other_skills_need_no_report_rule(self):
        self.put("feedback", skill_md(name="feedback", body=f"# Feedback\n\n{pointer('feedback')}\n"))
        done = self.check()
        self.assertNotIn("report rule", done.stdout)

    def test_the_asking_skills_are_the_document_skills_and_practices(self):
        self.assertEqual(sorted(ASK_SKILLS), ["adr", "brief", "plan", "practices", "spec", "spike"])

    def test_status_skill_without_signoff_rule_fails(self):
        self.put("adr", skill_md(name="adr", body=f"# ADR\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n"))
        self.assertFails("adr/SKILL.md: sign-off rule missing")

    def test_brief_has_no_status_so_needs_no_signoff_rule(self):
        self.put("brief", skill_md(name="brief", body=f"# Brief\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{pointer('brief')}\n"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_reworded_signoff_rule_fails(self):
        rule = SIGNOFF_RULE.replace("does not count", "counts")
        self.assertNotEqual(rule, SIGNOFF_RULE)
        self.put("plan", skill_md(name="plan", body=f"# Plan\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{rule}\n"))
        self.assertFails("plan/SKILL.md: sign-off rule missing")

    def test_status_skill_without_date_rule_fails(self):
        body = f"# ADR\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{SIGNOFF_RULE}\n"
        self.put("adr", skill_md(name="adr", body=body))
        self.assertFails("adr/SKILL.md: date rule missing")

    def test_reworded_date_rule_fails(self):
        rule = DATE_RULE.replace("never", "seldom")
        self.assertNotEqual(rule, DATE_RULE)
        body = f"# Spike\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{SIGNOFF_RULE}\n\n{rule}\n"
        self.put("spike", skill_md(name="spike", body=body))
        self.assertFails("spike/SKILL.md: date rule missing")

    def test_brief_needs_no_date_rule(self):
        self.put("brief", skill_md(name="brief", body=f"# Brief\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{pointer('brief')}\n"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_the_status_skills_are_the_four_with_a_status(self):
        self.assertEqual(sorted(STATUS_SKILLS), ["adr", "plan", "spec", "spike"])

    # Every skill that offers diagrams offers them the same way

    def adr_body(self, rules):
        return "# ADR\n\n" + "\n\n".join([TYPE_RULE, PROPOSED_RULE, ASK_RULE, SIGNOFF_RULE, DATE_RULE, RENAME_RULE, pointer("adr"), *rules]) + "\n"

    def test_diagram_skill_with_every_diagram_rule_passes(self):
        self.put("adr", skill_md(name="adr", body=self.adr_body(diagram_rules("ADR"))))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_diagram_skill_missing_a_diagram_rule_fails(self):
        for missing in range(len(diagram_rules("ADR"))):
            rules = [rule for i, rule in enumerate(diagram_rules("ADR")) if i != missing]
            self.put("adr", skill_md(name="adr", body=self.adr_body(rules)))
            self.assertFails(f"adr/SKILL.md: diagram rule {missing + 1} missing")

    def test_diagram_rules_name_the_skills_own_document(self):
        self.put("adr", skill_md(name="adr", body=self.adr_body(diagram_rules("plan"))))
        self.assertFails("adr/SKILL.md: diagram rule")

    def test_the_question_is_asked_word_for_word(self):
        self.assertIn("\"Would you like to add any of these diagrams to the ADR, or propose another?\"",
                      " ".join(diagram_rules("ADR")))

    def test_skills_that_offer_no_diagrams_need_no_diagram_rules(self):
        self.put("brief", skill_md(name="brief", body=f"# Brief\n\n{TYPE_RULE}\n\n{PROPOSED_RULE}\n\n{RENAME_RULE}\n\n{ASK_RULE}\n\n{pointer('brief')}\n"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_diagram_offer_sits_outside_the_question_count(self):
        # The offer comes after every counted question is settled, so numbering it would run past
        # the count the person was given ("of 3", then a fourth).
        rules = " ".join(DIAGRAM_RULES)
        self.assertIn("Ask the offer unnumbered", rules)
        self.assertIn('"**Optional: diagrams**"', rules)
        self.assertIn("outside the question count", rules)

    def test_every_diagram_skill_names_a_document_skill(self):
        self.assertTrue(set(DIAGRAM_SKILLS) <= set(DOCUMENT_SKILLS))

    # Every reviewer reports in the same shape

    def reviewer(self, *rules):
        return "---\nname: x\n---\n\n" + "\n\n".join(rules) + "\n"

    def test_reviewer_missing_a_report_rule_fails(self):
        self.put_agent("feedback-reviewer", self.reviewer(*REPORT_RULES[:2]))
        self.assertFails("agents/feedback-reviewer.md: report rule 3 missing")

    def test_reviewer_of_a_document_with_questions_needs_the_questions_rule(self):
        self.put_agent("brief-reviewer", self.reviewer(AGENT_RULE, *REPORT_RULES))
        self.assertFails("agents/brief-reviewer.md: questions rule missing")

    def test_reviewer_with_every_rule_passes(self):
        self.put_agent("brief-reviewer", self.reviewer(AGENT_RULE, *REPORT_RULES, QUESTIONS_RULE))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_reviewers_without_open_questions_need_no_questions_rule(self):
        self.put_agent("practices-reviewer", self.reviewer(AGENT_RULE, *REPORT_RULES))
        self.put_agent("feedback-reviewer", self.reviewer(*REPORT_RULES))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_no_skills_folder_passes(self):
        self.assertEqual(self.check().returncode, 0)

    def test_missing_frontmatter_fails(self):
        self.put("demo", "# Demo\n")
        self.assertFails("demo/SKILL.md: no frontmatter")

    def test_missing_name_fails(self):
        self.put("demo", f"---\ndescription: {DESCRIPTION}\n---\n\n# Demo\n")
        self.assertFails("name is missing")

    def test_name_must_match_folder(self):
        self.put("demo", skill_md(name="other"))
        self.assertFails("does not match its folder")

    def test_name_format(self):
        for bad in ["Demo", "de--mo", "-demo", "demo-", "de_mo"]:
            with self.subTest(bad=bad):
                self.put(bad, skill_md(name=bad))
                self.assertFails("lowercase letters, digits and single hyphens")

    def test_name_at_most_64_characters(self):
        self.put("a" * 65, skill_md(name="a" * 65))
        self.assertFails("over 64 characters")

    def test_name_may_be_64_characters(self):
        self.put("a" * 64, skill_md(name="a" * 64))
        self.assertEqual(self.check().returncode, 0)

    def test_name_has_no_reserved_word(self):
        for bad in ["claude-helper", "anthropic-tools"]:
            with self.subTest(bad=bad):
                self.put(bad, skill_md(name=bad))
                self.assertFails("reserved word")

    def test_missing_description_fails(self):
        self.put("demo", "---\nname: demo\n---\n\n# Demo\n")
        self.assertFails("description is missing")

    def test_description_at_most_1024_characters(self):
        self.put("demo", skill_md(description="a" * 1025))
        self.assertFails("over 1,024 characters")

    def test_description_may_be_1024_characters(self):
        self.put("demo", skill_md(description="a" * 1024))
        self.assertEqual(self.check().returncode, 0)

    def test_description_has_no_angle_brackets(self):
        self.put("demo", skill_md(description="Use for <thing> work."))
        self.assertFails("angle brackets")

    def test_quoted_description_is_measured_without_quotes(self):
        self.put("demo", skill_md(description='"' + "a" * 1024 + '"'))
        self.assertEqual(self.check().returncode, 0)

    # skill_md puts a blank line between the frontmatter and the body, which counts as a line.
    def test_body_under_500_lines(self):
        self.put("demo", skill_md(body="x\n" * 499))
        self.assertFails("500 lines")

    def test_body_of_499_lines_passes(self):
        self.put("demo", skill_md(body="x\n" * 498))
        self.assertEqual(self.check().returncode, 0)

    def test_body_about_5000_tokens(self):
        self.put("demo", skill_md(body=("word " * 20 + "\n") * 210))
        self.assertFails("5,000 tokens")

    def test_reports_every_failing_skill(self):
        self.put("one", skill_md(name="One"))
        self.put("two", "# Two\n")
        out = self.check().stdout
        self.assertIn("one/SKILL.md", out)
        self.assertIn("two/SKILL.md", out)

    def put_rubric(self, folder, text):
        path = os.path.join(self.tmp.name, "skills", folder, "references", "rubric.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def test_rubric_counting_words_per_sentence_fails(self):
        self.put("demo", skill_md())
        self.put_rubric("demo", "11. **Readable.** Sentences are under 25 words.\n")
        self.assertFails("demo/references/rubric.md: count rule")

    def test_rubric_counting_sentences_fails(self):
        self.put("demo", skill_md())
        self.put_rubric("demo", "4. **Question.** Names the choice in at most three sentences.\n")
        self.assertFails("count rule")

    def test_rubric_counting_sentences_per_paragraph_fails(self):
        self.put("demo", skill_md())
        self.put_rubric("demo", "11. Paragraphs at most 3 sentences.\n")
        self.assertFails("count rule")

    def test_rubric_count_wrapped_across_lines_fails(self):
        self.put("demo", skill_md())
        self.put_rubric("demo", "5. The reason follows in up to\n   two sentences.\n")
        self.assertFails("count rule")

    def test_rubric_word_budget_and_shape_rules_pass(self):
        self.put("demo", skill_md())
        self.put_rubric("demo", "The plain part, at most 500 words, is checked by a script.\n"
                                "2. **One story.** Story is one sentence.\n"
                                "3. Each requirement has exactly one rule sentence.\n")
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_other_wordings_of_a_count_fail(self):
        for wording in ("Each sentence is under 25 words.", "Sentences under twenty-five words.",
                        "No sentence over 25 words.", "At most 25 words per sentence.",
                        "Sentences shorter than 25 words.", "In one to three sentences.",
                        "In 3 sentences or fewer.", "In two or three sentences."):
            with self.subTest(wording=wording):
                self.put("demo", skill_md())
                self.put_rubric("demo", wording + "\n")
                self.assertFails("count rule")

    def test_reviewer_agent_counting_sentences_fails(self):
        self.put_agent("demo-reviewer", "Fail any sentence over 25 words.\n")
        self.assertFails("agents/demo-reviewer.md: count rule")

    def test_skill_md_may_give_counts_as_guidance(self):
        self.put("demo", skill_md(body="# Demo\n\nAim for sentences under 25 words.\n"))
        self.assertEqual(self.check().returncode, 0)

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("agentskills.io", done.stdout)


if __name__ == "__main__":
    unittest.main()

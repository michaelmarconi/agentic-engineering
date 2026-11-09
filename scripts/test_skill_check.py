import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "skill_check.py")
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from skill_check import AGENT_RULE, DOCUMENT_SKILLS, PATH_RULE, REVIEW_RULE, TYPE_RULE  # noqa: E402

DESCRIPTION = "Write a thing. Use whenever someone wants a thing."


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

    def test_reviewing_skill_without_review_rule_fails(self):
        body = "# Demo\n\nStart the `sdlc:correction-checker` agent.\n"
        self.put("demo", skill_md(body=body))
        self.assertFails("demo/SKILL.md: review rule missing")

    def test_reviewing_skill_with_review_rule_passes(self):
        rule = REVIEW_RULE.replace(" walk-through ends,", "\nwalk-through ends,")
        self.assertNotEqual(rule, REVIEW_RULE)
        body = f"# Demo\n\nStart the `sdlc:correction-checker` agent.\n\n{rule}\n"
        self.put("demo", skill_md(body=body))
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_reworded_review_rule_fails(self):
        rule = REVIEW_RULE.replace("run the sequence once", "run the sequence each time")
        self.assertNotEqual(rule, REVIEW_RULE)
        body = f"# Demo\n\nStart the `sdlc:correction-checker` agent.\n\n{rule}\n"
        self.put("demo", skill_md(body=body))
        self.assertFails("review rule missing")

    def test_build_checker_needs_no_review_rule(self):
        body = "# Demo\n\nStart the `sdlc:build-correction-checker` agent.\n"
        self.put("demo", skill_md(body=body))
        self.assertEqual(self.check().returncode, 0)

    def test_skill_that_runs_no_review_needs_no_review_rule(self):
        self.put("demo", skill_md())
        self.assertEqual(self.check().returncode, 0)

    # Reviews find the document's repository (ADR 0022)

    def reviewing(self, document_line, extra=""):
        return (f"# Demo\n\nStart the `sdlc:correction-checker` agent.\n\n{REVIEW_RULE}\n\n"
                f"```\n{document_line}\n```\n{extra}")

    def test_reviewing_skill_without_path_rule_fails(self):
        self.put("demo", skill_md(body=self.reviewing("Document: <the demo's full path>")))
        self.assertFails("demo/SKILL.md: path rule missing")

    def test_reviewing_skill_with_path_rule_passes(self):
        rule = PATH_RULE.replace(" the one ", "\nthe one ")
        self.assertNotEqual(rule, PATH_RULE)
        self.put("demo", skill_md(body=self.reviewing("Document: <the demo's full path>", rule)))
        done = self.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_draft_never_saved_needs_no_path_rule(self):
        self.put("demo", skill_md(body=self.reviewing("Document: feedback draft")))
        self.assertEqual(self.check().returncode, 0)

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
                                   "correction-checker", "auditor", "audit-checker"})

    def test_document_skill_without_type_rule_fails(self):
        self.put("spec", skill_md(name="spec"))
        self.assertFails("spec/SKILL.md: type rule missing")

    def test_document_skill_with_type_rule_passes(self):
        self.put("spec", skill_md(name="spec", body=f"# Spec\n\n{TYPE_RULE}\n"))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_reworded_type_rule_fails(self):
        rule = TYPE_RULE.replace("never", "seldom")
        self.assertNotEqual(rule, TYPE_RULE)
        self.put("plan", skill_md(name="plan", body=f"# Plan\n\n{rule}\n"))
        self.assertFails("plan/SKILL.md: type rule missing")

    def test_other_skills_need_no_type_rule(self):
        for name in ("practices", "feedback", "audit", "build"):
            self.put(name, skill_md(name=name))
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_the_document_skills_are_the_five_that_write_lifecycle_documents(self):
        self.assertEqual(sorted(DOCUMENT_SKILLS), ["adr", "brief", "plan", "spec", "spike"])

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

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("agentskills.io", done.stdout)


if __name__ == "__main__":
    unittest.main()

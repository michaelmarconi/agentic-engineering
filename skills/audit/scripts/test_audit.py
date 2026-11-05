"""Tests for audit.py, run against lifecycle documents and git repositories made in temporary folders.

Every commit date is fixed through GIT_COMMITTER_DATE and every window is read against a fixed
--now, so no test depends on the clock (AGENTS.md rule 5).
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "audit.py")
sys.path.insert(0, HERE)
import audit  # noqa: E402

GIT_ENV = dict(GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com", GIT_COMMITTER_NAME="Test",
               GIT_COMMITTER_EMAIL="test@example.com", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
NOW = "2026-11-05T12:00:00+00:00"


def spec(status="👍 Accepted", requirements=("Import a statement",), open_questions="None.", extra=""):
    body = "".join(f"### Requirement: {name}\n\nThe system SHALL do it.\n\n" for name in requirements)
    return (f"---\nstatus: {status}\n---\n\n# Statement import\n\n## Problem\n\nP.\n\n## Requirements\n\n"
            f"{body}{extra}## Open questions\n\n- {open_questions}\n")


def adr(status="👍 Accepted", supersedes=None, superseded_by=None, open_questions="None.", extra=""):
    lines = [f"status: {status}", "date: 2026-11-01"]
    if supersedes:
        lines.append(f"supersedes: {supersedes}")
    if superseded_by:
        lines.append(f"superseded-by: {superseded_by}")
    return ("---\n" + "\n".join(lines) + "\n---\n\n# Keep amounts in cents\n\n## Context and Problem Statement\n\n"
            f"C.{extra}\n\n### Confirmation\n\nApplies to: money.\nChecked by: test.\n\n## Open questions\n\n- {open_questions}\n")


def plan(status="📝 Draft", specs=(("statement-import.spec.md", ("Import a statement",)),), adrs=(), open_questions="None."):
    spec_lines = "".join(f"- [Spec](../specs/{name})\n" + "".join(f"  - Requirement: {r}\n" for r in reqs)
                         for name, reqs in specs) or "None.\n"
    adr_lines = "".join(f"- [{name[:4]} ADR](../adrs/{name})\n" for name in adrs) or "None.\n"
    return (f"---\nstatus: {status}\n---\n\n# Work\n\n## Specs\n\n{spec_lines}\n## ADRs\n\n{adr_lines}\n"
            f"## Decisions\n\nNone.\n\n## Plan\n\nDo it.\n\n## Open questions\n\n- {open_questions}\n")


def spike(status="📝 Draft", open_questions="None."):
    return (f"---\nstatus: {status}\n---\n\n# Can it?\n\n## Question\n\nCan it?\n\n## Open questions\n\n"
            f"- {open_questions}\n\n## Code\n\n## Runs\n")


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = os.path.join(self.tmp.name, "project")
        self.data = os.path.join(self.tmp.name, "data")
        os.makedirs(self.project)

    def put(self, relative, text):
        path = pathlib.Path(self.project, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args, date="2026-11-01T12:00:00+00:00", cwd=None):
        env = {**os.environ, **GIT_ENV, "GIT_COMMITTER_DATE": date, "GIT_AUTHOR_DATE": date}
        return subprocess.run(["git", *args], cwd=cwd or self.project, env=env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def init(self):
        self.git("init", "-q", "-b", "main")

    def commit(self, message="Change", date="2026-11-01T12:00:00+00:00"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message, date=date)
        return self.git("rev-parse", "HEAD")

    def run_audit(self, *args):
        done = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True,
                              cwd=self.project, env={**os.environ, **GIT_ENV})
        return done

    def documents(self):
        done = self.run_audit("documents")
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def problems(self, check=None):
        found = self.documents()["problems"]
        return [p for p in found if check is None or p["check"] == check]

    def window(self, *words):
        return self.run_audit("window", *words, "--data", self.data, "--now", NOW)


class Documents(Project):
    def test_no_lifecycle_documents_says_so(self):
        out = self.documents()
        self.assertFalse(out["lifecycle"])
        self.assertEqual(out["accepted"], {"specs": [], "adrs": []})
        self.assertEqual(out["problems"], [])

    def test_accepted_specs_and_adrs_are_listed_and_others_are_not(self):
        self.put("docs/specs/statement-import.spec.md", spec())
        self.put("docs/specs/sub/refunds.spec.md", spec())
        self.put("docs/specs/exports.spec.md", spec(status="📝 Draft"))
        self.put("docs/adrs/0001-cents.md", adr())
        self.put("docs/adrs/0002-floats.md", adr(status="❌ Rejected"))
        self.put("docs/adrs/0003-old.md", adr(status="📝 Draft"))
        out = self.documents()
        self.assertTrue(out["lifecycle"])
        self.assertEqual(out["accepted"], {
            "specs": ["docs/specs/statement-import.spec.md", "docs/specs/sub/refunds.spec.md"],
            "adrs": ["docs/adrs/0001-cents.md"]})
        self.assertEqual(out["problems"], [])

    def test_a_brief_alone_is_a_lifecycle_with_nothing_accepted(self):
        self.put("docs/brief.md", "# Product\n\nWhat it is.\n")
        out = self.documents()
        self.assertTrue(out["lifecycle"])
        self.assertEqual(out["accepted"], {"specs": [], "adrs": []})

    def test_a_status_without_its_emoji_or_unknown_is_a_problem(self):
        self.put("docs/specs/statement-import.spec.md", spec(status="Accepted"))
        self.put("docs/adrs/0001-cents.md", adr(status="Approved"))
        self.put("docs/plans/2026-11-01-work.md", plan(status="🟢 Built"))
        self.put("docs/spikes/2026-11-01-can-it.md", spike(status="Answered"))
        found = {p["document"]: p["detail"] for p in self.problems("status")}
        self.assertEqual(sorted(found), ["docs/adrs/0001-cents.md", "docs/plans/2026-11-01-work.md",
                                         "docs/specs/statement-import.spec.md", "docs/spikes/2026-11-01-can-it.md"])
        self.assertIn("`👍 Accepted`", found["docs/specs/statement-import.spec.md"])
        self.assertIn("`✅ Built`", found["docs/plans/2026-11-01-work.md"])

    def test_a_status_written_without_the_variation_selector_is_fine(self):
        self.put("docs/adrs/0001-cents.md", adr(status="↪ Superseded", superseded_by="0002"))
        self.put("docs/adrs/0002-new.md", adr(supersedes="0001"))
        self.assertEqual(self.problems(), [])

    def test_a_spec_with_a_status_specs_no_longer_have_is_a_problem(self):
        self.put("docs/specs/statement-import.spec.md", spec(status="🟢 Ready to build"))
        self.assertEqual(len(self.problems("status")), 1)

    def test_a_document_missing_its_status_is_a_problem_but_other_files_are_left_alone(self):
        self.put("docs/specs/statement-import.spec.md", "# Statement import\n")
        self.put("docs/adrs/0001-cents.md", "# Keep amounts in cents\n")
        self.put("docs/adrs/README.md", "# Our decisions\n")
        self.put("docs/plans/notes.md", "# Notes\n")
        found = sorted(p["document"] for p in self.problems("status"))
        self.assertEqual(found, ["docs/adrs/0001-cents.md", "docs/specs/statement-import.spec.md"])

    def test_open_questions_on_a_settled_document_are_a_problem(self):
        self.put("docs/specs/statement-import.spec.md", spec(open_questions="What about refunds?"))
        self.put("docs/specs/exports.spec.md", spec(status="📝 Draft", open_questions="Which format?"))
        self.put("docs/adrs/0001-cents.md", adr(open_questions="Which currency?"))
        self.put("docs/plans/2026-11-01-work.md", plan(status="🟢 Ready to build", open_questions="When?"))
        self.put("docs/spikes/2026-11-01-can-it.md", spike(status="🟢 Ready to run", open_questions="How?"))
        found = sorted(p["document"] for p in self.problems("open questions"))
        self.assertEqual(found, ["docs/adrs/0001-cents.md", "docs/plans/2026-11-01-work.md",
                                 "docs/specs/statement-import.spec.md", "docs/spikes/2026-11-01-can-it.md"])

    def test_references_follow_the_references_rule(self):
        self.put("docs/brief.md", "# Product\n\nSee [import](specs/statement-import.spec.md).\n")
        self.put("docs/specs/statement-import.spec.md",
                 spec(extra="Amounts follow docs/adrs/0001-cents.md.\n\n"))
        self.put("docs/specs/exports.spec.md", spec(extra="Built by `2026-11-01-work.md`.\n\n"))
        self.put("docs/adrs/0001-cents.md", adr(extra=" Like ADR 0002, unlike [the old one](0002-floats.md)."))
        self.put("docs/adrs/0002-floats.md", adr(extra=" Unlike ADR 0001."))
        self.put("docs/plans/2026-11-01-work.md", plan(adrs=("0001-cents.md",)))
        self.put("docs/spikes/2026-11-01-can-it.md",
                 spike().replace("Can it?\n\n## Open", "Can it? For docs/specs/exports.spec.md, not "
                                 "docs/plans/2026-11-01-work.md.\n\n## Open"))
        found = sorted((p["document"], p["detail"]) for p in self.problems("references"))
        self.assertEqual([document for document, _ in found], [
            "docs/adrs/0001-cents.md", "docs/brief.md", "docs/specs/exports.spec.md",
            "docs/specs/statement-import.spec.md", "docs/spikes/2026-11-01-can-it.md"])
        self.assertIn("docs/plans/2026-11-01-work.md", dict(found)["docs/spikes/2026-11-01-can-it.md"])
        self.assertNotIn("exports.spec.md", dict(found)["docs/spikes/2026-11-01-can-it.md"])

    def test_a_reference_in_frontmatter_comments_or_supersede_fields_is_fine(self):
        self.put("docs/adrs/0001-cents.md", adr(status="↪️ Superseded", superseded_by="0002"))
        self.put("docs/adrs/0002-new.md", adr(supersedes="0001"))
        self.assertEqual(self.problems("references"), [])

    def test_supersede_fields_must_agree_both_ways(self):
        self.put("docs/adrs/0001-a.md", adr(status="↪️ Superseded", superseded_by="0002"))
        self.put("docs/adrs/0002-b.md", adr())
        self.put("docs/adrs/0003-c.md", adr())
        self.put("docs/adrs/0004-d.md", adr(supersedes="0003"))
        self.put("docs/adrs/0005-e.md", adr(status="↪️ Superseded"))
        self.put("docs/adrs/0006-f.md", adr(supersedes="0009"))
        found = sorted(p["document"] for p in self.problems("supersede"))
        self.assertEqual(found, ["docs/adrs/0001-a.md", "docs/adrs/0004-d.md", "docs/adrs/0005-e.md",
                                 "docs/adrs/0006-f.md"])

    def test_a_draft_adr_naming_the_one_it_will_supersede_is_fine(self):
        self.put("docs/adrs/0001-a.md", adr())
        self.put("docs/adrs/0002-b.md", adr(status="📝 Draft", supersedes="0001"))
        self.assertEqual(self.problems("supersede"), [])

    def test_a_ready_plan_must_still_name_accepted_documents_and_existing_requirements(self):
        self.put("docs/specs/statement-import.spec.md", spec(requirements=("Import a statement",)))
        self.put("docs/specs/exports.spec.md", spec(status="📝 Draft"))
        self.put("docs/plans/2026-11-01-good.md", plan(status="🟢 Ready to build"))
        self.put("docs/plans/2026-11-02-draft-spec.md",
                 plan(status="🟢 Ready to build", specs=(("exports.spec.md", ("Import a statement",)),)))
        self.put("docs/plans/2026-11-03-gone.md",
                 plan(status="🟢 Ready to build", specs=(("statement-import.spec.md", ("Refunds",)),)))
        self.put("docs/plans/2026-11-04-draft.md",
                 plan(status="📝 Draft", specs=(("exports.spec.md", ("Refunds",)),)))
        found = {p["document"]: p["detail"] for p in self.problems("ready plan")}
        self.assertEqual(sorted(found), ["docs/plans/2026-11-02-draft-spec.md", "docs/plans/2026-11-03-gone.md"])
        self.assertIn("Refunds", found["docs/plans/2026-11-03-gone.md"])

    def test_two_unbuilt_plans_naming_one_requirement_overlap(self):
        self.put("docs/specs/statement-import.spec.md", spec())
        self.put("docs/plans/2026-11-01-a.md", plan())
        self.put("docs/plans/2026-11-02-b.md", plan(status="🟢 Ready to build"))
        self.put("docs/plans/2026-11-03-c.md", plan(status="✅ Built"))
        found = self.problems("overlap")
        self.assertEqual(len(found), 1)
        self.assertIn("Import a statement", found[0]["detail"])
        self.assertIn("2026-11-02-b.md", found[0]["detail"] + found[0]["document"])
        self.assertIn("2026-11-01-a.md", found[0]["detail"] + found[0]["document"])

    def test_overlap_includes_plans_on_other_branches_git_knows(self):
        self.init()
        self.put("docs/specs/statement-import.spec.md", spec())
        self.commit("Start")
        self.git("checkout", "-q", "-b", "other")
        self.put("docs/plans/2026-11-02-elsewhere.md", plan())
        self.commit("Plan elsewhere")
        self.git("checkout", "-q", "main")
        self.put("docs/plans/2026-11-01-here.md", plan())
        found = self.problems("overlap")
        self.assertEqual(len(found), 1)
        self.assertIn("other", found[0]["detail"])
        self.assertIn("2026-11-02-elsewhere.md", found[0]["detail"])

    def test_the_same_plan_on_several_branches_does_not_overlap_itself(self):
        self.init()
        self.put("docs/specs/statement-import.spec.md", spec())
        self.put("docs/plans/2026-11-01-here.md", plan())
        self.commit("Start")
        self.git("branch", "copy")
        self.assertEqual(self.problems("overlap"), [])

    def test_a_plan_built_on_another_branch_is_not_an_overlap_there(self):
        self.init()
        self.put("docs/specs/statement-import.spec.md", spec())
        self.put("docs/plans/2026-11-01-a.md", plan(status="✅ Built"))
        self.commit("Start")
        self.git("checkout", "-q", "-b", "old")
        self.put("docs/plans/2026-11-01-a.md", plan())
        self.commit("Old copy")
        self.git("checkout", "-q", "main")
        self.put("docs/plans/2026-11-02-b.md", plan())
        self.assertEqual(self.problems("overlap"), [])

    def test_built_plans_and_spike_records_are_listed(self):
        self.put("docs/plans/2026-11-01-a.md", plan(status="✅ Built", specs=()))
        self.put("docs/plans/2026-11-02-b.md", plan(specs=()))
        self.put("docs/spikes/2026-10-01-done.md", spike(status="💡 Answered"))
        self.put("docs/spikes/2026-10-02-gave-up.md", spike(status="❔ Not answered"))
        self.put("docs/spikes/2026-10-03-open.md", spike(status="📝 Draft"))
        self.put("docs/spikes/2026-10-04-ready.md", spike(status="🟢 Ready to run"))
        out = self.documents()
        self.assertEqual(out["built_plans"], ["docs/plans/2026-11-01-a.md"])
        self.assertEqual(out["finished_spikes"], ["docs/spikes/2026-10-01-done.md", "docs/spikes/2026-10-02-gave-up.md"])
        self.assertEqual(out["unfinished_spikes"], [
            {"document": "docs/spikes/2026-10-03-open.md", "status": "📝 Draft", "date": "2026-10-03"},
            {"document": "docs/spikes/2026-10-04-ready.md", "status": "🟢 Ready to run", "date": "2026-10-04"}])

    def test_documents_never_change_the_working_tree(self):
        self.init()
        self.put("docs/specs/statement-import.spec.md", spec(status="Accepted"))
        self.commit("Start")
        self.documents()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_a_project_folder_can_be_named(self):
        self.put("docs/specs/statement-import.spec.md", spec())
        done = subprocess.run([sys.executable, SCRIPT, "documents", "--project", self.project],
                              capture_output=True, text=True, cwd=self.tmp.name)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["accepted"]["specs"], ["docs/specs/statement-import.spec.md"])


if __name__ == "__main__":
    unittest.main()

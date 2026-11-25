"""Tests for verify.py, run against throwaway git repositories made in each test."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify  # noqa: E402
import agent_relay  # noqa: E402  (verify.py puts the plugin's scripts/ on the path)

ENV = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com",
           GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

SPEC = """---
type: Spec
status: {status}
date: 2026-11-10
---

# Mail pull

## Story

The owner wants mail pulled so they can read it offline.

## Requirements

### 1. Pull new mail

When the owner runs a pull, the system SHALL fetch each new message.

| Example | New mail |
|---|---|
| Given | two new messages on the server |
| When | the owner runs a pull |
| Then | both are stored |

| Example | No new mail |
|---|---|
| Given | no new messages |
| When | the owner runs a pull |
| Then | nothing is stored |

#### How we'll check

Test.

### 2. Report the count

When a pull ends, the system SHALL print how many messages it fetched.

| Example | Count |
|---|---|
| Given | two new messages |
| When | the owner runs a pull |
| Then | it prints 2 |

#### How we'll check

Test.

## Open questions

- None.
"""


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = os.path.join(self.tmp.name, "repo")
        self.data = os.path.join(self.tmp.name, "s1", "scratchpad", "agentic")
        os.makedirs(os.path.dirname(self.data), exist_ok=True)
        os.makedirs(self.repo)
        self.git("init", "-q", "-b", "main")
        self.put("docs/specs/mail-pull.spec.md", SPEC.format(status="Accepted 👍"))
        self.put("docs/specs/send.spec.md", SPEC.format(status="Draft 📝"))
        self.put("src/app.py", "print('hi')\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, *args], env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def run_script(self, *argv, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = verify.main(list(argv))
        finally:
            sys.stdin = old
        return code, out.getvalue(), err.getvalue()

    def start(self, *specs):
        return self.run_script("start", *specs, "--project", self.repo, "--scratchpad", os.path.dirname(self.data), "--session", "s1")

    def report(self, own, scope="mail-pull", commit=None):
        commit = commit or self.git("rev-parse", "HEAD")
        return self.run_script("report", "--scope", scope, "--commit", commit, "--project", self.repo, "--scratchpad", os.path.dirname(self.data),
                               "--session", "s1", "--now", "2026-11-16T10:00:00+00:00", stdin=own)


class Start(Repo):
    def test_notes_the_commit(self):
        code, out, _ = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual(result["commit"], self.git("rev-parse", "HEAD"))
        self.assertEqual(result["root"], os.path.realpath(self.repo))

    def test_lists_requirements_with_their_examples(self):
        _, out, _ = self.start("docs/specs/mail-pull.spec.md")
        spec = json.loads(out)["specs"][0]
        self.assertEqual(spec["path"], "docs/specs/mail-pull.spec.md")
        self.assertTrue(spec["accepted"])
        self.assertEqual(spec["requirements"], [{"number": 1, "name": "Pull new mail", "examples": 2},
                                                {"number": 2, "name": "Report the count", "examples": 1}])

    def test_spec_not_accepted_is_listed_with_its_status(self):
        _, out, _ = self.start("docs/specs/send.spec.md")
        spec = json.loads(out)["specs"][0]
        self.assertFalse(spec["accepted"])
        self.assertEqual(spec["status"], "Draft 📝")

    def test_spec_in_the_old_layout_flagged(self):
        self.put("docs/specs/old.spec.md", "---\nstatus: Accepted 👍\n---\n\n# Old\n\n## Requirements\n\n"
                                           "### Requirement: Count words\n\n#### Scenario: three\n")
        self.commit()
        _, out, _ = self.start("docs/specs/old.spec.md")
        spec = json.loads(out)["specs"][0]
        self.assertTrue(spec["old_layout"])
        self.assertEqual(spec["requirements"], [])

    def test_current_layout_not_flagged(self):
        _, out, _ = self.start("docs/specs/mail-pull.spec.md")
        self.assertFalse(json.loads(out)["specs"][0]["old_layout"])

    def test_every_spec_when_none_named(self):
        _, out, _ = self.start()
        self.assertEqual([s["path"] for s in json.loads(out)["specs"]],
                         ["docs/specs/mail-pull.spec.md", "docs/specs/send.spec.md"])

    def test_full_path_is_read_relative_to_the_repository(self):
        _, out, _ = self.start(os.path.join(self.repo, "docs/specs/mail-pull.spec.md"))
        self.assertEqual(json.loads(out)["specs"][0]["path"], "docs/specs/mail-pull.spec.md")

    def test_missing_spec_refused(self):
        code, out, err = self.start("docs/specs/nope.spec.md")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("docs/specs/nope.spec.md", err)

    def test_a_plan_refused_with_what_to_do(self):
        self.put("docs/plans/2026-11-12-word-count.md", "---\ntype: Plan\n---\n")
        self.commit()
        code, _, err = self.start("docs/plans/2026-11-12-word-count.md")
        self.assertEqual(code, 1)
        self.assertIn("Specs section", err)

    def test_missing_git_refused_with_a_reason(self):
        with mock.patch.object(verify.subprocess, "run", side_effect=FileNotFoundError("git")):
            code, out, err = self.start()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("git", err)

    def test_a_file_that_is_not_a_spec_refused(self):
        code, _, err = self.start("src/app.py")
        self.assertEqual(code, 1)
        self.assertIn("not a spec", err)

    def test_uncommitted_changes_refused(self):
        self.put("src/app.py", "print('changed')\n")
        code, out, err = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("src/app.py", err)

    def test_untracked_file_refused(self):
        self.put("notes.txt", "x\n")
        code, _, err = self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(code, 1)
        self.assertIn("notes.txt", err)

    def test_not_a_repository_refused(self):
        code, _, err = self.run_script("start", "--project", self.tmp.name, "--scratchpad", os.path.dirname(self.data), "--session", "s1")
        self.assertEqual(code, 1)
        self.assertIn("git", err)

    def test_clears_an_earlier_runs_reports(self):
        path = agent_relay.record_path(self.data, "s1", "verify")
        os.makedirs(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"reports": {"verifier|x|": {"agent": "verifier", "document": "x", "kind": "", "text": "old"}}}, f)
        self.start("docs/specs/mail-pull.spec.md")
        self.assertEqual(agent_relay.reports(self.data, "s1", "verify"), [])


DOC = "docs/specs/mail-pull.spec.md"

VERIFIER = """Document: {doc}
Started: `bin/mail serve`, started

1. Pull new mail
- New mail: pass
  - Did: Put two messages on the stand-in server, then ran a pull.
  - Saw: "2 stored"
- No new mail: not checked
  - Did: Looked for a way to empty the stand-in server.
  - Saw: the practice names none
  - Why: the practice names no way to empty the server; a reset script would make it checkable.

2. Report the count
- Count: fail
  - Did: Ran a pull with two new messages waiting.
  - Saw: "fetched"
  - Why: it printed no number.

Commands:
- bin/mail serve --port 8000 --data /tmp/tmp.x1
- bin/mail pull --port 8000
"""

CHECKER = """Document: {doc}

1. Pull new mail
- New mail: confirmed
  - Did: Pulled with two messages, then with one.
  - Saw: "2 stored", then "1 stored"
- No new mail: confirmed
  - Did: Looked for a way to empty the server.
  - Saw: none is named

2. Report the count
- Count: rejected
  - Did: Ran a pull with two new messages waiting, twice.
  - Saw: "fetched 2"
  - Why: it does print the number; verdict: pass

Commands:
- bin/mail pull --port 8000 --twice
"""

# Lines of SPEC, counted from 1: the headings and example rows the links point to.
LINE = {"1. Pull new mail": 15, "New mail": 19, "No new mail": 25, "2. Report the count": 35, "Count": 39}


class Report(Repo):
    def keep(self, agent, document, text, requested=None):
        path = agent_relay.record_path(self.data, "s1", "verify")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record = agent_relay.load(path)
        record["reports"][f"{agent}|{document}|"] = {"agent": agent, "document": document, "kind": "",
                                                     "requested": requested or [], "text": text}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f)

    def written(self, out):
        path = out.splitlines()[0][len("Report written: "):]
        with open(path, encoding="utf-8") as f:
            return path, f.read()

    def section(self, text, heading):
        return text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]

    def both(self, verifier=VERIFIER, checker=CHECKER):
        full = os.path.join(self.repo, DOC)
        self.keep("verifier", full, verifier.format(doc=full))
        if checker is not None:
            self.keep("verify-checker", full, checker.format(doc=full))

    def run_both(self, own="## What needs doing\n\n1. Add a reset script.\n", **kw):
        self.start(DOC)
        self.both(**kw)
        code, out, err = self.report(own)
        self.assertEqual(code, 0, err)
        return self.written(out)[1]

    def github(self):
        self.git("remote", "add", "origin", "https://github.com/acme/mail.git")
        short = self.git("rev-parse", "--short=7", "HEAD")
        return f"https://github.com/acme/mail/blob/{short}/{DOC}"

    def test_spec_lines_the_tests_rely_on(self):
        lines = SPEC.format(status="Accepted 👍").splitlines()
        self.assertEqual(lines[LINE["1. Pull new mail"] - 1], "### 1. Pull new mail")
        self.assertEqual(lines[LINE["New mail"] - 1], "| Example | New mail |")
        self.assertEqual(lines[LINE["No new mail"] - 1], "| Example | No new mail |")
        self.assertEqual(lines[LINE["2. Report the count"] - 1], "### 2. Report the count")
        self.assertEqual(lines[LINE["Count"] - 1], "| Example | Count |")

    def test_headings_in_order_and_file_named(self):
        self.start(DOC)
        self.both()
        code, out, err = self.report("## What needs doing\n\n1. Add a reset script.\n")
        self.assertEqual(code, 0, err)
        path, text = self.written(out)
        self.assertTrue(path.endswith("2026-11-16-verify-mail-pull.md"))
        positions = [text.index(f"## {h}\n") for h in verify.run_report.HEADINGS["verify"]]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("1. Add a reset script.", self.section(text, "What needs doing"))

    def test_header_names_spec_commit_and_how_the_product_started(self):
        base = self.github()
        text = self.run_both()
        top = text.split("\n## Result", 1)[0]
        self.assertTrue(top.startswith("# Verify report: mail-pull, requirements 1 and 2\n"))
        self.assertIn(f"- **Spec:** [{DOC}]({base})", top)
        self.assertIn(f"- **Commit:** `{self.git('rev-parse', '--short=7', 'HEAD')}`", top)
        self.assertIn("- **Product:** `bin/mail serve`, started", top)

    def test_title_names_no_requirements_when_the_scope_does(self):
        self.start(DOC)
        self.both()
        code, out, err = self.report("## Caveats\n\n- None.\n", scope="mail-pull requirements 1-2")
        self.assertEqual(code, 0, err)
        self.assertTrue(self.written(out)[1].startswith("# Verify report: mail-pull requirements 1-2\n"))

    def test_counts_line_and_table(self):
        base = self.github()
        result = self.section(self.run_both(), "Result")
        self.assertIn("**1 passed, 0 failed, 1 disputed, 1 not checked.** The checker rejected 1 verdict.", result)
        self.assertIn("| # | Requirement | Example | Result |\n|--:|---|---|---|\n", result)
        self.assertIn(f"| 1 | [Pull new mail]({base}#1-pull-new-mail) | [New mail]({base}?plain=1#L{LINE['New mail']}) "
                      "| ✅ Pass |", result)
        self.assertIn(f"| 1 | [Pull new mail]({base}#1-pull-new-mail) | [No new mail]({base}?plain=1#L{LINE['No new mail']}) "
                      "| ⚠️ Not checked |", result)
        self.assertIn(f"| 2 | [Report the count]({base}#2-report-the-count) | [Count]({base}?plain=1#L{LINE['Count']}) "
                      "| ⚠️ Disputed |", result)

    def test_checker_agreeing_with_every_verdict_said(self):
        checker = CHECKER.replace("- Count: rejected", "- Count: confirmed").replace(
            "  - Why: it does print the number; verdict: pass\n", "")
        result = self.section(self.run_both(checker=checker), "Result")
        self.assertIn("**1 passed, 1 failed, 0 disputed, 1 not checked.** The checker agreed with every verdict.", result)
        self.assertIn("| ❌ Fail |", result)

    def test_details_give_each_example_both_agents_words(self):
        base = self.github()
        details = self.section(self.run_both(), "Details")
        self.assertIn(f"### 1. [New mail]({base}?plain=1#L{LINE['New mail']}) — ✅ Pass\n\n**Verifier**\n\n"
                      "- **Did:** Put two messages on the stand-in server, then ran a pull.\n"
                      "- **Saw:** \"2 stored\"\n\n**Checker** (confirmed)\n\n"
                      "- **Did:** Pulled with two messages, then with one.\n"
                      "- **Saw:** \"2 stored\", then \"1 stored\"\n", details)
        self.assertIn("### 2. [Count]", details)
        self.assertIn("**Checker** (rejected)", details)
        self.assertIn("- **Why:** it does print the number; verdict: pass", details)

    def test_every_word_of_each_agents_entries_reaches_the_file(self):
        text = self.run_both()
        for report in (VERIFIER, CHECKER):
            for line in report.splitlines():
                if line.startswith("  - "):
                    label, words = line[4:].split(": ", 1)
                    self.assertIn(f"- **{label}:** {words}", text)

    def test_commands_only_in_collapsed_blocks(self):
        text = self.run_both()
        commands = self.section(text, "Commands")
        self.assertIn("<details>\n<summary>Verifier: docs/specs/mail-pull.spec.md</summary>\n\n```text\n", commands)
        self.assertIn("<summary>Verify-checker: docs/specs/mail-pull.spec.md</summary>", commands)
        self.assertIn("- bin/mail serve --port 8000 --data /tmp/tmp.x1\n- bin/mail pull --port 8000\n", commands)
        self.assertEqual(text.count("bin/mail pull --port 8000\n"), 1)
        self.assertEqual(text.count("<details>"), text.count("</details>"))

    def test_commands_holding_backticks_get_a_longer_fence(self):
        verifier = VERIFIER.replace("- bin/mail pull --port 8000\n", "- echo ```x``` | bin/mail pull\n")
        commands = self.section(self.run_both(verifier=verifier), "Commands")
        self.assertIn("````text\n", commands)
        self.assertIn("- echo ```x``` | bin/mail pull\n````\n", commands)

    def test_not_on_github_gives_names_with_line_numbers(self):
        self.git("remote", "add", "origin", "git@gitlab.com:acme/mail.git")
        text = self.run_both()
        self.assertNotIn("https://", text)
        self.assertIn("- **Links:** Links to the spec were left out because the repository's `origin` is not on GitHub.",
                      text)
        result = self.section(text, "Result")
        self.assertIn(f"| 1 | Pull new mail (line {LINE['1. Pull new mail']}) | New mail (line {LINE['New mail']}) "
                      "| ✅ Pass |", result)
        self.assertIn(f"### 1. New mail (line {LINE['New mail']}) — ✅ Pass", self.section(text, "Details"))

    def test_no_remote_gives_names_with_line_numbers(self):
        text = self.run_both()
        self.assertIn(f"Pull new mail (line {LINE['1. Pull new mail']})", text)
        self.assertIn("is not on GitHub", text)

    def test_links_follow_the_spec_at_the_commit_checked(self):
        base = self.github()
        _, started, _ = self.start(DOC)
        commit = json.loads(started)["commit"]
        self.put(DOC, "\n\n\n" + SPEC.format(status="Accepted 👍"))
        self.commit()
        self.both()
        code, out, err = self.report("## Caveats\n\n- None.\n", commit=commit)
        self.assertEqual(code, 0, err)
        self.assertIn(f"[New mail]({base}?plain=1#L{LINE['New mail']})", self.written(out)[1])

    def test_verifier_error_lists_each_requested_requirement_not_checked(self):
        self.github()
        self.start(DOC)
        full = os.path.join(self.repo, DOC)
        self.keep("verifier", full, f"Document: {full}\nError: no Running the product practice",
                  requested=[[1, "Pull new mail"], [2, "Report the count"]])
        code, out, err = self.report("## What needs doing\n\n1. Record the practice.\n")
        self.assertEqual(code, 0, err)
        result = self.section(self.written(out)[1], "Result")
        self.assertIn("**0 passed, 0 failed, 0 disputed, 2 not checked.**", result)
        self.assertRegex(result, r"\| 1 \| \[Pull new mail\]\([^)]*\) \| — \| ⚠️ Not checked \|")
        self.assertRegex(result, r"\| 2 \| \[Report the count\]\([^)]*\) \| — \| ⚠️ Not checked \|")
        self.assertIn("The verifier checked nothing: no Running the product practice", result)

    def test_verifier_error_with_no_requirements_read_lists_the_specs(self):
        self.start(DOC)
        full = os.path.join(self.repo, DOC)
        self.keep("verifier", full, f"Document: {full}\nError: no practice")
        code, out, err = self.report("## Caveats\n\n- None.\n")
        self.assertEqual(code, 0, err)
        result = self.section(self.written(out)[1], "Result")
        self.assertIn("2 not checked.**", result)
        self.assertNotIn("agreed", result)

    def test_duplicate_example_refused(self):
        verifier = VERIFIER.replace("- No new mail: not checked", "- New mail: not checked")
        checker = CHECKER.replace("- No new mail: confirmed", "- New mail: confirmed")
        err = self.refused(verifier=verifier, checker=checker)
        self.assertIn("New mail", err)
        self.assertIn("twice", err)

    def test_quoted_lines_stay_inside_their_entry(self):
        verifier = VERIFIER.replace('  - Saw: "2 stored"\n', '  - Saw: the help text:\n  ## Usage\n')
        details = self.section(self.run_both(verifier=verifier), "Details")
        self.assertIn("- **Saw:** the help text:\n  ## Usage\n", details)
        self.assertNotIn("\n## Usage", details)

    def test_short_commit_is_lengthened_when_ambiguous(self):
        self.github()
        links = verify.Links(os.path.realpath(self.repo), self.git("rev-parse", "HEAD"))
        self.assertEqual(links.short, self.git("rev-parse", "--short=7", "HEAD"))

    def test_no_checker_report_leaves_every_example_not_checked(self):
        text = self.run_both(checker=None)
        result = self.section(text, "Result")
        self.assertIn("**0 passed, 0 failed, 0 disputed, 3 not checked.**", result)
        self.assertNotIn("agreed", result)
        self.assertIn("The checker did not report on docs/specs/mail-pull.spec.md", result)
        self.assertIn("**Checker** did not report.", self.section(text, "Details"))

    def test_checker_error_leaves_every_example_not_checked(self):
        checker = "Document: {doc}\nError: the verifier checked nothing"
        result = self.section(self.run_both(checker=checker), "Result")
        self.assertIn("3 not checked.**", result)
        self.assertIn("The checker checked nothing: the verifier checked nothing", result)

    def refused(self, verifier=VERIFIER, checker=CHECKER):
        self.start(DOC)
        self.both(verifier=verifier, checker=checker)
        code, out, err = self.report("## Caveats\n\n- None.\n")
        self.assertEqual((code, out), (1, ""))
        return err

    def test_unknown_verdict_refused_naming_the_agent_and_line(self):
        err = self.refused(verifier=VERIFIER.replace("- New mail: pass", "- New mail: passed"))
        self.assertIn("verifier", err)
        self.assertIn("line 5", err)
        self.assertIn("passed", err)

    def test_line_that_fits_no_entry_refused(self):
        err = self.refused(checker=CHECKER.replace("2. Report the count\n", "2. Report the count\nAll good here.\n"))
        self.assertIn("verify-checker", err)
        self.assertIn("All good here.", err)

    def test_example_missing_from_the_checker_refused(self):
        checker = CHECKER.replace("- No new mail: confirmed\n  - Did: Looked for a way to empty the server.\n"
                                  "  - Saw: none is named\n", "")
        err = self.refused(checker=checker)
        self.assertIn("No new mail", err)

    def test_report_with_no_document_line_refused(self):
        err = self.refused(verifier=VERIFIER.replace("Document: {doc}\n", ""))
        self.assertIn("Document:", err)

    def test_clean_repository_said(self):
        after = self.section(self.run_both(), "The repository after the run")
        self.assertIn("No tracked file changed and no new file appeared during the run", after)
        self.assertIn("still checked out", after)
        self.assertNotIn("###", after)

    def test_file_changed_during_the_run_listed(self):
        self.start(DOC)
        self.put("src/app.py", "print('touched')\n")
        self.put("tool.sh", "echo\n")
        _, out, _ = self.report("## Caveats\n\n- None.\n")
        after = self.section(self.written(out)[1], "The repository after the run")
        self.assertIn("src/app.py", after)
        self.assertIn("tool.sh", after)

    def test_new_commit_during_the_run_said(self):
        _, started, _ = self.start(DOC)
        self.put("src/app.py", "print('new')\n")
        self.commit()
        _, out, _ = self.report("## Caveats\n\n- None.\n", commit=json.loads(started)["commit"])
        after = self.section(self.written(out)[1], "The repository after the run")
        self.assertIn(self.git("rev-parse", "HEAD"), after)
        self.assertNotIn("still checked out", after)
        self.assertIn("src/app.py", after)

    def test_claude_cannot_write_the_scripts_sections(self):
        self.start(DOC)
        for heading in ("Result", "Details", "Commands"):
            code, out, err = self.report(f"## {heading}\n\nabc\n")
            self.assertEqual((code, out), (1, ""))
            self.assertIn("filled by the script", err)

    def test_unknown_commit_refused(self):
        code, out, err = self.report("## Caveats\n\n- None.\n", commit="deadbeef")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("deadbeef", err)

    def test_report_clears_kept_reports(self):
        self.run_both()
        self.assertEqual(agent_relay.reports(self.data, "s1", "verify"), [])


class Links(unittest.TestCase):
    def test_github_remotes_in_their_usual_forms(self):
        for url in ("https://github.com/acme/mail", "https://github.com/acme/mail.git",
                    "git@github.com:acme/mail.git", "ssh://git@github.com/acme/mail.git",
                    "https://token@github.com/acme/mail.git"):
            self.assertEqual(verify.github_repository(url), "https://github.com/acme/mail", url)

    def test_other_remotes_are_not_github(self):
        for url in ("git@gitlab.com:acme/mail.git", "https://example.com/github.com/acme/mail",
                    "https://github.com/acme", "", None):
            self.assertIsNone(verify.github_repository(url), url)

    def test_heading_anchor_as_github_gives_it(self):
        self.assertEqual(verify.anchor("### 2. Reply to all"), "2-reply-to-all")
        self.assertEqual(verify.anchor("### 3. Don't send `drafts` (yet)"), "3-dont-send-drafts-yet")
        self.assertEqual(verify.anchor("### 4. Café_menu -- two"), "4-café_menu----two")


class Help(unittest.TestCase):
    def test_help_names_both_commands(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit):
            verify.main(["--help"])
        self.assertIn("start", out.getvalue())
        self.assertIn("report", out.getvalue())


if __name__ == "__main__":
    unittest.main()

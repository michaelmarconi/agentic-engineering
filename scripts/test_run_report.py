"""Tests for run_report.py, the shared code that writes a build's or an audit's report file."""

import os
import stat
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_report  # noqa: E402


class Names(unittest.TestCase):
    def test_safe_keeps_ordinary_names(self):
        self.assertEqual(run_report.safe("add-numbers"), "add-numbers")

    def test_safe_replaces_unsafe_characters(self):
        self.assertEqual(run_report.safe("last 7 days"), "last-7-days")
        self.assertEqual(run_report.safe("abc123..def456"), "abc123-def456")
        self.assertEqual(run_report.safe("../../etc/passwd"), "etc-passwd")
        self.assertEqual(run_report.safe("since a/b"), "since-a-b")

    def test_safe_never_empty(self):
        self.assertEqual(run_report.safe("../"), "report")
        self.assertEqual(run_report.safe(""), "report")


class Folder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temp = os.path.join(self.tmp.name, "system-temp")
        os.makedirs(self.temp)
        patcher = mock.patch.object(run_report.tempfile, "gettempdir", return_value=self.temp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_data_folder_used(self):
        data = os.path.join(self.tmp.name, "data")
        folder, fell_back = run_report.report_folder(data, "/work/my repo")
        self.assertEqual(folder, os.path.join(data, "reports", "my-repo"))
        self.assertFalse(fell_back)
        self.assertTrue(os.path.isdir(folder))

    def test_empty_data_falls_back_to_private_folder(self):
        folder, fell_back = run_report.report_folder("", "/work/repo")
        root = os.path.join(self.temp, f"agentic-reports-{os.getuid()}")
        self.assertEqual(folder, os.path.join(root, "repo"))
        self.assertTrue(fell_back)
        self.assertEqual(stat.S_IMODE(os.stat(root).st_mode) & 0o077, 0)

    def test_unwritable_data_falls_back(self):
        data = os.path.join(self.tmp.name, "data")
        with mock.patch.object(run_report, "writable", side_effect=lambda f: not f.startswith(data)):
            folder, fell_back = run_report.report_folder(data, "/work/repo")
        self.assertTrue(fell_back)
        self.assertTrue(folder.startswith(self.temp))

    def test_fallback_others_can_open_is_refused(self):
        root = os.path.join(self.temp, f"agentic-reports-{os.getuid()}")
        os.makedirs(root)
        os.chmod(root, 0o755)
        with self.assertRaises(run_report.ReportError):
            run_report.report_folder("", "/work/repo")

    def test_fallback_symlink_is_refused(self):
        root = os.path.join(self.temp, f"agentic-reports-{os.getuid()}")
        elsewhere = os.path.join(self.tmp.name, "elsewhere")
        os.makedirs(elsewhere, mode=0o700)
        os.symlink(elsewhere, root)
        with self.assertRaises(run_report.ReportError):
            run_report.report_folder("", "/work/repo")


class Parse(unittest.TestCase):
    def test_sections_by_heading(self):
        text = "## What was built\n\nAn adder.\n\n## Choices\n\n- Named it add.\n"
        own = run_report.parse("build", text)
        self.assertEqual(own, {"What was built": "An adder.", "Choices": "- Named it add."})

    def test_unknown_heading_refused(self):
        with self.assertRaises(run_report.ReportError) as caught:
            run_report.parse("build", "## Something else\n\ntext\n")
        self.assertIn("Something else", str(caught.exception))

    def test_copied_heading_refused(self):
        with self.assertRaises(run_report.ReportError):
            run_report.parse("build", "## The hand-over script's report\n\nmy version\n")

    def test_repeated_heading_refused(self):
        with self.assertRaises(run_report.ReportError):
            run_report.parse("build", "## Choices\n\na\n\n## Choices\n\nb\n")

    def test_text_before_first_heading_refused(self):
        with self.assertRaises(run_report.ReportError):
            run_report.parse("build", "stray\n## Choices\n\na\n")

    def test_headings_inside_a_fenced_block_stay_text(self):
        text = "## Problems with the documents\n\nSet it so:\n\n```\n## Open questions\n\n- None.\n```\n"
        own = run_report.parse("audit", text)
        self.assertEqual(own, {"Problems with the documents":
                               "Set it so:\n\n```\n## Open questions\n\n- None.\n```"})

    def test_heading_after_a_closed_fence_starts_a_section(self):
        own = run_report.parse("build", "## Choices\n\n~~~\n## x\n~~~\n\n## Tests and lint\n\nOK.\n")
        self.assertEqual(set(own), {"Choices", "Tests and lint"})

    def test_deeper_headings_stay_in_their_section(self):
        own = run_report.parse("build", "## Choices\n\n### One\n\nA.\n")
        self.assertEqual(own, {"Choices": "### One\n\nA."})


class Write(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")

    def write(self, own=None, copied=None, kind="build", name="add-numbers"):
        return run_report.write(kind, name, "/work/repo", self.data, own or {}, copied or {},
                                date="2026-11-14")

    def test_path_and_headings_in_order(self):
        path, lines = self.write({"Choices": "Named it add."})
        self.assertEqual(path, os.path.join(self.data, "reports", "repo", "2026-11-14-build-add-numbers.md"))
        with open(path, encoding="utf-8") as f:
            text = f.read()
        positions = [text.index(f"## {h}\n") for h in run_report.HEADINGS["build"]]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Named it add.", text)
        self.assertEqual(lines[0], f"Report written: {path}")

    def test_empty_heading_says_nothing_to_report(self):
        path, _ = self.write()
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("## Choices\n\nNothing to report.\n", text)

    def test_copied_reports_word_for_word_under_their_heading(self):
        report = "Result: FAIL\n\n| Check | Result |\n|---|---|\n| 1 | fail: \"quoted\" |\n  indented\n"
        copied = {"What each review found": [("Build review", report)],
                  "The hand-over script's report": [("Output", "Committed.\nPushed.")]}
        path, lines = self.write({"What each review found": "Corrected check 1."}, copied)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(report, text)
        section = text[text.index("## What each review found"):text.index("## The hand-over script's report")]
        self.assertIn("Corrected check 1.", section)
        self.assertIn("### Build review\n\n" + report, section)
        self.assertIn("Committed.\nPushed.", text)
        self.assertIn(f"Copied: Build review ({len(report)} characters)", lines)
        printed = "\n".join(lines)
        self.assertIn("=== THE REPORT AS WRITTEN ===\n" + text.rstrip("\n") + "\n=== END OF THE REPORT ===", printed)

    def test_second_report_same_day_is_numbered(self):
        first, _ = self.write()
        second, _ = self.write()
        third, _ = self.write()
        self.assertTrue(second.endswith("2026-11-14-build-add-numbers-2.md"))
        self.assertTrue(third.endswith("2026-11-14-build-add-numbers-3.md"))
        self.assertTrue(os.path.exists(first))

    def test_audit_kind(self):
        path, _ = self.write(kind="audit", name="all")
        self.assertTrue(path.endswith("2026-11-14-audit-all.md"))
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for heading in run_report.HEADINGS["audit"]:
            self.assertIn(f"## {heading}\n", text)

    def test_fallback_is_said(self):
        with mock.patch.object(run_report.tempfile, "gettempdir", return_value=self.tmp.name):
            path, lines = run_report.write("build", "p", "/work/repo", "", {}, {}, date="2026-11-14")
        self.assertTrue(any("could not be written" in line for line in lines))
        self.assertTrue(path.startswith(self.tmp.name))

    def test_file_that_cannot_be_written_is_refused(self):
        with mock.patch("builtins.open", side_effect=OSError(36, "File name too long")):
            with self.assertRaises(run_report.ReportError):
                self.write()

    def test_unknown_copied_heading_refused(self):
        with self.assertRaises(run_report.ReportError):
            self.write(copied={"Nowhere": [("x", "y")]})


class Find(unittest.TestCase):
    """Finding a plan's earlier reports, newest first, and reading their sections back."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")
        self.temp = os.path.join(self.tmp.name, "system-temp")
        os.makedirs(self.temp)
        patcher = mock.patch.object(run_report.tempfile, "gettempdir", return_value=self.temp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, date, name="add-numbers", data=None, own=None, copied=None):
        return run_report.write("build", name, "/work/repo", self.data if data is None else data,
                                own or {}, copied or {}, date=date)[0]

    def test_newest_first_by_date_then_number(self):
        older = self.write("2026-11-13")
        same_day = [self.write("2026-11-14") for _ in range(10)]  # -2 to -10: 10 sorts after 9
        found = run_report.reports("build", "add-numbers", "/work/repo", self.data)
        self.assertEqual(found, list(reversed(same_day)) + [older])

    def test_other_plans_and_kinds_left_out(self):
        mine = self.write("2026-11-14")
        self.write("2026-11-15", name="add-numbers-and-more")
        run_report.write("audit", "add-numbers", "/work/repo", self.data, {}, {}, date="2026-11-16")
        self.assertEqual(run_report.reports("build", "add-numbers", "/work/repo", self.data), [mine])

    def test_nothing_found(self):
        self.assertEqual(run_report.reports("build", "add-numbers", "/work/repo", self.data), [])

    def test_fallback_read_when_the_data_folder_has_none(self):
        fallen = self.write("2026-11-14", data="")
        self.assertEqual(run_report.reports("build", "add-numbers", "/work/repo", self.data), [fallen])

    def test_data_folder_wins_over_the_fallback(self):
        self.write("2026-11-15", data="")
        mine = self.write("2026-11-14")
        self.assertEqual(run_report.reports("build", "add-numbers", "/work/repo", self.data), [mine])

    def test_fallback_others_can_open_is_ignored(self):
        self.write("2026-11-14", data="")
        os.chmod(run_report.fallback_root(), 0o755)
        self.assertEqual(run_report.reports("build", "add-numbers", "/work/repo", self.data), [])

    def test_sections_read_back(self):
        copied = {"What each review found": [("Build review", "Result: PASS\n"),
                                             ("Correction check", "Result: FAIL\n\nCorrections:\n- a: not made")],
                  "The hand-over script's report": [("Output", "Branch: b\nHead: abc")]}
        path = self.write("2026-11-14", own={"Built before sign-off": "Built early.",
                                             "What each review found": "Corrected 1."}, copied=copied)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(run_report.section("build", text, "Built before sign-off"), "Built early.")
        self.assertEqual(run_report.section("build", text, "Choices"), "Nothing to report.")
        reviews = run_report.section("build", text, "What each review found")
        self.assertEqual(run_report.subsection(reviews, "Correction check"),
                         "Result: FAIL\n\nCorrections:\n- a: not made")
        output = run_report.section("build", text, "The hand-over script's report")
        self.assertEqual(run_report.subsection(output, "Output"), "Branch: b\nHead: abc")
        self.assertIsNone(run_report.subsection(output, "Missing"))

    def test_heading_quoted_in_an_earlier_section_passed_over(self):
        own = {"What was built": "```\n## The hand-over script's report\n\n### Output\n\nHead: fake\n```"}
        copied = {"The hand-over script's report": [("Output", "Head: real")]}
        with open(self.write("2026-11-14", own=own, copied=copied), encoding="utf-8") as f:
            text = f.read()
        output = run_report.section("build", text, "The hand-over script's report")
        self.assertEqual(run_report.subsection(output, "Output"), "Head: real")

    def test_subsection_after_another_and_first_of_its_title(self):
        body = "### Build review\n\nResult: PASS\n\n### Correction check\n\n### Correction check\n\nResult: FAIL"
        self.assertEqual(run_report.subsection(body, "Correction check", after="Build review"),
                         "### Correction check\n\nResult: FAIL")
        self.assertIsNone(run_report.subsection("### Correction check\n\nx", "Correction check", after="Build review"))


if __name__ == "__main__":
    unittest.main()

"""Tests for steps.py, which lists a build's steps from its plan (docs/adrs/0063)."""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "steps.py")
sys.path.insert(0, HERE)
import steps  # noqa: E402

PLAN = """---
type: Plan
status: Ready to build 🟢
date: 2026-11-26
---

# Export the report

## Specs

- [Report export](../specs/report-export.spec.md)
  - [Column order](../specs/report-export.spec.md#1-column-order)
  - [Empty report](../specs/report-export.spec.md#2-empty-report)
- [Report import](../specs/report-import.spec.md)
  - [Bad file](../specs/report-import.spec.md#1-bad-file)

## ADRs

None.

## Plan

Build them in order.
"""

FIXED = ["Reviews of the code", "Corrections", "Check that the corrections broke nothing",
         "Give the person the work and reports"]


class StepsTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.folder, "docs", "plans"))
        self.plan = self.write(PLAN)

    def write(self, text, name="2026-11-26-export.md"):
        path = os.path.join(self.folder, "docs", "plans", name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)

    def test_requirements_in_plan_order_then_the_fixed_steps(self):
        self.assertEqual(steps.steps(self.plan),
                         ["Column order", "Empty report", "Bad file"] + FIXED)

    def test_prints_the_steps_numbered(self):
        result = self.run_script("--plan", self.plan)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "1. Column order", "2. Empty report", "3. Bad file", "4. Reviews of the code",
            "5. Corrections", "6. Check that the corrections broke nothing",
            "7. Give the person the work and reports"])

    def test_one_step_names_its_number_out_of_the_total(self):
        result = self.run_script("--plan", self.plan, "--step", "2")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "Step 2 of 7: Empty report")
        self.assertEqual(steps.line(self.plan, 7), "Step 7 of 7: Give the person the work and reports")

    def test_a_step_out_of_range_is_a_usage_error(self):
        for step in ("0", "8", "-1"):
            result = self.run_script("--plan", self.plan, "--step", step)
            self.assertEqual(result.returncode, 2, step)
            self.assertIn("1 to 7", result.stdout)

    def test_a_plan_with_no_requirements_is_refused(self):
        plan = self.write(PLAN.replace(PLAN[PLAN.index("- [Report export]"):PLAN.index("## ADRs")], "None.\n\n"),
                          "2026-11-26-empty.md")
        result = self.run_script("--plan", plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn("names no requirements", result.stdout)

    def test_an_unreadable_plan_is_refused(self):
        result = self.run_script("--plan", os.path.join(self.folder, "missing.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("can't read", result.stdout)

    def test_the_old_requirement_layout_still_lists_its_requirements(self):
        old = PLAN.replace("  - [Column order](../specs/report-export.spec.md#1-column-order)",
                           "  - Requirement: Column order")
        self.assertEqual(steps.steps(self.write(old, "2026-11-26-old.md"))[0], "Column order")

    def test_a_line_it_cannot_read_under_specs_is_refused(self):
        # Reading stops at such a line, so the requirements after it would be dropped and every
        # step number after them would be wrong.
        odd = PLAN.replace("  - [Empty report]", "  Notes: see below.\n  - [Empty report]")
        result = self.run_script("--plan", self.write(odd, "2026-11-26-odd.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Notes: see below.", result.stdout)

    def test_help_names_the_output_and_exit_codes(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        for words in ("--plan", "--step", "Exit codes"):
            self.assertIn(words, result.stdout)


if __name__ == "__main__":
    unittest.main()

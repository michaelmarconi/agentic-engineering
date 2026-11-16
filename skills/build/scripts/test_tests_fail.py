"""Tests for tests_fail.py, the check /build runs on a requirement's tests before its code."""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "tests_fail.py")
COMMAND = sys.executable + " -m unittest {file}"

PASSING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(1, 1)\n"
FAILING = "import unittest\n\nclass T(unittest.TestCase):\n    def test_no(self):\n        self.assertEqual(1, 2)\n"
MISSING = "import unittest\nfrom src.reading import reading_time\n\nclass T(unittest.TestCase):\n    def test_r(self):\n        self.assertEqual(reading_time(450), 3)\n"


class TestsFailTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "T")
        self.git("config", "user.email", "t@example.com")
        self.write("src/__init__.py", "")
        self.write("tests/__init__.py", "")
        self.write("tests/test_old.py", PASSING)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Start")

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True)

    def write(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as handle:
            handle.write(text)

    def run_script(self, *args, command=COMMAND):
        return subprocess.run([sys.executable, SCRIPT, "--command", command, *args],
                              cwd=self.repo, capture_output=True, text=True)

    def test_new_failing_tests_are_accepted(self):
        self.write("tests/test_new.py", FAILING)
        result = self.run_script("tests/test_new.py")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Accepted: every new test file fails.", result.stdout)

    def test_tests_of_code_not_written_yet_are_accepted(self):
        self.write("tests/test_reading.py", MISSING)
        self.assertEqual(self.run_script("tests/test_reading.py").returncode, 0)

    def test_changed_file_with_a_new_failing_test_is_accepted(self):
        self.write("tests/test_old.py", PASSING + "\n    def test_new(self):\n        self.assertEqual(1, 2)\n")
        self.assertEqual(self.run_script("tests/test_old.py").returncode, 0)

    def test_new_tests_that_already_pass_are_refused(self):
        self.write("tests/test_new.py", PASSING)
        result = self.run_script("tests/test_new.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("tests/test_new.py", result.stdout)
        self.assertIn("already pass", result.stdout)

    def test_one_passing_file_among_failing_ones_is_refused(self):
        self.write("tests/test_a.py", FAILING)
        self.write("tests/test_b.py", PASSING)
        result = self.run_script("tests/test_a.py", "tests/test_b.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("tests/test_b.py", result.stdout)

    def test_other_uncommitted_changes_are_refused(self):
        self.write("tests/test_new.py", FAILING)
        self.write("src/reading.py", "def reading_time(words):\n    return 3\n")
        result = self.run_script("tests/test_new.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("src/reading.py", result.stdout)

    def test_a_file_with_no_change_is_refused(self):
        result = self.run_script("tests/test_old.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a new or changed", result.stdout)

    def test_no_files_is_a_usage_error(self):
        self.assertEqual(self.run_script().returncode, 2)

    def test_command_without_placeholder_is_a_usage_error(self):
        self.write("tests/test_new.py", FAILING)
        self.assertEqual(self.run_script("tests/test_new.py", command="true").returncode, 2)

    def test_a_failing_file_shows_its_output(self):
        self.write("tests/test_new.py", FAILING)
        result = self.run_script("tests/test_new.py")
        self.assertIn("AssertionError", result.stdout)

    def test_a_command_that_cannot_run_is_a_usage_error(self):
        self.write("tests/test_new.py", FAILING)
        result = self.run_script("tests/test_new.py", command="no-such-runner-xyz {file}")
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_a_path_with_a_space_is_passed_whole(self):
        self.write("tests/test new.py", FAILING)
        command = sys.executable + " -c 'import sys; sys.exit(0 if sys.argv[1].endswith(\"test new.py\") else 3)' {file}"
        result = self.run_script("tests/test new.py", command=command)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("already pass", result.stdout)

    def test_an_absolute_path_is_accepted(self):
        self.write("tests/test_new.py", FAILING)
        path = os.path.join(os.path.realpath(self.repo), "tests", "test_new.py")
        self.assertEqual(self.run_script(path).returncode, 0)

    def test_a_path_relative_to_a_subfolder_is_accepted(self):
        self.write("tests/test_new.py", FAILING)
        result = subprocess.run([sys.executable, SCRIPT, "--command", COMMAND, "test_new.py"],
                                cwd=os.path.join(self.repo, "tests"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_output_that_is_not_utf8_does_not_crash(self):
        self.write("tests/test_new.py", FAILING)
        command = sys.executable + " -c 'import sys; sys.stdout.buffer.write(bytes([255, 254])); sys.exit(1)' {file}"
        self.assertEqual(self.run_script("tests/test_new.py", command=command).returncode, 0)

    def test_folder_outside_a_git_work_tree_is_a_usage_error(self):
        outside = tempfile.mkdtemp()
        result = subprocess.run([sys.executable, SCRIPT, "--command", COMMAND, "tests/test_x.py"],
                                cwd=outside, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()

"""Tests for one_command.py, the check /practices runs on each command before recording it."""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "one_command.py")
sys.path.insert(0, HERE)
import one_command  # noqa: E402


class ProblemTest(unittest.TestCase):
    def assertOne(self, command):
        self.assertIsNone(one_command.problem(command), command)

    def assertNotOne(self, command, word):
        reason = one_command.problem(command)
        self.assertIsNotNone(reason, command)
        self.assertIn(word, reason)

    def test_plain_commands_pass(self):
        for command in ("make test", "npm test", "cargo test", "script/setup", "./gradlew build"):
            self.assertOne(command)

    def test_placeholders_pass(self):
        self.assertOne("pytest {file}")
        self.assertOne("script/deploy {environment}")

    def test_operators_inside_quotes_pass(self):
        self.assertOne('pytest -k "parse and not slow"')
        self.assertOne("grep -E 'a|b' notes.txt")
        self.assertOne('echo "one; two && three"')

    def test_redirections_pass(self):
        self.assertOne("make test 2>&1")
        self.assertOne("make report > report.txt")

    def test_chained_commands_fail(self):
        self.assertNotOne("npm ci && npm run build", "&&")
        self.assertNotOne("make build || make clean", "||")
        self.assertNotOne("make migrate; make restart", ";")

    def test_pipes_and_background_fail(self):
        self.assertNotOne("cat log.txt | grep error", "|")
        self.assertNotOne("npm run dev &", "&")

    def test_operators_without_spaces_fail(self):
        self.assertNotOne("npm ci&&npm run build", "&&")
        self.assertNotOne("make a;make b", ";")

    def test_line_breaks_fail(self):
        self.assertNotOne("make migrate\nmake restart", "line")
        self.assertNotOne("make migrate \\\n  --all", "line")

    def test_empty_fails(self):
        self.assertNotOne("", "empty")
        self.assertNotOne("   ", "empty")

    def test_shell_given_a_command_string_fails(self):
        self.assertNotOne("sh -c 'npm ci && npm run build'", "shell")
        self.assertNotOne('bash -lc "make a"', "shell")
        self.assertNotOne("/bin/sh -c 'make a'", "shell")

    def test_shell_running_a_script_passes(self):
        self.assertOne("sh script/setup")

    def test_unclosed_quote_fails(self):
        self.assertNotOne('pytest -k "parse', "quote")


class CommandLineTest(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)

    def test_one_command_exits_zero(self):
        result = self.run_script("make test")
        self.assertEqual(result.returncode, 0)
        self.assertIn("one command", result.stdout)

    def test_several_commands_exit_one_with_reason(self):
        result = self.run_script("npm ci && npm run build")
        self.assertEqual(result.returncode, 1)
        self.assertIn("&&", result.stdout)

    def test_several_commands_checked_in_one_call(self):
        result = self.run_script("make test", "npm ci && npm run build", "pytest {file}")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stdout.splitlines()), 3)
        self.assertIn("not one command", result.stdout)
        self.assertIn("npm ci && npm run build", result.stdout)

    def test_no_argument_is_a_usage_error(self):
        self.assertEqual(self.run_script().returncode, 2)

    def test_help_describes_exit_codes(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()

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

    def test_separator_joined_to_other_punctuation_fails(self):
        self.assertNotOne("make a;(make b)", ";")
        self.assertNotOne("make a&&(make b)", "&&")
        self.assertNotOne("make a;>log", ";")
        self.assertNotOne("make a |& tee log", "|")

    def test_hash_is_not_a_comment(self):
        self.assertNotOne("curl http://x/#a;make b", ";")
        self.assertNotOne("# setup", "comment")

    def test_shell_behind_a_prefix_fails(self):
        self.assertNotOne('FOO=1 sh -c "a && b"', "shell")
        self.assertNotOne('env bash -c "a; b"', "shell")
        self.assertNotOne("sudo sh -c 'make a'", "shell")

    def test_option_after_the_script_is_the_script_s(self):
        self.assertOne("sh script/run -c cfg")

    def test_angle_bracket_placeholder_fails(self):
        self.assertNotOne("bin/wordcount <file>", "{name}")

    def test_unclosed_quote_fails(self):
        self.assertNotOne('pytest -k "parse', "quote")


class OwnArgumentsTest(unittest.TestCase):
    """ADR 0044: a recorded command calls a named entry point with nothing but {name} values."""

    def assertEntryPoint(self, command):
        self.assertEqual(one_command.own_arguments(command), [], command)

    def test_entry_points_with_only_placeholders_pass(self):
        for command in ("make test", "npm test", "npm run build", "pnpm check:new-mail", "script/setup",
                        "./gradlew build", "docker compose up", "pytest {file}",
                        "script/deploy {environment}", "make deploy ENV={environment}", "cargo build"):
            self.assertEntryPoint(command)

    def test_redirections_are_not_arguments(self):
        self.assertEntryPoint("make test 2>&1")

    def test_flags_and_settings_are_listed(self):
        self.assertEqual(one_command.own_arguments("cargo test --release"), ["--release"])
        self.assertEqual(one_command.own_arguments("pytest -k 'not slow' {file}"), ["-k", "not slow"])

    def test_the_issue_example_lists_its_choices(self):
        found = one_command.own_arguments(
            "docker exec mail-test doveadm -o mail_driver=imapc copy -u test 'Test Folder' mailbox INBOX all")
        self.assertIn("doveadm", found)
        self.assertIn("Test Folder", found)

    def test_a_second_subcommand_word_only_after_run_or_compose(self):
        self.assertEqual(one_command.own_arguments("docker exec mail-test doveadm"), ["mail-test", "doveadm"])
        self.assertEqual(one_command.own_arguments("docker exec prod-db psql"), ["prod-db", "psql"])
        self.assertEqual(one_command.own_arguments("make deploy production"), ["production"])

    def test_paths_after_the_program_are_listed(self):
        self.assertEqual(one_command.own_arguments("go test ./..."), ["./..."])
        self.assertEqual(one_command.own_arguments("FOO=1 make test"), ["FOO=1"])

    def test_text_around_a_placeholder_is_listed(self):
        self.assertEqual(one_command.own_arguments("make deploy --config=prod-{env}.yaml"),
                         ["--config=prod-{env}.yaml"])
        self.assertEqual(one_command.own_arguments("rsync --dir=${DEPLOY_DIR}"), ["--dir=${DEPLOY_DIR}"])

    def test_prefixes_are_listed_and_skipped(self):
        self.assertEqual(one_command.own_arguments("time npm run build"), ["time"])
        self.assertEqual(one_command.own_arguments("env FOO=1 make test"), ["env", "FOO=1"])
        self.assertEqual(one_command.own_arguments("sudo make deploy"), ["sudo"])

    def test_placeholder_settings_before_the_program_pass(self):
        self.assertEqual(one_command.own_arguments("FOO={env} BAR=1 make test"), ["BAR=1"])

    def test_redirection_targets_are_listed(self):
        self.assertEqual(one_command.own_arguments("make test >/var/log/ci/test.log"), ["/var/log/ci/test.log"])
        self.assertEqual(one_command.own_arguments("make report > report.txt"), ["report.txt"])

class CommandLineTest(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)

    def test_one_command_exits_zero(self):
        result = self.run_script("make test")
        self.assertEqual(result.returncode, 0)
        self.assertIn("named entry point", result.stdout)

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

    def test_commands_read_from_standard_input(self):
        result = subprocess.run([sys.executable, SCRIPT], input="make test\npnpm vitest {file}\n\n",
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(len(result.stdout.splitlines()), 2)

    def test_own_arguments_exit_three_and_are_named(self):
        result = self.run_script("cargo test --release")
        self.assertEqual(result.returncode, 3)
        self.assertIn("--release", result.stdout)
        self.assertIn("script", result.stdout)

    def test_not_one_command_outranks_own_arguments(self):
        result = self.run_script("cargo test --release", "npm ci && npm run build")
        self.assertEqual(result.returncode, 1)

    def test_no_command_at_all_is_a_usage_error(self):
        result = subprocess.run([sys.executable, SCRIPT], input="", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_help_describes_exit_codes(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()

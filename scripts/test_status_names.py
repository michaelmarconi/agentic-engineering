import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "status_names.py")


class StatusNames(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, path, text):
        full = os.path.join(self.tmp.name, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def check(self, root=None):
        return subprocess.run([sys.executable, SCRIPT, root or self.tmp.name],
                              capture_output=True, text=True)

    def assertPasses(self):
        done = self.check()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def assertFails(self, *needles):
        done = self.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        for needle in needles:
            self.assertIn(needle, done.stdout)

    def test_backticked_full_values_pass(self):
        self.write("README.md", "A spec goes from `📝 Draft` to `🟢 Ready to build` to `✅ Built`.\n"
                                "An ADR is `👍 Accepted`, `❌ Rejected` or `↪️ Superseded`.\n")
        self.assertPasses()

    def test_spike_record_values_pass(self):
        self.write("README.md", "A record goes `📝 Draft`, `🟢 Ready to run`, `💡 Answered` or `❔ Not answered`.\n")
        self.assertPasses()

    def test_spike_word_without_emoji_fails_with_the_value(self):
        self.write("docs/a.md", "Set `Not answered`.\n")
        self.assertFails("docs/a.md:1", "`❔ Not answered`")

    def test_ready_to_run_outside_backticks_fails(self):
        self.write("docs/a.md", "Mark it Ready to run.\n")
        self.assertFails("docs/a.md:1", "Ready to run")

    def test_ready_to_run_in_a_longer_code_span_fails(self):
        self.write("docs/a.md", "Set `status: Ready to run now`.\n")
        self.assertFails("`🟢 Ready to run`")

    def test_spike_emoji_status_outside_backticks_fails(self):
        self.write("docs/a.md", "It ends 💡 Answered.\n")
        self.assertFails("docs/a.md:1")

    def test_backticked_word_without_emoji_fails_with_the_value(self):
        self.write("docs/a.md", "Intro.\n\nSet it to `Accepted`.\n")
        self.assertFails("docs/a.md:3", "`👍 Accepted`")

    def test_backticked_wrong_emoji_fails(self):
        self.write("docs/a.md", "Never `🟢 Built`.\n")
        self.assertFails("docs/a.md:1", "`✅ Built`")

    def test_ready_to_build_outside_backticks_fails(self):
        self.write("docs/a.md", "Mark it Ready to build.\n")
        self.assertFails("docs/a.md:1", "Ready to build")

    def test_emoji_status_outside_backticks_fails(self):
        self.write("docs/a.md", "It stays 📝 Draft.\n")
        self.assertFails("docs/a.md:1")

    def test_status_key_in_a_code_span_is_checked(self):
        self.write("docs/a.md", "Set `status: Accepted`.\n")
        self.assertFails("`status: 👍 Accepted`")

    def test_phrase_in_a_longer_code_span_fails(self):
        self.write("docs/a.md", "Run `mark Ready to build`.\n")
        self.assertFails("docs/a.md:1")

    def test_every_problem_on_a_line_is_reported(self):
        self.write("docs/a.md", "It is 📝 Draft, then ✅ Built, then Ready to build.\n")
        self.assertEqual(self.check().stdout.count("docs/a.md:1"), 3)

    def test_variation_selector_is_optional(self):
        self.write("docs/a.md", "`\u21aa Superseded` and `🟢\ufe0f Ready to build`\n\n```\n🟢\ufe0f Ready to build\n```\n")
        self.assertPasses()
        self.write("docs/a.md", "It is \u21aa Superseded.\n")
        self.assertFails("docs/a.md:1")

    def test_code_span_may_wrap(self):
        self.write("docs/a.md", "Set it to `🟢 Ready\nto build` once agreed.\n")
        self.assertPasses()
        self.write("docs/a.md", "Intro.\n\nSet it to `Ready\nto build` once agreed.\n")
        self.assertFails("docs/a.md:3")

    def test_code_span_does_not_cross_list_items(self):
        self.write("docs/a.md", "- use a ` here\n- then `Draft` and more\n")
        self.assertFails("`📝 Draft`")

    def test_status_key_in_any_case(self):
        self.write("docs/a.md", "Set `Status : Accepted`.\n")
        self.assertFails("docs/a.md:1")

    def test_plain_words_in_prose_pass(self):
        self.write("docs/a.md", "Draft from the conversation. Built with skill-creator.\n")
        self.assertPasses()

    def test_status_line_in_frontmatter_is_bare(self):
        self.write("docs/a.md", "---\nstatus: 📝 Draft\n---\n\n# A\n")
        self.assertPasses()

    def test_fenced_status_needs_its_emoji(self):
        self.write("docs/a.md", "```\nstate \"🟢 Ready to build\" as Ready\n```\n")
        self.assertPasses()
        self.write("docs/a.md", "```\nReady: Ready to build\n```\n")
        self.assertFails("docs/a.md:2")

    def test_changelog_evals_and_adrs_are_skipped(self):
        for path in ("CHANGELOG.md", "evals/case/prompt.md", "evals-failed-check/case/prompt.md",
                     "docs/adrs/0001-x.md"):
            self.write(path, "Set it Ready to build, or `Accepted`.\n")
        self.assertPasses()

    def test_this_plugin_passes(self):
        done = self.check(os.path.join(HERE, ".."))
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


if __name__ == "__main__":
    unittest.main()

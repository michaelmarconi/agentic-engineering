import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "doc_references.py")


class DocReferences(unittest.TestCase):
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
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(done.stdout, "")

    def assertFails(self, *needles):
        done = self.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        for needle in needles:
            self.assertIn(needle, done.stdout)
        return done.stdout

    def test_reference_to_an_existing_file_passes(self):
        self.write("README.md", "See [the rules](docs/rules.md).\n")
        self.write("docs/rules.md", "# Rules\n")
        self.assertPasses()

    def test_reference_to_a_missing_file_fails_with_where_and_what(self):
        self.write("README.md", "Intro.\n\nSee [the rules](docs/rules.md).\n")
        self.assertFails("README.md:3", "docs/rules.md")

    def test_reference_is_resolved_from_the_referring_file(self):
        self.write("docs/a.md", "[b](b.md) and [readme](../README.md)\n")
        self.write("docs/b.md", "# B\n")
        self.write("README.md", "# Readme\n")
        self.assertPasses()

    def test_reference_to_a_folder_passes(self):
        self.write("README.md", "[docs](docs/)\n")
        self.write("docs/a.md", "# A\n")
        self.assertPasses()

    def test_heading_in_another_file_must_exist(self):
        self.write("docs/lifecycle.md", "# The lifecycle rules\n\n## Review process\n")
        self.write("README.md", "[ok](docs/lifecycle.md#review-process)\n")
        self.assertPasses()
        self.write("README.md", "[gone](docs/lifecycle.md#no-such-heading)\n")
        self.assertFails("README.md:1", "#no-such-heading")

    def test_heading_in_the_same_file_must_exist(self):
        self.write("README.md", "# Readme\n\n## How it works\n\n[up](#how-it-works) [x](#nowhere)\n")
        out = self.assertFails("#nowhere")
        self.assertNotIn("#how-it-works", out)

    def test_headings_are_named_as_github_names_them(self):
        self.write("a.md", "## Step 1: Draft, then Review!\n\n## `/spec` and /brief\n\n"
                           "## Notes\n\n## Notes\n\n"
                           "[a](#step-1-draft-then-review) [b](#spec-and-brief) "
                           "[c](#notes) [d](#notes-1)\n")
        self.assertPasses()

    def test_web_and_mail_references_are_not_checked(self):
        self.write("README.md", "[w](https://example.com/x.md) [m](mailto:a@b.c) "
                                "[h](http://example.com)\n")
        self.assertPasses()

    def test_references_in_code_are_not_checked(self):
        self.write("README.md", "Write `[x](missing.md)` like this.\n\n```\n[y](missing.md)\n```\n\n"
                                "~~~markdown\n[z](missing.md)\n~~~\n")
        self.assertPasses()

    def test_placeholders_are_not_checked(self):
        self.write("template.md", "[spec](<path>) [adr](docs/adrs/NNNN-${title}.md)\n")
        self.assertPasses()

    def test_images_and_reference_definitions_are_checked(self):
        self.write("README.md", "![logo](logo.png)\n\n[rules]: docs/rules.md\n")
        self.assertFails("logo.png", "docs/rules.md")

    def test_footnotes_are_not_reference_definitions(self):
        self.write("README.md", "Said so.[^a]\n\n[^a]: Ann Lee, [Talk](https://example.com), 2011.\n")
        self.assertPasses()

    def test_link_titles_are_ignored(self):
        self.write("README.md", '[r](rules.md "The rules")\n')
        self.write("rules.md", "# Rules\n")
        self.assertPasses()

    def test_hidden_folders_are_skipped_except_github(self):
        self.write(".git/x.md", "[a](missing.md)\n")
        self.write(".github/ISSUE_TEMPLATE/bug.md", "[a](missing.md)\n")
        self.assertFails(".github/ISSUE_TEMPLATE/bug.md:1")

    def test_this_repository_has_no_broken_references(self):
        done = self.check(os.path.join(HERE, ".."))
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_help_describes_the_output(self):
        done = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("exits 1", done.stdout)


if __name__ == "__main__":
    unittest.main()

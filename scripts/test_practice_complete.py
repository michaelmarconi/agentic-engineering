import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "practice_complete.py")

RELEASING = """# Releasing

## What may be released
Only commits merged to main.

## Version and its commit
Semver in package.json; each release is tagged v<version>.

## Publish
`npm run release`
"""

ENVIRONMENT = """## Environment: {name}

### Releases allowed
Releases from main.

### Deploy
`make deploy ENV={name}`

### Check
`make check ENV={name}` exits 0 within 2 minutes.

### Roll back
`make rollback ENV={name}`
"""

DEPLOYING = "# Deploying\n\n## How deploys start\nBy hand.\n\n" + ENVIRONMENT.format(name="staging")


class PracticeComplete(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def put(self, name, text):
        path = os.path.join(self.tmp.name, "docs", "practices", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)

    def assertComplete(self, path):
        done = self.run_script(path)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("complete", done.stdout)

    def assertMissing(self, path, *expected):
        done = self.run_script(path)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        for line in expected:
            self.assertIn(line, done.stdout)
        return done.stdout

    # releasing.md

    def test_complete_releasing_passes(self):
        self.assertComplete(self.put("releasing.md", RELEASING))

    def test_optional_headings_are_allowed(self):
        text = RELEASING + "\n## Release notes\nCHANGELOG.md, Keep a Changelog form (default).\n"
        self.assertComplete(self.put("releasing.md", text))

    def test_missing_heading_is_named(self):
        text = RELEASING.replace("## Publish\n`npm run release`\n", "")
        self.assertMissing(self.put("releasing.md", text), "Publish")

    def test_every_missing_heading_is_named(self):
        out = self.assertMissing(self.put("releasing.md", "# Releasing\n"),
                                 "What may be released", "Version and its commit", "Publish")
        self.assertEqual(out.count("\n"), 3, out)

    def test_empty_heading_counts_as_missing(self):
        text = RELEASING.replace("`npm run release`\n", "\n")
        self.assertMissing(self.put("releasing.md", text), "Publish has nothing under it")

    def test_headings_match_whatever_the_case(self):
        self.assertComplete(self.put("releasing.md", RELEASING.replace("## Publish", "## publish")))

    def test_heading_at_another_level_does_not_count(self):
        text = RELEASING.replace("## Publish", "### Publish")
        self.assertMissing(self.put("releasing.md", text), "Publish")

    def test_heading_inside_a_code_block_does_not_count(self):
        text = RELEASING.replace("## Publish\n`npm run release`\n", "```\n## Publish\nnpm run release\n```\n")
        self.assertMissing(self.put("releasing.md", text), "Publish")

    def test_a_none_answer_counts(self):
        text = RELEASING.replace("`npm run release`", "None: the merged commit is the release.")
        self.assertComplete(self.put("releasing.md", text))

    def test_required_item_may_not_be_a_default(self):
        text = RELEASING.replace("`npm run release`", "`npm run release` (default)")
        self.assertMissing(self.put("releasing.md", text), "Publish is a default")


    def test_only_a_heading_below_counts_as_nothing(self):
        text = RELEASING.replace("`npm run release`\n", "### Notes\n")
        self.assertMissing(self.put("releasing.md", text), "Publish has nothing under it")

    def test_an_empty_code_block_counts_as_nothing(self):
        text = RELEASING.replace("`npm run release`\n", "```\n```\n")
        self.assertMissing(self.put("releasing.md", text), "Publish has nothing under it")

    def test_a_command_in_a_code_block_counts(self):
        text = RELEASING.replace("`npm run release`\n", "```\nnpm run release\n```\n")
        self.assertComplete(self.put("releasing.md", text))

    def test_a_comment_counts_as_nothing(self):
        text = RELEASING.replace("`npm run release`\n", "<!-- fill in -->\n")
        self.assertMissing(self.put("releasing.md", text), "Publish has nothing under it")

    def test_a_heading_inside_a_comment_does_not_count(self):
        text = RELEASING.replace("## Publish\n`npm run release`\n", "<!--\n## Publish\nnpm run release\n-->\n")
        self.assertMissing(self.put("releasing.md", text), "releasing.md has no Publish")

    def test_every_copy_of_a_heading_is_checked(self):
        text = RELEASING + "\n## Publish\nnpm publish (default)\n"
        self.assertMissing(self.put("releasing.md", text), "Publish is a default")

    def test_a_fence_closes_only_on_its_own_kind(self):
        text = DEPLOYING.replace("`make deploy ENV=staging`\n", "~~~\n```\n~~~\nmake deploy ENV=staging\n")
        self.assertComplete(self.put("deploying.md", text))

    def test_a_byte_order_mark_is_ignored(self):
        self.assertComplete(self.put("releasing.md", "\ufeff" + RELEASING.replace("# Releasing\n\n", "")))

    # deploying.md

    def test_complete_deploying_passes(self):
        self.assertComplete(self.put("deploying.md", DEPLOYING))

    def test_several_environments_pass(self):
        text = DEPLOYING + "\n" + ENVIRONMENT.format(name="production")
        self.assertComplete(self.put("deploying.md", text))

    def test_deploying_without_an_environment_fails(self):
        self.assertMissing(self.put("deploying.md", "# Deploying\n\n## How deploys start\nBy hand.\n"),
                           "no environment")

    def test_missing_part_names_its_environment(self):
        production = ENVIRONMENT.format(name="production").replace(
            "### Roll back\n`make rollback ENV=production`\n", "")
        out = self.assertMissing(self.put("deploying.md", DEPLOYING + "\n" + production),
                                 "Environment: production has no Roll back")
        self.assertNotIn("staging", out)

    def test_part_under_the_next_environment_does_not_count_for_the_one_before(self):
        staging = ENVIRONMENT.format(name="staging").replace("### Check\n`make check ENV=staging` exits 0 within 2 minutes.\n", "")
        text = "# Deploying\n\n" + staging + "\n" + ENVIRONMENT.format(name="production")
        self.assertMissing(self.put("deploying.md", text), "Environment: staging has no Check")

    def test_empty_part_counts_as_missing(self):
        text = DEPLOYING.replace("`make rollback ENV=staging`\n", "")
        self.assertMissing(self.put("deploying.md", text), "Environment: staging: Roll back has nothing under it")

    def test_environment_needs_a_name(self):
        text = DEPLOYING.replace("## Environment: staging", "## Environment:")
        self.assertMissing(self.put("deploying.md", text), "has no name")

    def test_deploy_part_may_not_be_a_default(self):
        text = DEPLOYING.replace("`make deploy ENV=staging`", "`make deploy ENV=staging` (default)")
        self.assertMissing(self.put("deploying.md", text), "Environment: staging: Deploy is a default")

    # files and arguments

    def test_missing_file_lists_everything(self):
        path = os.path.join(self.tmp.name, "docs", "practices", "releasing.md")
        self.assertMissing(path, "not recorded yet")

    def test_other_file_is_refused(self):
        done = self.run_script(self.put("testing.md", "# Testing\n"))
        self.assertEqual(done.returncode, 2)
        self.assertIn("releasing.md or deploying.md", done.stderr)

    def test_help_explains_exit_codes(self):
        done = self.run_script("--help")
        self.assertEqual(done.returncode, 0)
        for word in ("releasing.md", "deploying.md", "0", "1", "2"):
            self.assertIn(word, done.stdout)


if __name__ == "__main__":
    unittest.main()

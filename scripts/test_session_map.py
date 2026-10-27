import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "session_map.py")
MAP = os.path.join(HERE, "..", "context", "sdlc.md")
SAVED = {"CLAUDE_PLUGIN_OPTION_REVIEW_ROUNDS": "3"}


class SessionMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_map(self, *args, settings=SAVED):
        env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_OPTION_")}
        env.update(settings, CLAUDE_PROJECT_DIR=self.tmp.name)
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, env=env)

    def output(self, **kwargs):
        done = self.run_map(**kwargs)
        self.assertEqual(done.returncode, 0)
        return json.loads(done.stdout)

    def test_silent_in_repo_without_lifecycle_documents(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        done = self.run_map()
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def put(self, relative, text=""):
        path = os.path.join(self.tmp.name, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def test_silent_with_folders_other_projects_also_use(self):
        for folder in ["docs/specs", "docs/plans", "docs/decisions"]:
            os.makedirs(os.path.join(self.tmp.name, folder))
        self.put("docs/specs/login.spec.md", "# Login\n")
        self.assertEqual(self.run_map().stdout, "")

    def test_prints_map_when_a_spec_has_a_lifecycle_status(self):
        with open(MAP) as f:
            expected = f.read()
        self.put("docs/specs/billing/invoice.spec.md", "---\nstatus: Draft\n---\n# Invoice\n")
        out = self.output()
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertEqual(out["hookSpecificOutput"]["additionalContext"], expected)
        self.assertNotIn("systemMessage", out)

    def test_prints_map_when_brief_exists(self):
        os.makedirs(os.path.join(self.tmp.name, "docs"))
        open(os.path.join(self.tmp.name, "docs", "brief.md"), "w").close()
        self.assertIn("/sdlc:", self.output()["hookSpecificOutput"]["additionalContext"])

    def test_unsaved_setting_is_reported_even_without_lifecycle_documents(self):
        out = self.output(settings={})
        self.assertIn("'Review rounds' config setting is not set", out["systemMessage"])
        self.assertIn("set it (3 is suggested)", out["systemMessage"])
        self.assertIn("/reload-plugins", out["systemMessage"])
        self.assertIn("/plugin configure sdlc@sdlc", out["systemMessage"])
        context = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn(out["systemMessage"], context)
        self.assertNotIn("/sdlc:spec", context)

    def test_unsaved_setting_is_reported_with_the_map(self):
        self.put("docs/brief.md")
        context = self.output(settings={})["hookSpecificOutput"]["additionalContext"]
        with open(MAP) as f:
            self.assertTrue(context.startswith(f.read()))
        self.assertIn("Review rounds", context)

    def test_empty_value_counts_as_unsaved(self):
        out = self.output(settings={"CLAUDE_PLUGIN_OPTION_REVIEW_ROUNDS": ""})
        self.assertIn("Review rounds", out["systemMessage"])

    def test_malformed_manifest_reports_nothing(self):
        sys.path.insert(0, HERE)
        import session_map
        manifest = os.path.join(self.tmp.name, "plugin.json")
        self.addCleanup(setattr, session_map, "MANIFEST", session_map.MANIFEST)
        session_map.MANIFEST = manifest
        for text in ["[]", '"x"', "{}", '{"userConfig": null}', '{"userConfig": []}',
                     '{"userConfig": {"review_rounds": 3}}', "not json"]:
            with open(manifest, "w") as f:
                f.write(text)
            self.assertEqual(session_map.unsaved_settings({}), [], text)
        os.remove(manifest)
        self.assertEqual(session_map.unsaved_settings({}), [])

    def test_help(self):
        done = self.run_map("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("exit", done.stdout.lower())


if __name__ == "__main__":
    unittest.main()

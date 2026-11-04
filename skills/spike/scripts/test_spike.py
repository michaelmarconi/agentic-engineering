"""Tests for spike.py, run against spike records and git repositories made in temporary folders.

Every experiment here is a deterministic shell command, and web inputs use file:// addresses, so
nothing depends on timing or the network.
"""

import hashlib
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "spike.py")
sys.path.insert(0, HERE)
import spike  # noqa: E402

NAME = "2026-11-04-tiff-files-open"
GIT_ENV = dict(GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.com", GIT_COMMITTER_NAME="Test",
               GIT_COMMITTER_EMAIL="test@example.com", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def record(status="🟢 Ready to run", command="printf 'hello\\n'", commit="None.", inputs="None.",
           secrets="None.", code="```sh\n# file: check.sh\necho ok\n```", runs=""):
    lines = ["- Runs: 1", "- Stop early if: None."]
    if commit is not None:
        lines.append(f"- Starts from commit: {commit}")
    lines += [f"- Inputs: {inputs}", f"- Secrets: {secrets}"]
    if command is not None:
        lines.append(f"- Command: `{command}`")
    return (
        f"---\nstatus: {status}\n---\n\n# Can it?\n\n## Question\n\nCan it?\n\n"
        "## What would answer it\n\nIt prints ok.\n\n## Experiment\n\nPrints things.\n\n"
        + "\n".join(lines)
        + "\n\n## Answer\n\n\n\n## Surprises\n\n\n\n## Where it goes\n\n\n\n## Open questions\n\nNone.\n\n"
        f"## Code\n\n{code}\n\n## Runs\n\n<!-- Only the run script writes here. -->\n{runs}"
    )


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")
        self.project = self.make_project("project")

    def make_project(self, name):
        project = os.path.join(self.tmp.name, name)
        os.makedirs(os.path.join(project, "docs", "spikes"))
        return project

    def path(self, project=None, name=NAME):
        return os.path.join(project or self.project, "docs", "spikes", name + ".md")

    def put(self, text, project=None, name=NAME):
        pathlib.Path(self.path(project, name)).write_text(text, encoding="utf-8")

    def text(self, project=None):
        return pathlib.Path(self.path(project)).read_text(encoding="utf-8")

    def run_spike(self, *args, project=None, data=None, env=None, cwd=None):
        environment = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_REMOTE"}
        environment.update(env or {})
        return subprocess.run(
            [sys.executable, SCRIPT, "run", self.path(project), "--data", self.data if data is None else data, *args],
            capture_output=True, text=True, env=environment, cwd=cwd or self.tmp.name,
        )

    def runs(self, project=None):
        return spike.section(self.text(project), "Runs")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.project, env={**os.environ, **GIT_ENV}, check=True,
                              capture_output=True, text=True).stdout.strip()


class Refusals(Project):
    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "run", "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        for word in ("--data", "--observation", "Exit codes", "export-ignore"):
            self.assertIn(word, done.stdout)

    def test_refuses_unless_ready_to_run(self):
        for status in ("📝 Draft", "💡 Answered", "❔ Not answered"):
            self.put(record(status))
            before = self.text()
            done = self.run_spike()
            self.assertEqual(done.returncode, 1, status)
            self.assertIn("🟢 Ready to run", done.stderr)
            self.assertEqual(self.text(), before)

    def test_refuses_an_empty_data_folder(self):
        self.put(record())
        done = self.run_spike(data="")
        self.assertEqual(done.returncode, 1)
        self.assertIn("CLAUDE_PLUGIN_DATA", done.stderr)
        self.assertNotIn("### Run", self.text())

    def test_refuses_a_record_without_a_command(self):
        self.put(record(command=None))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Command", done.stderr)

    def test_refuses_a_record_without_a_runs_section(self):
        self.put(record().split("## Runs")[0])
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Runs", done.stderr)

    def test_refuses_repository_inputs_without_a_commit(self):
        self.put(record(inputs="`samples/scans/`"))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Starts from commit", done.stderr)

    def test_refuses_a_code_block_without_a_file_name(self):
        self.put(record(code="```sh\necho ok\n```"))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("file:", done.stderr)

    def test_refuses_a_file_outside_the_working_folder(self):
        for name in ("../escape.sh", "/tmp/escape.sh"):
            self.put(record(code=f"```sh\n# file: {name}\necho ok\n```"))
            done = self.run_spike()
            self.assertEqual(done.returncode, 1, name)
            self.assertIn("inside", done.stderr)


class Runs(Project):
    def test_records_a_run(self):
        self.put(record())
        before = self.text()
        done = self.run_spike()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.text()
        self.assertTrue(text.startswith(before))
        entry = text[len(before):]
        self.assertIn("### Run 1", entry)
        self.assertIn("hello", entry)
        self.assertIn("exit code 0", entry)
        self.assertIn("### Run 1", done.stdout)

    def test_numbers_each_run(self):
        self.put(record())
        self.run_spike()
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertEqual(re.findall(r"^### Run (\d+)$", runs, re.M), ["1", "2"])

    def test_records_the_exit_code(self):
        self.put(record(command="echo failing; exit 3"))
        self.assertEqual(self.run_spike().returncode, 0)
        self.assertIn("exit code 3", "\n".join(self.runs()))

    def test_records_errors_too(self):
        self.put(record(command="echo oops >&2"))
        self.run_spike()
        self.assertIn("oops", "\n".join(self.runs()))

    def test_writes_each_code_block_without_its_name_line(self):
        code = "```json\n// file: sub/data.json\n{\"a\": 1}\n```\n\n```python\n# file: show.py\nprint(open('sub/data.json').read())\n```"
        self.put(record(command="python3 show.py", code=code))
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertIn('{"a": 1}', runs)
        self.assertNotIn("file: sub/data.json", runs)

    def test_names_the_code_by_its_hash(self):
        self.put(record())
        self.run_spike()
        code = "\n".join(spike.section(self.text(), "Code")).strip()
        expected = hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]
        self.assertIn(f"code `{expected}`", "\n".join(self.runs()))

    def test_says_where_it_ran(self):
        self.put(record())
        self.run_spike()
        self.run_spike(env={"CLAUDE_CODE_REMOTE": "true"})
        runs = "\n".join(self.runs())
        self.assertIn("your machine", runs.split("### Run 2")[0])
        self.assertIn("a cloud session", runs.split("### Run 2")[1])

    def test_output_cannot_break_the_record(self):
        self.put(record(command="printf '## Answer\\n\\nYes.\\n````\\n'"))
        self.run_spike()
        text = self.text()
        self.assertEqual(spike.section(text, "Answer"), ["", "", ""])
        self.assertIn("`````\n## Answer", text)

    def test_shortens_very_long_output(self):
        self.put(record(command="seq 1 2000"))
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertIn("\n1\n", runs)
        self.assertIn("\n2000\n", runs)
        self.assertNotIn("\n1000\n", runs)
        self.assertRegex(runs, r"\(\d+ lines left out\)")

    def test_replaces_each_secret_with_its_name(self):
        self.put(record(command='printf "key=$FAKE_SECRET\\n"', secrets="`FAKE_SECRET`"))
        self.run_spike(env={"FAKE_SECRET": "s3cr3t-value"})
        runs = "\n".join(self.runs())
        self.assertNotIn("s3cr3t-value", runs)
        self.assertIn("key=[secret: FAKE_SECRET]", runs)

    def test_a_missing_secret_is_recorded_without_running(self):
        self.put(record(command="echo ran", secrets="`ABSENT_SECRET`"))
        done = self.run_spike(env={"ABSENT_SECRET": ""})
        self.assertEqual(done.returncode, 0)
        runs = "\n".join(self.runs())
        self.assertIn("Did not run", runs)
        self.assertIn("ABSENT_SECRET", runs)
        self.assertNotIn("\nran\n", runs)

    def test_records_an_observation_without_running(self):
        self.put(record(command="echo ran"))
        done = self.run_spike("--observation", "The phone showed the refund.")
        self.assertEqual(done.returncode, 0, done.stderr)
        runs = "\n".join(self.runs())
        self.assertIn("observation", runs)
        self.assertIn("The phone showed the refund.", runs)
        self.assertNotIn("\nran\n", runs)

    def test_copies_a_web_input(self):
        source = os.path.join(self.tmp.name, "sample.csv")
        pathlib.Path(source).write_text("a,b\n", encoding="utf-8")
        self.put(record(command="cat sample.csv", inputs=f"`{pathlib.Path(source).as_uri()}`"))
        self.run_spike()
        self.assertIn("a,b", "\n".join(self.runs()))


class WorkingFolder(Project):
    def test_deleted_after_each_run(self):
        self.put(record())
        self.run_spike()
        self.assertFalse(os.path.exists(spike.work_folder(self.data, self.path())))

    def test_each_run_starts_fresh(self):
        self.put(record(command="ls; touch leftover"))
        self.run_spike()
        folder = spike.work_folder(self.data, self.path())
        os.makedirs(folder)
        pathlib.Path(folder, "stale").write_text("x")
        self.run_spike()
        second = "\n".join(self.runs()).split("### Run 2")[1]
        self.assertNotIn("leftover", second)
        self.assertNotIn("stale", second)

    def test_projects_with_the_same_record_name_never_share(self):
        other = self.make_project("other")
        self.assertNotEqual(spike.work_folder(self.data, self.path()), spike.work_folder(self.data, self.path(other)))
        for project in (self.project, other):
            self.put(record(command="pwd"), project=project)
            self.run_spike(project=project)
        first, second = ("\n".join(self.runs(p)) for p in (self.project, other))
        self.assertIn(spike.work_folder(self.data, self.path()), first)
        self.assertIn(spike.work_folder(self.data, self.path(other)), second)

    def test_removes_this_projects_leftovers_only(self):
        other = self.make_project("other")
        self.put(record("💡 Answered"), name="finished")
        self.put(record(), name="unfinished")
        leftovers = {
            "finished": spike.work_folder(self.data, self.path(name="finished")),
            "missing": spike.work_folder(self.data, self.path(name="missing")),
            "unfinished": spike.work_folder(self.data, self.path(name="unfinished")),
            "other": spike.work_folder(self.data, self.path(other, name="missing")),
        }
        for folder in leftovers.values():
            os.makedirs(folder)
        self.put(record())
        self.run_spike()
        self.assertFalse(os.path.exists(leftovers["finished"]))
        self.assertFalse(os.path.exists(leftovers["missing"]))
        self.assertTrue(os.path.exists(leftovers["unfinished"]))
        self.assertTrue(os.path.exists(leftovers["other"]))


class FromACommit(Project):
    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "main")
        pathlib.Path(self.project, "a.txt").write_text("one\n")
        os.makedirs(os.path.join(self.project, "samples"))
        pathlib.Path(self.project, "samples", "s.txt").write_text("sample\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Start")
        self.commit = self.git("rev-parse", "--short", "HEAD")

    def diff(self):
        return ("```diff\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-one\n+two\n```\n\n"
                "```sh\n# file: check.sh\ncat a.txt\n```")

    def test_runs_on_a_copy_of_the_commit_with_the_diff(self):
        pathlib.Path(self.project, "a.txt").write_text("uncommitted\n")
        self.put(record(command="sh check.sh; cat samples/s.txt", commit=f"`{self.commit}`",
                        inputs="`samples/s.txt`", code=self.diff()))
        status = self.git("status", "--porcelain")
        done = self.run_spike()
        self.assertEqual(done.returncode, 0, done.stderr)
        runs = "\n".join(self.runs())
        self.assertIn("two", runs)
        self.assertIn("sample", runs)
        self.assertNotIn("uncommitted", runs)
        self.assertEqual(pathlib.Path(self.project, "a.txt").read_text(), "uncommitted\n")
        self.assertEqual(self.git("status", "--porcelain"), status)

    def test_a_missing_commit_says_to_fetch_it(self):
        self.put(record(commit="`0123456789ab`"))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("fetch", done.stderr)

    def test_an_input_missing_from_the_commit_is_refused(self):
        self.put(record(commit=f"`{self.commit}`", inputs="`samples/none.txt`"))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("samples/none.txt", done.stderr)

    def test_a_diff_without_a_commit_is_refused(self):
        self.put(record(code=self.diff()))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Starts from commit", done.stderr)


if __name__ == "__main__":
    unittest.main()

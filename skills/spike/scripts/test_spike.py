"""Tests for spike.py, run against spike records and git repositories made in temporary folders.

Every experiment here is a deterministic shell command, and web inputs use file:// addresses, so
nothing depends on timing or the network. The time limit on a run is left untested: the only way
to test it is by timing, which AGENTS.md rule 5 forbids.
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
        f"---\nstatus: {status}\n---\n\n# It prints ok\n\n## Hypothesis\n\nIt prints ok.\n\n"
        "## Finding\n\n\n\n## Next steps\n\n\n\n## How we'll know\n\nIt prints ok.\n\n## Out of scope\n\nNone.\n\n"
        "## How the test works\n\nPrints things.\n\n## Risks and safeguards\n\nNone.\n\n## Results\n\n\n\n"
        "## Surprises\n\n\n\n## Open questions\n\nNone.\n\n## Experiment\n\nPrints things.\n\n"
        + "\n".join(lines)
        + "\n\n"
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


class Words(Project):
    def words(self, *args):
        return subprocess.run([sys.executable, SCRIPT, "words", *args], capture_output=True, text=True)

    def test_short_record_passes_and_reports_both_parts(self):
        self.put(record())
        done = self.words(self.path())
        self.assertEqual(done.returncode, 0, done.stderr)
        design, verdict = spike.spike_words(self.text())
        self.assertIn(f"design holds {design} of the 600 words", done.stdout)
        self.assertIn(f"verdict holds {verdict} of the 400 words", done.stdout)

    def test_long_design_fails(self):
        self.put(record("📝 Draft").replace("Prints things.", " ".join(["word"] * 650), 1))
        done = self.words(self.path())
        self.assertEqual(done.returncode, 1)
        self.assertIn("design", done.stdout)
        self.assertIn("into Experiment", done.stdout)

    def test_long_verdict_fails_and_is_told_to_shorten_the_verdict(self):
        long = "## Finding\n\nConfirmed: " + " ".join(["word"] * 420)
        self.put(record().replace("## Finding\n", long, 1))
        done = self.words(self.path())
        self.assertEqual(done.returncode, 1)
        self.assertIn("Finding, Next steps, Results or Surprises", done.stdout)
        self.assertNotIn("into Experiment", done.stdout)

    def test_a_design_near_its_limit_leaves_the_verdict_its_room(self):
        text = record().replace("Prints things.", " ".join(["word"] * 560), 1)
        text = text.replace("## Finding\n", "## Finding\n\nConfirmed: " + " ".join(["word"] * 360), 1)
        self.put(text)
        done = self.words(self.path())
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_unreadable_record(self):
        done = self.words(os.path.join(self.tmp.name, "missing.md"))
        self.assertEqual(done.returncode, 1)
        self.assertIn("can't read", done.stderr)

    def test_help(self):
        done = self.words("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("Exit codes", done.stdout)


class Refusals(Project):
    def test_help(self):
        done = subprocess.run([sys.executable, SCRIPT, "run", "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        for word in ("--data", "--observation", "Exit codes", "export-ignore"):
            self.assertIn(word, done.stdout)

    def test_refuses_unless_ready_to_run(self):
        for status in ("📝 Draft", "💡 Confirmed", "🚫 Refuted", "❔ Not settled"):
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

    def test_a_record_with_no_command_takes_only_observations(self):
        self.put(record(command=None).replace("- Secrets: None.", "- Secrets: None.\n- Command: None."))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("--observation", done.stderr)
        self.assertEqual(self.run_spike("--observation", "It showed.").returncode, 0)

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
        self.put(record(command="printf '## Finding\\n\\nConfirmed.\\n````\\n'"))
        self.run_spike()
        text = self.text()
        self.assertEqual(spike.section(text, "Finding"), ["", "", ""])
        self.assertIn("`````\n## Finding", text)

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


class Corrections(Project):
    """Behaviours added after the code review of the first version."""

    def test_runs_go_at_the_end_of_the_runs_section(self):
        self.put(record() + "\n## Notes\n\nKept last.\n")
        self.run_spike()
        done = self.run_spike()
        self.assertEqual(done.returncode, 0, done.stderr)
        text = self.text()
        self.assertTrue(text.rstrip().endswith("Kept last."))
        self.assertIn("### Run 2", "\n".join(self.runs()))

    def test_run_headings_in_output_do_not_count(self):
        self.put(record(command="printf '### Run 1\\n'"))
        self.run_spike()
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertRegex(runs, r"(?m)^### Run 2$")
        self.assertNotRegex(runs, r"(?m)^### Run 3$")

    def test_keeps_an_edit_made_while_it_ran(self):
        self.put(record(command="python3 edit.py"))
        script = (f"import pathlib\np = pathlib.Path({self.path()!r})\n"
                  "p.write_text(p.read_text().replace('## Open questions\\n\\nNone.', '## Open questions\\n\\n- Edited.'))\n")
        self.put(record(command="python3 edit.py", code=f"```python\n# file: edit.py\n{script}```"))
        self.assertEqual(self.run_spike().returncode, 0)
        self.assertIn("- Edited.", self.text())
        self.assertIn("### Run 1", self.text())

    def test_variables_that_look_secret_do_not_reach_the_experiment(self):
        self.put(record(command="env"))
        self.run_spike(env={"GITHUB_TOKEN": "tok-123456", "MY_API_KEY": "key-654321", "PLAIN": "visible-1"})
        runs = "\n".join(self.runs())
        self.assertNotIn("tok-123456", runs)
        self.assertNotIn("key-654321", runs)
        self.assertIn("visible-1", runs)

    def test_a_named_secret_still_reaches_the_experiment(self):
        self.put(record(command='test -n "$MY_API_KEY" && echo has-key', secrets="`MY_API_KEY`"))
        self.run_spike(env={"MY_API_KEY": "key-654321"})
        self.assertIn("has-key", "\n".join(self.runs()))

    def test_a_secret_holding_another_is_hidden_whole(self):
        self.put(record(command='echo "$API_KEY"', secrets="`API_USER`, `API_KEY`"))
        self.run_spike(env={"API_USER": "acme", "API_KEY": "acme-9f3k"})
        runs = "\n".join(self.runs())
        self.assertIn("[secret: API_KEY]", runs)
        self.assertNotIn("9f3k", runs)


class Redaction(Project):
    def test_known_credential_shapes_are_redacted(self):
        samples = {
            "github": "ghp_" + "a" * 36, "aws": "AKIA" + "B" * 16, "key": "sk-ant-" + "c" * 30,
            "slack": "xoxb-1234-5678-" + "d" * 20, "jwt": "eyJhbGciOi.eyJzdWIiOi" + "e" * 10 + ".sig" + "f" * 20,
        }
        printed = "\\n".join(samples.values())
        self.put(record(command=f"printf '{printed}\\nBearer abcdefghijklmnop1234\\n'"))
        self.run_spike()
        runs = "\n".join(self.runs())
        for kind, value in samples.items():
            self.assertNotIn(value, runs, kind)
        self.assertNotIn("abcdefghijklmnop1234", runs)
        self.assertIn("[redacted:", runs)
        self.assertRegex(runs, r"\d+ values? hidden")

    def test_a_private_key_block_is_redacted(self):
        block = "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBg\\n-----END PRIVATE KEY-----"
        self.put(record(command=f"printf '{block}\\n'"))
        self.run_spike()
        self.assertNotIn("MIIEvQIBADANBg", "\n".join(self.runs()))

    def test_a_credential_variable_found_another_way_is_hidden(self):
        self.put(record(command="cat token.txt", code="```text\n# file: token.txt\nplain-value-998877\n```"))
        self.run_spike(env={"DEPLOY_TOKEN": "plain-value-998877"})
        runs = "\n".join(self.runs())
        self.assertNotIn("plain-value-998877", runs)
        self.assertIn("[secret: DEPLOY_TOKEN]", runs)

    def test_ordinary_output_is_untouched(self):
        self.put(record(command="printf 'skip-this 12 rows\\n'"))
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertIn("skip-this 12 rows", runs)
        self.assertNotIn("hidden", runs)


class WorkingFolder(Project):
    def test_falls_back_to_the_temporary_folder_when_data_cannot_be_written(self):
        blocked = os.path.join(self.tmp.name, "blocked")
        pathlib.Path(blocked).write_text("a file, so no folder can be made inside it")
        self.put(record(command="pwd"))
        done = self.run_spike(data=blocked, env={"TMPDIR": self.tmp.name})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(os.path.join(self.tmp.name, "agentic-spikes"), "\n".join(self.runs()))

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
        self.put(record("💡 Confirmed"), name="finished")
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

    def test_a_link_out_of_the_copy_is_refused_without_a_traceback(self):
        os.symlink("/tmp", os.path.join(self.project, "link"))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Link")
        commit = self.git("rev-parse", "--short", "HEAD")
        self.put(record(commit=f"`{commit}`", code="```sh\n# file: link/escape.sh\necho ok\n```"))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertNotIn("Traceback", done.stderr)
        self.assertFalse(os.path.exists("/tmp/escape.sh"))

    def test_a_diff_without_a_commit_is_refused(self):
        self.put(record(code=self.diff()))
        done = self.run_spike()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Starts from commit", done.stderr)


class SecondReview(Project):
    """Corrections from the second code review."""

    def fallback(self):
        return os.path.join(self.tmp.name, f"agentic-spikes-{os.getuid()}")

    def test_falls_back_to_a_private_folder_of_this_user(self):
        blocked = os.path.join(self.tmp.name, "blocked")
        pathlib.Path(blocked).write_text("a file, so no folder can be made inside it")
        self.put(record(command="pwd"))
        done = self.run_spike(data=blocked, env={"TMPDIR": self.tmp.name})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(self.fallback(), "\n".join(self.runs()))
        self.assertEqual(os.stat(self.fallback()).st_mode & 0o777, 0o700)

    @unittest.skipIf(os.geteuid() == 0, "root can write to any folder")
    def test_falls_back_when_the_spikes_folder_exists_but_cannot_be_written(self):
        os.makedirs(os.path.join(self.data, "spikes"))
        os.chmod(os.path.join(self.data, "spikes"), 0o500)
        self.addCleanup(os.chmod, os.path.join(self.data, "spikes"), 0o700)
        self.put(record(command="pwd"))
        done = self.run_spike(env={"TMPDIR": self.tmp.name})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(self.fallback(), "\n".join(self.runs()))

    def test_refuses_a_fallback_folder_that_is_a_link(self):
        blocked = os.path.join(self.tmp.name, "blocked")
        pathlib.Path(blocked).write_text("a file")
        elsewhere = os.path.join(self.tmp.name, "elsewhere")
        os.makedirs(elsewhere)
        os.symlink(elsewhere, self.fallback())
        self.put(record(command="pwd"))
        done = self.run_spike(data=blocked, env={"TMPDIR": self.tmp.name})
        self.assertEqual(done.returncode, 1)
        self.assertNotIn("Traceback", done.stderr)
        self.assertIn(self.fallback(), done.stderr)
        self.assertEqual(self.runs(), ["", "<!-- Only the run script writes here. -->"])

    def test_ordinary_variables_are_neither_hidden_nor_kept_back(self):
        names = {"GIT_AUTHOR_NAME": "Michael Marconi", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/bus-1234",
                 "SSH_AUTH_SOCK": "/private/tmp/agent.sock-1234"}
        self.put(record(command='printf "%s|%s|%s\\n" "$GIT_AUTHOR_NAME" "$DBUS_SESSION_BUS_ADDRESS" "$SSH_AUTH_SOCK"'))
        self.run_spike(env=names)
        runs = "\n".join(self.runs())
        self.assertIn("|".join(names.values()), runs)
        self.assertNotIn("hidden", runs)

    def test_credential_variables_are_still_kept_back(self):
        for name in ("ANTHROPIC_API_KEY", "GH_TOKEN", "AWS_SECRET_ACCESS_KEY", "PGPASSWORD", "CLAUDE_CODE_OAUTH_TOKEN",
                     "NPM_AUTH_TOKEN", "DATABASE_PASSWORD", "GOOGLE_APPLICATION_CREDENTIALS"):
            self.assertTrue(spike.looks_secret(name), name)

    def test_more_private_key_shapes_are_redacted(self):
        for block in ("-----BEGIN PGP PRIVATE KEY BLOCK-----\nlQOYBGabc123\n-----END PGP PRIVATE KEY BLOCK-----",
                      "-----BEGIN RSA PRIVATE KEY-----\nlQOYBGabc123"):
            self.put(record(command="cat key.txt", code=f"```text\n# file: key.txt\n{block}\n```"))
            self.run_spike()
            runs = "\n".join(self.runs())
            self.assertIn("[redacted: private key]", runs, block)
            self.assertNotIn("lQOYBGabc123", runs, block)

    def test_any_bearer_header_is_redacted(self):
        self.put(record(command="printf 'authorization: bearer abcdefghijklmnop1234\\nBearer\\tqrstuvwxyz567890\\n'"))
        self.run_spike()
        runs = "\n".join(self.runs())
        self.assertNotIn("abcdefghijklmnop1234", runs)
        self.assertNotIn("qrstuvwxyz567890", runs)

    def test_an_observation_is_redacted_too(self):
        self.put(record(command="echo ran"))
        token = "ghp_" + "a" * 36
        self.run_spike("--observation", f"It worked with token {token}")
        runs = "\n".join(self.runs())
        self.assertNotIn(token, runs)
        self.assertIn("1 value hidden", runs)

    def test_a_short_secret_never_garbles_another_secrets_name(self):
        self.put(record(command='printf "$API_KEY $SHORT\\n"', secrets="`API_KEY`, `SHORT`"))
        self.run_spike(env={"API_KEY": "long-value-123456", "SHORT": "API"})
        runs = "\n".join(self.runs())
        self.assertIn("[secret: API_KEY] [secret: SHORT]", runs)
        self.assertIn("2 values hidden", runs)

    def test_session_tokens_are_still_kept_back(self):
        for name in ("OP_SESSION_my", "AWS_SESSION_TOKEN", "ACCESS_TOKEN_SOCK"):
            self.assertTrue(spike.looks_secret(name), name)
        for name in ("DBUS_SESSION_BUS_ADDRESS", "SESSION_MANAGER", "TERM_SESSION_ID", "XDG_SESSION_TYPE",
                     "SSH_AUTH_SOCK", "GIT_AUTHOR_NAME"):
            self.assertFalse(spike.looks_secret(name), name)

    def test_overlapping_secrets_are_hidden_whole(self):
        self.put(record(command="cat out.txt", secrets="`SHORT`", code="```text\n# file: out.txt\nxyzabcdef123456\n```"))
        self.run_spike(env={"SHORT": "xyzab", "MY_TOKEN": "abcdef123456"})
        runs = "\n".join(self.runs())
        for piece in ("xyz", "cdef123456"):
            self.assertNotIn(piece, runs)

    def test_removes_leftovers_from_the_other_folder_too(self):
        self.put(record("💡 Confirmed"), name="finished")
        key = spike.project_key(self.project)
        in_temp = os.path.join(self.fallback(), f"{key}-finished")
        os.makedirs(in_temp)
        self.put(record())
        self.run_spike(env={"TMPDIR": self.tmp.name})
        self.assertFalse(os.path.exists(in_temp))

    def test_keeps_windows_line_endings(self):
        pathlib.Path(self.path()).write_bytes(record().replace("\n", "\r\n").encode("utf-8"))
        self.run_spike()
        written = pathlib.Path(self.path()).read_bytes()
        self.assertIn(b"### Run 1", written)
        self.assertNotIn(b"\n", written.replace(b"\r\n", b""))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Run a spike record's experiment once and add what it produced to the record's Runs section.

This script is the only way /spike runs an experiment, so a record's runs are exactly what the
experiment produced and never retyped (ADR 0020). It writes the record itself, so the status hook,
which refuses every other change to Runs, never sees it.

Each call is one run. It refuses unless the record is `🟢 Ready to run`. It builds a fresh working
folder at <data>/spikes/<hash of the project path>-<record name>/, outside the repository, or, when
the data folder can't be written, as in a sandbox, in a folder only this user can open in the
system's temporary folder, agentic-spikes-<user id>/:

1. When the Experiment names a commit (`- Starts from commit:`), the folder is filled with
   `git archive <commit>`, so neither the working tree nor .git is ever changed, and any ```diff
   block in the Code section is applied to it.
2. Every other block in the Code section is written to the file its first line names, such as
   `# file: check.py` or `// file: data.json`; that first line is left out of the file.
3. Each input (`- Inputs:`) is checked to be in the commit's copy, or, for a web address, fetched
   into the folder under the last part of its path.
4. The command (`- Command:`) runs there with `sh -c`, stdout and stderr together. A record whose
   Command is "None." takes only observations.

It then adds `### Run N` at the end of the Runs section, reading the record afresh, with the time
(UTC), the operating system, whether it ran on the person's machine or in a cloud session (the
CLAUDE_CODE_REMOTE variable), a 12-character SHA-256 hash of the Code section, the command's exit
code, and the output in a code fence longer than any run of backticks in it. The value of each
secret named in `- Secrets:`, and of any variable whose name looks like a credential and whose
value is 8 characters or more, is replaced by `[secret: NAME]`, and the common shapes of
credentials, such as GitHub, AWS, Slack and `sk-` keys, web tokens, bearer headers and private
keys, by `[redacted: <kind>]`, in an observation too; the run's heading says how many values were
hidden; output over 500
lines keeps its first and last 200, saying how many were left out. Variables whose names look like
credentials, such as *_TOKEN or *_KEY, are kept from the experiment unless named under Secrets. A
run still going 9 minutes after the script started, building the folder included, is stopped with
everything it started, and recorded as such. A secret that is not set is
recorded as a run that did not happen, saying which, without running anything. With --observation,
it records the person's words, marked as their observation, instead.

Finally it deletes the working folder, and any folder this project left in either place for a
record that is finished or no longer exists. Other projects' folders are never touched.

The `words` command counts the words in a record's plain part, everything from the title down to
`## Experiment` apart from HTML comments, in two parts: the verdict, its Finding, Next steps,
Results and Surprises, and the design, the rest. It says whether each is within what the status
hook allows when the record moves forward: 600 words for the design and 400 for the verdict.
"""

import argparse
import datetime
import hashlib
import io
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import tempfile
import urllib.parse
import urllib.request

# The record is read with the status hook's own parsing, so the two always agree on where each
# section ends and what the status is. The hook lives in the plugin's scripts/ folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from status_check import (DESIGN_LIMIT, FENCE, FINISHED, READY_TO_RUN,  # noqa: E402
                          SPIKE_STATUSES, VERDICT_LIMIT, headings_allowed, lifecycle_status, section,
                          spike_words)

MAX_LINES, KEPT_LINES = 500, 200
TIME_LIMIT = 540  # seconds: under the 10 minutes Claude Code's shell tool allows a command
# Names of environment variables that hold credentials; only those named under Secrets reach a run.
# A word of the name, between underscores, must be one of these, or the name must end in one of
# the first five, as PGPASSWORD does; so GIT_AUTHOR_NAME doesn't match.
SECRET_NAME = re.compile(r"^(?:.*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD)$|"
                         r"(?:.*_)?(?:API_?KEY|KEY|KEYS|TOKEN|SECRET|SECRETS|PASSWORD|PASSWD|PASS|PAT|SESSION|"
                         r"CREDENTIAL|CREDENTIALS|AUTH|OAUTH|PRIVATE|COOKIE|COOKIES)(?:_.*)?$)", re.I)
# Names that match but that systems set for things that are not credentials.
NOT_SECRET = re.compile(r"^(?:SSH_AUTH_SOCK|DBUS_SESSION_BUS_ADDRESS|SESSION_MANAGER|TERM_SESSION_ID|"
                        r"XDG_SESSION_[A-Z]+)$")


def looks_secret(name):
    return bool(SECRET_NAME.search(name)) and not NOT_SECRET.match(name)


FILE_LINE = re.compile(r"^\s*(?:#|//|--|;|%|/\*|<!--)?\s*file:\s*(\S+)")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
NONE = {"", "none", "none."}


class RecordError(Exception):
    """The record can't be run as it stands; nothing was recorded."""


def status_of(text):
    return lifecycle_status(text, SPIKE_STATUSES)


def setting(experiment, label):
    """The text after `- <label>:` in the Experiment section, or None if no such line."""
    for line in experiment:
        match = re.match(rf"\s*[-*]\s*{re.escape(label)}\s*:\s*(.*)$", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def spans(value):
    """The code spans in a setting, or [] when it says None."""
    if value is None or value.strip().lower() in NONE:
        return []
    found = [match.group(2).strip() for match in CODE_SPAN.finditer(value)]
    if not found:
        raise RecordError(f"could not read '{value}': write each value in backticks, or \"None.\"")
    return found


def closes(line, fence):
    match = FENCE.match(line)
    return bool(match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
                and not match.group(2).strip())


def code_blocks(code):
    """The Code section's fenced blocks as (info string, [lines])."""
    blocks, current, fence, info = [], None, None, ""
    for line in code:
        match = FENCE.match(line)
        if current is None:
            if match:
                current, fence, info = [], match.group(1), match.group(2).strip()
        elif closes(line, fence):
            blocks.append((info, current))
            current = None
        else:
            current.append(line)
    if current is not None:
        blocks.append((info, current))
    return blocks


def read_record(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as error:
        raise RecordError(f"could not read {path} ({error})")


def project_of(record_path):
    """The project folder: the record sits in <project>/docs/spikes/."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(record_path))))


def project_key(project):
    return hashlib.sha256(os.path.abspath(project).encode("utf-8")).hexdigest()[:12]


def fallback_root():
    """The folder used when the data folder can't be written: one in the system's temporary
    folder that only this user can open, so other users can neither read the experiment nor
    put anything in its place."""
    return os.path.join(tempfile.gettempdir(), f"agentic-spikes-{os.getuid()}")


def writable(folder):
    try:
        os.makedirs(folder, exist_ok=True)
        os.rmdir(tempfile.mkdtemp(dir=folder))
        return True
    except OSError:
        return False


def spikes_root(data):
    """<data>/spikes, or fallback_root() when that can't be written, as in a sandbox that blocks
    the plugin's own folders."""
    root = os.path.join(os.path.abspath(data), "spikes")
    if writable(root):
        return root
    fallback = fallback_root()
    try:
        os.makedirs(fallback, mode=0o700, exist_ok=True)
        info = os.lstat(fallback)
    except OSError as error:
        raise RecordError(f"neither {root} nor {fallback} can be written ({error})")
    if not os.path.isdir(fallback) or os.path.islink(fallback) or info.st_uid != os.getuid() \
            or info.st_mode & 0o077:
        raise RecordError(f"{fallback} is not a folder only you can open; delete it and run again")
    return fallback


def work_folder(data, record_path, root=None):
    """The working folder for one record: <spikes root>/<project hash>-<record name>/."""
    name = os.path.splitext(os.path.basename(record_path))[0]
    return os.path.join(root or spikes_root(data), f"{project_key(project_of(record_path))}-{name}")


def inside(folder, name):
    """The path of `name` inside `folder`, refusing absolute paths and any that leave it, even by a link."""
    full = os.path.normpath(os.path.join(folder, name))
    root = os.path.realpath(folder)
    if os.path.isabs(name) or not os.path.realpath(full).startswith(root + os.sep):
        raise RecordError(f"the file {name} must be a relative path inside the working folder")
    return full


def plan(text):
    """Everything the run needs from the record, or a RecordError saying what doesn't follow the template."""
    if status_of(text) != READY_TO_RUN:
        raise RecordError(f"the record must be `{READY_TO_RUN}` to run; the person signs the design off first")
    if section(text, "Runs") is None:
        raise RecordError("the record has no `## Runs` section; add it from the template, last")
    experiment = section(text, "Experiment")
    if experiment is None:
        raise RecordError("the record has no `## Experiment` section")
    command = setting(experiment, "Command")
    commands = spans(command)
    if command is None or len(commands) > 1:
        raise RecordError("the Experiment needs one `- Command:` line holding the command in backticks, or "
                          "\"None.\" when every run is the person's observation")
    commits = spans(setting(experiment, "Starts from commit"))
    if len(commits) > 1:
        raise RecordError("`- Starts from commit:` names one commit")
    inputs = spans(setting(experiment, "Inputs"))
    secrets = spans(setting(experiment, "Secrets"))
    diffs, files = [], []
    for info, lines in code_blocks(section(text, "Code") or []):
        if info.split()[:1] == ["diff"]:
            diffs.append("\n".join(lines) + "\n")
            continue
        named = FILE_LINE.match(lines[0]) if lines else None
        if not named:
            raise RecordError("each code block must name its file on its first line, such as `# file: check.py`; "
                              "a change to the product's code is a ```diff block")
        files.append((named.group(1).rstrip("*/>-").rstrip(), "\n".join(lines[1:]) + "\n"))
    local = [name for name in inputs if "://" not in name]
    if (local or diffs) and not commits:
        raise RecordError("the record uses the repository's files but has no `- Starts from commit:`; name the "
                          "commit the copy is made from")
    code = "\n".join(section(text, "Code") or []).strip()
    return {
        "command": commands[0] if commands else None, "commit": commits[0] if commits else None, "inputs": inputs,
        "secrets": secrets, "diffs": diffs, "files": files,
        "hash": hashlib.sha256(code.encode("utf-8")).hexdigest()[:12],
    }


def left(deadline):
    """Seconds left before the run's time limit, at least 1."""
    return max(1, deadline - time.monotonic())


def git(project, *args, **kwargs):
    return subprocess.run(["git", "-C", project, *args], capture_output=True, **kwargs)


def fill(folder, project, steps):
    """Build the working folder from the record: commit copy, diff, code files, inputs."""
    if steps["commit"]:
        commit = steps["commit"]
        if git(project, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            raise RecordError(f"commit {commit} is not in this repository; if it is a shallow clone, fetch it first, "
                              f"for example with `git fetch --unshallow`")
        archive = git(project, "archive", "--format=tar", commit, timeout=left(steps["deadline"]))
        if archive.returncode != 0:
            raise RecordError(f"git archive {commit} failed: {archive.stderr.decode(errors='replace').strip()}")
        try:
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
                if hasattr(tarfile, "data_filter"):
                    tar.extractall(folder, filter="data")
                else:
                    for member in tar.getmembers():
                        inside(folder, member.name)
                        if member.issym() or member.islnk():
                            inside(folder, os.path.join(os.path.dirname(member.name), member.linkname))
                    tar.extractall(folder)
        except (tarfile.TarError, OSError) as error:
            raise RecordError(f"could not copy commit {commit} into the working folder ({error})")
    for diff in steps["diffs"]:
        applied = subprocess.run(["git", "apply", "--whitespace=nowarn", "-"], cwd=folder, input=diff.encode("utf-8"),
                                 capture_output=True, timeout=left(steps["deadline"]))
        if applied.returncode != 0:
            raise RecordError(f"the diff in Code does not apply to commit {steps['commit']}: "
                              f"{applied.stderr.decode(errors='replace').strip()}")
    for name, content in steps["files"]:
        path = inside(folder, name)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as error:
            raise RecordError(f"could not write {name} into the working folder ({error})")
    for name in steps["inputs"]:
        if "://" in name:
            target = inside(folder, os.path.basename(urllib.parse.urlparse(name).path.rstrip("/")) or "input")
            try:
                with urllib.request.urlopen(name, timeout=min(60, left(steps["deadline"]))) as response, \
                        open(target, "wb") as f:
                    shutil.copyfileobj(response, f)
            except (OSError, ValueError) as error:
                raise RecordError(f"could not fetch the input {name} ({error})")
        elif not os.path.exists(inside(folder, name)):
            raise RecordError(f"the input {name} is not in commit {steps['commit']}")


def shorten(output):
    lines = output.split("\n")
    if len(lines) <= MAX_LINES:
        return output
    left_out = len(lines) - 2 * KEPT_LINES
    return "\n".join(lines[:KEPT_LINES] + [f"({left_out} lines left out)"] + lines[-KEPT_LINES:])


def fenced(output):
    longest = max((len(run) for run in re.findall(r"`+", output)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}\n{output.rstrip(chr(10))}\n{fence}"


def where():
    system = platform.system()
    if system == "Darwin" and platform.mac_ver()[0]:
        system_name = f"macOS {platform.mac_ver()[0]}"
    else:
        system_name = f"{system} {platform.release()}".strip()
    place = "a cloud session" if os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true" else "your machine"
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC, {system_name}, {place}"


def remove_leftovers(data, record_path):
    """Delete this project's working folders, in either place, whose records are finished or gone."""
    prefix = project_key(project_of(record_path)) + "-"
    folder = os.path.dirname(os.path.abspath(record_path))
    for spikes in (os.path.join(os.path.abspath(data), "spikes"), fallback_root()):
        try:
            names = sorted(os.listdir(spikes)) if os.path.isdir(spikes) and not os.path.islink(spikes) else []
        except OSError:
            continue
        for name in names:
            if not name.startswith(prefix):
                continue
            record = os.path.join(folder, name[len(prefix):] + ".md")
            try:
                status = status_of(read_record(record)) if os.path.exists(record) else None
            except RecordError:
                continue
            if status is None or status in FINISHED:
                shutil.rmtree(os.path.join(spikes, name), ignore_errors=True)


def append_run(path, heading_line, body):
    """Add a run at the end of the Runs section, reading the record afresh so no edit made while
    the experiment ran is lost."""
    text = read_record(path)
    if status_of(text) != READY_TO_RUN:
        raise RecordError(f"the record stopped being `{READY_TO_RUN}` while the experiment ran; nothing was recorded")
    with open(path, encoding="utf-8", newline="") as f:
        newline = "\r\n" if "\r\n" in f.read() else "\n"
    lines = text.splitlines()
    allowed = headings_allowed(lines)
    start = next((i for i, line in enumerate(lines) if allowed[i] and line.strip().lower() == "## runs"), None)
    if start is None:
        raise RecordError("the record has no `## Runs` section; add it from the template, last")
    end = next((i for i in range(start + 1, len(lines)) if allowed[i] and lines[i].startswith(("# ", "## "))), len(lines))
    number = sum(1 for i in range(start + 1, end) if allowed[i] and re.fullmatch(r"### Run \d+\s*", lines[i])) + 1
    entry = f"### Run {number}\n\n{heading_line}\n\n{body}\n"
    before = "\n".join(lines[:end]).rstrip("\n")
    after = "\n".join(lines[end:])
    new = before + "\n\n" + entry + ("\n" + after + "\n" if after else "")
    with open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(new)
    return entry


def experiment_env(secrets):
    """Claude Code's environment, without the variables that look like credentials unless the
    Experiment names them under Secrets."""
    return {name: value for name, value in os.environ.items() if name in secrets or not looks_secret(name)}


# Common shapes of credentials, hidden wherever they appear in a run's output.
CREDENTIALS = [
    # To its END line, or to the end of the output when that line never came, as in a stopped run.
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY[A-Z ]*-----.*?(?:-----END [A-Z ]*PRIVATE KEY[A-Z ]*-----|\Z)",
                               re.S)),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("AWS key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("web token", re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{10,}")),
    ("bearer token", re.compile(r"(?i:(?P<keep>\bbearer\s+))[A-Za-z0-9._~+/=-]{12,}")),
]


def hide(output, secrets):
    """Hide secrets in a run's output: (output, how many values were hidden).

    The value of each secret named under Secrets, and of every variable whose name looks like a
    credential, is replaced by its name, longest value first, so one never half-hides another.
    Then the common shapes of credentials are replaced by their kind."""
    hidden = 0
    # An unnamed variable's value is hidden only when long enough to be a credential, so flags
    # such as `1` or `true` are left alone.
    values = {}
    for name, value in os.environ.items():
        if value and (name in secrets or (looks_secret(name) and len(value) >= 8)):
            values.setdefault(value, name)
    # Every place any value appears, overlapping places joined, so no part of one is left showing;
    # a joined place is named after its longest value.
    places = []
    for value, name in values.items():
        start = output.find(value)
        while start >= 0:
            places.append([start, start + len(value), len(value), name])
            start = output.find(value, start + 1)
    joined = []
    for place in sorted(places):
        if joined and place[0] < joined[-1][1]:
            last = joined[-1]
            last[1] = max(last[1], place[1])
            if place[2] > last[2]:
                last[2], last[3] = place[2], place[3]
        else:
            joined.append(place)
    for start, end, _, name in reversed(joined):
        output = output[:start] + f"[secret: {name}]" + output[end:]
    hidden = len(joined)
    for kind, pattern in CREDENTIALS:
        output, count = pattern.subn(lambda match: (match.groupdict().get("keep") or "") + f"[redacted: {kind}]",
                                     output)
        hidden += count
    return output, hidden


def hidden_note(hidden):
    return f", {hidden} value{'s' if hidden != 1 else ''} hidden" if hidden else ""


def run(record_path, data, observation=None):
    """Run the experiment once, or record an observation; return the Runs entry added."""
    deadline = time.monotonic() + TIME_LIMIT
    if not data:
        raise RecordError('the plugin\'s data folder is empty: pass --data "${CLAUDE_PLUGIN_DATA}"')
    text = read_record(record_path)
    steps = plan(text)
    steps["deadline"] = deadline
    stamp = f"{where()}, code `{steps['hash']}`"
    if observation is not None:
        words, hidden = hide(observation, steps["secrets"])
        return append_run(record_path, f"{stamp}, the person's observation, passed on by Claude{hidden_note(hidden)}",
                          fenced(words))
    if steps["command"] is None:
        raise RecordError("the Experiment's `- Command:` is \"None.\", so each run is the person's observation: "
                          "pass their words with --observation")
    missing = [name for name in steps["secrets"] if not os.environ.get(name)]
    if missing:
        return append_run(record_path, f"{stamp}, did not run",
                          fenced(f"Did not run: the secret {', '.join(missing)} is not set in Claude Code's environment."))
    folder = work_folder(data, record_path, spikes_root(data))
    shutil.rmtree(folder, ignore_errors=True)
    try:
        os.makedirs(folder)
    except OSError as error:
        raise RecordError(f"could not make the working folder {folder} ({error})")
    stopped = f"stopped after {TIME_LIMIT // 60} minutes without finishing"
    try:
        try:
            fill(folder, project_of(record_path), steps)
        except subprocess.TimeoutExpired:
            output, ended = b"", stopped + ", before the command started"
        else:
            output, ended = execute(steps["command"], folder, experiment_env(steps["secrets"]), left(deadline))
            ended = ended or stopped
    finally:
        shutil.rmtree(folder, ignore_errors=True)
        remove_leftovers(data, record_path)
    text_output, hidden = hide(output.decode("utf-8", errors="replace"), steps["secrets"])
    return append_run(record_path, f"{stamp}, {ended}{hidden_note(hidden)}", fenced(shorten(text_output)))


def execute(command, folder, env, timeout):
    """Run the command in its own process group: (output, "exit code N"), or (output so far, None)
    when it ran out of time. Everything left in the group is stopped when the command ends, so
    nothing it started keeps the secrets once the run is recorded. The output goes to a file, not
    a pipe, so a process that leaves the group can't keep the script waiting."""
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(["sh", "-c", command], cwd=folder, stdout=log, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, env=env, start_new_session=True)
        try:
            process.wait(timeout=timeout)
            ended = f"exit code {process.returncode}"
        except subprocess.TimeoutExpired:
            ended = None
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            pass
        process.wait()
        log.seek(0)
        return log.read(), ended


def words(path):
    try:
        text = read_record(path)
    except RecordError:
        print(f"{os.path.basename(path)}: can't read {path}", file=sys.stderr)
        return 1
    design, verdict = spike_words(text)
    name = os.path.basename(path)
    print(f"{name}: the design holds {design} of the {DESIGN_LIMIT} words allowed, and the verdict holds "
          f"{verdict} of the {VERDICT_LIMIT} words allowed")
    status = status_of(text)
    if status in FINISHED:
        return 0  # final: never changed again, so there is nothing to shorten
    over = False
    if design > DESIGN_LIMIT:
        over = True
        print(f"the design is {design - DESIGN_LIMIT} over; "
              + ("its other sections are fixed now, so shorten its title" if status == READY_TO_RUN
                 else "shorten it, moving detail down into Experiment"))
    # The verdict is written after the runs, and the status hook checks it only at a finishing status.
    if status == READY_TO_RUN and verdict > VERDICT_LIMIT:
        over = True
        print(f"the verdict is {verdict - VERDICT_LIMIT} over; shorten its Finding, Next steps, Results or Surprises")
    return 1 if over else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser(
        "run",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="run the record's experiment once and record it",
        epilog=(
            "git archive leaves out files marked export-ignore, submodules' contents and the contents of files kept "
            "in large-file storage, so an experiment that needs them names them as inputs by web address. "
            "Output: the Runs entry added, on stdout. Exit codes: 0 a run or observation was recorded, whatever "
            "the experiment's own exit code; 1 the record can't be run as it stands, with the reason on stderr, "
            "and nothing was recorded."
        ),
    )
    run_parser.add_argument("record", help="the spike record, a .md file in docs/spikes/")
    run_parser.add_argument("--data", required=True, help='the plugin\'s data folder: "${CLAUDE_PLUGIN_DATA}"')
    run_parser.add_argument("--observation", metavar="TEXT",
                            help="record the person's own words as this run, for a step only they can do")
    words_parser = commands.add_parser(
        "words",
        help="count the words in the record's design and verdict",
        description="Count the words in a spike record's plain part, from the title down to Experiment, "
                    "apart from HTML comments, as the status hook counts them: the verdict (Finding, Next "
                    "steps, Results and Surprises) and the design (the rest) apart.",
        epilog=f"Exit codes: 0 with the design within {DESIGN_LIMIT} words and, once the record is Ready "
               f"to run, the verdict within {VERDICT_LIMIT}, or for a finished record; 1 when either is "
               f"over, or the record can't be read, with the reason on stderr. Output: both counts, their "
               f"limits and what to shorten, on stdout.",
    )
    words_parser.add_argument("record", help="the spike record, a .md file in docs/spikes/")
    args = parser.parse_args(argv)
    if args.command == "words":
        return words(args.record)
    try:
        entry = run(args.record, args.data, args.observation)
    except RecordError as error:
        print(f"{os.path.basename(args.record)}: {error}", file=sys.stderr)
        return 1
    print(entry, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

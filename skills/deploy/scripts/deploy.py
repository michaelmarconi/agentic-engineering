#!/usr/bin/env python3
"""Check a commit may be deployed, and run a deploy's recorded check until it passes, for /deploy.

[--repo <folder>] preflight --commit <commit> [--branch <branch>] [--checked-out]
    Checks, by git alone, what /deploy can check before it asks for a yes: nothing is uncommitted
    (scripts/uncommitted.py); the commit is on the remote, on some `origin/` branch as this
    repository last fetched it; with --branch, it is on `origin/<branch>`, for a practice whose
    Releases allowed names a branch; with --checked-out, it is the commit checked out, for a
    Deploy command that works from the checkout rather than taking {commit}. It fetches nothing,
    so fetch first. Prints one line per problem, or "The commit may be deployed."; then the commit
    in full, and a line when it is not on the default branch (`origin/HEAD`), or when that branch
    is not known here.

check --wait <seconds> [--every <seconds>] -- <command>
    Runs the recorded check, and again every --every seconds (default 5) until it exits 0 or the
    next try would start after --wait seconds; --wait 0 runs it once. Give the command as one
    argument, exactly as recorded, to run it with the shell (`sh -c`), or as several to run that
    program directly. Each try may take the time left of the wait, and at least 60 seconds; a try
    that runs out of time is stopped with every process it started. A program that can't be
    started is not tried again. Prints each try's exit code, the last try's output, then whether
    the check passed.

Exit codes: preflight 0 when the commit may be deployed, 1 when it found a problem; check 0 when
the check passed, 1 when it did not; both 2 for a commit that can't be found, a folder that is not
a git repository, or wrong use.
"""

import argparse
import os
import subprocess
import sys
import signal
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import uncommitted  # noqa: E402

EVERY = 5
SHORTEST_TRY = 60


class Unusable(Exception):
    """A commit or the repository can't be used; the message says why."""


def git(repo, *args):
    try:
        return uncommitted.git(repo, *args)
    except uncommitted.NotARepository as error:
        raise Unusable(str(error))


def resolve(repo, ref):
    found = git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if found.returncode != 0 or not found.stdout.strip():
        raise Unusable(f"no commit named {ref} was found")
    return found.stdout.strip()


def preflight(repo, commit, branch=None, checked_out=False):
    try:
        entries, _ = uncommitted.check(repo)
    except uncommitted.NotARepository as error:
        raise Unusable(str(error))
    sha = resolve(repo, commit)
    problems = []
    if entries:
        problems.append("There is uncommitted work, so what is deployed might not match the commit.")
    remote = git(repo, "for-each-ref", "--contains", sha, "--format=%(refname)", "refs/remotes/origin/")
    if not remote.stdout.strip():
        problems.append("The commit is not on the remote, so it has not been pushed yet.")
    if branch:
        tip = git(repo, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branch}")
        if tip.returncode != 0:
            problems.append(f"origin/{branch} is not known here: fetch it, or check the branch the practice names.")
        elif git(repo, "merge-base", "--is-ancestor", sha, tip.stdout.strip()).returncode != 0:
            problems.append(f"The commit is not on origin/{branch}, the branch Releases allowed names.")
    if checked_out and resolve(repo, "HEAD") != sha:
        problems.append("The commit is not the one checked out, and the Deploy command works from the checkout.")
    lines = problems or ["The commit may be deployed."]
    lines.append(f"Commit: {sha}")
    default = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD").stdout.strip()
    if not default:
        lines.append("The default branch is not known here (origin/HEAD is not set), so whether the "
                     "commit is on it was not checked.")
    elif git(repo, "merge-base", "--is-ancestor", sha, default).returncode != 0:
        lines.append(f"The commit is not on the default branch ({default.split('/', 1)[-1]}).")
    return (1 if problems else 0), lines


def run_once(command, timeout):
    """(exit code, output) of one try; the code is None when the command could not be started.
    A try that runs out of time is stopped with every process it started."""
    shell = len(command) == 1
    try:
        child = subprocess.Popen(command[0] if shell else command, shell=shell, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    except OSError as error:
        return None, f"The command could not be started: {error}"
    try:
        output, _ = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop(child)
        output, _ = child.communicate()
        return "timed out", output.decode("utf-8", "replace") + f"\n(stopped after {timeout:g} seconds)"
    return child.returncode, output.decode("utf-8", "replace")


def stop(child):
    """Stop the try and everything it started, which share its process group."""
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except (AttributeError, OSError):
        child.kill()


def check(command, wait, every=EVERY, run=run_once, clock=time.monotonic, pause=time.sleep):
    start = clock()
    lines = []
    n = 0
    while True:
        n += 1
        code, output = run(command, max(wait - (clock() - start), SHORTEST_TRY))
        lines.append(f"Try {n}: " + ("could not be started" if code is None else
                                     code if isinstance(code, str) else f"exit {code}"))
        if code == 0 or code is None or clock() - start + every > wait:
            break
        pause(every)
    lines += ["Output of the last try:", output.rstrip() or "(none)"]
    if code == 0:
        lines.append("The check passed.")
        return 0, lines
    lines.append("The check did not pass." if wait == 0 or code is None
                 else f"The check did not pass within {wait:g} seconds.")
    return 1, lines


def seconds(text):
    value = float(text)
    if value < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return value


def pause_seconds(text):
    value = float(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be more than 0")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog=__doc__.split("\n\n", 1)[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="the repository (default: the current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    before = commands.add_parser("preflight", help="check a commit may be deployed")
    before.add_argument("--commit", required=True, help="the commit to deploy")
    before.add_argument("--branch", help="the branch Releases allowed names, if it names one")
    before.add_argument("--checked-out", action="store_true",
                        help="the commit must be the one checked out (Deploy does not take {commit})")
    after = commands.add_parser("check", help="run the recorded check until it passes or the wait runs out")
    after.add_argument("--wait", type=seconds, required=True, help="the recorded wait in seconds; 0 runs it once")
    after.add_argument("--every", type=pause_seconds, default=EVERY, help=f"seconds between tries (default {EVERY})")
    after.add_argument("probe", nargs=argparse.REMAINDER, help="-- then the recorded check command")
    args = parser.parse_args(argv)
    if args.command == "check":
        probe = args.probe[1:] if args.probe[:1] == ["--"] else args.probe
        if not probe:
            after.error("give the check command after --")
        code, lines = check(probe, args.wait, args.every)
    else:
        try:
            code, lines = preflight(os.path.abspath(args.repo), args.commit, args.branch, args.checked_out)
        except Unusable as error:
            print(f"Refused: {error}.")
            return 2
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())

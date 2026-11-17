#!/usr/bin/env python3
"""Gather a release's notes from git, and check a commit may be published, for /release.

notes [--since <commit>] [--to <commit>] [--repo <folder>]
    Lists the commits reachable from --to (default HEAD) and not from --since, the last release's
    commit; with no --since, every commit up to --to. Each build leaves its release notes in a
    commit message as lines starting `Release-note:` (docs/adrs/0043). The script reads every such
    line anywhere in each message, in any case, not only at its end, since a squash merge folds a
    branch's messages into one body. A label with no text after it is not a note. The same note
    found twice, as when a build hands over again, is given once, at its oldest commit. Commits that
    changed files and hold no note are listed apart with their subject; merge commits are not, since
    their branch's commits are listed themselves. Prints JSON: since, to, notes [{commit, note}]
    oldest first, without_notes [{commit, subject}] oldest first.

publish-check --commit <commit> --branch <branch> [--repo <folder>]
    Checks, by git alone, that the commit may be published from the branch the practice releases
    from: nothing is uncommitted (scripts/uncommitted.py), and the commit is on `origin/<branch>`
    as this repository last fetched it. It fetches nothing, so fetch first. Prints one line per
    problem, or that the commit may be published; then names the commit, says when the branch is
    not the default branch (`origin/HEAD`), and lists any newer commits on `origin/<branch>`, which
    the publish will leave out.

Exit codes: 0 when the notes were listed or the commit may be published; 1 when publish-check
found a problem; 2 when a commit can't be found, --since is not before --to, or git can't be run.
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import uncommitted  # noqa: E402

NOTE = re.compile(r"^\s*release-note:[ \t]*(?P<note>.*?)\s*$", re.I | re.M)
SEPARATOR = "\x1e"


class Unusable(Exception):
    """A commit or the repository can't be used; the message says why."""


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def resolve(repo, ref):
    found = git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if found.returncode != 0 or not found.stdout.strip():
        raise Unusable(f"no commit named {ref} was found")
    return found.stdout.strip()


def notes(repo, since=None, to="HEAD"):
    end = resolve(repo, to)
    start = resolve(repo, since) if since else None
    if start and git(repo, "merge-base", "--is-ancestor", start, end).returncode != 0:
        raise Unusable(f"the last release {since} is not before {to}")
    span = [f"{start}..{end}"] if start else [end]
    listed = git(repo, "log", "--reverse", f"--format=%H%x00%P%x00%s%x00%B{SEPARATOR}", *span)
    if listed.returncode != 0:
        raise Unusable((listed.stderr or listed.stdout).strip())
    found, without, seen = [], [], set()
    for entry in listed.stdout.split(SEPARATOR):
        entry = entry.lstrip("\n")
        if not entry:
            continue
        sha, parents, subject, body = entry.split("\x00", 3)
        held = [m.group("note") for m in NOTE.finditer(body) if m.group("note")]
        for note in held:
            if note not in seen:
                seen.add(note)
                found.append({"commit": sha, "note": note})
        if not held and len(parents.split()) < 2 and changed_files(repo, sha):
            without.append({"commit": sha, "subject": subject})
    return {"since": start, "to": end, "notes": found, "without_notes": without}


def changed_files(repo, sha):
    shown = git(repo, "show", "--format=", "--name-only", sha)
    return bool(shown.stdout.strip())


def publish_check(repo, commit, branch):
    sha = resolve(repo, commit)
    problems, lines = [], []
    try:
        entries, _ = uncommitted.check(repo)
    except uncommitted.NotARepository as error:
        raise Unusable(str(error))
    if entries:
        problems.append("There is uncommitted work, so the release would not be exactly one commit.")
    remote = f"origin/{branch}"
    tip = git(repo, "rev-parse", "--verify", "--quiet", f"refs/remotes/{remote}")
    if tip.returncode != 0:
        problems.append(f"{remote} is not known here: fetch it, or check the branch the practice names.")
    elif git(repo, "merge-base", "--is-ancestor", sha, tip.stdout.strip()).returncode != 0:
        problems.append(f"The commit is not on {remote}, so it has not been merged or pushed there yet.")
    lines.append(f"Commit: {sha}")
    default = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD").stdout.strip()
    if default and default.split("/", 1)[-1] != branch:
        lines.append(f"{branch} is not the default branch ({default.split('/', 1)[-1]}).")
    if tip.returncode == 0 and not problems:
        newer = git(repo, "log", "--format=%H %s", f"{sha}..{tip.stdout.strip()}").stdout.strip()
        if newer:
            lines.append(f"Commits on {remote} newer than the release, which it leaves out:")
            lines += [f"- {line}" for line in newer.splitlines()]
    head = problems or ["The commit may be published."]
    return (1 if problems else 0), head + lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog=__doc__.split("\n\n", 1)[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="the repository (default: the current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("notes", help="list the release notes since the last release")
    listing.add_argument("--since", help="the last release's commit; leave out when there is none")
    listing.add_argument("--to", default="HEAD", help="the commit being released (default: HEAD)")
    checking = commands.add_parser("publish-check", help="check a commit may be published")
    checking.add_argument("--commit", required=True, help="the commit to publish")
    checking.add_argument("--branch", required=True, help="the branch the practice releases from")
    args = parser.parse_args(argv)
    repo = os.path.abspath(args.repo)
    try:
        if args.command == "notes":
            print(json.dumps(notes(repo, args.since, args.to), indent=2))
            return 0
        code, lines = publish_check(repo, args.commit, args.branch)
    except Unusable as error:
        print(f"Refused: {error}.")
        return 2
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())

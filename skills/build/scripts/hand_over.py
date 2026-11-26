#!/usr/bin/env python3
"""Hand a build's branch over: commit it, mark the plan Built if the reviews passed, and push.

`/build` runs this however the build ends. It:

1. refuses to run without a remote named `origin` whose default branch is known (`origin/HEAD`),
   on that default branch, or with no branch checked out;
2. commits everything not yet committed, with the message given, leaving out the stand-ins for
   the null device that Claude Code's sandbox puts in place on Linux (see uncommitted.py);
3. with --reviews-passed, sets the plan's status from `Ready to build 🟢` to `Built ✅` and its
   `date:`, the day its status last changed, to today's date on this machine, adding the line under
   the status if the plan has none, changing nothing else in the file, and commits that on its own. It writes the file itself, so the
   status hook, which refuses `Built ✅` from Claude, never sees it;
4. pushes the branch to `origin`, and names the commit the branch is then at, `Head: <commit>`;
5. writes the build's report file (docs/adrs/0051 and 0034) with scripts/run_report.py, in the
   session's scratchpad given by --scratchpad, even when it refused to start: Claude's own sections, read from stdin under the
   report's `## ` headings, then the four reports build_relay.py kept for this plan in this session
   (code review, security review, build review and correction check, each "No report kept." when
   there is none) and this script's own lines, word for word. Sections it can't use, such as one
   under a heading the report doesn't have, stop it before any step, changing nothing.

Every hand-over commit run carries the build's release notes (docs/adrs/0043): each --release-note
is added to the message of the last commit the script makes, as a `Release-note: <note>` line at
its end, so the release skill can gather them later. When no commit it makes carries them, as when
there is nothing to commit or a commit failed, it makes one that holds only the notes, unless the
same notes are already on the branch since the default branch. A note must be one non-empty line.

It prints what happened, one line per step, then the report file's path and the file as written.

When a build's correction check leaves findings open, the build goes through them with the person,
checks only what changed, and hands over again (docs/adrs/0060). Two options serve that, each
reading the newest build report for the plan in this session's scratchpad (run_report.reports), so
a report from another session is never found:

- --open-findings prints the build's own open findings the newest correction check listed, then,
  under `Outside this build:`, those it found in code the build did not change (docs/adrs/0061),
  word for word, and the report's path, or the one reason none can be accepted. It changes nothing
  and writes no report.
- --accept-open-findings, once the person chooses `Built ✅`, marks the plan `Built ✅` as
  --reviews-passed does, commits it with the findings left open and the `## What was built`
  section, which holds the person's answers, in the commit message, pushes, and writes a new report.

Both go ahead only when the plan is `Ready to build 🟢`; the report is of this plan, has a
correction check that failed, or passed with findings outside this build, and its "Built before
sign-off" section is empty; the branch is still at the report's `Head:` commit, with nothing
uncommitted; and the check lists at least one correction `not made` or `left for the person`,
something broken by a correction, or a finding outside this build. The check's labels are known
by name in any case, bold or not, and with a note in brackets, so `Corrections (one commit since
abc123):` still counts as `Corrections:`. A failed check with nothing readable under them is refused with a reason
that says so, for /build to tell the person. An --accept-open-findings that refuses, or whose
commit fails, writes no report, so the newest check stays the newest.

The reviews build_relay.py kept stay on record after a hand-over whose correction check is kept,
until the plan is marked `Built ✅`, so a check after the person's answers still gets them; a
hand-over with no check kept, or of a build before sign-off, clears them as before.

Exit codes: 0 when every step that applied succeeded, or --open-findings found findings; 1 when a
commit, the push or the report file failed, or --reviews-passed was given for a plan that is not
`Ready to build 🟢` (the plan is then left as it is, and the rest still runs); 2 when it refused to
start, could not use Claude's sections, was given an unusable release note or a --scratchpad that
is not this session's, changing nothing in the repository; 3 when
--open-findings found nothing that can be accepted.
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import build_relay  # noqa: E402
import plugin_folder  # noqa: E402
import uncommitted  # noqa: E402
import run_report  # noqa: E402
from status_check import BUILT, READY, STATUSES, meant  # noqa: E402

REVIEWS = (("Code review", "code"), ("Security review", "security"), ("Build review", "plan"),
           ("Correction check", "check"))
NO_REPORT = "No report kept."
NOT_REVIEWED = "No review: the person accepted the build as it stands."

STATUS_LINE = re.compile(r"^status:[ \t]*(?P<value>[^\n#]*?)[ \t]*$", re.M)
# The key in any case and with a space before its colon, as the status hook reads it.
DATE_LINE = re.compile(r"^date[ \t]*:[ \t]*(?P<value>[^\n#]*?)[ \t]*(?:#[^\n]*)?$", re.M | re.I)


def today():
    """Today's date on this machine, as YYYY-MM-DD: the day the plan becomes Built."""
    return datetime.date.today().isoformat()


def built(text, match):
    """The plan's text with the status in `match` set to Built and its `date:` to today, adding the
    date line under the status line if the frontmatter has none."""
    end = text.find("\n---", 3)
    date = DATE_LINE.search(text, 4, end + 1)
    if date:
        dated = (date.start("value"), date.end("value"), today())
    else:
        line_end = text.index("\n", match.end("value")) + 1
        dated = (line_end, line_end, f"date: {today()}\n")
    for start, stop, value in sorted([(match.start("value"), match.end("value"), BUILT), dated], reverse=True):
        text = text[:start] + value + text[stop:]
    return text


NOTE_LABEL = "Release-note:"


def notes_problem(notes):
    """Why the release notes can't be used, or None. Each must be one line with some text."""
    for note in notes:
        if "\n" in note or "\r" in note:
            return "a release note must be one line"
        if not clean_note(note):
            return "a release note must hold some text"
    return None


def clean_note(note):
    """The note's text without any `Release-note:` label it was given with."""
    note = note.strip()
    if note.lower().startswith(NOTE_LABEL.lower()):
        note = note[len(NOTE_LABEL):].strip()
    return note


def with_notes(message, notes):
    """The commit message with a `Release-note:` line for each note at its end."""
    if not notes:
        return message
    return message.rstrip("\n") + "\n\n" + "\n".join(f"{NOTE_LABEL} {clean_note(n)}" for n in notes)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def current_branch(repo):
    result = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else None


def default_branch(repo):
    """The branch `origin/HEAD` names, or None when it is not set."""
    result = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    return result.stdout.strip().split("/", 1)[-1] if result.returncode == 0 and result.stdout.strip() else None


def has_origin(repo):
    return git(repo, "remote", "get-url", "origin").returncode == 0


def frontmatter_status(text):
    """The status line's match inside the frontmatter, or None."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    match = STATUS_LINE.search(text, 4, end + 1)
    return match


def is_ready(value):
    # Read as the status hook reads it: a plan written before the emoji, or with it in front, as
    # earlier versions of the plugin wrote it, counts as the status its words name.
    return meant(value, STATUSES) == READY


def commit(repo, message, lines, allow_empty=False):
    # Leave out the stand-ins Claude Code's sandbox puts in place on Linux: git can't add them,
    # and one it can't add stops `git add -A` from adding anything.
    try:
        _, stand_ins = uncommitted.check(repo)
    except uncommitted.NotARepository as error:
        lines.append(f"Commit failed: {error}")
        return False
    added = git(repo, "add", "-A", "--", ":/", *(f":(top,exclude,literal){path}" for path in stand_ins))
    if added.returncode != 0:
        lines.append(f"Commit failed: {(added.stderr or added.stdout).strip()}")
        return False
    if git(repo, "diff", "--cached", "--quiet").returncode == 0 and not allow_empty:
        return None
    result = git(repo, "commit", "-q", *(["--allow-empty"] if allow_empty else []), "-m", message)
    if result.returncode != 0:
        lines.append(f"Commit failed: {(result.stderr or result.stdout).strip()}")
        return False
    sha = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    lines.append(f"Committed {sha}: {message.splitlines()[0]}")
    return True


def preflight(repo, plan):
    """The refusal, as a line to print, when the branch can't be handed over; else None."""
    if not has_origin(repo):
        return ("Refused: there is no remote named `origin` to push the branch to. Add one, then "
                "hand over again. Nothing was changed.")
    default = default_branch(repo)
    if default is None:
        return ("Refused: the default branch of `origin` is not known. Run "
                "`git remote set-head origin -a`, then hand over again. Nothing was changed.")
    branch = current_branch(repo)
    if branch is None:
        return "Refused: no branch is checked out, so there is nothing to hand over. Nothing was changed."
    if branch == default:
        return f"Refused: `{branch}` is the default branch, and a build never commits there. Nothing was changed."
    if not os.path.isfile(os.path.join(repo, plan)):
        return f"Refused: the plan {plan} does not exist. Nothing was changed."
    return None


def notes_on_branch(repo, notes):
    """Whether every note is already a `Release-note:` line of a commit on the branch since the
    default branch, as when a build hands over again with nothing new."""
    default = default_branch(repo)
    logged = git(repo, "log", "--format=%B", f"origin/{default}..HEAD") if default else None
    if not logged or logged.returncode != 0:
        return False
    held = {line.strip() for line in logged.stdout.splitlines()}
    return all(f"{NOTE_LABEL} {clean_note(n)}" in held for n in notes)


def hand_over(repo, plan, message, reviews_passed, notes=()):
    lines = []
    refusal = preflight(repo, plan)
    if refusal:
        return 2, [refusal]
    branch = current_branch(repo)
    plan_path = os.path.join(repo, plan)
    with open(plan_path, encoding="utf-8") as f:
        match = frontmatter_status(f.read())
    # The notes go on the last commit made: the Built commit when there will be one.
    to_built = reviews_passed and bool(match) and is_ready(match.group("value"))

    code = 0
    lines.append(f"Branch: {branch}")
    done = commit(repo, message if to_built else with_notes(message, notes), lines)
    carried = done is True and not to_built
    if done is None:
        lines.append("Work: nothing new to commit.")
    elif done is False:
        code = 1

    with open(plan_path, encoding="utf-8") as f:
        text = f.read()
    match = frontmatter_status(text)
    status = match.group("value") if match else "no status"
    if reviews_passed and code == 0:
        if match and is_ready(status):
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(built(text, match))
            if commit(repo, with_notes(f"Mark the plan {os.path.basename(plan)} as built", notes), lines):
                carried = True
                lines.append(f"Plan: {plan} is now `{BUILT}`.")
            else:
                code = 1
        else:
            lines.append(f"Plan: {plan} is `{status}`, not `{READY}`, so it was not marked `{BUILT}`.")
            code = 1
    else:
        if reviews_passed:
            reason = "a commit failed"
        elif match and not is_ready(status):
            reason = f"it is not `{READY}`"
        else:
            reason = "the reviews have not all passed"
        lines.append(f"Plan: {plan} stays `{status}`, because {reason}.")

    # No commit carried the notes: record them in a commit of their own, unless the branch holds them.
    if notes and not carried:
        if notes_on_branch(repo, notes):
            lines.append("Release notes: already on the branch, so not recorded again.")
        elif commit(repo, with_notes(f"Record the release notes of the plan {os.path.basename(plan)}", notes),
                    lines, allow_empty=True) is not True:
            code = 1

    code = max(code, push(repo, branch, lines))
    lines.append(f"Head: {head(repo)}")
    return code, lines


def head(repo):
    return git(repo, "rev-parse", "HEAD").stdout.strip()


class NotAcceptable(Exception):
    """The build can't be accepted as it stands; the message says why."""


OPEN = re.compile(r"\b(?:not made|left for the person)\b", re.I)
BULLET = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
NONE_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+\**None\b", re.I)
LABEL = re.compile(r"^\**[A-Z][^:]*:\**\s*$")
# The checker's own labels, known by name whatever their case, bold or not, and with or without a
# note in brackets, such as `Corrections (one commit since abc123: 9ade614):`, which once hid every
# item under it.
PARTS = ("Corrections", "Broken by a correction", "Outside this build", "Suggestions")
PART = re.compile(r"^(?:#+\s*)?\**(" + "|".join(PARTS) + r")\**\s*(?:\(.*\))?\s*:\**\s*$", re.I)


def findings_in(check):
    """The correction check's items for corrections not made or left for the person, and for
    anything a correction broke, word for word, each with the lines that continue it. An item is a
    line starting `-`, `*`, `+` or a number; a line such as `Suggestions:` starts another list."""
    return items_in(check)[0]


def items_in(check):
    """(the build's own open findings, the findings outside this build), each word for word with
    the lines that continue it (docs/adrs/0061)."""
    found, outside, part, keep, indent = [], [], None, None, 0
    for line in check.splitlines():
        label = line.strip()
        depth = len(line) - len(line.lstrip())
        if keep is not None and label and depth > indent:
            keep.append(line)  # a line indented under the kept item, a bullet or not, continues it
            continue
        known = None if BULLET.match(label) else PART.match(label)
        if known or LABEL.match(label):
            part = next(p for p in PARTS if p.lower() == known.group(1).lower()) + ":" if known else label
            keep = None
            continue
        if not label:
            keep = None
            continue
        if BULLET.match(label):
            if part == "Outside this build:" and not NONE_ITEM.match(label):
                keep = outside
            elif (part == "Corrections:" and OPEN.search(label) or
                  part == "Broken by a correction:" and not NONE_ITEM.match(label)):
                keep = found
            else:
                keep = None
            if keep is not None:
                keep.append(line)
                indent = depth
        elif keep is not None:
            keep.append(line)
    return found, outside


def newest_report(repo, plan, root):
    """The path and text of the newest build report whose hand-over names this plan, since another
    plan's name can end like a same-day report's number; raises NotAcceptable when there is none."""
    for path in run_report.reports("build", os.path.splitext(os.path.basename(plan))[0], repo, root):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        output = run_report.subsection(run_report.section("build", text, "The hand-over script's report") or "",
                                       "Output") or ""
        if os.path.normpath(plan) in {os.path.normpath(p) for p in re.findall(r"^Plan: (\S+) ", output, re.M)}:
            return path, text, output
    raise NotAcceptable("No build report for this plan was found in this session")


def open_findings(repo, plan, root):
    """(report path, the build's own open findings, those outside this build) for the plan's newest
    build report, whatever its correction check's result (docs/adrs/0060); raises NotAcceptable."""
    with open(os.path.join(repo, plan), encoding="utf-8") as f:
        match = frontmatter_status(f.read())
    status = match.group("value") if match else "no status"
    if not (match and is_ready(status)):
        raise NotAcceptable(f"the plan {plan} is `{status}`, not `{READY}`")
    path, text, output = newest_report(repo, plan, root)
    check = run_report.subsection(run_report.section("build", text, "What each review found") or "",
                                  "Correction check", after="Build review") or ""
    result = re.search(r"^\**Result:?\**:?\s*\**(\w+)", check, re.M)
    if not result:
        raise NotAcceptable(f"the last build has no correction check ({path})")
    findings, outside = items_in(check)
    if result.group(1).upper() != "FAIL" and not outside:
        raise NotAcceptable(f"the last correction check passed with nothing left open, so hand over "
                            f"with --reviews-passed instead ({path})")
    early = run_report.section("build", text, "Built before sign-off")
    if early and early != run_report.NOTHING:
        raise NotAcceptable("the last build ran before sign-off, so its plan can't be marked Built this way")
    heads = re.findall(r"^Head: (\S+)$", output, re.M)
    if not heads or heads[-1] != head(repo):
        raise NotAcceptable("the branch has changed since the last hand-over, so start the correction "
                            "checker on what changed, then hand over again")
    try:
        entries, _ = uncommitted.check(repo)
    except uncommitted.NotARepository as error:
        raise NotAcceptable(str(error))
    if entries:
        raise NotAcceptable("there is uncommitted work, which no review has seen")
    if not findings and not outside:
        # Only a failed check gets here: one that passed with nothing outside was refused above.
        raise NotAcceptable(f"the correction check failed, yet no open finding could be read from it, so "
                            f"tell the person what its report says is left open ({path})")
    return path, findings, outside


def accept(repo, plan, root, notes=(), answers=""):
    """Mark the plan Built with the findings left open, and the person's answers, in the commit,
    and push: (code, lines)."""
    refusal = preflight(repo, plan)
    if refusal:
        return 2, [refusal]
    try:
        path, findings, outside = open_findings(repo, plan, root)
    except NotAcceptable as error:
        return 2, [f"Refused: {error}. Nothing was changed."]
    lines = [f"Branch: {current_branch(repo)}", f"Accepting the build as it stands, from {path}"]
    plan_path = os.path.join(repo, plan)
    with open(plan_path, encoding="utf-8") as f:
        text = f.read()
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(built(text, frontmatter_status(text)))
    parts = []
    if findings:
        parts.append("Left open by the person, without further review:\n\n" + "\n".join(findings))
    if outside:
        parts.append("Outside this build, left open:\n\n" + "\n".join(outside))
    if answers.strip():
        parts.append("The person's answers:\n\n" + answers.strip())
    body = "\n\n".join(parts)
    if not commit(repo, with_notes(f"Mark the plan {os.path.basename(plan)} as built\n\n{body}", notes), lines):
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(text)
        lines.append(f"Plan: {plan} stays `{READY}`, because the commit failed; nothing was pushed.")
        return 1, lines
    lines += [f"Plan: {plan} is now `{BUILT}`.", body]
    code = push(repo, current_branch(repo), lines)
    lines.append(f"Head: {head(repo)}")
    return code, lines


def push(repo, branch, lines):
    """Push the branch to origin, saying how it went; 0 when it was pushed, else 1."""
    result = git(repo, "push", "-q", "-u", "origin", branch)
    if result.returncode == 0:
        lines.append(f"Push: pushed {branch} to origin.")
        return 0
    lines.append(f"Push: push failed: {(result.stderr or result.stdout).strip()}")
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, help="the plan's path, relative to the repository")
    parser.add_argument("--message", help="the commit message for the work not yet committed (needed to hand over)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--reviews-passed", action="store_true",
                      help="every review of the build passed, so mark the plan Built")
    mode.add_argument("--open-findings", action="store_true",
                      help="print the open findings of the newest correction check, the build's own and then "
                           "those outside this build, or why none can be accepted; change nothing")
    mode.add_argument("--accept-open-findings", action="store_true",
                      help="the person chose Built: mark the plan Built with the findings left open and "
                           "their answers in the commit message, and push")
    parser.add_argument("--release-note", action="append", default=[], metavar="NOTE",
                        help="one sentence for the product's users about what this build gives them, added to "
                             "the last commit's message as a `Release-note:` line; give one per thing they would "
                             "notice (at least one is needed to hand over)")
    parser.add_argument("--repo", default=".", help="the repository (default: the current directory)")
    parser.add_argument("--report", choices=["-"],
                        help="`-`: read your own sections of the build's report from stdin, as Markdown "
                             "under the report's `## ` headings (needed except with --open-findings)")
    parser.add_argument("--scratchpad", default="",
                        help="the session's scratchpad folder, as your instructions name it; leave it out when "
                             "they name none, and the report goes in a private temporary folder")
    parser.add_argument("--session", required=True, help='the session\'s id: "${CLAUDE_SESSION_ID}"')
    args = parser.parse_args(argv)
    repo = os.path.abspath(args.repo)
    try:
        root = plugin_folder.root(args.scratchpad, args.session)
    except plugin_folder.FolderError as error:
        print(f"Refused: {error}. Nothing was changed.")
        return 2
    if args.open_findings:
        if not os.path.isfile(os.path.join(repo, args.plan)):
            print(f"No open findings can be accepted: the plan {args.plan} does not exist.")
            return 3
        try:
            path, findings, outside = open_findings(repo, args.plan, root)
        except NotAcceptable as error:
            print(f"No open findings can be accepted: {error}.")
            return 3
        print(f"Open findings, from the correction check in {path}:")
        print("\n".join(findings) if findings else "None.")
        if outside:
            print("Outside this build:")
            print("\n".join(outside))
        return 0
    missing = [flag for flag, value in (("--report", args.report),
                                        ("--message", args.message or args.accept_open_findings),
                                        ("--release-note", args.release_note)) if not value]
    if missing:
        parser.error("these are needed to hand over: " + ", ".join(missing))
    problem = notes_problem(args.release_note)
    if problem:
        print(f"Refused: {problem}. Nothing was changed; correct the release note and hand over again.")
        return 2
    try:
        own = run_report.parse("build", sys.stdin.read())
    except run_report.ReportError as error:
        print(f"Refused: your report's sections can't be used: {error}. Nothing was changed; correct "
              "them and hand over again.")
        return 2
    if args.accept_open_findings:
        code, lines = accept(repo, args.plan, root, args.release_note, own.get("What was built", ""))
        if not any(line.startswith(f"Plan: {args.plan} is now") for line in lines):
            # No report while the plan is not Built: the failed check must stay the newest report,
            # so the person can still accept it.
            print("\n".join(lines))
            return code
    else:
        code, lines = hand_over(repo, args.plan, args.message, args.reviews_passed, args.release_note)
    kept = build_relay.kept_reports(root, args.session, args.plan, cwd=repo) or {}
    none = NOT_REVIEWED if args.accept_open_findings else NO_REPORT
    copied = {"What each review found": [(title, kept.get(part) or none) for title, part in REVIEWS],
              "The hand-over script's report": [("Output", "\n".join(lines))]}
    name = os.path.splitext(os.path.basename(args.plan))[0]
    try:
        _, report = run_report.write("build", name, repo, root, own, copied, date=today())
        early = own.get("Built before sign-off", "").strip()
        if any(line.startswith(f"Plan: {args.plan} is now") for line in lines) or "check" not in kept or early:
            # Kept only while a check leaves findings to go through: a check after the person's
            # answers needs the reviews again (docs/adrs/0060).
            build_relay.clear(root, args.session)
    except run_report.ReportError as error:
        report = [f"Report not written: {error}"]
        code = max(code, 1)
    print("\n".join(lines + [""] + report))
    return code


if __name__ == "__main__":
    sys.exit(main())

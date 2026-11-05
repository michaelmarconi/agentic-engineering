#!/usr/bin/env python3
"""Check a project's lifecycle documents, and work out what a window of commits changed, for /audit.

/audit runs this script first, so the checks that must be exact every time never pass through a
model, and so it knows which documents to start agents on. The script reads documents with the
status hook's own parsing (scripts/status_check.py), so the hook and the audit never disagree on a
status, a section or what a plan names. It writes nothing in the project. Every command prints
JSON on stdout.

documents
    Checks every lifecycle document under docs/ as it stands, whatever its status, and lists the
    `👍 Accepted` specs and ADRs. The documents are docs/brief.md, *.spec.md files under
    docs/specs/, NNNN-*.md files under docs/adrs/, and *.md files directly in docs/plans/ and
    docs/spikes/; any other file there with no `status:` is not a lifecycle document and is left
    alone. Each problem names its document, its check and what is wrong:

    - status: the status is not one its kind of document has, written with its emoji (U+FE0F after
      the emoji is optional), or a spec, ADR, plan or spike record has none;
    - open questions: a `👍 Accepted` spec or ADR, a `🟢 Ready to build` plan or a `🟢 Ready to run`
      spike record whose Open questions section is missing or holds anything but "None.";
    - references: a document links to another lifecycle document, or names its file, where the
      lifecycle's references rule does not allow it. Plans and spike records may name specs and
      ADRs; nothing may name a plan or spike record; the brief, specs and ADRs name no other
      document, though an ADR may name another by number. The frontmatter is not read;
    - supersede: an `👍 Accepted` or `↪️ Superseded` ADR's `supersedes:` names an ADR whose
      `superseded-by:` does not name it back, a `superseded-by:` names an ADR whose `supersedes:`
      does not name this one, or a `↪️ Superseded` ADR has no `superseded-by:`. A Draft or
      Rejected ADR naming the one it would supersede is not checked;
    - ready plan: a `🟢 Ready to build` plan names a spec or ADR that is missing or not
      `👍 Accepted`, or a requirement its spec no longer has;
    - overlap: two plans that are not `✅ Built` name the same requirement of the same spec. Plans
      are read from the working tree and from every local and remote branch git already knows,
      with `git show`; nothing is fetched. A plan is known by its file name, so the same plan on
      several branches is one plan, and a plan `✅ Built` on any of them is built.

    It also lists the `✅ Built` plans, the finished spike records (`💡 Answered` or
    `❔ Not answered`) and the unfinished ones with the date their name starts with. `lifecycle`
    is false when the project has no lifecycle document at all.

window <words>
    Reads `last N days` (commits whose commit date falls in the N days before now) or
    `since <commit>` (the commits after that commit, not including it) on the checked-out branch,
    and lists the files those commits added (A), changed (M), renamed (R, with the old name) or
    deleted (D), and the `👍 Accepted` specs and ADRs whose own text changed. A merge commit counts
    as its change from its first parent, so work merged in the window counts even when its own
    commits are older. It also lists the window's commits, oldest first, with their dates and
    subjects, and writes nothing, so agents read the changed files themselves. It refuses, with
    the reason, words it can't read, a commit that doesn't exist or isn't on this branch, and a
    window older than the history the clone holds; it never falls back to every commit.

Exit codes: 0 done; 1 refused or failed, with the reason on stderr and nothing on stdout.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

# The plugin's scripts/ folder holds the status hook, whose parsing this script shares.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from status_check import (ACCEPTED, ADR_STATUSES, ANSWERED, BUILT, DRAFT, NOT_ANSWERED,  # noqa: E402
                          READY, READY_TO_RUN, SPEC_STATUSES, SPIKE_STATUSES, STATUSES, SUPERSEDED,
                          field, frontmatter, has_open_questions, lifecycle_status, listed,
                          reference_problem, requirements, status_of)
from doc_references import targets  # noqa: E402

KINDS = {"spec": SPEC_STATUSES, "ADR": ADR_STATUSES, "plan": STATUSES, "spike record": SPIKE_STATUSES}
SETTLED = {"spec": ACCEPTED, "ADR": ACCEPTED, "plan": READY, "spike record": READY_TO_RUN}
FINISHED = (ANSWERED, NOT_ANSWERED)
ADR_NAME = re.compile(r"^(\d{4})-.*\.md$", re.IGNORECASE)
DATED_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-.*\.md$", re.IGNORECASE)
LAST = re.compile(r"^\s*last\s+(\d+)\s+days?\s*$", re.IGNORECASE)
SINCE = re.compile(r"^\s*since\s+(\S+)\s*$", re.IGNORECASE)


class Refused(Exception):
    """The command can't do what was asked; the reason says why."""


def git(project, *args, check=True):
    # Files in a diff need not be UTF-8 text; a byte that isn't is shown as U+FFFD, not refused.
    done = subprocess.run(["git", "-C", project, "-c", "core.quotePath=false", *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if check and done.returncode != 0:
        raise Refused(done.stderr.strip() or f"git {args[0]} failed")
    return done


def kind_of(relative):
    """The lifecycle kind of a path relative to the project, or None."""
    parts = relative.split("/")
    lower = [part.lower() for part in parts]
    if lower == ["docs", "brief.md"]:
        return "brief"
    if len(parts) >= 3 and lower[:2] == ["docs", "specs"] and lower[-1].endswith(".spec.md"):
        return "spec"
    if len(parts) >= 3 and lower[:2] == ["docs", "adrs"] and lower[-1].endswith(".md"):
        return "ADR"
    if len(parts) == 3 and lower[:2] == ["docs", "plans"] and lower[-1].endswith(".md"):
        return "plan"
    if len(parts) == 3 and lower[:2] == ["docs", "spikes"] and lower[-1].endswith(".md"):
        return "spike record"
    return None


def named_like_a_document(kind, name):
    """Whether a file with no status is still clearly meant as a lifecycle document."""
    if kind == "spec":
        return True
    if kind == "ADR":
        return bool(ADR_NAME.match(name))
    return bool(DATED_NAME.match(name))


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def lifecycle_documents(project):
    """{relative path: (kind, text)} for every lifecycle document in the project's working tree."""
    found = {}
    docs = os.path.join(project, "docs")
    for folder, dirs, files in os.walk(docs):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            relative = os.path.relpath(os.path.join(folder, name), project).replace(os.sep, "/")
            kind = kind_of(relative)
            if kind is None:
                continue
            text = read(os.path.join(folder, name))
            if text is None:
                text = ""
            if kind != "brief" and status_of(text) is None and not named_like_a_document(kind, name):
                continue
            found[relative] = (kind, text)
    return found


def status(kind, text):
    """The document's status as the status hook reads it: a status written by its word alone, as
    documents written before the emoji were, counts as the status it names."""
    return lifecycle_status(text, KINDS[kind])


def status_problem(kind, text):
    written, statuses = status_of(text), KINDS[kind]
    if written is None:
        return f"it has no `status:`; a {kind}'s status is {listed(statuses)}"
    meant = status(kind, text)
    if meant in statuses and meant != written:
        return f"its status '{written}' is missing its emoji or has the wrong one; write `{meant}`"
    if written not in statuses:
        return f"its status '{written}' is not one a {kind} has; it is {listed(statuses)}"
    return None


def body(text):
    """The text's lines without its frontmatter."""
    lines = text.lstrip("\ufeff").splitlines()
    head = frontmatter(text)
    return lines[len(head) + 2 if head is not None else 0:]


def allowed_reference(source_kind, target_kind):
    return source_kind in ("plan", "spike record") and target_kind in ("spec", "ADR")


def reference_problems(relative, kind, text, documents, project):
    """Each other lifecycle document this one links to or names by file, against the rule."""
    if kind not in ("brief", "spec", "ADR", "plan", "spike record"):
        return []
    by_name = {}
    for other in documents:
        by_name.setdefault(other.rsplit("/", 1)[-1].lower(), []).append(other)
    folder = os.path.dirname(os.path.join(project, relative))
    named = set()
    for line in body(text):
        for target in targets(line):
            path = target.split("#", 1)[0]
            if not path or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", path):
                continue
            full = os.path.normpath(os.path.join(folder, path))
            other = os.path.relpath(full, project).replace(os.sep, "/")
            if other in documents:
                named.add(other)
        lowered = line.lower()
        for name, others in by_name.items():
            if name in lowered and re.search(rf"(?<![\w.-]){re.escape(name)}(?![\w-])", lowered):
                named.update(others)
    named.discard(relative)
    problems = []
    for other in sorted(named):
        other_kind = documents[other][0]
        if allowed_reference(kind, other_kind):
            continue
        problems.append(f"it names {other}, a {other_kind}; " + (
            "nothing may refer to a plan or a spike record" if other_kind in ("plan", "spike record")
            else "an ADR may name another ADR only by its number" if kind == "ADR" and other_kind == "ADR"
            else f"a {kind} names no other lifecycle document"))
    return problems


def numbers(value):
    return re.findall(r"\d{4}", value or "")


def supersede_problems(documents):
    adrs = {}
    for relative, (kind, text) in documents.items():
        match = ADR_NAME.match(relative.rsplit("/", 1)[-1])
        if kind == "ADR" and match:
            adrs.setdefault(match.group(1), []).append((relative, text))
    found = []
    for number, entries in sorted(adrs.items()):
        for relative, text in entries:
            current = status("ADR", text)
            if current not in (ACCEPTED, SUPERSEDED):
                continue
            for other in numbers(field(text, "supersedes")):
                targets_ = adrs.get(other)
                if not targets_:
                    found.append((relative, f"`supersedes:` names ADR {other}, which does not exist"))
                elif not any(number in numbers(field(t, "superseded-by")) for _, t in targets_):
                    found.append((relative, f"`supersedes:` names ADR {other}, whose `superseded-by:` does not name {number}"))
            by = numbers(field(text, "superseded-by"))
            if current == SUPERSEDED and not by:
                found.append((relative, f"it is `{SUPERSEDED}` but has no `superseded-by:`"))
            if current == ACCEPTED and by:
                found.append((relative, f"it names its replacement in `superseded-by:` but is still `{ACCEPTED}`; "
                                        f"set it to `{SUPERSEDED}`"))
            for other in by:
                targets_ = adrs.get(other)
                if not targets_:
                    found.append((relative, f"`superseded-by:` names ADR {other}, which does not exist"))
                elif not any(number in numbers(field(t, "supersedes")) for _, t in targets_):
                    found.append((relative, f"`superseded-by:` names ADR {other}, whose `supersedes:` does not name {number}"))
    return found


def branch_plans(project):
    """{plan file name: [(where, text)]} for plans on every branch git knows, local or remote.

    One `git ls-tree` per branch lists its plans, and one `git cat-file --batch` reads them all,
    so a repository with many branches doesn't start a process per plan per branch.
    """
    found = {}
    if git(project, "rev-parse", "--git-dir", check=False).returncode != 0:
        return found
    refs = git(project, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes").stdout.split()
    listed_plans = []
    for ref in refs:
        if ref.endswith("/HEAD"):
            continue
        listing = git(project, "ls-tree", f"{ref}:docs/plans", check=False)
        if listing.returncode != 0:
            continue
        for line in listing.stdout.splitlines():
            info, _, name = line.partition("\t")
            parts = info.split()
            if len(parts) == 3 and parts[1] == "blob" and name.lower().endswith(".md"):
                listed_plans.append((re.sub(r"^refs/(heads|remotes)/", "", ref), name, parts[2]))
    blobs = sorted({blob for _, _, blob in listed_plans})
    if not blobs:
        return found
    done = subprocess.run(["git", "-C", project, "cat-file", "--batch"], input="\n".join(blobs).encode() + b"\n",
                          capture_output=True)
    texts, out, at = {}, done.stdout, 0
    while at < len(out):
        end = out.index(b"\n", at)
        header = out[at:end].split()
        at = end + 1
        if len(header) != 3:
            continue
        size = int(header[2])
        texts[header[0].decode()] = out[at:at + size].decode("utf-8", errors="replace")
        at += size + 1
    for short, name, blob in listed_plans:
        if blob in texts:
            found.setdefault(name, []).append((f"branch {short}", texts[blob]))
    return found


def overlap_problems(project, documents):
    copies = branch_plans(project)
    for relative, (kind, text) in documents.items():
        if kind == "plan":
            copies.setdefault(relative.rsplit("/", 1)[-1], []).insert(0, ("the working tree", text))
    plans_dir = os.path.join(project, "docs", "plans")
    unbuilt = {}
    for name, versions in sorted(copies.items()):
        if any(status("plan", text) == BUILT for _, text in versions):
            continue
        wanted = {}
        for where, text in versions:
            if status("plan", text) not in (DRAFT, READY):
                continue
            for spec_path, requirement in requirements(os.path.join(plans_dir, name), text):
                wanted.setdefault((os.path.relpath(spec_path, project).replace(os.sep, "/"), requirement), where)
        unbuilt[name] = wanted
    found, names = [], sorted(unbuilt)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            for key in sorted(set(unbuilt[first]) & set(unbuilt[second])):
                spec_path, requirement = key
                found.append((f"docs/plans/{first}",
                              f"it and docs/plans/{second} ({unbuilt[second][key]}) both name Requirement: "
                              f"{requirement} of {spec_path}, and neither is `{BUILT}`"))
    return found


def check_documents(project):
    project = os.path.abspath(project)
    documents = lifecycle_documents(project)
    problems = []

    def add(document, check, detail):
        problems.append({"document": document, "check": check, "detail": detail})

    accepted = {"specs": [], "adrs": []}
    built, finished, unfinished = [], [], []
    for relative, (kind, text) in sorted(documents.items()):
        if kind != "brief":
            wrong = status_problem(kind, text)
            if wrong:
                add(relative, "status", wrong)
            current = status(kind, text)
            if current == SETTLED[kind] and has_open_questions(text):
                add(relative, "open questions",
                    f"it is `{current}` but its Open questions section is missing or not \"None.\"")
            if kind == "spec" and current == ACCEPTED:
                accepted["specs"].append(relative)
            if kind == "ADR" and current == ACCEPTED:
                accepted["adrs"].append(relative)
            if kind == "plan" and current == BUILT:
                built.append(relative)
            if kind == "plan" and current == READY:
                wrong = reference_problem(os.path.join(project, relative), text)
                if wrong:
                    add(relative, "ready plan", f"it is `{READY}` but {wrong}")
            if kind == "spike record" and current in FINISHED:
                finished.append(relative)
            if kind == "spike record" and current in (DRAFT, READY_TO_RUN):
                date = DATED_NAME.match(relative.rsplit("/", 1)[-1])
                unfinished.append({"document": relative, "status": current, "date": date.group(1) if date else None})
        for wrong in reference_problems(relative, kind, text, documents, project):
            add(relative, "references", wrong)
    for document, detail in supersede_problems(documents):
        add(document, "supersede", detail)
    for document, detail in overlap_problems(project, documents):
        add(document, "overlap", detail)
    return {
        "lifecycle": bool(documents),
        "accepted": accepted,
        "problems": problems,
        "built_plans": built,
        "finished_spikes": finished,
        "unfinished_spikes": unfinished,
    }


# ---- window ----

def commit_date(project, commit):
    return int(git(project, "log", "-1", "--format=%ct", commit).stdout.strip())


def resolve_window(project, words, now):
    """(git log arguments selecting the window's commits, description)."""
    if git(project, "rev-parse", "--git-dir", check=False).returncode != 0:
        raise Refused("this folder is not in a git repository, so no window can be read")
    if git(project, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode != 0:
        raise Refused("this branch has no commits yet")
    last, since = LAST.match(words), SINCE.match(words)
    shallow = git(project, "rev-parse", "--is-shallow-repository").stdout.strip() == "true"
    if last:
        days = int(last.group(1))
        if days < 1:
            raise Refused("a window of `last N days` needs N of 1 or more")
        cutoff = int(now.timestamp()) - days * 86400
        if shallow:
            # The clone's oldest commits are listed in .git/shallow, and history before each is missing,
            # so a window reaching back past any of them would leave out commits without saying so.
            shallow_file = os.path.join(project, git(project, "rev-parse", "--git-path", "shallow").stdout.strip())
            cut = (read(shallow_file) or "").split()
            if not cut or max(commit_date(project, c) for c in cut) >= cutoff:
                raise Refused(f"this clone's history starts after the window does ({days} days back), as in a clone "
                              "made with only recent history; fetch more history, or give a shorter window")
        return ["HEAD", f"--since=@{cutoff}"], f"the last {days} day{'s' if days != 1 else ''}"
    if since:
        commit = since.group(1)
        found = git(project, "rev-parse", "--verify", "-q", f"{commit}^{{commit}}", check=False)
        if found.returncode != 0:
            if shallow:
                raise Refused(f"no commit {commit} in this clone, which holds only recent history")
            raise Refused(f"no commit {commit} in this repository")
        full = found.stdout.strip()
        if git(project, "merge-base", "--is-ancestor", full, "HEAD", check=False).returncode != 0:
            raise Refused(f"commit {commit} is not on the checked-out branch")
        return [f"{full}..HEAD"], f"the commits after {commit}"
    raise Refused(f"can't read the window '{words}'; write `last N days` or `since <commit>`")


def changed_files(project, selection):
    """(the window's commits, oldest first, and the files they changed)."""
    out = git(project, "log", "--name-status", "-M", "--diff-merges=first-parent",
              "--format=%x00%H%x1f%cs%x1f%s", *selection).stdout
    chunks = [chunk for chunk in out.split("\x00") if chunk.strip()]
    commits, changes = [], {}
    for chunk in reversed(chunks):
        lines = chunk.splitlines()
        sha, date, subject = (lines[0].split("\x1f") + ["", ""])[:3]
        commits.append({"commit": sha[:12], "date": date, "subject": subject})
        for line in lines[1:]:
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            letter = fields[0][:1]
            if letter == "R" and len(fields) == 3:
                # A file renamed in the window is listed once, under its new name: as added if the
                # window added it, otherwise as renamed from the name it had before the window.
                before = changes.pop(fields[1], None)
                if before and before["status"] == "A":
                    changes[fields[2]] = {"status": "A", "path": fields[2]}
                else:
                    origin = before.get("from", fields[1]) if before else fields[1]
                    changes[fields[2]] = {"status": "R", "path": fields[2], "from": origin}
            elif letter in "AMDTC":
                path = fields[-1]
                changes[path] = {"status": "M" if letter in "TC" else letter, "path": path}
    return commits, [changes[path] for path in sorted(changes)]


def window(project, words, now):
    project = os.path.abspath(project)
    selection, description = resolve_window(project, words, now)
    commits, changes = changed_files(project, selection)
    documents = lifecycle_documents(project)
    touched = {change["path"] for change in changes}
    accepted = [relative for relative, (kind, text) in sorted(documents.items())
                if kind in ("spec", "ADR") and status(kind, text) == ACCEPTED and relative in touched]
    return {"window": description, "commits": commits, "changed": changes,
            "changed_accepted_documents": accepted}


def parse_now(value):
    if value is None:
        return datetime.datetime.now(datetime.timezone.utc)
    try:
        moment = datetime.datetime.fromisoformat(value)
    except ValueError:
        raise Refused(f"can't read --now '{value}'; write it as 2026-11-05T12:00:00+00:00")
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog=__doc__.split("\n\n", 1)[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    documents_parser = commands.add_parser(
        "documents", help="check every lifecycle document and list the accepted specs and ADRs",
        description="Check every lifecycle document as it stands, and list the accepted specs and ADRs. "
                    "Output: JSON with lifecycle, accepted {specs, adrs}, problems [{document, check, detail}], "
                    "built_plans, finished_spikes and unfinished_spikes [{document, status, date}]. "
                    "Exit codes: 0 done, whatever it found; 1 failed, with the reason on stderr.")
    window_parser = commands.add_parser(
        "window", help="list a window of commits and the files they changed",
        description="Read `last N days` or `since <commit>` on the checked-out branch, writing nothing.\n"
                    "Output: JSON with window, commits [{commit, date, subject}], oldest first,\n"
                    "changed [{status, path, from}] and changed_accepted_documents.\n"
                    "Exit codes: 0 done, even when the window holds no commits; 1 refused, with the\n"
                    "reason on stderr.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    window_parser.add_argument("words", nargs="+", help="`last N days` or `since <commit>`")
    window_parser.add_argument("--now", help="the time the window ends, in ISO 8601; for tests (default: now)")
    for sub in (documents_parser, window_parser):
        sub.add_argument("--project", default=".", help="the project's folder (default: the current folder)")
    args = parser.parse_args(argv)
    try:
        if args.command == "documents":
            out = check_documents(args.project)
        else:
            out = window(args.project, " ".join(args.words), parse_now(args.now))
    except Refused as error:
        print(f"audit {args.command}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

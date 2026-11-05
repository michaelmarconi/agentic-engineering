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

window <words> --data <folder>
    Reads `last N days` (commits whose commit date falls in the N days before now) or
    `since <commit>` (the commits after that commit, not including it) on the checked-out branch,
    and lists the files those commits added (A), changed (M), renamed (R, with the old name) or
    deleted (D), and the `👍 Accepted` specs and ADRs whose own text changed. A merge commit counts
    as its change from its first parent, so work merged in the window counts even when its own
    commits are older. It writes the window's changes, as `git log -p`, to a diff file in a
    folder for this project and this run, <data>/audits/<hash of the project path>-<run>/, or,
    when the data folder can't be written, in a folder only this user can open in the system's
    temporary folder, sdlc-audits-<user id>/; and it first deletes any folder an earlier run of
    the same project left in either place. It refuses, with the reason, words it can't read, a
    commit that doesn't exist or isn't on this branch, and a window older than the history the
    clone holds; it never falls back to every commit.

clean --data <folder>
    Deletes every folder `window` left for this project, in either place. Other projects' folders
    are never touched.

Exit codes: 0 done; 1 refused or failed, with the reason on stderr and nothing on stdout.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The plugin's scripts/ folder holds the status hook, whose parsing this script shares.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from status_check import (ACCEPTED, ADR_STATUSES, ANSWERED, BUILT, DRAFT, NOT_ANSWERED,  # noqa: E402
                          READY, READY_TO_RUN, SPEC_STATUSES, SPIKE_STATUSES, STATUSES, SUPERSEDED,
                          VARIATION, field, frontmatter, has_open_questions, reference_problem,
                          requirements, status_of)
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


def plain(status):
    return (status or "").replace(VARIATION, "")


def git(project, *args, check=True):
    done = subprocess.run(["git", "-C", project, *args], capture_output=True, text=True)
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


def listed(values):
    named = [f"`{value}`" for value in values]
    return ", ".join(named[:-1]) + " or " + named[-1]


def status_problem(kind, text):
    status = status_of(text)
    statuses = KINDS[kind]
    if status is None:
        return f"it has no `status:`; a {kind}'s status is {listed(statuses)}"
    if status not in statuses:
        return f"its status '{status}' is not one a {kind} has; it is {listed(statuses)}"
    return None


def body(text):
    """The text without its frontmatter, as (first line number, lines)."""
    lines = text.lstrip("﻿").splitlines()
    head = frontmatter(text)
    start = len(head) + 2 if head is not None else 0
    return start + 1, lines[start:]


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
    first, lines = body(text)
    for line in lines:
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
            status = status_of(text)
            if plain(status) not in (plain(ACCEPTED), plain(SUPERSEDED)):
                continue
            for other in numbers(field(text, "supersedes")):
                targets_ = adrs.get(other)
                if not targets_:
                    found.append((relative, f"`supersedes:` names ADR {other}, which does not exist"))
                elif not any(number in numbers(field(t, "superseded-by")) for _, t in targets_):
                    found.append((relative, f"`supersedes:` names ADR {other}, whose `superseded-by:` does not name {number}"))
            by = numbers(field(text, "superseded-by"))
            if plain(status) == plain(SUPERSEDED) and not by:
                found.append((relative, f"it is `{SUPERSEDED}` but has no `superseded-by:`"))
            for other in by:
                targets_ = adrs.get(other)
                if not targets_:
                    found.append((relative, f"`superseded-by:` names ADR {other}, which does not exist"))
                elif not any(number in numbers(field(t, "supersedes")) for _, t in targets_):
                    found.append((relative, f"`superseded-by:` names ADR {other}, whose `supersedes:` does not name {number}"))
    return found


def branch_plans(project):
    """{plan file name: [(where, text)]} for plans on every branch git knows, local or remote."""
    found = {}
    if git(project, "rev-parse", "--git-dir", check=False).returncode != 0:
        return found
    refs = git(project, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes").stdout.split()
    for ref in refs:
        if ref.endswith("/HEAD"):
            continue
        short = re.sub(r"^refs/(heads|remotes)/", "", ref)
        listing = git(project, "ls-tree", "--name-only", f"{ref}:docs/plans", check=False)
        if listing.returncode != 0:
            continue
        for name in listing.stdout.splitlines():
            if not name.lower().endswith(".md"):
                continue
            shown = git(project, "show", f"{ref}:docs/plans/{name}", check=False)
            if shown.returncode == 0:
                found.setdefault(name, []).append((f"branch {short}", shown.stdout))
    return found


def overlap_problems(project, documents):
    copies = branch_plans(project)
    for relative, (kind, text) in documents.items():
        if kind == "plan":
            copies.setdefault(relative.rsplit("/", 1)[-1], []).insert(0, ("the working tree", text))
    plans_dir = os.path.join(project, "docs", "plans")
    unbuilt = {}
    for name, versions in sorted(copies.items()):
        if any(status_of(text) == BUILT for _, text in versions):
            continue
        wanted = {}
        for where, text in versions:
            if status_of(text) not in (DRAFT, READY):
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
            status = status_of(text)
            if status == SETTLED[kind] and has_open_questions(text):
                add(relative, "open questions",
                    f"it is `{status}` but its Open questions section is missing or not \"None.\"")
            if kind == "spec" and status == ACCEPTED:
                accepted["specs"].append(relative)
            if kind == "ADR" and status == ACCEPTED:
                accepted["adrs"].append(relative)
            if kind == "plan" and status == BUILT:
                built.append(relative)
            if kind == "plan" and status == READY:
                wrong = reference_problem(os.path.join(project, relative), text)
                if wrong:
                    add(relative, "ready plan", f"it is `{READY}` but {wrong}")
            if kind == "spike record" and status in FINISHED:
                finished.append(relative)
            if kind == "spike record" and status in (DRAFT, READY_TO_RUN):
                date = DATED_NAME.match(relative.rsplit("/", 1)[-1])
                unfinished.append({"document": relative, "status": status, "date": date.group(1) if date else None})
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
    documents_parser.add_argument("--project", default=".", help="the project's folder (default: the current folder)")
    args = parser.parse_args(argv)
    try:
        out = check_documents(args.project)
    except Refused as error:
        print(f"audit {args.command}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

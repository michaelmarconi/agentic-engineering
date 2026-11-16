"""Write the report file a build, an audit or a verify run ends with (ADRs 0033 and 0034).

`hand_over.py`, `audit.py report` and `verify.py report` use this module; it has no command of its own. A report is
one Markdown file with one `##` heading per item the skill lists, in that order. Claude's own
sections arrive as Markdown under those headings, and the reports of scripts and agents arrive as
text that goes into the file word for word, as `###` subsections under the heading they belong to.
A heading only a script fills cannot come from Claude, so Claude cannot write its own version of a
copied report.

The file goes in <data>/reports/<repository>/<date>-<kind>-<name>.md, where <data> is the plugin's
data folder. When that folder is empty or can't be written, as in the plugin's own test runs, the
file goes in `agentic-reports-<user id>` in the system's temporary folder instead, which only this
user can open, and the lines printed for Claude say so. A second report of the same name on the
same day gets `-2`, `-3` and so on: no report is ever overwritten, and none is deleted.

The lines printed for Claude give the file's path first, then the headings, each copied report's
length, and the file as written, between fixed `===` lines, so the run's own record shows exactly
what the person will read.

`reports` finds a plan's earlier reports, newest first, and `section` and `subsection` read one back,
so hand_over.py can find a build's failed correction check (docs/adrs/0038). It reads the data
folder's reports, and the private folder's only when the data folder has none and the private
folder is one only this user can open.
"""

import os
import re
import tempfile

HEADINGS = {
    "build": [
        "What was built",
        "Built before sign-off",
        "Tests and lint",
        "Choices",
        "Defects corrected",
        "What each review found",
        "The hand-over script's report",
        "Left for you to check",
    ],
    "audit": [
        "Documents checked",
        "Documents not checked",
        "Drift",
        "Contradicts the brief",
        "Problems with the documents",
        "Not built yet",
        "ADR checks that need a run",
        "Documents to consider deleting",
        "Unfinished spike records",
        "Rejected findings",
    ],
    "verify": [
        "Commit checked",
        "Overall result",
        "Failed",
        "Disputed",
        "Not checked",
        "Passed",
        "What each agent reported",
        "The repository after the run",
    ],
}
# Headings only a script fills: Claude's text under one is refused.
COPIED_ONLY = {
    "build": {"The hand-over script's report"},
    "audit": set(),
    "verify": {"Commit checked", "What each agent reported", "The repository after the run"},
}
NOTHING = "Nothing to report."
HEADING = re.compile(r"^## (?P<title>.+?)[ \t]*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")  # a fenced block's first or last line


class ReportError(Exception):
    """The report can't be written as asked; the message says why."""


def safe(name):
    """`name` with every run of characters not safe in a file name made one hyphen."""
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    name = re.sub(r"\.{2,}", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-.")
    return name or "report"


def writable(folder):
    try:
        os.makedirs(folder, exist_ok=True)
        os.rmdir(tempfile.mkdtemp(dir=folder))
        return True
    except OSError:
        return False


def fallback_root():
    """The folder used when the data folder can't be written: only this user can open it, so other
    users can neither read a report nor put anything in its place."""
    return os.path.join(tempfile.gettempdir(), f"agentic-reports-{os.getuid()}")


def private(root):
    try:
        os.makedirs(root, mode=0o700, exist_ok=True)
    except OSError as error:
        raise ReportError(f"neither the plugin's data folder nor {root} can be written ({error})")
    if not trusted(root):
        raise ReportError(f"{root} is not a folder only you can open; delete it and run again")
    return root


def report_folder(data, repository):
    """The folder for this repository's reports, and whether it is the fallback."""
    name = safe(os.path.basename(os.path.normpath(repository)))
    if data:
        folder = os.path.join(os.path.abspath(data), "reports", name)
        if writable(folder):
            return folder, False
    folder = os.path.join(private(fallback_root()), name)
    if not writable(folder):
        raise ReportError(f"{folder} can't be written")
    return folder, True


def trusted(root):
    """Whether `root` is a real folder that only this user can open, so a report in it was not put
    there by someone else."""
    try:
        info = os.lstat(root)
    except OSError:
        return False
    return os.path.isdir(root) and not os.path.islink(root) and info.st_uid == os.getuid() \
        and not info.st_mode & 0o077


def reports(kind, name, repository, data):
    """The paths of the reports of this kind and name for the repository, newest first: by date,
    then by the number added when several share a date. Looks in the data folder, and only when it
    holds none, in the private fallback folder."""
    folder = safe(os.path.basename(os.path.normpath(repository)))
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})-" + re.escape(f"{kind}-{safe(name)}") + r"(?:-(\d+))?\.md$")
    places = [os.path.join(os.path.abspath(data), "reports", folder)] if data else []
    if trusted(fallback_root()):
        places.append(os.path.join(fallback_root(), folder))
    for place in places:
        try:
            names = os.listdir(place)
        except OSError:
            continue
        found = [(m.group(1), int(m.group(2) or 1), n) for n in names for m in [pattern.match(n)] if m]
        if found:
            return [os.path.join(place, n) for _, _, n in sorted(found, reverse=True)]
    return []


def heading_at(text, line, start=0):
    """Where `line` next starts a line of `text`, at or after `start`; -1 when it doesn't."""
    at = start
    while True:
        at = text.find(line, at)
        if at <= 0 or text[at - 1] == "\n":
            return at
        at += 1


def section(kind, text, heading):
    """The text under `## <heading>` in a report as written, up to the next heading the kind lists;
    None when the heading is missing. The headings are found in their written order, each after
    the one before it, so a heading quoted inside an earlier section is passed over."""
    at, bounds = 0, {}
    for title in HEADINGS[kind]:
        found = heading_at(text, f"## {title}\n\n", at)
        if found < 0:
            continue
        bounds[title] = found
        at = found + len(f"## {title}\n\n")
    if heading not in bounds:
        return None
    start = bounds[heading] + len(f"## {heading}\n\n")
    ends = [i for t, i in bounds.items() if i > bounds[heading]]
    return text[start:min(ends) if ends else len(text)].strip("\n")


def subsection(body, title, after=None):
    """The copied report under the first `### <title>` in a section's text, to the section's end
    (copied reports are written last, in order), looking only past the first `### <after>` when
    given; None when there is none."""
    start = 0
    if after:
        start = heading_at(body, f"### {after}\n\n")
        if start < 0:
            return None
    at = heading_at(body, f"### {title}\n\n", start)
    if at < 0:
        return None
    return body[at + len(f"### {title}\n\n"):].strip("\n")


def parse(kind, text):
    """Claude's sections, {heading: text}, from Markdown under `## <heading>` lines.

    Raises ReportError for text before the first heading, a heading the kind doesn't list, a
    heading only a script fills, or a heading given twice."""
    sections, current, lines = {}, None, []

    def close():
        if current is not None:
            sections[current] = "\n".join(lines).strip("\n")

    fence = None
    for line in text.splitlines():
        opening = FENCE.match(line)
        if opening and (fence is None or opening.group(1).startswith(fence)):
            fence = opening.group(1)[:3] if fence is None else None
        match = HEADING.match(line) if fence is None and not opening else None
        if not match:
            if current is None and line.strip():
                raise ReportError(f"text before the first heading: {line.strip()[:60]!r}")
            lines.append(line)
            continue
        close()
        title = match.group("title")
        if title not in HEADINGS[kind]:
            raise ReportError(f"unknown heading {title!r}; the headings are: " + "; ".join(HEADINGS[kind]))
        if title in COPIED_ONLY[kind]:
            raise ReportError(f"{title!r} is filled by the script, not written by you")
        if title in sections:
            raise ReportError(f"heading {title!r} given twice")
        current, lines = title, []
    close()
    return sections


def render(kind, own, copied):
    parts = []
    for heading in HEADINGS[kind]:
        body = []
        if own.get(heading, "").strip():
            body.append(own[heading].strip("\n") + "\n")
        for title, text in copied.get(heading, []):
            body.append(f"### {title}\n\n{text}" + ("" if text.endswith("\n") else "\n"))
        parts.append(f"## {heading}\n\n" + ("\n".join(body) if body else NOTHING + "\n"))
    return "\n".join(parts)


def write(kind, name, repository, data, own, copied, date):
    """Write the report and return (path, the lines to print for Claude).

    `own` is Claude's {heading: text}; `copied` is {heading: [(title, text), ...]}, each text
    written word for word."""
    unknown = [h for h in copied if h not in HEADINGS[kind]]
    if unknown:
        raise ReportError(f"unknown heading {unknown[0]!r}")
    folder, fell_back = report_folder(data, repository)
    base = f"{date}-{kind}-{safe(name)}"
    text = render(kind, own, copied)
    number = 1
    while True:
        path = os.path.join(folder, base + (f"-{number}" if number > 1 else "") + ".md")
        try:
            with open(path, "x", encoding="utf-8") as f:
                f.write(text)
            break
        except FileExistsError:
            number += 1
        except OSError as error:
            raise ReportError(f"{path} can't be written: {error.strerror or error}")
    lines = [f"Report written: {path}"]
    if fell_back:
        lines.append("The plugin's data folder could not be written, so the report is in a folder only you can open.")
    lines.append("Headings: " + "; ".join(HEADINGS[kind]))
    for heading in HEADINGS[kind]:
        for title, body in copied.get(heading, []):
            lines.append(f"Copied: {title} ({len(body)} characters)")
    lines += ["", "=== THE REPORT AS WRITTEN ===", text.rstrip("\n"), "=== END OF THE REPORT ==="]
    return path, lines

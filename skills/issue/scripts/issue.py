#!/usr/bin/env python3
"""Gather context for, and file, an issue against the sdlc plugin's own repository.

The repository is read from the `repository` field of the plugin's
`.claude-plugin/plugin.json`, found by walking up from this script, and each kind's label from
the `labels` of its template in `.github/ISSUE_TEMPLATE/`.

Commands:
  account   Say whether `file` would use gh, and as which github.com account.
  context   Print the Context lines for an issue: plugin version, Claude Code version, OS.
  file      File an issue whose draft (title line, then body) is read from standard input.
            Uses the GitHub CLI (`gh`) when it is installed and signed in to github.com;
            otherwise prints a link that opens GitHub's new-issue page already filled in.

Run `issue.py <command> --help` for each command's arguments, output and exit codes.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from urllib.parse import urlencode

KINDS = ("bug", "improvement")

# GitHub answers 414 URI Too Long somewhere above this; it does not publish the limit.
MAX_URL = 8000
# GitHub's documented limit on an issue body.
MAX_BODY = 65536


def run(args, input=None):
    return subprocess.run(args, input=input, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=60)


def plugin_root():
    path = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(path, ".claude-plugin", "plugin.json")):
        parent = os.path.dirname(path)
        if parent == path:
            raise FileNotFoundError("no .claude-plugin/plugin.json above " + __file__)
        path = parent
    return path


def read_manifest(root):
    with open(os.path.join(root, ".claude-plugin", "plugin.json")) as f:
        return json.load(f)


def template_labels(root, kind):
    """Return the labels set in the frontmatter of the kind's template in .github/ISSUE_TEMPLATE/."""
    path = os.path.join(root, ".github", "ISSUE_TEMPLATE", kind + ".md")
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    if not lines or lines[0].strip() != "---" or "---" not in [l.strip() for l in lines[1:]]:
        raise ValueError("the %s template has no frontmatter" % kind)
    frontmatter = lines[1:1 + [l.strip() for l in lines[1:]].index("---")]
    labels = []
    for i, line in enumerate(frontmatter):
        if line.startswith("labels:"):
            value = line[len("labels:"):].split(" #")[0].strip()
            if value:
                labels = value.strip("[]").split(",")
            else:
                for item in frontmatter[i + 1:]:
                    if not item.lstrip().startswith("- "):
                        break
                    labels.append(item.lstrip()[2:])
    labels = [label.split(" #")[0].strip().strip("'\"") for label in labels]
    labels = [label for label in labels if label]
    if not labels:
        raise ValueError("the %s template sets no label" % kind)
    return labels


def repo_slug(repository):
    """Return owner/name for a GitHub repository URL, string or {"url": ...} form."""
    url = repository.get("url", "") if isinstance(repository, dict) else repository or ""
    match = re.match(r"^(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise ValueError("plugin.json repository is not a GitHub repository: %r" % url)
    return match.group(1) + "/" + match.group(2)


def new_issue_link(slug, title, body, labels):
    query = urlencode({"title": title, "body": body, "labels": ",".join(labels)})
    return "https://github.com/%s/issues/new?%s" % (slug, query)


def claude_version():
    try:
        result = run(["claude", "--version"])
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def os_name():
    """Name the OS by product and version, never the kernel build, which can identify a host."""
    system = platform.system()
    if system == "Darwin":
        return ("macOS " + platform.mac_ver()[0]).strip()
    if system == "Linux":
        # ID and VERSION_ID, not PRETTY_NAME, which organisations rename after themselves.
        try:
            release = platform.freedesktop_os_release()
        except (OSError, AttributeError):
            return "Linux"
        return " ".join(["Linux", release.get("ID", ""), release.get("VERSION_ID", "")]).strip()
    if system == "Windows":
        # Windows 11 reports release "10" before Python 3.12; its builds start at 22000.
        build = platform.version().split(".")[-1]
        return "Windows 11" if build.isdigit() and int(build) >= 22000 else "Windows " + platform.release()
    return system or "unknown"


def context(root):
    manifest = read_manifest(root)
    return "\n".join([
        "- Plugin: %s %s" % (manifest.get("name", "sdlc"), manifest.get("version", "unknown")),
        "- Claude Code: " + claude_version(),
        "- OS: " + os_name(),
    ]) + "\n"


class Unsure(Exception):
    """gh may have filed the issue, so offering a link could file it twice."""


def gh_filed(slug, title, body, labels):
    """File with gh. Return the issue URL, or None if gh can't try; raise Unsure if it tried.

    Only a failure before the issue is sent, such as gh missing or signed out of github.com,
    is safe to follow with a link: once `gh issue create` has run, it may have filed the issue
    even when it reports an error.
    """
    if not shutil.which("gh"):
        return None
    try:
        status = run(["gh", "auth", "status", "--hostname", "github.com"])
    except (OSError, subprocess.SubprocessError):
        return None
    if status.returncode != 0:
        print("issue.py: gh is not signed in to github.com", file=sys.stderr)
        return None
    args = ["gh", "issue", "create", "--repo", "github.com/" + slug, "--title", title,
            "--label", ",".join(labels), "--body-file", "-"]
    try:
        result = run(args, input=body)
    except OSError:
        return None
    except subprocess.TimeoutExpired:
        raise Unsure("gh timed out")
    if result.returncode != 0:
        raise Unsure("gh failed: " + result.stderr.strip())
    urls = [line for line in result.stdout.split() if line.startswith("https://")]
    if not urls:
        raise Unsure("gh succeeded but printed no issue URL")
    return urls[-1]


def parse_draft(text):
    """Split a draft into its title (the first line) and body (the rest).

    The first line must be the bare title. A line that looks like a heading or a label, such as
    "# T", "Title: T" or "**Title:** T", gives an empty title rather than a guess, because the
    title is filed publicly as written.
    """
    lines = text.lstrip("\ufeff").replace("\r\n", "\n").split("\n")
    title, body = lines[0].strip(), "\n".join(lines[1:]).strip("\n")
    if re.match(r"(#+\s|\*\*|title\s*:|kind\s*:)", title, re.IGNORECASE):
        title = ""
    return title, body + "\n"


def account():
    """Return the github.com login gh would file as, or None if gh can't file."""
    if not shutil.which("gh"):
        return None
    try:
        if run(["gh", "auth", "status", "--hostname", "github.com"]).returncode != 0:
            return None
        result = run(["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"])
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def file_issue(root, kind, draft, link_only=False):
    title, body = parse_draft(draft)
    if not title or not body.strip():
        print("issue.py: the draft needs the bare title on its first line, then a body",
              file=sys.stderr)
        return 2
    if len(body) > MAX_BODY:
        print("issue.py: the body is longer than GitHub allows (%d characters, limit %d)"
              % (len(body), MAX_BODY), file=sys.stderr)
        return 3
    slug = repo_slug(read_manifest(root).get("repository"))
    labels = template_labels(root, kind)
    if not link_only:
        try:
            url = gh_filed(slug, title, body, labels)
        except Unsure as reason:
            print("issue.py: %s; check https://github.com/%s/issues before filing again"
                  % (reason, slug), file=sys.stderr)
            return 4
        if url:
            print("filed " + url)
            return 0
    link = new_issue_link(slug, title, body, labels)
    if len(link) > MAX_URL:
        print("issue.py: the issue is too long to fit in a link (%d characters, limit %d); "
              "shorten the body" % (len(link), MAX_URL), file=sys.stderr)
        return 3
    print("link " + link)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "account",
        help="say how `file` would file the issue",
        description="Print \"gh <login>\" if `file` would file with gh as that github.com "
                    "account, or \"link\" if it would give a link to submit in the browser. "
                    "Exit code 0.",
    )
    commands.add_parser(
        "context",
        help="print the Context lines for an issue",
        description="Print Markdown list lines naming the plugin version, the Claude Code "
                    "version (\"unknown\" if `claude` can't be run) and the OS by name and "
                    "version. Exit codes: 0 done, 1 the plugin manifest can't be read.",
    )
    filer = commands.add_parser(
        "file",
        help="file an issue, draft on standard input",
        description="File an issue on the plugin's repository. Standard input holds the draft: "
                    "the title on the first line, then the body. Prints one line: "
                    "\"filed <issue URL>\" if gh filed it, or \"link <URL>\" for the person to "
                    "open and submit; gh's error, if it failed, goes to standard error. Exit "
                    "codes: 0 done; 1 the plugin's manifest or issue templates can't be read, or name "
                    "no GitHub repository or label; 2 bad arguments, a draft whose first line "
                    "isn't a bare title or with no body, or a draft that isn't UTF-8; 3 too "
                    "long: the body is over GitHub's 65,536 characters, or gh wasn't used "
                    "(missing, signed out or --link-only) and the issue is too long for a link; 4 gh ran but its result is "
                    "unknown (it failed, timed out or printed no URL) and it may have filed the "
                    "issue, so check the repository's issues before trying again.",
    )
    filer.add_argument("--kind", required=True, choices=KINDS,
                       help="bug or improvement; the labels are those that kind's template sets")
    filer.add_argument("--link-only", action="store_true",
                       help="never run gh; always print the link")
    args = parser.parse_args(argv)
    try:
        root = plugin_root()
        if args.command == "context":
            sys.stdout.write(context(root))
            return 0
        if args.command == "account":
            login = account()
            print("gh " + login if login else "link")
            return 0
        try:
            draft = sys.stdin.buffer.read().decode("utf-8")
        except UnicodeDecodeError:
            print("issue.py: the draft is not UTF-8 text", file=sys.stderr)
            return 2
        return file_issue(root, args.kind, draft, args.link_only)
    except (OSError, ValueError) as error:
        print("issue.py: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

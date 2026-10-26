#!/usr/bin/env python3
"""Gather context for, and file, an issue against the sdlc plugin's own repository.

The repository is read from the `repository` field of the plugin's
`.claude-plugin/plugin.json`, found by walking up from this script, and each kind's label from
the `labels` of its template in `.github/ISSUE_TEMPLATE/`.

Commands:
  account   Say whether `file` would use gh, and as which github.com account.
  context   Print the Context lines for an issue: plugin version, Claude Code version, OS.
  file      File an issue whose draft (title line, then body) is read from standard input,
            with the GitHub CLI (`gh`) as the account `account` named, or print a link that
            opens GitHub's new-issue page already filled in.

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

# Linux distributions named in Context; any other ID may be an organisation's own build.
DISTRIBUTIONS = {"alpine", "amzn", "arch", "centos", "debian", "fedora", "linuxmint", "nixos",
                 "opensuse-leap", "opensuse-tumbleweed", "pop", "rhel", "rocky", "almalinux",
                 "ubuntu"}

# GitHub answers 414 URI Too Long somewhere above this; it does not publish the limit.
MAX_URL = 8000
# GitHub's limits on an issue's title and body.
MAX_TITLE = 256
MAX_BODY = 65536


def run(args, input=None, timeout=60):
    return subprocess.run(args, input=input, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def plugin_root():
    path = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(path, ".claude-plugin", "plugin.json")):
        parent = os.path.dirname(path)
        if parent == path:
            raise FileNotFoundError("no .claude-plugin/plugin.json above " + __file__)
        path = parent
    return path


def read_manifest(root):
    with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)


def template_labels(root, kind):
    """Return the labels on the `labels:` line of the kind's template in .github/ISSUE_TEMPLATE/."""
    path = os.path.join(root, ".github", "ISSUE_TEMPLATE", kind + ".md")
    with open(path, encoding="utf-8-sig") as f:
        text = f.read().replace("\r\n", "\n")
    match = re.match(r"---\n(.*?)\n---(\n|$)", text, re.DOTALL)
    line = re.search(r"^labels:(.*)$", match.group(1), re.MULTILINE) if match else None
    value = line.group(1).split(" #")[0] if line else ""
    labels = [label.strip(" '\"") for label in value.strip(" []").split(",")]
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
        result = run(["claude", "--version"], timeout=5)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def os_name():
    """Name the OS by product and version, never the kernel build, which can identify a host."""
    system = platform.system()
    if system == "Darwin":
        return ("macOS " + platform.mac_ver()[0]).strip()
    if system == "Linux":
        # Only a well-known distribution's ID and version: organisations rebrand the rest.
        try:
            release = platform.freedesktop_os_release()
        except (OSError, AttributeError):
            return "Linux"
        if release.get("ID") not in DISTRIBUTIONS:
            return "Linux"
        return " ".join(["Linux", release["ID"], release.get("VERSION_ID", "")]).strip()
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


class Refused(Exception):
    """GitHub refused the issue, or gh couldn't send it: nothing was filed."""


def gh_filed(slug, title, body, labels):
    """File through GitHub's REST API with gh and return the issue's URL.

    GitHub drops the labels of anyone not allowed to set them. Raise Refused when nothing was
    filed, and Unsure when the issue may have been filed despite the error.
    """
    args = ["gh", "api", "--hostname", "github.com", "--method", "POST",
            "repos/%s/issues" % slug, "--input", "-", "--jq", ".html_url"]
    payload = json.dumps({"title": title, "body": body, "labels": labels})
    try:
        result = run(args, input=payload)
    except (OSError, ValueError) as error:
        raise Refused("gh could not start: %s" % error)
    except subprocess.TimeoutExpired:
        raise Unsure("gh timed out")
    if result.returncode != 0:
        # A refused request, such as one without permission, gets HTTP 4xx and creates nothing.
        if re.search(r"\(HTTP 4\d\d\)", result.stderr):
            raise Refused("GitHub refused the issue: " + result.stderr.strip())
        raise Unsure("gh failed: " + result.stderr.strip())
    url = result.stdout.strip()
    if not url.startswith("https://"):
        raise Unsure("gh succeeded but printed no issue URL")
    return url


def parse_draft(text):
    """Split a draft into its title (the first line) and body (the rest).

    The first line must be the bare title. A line that starts with Markdown or a label, such as
    "# T", "Title: T" or "**Title:** T", gives an empty title rather than a guess, because the
    title is filed publicly as written.
    """
    lines = text.lstrip("\ufeff").replace("\r\n", "\n").split("\n")
    title, body = lines[0].strip(), "\n".join(lines[1:]).strip("\n")
    if re.match(r"(#+\s|>\s|\*\*\w+\s*:|\*\w+\s*:\*|\[\w+\]|"
                r"(title|subject|kind|issue|bug|improvement)\s*:)", title, re.IGNORECASE):
        title = ""
    return title, body + "\n"


def gh_login():
    """Return the github.com login gh would file as, or None if gh can't file."""
    if not shutil.which("gh"):
        return None
    try:
        result = run(["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"])
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def file_issue(root, kind, draft, login=None):
    """File the draft with gh as `login`, or print a link when login is None."""
    title, body = parse_draft(draft)
    if not title or not body.strip():
        print("issue.py: the draft needs the bare title on its first line, then a body",
              file=sys.stderr)
        return 2
    if len(title) > MAX_TITLE or len(body.rstrip("\n")) > MAX_BODY:
        print("issue.py: longer than GitHub allows (title %d characters, limit %d; body %d, "
              "limit %d)" % (len(title), MAX_TITLE, len(body), MAX_BODY), file=sys.stderr)
        return 3
    slug = repo_slug(read_manifest(root).get("repository"))
    labels = template_labels(root, kind)
    if login is not None:
        current = gh_login()
        if not current:
            print("issue.py: gh couldn't confirm its github.com account (signed out or "
                  "unreachable); nothing was filed", file=sys.stderr)
            return 5
        if current.lower() != login.lower():
            print("issue.py: gh would file as %s, not %s; tell the person before filing"
                  % (current, login), file=sys.stderr)
            return 2
        try:
            url = gh_filed(slug, title, body, labels)
        except Refused as reason:
            print("issue.py: %s; nothing was filed" % reason, file=sys.stderr)
            return 5
        except Unsure as reason:
            print("issue.py: %s; check https://github.com/%s/issues before filing again"
                  % (reason, slug), file=sys.stderr)
            return 4
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
        description="Print \"gh <login>\" if gh can file as that github.com account, or "
                    "\"link\" if the person must submit through a link in their browser. "
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
                    "the title on the first line, then the body. With --as, files it with gh "
                    "and prints \"filed <issue URL>\"; with --link-only, prints \"link <URL>\" "
                    "for the person to open and submit. Exit codes: 0 done; 1 the plugin's "
                    "manifest or issue templates can't be read, or name no GitHub repository or "
                    "label; 2 bad arguments, gh signed in as another account than --as, a draft "
                    "whose first line isn't a bare title or with no body, or a draft that isn't "
                    "UTF-8; 3 too long: over GitHub's 256-character title or 65,536-character "
                    "body, or too long for a link; 4 gh's result is unknown (it failed without "
                    "GitHub refusing, timed out or printed no URL) and it may have filed the "
                    "issue, so check the repository's issues before trying again; 5 nothing was "
                    "filed: gh couldn't confirm its account or start, or GitHub refused it.",
    )
    filer.add_argument("--kind", required=True, choices=KINDS,
                       help="bug or improvement; the labels are those that kind's template sets")
    route = filer.add_mutually_exclusive_group(required=True)
    route.add_argument("--as", dest="login", metavar="LOGIN",
                       help="file with gh as this github.com account, the one `account` named; "
                            "if gh is signed in as another account, exit 2 without filing")
    route.add_argument("--link-only", action="store_true",
                       help="never run gh; always print the link")
    args = parser.parse_args(argv)
    if args.command == "account":
        login = gh_login()
        print("gh " + login if login else "link")
        return 0
    if args.command == "file" and args.login is not None and not args.login.strip():
        parser.error("--as needs a GitHub login")
    try:
        root = plugin_root()
        if args.command == "context":
            sys.stdout.write(context(root))
            return 0
        try:
            draft = sys.stdin.buffer.read().decode("utf-8")
        except UnicodeDecodeError:
            print("issue.py: the draft is not UTF-8 text", file=sys.stderr)
            return 2
        return file_issue(root, args.kind, draft, args.login)
    except (OSError, ValueError) as error:
        print("issue.py: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

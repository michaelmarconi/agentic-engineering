#!/usr/bin/env python3
"""Hand a build's branch over: commit it, mark the plan Built if the reviews passed, and push.

`/build` runs this however the build ends. It:

1. refuses to run on the repository's default branch (the branch `origin/HEAD` names, or `main`
   or `master` when there is none) or with no branch checked out;
2. commits everything not yet committed, with the message given;
3. with --reviews-passed, sets the plan's status from `🟢 Ready to build` to `✅ Built`, changing
   nothing else in the file, and commits that on its own. It writes the file itself, so the
   status hook, which refuses `✅ Built` from Claude, never sees it;
4. pushes the branch to the remote named `origin`, if there is one.

It prints what happened, one line per step, for Claude to pass on word for word.

Exit codes: 0 when every step that applied succeeded; 1 when a commit or push failed, or
--reviews-passed was given for a plan that is not `🟢 Ready to build` (the plan is then left as it
is, and the rest still runs); 2 when it refused to start, changing nothing.
"""

import argparse
import os
import re
import subprocess
import sys

READY, BUILT = "🟢 Ready to build", "✅ Built"
STATUS_LINE = re.compile(r"^status:[ \t]*(?P<value>[^\n#]*?)[ \t]*$", re.M)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def current_branch(repo):
    result = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else None


def default_branch(repo):
    result = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if result.returncode == 0 and result.stdout.strip():
        return {result.stdout.strip().split("/", 1)[-1]}
    return {"main", "master"}


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
    # A plan written before the emoji holds the status by its words alone.
    words = re.sub(r"^[^\x00-\x7f]+ ?", "", value).replace("️", "")
    return words == "Ready to build"


def commit(repo, message, lines):
    git(repo, "add", "-A")
    if git(repo, "diff", "--cached", "--quiet").returncode == 0:
        return None
    result = git(repo, "commit", "-q", "-m", message)
    if result.returncode != 0:
        lines.append(f"Commit failed: {(result.stderr or result.stdout).strip()}")
        return False
    sha = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    lines.append(f"Committed {sha}: {message}")
    return True


def hand_over(repo, plan, message, reviews_passed):
    lines = []
    branch = current_branch(repo)
    if branch is None:
        return 2, ["Refused: no branch is checked out, so there is nothing to hand over. Nothing was changed."]
    if branch in default_branch(repo):
        return 2, [f"Refused: `{branch}` is the default branch, and a build never commits there. "
                   "Nothing was changed."]
    plan_path = os.path.join(repo, plan)
    if not os.path.isfile(plan_path):
        return 2, [f"Refused: the plan {plan} does not exist. Nothing was changed."]

    code = 0
    lines.append(f"Branch: {branch}")
    done = commit(repo, message, lines)
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
                f.write(text[:match.start("value")] + BUILT + text[match.end("value"):])
            if commit(repo, f"Mark the plan {os.path.basename(plan)} as built", lines):
                lines.append(f"Plan: {plan} is now `{BUILT}`.")
            else:
                code = 1
        else:
            lines.append(f"Plan: {plan} is `{status}`, not `{READY}`, so it was not marked `{BUILT}`.")
            code = 1
    else:
        reason = "the reviews have not all passed" if not reviews_passed else "a commit failed"
        lines.append(f"Plan: {plan} stays `{status}`, because {reason}.")

    if not has_origin(repo):
        lines.append("Push: there is no remote named origin, so the branch stays on this machine.")
    else:
        result = git(repo, "push", "-q", "-u", "origin", branch)
        if result.returncode == 0:
            lines.append(f"Push: pushed {branch} to origin.")
        else:
            lines.append(f"Push: push failed: {(result.stderr or result.stdout).strip()}")
            code = 1
    return code, lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, help="the plan's path, relative to the repository")
    parser.add_argument("--message", required=True, help="the commit message for the work not yet committed")
    parser.add_argument("--reviews-passed", action="store_true",
                        help="every review of the build passed, so mark the plan Built")
    parser.add_argument("--repo", default=".", help="the repository (default: the current directory)")
    args = parser.parse_args(argv)
    code, lines = hand_over(os.path.abspath(args.repo), args.plan, args.message, args.reviews_passed)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())

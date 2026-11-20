"""Every eval case starts in a git repository of its own.

`claude plugin eval` gives each run a home folder that already holds an empty git repository.
A case folder that is not a repository of its own is then a subfolder of that one, so the
plugin's hooks, which judge a path from the top of its repository (docs/adrs/0046), see
`cwd/AGENTS.md` instead of `AGENTS.md` and stay silent, and skills write their documents in the
home folder, where the run may not write. So every case's setup script, `place-files.sh`, starts
a repository in the case folder, as a real project has, and the case declares it.

A plan or spike record is named by the day it is written, and a hook refuses any other date, so
a case that has one written names it in its prompt as `<today's date>-<words>.md`, never a fixed
date, which would pass on that day only. Its graders read it through a link the setup script
makes once it knows the date. The date is the one when the case starts, so a run that crosses
midnight cannot find its document; no grader can follow a pattern of names instead.

A case whose session folder deliberately holds its repository one level down, as in a Claude
project thread, starts that repository itself, so any `git init` counts.
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIRS = ("evals", "evals-failed-check")
SCAFFOLD = re.compile(r"^context:[ \t]*\n(?:[ \t]+\S[^\n]*\n)*?[ \t]+scaffold_script:[ \t]*place-files\.sh[ \t]*$", re.M)
DATED = re.compile(r"docs/(?:plans|spikes)/(?:[^\s`]*/)?\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md")


def cases():
    """Each case folder: one holding case.yaml or prompt.md."""
    for base in EVAL_DIRS:
        folder = os.path.join(ROOT, base)
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if any(os.path.isfile(os.path.join(path, f)) for f in ("case.yaml", "prompt.md")):
                yield f"{base}/{name}", path


def read(path):
    """The file's text, or "" when there is none."""
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def problems(path):
    """Why the case would not start in a repository of its own, or an empty list."""
    found = []
    # The runner reads scaffold_script only under context:, indented below it.
    if not SCAFFOLD.search(read(os.path.join(path, "case.yaml"))):
        found.append("case.yaml does not declare scaffold_script: place-files.sh under context:")
    script = os.path.join(path, "place-files.sh")
    if not os.path.isfile(script):
        found.append("no place-files.sh")
    elif not re.search(r"^\s*git init\b", read(script), re.M):
        found.append("place-files.sh never runs git init")
    for name in DATED.findall(read(os.path.join(path, "prompt.md"))):
        if not os.path.exists(os.path.join(path, "files", name)):
            found.append(f"prompt names a new document with a fixed date: {name}")
    return found


class EveryCaseStartsInARepository(unittest.TestCase):
    def test_every_case(self):
        bad = {name: found for name, path in cases() if (found := problems(path))}
        self.assertEqual(bad, {})

    def test_finds_cases(self):
        self.assertGreater(len(list(cases())), 200)


if __name__ == "__main__":
    unittest.main()

"""Every eval case starts in a git repository of its own.

`claude plugin eval` gives each run a home folder that already holds an empty git repository.
A case folder that is not a repository of its own is then a subfolder of that one, so the
plugin's hooks, which judge a path from the top of its repository (docs/adrs/0046), see
`cwd/AGENTS.md` instead of `AGENTS.md` and stay silent, and skills write their documents in the
home folder, where the run may not write. So every case's setup script, `place-files.sh`, starts
a repository in the case folder, as a real project has, and the case declares it.

A case whose session folder deliberately holds its repository one level down, as in a Claude
project thread, starts that repository itself, so any `git init` counts.
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIRS = ("evals", "evals-failed-check")


def cases():
    """Each case folder: one holding case.yaml or prompt.md."""
    for base in EVAL_DIRS:
        folder = os.path.join(ROOT, base)
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if any(os.path.isfile(os.path.join(path, f)) for f in ("case.yaml", "prompt.md")):
                yield f"{base}/{name}", path


def problems(path):
    """Why the case would not start in a repository of its own, or an empty list."""
    found = []
    case = os.path.join(path, "case.yaml")
    text = open(case, encoding="utf-8").read() if os.path.isfile(case) else ""
    if not re.search(r"^\s*scaffold_script:\s*place-files\.sh\s*$", text, re.M):
        found.append("case.yaml does not declare scaffold_script: place-files.sh")
    script = os.path.join(path, "place-files.sh")
    if not os.path.isfile(script):
        found.append("no place-files.sh")
    elif not re.search(r"^\s*git init\b", open(script, encoding="utf-8").read(), re.M):
        found.append("place-files.sh never runs git init")
    return found


class EveryCaseStartsInARepository(unittest.TestCase):
    def test_every_case(self):
        bad = {name: found for name, path in cases() if (found := problems(path))}
        self.assertEqual(bad, {})

    def test_finds_cases(self):
        self.assertGreater(len(list(cases())), 200)


if __name__ == "__main__":
    unittest.main()

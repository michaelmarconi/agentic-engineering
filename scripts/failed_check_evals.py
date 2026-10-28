#!/usr/bin/env python3
"""Run the evals that test what a skill does when the correction check fails.

The correction checker is a model, so no ordinary eval can make it fail on demand. This script
copies the plugin to a temporary folder, replaces each agent there with the stand-in of the same
name from evals-failed-check/agents/ (the checker always fails with a known finding; a stand-in
reviewer always reports a failure the drafting agent can correct, for a skill whose own draft
would otherwise pass review and never reach the check), makes the case folders under
evals-failed-check/ the copy's only evals, and runs `claude plugin eval` on the copy with any
further arguments given.
The plugin itself is never changed. The run's results are copied to evals-failed-check/results/
and the temporary folder is deleted.

Example:
  python3 scripts/failed_check_evals.py --case 'spec-*' --model sonnet --judge-model sonnet \\
      --scaffold --allow-tools Write Edit
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CASES = "evals-failed-check"
STAND_INS = "agents"


def build_copy(plugin, copy):
    """Copy the plugin to `copy`, with the stand-in agents and only the failed-check cases."""
    shutil.copytree(plugin, copy, ignore=shutil.ignore_patterns(".git", "evals", CASES, "__pycache__"))
    shutil.copytree(os.path.join(plugin, CASES, STAND_INS), os.path.join(copy, "agents"), dirs_exist_ok=True)
    shutil.copytree(os.path.join(plugin, CASES), os.path.join(copy, "evals"),
                    ignore=shutil.ignore_patterns(STAND_INS, "results"))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    _, rest = parser.parse_known_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "sdlc")
        build_copy(ROOT, copy)
        code = subprocess.call(["claude", "plugin", "eval", copy, "--trust-plugin", *rest])
        results = os.path.join(copy, "evals", "results")
        if os.path.isdir(results):
            shutil.copytree(results, os.path.join(ROOT, CASES, "results"), dirs_exist_ok=True)
    return code


if __name__ == "__main__":
    sys.exit(main())

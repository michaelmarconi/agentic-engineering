#!/usr/bin/env python3
"""List a build's steps from its plan, numbered, so its progress list is the same every run.

`/build` runs this once its checks before building pass, to fill the progress list the lifecycle
page's "Showing progress" section describes (docs/adrs/0062, docs/adrs/0063). The steps are each
requirement the plan's Specs section names, in the order listed there, read with the parsing
`scripts/status_check.py` already has, then four fixed steps: "Reviews of the code",
"Corrections", "Check that the corrections broke nothing" and "Give the person the work and
reports".

Output: with --plan alone, one line per step, as "1. <step>". With --step N as well, only
"Step N of M: <step>", which before_code.py also prints at each requirement.

Exit codes: 0 when the steps are printed; 2 when the plan cannot be read, names no requirements,
or --step is out of range.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import status_check  # noqa: E402

FIXED = ("Reviews of the code", "Corrections", "Check that the corrections broke nothing",
         "Give the person the work and reports")


class Refused(Exception):
    """Why the plan's steps cannot be listed."""


def steps(plan):
    """The build's steps for the plan at that path: its requirements in order, then FIXED."""
    text = status_check.read(plan)
    if text is None:
        raise Refused(f"It can't read the plan {plan}.")
    entries, _ = status_check.named_specs(plan, text)
    names = [name for _, _, requirements in entries for name, _, _ in requirements]
    if not names:
        raise Refused(f"The plan {plan} names no requirements under Specs, so there are no steps to list.")
    return names + list(FIXED)


def line(plan, step):
    """The line naming one step by its number out of the total, as "Step N of M: <step>"."""
    listed = steps(plan)
    if not 1 <= step <= len(listed):
        raise Refused(f"Step {step} is not one of this build's steps: give 1 to {len(listed)}.")
    return f"Step {step} of {len(listed)}: {listed[step - 1]}"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True, help="the plan's path")
    parser.add_argument("--step", type=int, help="print only this step, by its number")
    args = parser.parse_args(argv)
    try:
        if args.step is None:
            for number, step in enumerate(steps(args.plan), 1):
                print(f"{number}. {step}")
        else:
            print(line(args.plan, args.step))
    except Refused as reason:
        print(reason)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

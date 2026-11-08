#!/usr/bin/env python3
"""Count the words in an ADR's plain part, so /adr can keep it short enough for a person to read.

Usage: python3 adr.py words <path to the ADR>

An ADR reads from plain to technical. Its plain part is everything between the frontmatter and
`## Technical detail`, apart from HTML comments; words are counted exactly as the plugin's status
hook counts them (scripts/status_check.py), which refuses `👍 Accepted` for an ADR whose plain part
holds more than 500 words. The count and the limit go to stdout; exit code 0 means within the
limit, 1 over it or unreadable.
"""

import argparse
import os
import sys

# The status hook lives in the plugin's scripts/ folder; sharing its counting keeps the two in step.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from status_check import ADR_DETAIL, ADR_PLAIN_LIMIT, plain_words  # noqa: E402


def words(path):
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"{name}: can't read {path} ({error})", file=sys.stderr)
        return 1
    count = plain_words(text, ADR_DETAIL)
    if count > ADR_PLAIN_LIMIT:
        print(f"{name}: the plain part holds {count} words, {count - ADR_PLAIN_LIMIT} over the "
              f"{ADR_PLAIN_LIMIT} allowed; shorten it, moving detail down into {ADR_DETAIL}")
        return 1
    print(f"{name}: the plain part holds {count} words, within the {ADR_PLAIN_LIMIT} allowed")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    words_parser = commands.add_parser(
        "words",
        help="count the words in the ADR's plain part",
        description=f"Count the words in an ADR's plain part, from the title down to {ADR_DETAIL}, "
                    "apart from HTML comments, as the status hook counts them.",
        epilog=f"Output: the count and the limit, on stdout. Exit codes: 0 within {ADR_PLAIN_LIMIT} words; "
               "1 over it, or the ADR can't be read, with the reason on stderr.",
    )
    words_parser.add_argument("adr", help="the ADR, a .md file in docs/adrs/")
    args = parser.parse_args(argv)
    return words(args.adr)


if __name__ == "__main__":
    sys.exit(main())

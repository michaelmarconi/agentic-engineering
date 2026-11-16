set -eu
git checkout -q -b build/word-count
mkdir -p src
: > src/__init__.py
cat > src/wordcount.py <<'PY'
"""Count the words in a text file."""

import sys


def count(text):
    return len(text.split())


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    with open(argv[0], encoding="utf-8") as f:
        print(count(f.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
PY
cat > tests/test_wordcount.py <<'PY'
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from src import wordcount


class CountWords(unittest.TestCase):
    def run_on(self, text):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.txt")
            with open(path, "w") as f:
                f.write(text)
            out = io.StringIO()
            with redirect_stdout(out):
                wordcount.main([path])
            return out.getvalue().strip()

    def test_two_words(self):
        self.assertEqual(self.run_on("hello  world\n"), "2")

    def test_empty_file(self):
        self.assertEqual(self.run_on(""), "0")
PY
git add -A
git commit -q -m 'Count the words in a file'
git push -q origin build/word-count
# The last build's report, as the hand-over script writes it, in the private folder it falls back to
# when the plugin's data folder can't be used, as in the eval's sandbox. Its correction check failed
# with three open findings, and its Head is the branch as it now stands.
# The sandbox may give Bash another temporary folder than this script's, so the report goes in
# each place that folder can be.
head="$(git rev-parse HEAD)"
report="$(mktemp)"
cat > "$report" <<MD
## What was built

Count words, with its tests. Missing file was not finished; see the correction check.

## Built before sign-off

Nothing to report.

## Tests and lint

python3 -m unittest: 2 tests, OK.

## Choices

Nothing to report.

## Defects corrected

Nothing to report.

## What each review found

Corrected the findings once; the correction check failed.

### Code review

[]

### Security review

No security issues found.

### Build review

Result: FAIL

### Correction check

Result: FAIL

Corrections:
- "Missing file is not handled": not made, src/wordcount.py still raises a traceback for a missing file
- "Wording of the missing-file message": left for the person, the spec does not settle it
- "Test for Count words committed after its code": not made, the commit order is unchanged

Broken by a correction:
- None.

Suggestions:
- None.

## The hand-over script's report

### Output

Branch: build/word-count
Work: nothing new to commit.
Plan: docs/plans/2026-11-03-word-count.md stays \`🟢 Ready to build\`, because the reviews have not all passed.
Push: pushed build/word-count to origin.
Head: $head

## Left for you to check

Nothing to report.
MD
for temp in "$(python3 -c 'import tempfile; print(tempfile.gettempdir())')" /tmp /tmp/claude "/tmp/claude-$(id -u)"; do
  folder="$temp/agentic-reports-$(id -u)"
  mkdir -p "$folder/$(basename "$PWD")" 2>/dev/null || continue
  chmod 700 "$folder"
  cp "$report" "$folder/$(basename "$PWD")/2026-11-15-build-2026-11-03-word-count.md"
done
rm "$report"

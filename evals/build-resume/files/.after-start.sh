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

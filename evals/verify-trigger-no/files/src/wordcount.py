"""Count the words or lines in a file, or the words in a web page."""

import re
import sys
import urllib.request


def words(text):
    return len(text.split())


def main(argv):
    if argv[:1] == ["--lines"]:
        with open(argv[1], encoding="utf-8") as f:
            print(len(f.read()))
        return 0
    if argv[:1] == ["--url"]:
        with urllib.request.urlopen(argv[1], timeout=5) as page:
            text = re.sub(r"<[^>]+>", " ", page.read().decode("utf-8"))
        print(words(text))
        return 0
    with open(argv[0], encoding="utf-8") as f:
        print(words(f.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

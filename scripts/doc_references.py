#!/usr/bin/env python3
"""Check that every relative reference in this repository's Markdown points at something.

Reads every `.md` file under the root, skipping hidden folders other than `.github`. In each, it
checks inline links and images, `[text](target)` and `![alt](target)`, and reference
definitions, `[name]: target` (footnotes are not references), outside code spans and fenced code blocks:

- A target with a scheme, such as `https:` or `mailto:`, is not checked.
- A target holding a placeholder, any of `< > { } $`, is not checked, so templates can show
  the shape of a reference.
- Any other target is a path relative to the referring file and must exist, as a file or a
  folder.
- A `#heading` part, on a Markdown file or on its own for the same file, must name a heading in
  that file, as GitHub names them: lowercase, punctuation dropped, spaces as hyphens, and `-1`,
  `-2` added to repeats.

Moving or renaming a file or a heading then fails a test instead of leaving a reference that
quietly points at nothing.
"""

import argparse
import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r" {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
CODE_SPAN = re.compile(r"(`+).*?\1")
INLINE = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*([^)\s]*)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
DEFINITION = re.compile(r" {0,3}\[(?!\^)[^\]]+\]:\s*(\S+)")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
PLACEHOLDER = re.compile(r"[<>{}$]")


def markdown_files(root):
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs
                         if (not d.startswith(".") or d == ".github") and d != "__pycache__")
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(folder, name)


def prose_lines(text):
    """Yield (line number, line) for every line outside fenced code blocks."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        yield number, line


def slug(heading):
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path, cache):
    if path not in cache:
        found, seen = set(), {}
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, ValueError):
            text = ""
        for _, line in prose_lines(text):
            match = HEADING.match(line)
            if match:
                base = slug(match.group(2))
                count = seen.get(base, 0)
                seen[base] = count + 1
                found.add(base if count == 0 else f"{base}-{count}")
        cache[path] = found
    return cache[path]


def targets(line):
    bare = CODE_SPAN.sub("", line)
    found = [m.group(1) for m in INLINE.finditer(bare)]
    definition = DEFINITION.match(bare)
    if definition:
        found.append(definition.group(1))
    return found


def problem(source, target, cache):
    if not target or SCHEME.match(target) or PLACEHOLDER.search(target):
        return None
    path, _, heading = target.partition("#")
    full = os.path.normpath(os.path.join(os.path.dirname(source), unquote(path))) if path else source
    if not os.path.exists(full):
        return "points at nothing"
    if heading and full.endswith(".md") and os.path.isfile(full):
        if unquote(heading).lower() not in anchors(full, cache):
            return f"has no heading #{heading}"
    return None


def problems(root):
    root = os.path.abspath(root)
    cache, found = {}, []
    for source in markdown_files(root):
        try:
            with open(source, encoding="utf-8") as f:
                text = f.read()
        except (OSError, ValueError):
            found.append(f"{os.path.relpath(source, root)}: can't be read as UTF-8 text")
            continue
        for number, line in prose_lines(text):
            for target in targets(line):
                wrong = problem(source, target, cache)
                if wrong:
                    found.append(f"{os.path.relpath(source, root)}:{number}: {target} {wrong}")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Prints one line per broken reference, as `file:line: target problem`, and exits 1 "
               "if there is any; prints nothing and exits 0 otherwise. Its tests run it on this "
               "repository, so `python3 -m unittest discover -s scripts` fails on a broken "
               "reference.")
    parser.add_argument("root", nargs="?", default=ROOT, help="folder to check (default: this repository)")
    args = parser.parse_args(argv)
    found = problems(args.root)
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

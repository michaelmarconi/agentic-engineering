# Three changes merged since 1.3.0: two builds with release notes, one quick fix without.
printf '\ndef lines(text):\n    return len(text.splitlines())\n' >> src/wordcount.py
git add -A; git commit -q -m "Build line counting" -m "Release-note: You can count lines instead of words with --lines."
printf '\ndef as_json(n):\n    return "{\\"words\\": %d}" % n\n' >> src/wordcount.py
git add -A; git commit -q -m "Build JSON output" -m "Release-note: You can get the count as JSON with --json."
sed -i.bak 's/len(text.split())/len(text.replace(",", " ").split())/' src/wordcount.py && rm -f src/wordcount.py.bak
git add -A; git commit -q -m "Count words split by commas alone"
git push -q origin main
git checkout -q -b release/1.4.0
echo "1.4.0" > VERSION
python3 - <<'PY'
p = "CHANGELOG.md"
s = open(p).read()
entry = "## [1.4.0] - 2026-11-17\n\n### Added\n\n- You can count lines instead of words with --lines.\n- You can get the count as JSON with --json.\n\n"
s = s.replace("## [1.3.0]", entry + "## [1.3.0]", 1)
open(p, "w").write(s)
PY
git add -A; git commit -q -m "Release 1.4.0"
git checkout -q main
git merge -q --no-ff -m "Merge release/1.4.0" release/1.4.0
git branch -q -D release/1.4.0
git push -q origin main

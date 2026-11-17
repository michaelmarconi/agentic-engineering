# Three changes merged since 1.3.0: two builds with release notes, one quick fix without.
printf '\ndef lines(text):\n    return len(text.splitlines())\n' >> src/wordcount.py
git add -A; git commit -q -m "Build line counting" -m "Release-note: You can count lines instead of words with --lines."
printf '\ndef as_json(n):\n    return "{\\"words\\": %d}" % n\n' >> src/wordcount.py
git add -A; git commit -q -m "Build JSON output" -m "Release-note: You can get the count as JSON with --json."
sed -i.bak 's/len(text.split())/len(text.replace(",", " ").split())/' src/wordcount.py && rm -f src/wordcount.py.bak
git add -A; git commit -q -m "Count words split by commas alone"
git push -q origin main

git checkout -q -b build/word-count
sed -i.bak 's/^status: .*/status: ✅ Built/' docs/plans/2026-11-12-word-count.md && rm docs/plans/2026-11-12-word-count.md.bak
git add -A
git commit -q -m "Mark the word count plan built"

git tag before-export
sed 's/writer.writerow(\["number", "date", "total"\])/writer.writerow(["number", "total", "date"])/; s/inv\["issued"\].isoformat(), total(inv)/total(inv), inv["issued"].isoformat()/' src/export.py > src/x && mv src/x src/export.py
git add -A
GIT_COMMITTER_DATE="2026-10-15T12:00:00Z" GIT_AUTHOR_DATE="2026-10-15T12:00:00Z" git commit -q -m "Put the total before the date in exports"
sed "s/where nothing can be installed./where nothing can be installed, not even with pip./" docs/adrs/0003-standard-library-only.md > docs/x && mv docs/x docs/adrs/0003-standard-library-only.md
git add -A
GIT_COMMITTER_DATE="2026-10-16T12:00:00Z" GIT_AUTHOR_DATE="2026-10-16T12:00:00Z" git commit -q -m "Say that pip can't be used either"

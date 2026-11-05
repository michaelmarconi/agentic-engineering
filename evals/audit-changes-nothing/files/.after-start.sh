git tag before-export
sed 's/writer.writerow(\["number", "date", "total"\])/writer.writerow(["number", "total", "date"])/; s/inv\["issued"\].isoformat(), total(inv)/total(inv), inv["issued"].isoformat()/' src/export.py > src/x && mv src/x src/export.py
git add -A
GIT_COMMITTER_DATE="2026-10-15T12:00:00Z" GIT_AUTHOR_DATE="2026-10-15T12:00:00Z" git commit -q -m "Put the total before the date in exports"
sed 's/Unpaid invoices are forgotten until the firm runs short of cash./Unpaid invoices are forgotten until the firm runs short of cash, as in March./' docs/specs/overdue-reminders.spec.md > docs/x && mv docs/x docs/specs/overdue-reminders.spec.md
git add -A
GIT_COMMITTER_DATE="2026-10-16T12:00:00Z" GIT_AUTHOR_DATE="2026-10-16T12:00:00Z" git commit -q -m "Say when invoices were forgotten"

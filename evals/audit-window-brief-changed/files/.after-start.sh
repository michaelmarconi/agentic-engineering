git tag before-brief
python3 - <<'PY'
p = "docs/brief.md"
s = open(p).read()
s = s.replace("- Selling parts or bikes online.\n", "- Selling parts or bikes online.\n- Closing the shop to bookings on chosen days: the shop opens every weekday.\n")
open(p, "w").write(s)
PY
git add -A
GIT_COMMITTER_DATE="2026-10-15T12:00:00Z" GIT_AUTHOR_DATE="2026-10-15T12:00:00Z" git commit -q -m "Say the shop opens every weekday"

#!/usr/bin/env bash
# Copies the case's files into a git repository with one commit on main and, unless the case
# holds a file named .no-origin, a bare repository at ../origin.git as its origin. Each commit
# and each pushed branch is logged under .git/ for the graders to read. A case's .after-start.sh,
# if any, runs after that, to set up state such as uncommitted work or an earlier build.
set -eu
cp -R "$(dirname "$0")/files/." .
no_origin=0
if [ -e .no-origin ]; then no_origin=1; rm .no-origin; fi
after=""
if [ -e .after-start.sh ]; then after="$(mktemp)"; mv .after-start.sh "$after"; fi
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
cat > .git/hooks/post-commit <<'HOOK'
#!/bin/sh
{ echo "=== $(git rev-parse --abbrev-ref HEAD): $(git log -1 --format=%s)"; git show --name-only --format= HEAD; } >> "$(git rev-parse --git-dir)/commits.log"
HOOK
chmod +x .git/hooks/post-commit
git add -A
git commit -q -m "Start"
: > .git/commits.log
if [ "$no_origin" = 0 ]; then
  git init -q --bare ../origin.git
  printf '#!/bin/sh\nwhile read old new ref; do echo "$ref" >> "%s"; done\n' "$(pwd)/.git/pushes.log" > ../origin.git/hooks/post-receive
  chmod +x ../origin.git/hooks/post-receive
  git remote add origin ../origin.git
  git push -q origin main
  git remote set-head origin main
fi
: > .git/pushes.log
if [ -n "$after" ]; then sh "$after"; rm "$after"; : > .git/commits.log; : > .git/pushes.log; fi

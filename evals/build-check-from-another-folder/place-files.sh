#!/usr/bin/env bash
# Copies the case's files into app/, a git repository with one commit on main, inside the
# session folder, which is not a repository itself, as in a Claude project thread (ADR 0032).
# A bare repository at ../origin.git, beside the session folder, is app's origin; it logs each
# pushed branch to app/.git/pushes.log, and each commit a push brings, with the files it changed,
# to app/.git/commits.log, for the graders to read.
set -eu
mkdir app
cp -R "$(dirname "$0")/files/." app/
cd app
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
git add -A
git commit -q -m "Start"
origin="$(cd .. && cd .. && pwd)/origin.git"
git init -q --bare "$origin"
cat > "$origin/hooks/post-receive" <<HOOK
#!/bin/sh
work="$(pwd)/.git"
while read old new ref; do
  echo "\$ref" >> "\$work/pushes.log"
  case "\$old" in
    0000000000000000000000000000000000000000) range="\$new --not --exclude=\$ref --all" ;;
    *) range="\$old..\$new" ;;
  esac
  for c in \$(git rev-list --reverse \$range); do
    { echo "=== \${ref#refs/heads/}: \$(git log -1 --format=%s \$c)"; git show --name-only --format= \$c; } >> "\$work/commits.log"
  done
done
HOOK
chmod +x "$origin/hooks/post-receive"
git remote add origin "$origin"
git push -q origin main
git remote set-head origin main
: > .git/commits.log
: > .git/pushes.log

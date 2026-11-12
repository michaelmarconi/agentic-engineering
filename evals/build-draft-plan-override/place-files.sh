#!/usr/bin/env bash
# Copies the case's files into a git repository with one commit on main and, unless the case
# holds a file named .no-origin, a bare repository at ../origin.git as its origin. The origin
# logs each pushed branch to .git/pushes.log, and each commit a push brings, with the files it
# changed, to .git/commits.log, for the graders to read. (A post-commit hook in the repository
# itself would not do: the eval's sandbox stops it recording.) A case's .after-start.sh, if any,
# runs after that, to set up state such as uncommitted work or an earlier build.
set -eu
cp -R "$(dirname "$0")/files/." .
no_origin=0
if [ -e .no-origin ]; then no_origin=1; rm .no-origin; fi
after=""
if [ -e .after-start.sh ]; then after="$(mktemp)"; mv .after-start.sh "$after"; fi
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
git add -A
git commit -q -m "Start"
if [ "$no_origin" = 0 ]; then
  git init -q --bare ../origin.git
  cat > ../origin.git/hooks/post-receive <<HOOK
#!/bin/sh
work="$(pwd)/.git"
while read old new ref; do
  echo "\$ref" >> "\$work/pushes.log"
  case "\$old" in
    0000000000000000000000000000000000000000) range="\$new --not --exclude=\$ref --all" ;;
    *) range="\$old..\$new" ;;
  esac
  for c in \$(git rev-list --reverse \$range); do
    { echo "=== \${ref#refs/heads/}: \$(git log -1 --format=%B \$c)"; git show --name-only --format= \$c; } >> "\$work/commits.log"
  done
done
HOOK
  chmod +x ../origin.git/hooks/post-receive
  git remote add origin ../origin.git
  git push -q origin main
  git remote set-head origin main
fi
: > .git/commits.log
: > .git/pushes.log
if [ -n "$after" ]; then sh "$after"; rm "$after"; : > .git/commits.log; : > .git/pushes.log; fi

#!/usr/bin/env bash
# Copies the case's files into a git repository with one commit, then writes that commit's short
# hash into each spike record in place of @COMMIT@, as a record made in this repository would
# name it. The records' change stays uncommitted, as a person's work in progress would.
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
git add -A
git commit -q -m "Start"
commit="$(git rev-parse --short=12 HEAD)"
for f in docs/spikes/*.md; do
  [ -e "$f" ] || continue
  sed "s/@COMMIT@/$commit/g" "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done

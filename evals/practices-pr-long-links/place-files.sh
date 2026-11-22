#!/usr/bin/env bash
# Copies the case's files into a git repository on GitHub, with the build's work on its own
# branch. The remote is never reached; bin/gh stands in for the GitHub command.
set -eu
cp -R "$(dirname "$0")/files/." .
chmod +x bin/gh
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
git remote add origin https://github.com/example/mailgate.git
git add AGENTS.md .github docs/specs bin
git commit -q -m "Start"
git checkout -q -b build/meaning-retry
git add -A
git commit -q -m "Report and retry messages that cannot be searched by meaning"

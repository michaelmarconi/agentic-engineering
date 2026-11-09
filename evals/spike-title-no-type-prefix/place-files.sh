#!/usr/bin/env bash
# Copies the case's files into a git repository with one commit, as the spike's run script expects.
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.com"
git add -A
git commit -q -m "Start"

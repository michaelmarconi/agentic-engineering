#!/usr/bin/env bash
# Copies the case's files into a git repository whose origin names GitHub. The remote is never
# reached: it only tells the skill the project is on GitHub.
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git remote add origin https://github.com/example/booklog.git

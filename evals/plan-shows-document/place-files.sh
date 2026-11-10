#!/usr/bin/env bash
set -eu
if [ -d "$(dirname "$0")/files" ]; then cp -R "$(dirname "$0")/files/." .; fi
# A repository on a code-hosting website, so a link to the document there is within reach.
git init -q
git remote add origin https://github.com/acme/shop.git

#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
# The document is named by the day it is written, as the plugin requires, so the graders
# read it through a link named here; the date is taken when the case starts.
mkdir -p .eval
ln -s "../docs/spikes/$(date +%F)-sandbox-sends-refunds.md" .eval/document.md
echo .eval/ >> .git/info/exclude

#!/usr/bin/env bash
set -eu
git init -q -b main
# The document is named by the day it is written, as the plugin requires, so the graders
# read it through a link named here; the date is taken when the case starts.
mkdir -p .eval
ln -s "../docs/spikes/$(date +%F)-geocoding-free-tier-limit.md" .eval/document.md
echo .eval/ >> .git/info/exclude

#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
python3 "$(dirname "$0")/../save_settings.py" review_rounds=3

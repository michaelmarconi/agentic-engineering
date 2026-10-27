#!/usr/bin/env bash
set -eu
python3 "$(dirname "$0")/../save_settings.py" review_rounds=3

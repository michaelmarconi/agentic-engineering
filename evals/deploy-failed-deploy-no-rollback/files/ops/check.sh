#!/bin/sh
# Stand-in for a real health check: records the call; the old release still answers.
mkdir -p .deploy-log
echo "check $*" >> .deploy-log/check.log
echo "health: 200 ok (version 1.3.0)"

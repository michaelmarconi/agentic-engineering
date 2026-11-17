#!/bin/sh
# Stand-in for a real health check: records the call; the product answers.
mkdir -p .deploy-log
echo "check $*" >> .deploy-log/check.log
echo "health: 200 ok"

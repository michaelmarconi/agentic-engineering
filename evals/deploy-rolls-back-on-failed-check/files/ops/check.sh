#!/bin/sh
# Stand-in for a real health check: records the call; the new release is broken, so the check
# fails until the roll back has run.
mkdir -p .deploy-log
echo "check $*" >> .deploy-log/check.log
if [ -f .deploy-log/rollback.log ]; then echo "health: 200 ok"; exit 0; fi
echo "health: 503 service unavailable"
exit 1

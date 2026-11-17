#!/bin/sh
# Stand-in for a deploy that fails: records the call and exits 1.
mkdir -p .deploy-log
echo "deploy $*" >> .deploy-log/deploy.log
echo "error: upload to $1 refused" >&2
exit 1

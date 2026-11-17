#!/bin/sh
# Stand-in for a real roll back: records the call and touches nothing else.
mkdir -p .deploy-log
echo "rollback $*" >> .deploy-log/rollback.log
echo "Rolled $1 back to the previous release."

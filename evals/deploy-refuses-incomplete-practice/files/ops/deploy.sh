#!/bin/sh
# Stand-in for a real deploy: records the call and touches nothing else.
mkdir -p .deploy-log
echo "deploy $*" >> .deploy-log/deploy.log
echo "Deployed $2 to $1."

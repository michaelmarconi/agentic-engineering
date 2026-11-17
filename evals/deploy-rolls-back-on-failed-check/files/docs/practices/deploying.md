# Deploying

## Where it runs

This machine; the scripts in `ops/` need no credentials.

## Environment: production

### Releases allowed

Any commit on `main`, named by commit.

### Deploy

`ops/deploy.sh {environment} {commit}`

### Check

`ops/check.sh production` exits 0 when the product works. No wait: check once.

### Roll back

`ops/rollback.sh {environment}`


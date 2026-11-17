# Deploying

## Where it runs

This machine; the scripts in `ops/` need no credentials.

## Environment: staging

### Releases allowed

Any commit on `main`, named by commit.

### Deploy

`ops/deploy.sh {environment} {commit}`

### Check

`ops/check.sh staging` exits 0 when the product works. No wait: check once.


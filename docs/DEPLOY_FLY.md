# Deploying DefendableRouter on Fly.io

Fly.io should host the public DefendableRouter API/control plane only:

- Member gate
- Dataset access broker
- Compute meter
- Job router API
- Receipt/admin API surface

Fly should not run GPU training jobs. GPU workloads belong on external DefendableWorker agents running on owned rigs or dedicated compute hosts.

## Production Rules

- Postgres is required for production relational state.
- SQLite is local development only.
- Local JSONL receipts are not enough for durable production receipts.
- Do not hardcode secrets in `fly.toml`, Dockerfile, or source code.
- The next production step is durable receipt persistence to Postgres and/or object storage.

DefendableRouter reads its database URL from:

```text
DEFENDABLE_ROUTER_DATABASE_URL
```

Local default:

```text
sqlite:///./data/defendable_router.db
```

Production should set a Postgres URL, for example:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

The package includes `psycopg[binary]` so SQLAlchemy can use Postgres URLs in production.

## Install flyctl

macOS:

```bash
brew install flyctl
```

Linux:

```bash
curl -L https://fly.io/install.sh | sh
```

Verify:

```bash
fly version
```

## Authenticate

```bash
fly auth login
```

## Launch App Shell

From the repo root:

```bash
cd /home/swarm/Desktop/defendable-router
fly launch --no-deploy
```

Use app name:

```text
defendable-router
```

The checked-in `fly.toml` already defines:

- `primary_region = "mia"`
- internal port `8080`
- forced HTTPS
- rolling deploys
- two minimum machines
- `/health` HTTP checks

If `mia` is unavailable for the account, change `primary_region` to `iad`.

## Configure Secrets

Set the production database URL:

```bash
fly secrets set DEFENDABLE_ROUTER_DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME'
```

Optional runtime label:

```bash
fly secrets set DEFENDABLE_ROUTER_ENV='production'
```

Optional receipt directory override:

```bash
fly secrets set DEFENDABLE_ROUTER_RECEIPTS_DIR='/app/data/receipts'
```

The receipt directory setting does not make receipts durable across machines. It is only a path override. Use Postgres/object storage receipt persistence before treating production receipts as durable records.

## Deploy

Direct deploy:

```bash
fly deploy
```

Safe script with tests first:

```bash
scripts/fly_deploy.sh
```

## Operate

Status:

```bash
fly status
```

Logs:

```bash
fly logs
```

Health checks:

```bash
fly checks list
```

Open app:

```bash
fly open
```

## Smoke Test

Default app URL:

```bash
scripts/fly_smoke.sh
```

Custom app URL:

```bash
APP_URL=https://defendable-router.fly.dev scripts/fly_smoke.sh
```

Manual health check:

```bash
curl https://defendable-router.fly.dev/health
```

Manual admin summary check:

```bash
curl https://defendable-router.fly.dev/admin/summary
```

## Docker Runtime

The Docker image runs:

```bash
uvicorn defendable_router.main:app --host 0.0.0.0 --port 8080
```

Fly routes public HTTPS traffic to internal port `8080`.

## Current Production Gaps

Before public production launch, add:

1. Postgres migration verification against the selected Fly Postgres instance.
2. Alembic migrations.
3. API key or JWT auth.
4. Admin route protection.
5. Durable receipt persistence to Postgres and/or object storage.
6. Receipt verification/export tooling.
7. Worker-agent job dispatch contract.

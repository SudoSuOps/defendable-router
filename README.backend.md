# DefendableRouter

> **Status — v0.1 spine, E2E-verified 2026-05-29.** Full end-to-end acceptance run on owned
> hardware (RTX 5090): `pytest` 26 passed, control plane (member gate · dataset broker · pricing),
> the v0.2 DefendableWorker contract (register → lease → complete/fail), and independent
> verification of all 23 ledger receipt checksums + a tamper test. Still v0.1: SQLite + local JSONL
> receipts; member/admin endpoints are unauthenticated (only `/workers/*` carries bearer auth) and
> must not be exposed publicly. Receipts are **hash-chained** (`seq` + `parent_hash`, verifiable via
> `GET /receipts/verify` / `defendable-router verify-ledger`), mirroring the DefendableCloud chain. See *Known Limitations*.

DefendableRouter is the first backend spine for DefendableCloud: the member gate, dataset access broker, compute meter, job router, and receipt ledger for member-only datasets and hourly GPU compute.

It is intentionally small in v0.1. The point is to make the core control plane explicit before connecting real GPU workers, Stripe, Postgres, Kubernetes, object storage, or DefendableOS anchoring.

## What It Is

DefendableRouter controls the first operational boundary for DefendableCloud.

- It decides whether a member is active.
- It brokers access to the dataset registry.
- It stores compute inventory and GPU availability.
- It prices hourly GPU work from central constants.
- It creates compute and fine-tune jobs.
- It routes jobs to an available node or queues them.
- It writes checksumed JSONL receipts for important actions.
- It exposes admin summary metrics for the local control plane.

DefendableRouter is the gate, meter, router, and receipt layer.

## Why It Exists

The doctrine is simple:

Members get the datasets. Compute gets metered. Every job gets a receipt.

DefendableCloud is not just selling raw GPU time. It is building a member-first compute and dataset platform where curated data access, transparent compute pricing, and proof-of-execution records are part of the product boundary from day one.

## Business Model

- Annual membership: `$100.00`
- Dataset access: included for active members
- `rtx6000_blackwell_96gb`: RTX PRO 6000 Blackwell Workstation 96GB at `$5/hr`
- `rog_astral_5090_32gb`: ASUS ROG Astral RTX 5090 32GB at `$2/hr`

The dataset library target is 2,000,000 curated datasets, dataset records, or dataset objects. v0.1 stores registry metadata locally and is structured so the registry can later point at object storage, signed URLs, or an external dataset index.

## Current v0.1 Capabilities

- Member creation and activation
- Membership status checks
- Dataset registry entries
- Member-only dataset access checks
- Compute node inventory
- GPU pricing quotes
- Compute job creation
- Fine-tune job type support
- Local JSONL receipts
- Admin summary endpoint
- Typer CLI for local operations
- Pytest coverage for health, membership gate, pricing, quotes, receipts, jobs, and admin summary

## Architecture

DefendableRouter is a modular FastAPI service with thin API handlers and business rules in service/core modules.

```text
Client / Admin / CLI
|
v
DefendableRouter FastAPI
|
+--> MemberGate
+--> DatasetRegistry
+--> ComputeInventory
+--> PricingEngine
+--> JobRouter
+--> ReceiptLedger
+--> AdminSummary
|
v
SQLite local dev / Postgres later
JSONL receipt ledger
GPU workers later
```

Module responsibilities:

- `MemberGate`: membership status, activation, active-member enforcement.
- `DatasetRegistry`: dataset metadata, filters, and access receipts.
- `ComputeInventory`: GPU node registration, availability, and capacity counters.
- `PricingEngine`: central membership and GPU hourly rates.
- `JobRouter`: validates jobs, assigns nodes, queues jobs, and calculates final cost.
- `ReceiptLedger`: writes canonical checksumed JSONL receipts.
- `AdminSummary`: returns local operating metrics.

Deeper notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Install

Preferred `uv` flow:

```bash
cd /home/swarm/Desktop/defendable-router
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Fallback Python venv flow:

```bash
cd /home/swarm/Desktop/defendable-router
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Initialize Local Database

```bash
defendable-router init-db
defendable-router seed-demo
```

This creates the local SQLite tables and inserts demo members, datasets, and compute nodes.

## Run API

```bash
uvicorn defendable_router.main:app --host 0.0.0.0 --port 8088 --reload
```

OpenAPI docs are available at:

- `http://localhost:8088/docs`
- `http://localhost:8088/redoc`

## Run Tests

```bash
pytest
```

Verified locally during this build: `11 passed, 3 warnings`.

## Demo Data

Seed command:

```bash
defendable-router seed-demo
```

Demo members:

- `mem_demo_active_1`: `ada@defendable.cloud`, active
- `mem_demo_active_2`: `grace@defendable.cloud`, active
- `mem_demo_inactive_1`: `inactive@defendable.cloud`, inactive

Demo datasets:

- `ds_finance_gold`: Curated Finance Signals, `finance`, `gold`
- `ds_health_silver`: Healthcare Claims Sample, `healthcare`, `silver`
- `ds_legal_platinum`: Legal Contract Clauses, `legal`, `platinum`
- `ds_security_royal`: Security Incident Royal Jelly, `security`, `royal_jelly`
- `ds_general_bronze`: General Web Bronze, `general`, `bronze`

Demo compute nodes:

- `node_rails_6000_01`: `rails-6000-01`, `rtx6000_blackwell_96gb`
- `node_smash_5090_01`: `smash-5090-01`, `rog_astral_5090_32gb`

## API Quickstart

Assume the API is running at `http://localhost:8088` and demo data has been seeded.

Health:

```bash
curl http://localhost:8088/health
```

Admin summary:

```bash
curl http://localhost:8088/admin/summary
```

Member status:

```bash
curl http://localhost:8088/members/mem_demo_active_1/status
```

Dataset list:

```bash
curl 'http://localhost:8088/datasets?limit=10&offset=0'
```

Dataset access with active member:

```bash
curl -X POST http://localhost:8088/datasets/ds_finance_gold/access   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1"}'
```

Dataset access with inactive member. This should return `403`:

```bash
curl -i -X POST http://localhost:8088/datasets/ds_finance_gold/access   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_inactive_1"}'
```

Compute inventory:

```bash
curl http://localhost:8088/compute/inventory
```

RTX 6000 quote, 2 hours = `$10.00`:

```bash
curl -X POST http://localhost:8088/compute/quote   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","requested_gpu_sku":"rtx6000_blackwell_96gb","estimated_hours":2,"job_type":"fine_tune"}'
```

5090 quote, 3 hours = `$6.00`:

```bash
curl -X POST http://localhost:8088/compute/quote   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","requested_gpu_sku":"rog_astral_5090_32gb","estimated_hours":3,"job_type":"inference"}'
```

Create fine-tune job:

```bash
curl -X POST http://localhost:8088/jobs   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","job_type":"fine_tune","requested_gpu_sku":"rtx6000_blackwell_96gb","estimated_hours":2.5,"input_dataset_ids":["ds_finance_gold"],"output_uri":"s3://defendable-runs/demo/fine-tune-001"}'
```

Read job:

```bash
curl http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE
```

Start job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/start
```

Complete job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/complete
```

Cancel job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/cancel
```

More examples: [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)

## CLI Quickstart

```bash
defendable-router --help
defendable-router init-db
defendable-router seed-demo
defendable-router list-members
defendable-router list-datasets
defendable-router list-compute
defendable-router admin-summary
defendable-router quote --member-id mem_demo_active_1 --gpu rtx6000_blackwell_96gb --hours 2.5 --job-type fine_tune
```

## Receipt Model

Receipts are written to:

```text
data/receipts/YYYY-MM-DD.receipts.jsonl
```

Each important action emits a receipt:

- Membership activation: `membership`
- Dataset access: `dataset_access`
- Compute quote: `compute_quote`
- Compute job creation/completion: `compute_job`
- Fine-tune job creation/completion: `fine_tune_job`

Each receipt includes a `checksum_sha256`. The checksum is SHA256 over a canonical JSON string of the receipt payload excluding the checksum field itself. Decimal values are normalized to two-place strings, timestamps are ISO formatted, and JSON keys are sorted.

**Hash chain.** Receipts are chained, mirroring the DefendableCloud per-org chain. Each receipt also carries a `seq` (monotonic from `0`) and a `parent_hash` equal to the prior receipt's `checksum_sha256` (genesis = 64 zeros); both are inside the hashed body, so the link is tamper-evident. The router keeps one house-wide chain. Validate it with `GET /receipts/verify` (recomputes every checksum, checks `seq` order + `parent_hash` links) or the CLI `defendable-router verify-ledger`. Tamper with any stored receipt and verification flips `ok: false` and pinpoints the offending `seq`.

Example receipt:

```json
{"amount_usd":"10.00","checksum_sha256":"b3f4...","created_at":"2026-05-28T19:33:59.596803+00:00","dataset_ids":["ds_finance_gold"],"job_id":"job_example","member_id":"mem_demo_active_1","metadata":{"gpu_sku":"rtx6000_blackwell_96gb","phase":"created","status":"running"},"receipt_id":"rcpt_example","receipt_type":"fine_tune_job"}
```

Receipts are local JSONL in v0.1. Later they can be Merkle-anchored, exported, audited, synced to object storage, or integrated with DefendableOS.

More detail: [docs/RECEIPTS.md](docs/RECEIPTS.md)

## Pricing Model

Central constants live in `defendable_router/core/pricing.py`:

- `ANNUAL_MEMBERSHIP_PRICE_USD = 100.00`
- `rtx6000_blackwell_96gb = $5/hr`
- `rog_astral_5090_32gb = $2/hr`

Sample math:

- 2 hours on RTX PRO 6000 Blackwell Workstation 96GB: `2 * $5 = $10`
- 3 hours on ASUS ROG Astral RTX 5090 32GB: `3 * $2 = $6`

The API never trusts a caller-supplied hourly rate. Quotes and job estimates are calculated from the central pricing module.

## Dataset Access Model

Dataset metadata is stored in the local registry. Active members can access member datasets. Inactive, expired, or banned members are blocked by `require_active_member`.

A successful dataset access call returns access metadata and emits a `dataset_access` receipt. v0.1 returns the configured `object_uri`; it does not generate signed object-store URLs yet.

## Compute Job Model

Supported job statuses:

- `queued`
- `running`
- `completed`
- `failed`
- `canceled`

Supported job types:

- `inference`
- `fine_tune`
- `eval`
- `dataset_build`
- `embedding`
- `batch`

v0.1 validates the member, GPU SKU, job type, and dataset IDs. It assigns an available compute node when capacity exists; otherwise the job is queued. It does not actually execute GPU workloads yet. Completion records `actual_started_at`, `actual_finished_at`, `actual_hours`, `actual_cost_usd`, and a final receipt.

## Environment Variables

The settings prefix is `DEFENDABLE_ROUTER_`. Values may be placed in `.env`.

- `DEFENDABLE_ROUTER_ENV`: runtime label, defaults to `local`
- `DEFENDABLE_ROUTER_DATABASE_URL`: SQLAlchemy database URL, defaults to `sqlite:///./data/defendable_router.db`
- `DEFENDABLE_ROUTER_RECEIPTS_DIR`: receipt ledger directory, defaults to `./data/receipts`

See [.env.example](.env.example).

## DefendableWorker Contract

DefendableRouter v0.2 adds the contract for owned-rig workers. Workers register capabilities, authenticate with bearer tokens, send heartbeats, lease queued jobs, report status/logs/artifacts, and complete or fail jobs. The router remains the public control plane; workers initiate outbound calls and perform local GPU execution later.

Worker docs: [docs/WORKER_CONTRACT.md](docs/WORKER_CONTRACT.md)

## Known Limitations

- No Alembic migrations yet.
- No Stripe integration yet.
- Worker bearer-token auth exists for `/workers/*`; member/admin API auth is not implemented yet.
- Worker lease/status/artifact contract exists; actual GPU execution agent is not implemented yet.
- No object storage signed URLs yet.
- No Kubernetes integration yet.
- Receipts are local JSONL only.
- SQLite is for local development.
- Admin endpoints are unauthenticated in v0.1 and should not be exposed publicly.

## Next Build Targets

1. Postgres migration path
2. Alembic migrations
3. API key or JWT auth
4. Stripe membership billing
5. Object storage dataset signed URLs
6. GPU worker agent
7. Job queue with Redis/RQ/Celery or Dramatiq
8. Web admin dashboard
9. Receipt export and Merkle anchoring
10. DefendableOS integration

Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)

Fly.io deployment guide: [docs/DEPLOY_FLY.md](docs/DEPLOY_FLY.md)

## Product Direction

DefendableRouter is not just a billing app. It is the first control plane for DefendableCloud: member access, dataset utility, compute routing, and proof-of-execution receipts.

The product direction is member-first compute with transparent pricing and defensible operational records. Dataset access should feel included and useful. Compute should be metered plainly. Every access, quote, and job should leave a receipt that can be audited later.

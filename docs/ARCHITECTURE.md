# Architecture

DefendableRouter v0.1 is a local-first FastAPI control plane for DefendableCloud. It does not try to run GPUs directly. It owns the access, pricing, routing, and receipt boundary so later worker systems can plug into a clear contract.

## Control Plane Shape

```text
Client / Admin / CLI
|
v
FastAPI application: defendable_router.main:app
|
+--> api/health.py
+--> api/members.py
+--> api/datasets.py
+--> api/compute.py
+--> api/jobs.py
+--> api/admin.py
|
v
services/* and core/*
|
v
SQLAlchemy models + JSONL receipts
```

## Modules

## MemberGate

Files:

- `defendable_router/services/members.py`
- `defendable_router/core/security.py`
- `defendable_router/api/members.py`

MemberGate creates members, activates annual memberships, checks expiration, and enforces `require_active_member` before protected actions.

Protected v0.1 actions:

- Dataset access
- Compute quote
- Job creation
- Fine-tune job creation through the job service

## DatasetRegistry

Files:

- `defendable_router/services/datasets.py`
- `defendable_router/api/datasets.py`
- `defendable_router/db/models.py`

The dataset registry stores metadata, not dataset bytes. The `object_uri` field is the future bridge to object storage. v0.1 returns metadata and writes a receipt when access is granted.

## ComputeInventory

Files:

- `defendable_router/services/compute_inventory.py`
- `defendable_router/api/compute.py`

ComputeInventory registers supported GPU nodes and tracks simple local capacity with `max_concurrent_jobs` and `current_jobs`. A node becomes `busy` when capacity is full and returns to `available` when capacity is released.

## PricingEngine

Files:

- `defendable_router/core/pricing.py`
- `defendable_router/services/billing.py`

Pricing is centralized. Callers pass SKU and hours; the service calculates the hourly rate and estimated cost from constants. This prevents clients from injecting arbitrary rates.

## JobRouter

Files:

- `defendable_router/services/job_router.py`
- `defendable_router/api/jobs.py`
- `defendable_router/services/fine_tune.py`

JobRouter validates member eligibility at the API boundary, then validates GPU SKU, job type, and referenced dataset IDs. It assigns an available node when possible. If no node is available, the job is queued.

v0.1 does not launch containers, call Kubernetes, or run training. It records the requested work and creates receipts.

## ReceiptLedger

Files:

- `defendable_router/core/receipts.py`

ReceiptLedger appends canonical JSON records to daily JSONL files. It is intentionally simple and local in v0.1, but the receipt shape is designed to be exportable.

## AdminSummary

Files:

- `defendable_router/api/admin.py`

AdminSummary returns counts for active members, datasets, node states, job states, estimated job revenue, and annual membership revenue.

## Data Stores

v0.1 uses:

- SQLite for local relational state
- JSONL files for receipts
- Sample JSON/JSONL files for fixture-style local data

Production path:

- Postgres for relational state
- Object storage for datasets and artifacts
- Worker queue for GPU dispatch
- Receipt export/anchoring for audit durability

## Request Flow Examples

Dataset access:

```text
POST /datasets/{dataset_id}/access
-> require_active_member(member_id)
-> load dataset metadata
-> write dataset_access receipt
-> return object_uri metadata
```

Compute quote:

```text
POST /compute/quote
-> require_active_member(member_id)
-> load hourly rate from pricing.py
-> estimated_cost = hourly_rate * estimated_hours
-> write compute_quote receipt
-> return quote
```

Fine-tune job:

```text
POST /jobs
-> require_active_member(member_id)
-> validate job_type == fine_tune is supported
-> validate GPU SKU
-> validate dataset IDs
-> assign available node or queue
-> write fine_tune_job receipt
-> return job
```

## Router / Worker Relationship

DefendableRouter is the public API and control plane. DefendableWorker agents run on owned GPU rigs and call home to the router. The router does not need inbound access to private rigs in v0.2.

DefendableRouter owns:

- Public API
- Member gate
- Dataset broker
- Pricing
- Job queue
- Receipts
- Worker contract

DefendableWorker owns:

- Rig-local execution
- Capability registration
- Heartbeats
- Job lease polling
- Local GPU work
- Logs and artifact reporting
- Complete/fail callbacks

Worker contract details: [WORKER_CONTRACT.md](WORKER_CONTRACT.md)

# Roadmap

This roadmap keeps v0.1 honest: DefendableRouter is a working backend scaffold, not a full production cloud yet.

## v0.2: Production Data Foundations

- Add Alembic migrations.
- Add Postgres-first deployment configuration.
- Add API key or JWT auth.
- Protect admin routes.
- Add receipt verification CLI command.
- Add structured error responses for client integrations.
- Add pagination metadata for dataset and job list endpoints.

## v0.3: Billing and Dataset Delivery

- Integrate Stripe for annual membership billing.
- Store Stripe customer/subscription references on members.
- Reconcile membership receipts with Stripe payment events.
- Add object storage signed URL generation for dataset access.
- Add dataset ingestion/import tooling.
- Add dataset quality and provenance fields.
- Add receipt export to object storage.

## v0.4: Compute Dispatch

- Add a real job queue using Redis/RQ/Celery or Dramatiq.
- Add GPU worker agent registration and heartbeat.
- Add job lease/timeout semantics.
- Add worker-side status updates.
- Add artifact/output registration.
- Add failure receipts and retry policy.

## v0.5: Admin and Operations

- Add web admin dashboard.
- Add member search and dataset search.
- Add inventory health view.
- Add job timeline view.
- Add receipt browser and checksum verifier.
- Add operational metrics and logs.

## v1.0: DefendableCloud Control Plane

- Postgres-backed production API.
- Authenticated member and admin surfaces.
- Stripe-backed membership lifecycle.
- Object-storage-backed dataset access.
- GPU worker fleet integration.
- Receipt export, verification, and Merkle anchoring.
- DefendableOS integration for proof-of-execution records.
- Production deployment docs and runbooks.

# DefendableRouter

Deterministic receipt spine for the DefendableOS ecosystem. Ring ring · to the shed.

DefendableRouter is the intake and receipt rail. It captures client meaning, turns it into an assignment, mints a canonical receipt object, hashes it, stamps an object-storage path, opens Tribunal + DDEED stubs, writes a manifest, and hands the bundle to StreetLedger. Books and records first. No fluff.

## Mission thesis

Language becomes assignment.
Assignment becomes receipt.
Receipt becomes deed.
Deed becomes books and records.
Books and records become trust.

The language lives in the blocks.

## What this repo IS

- A deterministic receipt object generator (Pydantic v2, orjson, SHA256).
- A CLI for: `create`, `verify`, `hash`, `export`, `agent kimi-review`.
- Canonical JSON + reproducible hashes. Verify reproduces the same digest, byte for byte.
- Stub generators for Tribunal verdicts and DDEED deeds (filled in by downstream rails).
- Object-storage-ready run folders with manifests and `SHA256SUMS.txt`.
- A Kimi/Moonshot agent reviewer that audits receipts but never overrides hashes.

## What this repo is NOT

- Not a frontend.
- Not a model training repo.
- Not a Kubernetes / distributed-worker framework.
- Not a generic agent SDK.
- Not the ledger. The ledger is StreetLedger. This is the intake.

## Why deterministic receipts matter

If the AI agent is now part of the business, the business needs books and records of what the agent did, why it did it, whether the assignment succeeded, and what happened when it failed. Deterministic receipts mean every output is hashable, every hash is reproducible, every artifact has a provable path, and every dispute has an exhibit. Cost to mint a receipt is fixed and visible. Receipts first.

## How the rails connect

```
Client / StreetChat / API / Edge
  ↓
DefendableRouter           ← this repo · the spine
  ↓
Canonical Receipt Object
  ↓
SHA256 + canonical SHA256
  ↓
Object Storage prefix (streetledger bucket)
  ↓
Tribunal Stub  →  Tribunal verdict  (downstream)
  ↓
DDEED Stub     →  DDEED anchored on Hedera (downstream)
  ↓
Manifest + SHA256SUMS.txt
  ↓
StreetLedger export
  ↓
SwarmFixer / Communicator training candidates
```

- **StreetChat** is the client-facing intake. It POSTs a `RouterEvent`. Router builds the receipt.
- **Tribunal** consumes the receipt + the Tribunal stub, runs the rubric, and emits a verdict. The verdict references `verdict_id` that the Router already stubbed.
- **DDEED** picks up Tribunal verdicts that pass and anchors them on Hedera HCS 0.0.10291838.
- **StreetLedger** ingests the manifest + the artifacts at the object-storage prefix. Books and records.
- **SwarmFixer** consumes repaired traces (later receipts referencing prior `receipt_id`).

## Receipt object

The canonical receipt has a stable shape and a reproducible hash.

- `canonical_receipt_sha256` = SHA256 over the receipt with `created_at` + `hashes` stripped (volatile-free).
- `receipt_sha256` = SHA256 over the receipt with the canonical hash inserted and `receipt_sha256` nulled out — reproducible by any verifier with the same JSON.

The full schema lives in `defendablerouter/schemas/router_receipt.py`. The canonicalizer is in `defendablerouter/core/canonicalize.py`. There is one way to hash. There is one way to verify.

## Object storage layout

Each run lives in its own directory and on its own prefix.

```
data/runs/router_smoke_001/
  input.json                  # the original RouterEvent
  router_receipt.json         # the canonical receipt (deed-ready)
  tribunal_stub.json          # opens the Tribunal verdict slot
  ddeed_stub.json             # opens the DDEED deed slot
  manifest.json               # manifest of all artifacts in this run
  SHA256SUMS.txt              # reproducible per-file hashes
  object_storage_path.txt     # s3://streetledger/router/<client>/<app>/<assignment>/
  kimi_review.json            # agent review (skipped cleanly if no MOONSHOT_API_KEY)
```

S3 prefix scheme:

```
s3://streetledger/router/<client_id>/<app_id>/<assignment_id>/
```

## CLI

```bash
defendablerouter receipt create \
  --event defendablerouter/examples/sample_event.json \
  --out data/runs/router_smoke_001

defendablerouter receipt verify --run data/runs/router_smoke_001

defendablerouter receipt hash --file data/runs/router_smoke_001/router_receipt.json

defendablerouter receipt export --run data/runs/router_smoke_001 --target local

defendablerouter agent kimi-review --run data/runs/router_smoke_001
```

## Make targets

```bash
make install      # venv + editable install
make test         # pytest
make smoke        # create → verify → kimi-review (skips cleanly without key)
make verify       # re-verify the smoke run
make clean-runs   # wipe data/runs
```

## Agent layer (Kimi / Moonshot)

Kimi is an agent reviewer. Kimi is NOT the ledger. Kimi may flag schema risks, missing fields, verification weaknesses, provenance gaps, and object-storage improvements. Kimi may NOT invent receipt facts, override hashes, or replace canonicalization. The deterministic spine ignores the model.

Without `MOONSHOT_API_KEY`, the review is recorded as `verdict: SKIPPED` with a `skip_reason`. The smoke test still passes. Receipts first.

## Voice

Class A 5-cap. Operator-grade. Books and records. No startup-speak. No AI hype.
Ring ring. To the shed.

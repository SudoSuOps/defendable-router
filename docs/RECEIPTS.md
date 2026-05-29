# Receipts

Receipts are the audit primitive in DefendableRouter v0.1. They make member actions, dataset access, compute quotes, and compute jobs inspectable after the fact.

## Location

Receipts are written to daily JSONL files:

```text
data/receipts/YYYY-MM-DD.receipts.jsonl
```

Each line is one JSON object.

## Receipt Types

Current receipt types:

- `membership`: member activation and annual fee marker
- `dataset_access`: member access to dataset metadata/object URI
- `compute_quote`: priced estimate for a compute request
- `compute_job`: generic compute job creation or completion
- `fine_tune_job`: fine-tune job creation or completion

## Fields

A receipt contains:

- `receipt_id`: generated `rcpt_...` ID
- `receipt_type`: action category
- `member_id`: member responsible for the action
- `job_id`: optional job reference
- `dataset_ids`: optional dataset references
- `amount_usd`: normalized two-decimal amount string
- `metadata`: receipt-specific context
- `created_at`: UTC timestamp
- `checksum_sha256`: integrity checksum

## Checksum Integrity

The checksum is calculated from canonical JSON excluding `checksum_sha256`.

Canonicalization in v0.1:

- JSON keys are sorted.
- Separators are compact.
- Decimal values become two-decimal strings.
- Timestamps use ISO format.
- ASCII output is used for ledger stability.

In code:

```text
checksum_sha256 = sha256(canonical_json(receipt_without_checksum))
```

This is not a cryptographic anchoring system yet. It is a local tamper-evidence primitive: if a receipt line changes, recomputing the checksum from the receipt body will no longer match.

## Example

```json
{"amount_usd":"0.00","checksum_sha256":"9d1c...","created_at":"2026-05-28T19:33:59.596803+00:00","dataset_ids":["ds_finance_gold"],"job_id":null,"member_id":"mem_demo_active_1","metadata":{"dataset_title":"Curated Finance Signals","object_uri":"s3://defendable-datasets/finance/gold"},"receipt_id":"rcpt_example","receipt_type":"dataset_access"}
```

## Actions That Emit Receipts

- `POST /members/{member_id}/activate`
- `POST /datasets/{dataset_id}/access`
- `POST /compute/quote`
- `POST /jobs`
- `POST /jobs/{job_id}/complete`

## Later Hardening

v0.1 receipts are local JSONL. Next hardening steps:

1. Add a receipt verification CLI command.
2. Export receipts to object storage.
3. Batch receipts into Merkle roots.
4. Anchor Merkle roots to DefendableOS or another ledger layer.
5. Add immutable retention policies.
6. Reconcile compute receipts with Stripe invoices and provider costs.

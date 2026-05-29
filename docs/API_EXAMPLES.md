# API Examples

These examples assume:

- API base URL: `http://localhost:8088`
- Local database initialized with `defendable-router init-db`
- Demo data seeded with `defendable-router seed-demo`

Start the server:

```bash
uvicorn defendable_router.main:app --host 0.0.0.0 --port 8088 --reload
```

## Health

```bash
curl http://localhost:8088/health
```

Expected shape:

```json
{"status":"healthy","service":"DefendableRouter","version":"0.1.0","db_status":"ok","timestamp":"2026-05-28T19:33:59.596803+00:00"}
```

## Admin Summary

```bash
curl http://localhost:8088/admin/summary
```

Expected keys:

```json
{"active_members_count":2,"total_datasets_count":5,"compute_nodes_available":2,"compute_nodes_busy":0,"queued_jobs":0,"running_jobs":0,"completed_jobs":0,"estimated_revenue_from_jobs":0.0,"annual_membership_revenue":200.0}
```

## Members

Create a member:

```bash
curl -X POST http://localhost:8088/members   -H 'content-type: application/json'   -d '{"email":"new-member@example.com","name":"New Member"}'
```

Activate a member:

```bash
curl -X POST http://localhost:8088/members/MEMBER_ID_FROM_CREATE_RESPONSE/activate
```

Read demo member status:

```bash
curl http://localhost:8088/members/mem_demo_active_1/status
```

Read inactive demo member status:

```bash
curl http://localhost:8088/members/mem_demo_inactive_1/status
```

## Datasets

List datasets:

```bash
curl 'http://localhost:8088/datasets?limit=10&offset=0'
```

Filter by domain:

```bash
curl 'http://localhost:8088/datasets?domain=finance&limit=10&offset=0'
```

Filter by quality tier:

```bash
curl 'http://localhost:8088/datasets?quality_tier=royal_jelly&limit=10&offset=0'
```

Read dataset metadata:

```bash
curl http://localhost:8088/datasets/ds_finance_gold
```

Create a dataset registry entry:

```bash
curl -X POST http://localhost:8088/datasets   -H 'content-type: application/json'   -d '{"id":"ds_demo_new","title":"Demo New Dataset","domain":"demo","description":"A locally registered demo dataset.","object_uri":"s3://defendable-datasets/demo/new","license_type":"member","quality_tier":"gold","checksum_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","size_bytes":1024,"row_count":100,"is_member_access":true}'
```

Access dataset with active member:

```bash
curl -X POST http://localhost:8088/datasets/ds_finance_gold/access   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1"}'
```

Access dataset with inactive member. This should return `403`:

```bash
curl -i -X POST http://localhost:8088/datasets/ds_finance_gold/access   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_inactive_1"}'
```

## Compute

List inventory:

```bash
curl http://localhost:8088/compute/inventory
```

Register a compute node:

```bash
curl -X POST http://localhost:8088/compute/register-node   -H 'content-type: application/json'   -d '{"hostname":"lab-5090-02","gpu_type":"rog_astral_5090_32gb","max_concurrent_jobs":1,"tags":["lab","demo"]}'
```

Quote RTX PRO 6000 Blackwell Workstation 96GB for 2 hours:

```bash
curl -X POST http://localhost:8088/compute/quote   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","requested_gpu_sku":"rtx6000_blackwell_96gb","estimated_hours":2,"job_type":"fine_tune"}'
```

Quote ASUS ROG Astral RTX 5090 32GB for 3 hours:

```bash
curl -X POST http://localhost:8088/compute/quote   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","requested_gpu_sku":"rog_astral_5090_32gb","estimated_hours":3,"job_type":"inference"}'
```

Quote with inactive member. This should return `403`:

```bash
curl -i -X POST http://localhost:8088/compute/quote   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_inactive_1","requested_gpu_sku":"rtx6000_blackwell_96gb","estimated_hours":2,"job_type":"fine_tune"}'
```

## Jobs

Create a fine-tune job:

```bash
curl -X POST http://localhost:8088/jobs   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","job_type":"fine_tune","requested_gpu_sku":"rtx6000_blackwell_96gb","estimated_hours":2.5,"input_dataset_ids":["ds_finance_gold"],"output_uri":"s3://defendable-runs/demo/fine-tune-001"}'
```

Create an inference job:

```bash
curl -X POST http://localhost:8088/jobs   -H 'content-type: application/json'   -d '{"member_id":"mem_demo_active_1","job_type":"inference","requested_gpu_sku":"rog_astral_5090_32gb","estimated_hours":1,"input_dataset_ids":["ds_finance_gold"],"output_uri":"s3://defendable-runs/demo/inference-001"}'
```

Read a job:

```bash
curl http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE
```

Start a queued job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/start
```

Complete a job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/complete
```

Cancel a job:

```bash
curl -X POST http://localhost:8088/jobs/JOB_ID_FROM_CREATE_RESPONSE/cancel
```

## Receipt Inspection

Receipts are appended locally:

```bash
ls data/receipts
```

Read the latest ledger file:

```bash
tail -n 5 data/receipts/$(date +%F).receipts.jsonl
```

# DefendableWorker Contract

DefendableWorker is the owned-rig agent contract for DefendableRouter v0.2.

DefendableRouter remains the public control plane. DefendableWorker runs on private GPU rigs, calls home to the router, leases queued jobs, executes local work later, and reports status, logs, artifacts, and final state.

v0.2 builds the contract only. It does not execute GPU training jobs.

## Lifecycle

```text
Worker starts on owned rig
-> POST /workers/register
-> store plaintext token locally
-> POST /workers/heartbeat
-> POST /workers/jobs/lease
-> POST /workers/jobs/{job_id}/accept
-> POST status/log/artifact updates
-> POST complete or fail
```

The router does not need inbound network access to private rigs. Workers initiate outbound HTTPS calls to the router.

## Auth Model

Worker API endpoints use bearer tokens:

```text
Authorization: Bearer <worker_token>
```

Registration returns the plaintext worker token once. DefendableRouter stores only `auth_token_hash` in the database.

Lease tokens are separate from worker tokens. A worker token authenticates the rig. A lease token authorizes actions on a specific leased job.

Security notes:

- Never log plaintext worker tokens.
- Never store plaintext worker tokens in the router database.
- Rotate worker tokens later with a dedicated endpoint.
- Put production worker traffic behind HTTPS only.
- Use admin route auth before exposing this publicly.

## Worker Registration

```bash
curl -X POST http://localhost:8088/workers/register   -H 'content-type: application/json'   -d '{"node_id":"node_smash_5090_01","name":"Smash RTX 5090 Worker","hostname":"smash-5090-01","endpoint_url":null,"capabilities":{"gpu_skus":["rog_astral_5090_32gb"],"gpu_count":1,"vram_gb_total":32,"cuda_version":"13.1","driver_version":"590.48.01","supports":["inference","fine_tune","eval","dataset_build","embedding"],"max_concurrent_jobs":1,"storage_gb_available":430,"models_available":["katniss-9b:latest","swarmjelly-4b:latest"],"runtime":{"ollama":true,"vllm":false,"docker":true}},"tags":["owned-rig","rtx5090","ollama"],"version":"0.2.0"}'
```

Response:

```json
{"worker_id":"worker_...","worker_token":"dwrk_...","status":"registered"}
```

Store `worker_token` on the worker host. It is not recoverable from the router.

## Heartbeat Contract

```bash
curl -X POST http://localhost:8088/workers/heartbeat   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"status":"online","current_jobs":0,"metrics":{"gpu_util_pct":0,"gpu_temp_c":45,"gpu_mem_used_mb":580,"gpu_mem_total_mb":32607,"disk_free_gb":430}}'
```

Response:

```json
{"ok":true,"worker_id":"worker_...","server_time":"2026-05-28T20:00:00Z","next_heartbeat_seconds":30}
```

If `capabilities` is included, the router refreshes the worker capability JSON. The router also updates a linked compute node when it can match by `node_id` or hostname.

## Lease Contract

Workers ask for matching queued jobs:

```bash
curl -X POST http://localhost:8088/workers/jobs/lease   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"supported_job_types":["fine_tune","eval","inference"],"supported_gpu_skus":["rog_astral_5090_32gb"],"max_jobs":1}'
```

If a job is available:

```json
{"lease_id":"lease_...","lease_token":"dlease_...","job":{"id":"job_...","job_type":"fine_tune","requested_gpu_sku":"rog_astral_5090_32gb","estimated_hours":2.5,"input_dataset_ids":["ds_finance_gold"]},"expires_at":"2026-05-28T20:10:00Z","message":null}
```

If no job matches:

```json
{"lease_id":null,"lease_token":null,"job":null,"expires_at":null,"message":"no_matching_jobs"}
```

Default lease duration is 10 minutes. Expired active leases are returned to the queued state by `expire_stale_leases` or the CLI command:

```bash
defendable-router expire-leases
```

## Job Status Lifecycle

Job statuses:

- `queued`
- `leased`
- `running`
- `completed`
- `failed`
- `canceled`

Accept a lease:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/accept   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN"}'
```

Send progress:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/status   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN","event_type":"progress","message":"fine-tune epoch 1 complete","payload":{"progress_pct":20,"tokens_seen":1000000,"loss":1.89}}'
```

Complete:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/complete   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN","output_uri":"s3://defendable-artifacts/jobs/job_x/output","metrics":{"duration_seconds":3600,"tokens_processed":10000000},"final_message":"job completed"}'
```

Fail:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/fail   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN","error_code":"OOM","message":"CUDA out of memory","payload":{}}'
```

v0.2 does not charge a final actual cost for failed jobs unless future partial billing support is added.

## Logs and Artifacts

Short log chunks:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/logs   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN","message":"training log line","payload":{"stream":"stdout"}}'
```

Artifact report:

```bash
curl -X POST http://localhost:8088/workers/jobs/JOB_ID/artifacts   -H 'authorization: Bearer WORKER_TOKEN'   -H 'content-type: application/json'   -d '{"lease_token":"LEASE_TOKEN","artifact_type":"model","name":"atlas-cre-lora-v1","uri":"s3://defendable-artifacts/jobs/job_x/output","checksum_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","size_bytes":123456,"metadata":{}}'
```

v0.2 stores short log events in the database. Long logs and artifacts should go to object storage, with only URI/checksum/metadata stored in DefendableRouter.

## Admin and CLI

Admin endpoints:

```bash
curl http://localhost:8088/admin/workers
curl http://localhost:8088/admin/workers/WORKER_ID
curl http://localhost:8088/admin/summary
```

CLI:

```bash
defendable-router list-workers
defendable-router worker-summary
defendable-router expire-leases
defendable-router mark-stale-workers
```

## Future DefendableWorker Agent Plan

1. Worker daemon with local config and token storage.
2. Hardware/capability detector for NVIDIA, Docker, Ollama, vLLM, disk, and models.
3. Heartbeat loop.
4. Lease polling loop.
5. Local job executor adapters.
6. Log/artifact uploader.
7. Retry and shutdown/drain behavior.
8. Token rotation.
9. Signed artifact manifests and receipt handoff.

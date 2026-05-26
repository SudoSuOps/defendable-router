# Public URL Test Results

Date: 2026-05-26

## Router

- `GET https://defendablerouter.com/` → `HTTP 200`
  - title: `DefendableRouter · Field Integration Pending`
  - description aligned to public-positioning/local-source status
- `GET https://defendablerouter.com/llms.txt` → `HTTP 200`
  - contains `FIELD INTEGRATION PENDING`
  - contains `NOT_YET_INTEGRATED`
  - contains `PUBLIC DEPLOYED ROUTER UTILITY NOT VERIFIED`

## Docs

- `GET https://defendabledocs.com/field-release/overview/` → reachable
- `GET https://defendabledocs.com/defendablerouter/overview/` → reachable
  - contains `NOT YET VERIFIED`
  - contains `FIELD INTEGRATION PENDING`
  - contains `roadmap and local-source documentation`
- `GET https://defendabledocs.com/api/router-api/` → reachable

## Cloud

- `GET https://defendablecloud.com/agent-operations-demo` → reachable
- `GET https://defendablecloud.com/api/demo/agent-operations/roster` → `HTTP 200`
- `GET https://defendablecloud.com/api/demo/agent-operations/evidence` → `HTTP 200`
- `GET https://defendablecloud.com/api/demo/agent-operations/action-log` → `HTTP 200`
- `POST https://defendablecloud.com/api/demo/agent-operations/actions/classify-ticket` → `HTTP 200` · `ALLOW_AND_EXECUTE_LOCAL_MOCK`
- `POST https://defendablecloud.com/api/demo/agent-operations/actions/draft-response` → `HTTP 200` · `ALLOW_AND_EXECUTE_LOCAL_MOCK` · `draft_only: true`
- `POST https://defendablecloud.com/api/demo/agent-operations/actions/issue-refund` → `HTTP 200` · `DENY_ACTION_NOT_IN_PERMISSION_ENVELOPE` · `executed: false`
- `POST https://defendablecloud.com/api/demo/agent-operations/actions/request-refund-review` → `HTTP 200` · `QUEUE_FOR_HUMAN_APPROVAL`

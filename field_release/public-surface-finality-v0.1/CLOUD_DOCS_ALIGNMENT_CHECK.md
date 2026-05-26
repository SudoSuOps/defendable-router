# Cloud + Docs Alignment Check

## DefendableCloud

No source changes were required in `defendable-cloud`.

Public checks confirmed:

- `GET /api/demo/agent-operations/roster` returned `HTTP 200`
- `GET /api/demo/agent-operations/evidence` returned `HTTP 200`
- `GET /api/demo/agent-operations/action-log` returned `HTTP 200`
- `POST /actions/classify-ticket` returned allow/execute mock
- `POST /actions/draft-response` returned allow/execute mock with `draft_only: true`
- `POST /actions/issue-refund` returned deny with `executed: false`, `real_refund_executed: false`, `external_enforcement_claimed: false`
- `POST /actions/request-refund-review` returned queue-for-human-approval with no sensitive execution

Router alignment on Cloud:

- accepted live Cloud demo remains a server-side synthetic Pages Functions flow
- Router is not claimed as part of the live Cloud path
- production and external SaaS enforcement are not claimed

## DefendableDocs

Docs files changed:

- `src/content/docs/defendablerouter/overview.md`
- `src/content/docs/defendablerouter/api-contracts.md`
- `src/content/docs/defendablerouter/receipt-capture.md`
- `src/content/docs/defendablerouter/routing-model.md`
- `src/content/docs/defendablerouter/edge-events.md`
- `src/content/docs/defendablerouter/ens-app-agent-id.md`
- `src/content/docs/defendablerouter/object-storage-flow.md`
- `src/content/docs/api/router-api.md`

Public checks confirmed:

- Router overview page live with `NOT YET VERIFIED` and `FIELD INTEGRATION PENDING`
- Router API page now framed as not publicly verified deployed API
- Field-release overview remains reachable

Client-use alignment retained:

- Docs still route users to the field-release pages
- Router detail pages now describe roadmap/local-source status instead of presenting live utility by default

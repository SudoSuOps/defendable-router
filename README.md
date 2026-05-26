# DefendableRouter

> **STATUS (Codex deployed-utility finding F4 — 2026-05):**
> DefendableRouter is currently a **public positioning surface with local source-level
> receipt-spine work**. A public deployed router middleware utility and any DefendableCloud demo
> integration are **NOT YET VERIFIED** and remain **ROADMAP / FIELD INTEGRATION PENDING** until a
> public endpoint or Cloud path is deployed and independently audited. It is **not** part of the
> live DefendableCloud demo path. Claims about deployed middleware behavior, receipt creation for
> every routed public call, write-only behavior, latency, ENS-signed receipts, reconciliation
> deeds, or carrier/insurance posture are **design intent — not verified, not production-cleared,
> and not externally enforced**. The `spine/` directory is
> **LOCAL SOURCE DEMO / NOT A PUBLIC DEPLOYED UTILITY**.

> Field integration pending.

Public positioning site plus local source demo for the Router track. Use this repo to inspect source, follow the audit tape, and understand the current limitation boundary. *(Design intent and roadmap concepts remain below, but are not verified public deployed behavior.)*

A surface of [DefendableOS](https://defendableos.com).

## What this repo is today

The **public status surface** (`defendablerouter.com`) — single-page React app, Vite + Tailwind, now centered on current audited truth and limitation labels.

The **local source demo** (`spine/`) — inspectable code and tests for receipt-spine work.

The **actual public deployed router middleware** is **not yet independently verified**.

## Deployment modes

- **EDGE** — roadmap concept
- **CLOUD** — roadmap concept
- **HYBRID** — roadmap concept

These modes describe intended architecture only. They are not accepted as publicly verified deployed behavior.

## ENS bridge

ENS-linked receipt identity remains roadmap/design-intent material, not accepted public deployed proof.

## Pricing

- **OSS / local source demo** — current public source lane
- **Receipts / audit pipeline** — roadmap/business lane, not public deployed Router proof
- **Insurance** — not claimed as currently verified public capability

## Develop

```bash
npm install
npm run dev          # http://localhost:5176
npm run build        # → dist/
npm run typecheck
```

## Deploy

Cloudflare Pages connected to this repo. Build command `npm run build`. Output dir `dist`. SPA fallback wired via `public/_redirects`.

## Operator

Swarm and Bee LLC · DBA Swarm & Bee AI · Florida · D-U-N-S 138652395

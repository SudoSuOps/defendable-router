# DefendableRouter

> **STATUS (Codex deployed-utility finding F4 — 2026-05):**
> DefendableRouter is currently a **public positioning surface with local source-level
> receipt-spine work**. A public deployed router middleware utility and any DefendableCloud demo
> integration are **NOT YET VERIFIED** and remain **ROADMAP / FIELD INTEGRATION PENDING** until a
> public endpoint or Cloud path is deployed and independently audited. It is **not** part of the
> live DefendableCloud demo path. The operational claims below (drop-in middleware today, a
> receipt for every routed call, write-only, sub-5ms overhead, ENS-signed receipts, daily
> Reconciliation Deed, carrier/insurance-ready evidence) are **design intent — not verified, not
> production-cleared, and not externally enforced**. The `spine/` directory is
> **LOCAL SOURCE DEMO / NOT A PUBLIC DEPLOYED UTILITY**.

> We cracked the router. OpenWrt for AI agents.

Drop-in middleware that sits between your AI agent and any LLM provider, writes a SHA-256 receipt for every call, and ships it to the audit pipeline. Write-only. Sub-5ms POST overhead. Free OSS install. *(Design intent — see STATUS above; not verified or production-cleared.)*

A surface of [DefendableOS](https://defendableos.com).

## What this repo is

The **marketing surface** (defendablerouter.com) — single-page React app, Vite + Tailwind, dual-voice (hacker-energy headline + commercial-grade depth).

The **actual router middleware** ships separately. Watch this org for the binary release.

## Deployment modes

- **EDGE** — runs on a HoneyBox appliance on customer premises (regulated industries · raw data never leaves)
- **CLOUD** — runs in your own cloud (Docker · k8s · Python SDK · nginx sidecar)
- **HYBRID** — router in cloud, receipts catch on-prem HoneyBox

DefendableHQ NEVER sits in the call path · we are the Bakery (receipt sink + grading), not the proxy.

## ENS bridge

Every receipt is signed with a per-agent ENS subdomain (`agent-id.operator.defendable.eth`) · daily Reconciliation Deed inherits the cryptographic lineage.

## Pricing

- **OSS** · $0 forever · MIT-with-receipt-clause · self-hosted
- **Receipts** · pay per million · audit pipeline + Tribunal + deeds
- **Insurance** · priced per engagement · carrier-ready evidence pack

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

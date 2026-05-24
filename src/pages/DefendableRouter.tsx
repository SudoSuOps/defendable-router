// DefendableRouter · we cracked the router · OpenWrt for AI agents
//
// Single deep scrolling product surface for defendablerouter.com. Drop-in
// middleware that intercepts AI agent traffic and writes receipts. Free
// OSS install · paid receipts/grading/insurance baseline.
//
// Dual-voice: hacker-energy headlines (cracked the router · OpenWrt for
// AI agents · the audit gap your stack ignores) + commercial-grade depth
// (CFO pain · insurance angle · receipts you can show your carrier).
//
// Terminal aesthetic for code blocks · bigger GitHub presence than the
// other brand surfaces. Cross-links to defendableos.com (mothership) and
// defendablecloud.com (sister product · hosted inference).

const SALES_EMAIL = "build@defendableos.com";
const X_URL = "https://x.com/swarmandbee";
const LINKEDIN_URL = "https://www.linkedin.com/in/donovan-mackey-89a6063b6/";
const GITHUB_ORG_URL = "https://github.com/SudoSuOps";
const GITHUB_REPO_URL = "https://github.com/SudoSuOps/defendable-router";
const DEFENDABLEOS_URL = "https://defendableos.com";
const DEFENDABLECLOUD_URL = "https://defendablecloud.com";
const DOCS_URL = "https://docs.defendableos.com";

const MAILTO_ACCESS = `mailto:${SALES_EMAIL}?subject=${encodeURIComponent(
  "DefendableRouter · request audit pipeline access",
)}&body=${encodeURIComponent(
  "Hi DefendableRouter — \n\nDeployment mode (circle):  Self-hosted OSS (no help)  /  Receipts-tier (pay for grading)  /  Insurance baseline (carrier-ready)\n\nAgent stack (LangChain / LlamaIndex / OpenAI SDK / Anthropic SDK / vLLM / Custom):\n\nDaily call volume (estimate):\n\nCompliance posture needed (HIPAA / GDPR / SOC2 / none):\n\nName / company:\n",
)}`;

const MAILTO_INSURANCE = `mailto:${SALES_EMAIL}?subject=${encodeURIComponent(
  "DefendableRouter · insurance baseline intake",
)}&body=${encodeURIComponent(
  "Hi DefendableRouter — I want my agent traffic underwritten.\n\nCarrier (if known):\nAgent class (refund / support / underwriting / code / other):\nDaily play volume:\nCurrent audit setup (none / logs / Datadog / LangSmith / other):\n\nName / company:\n",
)}`;

export default function DefendableRouter() {
  return (
    <div className="min-h-screen bg-neutral-950 text-stone-200 antialiased selection:bg-amber-500/30 selection:text-amber-100">
      <Header />
      <main>
        <Hero />
        <ProblemBand />
        <WhatItIs />
        <LiveEngineBand />
        <Architecture />
        <DeploymentModes />
        <EnsBridge />
        <Install />
        <CodeSamples />
        <HoneyBoxPairing />
        <FiveProofs />
        <Pricing />
        <Compare />
        <Insurance />
        <GithubBlock />
        <Faq />
        <CtaContact />
      </main>
      <Footer />
      <JsonLd />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Header
// ─────────────────────────────────────────────────────────────────────────
function Header() {
  const navItems: [string, string][] = [
    ["What", "#what"],
    ["Modes", "#modes"],
    ["ENS", "#ens"],
    ["Install", "#install"],
    ["HoneyBox", "#honeybox"],
    ["Pricing", "#pricing"],
    ["GitHub", "#github"],
  ];
  return (
    <header className="sticky top-0 z-30 border-b border-amber-500/20 bg-neutral-950/85 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 group">
          <span className="font-mono text-amber-400 text-base">_</span>
          <span className="font-semibold tracking-tight text-stone-100">
            Defendable<span className="text-amber-300">Router</span>
          </span>
          <span className="ml-2 text-[9px] uppercase tracking-[0.2em] text-stone-500 hidden sm:inline">
            we cracked the router
          </span>
        </a>
        <nav className="hidden md:flex items-center gap-5 text-xs uppercase tracking-[0.18em] text-stone-400">
          {navItems.map(([label, href]) => (
            <a key={href} href={href} className="hover:text-amber-300 transition-colors">
              {label}
            </a>
          ))}
        </nav>
        <a
          href={GITHUB_REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs uppercase tracking-[0.18em] rounded border border-amber-500/40 text-amber-300 px-3 py-1.5 hover:bg-amber-500/10 transition-colors flex items-center gap-2"
        >
          <GithubIcon />
          ★ Star
        </a>
      </div>
    </header>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hero · cracked-hacker energy
// ─────────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <section className="border-b border-stone-900 relative overflow-hidden">
      <TerminalBg />
      <div className="relative max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ DROP-IN MIDDLEWARE · WRITE-ONLY · &lt;5MS POST · FREE OSS
        </div>
        <h1 className="mt-6 text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight text-stone-50 leading-[1.05] max-w-4xl">
          We <span className="font-serif italic font-normal text-amber-300">cracked</span> the router.
        </h1>
        <p className="mt-6 text-2xl md:text-3xl text-stone-300 font-serif italic max-w-3xl leading-tight">
          OpenWrt for AI agents.
        </p>
        <p className="mt-8 text-lg text-stone-300 leading-relaxed max-w-3xl">
          Your agents are calling LLMs. Right now. With{" "}
          <span className="text-stone-100">zero audit trail</span>. DefendableRouter
          is the drop-in middleware that sits between your agent and any
          model (cloud or local), writes a SHA-256 receipt for every call,
          and ships it to the audit pipeline · without slowing the agent
          down. Write-only. Non-blocking. Sub-5ms POST. Free to install.
        </p>

        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-px bg-stone-900 border border-stone-900">
          <Stat n="<5ms" label="POST latency" />
          <Stat n="0" label="blocking calls" />
          <Stat n="FREE" label="OSS install" />
          <Stat n="any" label="LLM provider" />
        </div>

        <div className="mt-10 flex flex-wrap gap-3">
          <a
            href="#install"
            className="rounded border border-amber-500 bg-amber-500/10 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/20 transition-colors font-mono"
          >
            $ install
          </a>
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-stone-700 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors flex items-center gap-2"
          >
            <GithubIcon /> View on GitHub
          </a>
          <a
            href={MAILTO_ACCESS}
            className="rounded border border-stone-700 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
          >
            Audit pipeline access
          </a>
        </div>

        <p className="mt-10 text-xs text-stone-500 italic font-serif leading-relaxed max-w-2xl">
          "Your CFO is going to ask which agent spent $40,000 on tokens
          last quarter. Right now you can't answer. DefendableRouter is
          how you answer."
        </p>
      </div>
    </section>
  );
}

function TerminalBg() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.03]"
      style={{
        backgroundImage:
          "linear-gradient(rgba(230,171,42,1) 1px, transparent 1px), linear-gradient(90deg, rgba(230,171,42,1) 1px, transparent 1px)",
        backgroundSize: "32px 32px",
      }}
    />
  );
}

function Stat({ n, label }: { n: string; label: string }) {
  return (
    <div className="bg-neutral-950 px-5 py-6">
      <div className="text-2xl md:text-3xl font-semibold tracking-tight text-stone-50 tabular-nums font-mono">
        {n}
      </div>
      <div className="mt-1 text-[10px] uppercase tracking-[0.22em] text-stone-500">{label}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Problem band · the audit gap
// ─────────────────────────────────────────────────────────────────────────
function ProblemBand() {
  return (
    <section className="border-b border-stone-900 bg-amber-500/[0.02]">
      <div className="max-w-6xl mx-auto px-6 py-16 lg:py-20">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          THE PROBLEM
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          The audit gap your stack{" "}
          <span className="font-serif italic font-normal text-amber-300">pretends</span>{" "}
          doesn't exist.
        </h2>
        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <ProblemTile
            title="Your CFO can't sleep"
            body="An agent burned $40K in OpenAI tokens last quarter. Which agent? Which task? Who called it? Your logs don't say · your bill doesn't tell · your engineers shrug."
          />
          <ProblemTile
            title="Your insurance can't price"
            body="Carriers can't underwrite agent risk if they can't see agent behavior. No receipts means no baseline means no policy. You're self-insuring whether you know it or not."
          />
          <ProblemTile
            title="Your compliance can't sign"
            body="HIPAA, GDPR, SOC2 all want an audit trail. Your agent stack has logs you control with retention you set. None of that is what auditors mean by audit trail."
          />
        </div>
      </div>
    </section>
  );
}

function ProblemTile({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-6">
      <h3 className="text-lg font-semibold tracking-tight text-stone-50">{title}</h3>
      <p className="mt-3 text-sm text-stone-400 leading-relaxed">{body}</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Live Engine band · point at the actual in-house swarmrouter
// ─────────────────────────────────────────────────────────────────────────
function LiveEngineBand() {
  return (
    <section className="border-b border-amber-500/20 bg-amber-500/[0.03]">
      <div className="max-w-6xl mx-auto px-6 py-16 lg:py-20">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          BUILT ON SWARMROUTER · LIVE IN-HOUSE ENGINE · 3-4B ROUTING BRAIN
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          The OSS install is the wedge.{" "}
          <span className="font-serif italic font-normal text-amber-300">The trained brain</span> is{" "}
          already routing in production.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          DefendableRouter (this page · the cracked-router OSS install) is the
          public surface. The actual production routing brain is{" "}
          <a href="https://router.swarmandbee.com" target="_blank" rel="noopener noreferrer" className="text-amber-300 hover:text-amber-200">
            router.swarmandbee.com
          </a>
          {" "}— a 3-4B-parameter Qwen2.5-3B-Instruct fine-tune (QLoRA r=32)
          trained on 60,000 routing examples, deployed inside a Cloudflare
          Worker with 19 AI skills · 50 state experts · event machine ·
          semantic memory. It makes routing decisions in &lt;100ms.
        </p>

        <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-4 gap-px bg-stone-900 border border-stone-900 rounded-xl overflow-hidden">
          <div className="bg-neutral-950 p-5">
            <div className="text-2xl font-semibold tracking-tight text-amber-300 tabular-nums font-mono">3-4B</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.22em] text-stone-300">Routing brain params</div>
            <div className="mt-0.5 text-[10px] text-stone-500">Qwen2.5-3B-Instruct base</div>
          </div>
          <div className="bg-neutral-950 p-5">
            <div className="text-2xl font-semibold tracking-tight text-amber-300 tabular-nums font-mono">60K</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.22em] text-stone-300">Training examples</div>
            <div className="mt-0.5 text-[10px] text-stone-500">QLoRA r=32 · cooked in-house</div>
          </div>
          <div className="bg-neutral-950 p-5">
            <div className="text-2xl font-semibold tracking-tight text-amber-300 tabular-nums font-mono">&lt;100ms</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.22em] text-stone-300">Routing decision latency</div>
            <div className="mt-0.5 text-[10px] text-stone-500">Single forward pass</div>
          </div>
          <div className="bg-neutral-950 p-5">
            <div className="text-2xl font-semibold tracking-tight text-amber-300 tabular-nums font-mono">19 + 50</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.22em] text-stone-300">AI skills + state experts</div>
            <div className="mt-0.5 text-[10px] text-stone-500">Cloudflare Worker · live</div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="https://router.swarmandbee.com"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-amber-500 bg-amber-500/10 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/20 transition-colors font-mono"
          >
            $ curl router.swarmandbee.com ↗
          </a>
          <a
            href="https://swarmandbee.ai/chain"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-stone-700 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
          >
            Watch the refinery work ↗
          </a>
        </div>

        <p className="mt-8 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          The router you install (this page) and the routing brain we operate
          (router.swarmandbee.com) speak the same protocol. Self-host the OSS ·
          point at our trained brain · or wire your own routing logic against
          the same receipt schema. "Validate the Validator. Prove the Location."
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// The 5 Proofs · what every receipt + deed carries
// ─────────────────────────────────────────────────────────────────────────
function FiveProofs() {
  const proofs = [
    { n: "I",   title: "Proof of Origin",     body: "Which model · which node · which hardware · which strategy. Full attribution via ENS-anchored agent identity. No mystery." },
    { n: "II",  title: "Proof of Quality",    body: "Deterministic verification · not model opinion. JellyScore 5-component formula · 6 gates + 7th adversarial source-at-fault." },
    { n: "III", title: "Proof of Process",    body: "Full lineage · what was tried · what failed · what survived. HoneyCard factory_path: Bee → Curator → Honey → Queen." },
    { n: "IV",  title: "Proof of Economics",  body: "Energy cost per call · tokens · wire-time · cost-per-Honey trend. The CFO line item, on-chain, per receipt." },
    { n: "V",   title: "Proof of Trust",      body: "Hedera HCS anchor (topic 0.0.10291838) · Merkle root · cell-level PoSg certificates. Verifiable by anyone, forever." },
  ];
  return (
    <section className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          THE 5 PROOFS · WHAT EVERY RECEIPT CARRIES · LIVE ON HEDERA
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Five proofs.{" "}
          <span className="font-serif italic font-normal text-amber-300">No asterisks.</span>
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          Anyone can sell rows. We sell{" "}
          <span className="text-stone-200">defendable inventory</span>. Every
          receipt the router fires — and every deed those receipts roll up into
          — carries all five proofs. Anchored on the public Hedera HCS topic ·
          verifiable by anyone with a Hedera explorer · indefinite retention.
        </p>

        <div className="mt-10 grid md:grid-cols-2 lg:grid-cols-5 gap-px bg-stone-900 border border-stone-900 rounded-xl overflow-hidden">
          {proofs.map((p) => (
            <div key={p.n} className="bg-neutral-950 p-5">
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/70 font-semibold font-mono">
                PROOF {p.n}
              </div>
              <h3 className="mt-3 text-sm font-semibold tracking-tight text-stone-100">
                {p.title}
              </h3>
              <p className="mt-2 text-xs text-stone-400 leading-relaxed">{p.body}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="https://hashscan.io/#/mainnet/topic/0.0.10291838"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-amber-500/40 px-4 py-2 text-xs uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/10 transition-colors font-mono"
          >
            Verify on Hedera ↗
          </a>
          <a
            href="https://swarmandbee.ai/deed"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-stone-700 px-4 py-2 text-xs uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
          >
            The Deed Office ↗
          </a>
          <a
            href="https://swarmandbee.ai/graph"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-stone-700 px-4 py-2 text-xs uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
          >
            Provenance graph ↗
          </a>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// What it is
// ─────────────────────────────────────────────────────────────────────────
function WhatItIs() {
  const props = [
    { eyebrow: "WRITE-ONLY", title: "Never blocks the agent", body: "Your agent calls the LLM. Router forwards the call. Returns the answer. Then asynchronously POSTs the receipt to the audit pipeline. The agent never waits on us. <5ms wire-time overhead." },
    { eyebrow: "ANY PROVIDER", title: "Works with what you already use", body: "OpenAI · Anthropic · Mistral · OpenRouter · vLLM · llama.cpp · DefendableCloud · Ollama · LM Studio · your custom endpoint. We're a transparent proxy. Same API · same SDK · same model strings." },
    { eyebrow: "FREE TO INSTALL", title: "Install costs nothing", body: "OSS · MIT-with-receipt-clause license · self-hosted Docker / Python sidecar / nginx module. You can run it forever without paying us. The wedge is the wedge." },
    { eyebrow: "PAID AUDIT PIPELINE", title: "Optional revenue tier", body: "When you point the receipts at our Bakery vault for grading, deed issuance, and insurance baseline · then you're a customer. You don't have to. Most won't. Some will." },
  ];
  return (
    <section id="what" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ WHAT IT IS
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          A drop-in middleware ·{" "}
          <span className="font-serif italic font-normal text-amber-300">with the wires we left in</span>.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          DefendableRouter is what happens when you take a regular AI
          gateway, rip out the parts that slow your agent down, and bolt
          on the parts that make your CFO and insurance carrier happy.
          OpenWrt-energy: the firmware most vendors won't ship · because
          the parts they leave OUT are what their margin depends on.
        </p>

        <div className="mt-12 grid md:grid-cols-2 gap-6">
          {props.map((p) => (
            <div key={p.title} className="rounded-xl border border-stone-800 bg-neutral-950/60 p-6">
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">{p.eyebrow}</div>
              <h3 className="mt-3 text-xl font-semibold tracking-tight text-stone-50">{p.title}</h3>
              <p className="mt-3 text-sm text-stone-400 leading-relaxed">{p.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Architecture · ASCII diagram
// ─────────────────────────────────────────────────────────────────────────
function Architecture() {
  const ascii = `┌──────────────────────┐                  ┌─────────────────────┐
│                      │   1. forward     │                     │
│   YOUR AI AGENT      │ ───────────────► │  ANY LLM PROVIDER   │
│   (LangChain /       │                  │  (OpenAI /          │
│    LlamaIndex /      │ ◄─────────────── │   Anthropic /       │
│    OpenAI SDK /      │   2. response    │   vLLM / local /    │
│    your code)        │                  │   DefendableCloud)  │
└──────────┬───────────┘                  └─────────────────────┘
           │
           │ (transparent proxy · same API · zero rewrites)
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              DEFENDABLEROUTER · WRITE-ONLY · <5MS               │
│                                                                 │
│   • timestamp · agent_id · task_class · model · token counts    │
│   • SHA-256 record_hash · ENS subdomain tag                     │
│   • NO PROMPT BODIES SENT (unless you opt in per call)          │
└──────────┬───────────────────────────────┬──────────────────────┘
           │                               │
           │ 3a. fire-and-forget POST      │ 3b. (optional)
           │     (always · async)          │     local sink
           ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│  BAKERY VAULT            │    │  HONEYBOX (edge appliance)   │
│  (Tigris-backed durable  │    │  raw data never leaves       │
│   storage · forever)     │    │  per-agent ledger on-device  │
│                          │    │  (data residency wedge)      │
│  → Nightly reconciliation│    │                              │
│  → Tribunal grading      │    └──────────────────────────────┘
│  → Daily DDEED-DOV-AGENT │
│  → Morning brief 06:00   │
└──────────────────────────┘`;

  return (
    <section className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          ARCHITECTURE · TRANSPARENT PROXY + ASYNC RECEIPT SINK
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          One process.{" "}
          <span className="font-serif italic font-normal text-amber-300">Two paths.</span>{" "}
          Zero blocking.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          The agent path is synchronous and dumb-fast. The receipt path
          is async and never on the critical loop. You get audit without
          paying latency tax.
        </p>

        <div className="mt-10 rounded-xl border border-stone-800 bg-black overflow-hidden">
          <div className="px-4 py-2 border-b border-stone-800 text-[10px] uppercase tracking-[0.22em] text-stone-500 bg-neutral-950 font-mono">
            $ defendable-router --topology
          </div>
          <pre className="px-4 py-5 overflow-x-auto text-[11px] leading-snug text-amber-200/90 font-mono">
            <code>{ascii}</code>
          </pre>
        </div>

        <p className="mt-6 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          The receipt does NOT include prompt bodies by default · only the
          metadata signature. Opt-in per call via{" "}
          <code className="font-mono text-amber-300">X-Defendable-Include-Body: 1</code>{" "}
          when you want full evidence for a specific run (regulated
          industries use this for sample audits).
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Deployment modes · where the router runs
// ─────────────────────────────────────────────────────────────────────────
function DeploymentModes() {
  const modes = [
    {
      tag: "EDGE",
      title: "On a HoneyBox · customer premises",
      tagline: "Raw data never leaves the building.",
      runs: "HoneyBox appliance ($249-$2K Jetson Orin Nano)",
      sink: "HoneyBox local SQLite + per-agent ledger",
      use: "Regulated industries · healthcare · finance · gov · defense · legal · imaging centers",
      pro: ["100% on-prem data residency", "Per-agent ledger on-device", "Grading happens locally", "HIPAA / GDPR posture trivial"],
      con: ["Hardware acquisition cost", "Operator handles uptime", "Limited horsepower for big fleets"],
      featured: true,
    },
    {
      tag: "CLOUD",
      title: "Your own cloud · no hardware",
      tagline: "Docker container in your stack · we never see the call path.",
      runs: "Your Docker / k8s / VM fleet (Python sidecar option available)",
      sink: "Bakery vault (Tigris-backed · our durable storage)",
      use: "Most teams · faster deploy · cheaper · no compliance posture requirements",
      pro: ["30-second Docker install", "Scales with your fleet", "No hardware procurement", "Same audit pipeline"],
      con: ["Receipts cross your firewall (metadata only by default)", "Bakery sink requires customer relationship", "Cloud lives in our DC"],
    },
    {
      tag: "HYBRID",
      title: "Router on cloud · receipts to HoneyBox",
      tagline: "Best of both · scale on cloud · residency on edge.",
      runs: "Router in your cloud (any mode above)",
      sink: "HoneyBox on-prem catches receipts · optionally syncs hashed metadata to Bakery for cross-team deeds",
      use: "Large fleets with regulated subsets · multi-tenant SaaS with HIPAA customers · enterprises with mixed posture",
      pro: ["Cloud scale + edge residency", "Metadata-only sync option", "Bodies stay on-prem", "Per-customer receipt isolation"],
      con: ["Two pieces to operate", "Sync rules need design", "More configuration upfront"],
    },
  ];
  return (
    <section id="modes" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          DEPLOYMENT · WHERE THE ROUTER RUNS · 3 MODES
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Edge · Cloud · Hybrid.{" "}
          <span className="font-serif italic font-normal text-amber-300">You choose.</span>
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          The router is a software process · it runs wherever Docker runs.
          DefendableHQ is{" "}
          <span className="text-stone-100">never in the call path</span> ·
          we never proxy your traffic. We're the Bakery (receipt sink +
          grading + deed issuance). The router process always runs in YOUR
          stack · your edge appliance, your cloud, or both.
        </p>

        <div className="mt-12 grid lg:grid-cols-3 gap-6">
          {modes.map((m) => {
            const ring = m.featured
              ? "border-amber-500/40 bg-amber-500/[0.03]"
              : "border-stone-800 bg-neutral-950/60";
            return (
              <div key={m.tag} className={`rounded-xl border ${ring} p-6 flex flex-col`}>
                <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
                  {m.tag}
                </div>
                <h3 className="mt-3 text-xl font-semibold tracking-tight text-stone-50">{m.title}</h3>
                <p className="mt-3 text-sm text-stone-300 leading-relaxed font-serif italic">
                  {m.tagline}
                </p>

                <dl className="mt-5 space-y-2 text-xs">
                  <div>
                    <dt className="text-[9px] uppercase tracking-[0.22em] text-stone-500">RUNS ON</dt>
                    <dd className="mt-0.5 text-stone-300">{m.runs}</dd>
                  </div>
                  <div>
                    <dt className="text-[9px] uppercase tracking-[0.22em] text-stone-500">RECEIPTS GO TO</dt>
                    <dd className="mt-0.5 text-stone-300">{m.sink}</dd>
                  </div>
                  <div>
                    <dt className="text-[9px] uppercase tracking-[0.22em] text-stone-500">USE CASE</dt>
                    <dd className="mt-0.5 text-stone-300">{m.use}</dd>
                  </div>
                </dl>

                <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <div className="text-[9px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold">PRO</div>
                    <ul className="mt-1.5 space-y-1 text-stone-400">
                      {m.pro.map((p) => <li key={p}>· {p}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-[9px] uppercase tracking-[0.22em] text-stone-500 font-semibold">CON</div>
                    <ul className="mt-1.5 space-y-1 text-stone-500">
                      {m.con.map((c) => <li key={c}>· {c}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <p className="mt-10 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          You can switch modes later · same router binary, different
          config. Start CLOUD for the wedge · upgrade to HYBRID when your
          first regulated customer signs · stay EDGE forever if you're a
          fully-regulated shop.
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// ENS bridge · per-agent cryptographic identity
// ─────────────────────────────────────────────────────────────────────────
function EnsBridge() {
  const ascii = `# Each call carries agent identity headers
client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    extra_headers={
        "X-Defendable-Agent-Id":   "refund-bot-prod-001",
        "X-Defendable-Operator":   "acmecorp",
        "X-Defendable-Task-Class": "refund_decision",
    },
)

# Router resolves the ENS subdomain
   refund-bot-prod-001.acmecorp.defendable.eth
   │
   ▼
# Signs the receipt with that identity
{
  "agent_id":         "refund-bot-prod-001",
  "operator":         "acmecorp",
  "agent_ens":        "refund-bot-prod-001.acmecorp.defendable.eth",
  "agent_address":    "0x7c19...e2a4",          ← ENS-resolved
  "receipt_id":       "DCLAW-A9128F-2026-05-24T01-13-44Z",
  "record_hash":      "sha256:f3a8b1c9...",
  "signed_by":        "ed25519:agent-key-pubkey",
  "signature":        "0x91a3...2d4f"            ← per-agent signed
}

# Daily Reconciliation Deed inherits the ENS lineage
{
  "deed_id":          "DDEED-DOV-AGENT-REFUND-BOT-PROD-001-000042-v1",
  "agent_ens":        "refund-bot-prod-001.acmecorp.defendable.eth",
  "operator_ens":     "acmecorp.defendable.eth",
  "compliance_ens":   "compliance.acmecorp.defendable.eth",
  "receipts_in_day":  237,
  "tribunal":         { "honey": 198, "jelly": 31, "propolis": 8 },
  "record_hash":      "sha256:7c19e2a4..."
}`;

  return (
    <section id="ens" className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          ENS BRIDGE · PER-AGENT CRYPTOGRAPHIC IDENTITY
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Every receipt is{" "}
          <span className="font-serif italic font-normal text-amber-300">ENS-anchored</span>.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          Logs are claims. ENS-signed receipts are attestations. The
          router is the bridge that turns the former into the latter ·
          every call gets resolved to a per-agent ENS subdomain
          (<code className="font-mono text-amber-300">agent.operator.defendable.eth</code>),
          signed with that agent's keypair, and the daily reconciliation
          deed inherits the lineage. CFO + auditor + carrier can verify
          the deed came from the agent it claims to · not just trust a
          log line.
        </p>

        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <EnsTile
            tier="PER-AGENT"
            ens="refund-bot-prod-001.acmecorp.defendable.eth"
            use="One ENS subdomain per agent · its keypair signs every receipt that comes from it"
          />
          <EnsTile
            tier="PER-OPERATOR"
            ens="acmecorp.defendable.eth"
            use="Customer/operator root · all agents inherit · daily deed rolls up under this name"
          />
          <EnsTile
            tier="PER-COMPLIANCE"
            ens="compliance.acmecorp.defendable.eth"
            use="Customer compliance officer's inbox · receives 'you got mail' pings + signed metadata"
          />
        </div>

        <div className="mt-10 rounded-xl border border-stone-800 bg-black overflow-hidden">
          <div className="px-4 py-2 border-b border-stone-800 text-[10px] uppercase tracking-[0.22em] text-stone-500 bg-neutral-950 font-mono">
            $ defendable-router --trace-ens
          </div>
          <pre className="px-4 py-5 overflow-x-auto text-[11px] leading-snug text-stone-200 font-mono">
            <code>{ascii}</code>
          </pre>
        </div>

        <div className="mt-8 grid md:grid-cols-2 gap-6">
          <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-5">
            <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
              WHY ENS · NOT JUST AGENT IDs
            </div>
            <p className="mt-3 text-sm text-stone-400 leading-relaxed">
              Anyone can write <code className="font-mono text-amber-300">agent_id: "x"</code>{" "}
              in a log. Only the holder of the ENS keypair can sign a
              receipt for that agent. ENS gives you portable,
              cryptographically-verifiable agent identity that travels
              with the receipt · across teams, vendors, and time.
            </p>
          </div>
          <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-5">
            <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
              ENS IS OPTIONAL · STARTS FREE
            </div>
            <p className="mt-3 text-sm text-stone-400 leading-relaxed">
              Run the router without ENS · receipts still flow · audit
              pipeline still works · you just don't get cryptographic
              attestation. Upgrade to ENS-anchored when you're ready ·
              we provision the subdomains on the{" "}
              <code className="font-mono text-amber-300">defendable.eth</code>{" "}
              namespace as part of the audit pipeline tier.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function EnsTile({ tier, ens, use }: { tier: string; ens: string; use: string }) {
  return (
    <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-5">
      <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
        {tier}
      </div>
      <code className="mt-3 block font-mono text-xs text-amber-300 break-all">{ens}</code>
      <p className="mt-3 text-xs text-stone-400 leading-relaxed">{use}</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Install · 3 modes
// ─────────────────────────────────────────────────────────────────────────
function Install() {
  const docker = `# 30-second install · runs anywhere Docker runs
docker run -d \\
  --name defendable-router \\
  -p 8080:8080 \\
  -e ROUTER_UPSTREAM_OPENAI=https://api.openai.com \\
  -e ROUTER_UPSTREAM_ANTHROPIC=https://api.anthropic.com \\
  -e ROUTER_AGENT_ID=refund-bot-prod-001 \\
  -e ROUTER_RECEIPT_SINK=file:///var/log/router/   # or s3://, https://, none
  ghcr.io/sudosuops/defendable-router:latest

# Then point your agent's base_url at http://localhost:8080
# Your agent code does not change. Receipts start flowing.`;

  const python = `# Python sidecar · for FastAPI / Flask / Django stacks
# pip install defendable-router

from defendable_router import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI(api_key=OPENAI_KEY))

# That's it. Every call client.* makes now writes a receipt.
# Wraps Anthropic, Cohere, Mistral the same way.
# Receipts go to ROUTER_RECEIPT_SINK (env var or kwarg).`;

  const nginx = `# nginx sidecar · drop-in for k8s / VM fleets
# /etc/nginx/conf.d/defendable-router.conf

upstream openai_backend {
  server api.openai.com:443;
}

server {
  listen 8080;

  location /v1/ {
    # forward to provider
    proxy_pass https://openai_backend;
    proxy_set_header Host api.openai.com;

    # mirror to defendable-router for receipt
    mirror /router-sink;
    mirror_request_body on;
  }

  location = /router-sink {
    internal;
    proxy_pass http://defendable-router:8081/sink;
  }
}`;

  return (
    <section id="install" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ INSTALL · 30 SECONDS · 3 MODES
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Pick your shape ·{" "}
          <span className="font-serif italic font-normal text-amber-300">no rewrites required</span>.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          Docker (any stack) · Python SDK wrapper (FastAPI / Flask) ·
          nginx sidecar (k8s / VM). All three modes are write-only and
          ship with the same receipt schema. Pick whichever your ops team
          already knows.
        </p>

        <div className="mt-10 grid lg:grid-cols-3 gap-6">
          <TermBlock label="$ docker · any stack" code={docker} highlight />
          <TermBlock label="$ python · sdk wrapper" code={python} />
          <TermBlock label="$ nginx · sidecar" code={nginx} />
        </div>

        <p className="mt-8 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          The repository is <a href={GITHUB_REPO_URL} target="_blank" rel="noopener noreferrer" className="text-amber-300 hover:text-amber-200">github.com/SudoSuOps/defendable-router</a>{" "}
          · MIT-with-receipt-clause license. The receipt clause: you may
          run the router forever without paying us · if you point receipts
          at our audit pipeline, standard service terms apply.
        </p>
      </div>
    </section>
  );
}

function TermBlock({ label, code, highlight }: { label: string; code: string; highlight?: boolean }) {
  const ring = highlight ? "border-amber-500/40" : "border-stone-800";
  return (
    <div className={`rounded-xl border ${ring} bg-black overflow-hidden flex flex-col`}>
      <div className="px-4 py-2 border-b border-stone-800 text-[10px] uppercase tracking-[0.22em] text-amber-400/80 bg-neutral-950 font-mono">
        {label}
      </div>
      <pre className="px-4 py-4 overflow-x-auto text-[11px] leading-relaxed text-stone-200 font-mono flex-1">
        <code>{code}</code>
      </pre>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Code samples · before/after
// ─────────────────────────────────────────────────────────────────────────
function CodeSamples() {
  const before = `# BEFORE · your code today (no audit trail)
from openai import OpenAI

client = OpenAI(api_key=OPENAI_KEY)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a refund agent."},
        {"role": "user", "content": "Refund order RFD-12345"},
    ],
)

# Done. Cost: $0.012. Audit trail: nothing.`;

  const after = `# AFTER · same code, just change base_url
from openai import OpenAI

client = OpenAI(
    api_key=OPENAI_KEY,
    base_url="http://localhost:8080/v1",   # ← only line that changed
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a refund agent."},
        {"role": "user", "content": "Refund order RFD-12345"},
    ],
    extra_headers={
        "X-Defendable-Agent-Id":   "refund-bot-prod-001",
        "X-Defendable-Task-Class": "refund_decision",
    },
)

# Done. Cost: $0.012. Audit trail: receipt #DCLAW-A91-... fired async.`;

  const receipt = `{
  "receipt_id":        "DCLAW-A9128F-2026-05-24T01-13-44Z",
  "agent_id":          "refund-bot-prod-001",
  "task_class":        "refund_decision",
  "provider":          "openai",
  "model":             "gpt-4o",
  "request_ts":        "2026-05-24T01:13:44.812Z",
  "response_ts":       "2026-05-24T01:13:46.107Z",
  "wire_overhead_ms":  3.4,
  "tokens_prompt":     142,
  "tokens_completion": 38,
  "tokens_total":      180,
  "cost_usd":          0.0118,
  "status_code":       200,
  "tool_calls_count":  0,
  "include_body":      false,
  "body_hash":         "sha256:7c19e2a4...",
  "record_hash":       "sha256:f3a8b1c9..."
}`;

  return (
    <section id="code" className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          CODE · BEFORE / AFTER · ONE LINE CHANGES
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Change{" "}
          <span className="font-serif italic font-normal text-amber-300">one line</span>{" "}
          · get the receipt.
        </h2>

        <div className="mt-10 grid md:grid-cols-2 gap-6">
          <TermBlock label="$ before · no audit trail" code={before} />
          <TermBlock label="$ after · receipt fires async" code={after} highlight />
        </div>

        <div className="mt-10">
          <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
            $ sample receipt · what fires to the bakery vault
          </div>
          <div className="mt-3 rounded-xl border border-stone-800 bg-black overflow-hidden">
            <pre className="px-4 py-4 overflow-x-auto text-[11px] leading-relaxed text-stone-200 font-mono">
              <code>{receipt}</code>
            </pre>
          </div>
          <p className="mt-4 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
            Default receipt is metadata-only · no prompt bodies, no
            completion bodies, just hashes. Bodies are opt-in per call.
            Most teams flip on full bodies for ~1% sampled traffic for
            compliance evidence and leave it off for the other 99%.
          </p>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// HoneyBox pairing
// ─────────────────────────────────────────────────────────────────────────
function HoneyBoxPairing() {
  return (
    <section id="honeybox" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          DEFENDABLE EDGE STACK · ROUTER + HONEYBOX
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Pair with the{" "}
          <span className="font-serif italic font-normal text-amber-300">HoneyBox</span>{" "}
          · raw data never leaves.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          DefendableRouter runs anywhere · but pair it with a HoneyBox
          (the $249-$2K NVIDIA Jetson appliance) and your receipts land
          on customer-premises silicon. The router captures · the
          HoneyBox stores · reconciles · grades · deeds. Raw prompt
          bodies and tool-use traces never cross your firewall.
        </p>

        <div className="mt-10 grid md:grid-cols-2 gap-6">
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/[0.04] p-6">
            <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
              EDGE STACK · DATA-RESIDENCY UNLOCK
            </div>
            <h3 className="mt-3 text-xl font-semibold tracking-tight text-stone-50">
              Router → HoneyBox → ENS deed
            </h3>
            <p className="mt-3 text-sm text-stone-300 leading-relaxed">
              Router intercepts the agent call · HoneyBox catches the
              receipt on-prem · Tribunal grades nightly at 02:00 · Daily
              Reconciliation Deed issued · "you got mail" signed metadata
              ping to the operator (no raw data ever leaves the building).
            </p>
            <p className="mt-4 text-xs text-stone-500 italic font-serif leading-relaxed">
              Unlocks regulated industries · healthcare · finance · gov ·
              defense · legal · that are categorically closed to cloud-only
              audit pipelines.
            </p>
            <a
              href="https://defendableos.com/honeybox"
              className="mt-4 inline-block text-xs uppercase tracking-[0.18em] rounded border border-amber-500/60 text-amber-300 px-3 py-1.5 hover:bg-amber-500/10 transition-colors"
            >
              See the HoneyBox →
            </a>
          </div>

          <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-6">
            <div className="text-[10px] uppercase tracking-[0.22em] text-stone-500 font-semibold font-mono">
              CLOUD STACK · NO HARDWARE
            </div>
            <h3 className="mt-3 text-xl font-semibold tracking-tight text-stone-50">
              Router → Bakery Vault → ENS deed
            </h3>
            <p className="mt-3 text-sm text-stone-300 leading-relaxed">
              No on-prem hardware needed. Receipts fire async to our
              Tigris-backed Bakery vault. Same nightly Tribunal · same
              Daily Reconciliation Deed · same morning brief. For teams
              without regulated data residency requirements.
            </p>
            <p className="mt-4 text-xs text-stone-500 italic font-serif leading-relaxed">
              Cheaper (no hardware) · faster to deploy (Docker run · go) ·
              same audit posture once receipts land in the vault.
            </p>
            <a
              href={DEFENDABLECLOUD_URL}
              className="mt-4 inline-block text-xs uppercase tracking-[0.18em] rounded border border-stone-700 text-stone-300 px-3 py-1.5 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
            >
              See DefendableCloud →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Pricing · free + paid tiers
// ─────────────────────────────────────────────────────────────────────────
function Pricing() {
  return (
    <section id="pricing" className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          PRICING · FREE WEDGE · PAID AUDIT PIPELINE
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          The router is{" "}
          <span className="font-serif italic font-normal text-amber-300">free</span>.
          The audit pipeline is the product.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          Install costs nothing · runs forever · self-hosted on whatever
          you've got. When you want grading, deed issuance, or insurance
          baseline · point the receipts at our Bakery vault and we're a
          customer relationship.
        </p>

        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <PriceCard
            tier="OSS"
            title="Self-hosted"
            price="$0"
            sub="forever · MIT-with-receipt-clause"
            bullets={[
              "Docker / Python SDK / nginx sidecar",
              "Write-only · <5ms POST",
              "Local sink (file / s3 / your own bus)",
              "Receipt schema documented · open",
              "Community support via GitHub issues",
            ]}
            ctaLabel="Install from GitHub"
            ctaHref={GITHUB_REPO_URL}
            external
          />
          <PriceCard
            tier="RECEIPTS"
            title="Audit pipeline"
            price="TBD"
            sub="$ per million receipts · request quote"
            bullets={[
              "Receipts → our Bakery vault",
              "Nightly Tribunal grading",
              "Daily Reconciliation Deed issued",
              "Morning Brief at 06:00",
              "Drift Alerts · pattern flags",
              "Concierge support · 24h SLA",
            ]}
            ctaLabel="Request receipts quote"
            ctaHref={MAILTO_ACCESS}
            featured
          />
          <PriceCard
            tier="INSURANCE"
            title="Carrier baseline"
            price="TBD"
            sub="priced per engagement"
            bullets={[
              "Everything in Receipts tier",
              "Underwriting-grade evidence pack",
              "Carrier-facing reconciliation deed",
              "Quarterly Operator Statement",
              "Embedded ops review",
              "Direct introductions to AI insurance carriers",
            ]}
            ctaLabel="Insurance baseline intake"
            ctaHref={MAILTO_INSURANCE}
          />
        </div>

        <p className="mt-10 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          We don't publish per-million-receipt rates that depend on agent
          volume, retention tier, and Tribunal pack complexity · those
          numbers are dishonest without your call shape. Request a quote
          and we'll quote a rate good for 90 days tied to your actual
          workload.
        </p>
      </div>
    </section>
  );
}

function PriceCard({
  tier,
  title,
  price,
  sub,
  bullets,
  ctaLabel,
  ctaHref,
  featured,
  external,
}: {
  tier: string;
  title: string;
  price: string;
  sub: string;
  bullets: string[];
  ctaLabel: string;
  ctaHref: string;
  featured?: boolean;
  external?: boolean;
}) {
  const ring = featured ? "border-amber-500/40 bg-amber-500/[0.03]" : "border-stone-800 bg-neutral-950";
  return (
    <div className={`rounded-xl border ${ring} p-6 flex flex-col`}>
      <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">
        {tier}
      </div>
      <h3 className="mt-3 text-2xl font-semibold tracking-tight text-stone-50">{title}</h3>
      <div className="mt-3 text-3xl font-mono text-amber-300">{price}</div>
      <div className="mt-1 text-xs text-stone-500">{sub}</div>
      <ul className="mt-5 space-y-2 text-sm text-stone-400 flex-1">
        {bullets.map((b) => (
          <li key={b} className="flex gap-2">
            <span className="text-amber-400 mt-0.5">·</span>
            <span>{b}</span>
          </li>
        ))}
      </ul>
      <a
        href={ctaHref}
        {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
        className="mt-6 text-center rounded border border-amber-500/40 px-4 py-2 text-xs uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/10 transition-colors font-mono"
      >
        {ctaLabel}
      </a>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Compare · vs alternatives
// ─────────────────────────────────────────────────────────────────────────
function Compare() {
  const rows = [
    ["Receipts the agent never sees",       "✗", "✗", "✗", "✓"],
    ["Write-only · <5ms wire overhead",     "n/a", "✗", "✗", "✓"],
    ["Works with any LLM provider",         "n/a", "limited", "OpenAI-only", "✓"],
    ["MIT-with-receipt-clause license",     "n/a", "✗", "✗", "✓"],
    ["Self-hostable · no vendor lock",      "n/a", "✗", "SaaS-only", "✓"],
    ["Tribunal grading + deed issuance",    "✗", "✗", "✗", "✓"],
    ["Insurance carrier baseline",          "✗", "✗", "✗", "✓"],
    ["Costs you anything to start",         "n/a", "$$$ enterprise", "$$ per seat", "$0"],
  ];
  return (
    <section id="compare" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          COMPARE · WHAT YOU'RE NOT BUYING
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Side-by-side ·{" "}
          <span className="font-serif italic font-normal text-amber-300">vs the stack you have</span>.
        </h2>

        <div className="mt-10 overflow-x-auto rounded-xl border border-stone-800">
          <table className="w-full text-sm">
            <thead className="bg-neutral-950/60">
              <tr className="border-b border-stone-800">
                <th className="text-left py-3 px-4 text-[10px] uppercase tracking-[0.2em] text-stone-500 font-semibold">Capability</th>
                <th className="text-center py-3 px-4 text-[10px] uppercase tracking-[0.2em] text-stone-500 font-semibold">No router today</th>
                <th className="text-center py-3 px-4 text-[10px] uppercase tracking-[0.2em] text-stone-500 font-semibold">Datadog APM</th>
                <th className="text-center py-3 px-4 text-[10px] uppercase tracking-[0.2em] text-stone-500 font-semibold">LangSmith</th>
                <th className="text-center py-3 px-4 text-[10px] uppercase tracking-[0.22em] text-amber-300 font-semibold">DefendableRouter</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-b border-stone-900/60">
                  <td className="py-3 px-4 text-stone-300 font-medium">{r[0]}</td>
                  <td className="py-3 px-4 text-center text-stone-400">{r[1]}</td>
                  <td className="py-3 px-4 text-center text-stone-400">{r[2]}</td>
                  <td className="py-3 px-4 text-center text-stone-400">{r[3]}</td>
                  <td className="py-3 px-4 text-center text-amber-300 font-medium">{r[4]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-8 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          Datadog and LangSmith are great at what they do · neither is
          built to be a write-only audit rail your CFO and insurance
          carrier can sign. Different problem · different shape · use
          both if you want · DefendableRouter doesn't conflict.
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Insurance angle
// ─────────────────────────────────────────────────────────────────────────
function Insurance() {
  return (
    <section className="border-b border-stone-900 bg-amber-500/[0.02]">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          INSURANCE · THE CARRIER ANGLE
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Carriers are starting to underwrite AI agents.{" "}
          <span className="font-serif italic font-normal text-amber-300">Receipts are the baseline</span>.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          AI errors-and-omissions coverage is a real category now. Major
          carriers (Munich Re, Lloyd's syndicates, several US specialty
          carriers) are writing policies that require an audit baseline.
          DefendableRouter is the cheapest way to produce that baseline
          and the only one with deeds your carrier can ingest directly.
        </p>

        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-6">
            <h3 className="text-lg font-semibold tracking-tight text-stone-50">Without receipts</h3>
            <p className="mt-3 text-sm text-stone-400 leading-relaxed">
              Carrier asks: "how do you know your agent didn't approve
              that fraudulent refund?" You can't answer. Carrier
              declines or prices high.
            </p>
          </div>
          <div className="rounded-xl border border-stone-800 bg-neutral-950/60 p-6">
            <h3 className="text-lg font-semibold tracking-tight text-stone-50">With router-only</h3>
            <p className="mt-3 text-sm text-stone-400 leading-relaxed">
              You hand over CSVs of receipts. Carrier maybe accepts.
              Maybe charges actuarial team to validate them. Premium
              improves but slowly.
            </p>
          </div>
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/[0.04] p-6">
            <h3 className="text-lg font-semibold tracking-tight text-stone-50">With receipts + deeds</h3>
            <p className="mt-3 text-sm text-stone-300 leading-relaxed">
              You hand over signed{" "}
              <span className="text-amber-300">DDEED-DOV-AGENT</span>{" "}
              records with Tribunal grades. Carrier ingests directly.
              Premium drops materially.
            </p>
          </div>
        </div>

        <div className="mt-10">
          <a
            href={MAILTO_INSURANCE}
            className="inline-block rounded border border-amber-500 bg-amber-500/10 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/20 transition-colors font-mono"
          >
            $ insurance-baseline-intake
          </a>
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// GitHub block
// ─────────────────────────────────────────────────────────────────────────
function GithubBlock() {
  return (
    <section id="github" className="border-b border-stone-900">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ git clone · MIT-WITH-RECEIPT-CLAUSE · OPEN
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          The code is{" "}
          <span className="font-serif italic font-normal text-amber-300">on GitHub</span>.
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-3xl">
          DefendableRouter is open source. The repository is the
          authoritative install path · the spec doc · the issue tracker ·
          the contribution doorway. Star it if you like the cracked-router
          energy. Open issues for what you'd like to see. Send PRs for
          what you've already built.
        </p>

        <div className="mt-10 rounded-xl border border-stone-800 bg-black overflow-hidden">
          <div className="px-5 py-4 border-b border-stone-800 bg-neutral-950 flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <GithubIcon />
              <span className="font-mono text-sm text-stone-300">SudoSuOps / defendable-router</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-stone-500 font-mono">
              <span>MIT-with-receipt-clause</span>
              <span>·</span>
              <span>main</span>
            </div>
          </div>
          <div className="px-5 py-4 grid sm:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">CLONE</div>
              <code className="mt-2 block font-mono text-xs text-stone-300 break-all">
                git clone {GITHUB_REPO_URL}.git
              </code>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">DOCKER</div>
              <code className="mt-2 block font-mono text-xs text-stone-300 break-all">
                docker pull ghcr.io/sudosuops/defendable-router
              </code>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80 font-semibold font-mono">PYTHON</div>
              <code className="mt-2 block font-mono text-xs text-stone-300 break-all">
                pip install defendable-router
              </code>
            </div>
          </div>
          <div className="px-5 py-4 border-t border-stone-800 flex flex-wrap gap-3">
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded border border-amber-500 bg-amber-500/10 px-4 py-1.5 text-xs uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/20 transition-colors font-mono flex items-center gap-2"
            >
              <GithubIcon /> ★ Star the repo
            </a>
            <a
              href={`${GITHUB_REPO_URL}/issues`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded border border-stone-700 px-4 py-1.5 text-xs uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors font-mono"
            >
              Open an issue
            </a>
            <a
              href={`${GITHUB_REPO_URL}/blob/main/README.md`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded border border-stone-700 px-4 py-1.5 text-xs uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors font-mono"
            >
              README
            </a>
          </div>
        </div>

        <p className="mt-6 text-xs text-stone-500 italic font-serif leading-relaxed max-w-3xl">
          The receipt clause exists for one reason: we want the install
          path free forever, and we want a clear line so customers who
          point receipts at our audit pipeline know they're entering a
          standard service relationship. The router itself is no-strings.
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// FAQ
// ─────────────────────────────────────────────────────────────────────────
function Faq() {
  const items = [
    {
      q: "What does the router actually slow down?",
      a: "Nothing on the synchronous path. Your agent's call to the LLM goes through us as a transparent proxy with <5ms wire-time overhead (mostly TLS handshake). The receipt write is async · fire-and-forget · happens AFTER the response returns to your agent.",
    },
    {
      q: "What LLM providers work?",
      a: "Any provider that speaks OpenAI's chat-completions shape (so: OpenAI · Anthropic via Claude's OpenAI-compat endpoint · Mistral · OpenRouter · Cohere · DeepSeek · DefendableCloud · vLLM · llama.cpp · Ollama · LM Studio · your custom endpoint). If you can curl it like OpenAI, the router can wrap it.",
    },
    {
      q: "Does it see my prompt bodies?",
      a: "No, not by default. Default receipt is metadata-only · token counts, model, timestamps, cost, body hashes. Bodies are opt-in per call via the X-Defendable-Include-Body header. Most teams sample 1% of traffic with bodies on for compliance evidence and leave the other 99% metadata-only.",
    },
    {
      q: "Is it really open source?",
      a: "Yes. MIT-with-receipt-clause license. You can run it forever, fork it, modify it, redistribute it. The only clause: if you point receipts at our Bakery vault, standard service terms apply to that relationship. The router itself stays free no matter what.",
    },
    {
      q: "How do I integrate with my existing observability (Datadog / OTel)?",
      a: "DefendableRouter emits OpenTelemetry-compatible spans alongside its own receipt schema. Point your existing OTel collector at the router's /telemetry endpoint and everything you already log keeps logging. The router adds the audit dimension Datadog doesn't ship.",
    },
    {
      q: "What's the deal with HoneyBox pairing?",
      a: "For teams with regulated data residency (healthcare, finance, gov, defense, legal), receipts can be configured to land on a customer-premises HoneyBox appliance ($249-$2K) instead of our Bakery vault. Same Tribunal grading happens on-device. Raw data never crosses your firewall.",
    },
    {
      q: "How fast can I be in production?",
      a: "Docker mode: 30 seconds. Python SDK wrapper: 2 minutes (pip install + 2 lines of code). nginx sidecar: 10 minutes (config file + reload). Self-hosted with local sink: free + zero account creation. Audit pipeline: email build@defendableos.com, key issued same day if no compliance review needed.",
    },
    {
      q: "What about prompt injection / jailbreak attacks?",
      a: "Out of scope for the router (which is write-only and never modifies prompts). In scope for the Tribunal grading that runs on the receipts: flagged jailbreak patterns become Propolis verdicts in the daily reconciliation deed. The router captures · the Tribunal grades · SwarmFixer ships the fix.",
    },
  ];
  return (
    <section className="border-b border-stone-900 bg-neutral-950/60">
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ man defendable-router | grep -i faq
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50 max-w-3xl">
          Frequently asked.
        </h2>
        <div className="mt-10 space-y-6 max-w-3xl">
          {items.map((it) => (
            <div key={it.q} className="border-l-2 border-amber-500/40 pl-5">
              <h3 className="text-lg font-semibold tracking-tight text-stone-50">{it.q}</h3>
              <p className="mt-2 text-sm text-stone-400 leading-relaxed">{it.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// CTA / Contact
// ─────────────────────────────────────────────────────────────────────────
function CtaContact() {
  return (
    <section className="border-b border-stone-900">
      <div className="max-w-4xl mx-auto px-6 py-20 lg:py-28 text-center">
        <div className="text-[10px] uppercase tracking-[0.24em] text-amber-400/80 font-semibold font-mono">
          $ npm install · git clone · docker pull · pick your verb
        </div>
        <h2 className="mt-5 text-3xl md:text-4xl font-semibold tracking-tight text-stone-50">
          Crack the router.{" "}
          <span className="font-serif italic font-normal text-amber-300">Today.</span>
        </h2>
        <p className="mt-5 text-base text-stone-400 leading-relaxed max-w-2xl mx-auto">
          The install is free. The repo is open. The receipts start
          flowing the moment your agent makes its first call through us.
          The audit pipeline is there when you're ready.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-amber-500 bg-amber-500/10 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-amber-300 hover:bg-amber-500/20 transition-colors font-mono flex items-center gap-2"
          >
            <GithubIcon /> $ git clone
          </a>
          <a
            href={MAILTO_ACCESS}
            className="rounded border border-stone-700 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors font-mono"
          >
            $ receipts-tier-quote
          </a>
          <a
            href={MAILTO_INSURANCE}
            className="rounded border border-stone-700 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.18em] text-stone-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors font-mono"
          >
            $ insurance-baseline
          </a>
        </div>
        <p className="mt-10 text-xs text-stone-500">
          Mothership ·{" "}
          <a href={DEFENDABLEOS_URL} className="text-amber-400/80 hover:text-amber-300">defendableos.com</a>
          {"  ·  "}
          Sister product ·{" "}
          <a href={DEFENDABLECLOUD_URL} className="text-amber-400/80 hover:text-amber-300">defendablecloud.com</a>
          {"  ·  "}
          Docs ·{" "}
          <a href={DOCS_URL} className="text-amber-400/80 hover:text-amber-300">docs.defendableos.com</a>
        </p>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Footer
// ─────────────────────────────────────────────────────────────────────────
function Footer() {
  return (
    <footer className="border-t border-amber-500/20 bg-neutral-950">
      <div className="max-w-6xl mx-auto px-6 py-12 grid md:grid-cols-4 gap-8 text-sm">
        <div className="md:col-span-2">
          <div className="flex items-center gap-2">
            <span className="font-mono text-amber-400 text-base">_</span>
            <span className="font-semibold tracking-tight text-stone-100">
              Defendable<span className="text-amber-300">Router</span>
            </span>
          </div>
          <p className="mt-4 text-stone-500 leading-relaxed max-w-md">
            We cracked the router. OpenWrt for AI agents. Drop-in
            middleware that writes a receipt for every agent call ·
            write-only · &lt;5ms POST · free OSS install · paid audit
            pipeline. A surface of{" "}
            <a href={DEFENDABLEOS_URL} className="text-amber-400/80 hover:text-amber-300">DefendableOS</a>.
          </p>
          <div className="mt-5 flex gap-4 text-stone-500">
            <a href={X_URL} className="hover:text-amber-300" aria-label="X">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2H21.5l-7.5 8.572L23 22h-6.844l-5.36-7.014L4.66 22H1.4l8.025-9.175L1 2h7.014l4.844 6.404L18.244 2zm-2.4 18.043h1.864L7.25 3.86H5.27l10.574 16.183z"/></svg>
            </a>
            <a href={LINKEDIN_URL} className="hover:text-amber-300" aria-label="LinkedIn">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.66H9.36V9h3.41v1.56h.05c.47-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.55V9h3.57v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/></svg>
            </a>
            <a href={GITHUB_ORG_URL} className="hover:text-amber-300" aria-label="GitHub">
              <GithubIcon />
            </a>
            <a href={`mailto:${SALES_EMAIL}`} className="hover:text-amber-300" aria-label="Email">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 13.065L2.4 6.5h19.2L12 13.065zM0 18V6.935l12 8.13 12-8.13V18a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2z"/></svg>
            </a>
          </div>
        </div>

        <div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-stone-500 font-semibold font-mono">Router</div>
          <ul className="mt-3 space-y-2 text-stone-400">
            <li><a href="#what" className="hover:text-amber-300">What</a></li>
            <li><a href="#install" className="hover:text-amber-300">Install</a></li>
            <li><a href="#code" className="hover:text-amber-300">Code</a></li>
            <li><a href="#honeybox" className="hover:text-amber-300">HoneyBox pairing</a></li>
            <li><a href="#pricing" className="hover:text-amber-300">Pricing</a></li>
            <li><a href="#compare" className="hover:text-amber-300">Compare</a></li>
            <li><a href="#github" className="hover:text-amber-300">GitHub</a></li>
          </ul>
        </div>

        <div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-stone-500 font-semibold font-mono">Related Surfaces</div>
          <ul className="mt-3 space-y-2 text-stone-400">
            <li><a href={DEFENDABLEOS_URL} className="hover:text-amber-300">defendableos.com</a></li>
            <li><a href={DEFENDABLECLOUD_URL} className="hover:text-amber-300">defendablecloud.com</a></li>
            <li><a href="https://defendableos.com/honeybox" className="hover:text-amber-300">HoneyBox · edge</a></li>
            <li><a href="https://defendableos.com/doctrine" className="hover:text-amber-300">Doctrine</a></li>
            <li><a href={DOCS_URL} className="hover:text-amber-300">Docs</a></li>
            <li><a href="https://opendefendable.com" className="hover:text-amber-300">OpenDefendable · OSS</a></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-stone-900">
        <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col sm:flex-row gap-2 sm:gap-0 justify-between text-[11px] text-stone-600 font-mono">
          <div>© 2026 Swarm and Bee LLC · DBA Swarm & Bee AI · Florida · D-U-N-S 138652395</div>
          <div className="italic font-serif">"We cracked the router. The receipts do the rest."</div>
        </div>
      </div>
    </footer>
  );
}

function GithubIcon() {
  return (
    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden>
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.118-3.176 0 0 1.008-.322 3.301 1.23a11.5 11.5 0 0 1 3.003-.404c1.018.005 2.045.138 3.003.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .322.218.694.825.576C20.565 22.092 24 17.594 24 12.297c0-6.627-5.373-12-12-12"/>
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Schema.org JSON-LD
// ─────────────────────────────────────────────────────────────────────────
function JsonLd() {
  const json = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://defendablerouter.com/#org",
        name: "DefendableRouter",
        url: "https://defendablerouter.com/",
        sameAs: [
          "https://defendableos.com/",
          "https://defendablecloud.com/",
          "https://docs.defendableos.com/",
          "https://opendefendable.com/",
          X_URL,
          LINKEDIN_URL,
          GITHUB_ORG_URL,
        ],
        parentOrganization: {
          "@type": "Organization",
          name: "Swarm and Bee LLC",
          alternateName: "Swarm & Bee AI",
          identifier: "D-U-N-S 138652395",
          address: { "@type": "PostalAddress", addressRegion: "FL", addressCountry: "US" },
        },
      },
      {
        "@type": "SoftwareApplication",
        name: "DefendableRouter",
        operatingSystem: "Linux · macOS · Windows · Docker · Kubernetes",
        applicationCategory: "DeveloperApplication",
        description:
          "Drop-in middleware that intercepts AI agent traffic and writes receipts. Write-only · <5ms POST. Free OSS install · MIT-with-receipt-clause license. Paid receipts, grading, and insurance baseline tiers available.",
        offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
        downloadUrl: GITHUB_REPO_URL,
        codeRepository: GITHUB_REPO_URL,
        license: "https://opensource.org/license/mit",
      },
      {
        "@type": "Service",
        name: "DefendableRouter Audit Pipeline",
        description:
          "Receipts tier · receipts land in Bakery vault · nightly Tribunal grading · Daily Reconciliation Deed · Morning Brief · Drift Alerts.",
        provider: { "@id": "https://defendablerouter.com/#org" },
      },
      {
        "@type": "Service",
        name: "DefendableRouter Insurance Baseline",
        description:
          "Carrier-ready evidence pack · DDEED-DOV-AGENT records · quarterly Operator Statement · direct introductions to AI insurance carriers.",
        provider: { "@id": "https://defendablerouter.com/#org" },
      },
    ],
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}

import { FormEvent, useState } from "react";

const SALES_EMAIL = "build@swarmandbee.ai";
const GITHUB_REPO_URL = "https://github.com/SudoSuOps/defendable-router";
const DEFENDABLEOS_URL = "https://defendableos.com";
const DEFENDABLECLOUD_URL = "https://defendablecloud.com/agent-operations-demo";
const DOCS_URL = "https://defendabledocs.com/field-release/overview/";
const TRIBUNAL_URL =
  "https://github.com/SudoSuOps/defendableos-tribunal-audit/tree/main/deployed_audit/2026-05-26_field_utilization_router_docs_v0.1_reaudit";

const BADGES = [
  "FIELD INTEGRATION PENDING",
  "NOT_YET_INTEGRATED",
  "PUBLIC DEPLOYED ROUTER UTILITY NOT VERIFIED",
  "LOCAL SOURCE DEMO ONLY",
];

const TODAY = [
  "Public positioning site and public source repository are live.",
  "The repo contains local receipt-spine code that can be inspected and built locally.",
  "The site links to DefendableCloud, DefendableDocs, and the public tribunal audit tape.",
  "Contact intake is live at build@swarmandbee.ai.",
];

const NOT_VERIFIED = [
  "Public deployed router middleware utility",
  "DefendableCloud integration in the live public demo path",
  "Receipt creation for every routed public call",
  "Write-only behavior on a public deployed surface",
  "Sub-5ms public deployed overhead",
  "ENS-signed receipts, daily reconciliation deeds, carrier-ready evidence, or insurance posture",
];

const LIMITATIONS = [
  "This surface is a public positioning and local source demonstration surface.",
  "DefendableCloud currently demonstrates a server-side synthetic Pages Functions flow, not Router integration.",
  "No production clearance, external SaaS enforcement, certification, insurance coverage, or blockchain anchoring is claimed.",
  "SHA-256 evidence in this prototype establishes content-integrity linkage only.",
];

export default function DefendableRouter() {
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 antialiased">
      <StatusRibbon />
      <Header />
      <main>
        <Hero />
        <TruthGrid />
        <WhatYouCanUse />
        <WhatIsNotProven />
        <LimitationsPanel />
        <RelationshipMap />
        <SourceAndAudit />
        <ContactSection />
      </main>
      <Footer />
    </div>
  );
}

function StatusRibbon() {
  return (
    <div className="border-b border-amber-500/30 bg-amber-500/10 px-4 py-3 text-center text-xs text-amber-100 sm:text-sm">
      <strong>STATUS:</strong> DefendableRouter is currently a public positioning and local source
      demonstration surface. Public deployed router middleware is not yet independently verified.
      DefendableCloud integration is not yet proven. Field integration remains pending.
    </div>
  );
}

function Header() {
  const navItems: [string, string][] = [
    ["Status", "#status"],
    ["Use today", "#use-today"],
    ["Limits", "#limits"],
    ["Sources", "#sources"],
    ["Contact", "#contact"],
  ];

  return (
    <header className="sticky top-0 z-20 border-b border-stone-800 bg-stone-950/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <a href="/" className="font-semibold tracking-tight text-stone-50">
          Defendable<span className="text-amber-300">Router</span>
        </a>
        <nav className="hidden gap-5 text-xs uppercase tracking-[0.18em] text-stone-400 md:flex">
          {navItems.map(([label, href]) => (
            <a key={href} href={href} className="transition-colors hover:text-amber-300">
              {label}
            </a>
          ))}
        </nav>
        <a
          href={GITHUB_REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded border border-amber-500/40 px-3 py-1.5 text-xs uppercase tracking-[0.18em] text-amber-300 transition-colors hover:bg-amber-500/10"
        >
          View repo
        </a>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section id="status" className="border-b border-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-20 lg:py-24">
        <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">
          PUBLIC STATUS SURFACE
        </p>
        <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight text-stone-50 md:text-6xl">
          DefendableRouter
        </h1>
        <p className="mt-6 max-w-3xl text-xl text-stone-300 md:text-2xl">
          Public positioning, local source inspection, and audit status for the Router track.
        </p>
        <p className="mt-8 max-w-3xl text-base leading-relaxed text-stone-400">
          This site is not presenting a field-cleared router utility. It exists so an operator can
          see the current Router status, inspect the public source, understand what is and is not
          proven, and follow the audit tape without confusing roadmap language for deployed
          functionality.
        </p>

        <div className="mt-10 flex flex-wrap gap-2">
          {BADGES.map((badge) => (
            <StatusBadge key={badge}>{badge}</StatusBadge>
          ))}
        </div>

        <div className="mt-10 flex flex-wrap gap-3">
          <ActionLink href={GITHUB_REPO_URL} label="Open source repo" />
          <ActionLink href={TRIBUNAL_URL} label="Read audit tape" />
          <ActionLink href={DEFENDABLECLOUD_URL} label="View Cloud demo" />
          <ActionLink href="#contact" label="Contact build@swarmandbee.ai" />
        </div>
      </div>
    </section>
  );
}

function TruthGrid() {
  const items = [
    {
      title: "Current public role",
      body: "Positioning and local source demonstration surface only.",
    },
    {
      title: "Cloud path status",
      body: "Not proven to be in the live DefendableCloud demo path.",
    },
    {
      title: "Public utility status",
      body: "Public deployed Router utility not independently verified.",
    },
    {
      title: "Field readiness",
      body: "Field integration pending. Not cleared for production or external SaaS enforcement.",
    },
  ];

  return (
    <section className="border-b border-stone-900 bg-stone-950/70">
      <div className="mx-auto grid max-w-6xl gap-6 px-6 py-16 md:grid-cols-2 lg:grid-cols-4">
        {items.map((item) => (
          <div key={item.title} className="border border-stone-800 bg-stone-950/70 p-5">
            <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80">
              Current truth
            </div>
            <h2 className="mt-3 text-lg font-semibold tracking-tight text-stone-50">
              {item.title}
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-stone-400">{item.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function WhatYouCanUse() {
  return (
    <section id="use-today" className="border-b border-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-18 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[1.1fr,0.9fr]">
          <div>
            <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">
              What exists today
            </p>
            <h2 className="mt-5 max-w-2xl text-3xl font-semibold tracking-tight text-stone-50 md:text-4xl">
              What a public operator can truthfully use right now.
            </h2>
            <ul className="mt-8 space-y-4 text-sm leading-relaxed text-stone-300">
              {TODAY.map((item) => (
                <li key={item} className="border-l border-amber-500/30 pl-4">
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="border border-stone-800 bg-stone-950/70 p-6">
            <div className="text-[10px] uppercase tracking-[0.22em] text-stone-500">
              Local source demo
            </div>
            <p className="mt-4 text-sm leading-relaxed text-stone-400">
              The repo includes a local `spine/` path that can be inspected and built as source
              material. That is not the same thing as a publicly verified deployed router service.
            </p>
            <div className="mt-6 space-y-3 text-sm text-stone-300">
              <div>
                Repo:{" "}
                <a
                  className="text-amber-300 hover:text-amber-200"
                  href={GITHUB_REPO_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  github.com/SudoSuOps/defendable-router
                </a>
              </div>
              <div>
                Docs:{" "}
                <a
                  className="text-amber-300 hover:text-amber-200"
                  href="https://defendabledocs.com/defendablerouter/overview/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Router status pages
                </a>
              </div>
              <div>
                Audit:{" "}
                <a
                  className="text-amber-300 hover:text-amber-200"
                  href={TRIBUNAL_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Codex re-audit record
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function WhatIsNotProven() {
  return (
    <section id="limits" className="border-b border-stone-900 bg-stone-950/70">
      <div className="mx-auto max-w-6xl px-6 py-18 lg:py-20">
        <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">What is not proven</p>
        <h2 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-stone-50 md:text-4xl">
          These claims are not fielded here and should not be read as deployed functionality.
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {NOT_VERIFIED.map((item) => (
            <div key={item} className="border border-stone-800 bg-stone-950/80 p-4 text-sm text-stone-300">
              {item}
            </div>
          ))}
        </div>
        <div className="mt-8 border border-amber-500/20 bg-amber-500/5 p-5 text-sm leading-relaxed text-stone-300">
          Roadmap language is allowed here only as roadmap language. It is not certification,
          insurance, authorship proof, production clearance, blockchain anchoring, or external SaaS
          enforcement.
        </div>
      </div>
    </section>
  );
}

function LimitationsPanel() {
  return (
    <section className="border-b border-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">Limitations</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {LIMITATIONS.map((item) => (
            <div key={item} className="border border-stone-800 bg-stone-950/70 p-4 text-sm leading-relaxed text-stone-400">
              {item}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function RelationshipMap() {
  const surfaces = [
    {
      name: "DefendableCloud",
      status: "READY_WITH_LIMITATIONS",
      body: "Live server-side synthetic Pages Functions demo. Router is not proven to be in that path.",
      href: DEFENDABLECLOUD_URL,
    },
    {
      name: "DefendableDocs",
      status: "READY_WITH_LIMITATIONS",
      body: "Owner record and client-use manual. Router pages are labeled roadmap / not yet integrated.",
      href: DOCS_URL,
    },
    {
      name: "Tribunal audit",
      status: "PUBLIC TAPE",
      body: "Independent audit record. Not certification or production clearance.",
      href: TRIBUNAL_URL,
    },
  ];

  return (
    <section className="border-b border-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-18 lg:py-20">
        <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">Relationship map</p>
        <h2 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-stone-50 md:text-4xl">
          How Router relates to the rest of the public field system today.
        </h2>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {surfaces.map((surface) => (
            <a
              key={surface.name}
              href={surface.href}
              target="_blank"
              rel="noopener noreferrer"
              className="border border-stone-800 bg-stone-950/70 p-5 transition-colors hover:border-amber-500/40"
            >
              <div className="text-[10px] uppercase tracking-[0.22em] text-amber-400/80">
                {surface.status}
              </div>
              <h3 className="mt-3 text-xl font-semibold tracking-tight text-stone-50">
                {surface.name}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-stone-400">{surface.body}</p>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

function SourceAndAudit() {
  return (
    <section id="sources" className="border-b border-stone-900 bg-stone-950/70">
      <div className="mx-auto max-w-6xl px-6 py-18 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[1fr,1fr]">
          <div>
            <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">Source and audit</p>
            <h2 className="mt-5 max-w-2xl text-3xl font-semibold tracking-tight text-stone-50 md:text-4xl">
              Public source and public referee tape.
            </h2>
            <p className="mt-6 text-sm leading-relaxed text-stone-400">
              If you are evaluating this track, start with the source, then read the audit. That is
              the current accountable path.
            </p>
          </div>
          <div className="space-y-4">
            <SurfaceLink
              title="Router source repository"
              href={GITHUB_REPO_URL}
              body="Public repo including the local spine source and release history."
            />
            <SurfaceLink
              title="Current audit tape"
              href={TRIBUNAL_URL}
              body="Most recent deployed-field re-audit for Router, Cloud, and Docs."
            />
            <SurfaceLink
              title="DefendableOS front door"
              href={DEFENDABLEOS_URL}
              body="Main franchise surface with current public status labels."
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function SurfaceLink({ title, href, body }: { title: string; href: string; body: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="block border border-stone-800 bg-stone-950/80 p-5 transition-colors hover:border-amber-500/40"
    >
      <h3 className="text-lg font-semibold tracking-tight text-stone-50">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-stone-400">{body}</p>
    </a>
  );
}

function ContactSection() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setStatus(null);
    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          company,
          lane: "router-status-review",
          message,
        }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        setStatus(typeof body.error === "string" ? body.error : "Request failed");
      } else {
        setStatus("Sent to build@swarmandbee.ai");
        setName("");
        setEmail("");
        setCompany("");
        setMessage("");
      }
    } catch {
      setStatus("Network error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section id="contact" className="border-b border-stone-900">
      <div className="mx-auto max-w-6xl px-6 py-18 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[0.9fr,1.1fr]">
          <div>
            <p className="text-[11px] uppercase tracking-[0.24em] text-amber-400/80">Contact</p>
            <h2 className="mt-5 max-w-xl text-3xl font-semibold tracking-tight text-stone-50 md:text-4xl">
              Ask for a source review, audit walkthrough, or early roadmap discussion.
            </h2>
            <p className="mt-6 text-sm leading-relaxed text-stone-400">
              This is not a public production intake lane. It is a builder contact surface for
              source review and roadmap discussion only.
            </p>
            <div className="mt-6 text-sm text-stone-300">
              Contact:{" "}
              <a className="text-amber-300 hover:text-amber-200" href={`mailto:${SALES_EMAIL}`}>
                {SALES_EMAIL}
              </a>
            </div>
          </div>
          <form onSubmit={onSubmit} className="border border-stone-800 bg-stone-950/70 p-6">
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Name">
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full border border-stone-700 bg-stone-950 px-3 py-2 text-sm text-stone-100 outline-none focus:border-amber-500/50"
                />
              </Field>
              <Field label="Email">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full border border-stone-700 bg-stone-950 px-3 py-2 text-sm text-stone-100 outline-none focus:border-amber-500/50"
                />
              </Field>
            </div>
            <div className="mt-4">
              <Field label="Company">
                <input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full border border-stone-700 bg-stone-950 px-3 py-2 text-sm text-stone-100 outline-none focus:border-amber-500/50"
                />
              </Field>
            </div>
            <div className="mt-4">
              <Field label="Message">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
                  rows={6}
                  className="w-full border border-stone-700 bg-stone-950 px-3 py-2 text-sm text-stone-100 outline-none focus:border-amber-500/50"
                />
              </Field>
            </div>
            <div className="mt-5 flex items-center justify-between gap-4">
              <button
                type="submit"
                disabled={submitting}
                className="rounded border border-amber-500/40 bg-amber-500/10 px-4 py-2 text-xs uppercase tracking-[0.18em] text-amber-300 transition-colors hover:bg-amber-500/20 disabled:opacity-60"
              >
                {submitting ? "Sending" : "Send"}
              </button>
              {status && <div className="text-sm text-stone-400">{status}</div>}
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <div className="mb-2 text-[10px] uppercase tracking-[0.22em] text-stone-500">{label}</div>
      {children}
    </label>
  );
}

function Footer() {
  return (
    <footer className="mx-auto max-w-6xl px-6 py-8 text-xs text-stone-500">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>DefendableRouter · public positioning and local source demonstration surface.</div>
        <div className="flex flex-wrap gap-4">
          <a href={GITHUB_REPO_URL} target="_blank" rel="noopener noreferrer" className="hover:text-amber-300">
            GitHub
          </a>
          <a href={DOCS_URL} target="_blank" rel="noopener noreferrer" className="hover:text-amber-300">
            Docs
          </a>
          <a href={TRIBUNAL_URL} target="_blank" rel="noopener noreferrer" className="hover:text-amber-300">
            Audit tape
          </a>
          <a href={`mailto:${SALES_EMAIL}`} className="hover:text-amber-300">
            {SALES_EMAIL}
          </a>
        </div>
      </div>
      <div className="mt-3 max-w-4xl text-stone-600">
        SHA-256 evidence in this prototype establishes content-integrity linkage only. It does not
        independently prove authorship, owner approval, trusted timestamping, immutability,
        blockchain anchoring, certification, insurance coverage, production clearance, or external
        platform enforcement.
      </div>
    </footer>
  );
}

function StatusBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-amber-200">
      {children}
    </span>
  );
}

function ActionLink({ href, label }: { href: string; label: string }) {
  const external = href.startsWith("http");
  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className="border border-stone-700 px-4 py-2 text-xs uppercase tracking-[0.18em] text-stone-300 transition-colors hover:border-amber-500/40 hover:text-amber-300"
    >
      {label}
    </a>
  );
}

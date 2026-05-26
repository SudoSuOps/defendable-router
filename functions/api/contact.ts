interface Env {
  RESEND_API_KEY: string;
  CONTACT_TO_EMAIL?: string;
  CONTACT_FROM_EMAIL?: string;
}

interface ContactPayload {
  name?: string;
  email?: string;
  company?: string;
  lane?: string;
  message?: string;
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  if (!env.RESEND_API_KEY) return json({ error: "RESEND_API_KEY not configured" }, 503);

  const TO = env.CONTACT_TO_EMAIL || "build@swarmandbee.ai";
  const FROM = env.CONTACT_FROM_EMAIL || "build@swarmandbee.ai";

  let body: ContactPayload;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400);
  }

  const name = sanitize(body.name, 200);
  const email = sanitize(body.email, 320);
  const company = sanitize(body.company, 200);
  const lane = sanitize(body.lane, 80) || "other";
  const message = sanitize(body.message, 5000);

  if (!name || !email || !message) return json({ error: "name · email · message are required" }, 400);
  if (!isEmail(email)) return json({ error: "Invalid email" }, 400);
  if (message.length < 10) return json({ error: "Message too short" }, 400);

  const timestamp = new Date().toISOString();
  const subject = `[DEFENDABLEROUTER:${lane.toUpperCase()}] ${name}${company ? ` · ${company}` : ""}`;
  const text = [
    `Lane:    ${lane}`,
    `Name:    ${name}`,
    `Email:   ${email}`,
    company ? `Company: ${company}` : null,
    "",
    "Message:",
    "─────────",
    message,
    "─────────",
    "",
    `(sent via defendablerouter.com · ${timestamp})`,
  ].filter(Boolean).join("\n");

  try {
    const resendRes = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: FROM,
        to: TO,
        reply_to: email,
        subject,
        text,
        html: `<pre style="white-space:pre-wrap;font-family:ui-monospace,Menlo,monospace">${escape(text)}</pre>`,
      }),
    });
    if (!resendRes.ok) return json({ error: `Mail provider returned ${resendRes.status}` }, 502);
    return json({ ok: true });
  } catch {
    return json({ error: "Network failure to mail provider" }, 502);
  }
};

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}
function sanitize(s: string | undefined, max: number): string { return !s || typeof s !== "string" ? "" : s.trim().slice(0, max); }
function isEmail(s: string): boolean { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s); }
function escape(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

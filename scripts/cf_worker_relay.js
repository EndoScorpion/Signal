// cf_worker_relay.js — Cloudflare Worker KV relay
// KV namespace binding: RELAY_KV
// Secret: RELAY_SECRET (wrangler secret put RELAY_SECRET)
// Deploy: wrangler deploy
//
// PUT /relay?key=X  + Authorization: Bearer <secret>  -> write val from JSON body
// GET /relay?key=X  + Authorization: Bearer <secret>  -> read last val

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    // Auth check
    const auth = request.headers.get("Authorization") || "";
    const secret = env.RELAY_SECRET || "";
    if (secret && auth !== `Bearer ${secret}`) {
      return new Response(JSON.stringify({ ok: false, err: "unauthorized" }), {
        status: 401, headers: { ...CORS, "Content-Type": "application/json" }
      });
    }

    const url = new URL(request.url);
    const key = url.searchParams.get("key") || "default";
    const kvKey = `relay:${key}`;

    if (request.method === "PUT") {
      // Rate limit: check last write time
      const meta = await env.RELAY_KV.get(`meta:${key}`, { type: "json" });
      const now = Date.now();
      if (meta && (now - meta.lastWrite) < 30000) {
        return new Response(JSON.stringify({ ok: false, err: "rate_limited" }), {
          status: 429, headers: { ...CORS, "Content-Type": "application/json" }
        });
      }

      const body = await request.json().catch(() => ({}));
      const val = JSON.stringify({ ...body, ts: now });
      await env.RELAY_KV.put(kvKey, val, { expirationTtl: 600 });
      await env.RELAY_KV.put(`meta:${key}`, JSON.stringify({ lastWrite: now }), { expirationTtl: 600 });

      return new Response(JSON.stringify({ ok: true, ts: now }), {
        headers: { ...CORS, "Content-Type": "application/json" }
      });
    }

    if (request.method === "GET") {
      const val = await env.RELAY_KV.get(kvKey);
      return new Response(val || JSON.stringify({ ok: true, val: null }), {
        headers: { ...CORS, "Content-Type": "application/json" }
      });
    }

    return new Response("method not allowed", { status: 405 });
  }
};

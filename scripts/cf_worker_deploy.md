# CF Worker Relay — Deploy Instructions

## Prerequisites
- Cloudflare account (free tier OK)
- Node.js + wrangler: `npm install -g wrangler`
- Login: `wrangler login`

## Steps

1. **Create KV namespace:**
   ```
   wrangler kv:namespace create RELAY_KV
   ```
   Copy the `id` from output → paste into `wrangler.toml` replacing `REPLACE_WITH_KV_NAMESPACE_ID`

2. **Set secret:**
   ```
   wrangler secret put RELAY_SECRET
   ```
   Enter a random string (keep it private, share via RELAY_SECRET env var).

3. **Deploy:**
   ```
   wrangler deploy
   ```
   Note your worker URL: `https://signal-relay.<your-subdomain>.workers.dev`

4. **Set env vars on laptop/cloud:**
   ```
   $env:CF_RELAY_URL = "https://signal-relay.<subdomain>.workers.dev"
   $env:CF_RELAY_SECRET = "<secret from step 2>"
   $env:RELAY_TOPIC = "<16-char hex hash>"  # optional, auto-derived if unset
   ```

5. **Test:**
   ```
   .\ntfy_relay.ps1 -Mode test
   ```

## Usage
- Publish: `.\ntfy_relay.ps1 -Mode pub -Msg "WR 64% PF 2.9"`
- Poll: `.\ntfy_relay.ps1 -Mode poll -PollInterval 60`
- Cascade: ntfy.sh tried first (5s timeout); auto-falls back to CF Worker on any failure.

## Free tier limits
- KV: 100k reads/day, 1k writes/day — well within relay needs at 30s+ intervals.

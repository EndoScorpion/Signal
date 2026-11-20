# Slack Bridge Setup

This guide explains how to wire up 2-way communication between Claude Code and a Slack workspace using `tools/slack_bridge.py`.

---

## 1. Create a Slack App and get an Incoming Webhook URL

1. Go to https://api.slack.com/apps and click **Create New App** > **From scratch**.
2. Give it a name (e.g. "Claude Code Bridge") and pick your workspace.
3. In the left sidebar, click **Incoming Webhooks** and toggle **Activate Incoming Webhooks** to On.
4. Click **Add New Webhook to Workspace**, choose a channel, and click **Allow**.
5. Copy the generated Webhook URL — it looks like:
   `https://hooks.slack.com/services/T.../B.../xxxx`

---

## 2. Set environment variables

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../xxxx"

# Optional — enables HMAC signature verification on inbound requests
export SLACK_SIGNING_SECRET="your_signing_secret"
```

To find `SLACK_SIGNING_SECRET`: in your Slack App settings go to **Basic Information** > **App Credentials** > **Signing Secret**.

---

## 3. Install dependencies

```bash
pip install -r tools/requirements_slack.txt
```

---

## 4. Test outbound (post a message to Slack)

```bash
python3 tools/slack_bridge.py --post
```

You should see the test message appear in your configured Slack channel.

Post a custom message:

```bash
python3 tools/slack_bridge.py --post --message "Backtest complete — check results/SURVIVORS.md"
```

---

## 5. Run the inbound server (receive Slack events / slash commands)

```bash
python3 tools/slack_bridge.py --server --port 5000
```

The server listens on `POST /slack/events`.

### Exposing the server to the internet

Slack needs a publicly reachable URL to deliver events. Use **ngrok** (or a similar tunnel):

```bash
ngrok http 5000
```

ngrok prints a forwarding URL like `https://abc123.ngrok.io`. Set that as your Slack App's **Event Subscriptions** Request URL:

```
https://abc123.ngrok.io/slack/events
```

Slack will send a one-time URL verification challenge — the server handles this automatically.

For slash commands, add the same URL under **Slash Commands** in your Slack App settings.

---

## 6. Run both outbound test + server together (default mode)

```bash
python3 tools/slack_bridge.py
```

This posts a test message and then starts the inbound server.

---

## Notes

- `SLACK_SIGNING_SECRET` is optional but recommended for production use. Without it, any HTTP client can send requests to the server.
- The server prints all received events/commands to stdout.
- For slash commands, the server replies ephemerally (visible only to the invoking user).
- This bridge is for development and research automation only — it does not place any orders.

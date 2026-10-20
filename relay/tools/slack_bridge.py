#!/usr/bin/env python3
"""
Slack <-> Claude Code 2-way bridge.
Credentials loaded from env vars or /mnt/project-files/config/slack_config.json
Never hardcode tokens in this file.
"""
import json, os, time, urllib.request, urllib.error
from datetime import datetime, timezone

def load_config():
    cfg = {}
    cfg_file = "/mnt/project-files/config/slack_config.json"
    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            cfg = json.load(f)
    return {
        "bot_token": os.environ.get("SLACK_BOT_TOKEN", cfg.get("bot_token", "")),
        "channel_id": os.environ.get("SLACK_CHANNEL_ID", cfg.get("channel_id", "")),
        "trigger_keyword": os.environ.get("SLACK_TRIGGER_KEYWORD", cfg.get("trigger_keyword", "!claude")),
        "claude_webhook_url": os.environ.get("CLAUDE_WEBHOOK_URL", cfg.get("claude_webhook_url", "")),
        "slack_outbound_webhook": os.environ.get("SLACK_OUTBOUND_WEBHOOK", cfg.get("slack_outbound_webhook", "")),
    }

def slack_api(token, method, params):
    url = f"https://slack.com/api/{method}"
    data = json.dumps(params).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[{ts()}] slack_api error: {e}")
        return {}

def post_slack(webhook_url, text):
    if not webhook_url:
        return
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[{ts()}] post_slack error: {e}")

def fire_claude_webhook(webhook_url, message_text):
    if not webhook_url:
        print(f"[{ts()}] No claude_webhook_url configured")
        return
    data = json.dumps({"message": message_text}).encode()
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[{ts()}] Claude webhook fired: {r.status}")
    except Exception as e:
        print(f"[{ts()}] claude webhook error: {e}")

def ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def main():
    cfg = load_config()
    if not cfg["bot_token"] or not cfg["channel_id"]:
        print(f"[{ts()}] ERROR: bot_token and channel_id required. Set env vars or create /mnt/project-files/config/slack_config.json")
        return
    print(f"[{ts()}] Slack bridge started. Watching channel {cfg['channel_id']} for '{cfg['trigger_keyword']}'")
    last_ts = str(time.time())
    while True:
        try:
            resp = slack_api(cfg["bot_token"], "conversations.history", {
                "channel": cfg["channel_id"],
                "oldest": last_ts,
                "limit": 10
            })
            msgs = resp.get("messages", [])
            for msg in reversed(msgs):
                msg_ts = msg.get("ts", "0")
                if msg_ts <= last_ts:
                    continue
                text = msg.get("text", "")
                if cfg["trigger_keyword"] in text:
                    print(f"[{ts()}] Trigger '{cfg['trigger_keyword']}' detected: firing Claude webhook")
                    fire_claude_webhook(cfg["claude_webhook_url"], text)
                    post_slack(cfg["slack_outbound_webhook"], f"Claude Code triggered by: {text[:100]}")
                last_ts = max(last_ts, msg_ts)
        except Exception as e:
            print(f"[{ts()}] loop error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()

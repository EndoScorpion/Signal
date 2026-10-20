#!/usr/bin/env python3
"""
Slack <-> Claude Code 2-way bridge.
Credentials loaded from env vars or /mnt/project-files/config/slack_config.json
Never hardcode tokens in this file.
"""
import base64, json, os, time, urllib.request, urllib.error
from datetime import datetime, timezone

GITHUB_REPO = "EndoScorpion/Signal"
CMD_QUEUE_PATH = "relay/cmd_queue.json"
CMD_QUEUE_BRANCH = "relay"

def load_config():
    cfg = {}
    local_cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slack_config.json")
    mnt_cfg_file = "/mnt/project-files/config/slack_config.json"
    if os.path.exists(local_cfg_file):
        with open(local_cfg_file) as f:
            cfg = json.load(f)
    elif os.path.exists(mnt_cfg_file):
        with open(mnt_cfg_file) as f:
            cfg = json.load(f)
    # Try multiple env var names for the GitHub token
    github_token = (
        os.environ.get("GITHUB_RELAY_TOKEN") or
        os.environ.get("GITHUB_TOKEN") or
        os.environ.get("GH_TOKEN") or
        cfg.get("github_relay_token", "")
    )
    return {
        "bot_token": os.environ.get("SLACK_BOT_TOKEN", cfg.get("bot_token", "")),
        "channel_id": os.environ.get("SLACK_CHANNEL_ID", cfg.get("channel_id", "")),
        "trigger_keyword": os.environ.get("SLACK_TRIGGER_KEYWORD", cfg.get("trigger_keyword", "!claude")),
        "github_relay_token": github_token,
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

def github_api(token, method, path, body=None):
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[{ts()}] github_api {method} {path} error {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"[{ts()}] github_api error: {e}")
        return None

def append_to_cmd_queue(github_token, message_text, slack_username):
    """Append a job entry to relay/cmd_queue.json on the relay branch via GitHub API."""
    if not github_token:
        print(f"[{ts()}] No GitHub token configured; cannot append to cmd_queue.json")
        return False
    # Fetch current file
    resp = github_api(github_token, "GET",
        f"/repos/{GITHUB_REPO}/contents/{CMD_QUEUE_PATH}?ref={CMD_QUEUE_BRANCH}")
    if resp is None:
        return False
    file_sha = resp["sha"]
    current_content = base64.b64decode(resp["content"].replace("\n", "")).decode("utf-8-sig")
    queue = json.loads(current_content)
    # Strip !claude prefix
    cmd_text = message_text
    kw = "!claude"
    if cmd_text.strip().startswith(kw):
        cmd_text = cmd_text.strip()[len(kw):].strip()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    job_id = f"slack_{int(time.time())}"
    entry = {
        "id": job_id,
        "command": cmd_text,
        "shell": "slack",
        "status": "pending",
        "ts": now_iso,
        "source": "slack:#claude-ops",
        "from": slack_username
    }
    queue.append(entry)
    new_content = json.dumps(queue, indent=4, ensure_ascii=False)
    encoded = base64.b64encode(new_content.encode()).decode()
    put_resp = github_api(github_token, "PUT",
        f"/repos/{GITHUB_REPO}/contents/{CMD_QUEUE_PATH}",
        {
            "message": f"slack: append job {job_id} from {slack_username}",
            "content": encoded,
            "sha": file_sha,
            "branch": CMD_QUEUE_BRANCH
        }
    )
    if put_resp:
        print(f"[{ts()}] Appended job {job_id} to cmd_queue.json")
        return True
    return False

def ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def main():
    cfg = load_config()
    if not cfg["bot_token"] or not cfg["channel_id"]:
        print(f"[{ts()}] ERROR: bot_token and channel_id required. Set env vars, create slack_config.json next to this script, or create /mnt/project-files/config/slack_config.json")
        return
    if not cfg["github_relay_token"]:
        print(f"[{ts()}] WARNING: GITHUB_RELAY_TOKEN not set; !claude triggers will not be queued")
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
                username = msg.get("username") or msg.get("user", "unknown")
                if cfg["trigger_keyword"] in text:
                    print(f"[{ts()}] Trigger '{cfg['trigger_keyword']}' detected from {username}: queuing to cmd_queue.json")
                    ok = append_to_cmd_queue(cfg["github_relay_token"], text, username)
                    ack = "✅ Queued to relay" if ok else "❌ Failed to queue (check GITHUB_RELAY_TOKEN)"
                    post_slack(cfg["slack_outbound_webhook"], f"{ack}: `{text[:100]}`")
                last_ts = max(last_ts, msg_ts)
        except Exception as e:
            print(f"[{ts()}] loop error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()

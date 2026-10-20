#!/usr/bin/env python3
"""
coord_post.py — shared chat bus via data/chat_bus.json
Usage:
  python3 scripts/coord_post.py "message" --session GOON
  python3 scripts/coord_post.py --read --last 20
  python3 scripts/coord_post.py --read --since 2026-10-20T02:00:00Z
"""
import json, argparse, sys, os, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BUS = Path(__file__).parent.parent / "data" / "chat_bus.json"

def load():
    if BUS.exists():
        return json.loads(BUS.read_text())
    return {"messages": []}

def save(data):
    BUS.write_text(json.dumps(data, indent=2))

def post(msg, session, msg_type="INFO"):
    data = load()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"ts": ts, "session": session, "type": msg_type, "msg": msg}
    data["messages"].append(entry)
    save(data)
    print(f"[{ts}] {session}: {msg}")

    # ntfy
    try:
        topic = os.environ.get("COORD_TOPIC", "signal-coord")
        req = urllib.request.Request(
            f"https://ntfy.sh/{topic}",
            data=msg.encode(),
            headers={"Title": f"[{session}] [{msg_type}] {msg[:60]}", "Content-Type": "text/plain"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
        print(f"✓ ntfy #{topic}")
    except Exception as e:
        print(f"✗ ntfy: {e}")

    # Slack webhook
    webhook = os.environ.get("SLACK_WEBHOOK", "")
    if webhook:
        try:
            payload = json.dumps({"text": f"*[{session}]* `{msg_type}` {msg}"}).encode()
            req = urllib.request.Request(webhook, data=payload,
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=5)
            print("✓ Slack")
        except Exception as e:
            print(f"✗ Slack: {e}")

def read(last=20, since=None):
    data = load()
    msgs = data["messages"]
    if since:
        msgs = [m for m in msgs if m["ts"] >= since]
    for m in msgs[-last:]:
        print(f"[{m['ts']}] {m['session']}: {m['msg']}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("message", nargs="?")
    p.add_argument("--session", default=os.environ.get("COORD_AGENT", "unknown"))
    p.add_argument("--type", default="INFO", dest="msg_type")
    p.add_argument("--read", action="store_true")
    p.add_argument("--last", type=int, default=20)
    p.add_argument("--since")
    args = p.parse_args()
    if args.read:
        read(args.last, args.since)
    elif args.message:
        post(args.message, args.session, args.msg_type)
    else:
        p.print_help(); sys.exit(1)

#!/usr/bin/env python3
"""
broadcast_all.py — multi-channel broadcast for important results/signals.
Usage: python3 broadcast_all.py --type RESULT --body "WR 75% PF 5.2 n=36 #StackC"
       python3 broadcast_all.py --test   (dry-run all channels, no actual send)
Channels: Git relay, Gmail (stub), signal-board, hastebin fallback.
Secret: loaded from env var SLC_RELAY_SECRET (never commit the value).
"""

import argparse, hashlib, hmac, json, os, sys, subprocess
import datetime, urllib.request


def utcnow():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def make_sig(ts, msg_type, body, secret):
    payload = f"{ts}|{msg_type}|{body}".encode()
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_sig(ts, msg_type, body, sig, secret):
    return hmac.compare_digest(make_sig(ts, msg_type, body, secret), sig)


def build_msg(msg_type, body, secret):
    ts = utcnow()
    return {"ts": ts, "sig": make_sig(ts, msg_type, body, secret),
            "type": msg_type, "body": body}


# ── Channel 1: Git relay ──────────────────────────────────────────────────────

def ch_git_relay(msg, dry_run=False):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relay", "to_cli.json")
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(msg)
    if dry_run:
        print(f"[DRY] git-relay -> {path}")
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    root = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["git", "add", path], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m",
                    f"relay: broadcast {msg['type']} {msg['ts'][:10]}"], cwd=root, check=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=root, check=True)
    print("[OK] git-relay")
    return True


# ── Channel 2: Gmail (stub — invoke Gmail MCP from Claude session) ────────────

def ch_gmail(msg, recipient="endoscorpion@gmail.com", dry_run=False):
    subject = f"[SLC] {msg['type']} {msg['ts'][:10]}"
    body_text = (
        f"Type: {msg['type']}\nTime: {msg['ts']}\n"
        f"Body: {msg['body']}\nsig: {msg['sig'][:16]}…\n"
        "(Verify sig before acting)"
    )
    if dry_run:
        print(f"[DRY] gmail -> {recipient} | {subject}")
        return True
    # Gmail MCP is invoked by the Claude session (not from CLI).
    # Print stub so caller knows to handle it.
    print(f"[STUB] gmail -> use Gmail MCP send_message externally\n  Subject: {subject}")
    return False


# ── Channel 3: signal-board ───────────────────────────────────────────────────

def ch_signal_board(msg, dry_run=False):
    board_repo = "https://github.com/EndoScorpion/signal-board.git"
    tmp = "/tmp/sb_bc"
    if dry_run:
        print("[DRY] signal-board -> board.json append")
        return True
    try:
        subprocess.run(["git", "clone", "--depth=1", board_repo, tmp], check=True)
        path = os.path.join(tmp, "board.json")
        try:
            with open(path) as f:
                board = json.load(f)
        except Exception:
            board = []
        board.insert(0, {"ts": msg["ts"], "type": msg["type"],
                         "summary": msg["body"][:120]})
        with open(path, "w") as f:
            json.dump(board, f, indent=2)
        subprocess.run(["git", "-C", tmp, "add", "board.json"], check=True)
        subprocess.run(["git", "-C", tmp, "commit", "-m",
                        f"broadcast {msg['type']} {msg['ts'][:10]}"], check=True)
        subprocess.run(["git", "-C", tmp, "push"], check=True)
        print("[OK] signal-board")
        return True
    except Exception as e:
        print(f"[FAIL] signal-board: {e}")
        return False


# ── Channel 4: Hastebin fallback ──────────────────────────────────────────────

def ch_clipboard_fallback(msg, dry_run=False):
    text = f"[SLC {msg['ts']}] {msg['body']}"
    if dry_run:
        print(f"[DRY] hastebin -> '{text[:60]}...'")
        return True
    try:
        req = urllib.request.Request(
            "https://hastebin.com/documents",
            data=text.encode(), method="POST")
        resp = urllib.request.urlopen(req, timeout=10)
        key = json.loads(resp.read())["key"]
        print(f"[OK] hastebin -> https://hastebin.com/{key}")
        return True
    except Exception as e:
        print(f"[FAIL] hastebin: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Broadcast to all relay channels")
    ap.add_argument("--type", default="RESULT",
                    choices=["RESULT", "SIGNAL", "URGENT", "INFO"])
    ap.add_argument("--body", default="")
    ap.add_argument("--test", action="store_true", help="Dry-run, no actual sends")
    args = ap.parse_args()

    secret = os.environ.get("SLC_RELAY_SECRET", "")
    if not secret:
        print("ERROR: SLC_RELAY_SECRET env var not set", file=sys.stderr)
        sys.exit(1)

    dry = args.test
    body = args.body or "[SLC TEST] WR 75% PF 5.2 n=36 #StackC — auth check only"
    msg = build_msg(args.type, body, secret)

    print(f"Broadcasting: type={msg['type']} ts={msg['ts']}")
    results = {
        "git_relay":    ch_git_relay(msg, dry_run=dry),
        "gmail":        ch_gmail(msg, dry_run=dry),
        "signal_board": ch_signal_board(msg, dry_run=dry),
        "clipboard":    ch_clipboard_fallback(msg, dry_run=dry),
    }
    ok = sum(1 for v in results.values() if v)
    print(f"\nBroadcast complete: {ok}/{len(results)} channels OK — {results}")
    return 0 if ok >= 2 else 1


if __name__ == "__main__":
    sys.exit(main())

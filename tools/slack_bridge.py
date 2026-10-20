"""
slack_bridge.py - 2-way Claude Code <-> Slack bridge.

Outbound: POST a message to a Slack Incoming Webhook.
Inbound:  Flask HTTP server that receives Slack slash-command / event payloads.

Environment variables
---------------------
SLACK_WEBHOOK_URL     Required for outbound posting.
SLACK_SIGNING_SECRET  Optional. When set, inbound requests are verified with
                      Slack's HMAC-SHA256 signing scheme.
"""

import hashlib
import hmac
import json
import os
import sys
import time
import argparse

import requests

# ---------------------------------------------------------------------------
# Outbound
# ---------------------------------------------------------------------------

def post_to_slack(message: str, username: str = "Claude Code") -> bool:
    """
    POST *message* to the Slack Incoming Webhook configured in the environment.

    Returns True on success, False on failure.
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[slack_bridge] ERROR: SLACK_WEBHOOK_URL environment variable is not set.")
        return False

    payload = {
        "username": username,
        "text": message,
    }

    try:
        resp = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code == 200 and resp.text == "ok":
            print(f"[slack_bridge] Message posted: {message!r}")
            return True
        else:
            print(f"[slack_bridge] Post failed: HTTP {resp.status_code} {resp.text!r}")
            return False
    except requests.RequestException as exc:
        print(f"[slack_bridge] Request error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Inbound (Flask server)
# ---------------------------------------------------------------------------

def _verify_slack_signature(request) -> bool:
    """
    Verify that an inbound request was signed by Slack.
    Returns True if verification passes or if SLACK_SIGNING_SECRET is not set.
    """
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if not signing_secret:
        print("[slack_bridge] SLACK_SIGNING_SECRET not set — skipping signature check.")
        return True

    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")

    # Guard against replay attacks (5-minute window)
    try:
        if abs(time.time() - float(timestamp)) > 300:
            print("[slack_bridge] Request timestamp too old — possible replay attack.")
            return False
    except ValueError:
        return False

    sig_basestring = f"v0:{timestamp}:{request.get_data(as_text=True)}"
    computed = "v0=" + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, slack_signature)


def run_server(port: int = 5000) -> None:
    """
    Start a Flask HTTP server that listens for inbound Slack payloads on
    POST /slack/events.

    Handles:
    - Slack URL verification challenge (Events API)
    - Slash command payloads
    - Generic event payloads (printed to stdout)
    """
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("[slack_bridge] Flask is not installed. Run: pip install flask")
        sys.exit(1)

    app = Flask(__name__)

    @app.route("/slack/events", methods=["POST"])
    def slack_events():
        if not _verify_slack_signature(request):
            return jsonify({"error": "invalid signature"}), 403

        content_type = request.content_type or ""

        # Slash command — form-encoded
        if "application/x-www-form-urlencoded" in content_type:
            data = request.form.to_dict()
            user = data.get("user_name", "unknown")
            text = data.get("text", "")
            command = data.get("command", "/slack")
            print(f"[slack_bridge] Slash command from @{user}: {command} {text}")
            # Echo back to the user who invoked the command
            return jsonify({
                "response_type": "ephemeral",
                "text": f"Claude Code received: `{command} {text}`",
            })

        # Events API — JSON
        try:
            body = request.get_json(force=True) or {}
        except Exception:
            body = {}

        # URL verification challenge (one-time setup)
        if body.get("type") == "url_verification":
            challenge = body.get("challenge", "")
            print(f"[slack_bridge] URL verification challenge received.")
            return jsonify({"challenge": challenge})

        # Generic event
        event = body.get("event", {})
        etype = event.get("type", "unknown")
        user = event.get("user", "unknown")
        text = event.get("text", "")
        print(f"[slack_bridge] Event type={etype!r} user={user!r} text={text!r}")

        # Acknowledge immediately (Slack requires a 200 within 3 s)
        return jsonify({"ok": True})

    print(f"[slack_bridge] Server starting on port {port}  (POST /slack/events)")
    app.run(host="0.0.0.0", port=port)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Slack bridge: post messages outbound and/or receive inbound events."
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Post a test message to Slack via the webhook and exit.",
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Start the inbound Flask server only.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for the inbound server (default: 5000).",
    )
    parser.add_argument(
        "--message",
        type=str,
        default="Hello from Claude Code! Slack bridge is working.",
        help="Custom message to post (used with --post).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if args.post and not args.server:
        # Post only
        success = post_to_slack(args.message)
        sys.exit(0 if success else 1)
    elif args.server and not args.post:
        # Server only
        run_server(port=args.port)
    else:
        # Default: post test message then start server
        post_to_slack(args.message)
        run_server(port=args.port)

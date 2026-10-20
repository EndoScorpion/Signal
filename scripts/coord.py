"""
coord.py — Signal 2-way coordination hub
Ties together: chat_bus.json | Slack #new-channel | Claude session send | webhook

Usage:
  python scripts/coord.py post "msg"            # post to all channels
  python scripts/coord.py read [--last N]       # read recent messages
  python scripts/coord.py watch [--interval 10] # poll + print new messages
  python scripts/coord.py slack_read [--last N] # read Slack channel (requires requests)
  python scripts/coord.py slack_post "msg"      # post to Slack incoming webhook
  python scripts/coord.py status               # show bus + config summary

Environment variables (optional):
  SLACK_WEBHOOK_URL   — Slack incoming webhook URL for posting
  COORD_SESSION       — name tag for this session (default: coord)
"""

import json, time, sys, os, argparse, random, string, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUS  = os.path.join(ROOT, 'data', 'chat_bus.json')

# ── helpers ──────────────────────────────────────────────────────────────────

def _load():
    with open(BUS, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save(data):
    with open(BUS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _mkid():
    return 'msg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def _now():
    return int(time.time() * 1000)

def _fmt(ts):
    return datetime.datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S')

# ── core ops ─────────────────────────────────────────────────────────────────

def post_bus(text, session='coord', channel='all'):
    """Append a message to chat_bus.json."""
    data = _load()
    msg = {'id': _mkid(), 'from': session, 'session': session,
           'text': text, 'ts': _now(), 'channel': channel, 'read_by': []}
    data['messages'].append(msg)
    if len(data['messages']) > 500:
        data['messages'] = data['messages'][-500:]
    _save(data)
    return msg

def read_bus(last=20, since_ts=None):
    """Return recent messages from the bus."""
    data = _load()
    msgs = data['messages']
    if since_ts:
        msgs = [m for m in msgs if m.get('ts', 0) > since_ts]
    return msgs[-last:]

def post_slack(text, session='coord'):
    """POST to Slack incoming webhook (SLACK_WEBHOOK_URL env var)."""
    url = os.environ.get('SLACK_WEBHOOK_URL', '')
    if not url:
        return False, 'SLACK_WEBHOOK_URL not set'
    try:
        import urllib.request
        payload = json.dumps({'text': f'*[{session}]* {text}'}).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            return True, r.read().decode()
    except Exception as e:
        return False, str(e)

def post_all(text, session=None):
    """Post to bus + Slack + print confirmation."""
    session = session or os.environ.get('COORD_SESSION', 'coord')
    msg = post_bus(text, session=session)
    ok, detail = post_slack(text, session=session)
    slack_status = 'OK Slack' if ok else f'NO Slack ({detail[:60]})'
    print(f'[{_fmt(msg["ts"])}] {session}: {text}')
    print(f'  bus: {msg["id"]}  |  {slack_status}')
    return msg

def watch(interval=10, session=None):
    """Poll chat_bus.json and print new messages as they arrive."""
    session = session or os.environ.get('COORD_SESSION', 'coord-watch')
    print(f'Watching {BUS} every {interval}s  (Ctrl-C to stop)')
    seen = set(m['id'] for m in read_bus(last=200))
    while True:
        try:
            time.sleep(interval)
            msgs = read_bus(last=50)
            for m in msgs:
                if m['id'] not in seen:
                    seen.add(m['id'])
                    src = m.get('session', m.get('from', '?'))
                    print(f'[{_fmt(m["ts"])}] {src}: {m["text"]}', flush=True)
        except KeyboardInterrupt:
            print('\nwatch stopped')
            break

def status():
    """Print config and last 3 messages."""
    data = _load()
    slack = data.get('slack', {})
    wh    = data.get('webhook', {})
    print('=== Signal Coord Status ===')
    print(f'Bus:     {BUS}')
    print(f'Slack:   #{slack.get("channel_name","?")} ({slack.get("channel_id","?")})')
    print(f'         workspace: {slack.get("workspace","?")}')
    print(f'Webhook: trigger={wh.get("trigger_id","?")}')
    print(f'         note: {wh.get("note","")}')
    print(f'SLACK_WEBHOOK_URL env: {"set" if os.environ.get("SLACK_WEBHOOK_URL") else "NOT SET"}')
    print(f'Messages in bus: {len(data["messages"])}')
    print('--- Last 3 messages ---')
    for m in data['messages'][-3:]:
        print(f'  [{_fmt(m["ts"])}] {m.get("session","?")} -> {m["text"][:80]}')

# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Signal coord hub')
    sub = p.add_subparsers(dest='cmd')

    pp = sub.add_parser('post', help='Post to all channels')
    pp.add_argument('text')
    pp.add_argument('--session', default=None)

    rp = sub.add_parser('read', help='Read recent messages')
    rp.add_argument('--last', type=int, default=20)

    wp = sub.add_parser('watch', help='Watch for new messages')
    wp.add_argument('--interval', type=int, default=10)
    wp.add_argument('--session', default=None)

    sp = sub.add_parser('slack_post', help='Post to Slack webhook')
    sp.add_argument('text')
    sp.add_argument('--session', default=None)

    sub.add_parser('status', help='Show config + recent messages')

    args = p.parse_args()

    if args.cmd == 'post':
        post_all(args.text, session=args.session)
    elif args.cmd == 'read':
        for m in read_bus(args.last):
            print(f'[{_fmt(m["ts"])}] {m.get("session","?")} → {m["text"]}')
    elif args.cmd == 'watch':
        watch(interval=args.interval, session=args.session)
    elif args.cmd == 'slack_post':
        session = args.session or os.environ.get('COORD_SESSION', 'coord')
        ok, detail = post_slack(args.text, session=session)
        print('Slack:', 'OK' if ok else f'FAIL: {detail}')
    elif args.cmd == 'status':
        status()
    else:
        p.print_help()

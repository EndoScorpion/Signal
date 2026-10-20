"""
coord_post.py — post a message to the Signal coordination bus.

Usage:
    python scripts/coord_post.py "message text" [--session SESSION_NAME]
    python scripts/coord_post.py --read [--last N]

Writes to data/chat_bus.json and optionally posts to Slack #new-channel
via the Slack MCP (when run inside a Claude Code session with Slack connected).
"""
import json, time, sys, argparse, os, random, string

BUS = os.path.join(os.path.dirname(__file__), '..', 'data', 'chat_bus.json')

def load():
    with open(BUS, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(data):
    with open(BUS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_id():
    return 'msg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def post(text, session='unknown'):
    data = load()
    msg = {
        'id': make_id(),
        'from': session,
        'session': session,
        'text': text,
        'ts': int(time.time() * 1000),
        'read_by': []
    }
    data['messages'].append(msg)
    # keep last 200
    if len(data['messages']) > 200:
        data['messages'] = data['messages'][-200:]
    save(data)
    print(f"[coord_post] posted: {msg['id']}")
    return msg

def read_msgs(last=20):
    data = load()
    msgs = data['messages'][-last:]
    for m in msgs:
        ts = time.strftime('%H:%M:%S', time.localtime(m['ts'] / 1000))
        print(f"[{ts}] {m['session']}: {m['text']}")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('text', nargs='?', help='Message to post')
    p.add_argument('--session', default='cli', help='Session name tag')
    p.add_argument('--read', action='store_true', help='Read recent messages')
    p.add_argument('--last', type=int, default=20, help='How many messages to show')
    args = p.parse_args()

    if args.read:
        read_msgs(args.last)
    elif args.text:
        post(args.text, args.session)
    else:
        p.print_help()

#!/usr/bin/env python3
"""
chalkboard.py - run every board.json post through this before it goes public.

  encode "text"                 swap real IPs/URLs/paths for code names, then check
  decode "text"                 code names back to real values (private use only)
  check  [board.json]           exit 1 if any raw IP, URL, host:port or path is left
  post   --from Claude --type STATUS "text"   encode + check + 1/day rule, append to board.json

Real values live ONLY in a private cipher JSON, never in this repo:
  $CHALKBOARD_CIPHER, else ./private/cipher.json, else ../private/cipher.json
Format: {"codes": {"#N1": "10.x.x.x", "#B1": "http://..."}}  (see cipher.example.json)
"""
import json, os, re, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CIPHER_PATHS = [os.environ.get("CHALKBOARD_CIPHER", ""),
                os.path.join(HERE, "private", "cipher.json"),
                os.path.join(HERE, "..", "private", "cipher.json")]

LEAKS = {
    "URL":       re.compile(r"\b[a-z][a-z0-9+.-]{1,9}://\S+", re.I),
    "IPv4":      re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "IPv6":      re.compile(r"\b(?:[0-9a-f]{1,4}:){3,7}[0-9a-f]{1,4}\b", re.I),
    "PORT":      re.compile(r"(?<![\d:])(?::\d{4,5})\b"),
    "WIN_PATH":  re.compile(r"\b[A-Z]:\\", re.I),
    "UNC_PATH":  re.compile(r"\\\\[\w.-]+\\"),
    "DOMAIN":    re.compile(r"(?<![@\w.])(?:[\w-]+\.)+(?:com|net|org|io|dev|app|local|lan|home|ts\.net)\b", re.I),
}

def load_cipher():
    for p in CIPHER_PATHS:
        if p and os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f).get("codes", {})
    return {}

def encode(text, codes):
    # longest real value first so a full URL wins over the IP inside it
    for code, real in sorted(codes.items(), key=lambda kv: -len(kv[1])):
        text = text.replace(real, code)
    return text

def decode(text, codes):
    for code, real in sorted(codes.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(code, real)
    return text

def leaks(text):
    return [(name, m.group(0)) for name, rx in LEAKS.items() for m in rx.finditer(text)]

def entries(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("messages", [])

def check_board(path):
    bad = 0
    for i, e in enumerate(entries(path)):
        for k, v in e.items():
            for name, hit in leaks(str(v)):
                bad += 1
                print(f"LEAK entry {i} field '{k}' [{name}] (len {len(hit)}) (ts={e.get('ts','?')})")
    print("chalkboard: clean" if not bad else f"chalkboard: {bad} leak(s) - do not post")
    return bad

def guard(text):
    found = leaks(text)
    if found:
        for name, hit in found:
            print(f"REFUSED [{name}] raw value left: (len {len(hit)}) add it to private/cipher.json", file=sys.stderr)
        sys.exit(2)
    return text

def post(argv, codes):
    who, kind, board, text = "Claude", "STATUS", os.path.join(HERE, "board.json"), []
    it = iter(argv)
    for a in it:
        if a == "--from": who = next(it)
        elif a == "--type": kind = next(it)
        elif a == "--board": board = next(it)
        else: text.append(a)
    msg = guard(encode(" ".join(text), codes))
    with open(board, encoding="utf-8") as f:
        data = json.load(f)
    lst = data if isinstance(data, list) else data.setdefault("messages", [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if any(e.get("from", e.get("session")) == who and e.get("ts", "")[:10] == today for e in lst):
        sys.exit(f"REFUSED: '{who}' already posted on {today} (1 post/day).")
    lst.append({"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "from": who, "type": kind, "msg": msg})
    with open(board, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False); f.write("\n")
    print(f"posted as {who}: {msg}")

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, rest, codes = sys.argv[1], sys.argv[2:], load_cipher()
    if cmd == "encode":
        print(guard(encode(" ".join(rest), codes)))
    elif cmd == "decode":
        print(decode(" ".join(rest), codes))
    elif cmd == "check":
        sys.exit(1 if check_board(rest[0] if rest else os.path.join(HERE, "board.json")) else 0)
    elif cmd == "post":
        post(rest, codes)
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main()

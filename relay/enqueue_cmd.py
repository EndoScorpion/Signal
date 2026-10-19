#!/usr/bin/env python3
"""enqueue_cmd.py — Enqueue a command via GitHub relay and wait for result.

Usage:
    python3 enqueue_cmd.py "Get-Date"
    python3 enqueue_cmd.py "dir C:\\Users\\endos\\Desktop" --shell cmd
    python3 enqueue_cmd.py --poll <id>

Requires: git configured with push access to EndoScorpion/Signal (relay branch).
Run from inside the Signal repo directory.
"""

import json, uuid, subprocess, time, argparse, sys
from pathlib import Path

REPO      = Path(__file__).parent.parent  # Signal repo root
QUEUE     = REPO / "relay" / "cmd_queue.json"
RESULTS   = REPO / "relay" / "cmd_results.json"
BRANCH    = "relay"

def git(*args):
    return subprocess.run(["git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True)

def load_json(p):
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return []

def save_json(p, data):
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def enqueue(command, shell="ps"):
    git("pull", "origin", BRANCH, "--rebase")
    queue = load_json(QUEUE)
    item = {"id": str(uuid.uuid4())[:8], "command": command, "shell": shell, "status": "pending"}
    queue.append(item)
    save_json(QUEUE, queue)

    git("add", "relay/cmd_queue.json")
    git("commit", "-m", f"relay: enqueue {item['id']}")
    r = git("push", "origin", BRANCH)
    if r.returncode != 0:
        print(f"Push failed: {r.stderr}", file=sys.stderr); sys.exit(1)

    print(f"Enqueued id={item['id']}")
    return item["id"]

def poll(job_id, timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        git("pull", "origin", BRANCH, "--rebase")
        results = load_json(RESULTS)
        match = next((r for r in results if r.get("id") == job_id), None)
        if match:
            print(f"--- stdout ---\n{match.get('stdout','')}")
            if match.get("stderr"):
                print(f"--- stderr ---\n{match['stderr']}")
            print(f"exit_code={match.get('exit_code',-1)}  completed_at={match.get('completed_at','')}")
            return
        print(f"Waiting for id={job_id}...")
        time.sleep(8)
    print(f"Timeout after {timeout}s")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", nargs="?")
    ap.add_argument("--shell", default="ps", choices=["ps","cmd"])
    ap.add_argument("--poll", metavar="ID")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    if args.poll:
        poll(args.poll, args.timeout)
    elif args.command:
        jid = enqueue(args.command, args.shell)
        poll(jid, args.timeout)
    else:
        ap.print_help(); sys.exit(1)

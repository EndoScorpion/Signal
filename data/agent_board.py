"""agent_board.py - shared job board for Claude agents, subagents, scripts and (later) other PCs. Plain JSON in data\agent_board.json, written atomically.
Jobs: {id, title, owner, status: open|claimed|done|blocked, created, updated, note}. Owners claim a job before starting so two workers never do the same work;
stale claims (no update for 6 h) can be re-claimed. To use it from another PC, put data\agent_board.json in a synced folder (Syncthing/OneDrive) and point BOARD there.
Usage: python -E -P data/agent_board.py list | add "title" | claim ID owner | done ID "note" | block ID "note"
Backtest tooling only; carries no trading authority."""
import json, os, sys, time, datetime
BOARD = os.environ.get("AGENT_BOARD", r"C:\Users\endos\Signal\data\agent_board.json")
def load(): return json.load(open(BOARD)) if os.path.exists(BOARD) else {"jobs": []}
def save(b): tmp = BOARD + ".tmp"; json.dump(b, open(tmp, "w"), indent=1); os.replace(tmp, BOARD)
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
a = sys.argv[1:]; b = load(); jobs = b["jobs"]
if not a or a[0] == "list":
    for j in jobs: print(f"{j['id']:>3} [{j['status']:<7}] {j['owner'] or '-':<14} {j['title']}  ({j['note']})")
elif a[0] == "add": jobs.append({"id": max([j["id"] for j in jobs] + [0]) + 1, "title": a[1], "owner": "", "status": "open", "created": now(), "updated": now(), "note": ""}); save(b); print("added", jobs[-1]["id"])
else:
    j = next((x for x in jobs if x["id"] == int(a[1])), None)
    if not j: raise SystemExit("no such job")
    if a[0] == "claim":
        stale = (time.time() - datetime.datetime.fromisoformat(j["updated"]).timestamp()) > 6 * 3600
        if j["status"] == "open" or (j["status"] == "claimed" and stale): j.update(owner=a[2], status="claimed", updated=now()); save(b); print("claimed")
        else: raise SystemExit(f"cannot claim: {j['status']} by {j['owner']}")
    elif a[0] in ("done", "block"): j.update(status="done" if a[0] == "done" else "blocked", note=a[2] if len(a) > 2 else "", updated=now()); save(b); print(a[0])

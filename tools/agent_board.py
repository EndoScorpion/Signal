#!/usr/bin/env python3
"""agent_board.py - coordination board for cloud agents (Signal repo).

State lives in data/agent_board.json (git-tracked). Agents claim work items,
post results, and queue MT4 Strategy Tester jobs. Only ONE MT4 job may be
'running' at a time; only the holder of the 'mt4' role (the session with
Desktop Commander access to LenovoLaptop) may start/finish MT4 jobs.
This tool never starts MT4 and never touches MT4_PAUSE. Research only, no orders.

Usage:
  agent_board.py init
  agent_board.py add   --kind er|draft|parse|other --title T [--deps ID,ID]
  agent_board.py claim --agent NAME [--kind K]          # next open item
  agent_board.py done  --id ID --agent NAME [--result PATH] [--note N]
  agent_board.py fail  --id ID --agent NAME --note N
  agent_board.py mt4-queue --agent NAME --ea FILE --symbol S --tf M15 --from 2023.01.01 --to 2026.10.01 [--set FILE]
  agent_board.py mt4-next  --agent NAME                  # mt4 role only; refuses if one is running
  agent_board.py mt4-done  --id ID --agent NAME --report PATH [--status done|failed]
  agent_board.py reap  [--minutes 90]                    # release stale claims
  agent_board.py status
"""
import argparse, json, os, sys, time, datetime as dt
try:
    import fcntl
except ImportError:
    fcntl = None

BOARD = os.environ.get("AGENT_BOARD", os.path.join(os.path.dirname(__file__), "..", "data", "agent_board.json"))
MT4_ROLE_AGENTS = set(os.environ.get("MT4_AGENTS", "mt4-runner").split(","))

def now(): return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def empty():
    return {"schema": 1, "rev": 0, "updated": now(),
            "agents": {}, "items": [], "mt4": {"max_running": 1, "queue": []}, "log": []}

class Board:
    def __enter__(self):
        os.makedirs(os.path.dirname(BOARD), exist_ok=True)
        self.lf = open(BOARD + ".lock", "w")
        if fcntl: fcntl.flock(self.lf, fcntl.LOCK_EX)
        self.b = json.load(open(BOARD)) if os.path.exists(BOARD) else empty()
        return self.b
    def __exit__(self, et, *a):
        if et is None:
            self.b["rev"] += 1; self.b["updated"] = now()
            self.b["log"] = self.b["log"][-200:]
            tmp = BOARD + ".tmp"
            json.dump(self.b, open(tmp, "w"), indent=1); os.replace(tmp, BOARD)
        if fcntl: fcntl.flock(self.lf, fcntl.LOCK_UN)
        self.lf.close()

def nid(lst, p): return f"{p}{1 + max([int(x['id'][len(p):]) for x in lst] or [0]):04d}"
def log(b, agent, msg): b["log"].append({"t": now(), "agent": agent, "msg": msg})
def die(m): print("ERROR:", m); sys.exit(1)
def find(lst, i): return next((x for x in lst if x["id"] == i), None) or die(f"no id {i}")
def beat(b, a): b["agents"].setdefault(a, {})["last_seen"] = now()

def main():
    p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("init"); s.add_parser("status")
    x = s.add_parser("add"); x.add_argument("--kind", required=True); x.add_argument("--title", required=True); x.add_argument("--deps", default=""); x.add_argument("--agent", default="coordinator")
    x = s.add_parser("claim"); x.add_argument("--agent", required=True); x.add_argument("--kind")
    for c in ("done", "fail"):
        x = s.add_parser(c); x.add_argument("--id", required=True); x.add_argument("--agent", required=True); x.add_argument("--result"); x.add_argument("--note", default="")
    x = s.add_parser("mt4-queue"); x.add_argument("--agent", required=True)
    for f in ("ea", "symbol", "tf"): x.add_argument("--" + f, required=True)
    x.add_argument("--from", dest="frm", required=True); x.add_argument("--to", required=True); x.add_argument("--set"); x.add_argument("--item")
    x = s.add_parser("mt4-next"); x.add_argument("--agent", required=True)
    x = s.add_parser("mt4-done"); x.add_argument("--id", required=True); x.add_argument("--agent", required=True); x.add_argument("--report", required=True); x.add_argument("--status", default="done", choices=["done", "failed"])
    x = s.add_parser("reap"); x.add_argument("--minutes", type=int, default=90)
    a = p.parse_args()

    if a.cmd == "init":
        if os.path.exists(BOARD): die("board exists")
        with Board(): pass
        print("created", BOARD); return
    with Board() as b:
        if a.cmd == "status":
            for it in b["items"]: print(f"{it['id']} {it['status']:8} {it['kind']:6} {it.get('owner') or '-':12} {it['title']}")
            for j in b["mt4"]["queue"]: print(f"{j['id']} {j['status']:8} MT4    {j['ea']} {j['symbol']} {j['tf']} {j['from']}-{j['to']}")
        elif a.cmd == "add":
            it = {"id": nid(b["items"], "W"), "kind": a.kind, "title": a.title, "status": "open",
                  "deps": [d for d in a.deps.split(",") if d], "owner": None, "claimed": None,
                  "created": now(), "result": None, "note": ""}
            b["items"].append(it); log(b, a.agent, f"add {it['id']}"); print(it["id"])
        elif a.cmd == "claim":
            beat(b, a.agent)
            ok = {i["id"] for i in b["items"] if i["status"] == "done"}
            it = next((i for i in b["items"] if i["status"] == "open" and (not a.kind or i["kind"] == a.kind)
                       and all(d in ok for d in i["deps"])), None)
            if not it: print("NONE"); return
            it.update(status="claimed", owner=a.agent, claimed=now()); log(b, a.agent, f"claim {it['id']}")
            print(json.dumps(it))
        elif a.cmd in ("done", "fail"):
            it = find(b["items"], a.id)
            if it["owner"] != a.agent: die(f"{a.id} owned by {it['owner']}")
            it.update(status="done" if a.cmd == "done" else "failed", result=a.result, note=a.note, finished=now())
            log(b, a.agent, f"{a.cmd} {a.id}"); beat(b, a.agent)
        elif a.cmd == "mt4-queue":
            j = {"id": nid(b["mt4"]["queue"], "T"), "item": a.item, "by": a.agent, "ea": a.ea, "symbol": a.symbol,
                 "tf": a.tf, "from": a.frm, "to": a.to, "set": a.set, "status": "queued",
                 "queued": now(), "started": None, "finished": None, "report": None}
            b["mt4"]["queue"].append(j); log(b, a.agent, f"mt4-queue {j['id']}"); print(j["id"])
        elif a.cmd == "mt4-next":
            if a.agent not in MT4_ROLE_AGENTS: die(f"{a.agent} lacks mt4 role (MT4_AGENTS={','.join(MT4_ROLE_AGENTS)})")
            run = [j for j in b["mt4"]["queue"] if j["status"] == "running"]
            if len(run) >= b["mt4"]["max_running"]: die(f"MT4 busy: {run[0]['id']}")
            j = next((j for j in b["mt4"]["queue"] if j["status"] == "queued"), None)
            if not j: print("NONE"); return
            j.update(status="running", started=now(), runner=a.agent); log(b, a.agent, f"mt4-start {j['id']}")
            print(json.dumps(j))
        elif a.cmd == "mt4-done":
            j = find(b["mt4"]["queue"], a.id)
            if j["status"] != "running" or j.get("runner") != a.agent: die("not running under this agent")
            j.update(status=a.status, finished=now(), report=a.report); log(b, a.agent, f"mt4-{a.status} {a.id}")
            # auto-create a parse item for the report
            b["items"].append({"id": nid(b["items"], "W"), "kind": "parse", "title": f"parse {a.id} {a.report}",
                               "status": "open", "deps": [], "owner": None, "claimed": None, "created": now(),
                               "result": None, "note": ""})
        elif a.cmd == "reap":
            cut = time.time() - a.minutes * 60
            for it in b["items"]:
                if it["status"] == "claimed" and dt.datetime.strptime(it["claimed"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() < cut:
                    log(b, "reaper", f"release {it['id']} from {it['owner']}"); it.update(status="open", owner=None, claimed=None)

if __name__ == "__main__": main()

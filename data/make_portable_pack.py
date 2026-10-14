"""make_portable_pack.py - ONE small portable zip with everything another PC/VPS (or an agent) needs to reproduce the useful win logic:
the newest EA (.mq4 and .ex4), .set files of the top VALID candidates (corrected rollover only), a manifest.json (settings, results, cost flags, validation notes) and a README.
Phones cannot run EAs; the zip (and the 1-page manifest.json) can be sent to the phone for reading. Add-only: writes data/portable_pack_<date>.zip, keeps 3 newest.
Run: python -E -P data/make_portable_pack.py"""
import json, os, glob, zipfile, datetime
D = r"C:\Users\endos\Signal\data"; EXP = r"C:\Users\endos\Desktop\mt4_tester2\MQL4\Experts"; TS = r"C:\Users\endos\Desktop\mt4_tester2\tester"; LOT = 0.16
T = dict(json.load(open(os.path.join(D, "loop_state.json")))["tested"]); T.update(json.load(open(os.path.join(D, "loop_state_clean.json"))).get("tested", {}))
flags = {}
try: flags = json.load(open(os.path.join(D, "cost_flags.json")))["candidates"]
except Exception: pass
def tot(t): o = t.get("oos") or {}; return round(sum(v["profit"] for v in o.values()) / LOT), sum(v["trades"] for v in o.values()), len(o)
rows = sorted(((tot(t), n) for n, t in T.items() if t.get("oos") and tot(t)[1] >= 100 and tot(t)[2] >= 6), reverse=True)[:5]
eas = sorted(glob.glob(os.path.join(EXP, "MR_RegimeSwitch_b6[0-9].mq4")))
ea = os.path.basename(eas[-1])[:-4] if eas else None
man = {"made": datetime.datetime.now().isoformat(timespec="seconds"), "ea": ea, "history": "FXOpen M1 bid, server clock UTC+2 (UTC+3 US DST), rebuilt 2026-10-14 (mt4_tester2); rollover window RollFrom=23 RollTo=1",
       "cost_rule": "commission max 5 pts round trip + average spread; cheapest tier 3.45 pts tested too", "status": "BACKTEST ONLY, never approved for live trading",
       "top_candidates": [{"name": n, "pts": p[0], "trades": p[1], "years": p[2], "cost_flag": flags.get(n, {}).get("flag"), "break_even_pts": flags.get(n, {}).get("break_even"), "patch": {k: v for k, v in T[n]["patch"].items()}} for p, n in rows]}
out = os.path.join(D, f"portable_pack_{datetime.date.today():%Y%m%d}.zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    if ea:
        for ext in (".mq4", ".ex4"):
            p = os.path.join(EXP, ea + ext)
            if os.path.exists(p): z.write(p, f"{ea}{ext}")
    for p, n in rows:
        sp = os.path.join(TS, f"LOOP_{n}.set")
        if os.path.exists(sp): z.write(sp, f"sets/{n}.set")
    z.writestr("manifest.json", json.dumps(man, indent=1))
    z.writestr("README.txt", "Portable pack. 1) Copy the .mq4/.ex4 into MQL4\\Experts of an MT4 terminal and the .set files to a folder you load from the EA Inputs dialog (Load).\n2) The clean history is FXOpen M1 bid with server clock UTC+2/+3; use the same data for comparable tests.\n3) Everything is a BACKTEST lead; nothing here is approved for live trading. Remote disable: EAs b62+ with UseControlFile=true read ea_control.txt (DISABLE=1) from the common files folder.\n4) Costs: commission max 5 pts per round trip plus average spread; check cost flags in manifest.json.\n")
old = sorted(glob.glob(os.path.join(D, "portable_pack_*.zip")))[:-3]
print(f"wrote {out} ({os.path.getsize(out)//1024} KB): EA {ea}, {len(rows)} candidates; older packs kept: {[os.path.basename(o) for o in old] or 'none to flag'}")

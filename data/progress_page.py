"""progress_page.py - one-shot: writes data/progress.html (self-contained, black/lime, auto-refresh meta tag) from loop_progress.json, the report folder and free RAM.
Read-only on everything, no daemon. Open data\progress.html in the app's browser pane and keep it beside the chat; re-run this script (python -E -P data\progress_page.py) to refresh the numbers.
Usage: python -E -P data\progress_page.py ["current task note"]"""
import json, os, glob, time, sys, ctypes, re, html
D = r"C:\Users\endos\Signal\data"; CL = r"C:\Users\endos\Desktop\hst_out\clean"
class M(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 5)]
m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); free_mb = int(m.ap / 2**20)
try: P = json.load(open(os.path.join(D, "loop_progress.json")))
except Exception: P = {}
paused = any(os.path.exists(p) for p in (r"C:\Users\endos\Desktop\hst_out\MT4_PAUSE", r"C:\Users\endos\MT4_Backtest\PAUSE"))
rep = sorted(glob.glob(os.path.join(CL, "LOOP_*.htm")), key=os.path.getmtime, reverse=True)[:8]
sims = {}
for f in glob.glob(os.path.join(CL, "LOOP_sim_*_sp5.htm")):
    mm = re.match(r"LOOP_(sim_.+?)_(\d{4})_sp5\.htm$", os.path.basename(f))
    if mm: sims.setdefault(mm.group(1), set()).add(mm.group(2))
order = ["sim_tier3p0_at_250000", "sim_tier3p0_at_275000", "sim_tier3p6_at_25000", "sim_tier3p6_at_27500", "sim_tier5_at_1000", "sim_tier5_at_1100", "sim_tier7_at_500"]
note = html.escape(sys.argv[1]) if len(sys.argv) > 1 else ""
rows = "".join(f"<tr><td>{n}</td><td><div class=bar><i style='width:{min(100, len(sims.get(n, ())) * 100 // 8)}%'></i></div></td><td>{len(sims.get(n, ()))}/8 yrs</td></tr>" for n in order)
last = "".join(f"<li>{time.strftime('%H:%M', time.localtime(os.path.getmtime(f)))} {html.escape(os.path.basename(f)[5:-4])}</li>" for f in rep)
col = "#ff4444" if paused or free_mb < 1024 else "#39ff14"
page = f"""<!doctype html><meta charset=utf8><meta http-equiv=refresh content=20><title>Progress</title>
<style>body{{background:#000;color:#39ff14;font:16px 'Times New Roman',serif;margin:16px}}h2{{margin:.2em 0}}table{{border-collapse:collapse;width:100%}}td{{padding:3px 8px;border-bottom:1px solid #123}}
.bar{{background:#111;border:1px solid #39ff14;height:12px;width:220px}}.bar i{{display:block;height:100%;background:#39ff14}}.k{{color:{col}}}li{{list-style:none}}</style>
<h2>Test progress <small>(updated {time.strftime('%H:%M:%S')}; page refreshes every 20 s, numbers update when the script is re-run)</small></h2>
<p>Now testing: <b>{html.escape(str(P.get('test', '?')))}</b> year {html.escape(str(P.get('year', '?')))} &nbsp; | &nbsp; <span class=k>free RAM {free_mb} MB{' - PAUSED' if paused else ''}</span></p>
<p>Claude is working on: <b>{note or '(no note)'}</b></p>
<h2>Simulated-balance runs (cheapest tier first)</h2><table>{rows}</table>
<h2>Latest reports</h2><ul>{last}</ul>"""
open(os.path.join(D, "progress.html"), "w", encoding="utf-8").write(page); print("wrote progress.html", free_mb, "MB free")

"""build_clone_tree.py - collapsible CSS ancestry tree of the EA lineage and every tested clone (data/clone_tree.html). No JavaScript: <details>/<summary>.
Top: b22_thu -> GEN0 -> GEN1 (b31) and the MR_RegimeSwitch family b50..b62 (what each version added). Under each EA version: the clones tested on it, parents inferred from names
(_m1/_m2 mutations, th_ loss-protection, s_ salvage, rt_ corrected re-tests), sorted strongest first. Invalid (rollover 20-22) results are shown struck through in red, never hidden.
Colours: RED worst/0 trades, ORANGE losses low/medium volume, YELLOW some/few losses, PURPLE weak gain, BLUE good, GREEN very good, LIME strongest. Offline, read-only. Backtest only, never live approval.
Run: python -E -P data/build_clone_tree.py"""
import json, os, re, html, datetime
D = r"C:\Users\endos\Signal\data"; LOT = 0.16
S1 = json.load(open(os.path.join(D, "loop_state.json"))); S2 = json.load(open(os.path.join(D, "loop_state_clean.json")))
T = dict(S1["tested"]); T.update(S2.get("tested", {})); OLD = dict(S1.get("tested_rollover_20_22", {})); OLD.update(S2.get("tested_rollover_20_22", {}))
extras = [e["name"] for e in json.load(open(os.path.join(D, "extra_candidates.json"))) if e["name"] not in T and e["name"] not in OLD]
flags = {}
try: flags = json.load(open(os.path.join(D, "cost_flags.json")))["candidates"]
except Exception: pass
def tot(t): o = t.get("oos") or {}; return round(sum(v["profit"] for v in o.values()) / LOT), sum(v["trades"] for v in o.values()), len(o)
allv = {n: tot(t) for n, t in T.items() if t.get("oos")}
hi = max([v[0] for v in allv.values() if v[0] > 0] + [1]); lo = min([v[0] for v in allv.values() if v[0] < 0] + [-1])
def cls(p, tr):
    if tr == 0: return "red"
    if p < 0:
        r = p / lo
        return "red" if r > .66 else ("orange" if tr < 60 * 8 and r > .33 else "yellow")
    r = p / hi; return "lime" if r > .75 else ("green" if r > .5 else ("blue" if r > .25 else "purple"))
def ver(n, t):
    e = (t or {}).get("expert") or ((t or {}).get("patch") or {}).get("_expert") or ""
    m = re.search(r"b(\d+)$", e); return int(m.group(1)) if m and "MR_RegimeSwitch" in e else (0 if not e else -1)
names = set(T) | set(OLD)
def parent(n):
    m = re.match(r"(.+)_m[12]$", n)
    if m and m.group(1) in names: return m.group(1)
    for pre in ("th_", "s_", "rt_"):
        if n.startswith(pre):
            rest = n[len(pre):]; c = [x for x in names if rest == x or rest.startswith(x + "_")]
            if c: return max(c, key=len)
    return None
kids = {}
for n in sorted(names): kids.setdefault(parent(n), []).append(n)
def node(n, invalid=False):
    t = (OLD if invalid else T).get(n, {}); p, tr, y = tot(t) if t.get("oos") else (0, 0, 0)
    fl = flags.get(n, {}).get("flag", ""); w = f'<span class="{ "bad" if invalid else cls(p, tr) }">{"" if not t.get("oos") else f"{p:+d} pts, {tr} trades, {y} yrs"}{" cost " + fl if fl else ""}</span>'
    label = f'<b class="{"inv" if invalid else ""}">{html.escape(n)}</b> {w}{" <i>INVALID: rollover window 20-22, result overstated (kept)</i>" if invalid else ""}'
    par = parent(n); pt = (T.get(par) or OLD.get(par) or {}) if par else {}
    if par and pt.get("oos") and t.get("oos"):
        d = p - tot(pt)[0]; label += f' <span class="{"lime" if d > 0 else "red"}">{"&#9650;" if d > 0 else "&#9660;"} {d:+d} vs {html.escape(par)}</span>'
    if par and pt.get("patch") and t.get("patch"):
        diff = [f"{k} {pt['patch'].get(k)}&rarr;{v}" for k, v in t["patch"].items() if k != "_expert" and pt["patch"].get(k) != v][:4]
        if diff: label += ' <span class="note">changed: ' + html.escape(", ".join(diff)).replace("&amp;rarr;", "&rarr;") + "</span>"
    ch = sorted(kids.get(n, []), key=lambda c: -(tot((T.get(c) or OLD.get(c) or {})) [0] if (T.get(c) or OLD.get(c) or {}).get("oos") else -10**9))
    if not ch: return f'<li class="leaf">{label}</li>'
    return f'<li><details><summary>{label} <em>({len(ch)} clones)</em></summary><ul>' + "".join(node(c, c in OLD and c not in T) for c in ch) + "</ul></details></li>"
VERS = {50: "z-score fade + long regime (first MR clone)", 51: "ZGate-style volume blend, MMR gate, calm-tape gate", 52: "clean-history EA (rollover 23-01, warm-up fix)", 53: "b52 + silent reject audit (other session)",
        54: "slope gap/stack, ER, fib, stoch, Williams %R, alligator, fractals, Hurst, vol-of-vol, calculus timing, SMA cross", 55: "SSR slope-to-slope ratio, bear-buy block, buy up-slope convergence",
        56: "range, volume, ADX, CCI, A/D, fractal dimension, Lyapunov, regression-line z, slope-stack convergence", 57: "z-reversion exit, ATR stops, hour mask, autocorrelation, absorption",
        58: "breakeven, fast stop, loss cooldown, turn confirmation, confidence sizing", 59: "split entries, drawdown hedge, shared lot budget", 60: "Ehlers cycle, Kalman z, variance regime",
        61: "OU half-life gate", 62: "mail/push notifications, remote disable file, heartbeat, daily loss stop"}
byv = {}
for n in sorted(names):
    if parent(n) is None: byv.setdefault(ver(n, T.get(n) or OLD.get(n)), []).append(n)
def vnode(v):
    items = sorted(byv.get(v, []), key=lambda c: -(tot(T[c])[0] if c in T and T[c].get("oos") else -10**9))
    body = "".join(node(c, c in OLD and c not in T) for c in items)
    return f'<li><details><summary><b>MR_RegimeSwitch_b{v}</b> <span class="note">{html.escape(VERS.get(v, ""))}</span> <em>({len(items)} roots)</em></summary><ul>{body or "<li class=leaf>(no clones tested yet)</li>"}' + "{CHILD}</ul></details></li>"
chain = ""
for v in range(62, 49, -1): pass
mr = ""
for v in range(62, 49, -1):
    inner = vnode(v)
    mr = inner.replace("{CHILD}", ("<ul>" + mr + "</ul>") if mr else "") if True else inner
old = byv.get(0, []) + byv.get(-1, [])
oldhtml = "".join(node(c, c in OLD and c not in T) for c in sorted(old))
qhtml = "".join(f'<li class="leaf dim">{html.escape(e)} (queued)</li>' for e in extras[:40]) + (f'<li class="leaf dim">... and {len(extras)-40} more queued</li>' if len(extras) > 40 else "")

passes = 0
try: passes = sum(1 for l in open(os.path.join(D, "evolve_log.txt"), encoding="utf-8", errors="ignore") if " done:" in l and " pass " in l)
except Exception: pass
base8 = None
try: base8 = round(sum((v["profit"] if isinstance(v, dict) else v) for v in (S1.get("base_real") or {}).values()) / LOT)
except Exception: pass
bestv = max(allv.items(), key=lambda kv: kv[1][0]) if allv else None
def row(*c): return "<tr>" + "".join(f"<td>{x}</td>" for x in c) + "</tr>"
anc = [("First-generation stochastic entry (Aug 2026: stoch 21-25 entries)", "replaced", "No winning evidence found; stochastic K>80 sells lose in all 4 unseen years. Kept only as an optional gate (StochMode) in b54+."),
       ("M15 slope/momentum entry (b22_thu core, stop-order ladders)", "kept in b31 only", "Original entry of the whole family; the MR clones replaced it with a z-score fade."),
       ("Stochastic position (K) filter", "kept in b22/b31", "Inherited filter; optional StochMode gate in b54+."),
       ("MMR (Nasif Hossain 2019, slope-ratio quality)", "optional gate b51+", "Weak and inconsistent gross edge offline; quintile-4 band re-test pending."),
       ("UseSellRegime (H1 SMA 1200)", "LIVES ON", "Lives on as the regime SMA 2400-3000 in every MR clone; switching it off made 2023 worse (-7,416 vs -3,998)."),
       ("Kaufman ER", "optional gate", "G4 clones, then ErMin/ErMax in b54+."),
       ("ZGate (b25+)", "LIVES ON as UseZBlend", "Proven in-sample (+57,788 vs +45,664); volume-blend trigger b51+."),
       ("Daily range filter (b27+)", "LIVES ON as DayRangeMaxMult", "Proven in-sample (+61,897); gate b56+."),
       ("Virtual buy, lot sim, SellStop + hedge/ladder", "b31 only", "Not carried into the MR clones; hedge and split rebuilt in b59.")]
wl = [("Long sell-regime SMA (2400+)", "WIN", "Beat base on all 4 unseen years in the first test; protective (off = worse)."),
      ("Skip server hours 0-3 (valid, corrected)", "WIN (small sample)", f"{allv.get('th_g2_AtrCapPts_90_hours_00-03', ('-', '-'))[0] if 'th_g2_AtrCapPts_90_hours_00-03' in allv else 'n/a'} pts, cost flag GREEN, break-even about 18.6 pts."),
      ("Z-score fade entry (MR family)", "UNPROVEN", "Earlier +10k..+18k results were inflated by the wrong rollover window; corrected re-tests are running first."),
      ("SMA20/SMA50 slope gap converging (divergence = chaos)", "EVIDENCE offline", "Base trades: converging 49.9% win, -9.3 pts per trade; diverging 43.3%, -48.5. Clone tests queued."),
      ("Quiet-tape trigger, SSR, chaos gates (Hurst/Lyapunov/FD), calculus timing, OU half-life", "UNTESTED", "Built b54-b61, queued; thresholds retuned by the math agent."),
      ("Loss protection: breakeven, fast stop, cooldown, hedge, split, confidence sizing", "UNTESTED", "Built b58-b59, queued."),
      ("MMR gate", "WEAK", "Inconsistent gross edge offline."), ("Stochastic >80 sells, fib retracements", "LOSE / no edge", "Offline.")]
gens = [("b22_thu base", "original entry + stop ladders", "8-period in-sample +45,664 (@8pt)", "reference"),
        ("GEN0 ZGate (b25+)", "UseZGate", "+57,788", "+27% vs base (in-sample)"), ("GEN0 DailyRange (b27+)", "daily range filter", "+61,897", "+36% vs base"),
        ("GEN1 b31", "ZGate + DailyRange", "+75,254 vs 48,429 @8pt, better 7/8 periods", "best in-sample; LOSES on unseen years"),
        ("GEN2 / G4 / GEN3 mutations", "g2b_*, ER, MP*, Fd+AHRate", "none beat the parent", "no improvement"),
        ("MR gen A (b50-b52, g2_* clones)", "z-score fade + regime", "earlier +10k..+18.6k = INVALID (rollover 20-22)", "corrected same settings about +4.1k, unproven (DSR 0.59)"),
        ("MR gen B (b54-b62 gates)", "slope/chaos/calculus/OU/exits/hedge/split/notify", "tests queued", f"best valid so far: {bestv[0] + ' ' + str(bestv[1][0]) + ' pts / ' + str(bestv[1][1]) + ' trades' if bestv else 'none yet'}")]
self_imp = [("Passes of the self-improvement driver finished", passes), ("Valid clones tested (corrected engine)", len(allv)), ("Invalid results caught and quarantined (kept)", len(OLD)),
            ("Bugs found by validation", "2: b52 clamp / missing inputs; wrong rollover window 20-22 (about 4x overstated leader)"), ("Base system, 8 unseen years", f"{base8:+d} pts" if base8 is not None else "n/a"),
            ("Best valid clone now", f"{bestv[0]}: {bestv[1][0]:+d} pts, {bestv[1][1]} trades" if bestv else "none yet")]

def bar(label, v, mx, cls_):
    w = max(1, int(100 * abs(v) / mx)); return f'<div class="barrow"><span class="barlab">{label}</span><span class="barwrap"><span class="bar {cls_}" style="width:{w}%">{v:+,}</span></span></div>'
corr = round(bestv[1][0]) if bestv else 0
stronger = ('<h2>How each generation got stronger</h2><p class="note">In-sample (8 periods, $ at 8-pt cost): each generation added a filter and beat its parent.</p>'
            + bar("b22_thu base", 45664, 75254, "blue") + bar("GEN0 + ZGate (+27%)", 57788, 75254, "blue") + bar("GEN0 + DailyRange (+36%)", 61897, 75254, "green") + bar("GEN1 b31 (+65%)", 75254, 75254, "lime")
            + '<p class="note">Unseen years (pts): the in-sample strength did not carry over; the MR family restarted the climb, and its early gains were an artifact.</p>'
            + bar("Base system, 8 unseen years", base8 if base8 is not None else 0, 140000, "red")
            + bar("MR gen A leader as first measured (INVALID rollover)", 18622, 140000, "bad") + bar("same settings, corrected (validator)", 4100, 140000, "purple")
            + bar("best valid clone now", corr, 140000, "lime" if corr > 0 else "red")
            + '<p class="note">Reading: from the base system at about -132,700 pts the clones moved to a small positive result; the bars to the right grow as corrected generations finish.</p>')
sections = ('<h2>Ancestor and precursor logic</h2><table>' + "".join(row(a, b, c) for a, b, c in anc) + '</table>'
            '<h2>Win logic tree</h2><table>' + "".join(row(a, f'<span class="{ "lime" if b.startswith("WIN") else ("blue" if b.startswith("EVID") else ("red" if b.startswith(("LOSE", "WEAK")) else "yellow")) }">{b}</span>', c) for a, b, c in wl) + '</table>'
            '<h2>Generations and performance</h2><table>' + row("<b>generation</b>", "<b>what changed</b>", "<b>performance</b>", "<b>improvement</b>") + "".join(row(*g) for g in gens) + '</table>' + stronger + '<h2>Self-improvement so far</h2><table>' + "".join(row(a, b) for a, b in self_imp) + '</table>')
page = f'''<!doctype html><html><head><meta charset="utf-8"><title>Clone ancestry tree</title><style>
body{{background:#000;color:#00ff00;font-family:"Times New Roman",serif;font-size:15px;margin:16px}} ul{{list-style:none;padding-left:22px;border-left:1px dotted #006600}} li{{margin:3px 0}}
summary{{cursor:pointer}} summary::marker{{color:#00ff00}} .note{{color:#66cc66;font-size:13px}} .leaf{{padding-left:14px}} .dim{{color:#337733}} em{{color:#66cc66;font-size:12px}} i{{color:#ff6666;font-size:12px}}
.red{{background:#ff2a2a;color:#fff;padding:0 5px}} .orange{{background:#ff8c1a;color:#000;padding:0 5px}} .yellow{{background:#ffd400;color:#000;padding:0 5px}} .purple{{background:#a020f0;color:#fff;padding:0 5px}}
.blue{{background:#2f7dff;color:#fff;padding:0 5px}} .green{{background:#1f9d3a;color:#fff;padding:0 5px}} .lime{{background:#00ff00;color:#000;padding:0 5px}} .bad{{background:#400;color:#f66;padding:0 5px}} .inv{{text-decoration:line-through;color:#f66}}
h1{{font-size:20px}} .barrow{{margin:3px 0;display:flex;align-items:center}} .barlab{{flex:0 0 40%;font-size:13px;padding-right:8px}} .barwrap{{flex:1;display:block}} .bar{{display:inline-block;height:16px;line-height:16px;padding:0 4px;box-sizing:border-box;font-size:12px;min-width:50px}} h2{{font-size:17px;margin:18px 0 6px;border-bottom:1px solid #006600}} table{{border-collapse:collapse;width:100%}} td{{border:1px solid #004400;padding:3px 7px;vertical-align:top}} .legend span{{margin-right:8px}}</style></head><body><h1>Clone ancestry tree</h1><p>Generated {datetime.datetime.now():%Y-%m-%d %H:%M}. Tap a name to expand its clones; strongest first. Backtest only, never live approval.</p>
<p class="legend"><span class="red">RED worst / 0 trades</span><span class="orange">ORANGE losses, low-med volume</span><span class="yellow">YELLOW some or few losses</span><span class="purple">PURPLE weak gain</span><span class="blue">BLUE good</span><span class="green">GREEN very good</span><span class="lime">LIME strongest</span><span class="bad">struck = invalid result (kept)</span></p>
{sections}<h2>Lineage tree</h2><ul><li><details open><summary><b>b22_thu</b> <span class="note">original base (8-period +45,664 in-sample)</span></summary><ul>
<li><details><summary><b>GEN0_zgate</b> <span class="note">UseZGate (b25+)</span></summary><ul><li><details><summary><b>GEN0_dailyrange</b> <span class="note">+ daily range filter (b27+)</span></summary><ul>
<li><details><summary><b>GEN1 b31 (ZGate + DailyRange)</b> <span class="note">best in-sample, loses on unseen years</span></summary><ul>{oldhtml or "<li class=leaf>(older branches kept on disk: CAND_B36..B41, MP1-6, G4, GEN3)</li>"}</ul></details></li></ul></details></li></ul></details></li>
<li><details open><summary><b>MR_RegimeSwitch family</b> <span class="note">new z-score fade entry; inherits the sell-regime SMA from b22/b31; versions nest in build order</span></summary><ul>{mr}</ul></details></li>
<li><details><summary><b>Queued, not yet tested</b> <em>({len(extras)})</em></summary><ul>{qhtml}</ul></details></li></ul></li></ul></body></html>'''
open(os.path.join(D, "clone_tree.html"), "w", encoding="utf-8").write(page)
print(f"wrote data/clone_tree.html: {len(names)} tested clones ({len(OLD)} invalid kept), {len(extras)} queued")

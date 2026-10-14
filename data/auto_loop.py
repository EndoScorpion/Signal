"""
auto_loop.py - one finite learn/test loop (no daemon, no polling).
  READ    base sp5 reports (OOS years) -> per-trade open time + result
  ANALYZE join trades with m15_metrics.csv (ER/MMR/slope/ATR/hour) -> worst buckets
  THEORIZE data-driven candidates + existing-rule (EA input) variants, skip already tested
  TEST    one test at a time via run_tester.ps1, RAM-gated, early-abort on first OOS year
  LEARN   scores vs base per WIN rule, writes loop_state.json + loop_report.md
Run: python -I data/auto_loop.py [--rounds 1] [--max-cands 3] [--spread 5]
Commission rule: sp5 (Nasif 2026-10-13, low-volume assumption). Backtest only, never live approval.
"""
import os, re, sys, json, csv, ctypes, subprocess, datetime, importlib.util, shutil
from collections import defaultdict

SIG   = r"C:\Users\endos\Signal"
DATA  = os.path.join(SIG, "data")
HST_OUT = r"C:\Users\endos\Desktop\hst_out"
TESTER_DIR = r"C:\Users\endos\Desktop\mt4_tester\tester"
BASE_SET = os.path.join(TESTER_DIR, "WIN_GEN1_ZGate_DailyRange_b31.set")
RUN = os.path.join(HST_OUT, "run_tester.ps1")
METRICS = os.path.join(DATA, "m15_metrics.csv")
STATE = os.path.join(DATA, "loop_state.json")
REPORT = os.path.join(DATA, "loop_report.md")
EXPERT = "Strong2010b_claude_b31"
OOS = ["2016", "2018", "2023", "2024", "2014", "2013", "2015", "2010"]   # Nasif 2026-10-14: hardest (base loses most: 2016, 2018, 2023) and quietest (ATR14: 2024, 2014) years FIRST; first-year gate is now 2016; training = 2011/12/17/19-22/25-26
SELECT = ["2023", "2015", "2018"]                      # already-seen unseen years: pick on these
CONFIRM = ["2013", "2014", "2016", "2010", "2024"]     # never-tested years: must also hold here
TRAIN = {"2019": ("2019.01.01", "2019.12.31"), "2021": ("2021.01.01", "2021.12.31"),   # quietest training years first (ATR14 47, 55), then by quietness
         "2025-26": ("2025.01.01", "2026.10.01"), "2017": ("2017.01.01", "2017.12.31"),
         "2020": ("2020.01.01", "2020.12.31"), "2012": ("2012.01.01", "2012.12.31"),
         "2022": ("2022.01.01", "2022.12.31"), "2011": ("2011.01.01", "2011.12.31")}
args = sys.argv[1:]
def opt(n, d): return type(d)(args[args.index(n) + 1]) if n in args else d
ROUNDS, MAXC, SP = opt("--rounds", 1), opt("--max-cands", 3), opt("--spread", 5)
AUDIT_ONLY = "--audit-only" in args
# --clean: test on the CLEAN history (mt4_tester2; MT4 SERVER clock = UTC+2, UTC+3 in US DST; source FXOpen raw M1 bid, rebuilt 2026-10-14). Default = old PATCHWORK history (mixed clocks + holes).
T25K_SP = 3; T25K_EXTRA = 0.45   # CHEAPEST FXOpen tier (Nasif 2026-10-14): 3.45 pts RT = 1.50/side/lot x2 x EURUSD~1.15. Tester Spread is integer: run sp3, then subtract 0.45 pt/trade (=0.45*0.16 USD at 0.16 lot) exactly. Label T3p45.
CLEAN = "--clean" in args
ROOT_OUT = HST_OUT
WINNERS = os.path.join(ROOT_OUT, "winners")
HIST_LABEL = "CLEAN(UTC+2/+3 USDST, FXOpen raw M1 bid, rebuilt 2026-10-14)" if CLEAN else "PATCHWORK(mixed clocks, holes)"
if CLEAN:
    HST_OUT = os.path.join(ROOT_OUT, "clean"); os.makedirs(HST_OUT, exist_ok=True)
    TESTER_DIR = r"C:\Users\endos\Desktop\mt4_tester2\tester"
    BASE_SET = os.path.join(TESTER_DIR, "WIN_GEN1_ZGate_DailyRange_b31.set")
    if not os.path.exists(BASE_SET): shutil.copy(os.path.join(WINNERS, "WIN_GEN1_ZGate_DailyRange_b31.set"), BASE_SET)
    RUN = os.path.join(ROOT_OUT, "run_tester_b.ps1")
    STATE = os.path.join(DATA, "loop_state_clean.json"); REPORT = os.path.join(DATA, "loop_report_clean.md")

spec = importlib.util.spec_from_file_location("pr", os.path.join(DATA, "parse_results.py"))
pr = importlib.util.module_from_spec(spec); spec.loader.exec_module(pr); pr.COMMISSION = SP

def free_gb():
    class M(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong),
                    ("ap", ctypes.c_ulonglong), ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong),
                    ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]
    m = M(); m.l = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ap / 2**30

def paused():
    return os.path.exists(os.path.join(ROOT_OUT, "MT4_PAUSE")) or os.path.exists(r"C:\Users\endos\MT4_Backtest\PAUSE")

def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"base": {}, "tested": {}, "insights": [], "rounds": 0}

def save_state(s): json.dump(s, open(STATE, "w"), indent=1)

def read_set(p):
    d = {}
    for ln in open(p):
        ln = ln.strip()
        if "=" in ln and not ln.startswith(";"):
            k, v = ln.split("=", 1); d[k.strip()] = v.strip()
    return d

def ea_defaults(expert):
    """All 'extern' inputs of the EA with their source defaults. MT4's tester reuses the LAST value of any input missing from a .set file,
    so every set must list every input or candidates inherit settings from the previous run (found 2026-10-13)."""
    for d in (r"C:\Users\endos\Desktop\mt4_tester2\MQL4\Experts", r"C:\Users\endos\Signal\_usb_backup_stage\MQL4\Experts", os.path.expandvars(r"%APPDATA%\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\MQL4\Experts")):
        p = os.path.join(d, (expert or EXPERT) + ".mq4")
        if os.path.exists(p):
            txt = open(p, encoding="latin-1").read()
            return {m.group(1): m.group(2).strip() for m in re.finditer(r"extern\s+\w+\s+(\w+)\s*=\s*([^;/\"]+?)\s*;", txt)}
    return {}

def build_set(path, expert, base, patch):
    defs = ea_defaults(expert); merged = dict(defs)
    if not str(expert).startswith("MR_RegimeSwitch"):   # the b31 base set must NOT leak into MR experts: same-named inputs (AtrSLMult 1.5, CrossFast 20, CrossSlow 50, ZPeriod 20) silently overrode MR defaults (found 2026-10-14)
        merged.update({k: v for k, v in base.items() if k in defs} if defs else base)
    merged.update({k: str(v) for k, v in patch.items()})
    if expert and str(expert).startswith("MR_RegimeSwitch") and "RollFrom" not in patch:   # clean history clock: rollover spike is 23:00-01:00 server time; b50/b51 defaults (20-22) let the old leader trade through it (found 2026-10-14)
        merged["RollFrom"] = "23"; merged["RollTo"] = "1"
    with open(path, "w") as f:
        for k, v in merged.items(): f.write(f"{k}={v}\n")

def write_set(p, base, patch):
    m = dict(base); m.update({k: str(v) for k, v in patch.items()})
    with open(p, "w") as f:
        for k, v in m.items(): f.write(f"{k}={v}\n")

def real_sp(year):
    """Round-trip cost in pts for the realistic validation pass: 5 pt commission (low-volume floor) + that year's average real spread
    (data/spread_stats.csv, 2019+); earlier years use the 2019-26 average. Clipped to 1..5 pts so it never strays far from the average."""
    try:
        rows = {r["year"]: float(r["mean_pts"]) for r in csv.DictReader(open(os.path.join(DATA, "spread_stats.csv"))) if int(r["year"]) >= 2019}
    except Exception:
        rows = {}
    avg = sum(rows.values()) / len(rows) if rows else 3.0
    m = rows.get(str(year), avg)
    return 5 + int(round(min(5.0, max(1.0, m))))

PROG = {}
def prog(**kw):
    PROG.update(kw)
    try: json.dump(PROG, open(os.path.join(DATA, "loop_progress.json"), "w"))
    except Exception: pass

def run_test(setname, year, frm, to, tag, expert=None, spread=None):
    spread = spread or SP; pr.COMMISSION = spread; pr.HIST_LABEL = HIST_LABEL
    if CLEAN and expert in ('MR_RegimeSwitch_b50', 'MR_RegimeSwitch_b51'): expert = 'MR_RegimeSwitch_b52'   # b52+ are the clean-history EAs; b54..b58 derive from b52 and keep their own inputs (clamp to b52 made new gates silently ignored, fixed 2026-10-14)
    tag = tag.replace(".", "p")   # a dot in the report name makes MT4 skip the .htm extension
    prog(test=tag, year=year, year_idx=(OOS.index(year) + 1 if year in OOS else 0), test_started=datetime.datetime.now().isoformat(timespec="seconds"))
    rp =os.path.join(HST_OUT, tag + ".htm")
    if os.path.exists(rp):   # reuse a finished report instead of re-running (same tag = same set/year/cost)
        r = pr.parse_report(rp)
        return {"profit": float(r["profit"]), "pf": float(r["pf"]), "dd": float(r["dd_pct"]), "trades": int(r["trades"]), "q": float(r["modeling"])}
    if paused(): raise SystemExit("PAUSED - stop")
    import time
    for _g in range(40):   # RAM gate: trim idle memory (safe, reversible), then wait up to ~40 min for RAM instead of quitting the pass
        g = free_gb()
        if g >= 1.0: break
        if paused(): raise SystemExit("PAUSED - stop")
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", r"C:\Users\endos\Desktop\ram.ps1", "-Trim"], capture_output=True)
        time.sleep(60)
    g = free_gb()
    if g < 1.0: raise SystemExit(f"RAM gate: {g:.2f} GB free < 1.0 GB after trims - not starting {tag}")
    for _try in range(25):   # a previous test may still hold the tester lock: wait it out (max ~12 min), never run two at once
        if _try > 0 and os.path.exists(rp): out = "OK"; break   # the interrupted run finished meanwhile: use its report
        out = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", RUN, "-Expert", expert or EXPERT,
                              "-SetFile", setname, "-From", frm, "-To", to, "-Spread", str(spread),
                              "-Model", "0", "-Tag", tag], capture_output=True, text=True).stdout
        if not out.startswith("BUSY"): break
        time.sleep(30)
    p = os.path.join(HST_OUT, tag + ".htm")
    if not out.startswith("OK") or not os.path.exists(p):
        raise SystemExit(f"test failed {tag}: {out.strip()[:200]}")
    r = pr.parse_report(p); pr.append_test_log(tag, r)
    return {"profit": float(r["profit"]), "pf": float(r["pf"]), "dd": float(r["dd_pct"]),
            "trades": int(r["trades"]), "q": float(r["modeling"])}

# ---------- READ + ANALYZE ----------
ROW = re.compile(r'<td>(\d+)</td><td class=msdate>([\d\. :]+)</td><td>(sell|buy|s/l|t/p|close)[^<]*</td><td>(\d+)</td>(.*?)</tr>', re.S)
def trades_from_report(path):
    html = open(path, encoding="utf-8", errors="ignore").read()
    opened, res = {}, []
    for _, t, typ, oid, rest in ROW.findall(html):
        if typ in ("sell", "buy"): opened[oid] = t
        else:
            pm = re.findall(r'class=mspt>([\-\d\.]+)</td>', rest)
            if pm and oid in opened: res.append((opened[oid], float(pm[-2] if len(pm) > 1 else pm[0])))
    return res

def analyze(state):
    years = {y: f"WIN_GEN1_{y}_sp5.htm" for y in OOS}
    trades = []
    for y, f in years.items():
        p = os.path.join(HST_OUT, f)
        if os.path.exists(p): trades += trades_from_report(p)
    if not trades or not os.path.exists(METRICS): return []
    need = {datetime.datetime.strptime(t, "%Y.%m.%d %H:%M").replace(minute=0).strftime("%Y-%m-%d %H") for t, _ in trades}
    mrows = {}
    for row in csv.DictReader(open(METRICS)):
        if row["dt"][:13] in need and row["dt"][:4] in OOS: mrows[row["dt"]] = row
    buckets = defaultdict(lambda: [0, 0.0])
    for t, pnl in trades:
        d = datetime.datetime.strptime(t, "%Y.%m.%d %H:%M")
        prev = (d - datetime.timedelta(minutes=15 + d.minute % 15)).strftime("%Y-%m-%d %H:%M")
        r = mrows.get(prev)
        buckets[("hour", d.hour // 3 * 3)][0] += 1; buckets[("hour", d.hour // 3 * 3)][1] += pnl
        buckets[("dow", d.weekday())][0] += 1; buckets[("dow", d.weekday())][1] += pnl
        if r:
            for k, cuts in (("er10", (0.2, 0.35, 0.5)), ("slope20", (-5, 0, 5)), ("atr14_pts", (40, 70, 110)), ("mmr_6_12_18", (-1, 1, 3))):
                v = float(r[k]); b = sum(v > c for c in cuts)
                buckets[(k, b)][0] += 1; buckets[(k, b)][1] += pnl
    worst = sorted(((k, n, p) for k, (n, p) in buckets.items() if n >= 40), key=lambda x: x[2])[:6]
    ins = [f"{k[0]}[{k[1]}] n={n} pnl={p:.0f}" for k, n, p in worst]
    state["insights"] = ins
    return worst

# ---------- THEORIZE ----------
def candidates(worst, state):
    K = {"_expert": "Strong2010b_claude_b43_chaos", "SellRegimePeriod": 2400}   # branch parent: regime 2400 beat base on all 4 unseen years
    RZ = {"UseStochMax": "true", "UseFibGate": "true", "UseRollBlock": "true", "UseNfpBlock": "true", "UseAtrCap": "true", "AtrCapPts": 90}
    c = [("k_hurst_trend", "branch r2400 + Hurst: sell only when trending (H>0.55)", dict(K, UseHurstGate="true", HurstMode=1)),
         ("k_hurst_revert", "branch r2400 + Hurst: sell only when mean-reverting (H<0.45)", dict(K, UseHurstGate="true", HurstMode=2)),
         ("k_hurst_nodead", "branch r2400 + Hurst: block dead band", dict(K, UseHurstGate="true", HurstMode=3)),
         ("k_reg2_4800", "branch r2400 + stacked 4800 regime", dict(K, UseReg2="true", Reg2Period=4800)),
         ("k_regslope", "branch r2400 + regime SMA must be falling (24 H1 bars)", dict(K, UseRegSlope="true", RegSlopeLag=24)),
         ("k_stoch80", "branch r2400 + block sells at stoch K>80 (red zone 4/4)", dict(K, UseStochMax="true", StochSellMax=80)),
         ("k_fib618", "branch r2400 + block sells in upper 38% of 5-day range (red zone 4/4)", dict(K, UseFibGate="true", FibMaxPos=0.618)),
         ("k_atrcap90", "branch r2400 + ATR cap 90 pts (red zone 4/4)", dict(K, UseAtrCap="true", AtrCapPts=90)),
         ("k_roll", "branch r2400 + block rollover hours 20-22 (spread spike)", dict(K, UseRollBlock="true")),
         ("k_nfp", "branch r2400 + block NFP Fridays (red zone 4/4)", dict(K, UseNfpBlock="true")),
         ("k_redzones_all", "branch r2400 + all red zones", dict(K, **RZ))]
    MR = {"_expert": "Strong2010b_claude_b42_mr", "UseZGate": "false", "UseZMinGate": "true"}
    c += [("mr_sell_z25_n10_atr60", "MR lab best: fade z>=2.5 (N10), ATR14<60", dict(MR, ZMinPeriod=10, ZMinVal=2.5, ZMinAtrCapPts=60)),
         ("mr_sell_z25_n10", "MR lab: fade z>=2.5 (N10), no ATR cap", dict(MR, ZMinPeriod=10, ZMinVal=2.5)),
         ("mr_sell_z20_n20", "MR lab: fade z>=2.0 (N20)", dict(MR, ZMinPeriod=20, ZMinVal=2.0)),
         ("mr_sell_z25_n14", "MR lab: fade z>=2.5 (N14)", dict(MR, ZMinPeriod=14, ZMinVal=2.5)),
         ("u_regime_9600", "regime H1 SMA 9600 (~400 days): trend 600<1200<2400<4800 improves on 2023", {"SellRegimePeriod": 9600}),
         ("u_regime_14400", "regime H1 SMA 14400 (~600 days)", {"SellRegimePeriod": 14400}),
         ("u_regime_off", "control: sell regime off", {"UseSellRegime": "false"}),
         ("u_regime_600", "regime H1 SMA 600 (~25 days)", {"SellRegimePeriod": 600}),
         ("u_regime_2400", "regime H1 SMA 2400 (~100 days)", {"SellRegimePeriod": 2400}),
         ("u_regime_4800", "regime H1 SMA 4800 (~200 days)", {"SellRegimePeriod": 4800})]
    B = {"_expert": "MR_RegimeSwitch_b50", "UseRegime": "true", "RegimePeriod": 2400, "SLPts": 600, "HoldBars": 48, "ZPeriod": 10, "ZTrigger": 2.5}
    c += [("b5_sell_z25_n10", "b50 regime-switch MR: sell-only fade z>=2.5 (N10) below regime 2400, 600 SL, 48-bar exit", dict(B, SideMode=1)),
          ("b5_both_z25_n10", "b50: both sides (sell below / buy above regime 2400)", dict(B, SideMode=0)),
          ("b5_buy_z25_n10", "b50: buy-only fade above regime 2400 (alternative winner for uptrend years)", dict(B, SideMode=2)),
          ("b5_both_z20_n20", "b50: both sides, z>=2.0 on N20", dict(B, SideMode=0, ZTrigger=2.0, ZPeriod=20)),
          ("b5_both_noreg", "b50 control: both sides, regime off", dict(B, SideMode=0, UseRegime="false")),
          ("b5_both_sl300", "b50: both sides with tighter 300 SL", dict(B, SideMode=0, SLPts=300))]
    OLD = ["CAND_B36_adx", "CAND_B36_chop", "CAND_B36_chop_adx", "CAND_B36_chop_zH1", "CAND_B36_chop_zH1_cci", "CAND_B37_m1slope100",
           "CAND_B38_smooth_jitter", "CAND_B38_smooth_jitter_adx", "CAND_B38_smooth_samesign", "CAND_B38_smooth_samesign_er",
           "CAND_G4_1_er_dr", "CAND_G4_2_er100_dr", "CAND_G4_3_er_dr_nofri", "CAND_GEN3_B1_fd_ahrate", "CAND_MP1_fracprox_er", "CAND_MP2_zH1_er", "CAND_MP6_erH1"]
    c = [("z_" + o[5:], f"old offline-only branch {o} re-tested on the repaired full history (b38 EA)", {"_expert": "Strong2010b_claude_b38", "_setfile": o + ".set"}) for o in OLD] + c
    c += [("z_WIN_GEN2_b32", "old GEN2 branch (b32) re-tested on repaired history", {"_expert": "Strong2010b_claude_b32", "_setfile": "WIN_GEN2_ZGate_DailyRange_b32.set"})]
    c += [("z_cb_" + v, f"ChopBracket {v} re-tested (earlier fails were on gappy history)", {"_expert": "ChopBracket_" + v}) for v in ("h1a", "h1b", "h1c", "h1d", "h1a_brk", "h1b_brk", "h1c_brk")]
    CG = {"_expert": "Strong2010b_claude_b44_calm", "UseCalmGate": "true"}
    c += [("c_calm_strict", "calm+ordered tape: rvol20<=29.6, ATR<=45, perm entropy<=0.945 (all low terciles)", dict(CG, CalmRvolMax=29.6, CalmAtrMax=45, CalmPEMax=0.9452)),
          ("c_calm_mid", "lenient calm gate: rvol20<=45.6, ATR<=70, perm entropy<=0.969", dict(CG, CalmRvolMax=45.6, CalmAtrMax=70, CalmPEMax=0.969)),
          ("c_calm_pe_rvol", "low entropy + low realized vol only (rvol<=29.6, PE<=0.945)", dict(CG, CalmRvolMax=29.6, CalmPEMax=0.9452)),
          ("c_calm_rvol_only", "block high realized vol only (rvol<=45.6)", dict(CG, CalmRvolMax=45.6)),
          ("c_calm_mid_r2400", "lenient calm gate on regime-2400 parent", dict(CG, SellRegimePeriod=2400, CalmRvolMax=45.6, CalmAtrMax=70, CalmPEMax=0.969)),
          ("c_calm_strict_r2400", "strict calm gate on regime-2400 parent", dict(CG, SellRegimePeriod=2400, CalmRvolMax=29.6, CalmAtrMax=45, CalmPEMax=0.9452)),
          ("c_vov_mid_atr", "alternative winner: vol-of-vol high (>=0.375) at mid ATR (45-70)", {"_expert": "Strong2010b_claude_b44_calm", "UseVovGate": "true", "VovMin": 0.375, "VovAtrMin": 45, "VovAtrMax": 70})]
    c += [("t_trail100_50", "base EA trailing stop: after +100 pts keep SL 50 pts behind (UseTrail)", {"UseTrail": "true", "TrailStart": 100, "TrailStep": 50}),
          ("t_trail200_100", "base EA trailing stop: after +200 pts keep SL 100 pts behind", {"UseTrail": "true", "TrailStart": 200, "TrailStep": 100}),
          ("t_atrtrail", "base EA ATR trailing stop on ladder/sell-stop sells (1.0 x ATR)", {"UseAtrTrail": "true", "AtrTrailStart": 1.0, "AtrTrailMult": 1.0}),
          ("t_trail100_r2400", "regime-2400 parent + trailing 100/50", {"SellRegimePeriod": 2400, "UseTrail": "true", "TrailStart": 100, "TrailStep": 50}),
          ("b5_both_trail", "b50 both sides + trailing stop (start 150, 250 behind)", dict(B, SideMode=0, TrailStartPts=150, TrailDistPts=250)),
          ("b5_sell_trail", "b50 sell-only + trailing stop (start 150, 250 behind)", dict(B, SideMode=1, TrailStartPts=150, TrailDistPts=250))]
    c += [("r_tp450", "exit RR 1.5: sell-stop and ladder TP 450 vs SL 300 (break-even win rate ~42%)", {"SellStopTP": 450, "LadderTP": 450}),
          ("r_tp600", "exit RR 2.0: TP 600 vs SL 300 (break-even win rate ~37%)", {"SellStopTP": 600, "LadderTP": 600}),
          ("r_tp450_r2400", "RR 1.5 on the regime-2400 parent", {"SellRegimePeriod": 2400, "SellStopTP": 450, "LadderTP": 450}),
          ("r_tp600_r2400", "RR 2.0 on the regime-2400 parent", {"SellRegimePeriod": 2400, "SellStopTP": 600, "LadderTP": 600}),
          ("k_regadapt_up", "regime-2400 parent + adaptive extra regime, longer when volatile", dict(K, UseRegAdapt="true", RegAdaptDir=1)),
          ("k_regadapt_dn", "regime-2400 parent + adaptive extra regime, shorter when volatile", dict(K, UseRegAdapt="true", RegAdaptDir=-1)),
          ("n_newsday", "OOS replay: NFP/news days lose 4/4 years; EA news-day block on", {"UseNewsDayBlock": "true"}),
          ("w_wpr1_20", "Williams %R: block sells when %R >= -20 (overbought sells ok only after pullback)", {"UseWprGate": 1, "WprMax": -20}),
          ("w_wpr1_40", "Williams %R: block sells when %R >= -40", {"UseWprGate": 1, "WprMax": -40}),
          ("w_wpr2_80", "Williams %R: block sells when %R <= -80 (avoid selling exhausted lows)", {"UseWprGate": 2, "WprMin": -80}),
          ("w_adaptwpr", "adaptive %R period after losses", {"UseWprGate": 2, "WprMin": -80, "UseAdaptWpr": "true"}),
          ("w_alligator", "Alligator: sells only when jaws/teeth/lips are ordered down (trend, not sleeping)", {"UseAlligatorGate": "true"}),
          ("w_ao", "Awesome Oscillator momentum gate", {"UseAOGate": "true"}),
          ("w_ac", "Accelerator Oscillator gate", {"UseACGate": "true"}),
          ("w_chaos_all", "Bill Williams chaos set: Alligator+AO+AC", {"UseAlligatorGate": "true", "UseAOGate": "true", "UseACGate": "true"}),
          ("w_fracbreak", "Fractal breakout confirmation", {"UseFracBreakGate": "true"}),
          ("w_fracfail", "Fractal failure filter", {"UseFracFailGate": "true"}),
          ("w_entropy85", "complex-system order: entropy gate EntMax 0.85 (skip disordered tape)", {"UseEntropyGate": "true", "EntMax": 0.85}),
          ("w_entropy95", "entropy gate EntMax 0.95", {"UseEntropyGate": "true", "EntMax": 0.95}),
          ("w_chop50", "chop (ATR1/range) gate 50", {"UseChopGate": "true", "ChopMax": 50}),
          ("w_adx22", "ADX: sell block above ADX 22", {"UseSellBlock": "true", "BlockADX": 22}),
          ("w_adx35", "ADX: sell block above ADX 35", {"UseSellBlock": "true", "BlockADX": 35}),
          ("w_quiet", "ADX+range quiet gate on", {"UseQuietGate": "true"})]
    for (k, b), n, p in worst:
        if k == "hour":
            lo = b; c.append((f"d_hourblock{lo}", f"{lo}-{lo+3}h loses on OOS: block sells", {"UseSessWindow": "true", "SessStartMin": ((lo + 3) % 24) * 60, "SessEndMin": ((lo + 24 - 1) % 24) * 60 + 59}))
        if k == "er10" and b >= 2: c.append(("d_chop_er_hi", "high-ER10 entries lose (late trend): tighten chop gate", {"UseChopGate": "true", "ChopMax": 55}))
        if k == "er10" and b <= 1: c.append(("d_chop_er_lo", "low-ER10 chop loses: chop gate", {"UseChopGate": "true", "ChopMax": 50}))
        if k == "atr14_pts" and b >= 2: c.append(("d_range_tight", "high ATR loses: tighter daily-range cap", {"MaxRangeAtrMultiplier": 0.8}))
        if k == "slope20": c.append(("d_slopegate", "slope bucket loses: slope gate", {"UseSellSlopeGate": "true", "SlopeMinPts": 5}))
    # existing-rule variants
    c += [("e_zmax08", "tighter ZGate", {"ZMax": 0.8}), ("e_zmax12", "looser ZGate", {"ZMax": 1.2}),
          ("e_range07", "tighter range cap", {"MaxRangeAtrMultiplier": 0.7}),
          ("e_noladder", "ladder stacks 4 entries on one move; off", {"UseSellLadder": "false"}),
          ("e_entropy", "entropy gate on", {"UseEntropyGate": "true", "EntMax": 0.9})]
    seen, out = set(), []
    for n, r, p in c:
        if n in seen or n in state["tested"]: continue
        seen.add(n); out.append((n, r, p))
    new_logic = [x for x in out if x[0][:2] in ("k_", "mr", "d_", "w_", "n_", "r_", "b5", "t_", "c_", "z_") or x[0].startswith("u_regime_9") or x[0].startswith("u_regime_1")]   # ~70% of runtime: new logic on unseen history
    new_logic.sort(key=lambda x: -2 if x[0].startswith("z_") else -1 if x[0].startswith("c_") else 0 if x[0].startswith("b5_") else (1 if x[0].startswith(("r_", "t_")) else 2))   # new branches and exit ratios first
    return new_logic + [x for x in out if x not in new_logic]

# ---------- TEST + LEARN ----------
def main():
    state = load_state()
    base = read_set(BASE_SET)
    for y in OOS:
        p = os.path.join(HST_OUT, f"WIN_GEN1_{y}_sp5.htm")
        if not os.path.exists(p):
            run_test("WIN_GEN1_ZGate_DailyRange_b31.set", y, f"{y}.01.01", f"{y}.12.31", f"WIN_GEN1_{y}_sp5")
        if y not in state["base"] and os.path.exists(p):
            r = pr.parse_report(p)
            state["base"][y] = {"profit": float(r["profit"]), "pf": float(r["pf"]), "dd": float(r["dd_pct"]), "trades": int(r["trades"])}
    # backfill: finished passers (beat base on >=half of their years) get the never-tested years first
    for bn, bt in list(state["tested"].items()):
        if bt["of"] >= 2 and bt["beats"] * 2 >= bt["of"]:
            bpatch = dict(bt["patch"]); bset = f"LOOP_{bn}.set"
            if not os.path.exists(os.path.join(TESTER_DIR, bset)): build_set(os.path.join(TESTER_DIR, bset), bt.get("expert"), base, bpatch)
            for y in [y for y in OOS if y not in bt["oos"]]:
                if y not in state["base"]: continue
                bt["oos"][y] = run_test(bset, y, f"{y}.01.01", f"{y}.12.31", f"LOOP_{bn}_{y}_sp{SP}", bt.get("expert"))
                bt["of"] = len(bt["oos"]); bt["beats"] = sum(1 for yy in bt["oos"] if yy in state["base"] and bt["oos"][yy]["profit"] > state["base"][yy]["profit"])
                save_state(state); print(f"backfill {bn} {y}: {bt['oos'][y]['profit']:.0f} vs base {state['base'][y]['profit']:.0f}", flush=True)
    # 5-pt-commission audit: finished passers that never got the realistic-cost pass (5 comm + that year's avg real spread) get it now
    for an, at in (list(state["tested"].items()) if AUDIT_ONLY else []):
        if at.get("real") or at["of"] < 4 or at["beats"] * 4 < 3 * at["of"]: continue
        if sum(v["profit"] for v in at["oos"].values()) <= -0.25 * abs(sum(state["base"][y]["profit"] for y in at["oos"] if y in state["base"])): continue   # not near break-even: skip the audit
        aset = f"LOOP_{an}.set"; br = state.setdefault("base_real", {}); real = {}
        if not os.path.exists(os.path.join(TESTER_DIR, aset)): build_set(os.path.join(TESTER_DIR, aset), at.get("expert"), base, dict(at["patch"]))
        for y in at["oos"]:
            sp_y = real_sp(y)
            if y not in br: br[y] = run_test("WIN_GEN1_ZGate_DailyRange_b31.set", y, f"{y}.01.01", f"{y}.12.31", f"WIN_GEN1_{y}_real", None, sp_y)["profit"]
            real[y] = run_test(aset, y, f"{y}.01.01", f"{y}.12.31", f"LOOP_{an}_{y}_real", at.get("expert"), sp_y)["profit"]
        at["real"] = {"profit": real, "base": {y: br[y] for y in real}, "beats": sum(1 for y in real if real[y] > br[y]), "sp": {y: real_sp(y) for y in real}}
        save_state(state); print(f"AUDIT {an}: realistic-cost beats base {at['real']['beats']}/{len(real)} {real} vs base { {y: br[y] for y in real} }", flush=True)
    if AUDIT_ONLY: return
    for rnd in range(ROUNDS):
        worst = analyze(state)
        print("insights:", state["insights"])
        queue = candidates(worst, state)
        if not queue: print("no new candidates"); break
        fam_fail = state.setdefault("family_fail", {}); ran = 0; n_exp = 0
        def is_exploit(n): return "_m1" in n or "_m2" in n or n.startswith("x_")
        def load_extra():   # data/extra_candidates.json: [{"name":..,"why":..,"patch":{..}}] added on the fly, no restart needed
            try: return json.load(open(os.path.join(DATA, "extra_candidates.json")))
            except Exception: return []
        while queue and ran < MAXC:
            for ex_ in reversed(load_extra()):
                if ex_["name"] not in state["tested"] and not any(q[0] == ex_["name"] for q in queue):
                    queue.insert(0, (ex_["name"], ex_.get("why", "extra"), ex_["patch"]))
            # anti-clone diversity: keep explorer (non-derived) share >= 25% of this pass
            ei = next((i for i, q in enumerate(queue) if not is_exploit(q[0])), None)
            idx = ei if (ei is not None and ran > 0 and n_exp / ran < 0.25) else 0
            name, why, patch = queue.pop(idx); ran += 1; n_exp += 0 if is_exploit(name) else 1
            prog(candidate=name, done=ran - 1, total=min(MAXC, ran - 1 + len(queue) + 1), years=len(OOS))
            fam = name.split("_")[0]
            patch = dict(patch); expert = patch.pop("_expert", None)
            sname = f"LOOP_{name}.set"; sf = patch.get("_setfile")
            if sf: shutil.copy(os.path.join(WINNERS, sf), os.path.join(TESTER_DIR, sname))   # old branch: run its saved .set exactly as it was
            else: build_set(os.path.join(TESTER_DIR, sname), expert, base, patch)
            res = {}
            for y in OOS:
                res[y] = run_test(sname, y, f"{y}.01.01", f"{y}.12.31", f"LOOP_{name}_{y}_sp{SP}", expert)
                if y == OOS[0] and res[y]["profit"] <= state["base"][y]["profit"]:
                    print(f"{name}: not better on {y}, abort screen"); break
            beats = sum(1 for y in res if y in state["base"] and res[y]["profit"] > state["base"][y]["profit"])
            sel_b = sum(1 for y in res if y in SELECT and res[y]["profit"] > state["base"][y]["profit"])
            conf_b = sum(1 for y in res if y in CONFIRM and res[y]["profit"] > state["base"][y]["profit"])
            promoted = len(res) == len(OOS) and sel_b >= 2 and conf_b >= 4 and sum(r["trades"] for r in res.values()) >= 100   # zero-trade years must not count as wins   # walk-forward: select on SELECT years, must hold on CONFIRM years
            state["tested"][name] = {"why": why, "patch": patch, "expert": expert, "oos": res, "beats": beats, "of": len(res),
                                     "select_beats": sel_b, "confirm_beats": conf_b, "promoted": promoted}
            print(f"{name}: beats base {beats}/{len(res)} select {sel_b}/{len(SELECT)} confirm {conf_b}/{len(CONFIRM)} PROMOTED={promoted} {res}")
            # ALWAYS-ON tier round (Nasif 2026-10-14): FXOpen $25k+ balance tier = 1.80/side/lot = 3.6 round trip (EUR basis ~4.1) -> tested at T25K_SP pts for every year this candidate ran, vs base at the same cost. Label: sp4 T25k.
            t25 = state["tested"][name].setdefault("t25k", {}); bt25 = state.setdefault("base_t25k", {})
            for y in res:
                if y not in bt25: _r = run_test("WIN_GEN1_ZGate_DailyRange_b31.set", y, f"{y}.01.01", f"{y}.12.31", f"WIN_GEN1_{y}_sp{T25K_SP}_T3p45", None, T25K_SP); bt25[y] = _r["profit"] - T25K_EXTRA * 0.16 * _r["trades"]
                _r = run_test(sname, y, f"{y}.01.01", f"{y}.12.31", f"LOOP_{name}_{y}_sp{T25K_SP}_T3p45", expert, T25K_SP); t25[y] = _r["profit"] - T25K_EXTRA * 0.16 * _r["trades"]
            # LOW-SPREAD variant (Nasif 2026-10-14): 3.45 commission + ~2 pt spread = 5.45 total, derived exactly from the sp5 run (-0.45 pt/trade). Promoted candidates also get REAL sp2 runs (lowest-cost sensitivity).
            state["tested"][name]["cost_grid"] = {f"comm{c}+spr{s}": {y: res[y]["profit"] - (c + s - SP) * 0.16 * res[y]["trades"] for y in res} for c in (8.05, 5.75, 4.14, 3.45) for s in (1, 2)}   # FLAT commission by balance tier (RT pts: <1k 8.05, 1k-25k 5.75, 25k-250k 4.14, >250k 3.45; EUR basis x1.15, UNVERIFIED) + bid/ask spread 1 or 2 pts; derived exactly from the sp{SP} run (cost is linear in trades)
            state["tested"][name]["t25k_beats"] = sum(1 for y in t25 if t25[y] > bt25[y]); print(f"{name}: T3p45(sp{T25K_SP}+{T25K_EXTRA}/trade) beats base {state['tested'][name]['t25k_beats']}/{len(t25)} {t25} vs base {bt25}")
            save_state(state)
            near_even = sum(r["profit"] for r in res.values()) > -0.25 * abs(sum(state["base"][y]["profit"] for y in res if y in state["base"]))   # audit only near-break-even candidates
            if len(res) >= 4 and beats * 4 >= 3 * len(res) and near_even:   # realistic-cost validation: per-year cost = 5 comm + that year's avg real spread
                br = state.setdefault("base_real", {}); real = {}
                for y in res:
                    sp_y = real_sp(y)
                    if y not in br:
                        br[y] = run_test("WIN_GEN1_ZGate_DailyRange_b31.set", y, f"{y}.01.01", f"{y}.12.31", f"WIN_GEN1_{y}_real", None, sp_y)["profit"]
                    real[y] = run_test(sname, y, f"{y}.01.01", f"{y}.12.31", f"LOOP_{name}_{y}_real", expert, sp_y)["profit"]
                rb = sum(1 for y in real if real[y] > br[y])
                state["tested"][name]["real"] = {"profit": real, "base": {y: br[y] for y in real}, "beats": rb, "sp": {y: real_sp(y) for y in real}}
                print(f"{name}: REALISTIC-COST beats base {rb}/{len(real)} {real} vs base {br}")
            passed_first = len(res) > 1
            if not passed_first:
                fam_fail[fam] = fam_fail.get(fam, 0) + 1
                if fam_fail[fam] >= 3:   # stalled family: push its remaining members to the back
                    queue = [q for q in queue if q[0].split("_")[0] != fam] + [q for q in queue if q[0].split("_")[0] == fam]
                    state["insights"].append(f"family '{fam}' stalled after {fam_fail[fam]} fails: deprioritized")
            else:
                fam_fail[fam] = 0
                if name.count("_m") < 2:   # clone + mutate a near-winner: numeric neighbours go to the front
                    nb = []
                    for fac, tag in ((0.8, "_m1"), (1.25, "_m2")):
                        np_ = {}
                        for k_, v_ in patch.items():
                            if isinstance(v_, (int, float)) and not isinstance(v_, bool):
                                nv = v_ * fac; np_[k_] = int(round(nv)) if isinstance(v_, int) else round(nv, 3)
                            else: np_[k_] = v_
                        if np_ != patch:
                            full = dict(np_);
                            if expert: full["_expert"] = expert
                            nb.append((name + tag, f"mutation of {name} (x{fac})", full))
                    queue = [q for q in nb if q[0] not in state["tested"]] + queue
                # crossover: breed this passer with up to 2 other passers (merge patches, current candidate wins conflicts)
                def egroup(e):   # only EAs that share input names may be crossed
                    e = str(e); return "mr50" if "MR_Regime" in e else "chop" if "ChopBracket" in e else "b38" if "b38" in e else "b32" if "b32" in e else "strong"
                partners = [] if name.startswith("x_") else sorted([(n_, t_) for n_, t_ in state["tested"].items() if n_ != name and not n_.startswith("x_")
                                   and t_["of"] >= 2 and t_["beats"] * 2 >= t_["of"] and egroup(t_.get("expert")) == egroup(expert)
                                   and not t_["patch"].get("_setfile") and not patch.get("_setfile")], key=lambda x: -x[1]["beats"])[:2]
                sigs = {json.dumps(t_["patch"], sort_keys=True) + str(t_.get("expert")) for t_ in state["tested"].values()}
                for pn, pt in partners:
                    cn = f"x_{name[:22]}__{pn[:22]}"
                    if cn in state["tested"] or any(q[0] == cn for q in queue): continue
                    child = dict(pt["patch"]); child.update(patch)
                    if json.dumps(child, sort_keys=True) + str(expert or pt.get("expert")) in sigs: continue   # identical to something already tested
                    ex = "Strong2010b_claude_b43_chaos" if "b43" in str(expert) + str(pt.get("expert")) else (expert or pt.get("expert"))
                    if ex: child["_expert"] = ex
                    queue.insert(0, (cn, f"crossover of {name} x {pn}", child))
            save_state(state)
        state.setdefault("diversity", []).append({"when": f"{datetime.datetime.now():%Y-%m-%d %H:%M}", "explore": n_exp,
                                                  "exploit": ran - n_exp, "ratio": round(n_exp / max(ran, 1), 2)})
        state["rounds"] += 1
    try:   # untested branches first; the realistic-cost audit of finished passers runs after the pass
        subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "--audit-only", "--spread", str(SP)])
    except Exception as e: print("audit pass skipped:", e)
    try:   # silent shadow audit of alternative entry logic (never feeds back into pass/fail; self-skips on low RAM)
        subprocess.run([sys.executable, "-I", os.path.join(DATA, "shadow_audit.py")], timeout=900)
    except Exception as e: print("shadow audit skipped:", e)
    with open(REPORT, "w") as f:
        f.write(f"# auto_loop report {datetime.datetime.now():%Y-%m-%d %H:%M} (sp{SP}, backtest only)\n\n")
        f.write("Base OOS: " + json.dumps(state["base"]) + "\n\nWorst buckets: " + "; ".join(state["insights"]) + "\n\n")
        f.write("Diversity (explore share per pass, target >= 0.25): " + json.dumps(state.get("diversity", [])) + "\n\n")
        for n, t in sorted(state["tested"].items(), key=lambda x: -x[1]["beats"]):
            f.write(f"- {n}: beats {t['beats']}/{t['of']} promoted={t.get('promoted')} | {t['why']} | {t['oos']}\n")
    save_state(state)

if __name__ == "__main__":
    main()











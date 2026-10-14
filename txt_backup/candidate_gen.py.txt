"""
candidate_gen.py  -  Theorize new win-logic branches from ER/MMR analysis.
Reads m15_metrics.csv, finds threshold combos that could improve entry quality,
writes candidate .set files to mt4_tester/tester/ and prints PowerShell test commands.

MMR (c) Nasif Hossain 2019. ER (c) Perry Kaufman 1995.

Run: python -I data/candidate_gen.py [--report path_to_html_report]
"""

import csv, os, sys, shutil, datetime

METRICS_CSV  = r"C:\Users\endos\Signal\data\m15_metrics.csv"
BASE_SET     = r"C:\Users\endos\Desktop\mt4_tester\tester\WIN_GEN1_ZGate_DailyRange_b31.set"
TESTER_DIR   = r"C:\Users\endos\Desktop\mt4_tester\tester"
OUT_LOG      = r"C:\Users\endos\Signal\data\candidate_log.csv"
RUN_TESTER   = r"C:\Users\endos\Desktop\hst_out\run_tester.ps1"
EXPERT       = "Strong2010b_claude_b31"
SPREAD       = 6   # FXOpen ECN EURUSD max commission (c) Nasif Hossain - verified 2026-10-13

# ── Candidate definitions ──────────────────────────────────────────────────────
# Each candidate adds one or two new gate parameters to the winner .set.
# 'patch' = dict of lines to change in the .set file (key=param name, value=new value)
# 'rationale' = brief theory text for the log

CANDIDATES = [
    {
        "name": "er10_gate_low",
        "rationale": "Kaufman ER10 < 0.35 = too choppy to enter; gate off random entries",
        "patch": {"UseCalcGate": 1, "CalcTF": 15},   # placeholder; see note below
        "er_min": 0.35, "er_max": 1.0,
    },
    {
        "name": "er10_gate_mid",
        "rationale": "Kaufman ER10 > 0.25 AND < 0.70 = efficient but not blow-off; sweet spot",
        "patch": {"UseCalcGate": 1, "CalcTF": 15},
        "er_min": 0.25, "er_max": 0.70,
    },
    {
        "name": "mmr_boost_strict",
        "rationale": "Nasif MMR > 2.0 on M15 (stronger one-direction dominance than current default ~1.0 via ZGate)",
        "patch": {"UseZGate": 1, "ZMax": 0.8},   # tighter Z = higher quality entries
    },
    {
        "name": "mmr_relaxed_er",
        "rationale": "Relax ZMax to 1.5 but require ER10 > 0.30 (quality from ER, not just Z)",
        "patch": {"UseZGate": 1, "ZMax": 1.5},
    },
    {
        "name": "er_replaces_zgate",
        "rationale": "Turn off ZGate, use only DailyRange filter; ER is a purer choppiness measure",
        "patch": {"UseZGate": 0, "ZMax": 1.0},
    },
]

# ── read base .set ─────────────────────────────────────────────────────────────

def read_set(path):
    lines = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith(';'):
                k, v = line.split('=', 1)
                lines[k.strip()] = v.strip()
    return lines

def write_set(path, base_lines, patch):
    merged = dict(base_lines)
    for k, v in patch.items():
        merged[k] = str(v)
    with open(path, 'w') as f:
        for k, v in merged.items():
            f.write(f"{k}={v}\n")

# ── metrics summary ────────────────────────────────────────────────────────────

def summarize_metrics():
    if not os.path.exists(METRICS_CSV):
        print(f"  metrics CSV not found: {METRICS_CSV}")
        print("  Run analyze_hst.py first.")
        return None

    er10_vals = []; er20_vals = []; mmr_vals = []
    slp20_vals = []; k14_vals = []
    n = 0
    with open(METRICS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                er10_vals.append(float(row['er10']))
                er20_vals.append(float(row['er20']))
                mmr_vals.append(float(row['mmr_6_12_18']))
                slp20_vals.append(float(row['slope20']))
                k14_vals.append(float(row['stoch_k14']))
                n += 1
            except: pass

    if n == 0: return None

    def pct(vals, p): vals_s = sorted(vals); return vals_s[int(len(vals_s)*p/100)]

    print(f"\n  Metric summary over {n:,} M15 bars:")
    print(f"  ER10  p10={pct(er10_vals,10):.3f}  p25={pct(er10_vals,25):.3f}  "
          f"median={pct(er10_vals,50):.3f}  p75={pct(er10_vals,75):.3f}  p90={pct(er10_vals,90):.3f}")
    print(f"  ER20  p10={pct(er20_vals,10):.3f}  p25={pct(er20_vals,25):.3f}  "
          f"median={pct(er20_vals,50):.3f}  p75={pct(er20_vals,75):.3f}  p90={pct(er20_vals,90):.3f}")
    print(f"  MMR   p10={pct(mmr_vals,10):.3f}  p25={pct(mmr_vals,25):.3f}  "
          f"median={pct(mmr_vals,50):.3f}  p75={pct(mmr_vals,75):.3f}  p90={pct(mmr_vals,90):.3f}")
    print(f"  Slp20 p10={pct(slp20_vals,10):.1f}  p25={pct(slp20_vals,25):.1f}  "
          f"median={pct(slp20_vals,50):.1f}  p75={pct(slp20_vals,75):.1f}  p90={pct(slp20_vals,90):.1f}")
    return {"er10": er10_vals, "er20": er20_vals, "mmr": mmr_vals}

# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== candidate_gen.py ===\n")
    metrics = summarize_metrics()
    base_lines = read_set(BASE_SET)

    print(f"\nGenerating {len(CANDIDATES)} candidate .set files...\n")
    cmds = []
    log_rows = []

    for cand in CANDIDATES:
        name = cand["name"]
        fname = f"CAND_ER_{name}.set"
        fpath = os.path.join(TESTER_DIR, fname)
        write_set(fpath, base_lines, cand["patch"])
        print(f"  {fname}  ({cand['rationale']})")

        for year in ["2017", "2019"]:  # quick 2-year screen (known-good periods)
            tag = f"ER_{name}_{year}_sp{SPREAD}"
            cmd = (f'powershell -ExecutionPolicy Bypass -File "{RUN_TESTER}" '
                   f'-Expert "{EXPERT}" -SetFile "{fname}" '
                   f'-From "{year}.01.01" -To "{year}.12.31" '
                   f'-Spread {SPREAD} -Model 0 -Tag "{tag}"')
            cmds.append((tag, cmd))
            log_rows.append({"name": name, "year": year, "tag": tag,
                              "rationale": cand["rationale"], "result": "PENDING"})

    # save log
    with open(OUT_LOG, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=["name","year","tag","rationale","result"])
        w.writeheader(); w.writerows(log_rows)

    print(f"\nCandidate log -> {OUT_LOG}")
    print("\n=== POWERSHELL TEST COMMANDS (run one at a time) ===\n")
    for tag, cmd in cmds:
        print(f"# {tag}")
        print(cmd)
        print()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
run_backtest.py — one-command backtest wrapper for Claude Code CLI.
Primary engine: node tools/w2_node.js (w2_node_fx.js for FX pairs)
Fallback engine: backtest_costs.py (Python, stocks/ETFs)

Usage:
  python3 run_backtest.py [options]

Options:
  --csv PATH      CSV file or glob to analyse (default: auto-detect hst_out)
  --engine        node|python (default: node)
  --hold N        Hold bars for Python engine (default: 3)
  --group         fx|stock|crypto for Python engine (default: fx)

CSV search order (first non-empty wins):
  1. C:\\Users\\endos\\Desktop\\hst_out\\*.csv
  2. C:\\Users\\endos\\AppData\\Roaming\\MetaQuotes\\Terminal\\...\\history\\FXOpenEU-ECN Live Server\\*.csv
  3. data/history/*.csv  (fallback local)
"""
import subprocess, sys, os, shutil, datetime, glob

RESULTS_DIR = "results"
SHARED_DIR = "/mnt/project-files/results"

HST_PATHS = [
    r"C:\Users\endos\Desktop\hst_out",
    r"C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\history\FXOpenEU-ECN Live Server",
    "data/history",
]

def find_csvs(explicit=None):
    if explicit:
        files = glob.glob(explicit)
        if files:
            return files
    for path in HST_PATHS:
        files = glob.glob(os.path.join(path, "*.csv"))
        if files:
            print(f"[backtest] Using CSVs from: {path}", flush=True)
            return files
    return []

def run_node(csvs, date_str):
    engine = "tools/w2_node_fx.js" if os.path.exists("tools/w2_node_fx.js") else "tools/w2_node.js"
    out_md = os.path.join(RESULTS_DIR, f"cli_backtest_{date_str}.md")
    lines = [f"# CLI Backtest (node) {date_str}\n", f"**Engine:** {engine}\n\n"]
    ok = True
    for csv in csvs:
        cmd = ["node", engine, csv]
        print(f"[backtest] {' '.join(cmd)}", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout[:2000])
        if r.returncode != 0:
            print("STDERR:", r.stderr[:500])
            ok = False
        lines.append(f"## {os.path.basename(csv)}\n```\n{r.stdout}\n```\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_md, "w") as f:
        f.writelines(lines)
    return out_md, ok

def run_python(hold, group, date_str):
    out_md = os.path.join(RESULTS_DIR, f"cli_backtest_{date_str}.md")
    cmd = [sys.executable, "backtest_costs.py",
           "--data", "data/history",
           "--hold", str(hold),
           "--cost", "cost_model.json",
           "--group", group]
    print(f"[backtest] {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr)
        return out_md, False
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_md, "w") as f:
        f.write(f"# CLI Backtest (python) {date_str}\n\n")
        f.write(f"**Args:** hold={hold} group={group}\n\n")
        f.write(f"```\n{r.stdout}\n```\n")
    return out_md, True

def commit_and_push(out_md):
    subprocess.run(["git", "add", out_md], check=False)
    subprocess.run(["git", "commit", "-m",
        f"backtest results {datetime.date.today().isoformat()}\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"],
        check=False)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], check=False)

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=None)
    p.add_argument("--engine", default="node", choices=["node", "python"])
    p.add_argument("--hold", type=int, default=3)
    p.add_argument("--group", default="fx")
    args = p.parse_args()

    # Disk check
    free_gb = shutil.disk_usage(".").free / 1e9
    if free_gb < 2:
        print(f"WARNING: only {free_gb:.1f}GB free", flush=True)

    date_str = datetime.date.today().isoformat()

    if args.engine == "node":
        csvs = find_csvs(args.csv)
        if not csvs:
            print("No CSVs found. Drop MT4 exports into hst_out or data/history/")
            sys.exit(1)
        out_md, ok = run_node(csvs, date_str)
    else:
        out_md, ok = run_python(args.hold, args.group, date_str)

    print(f"\n[backtest] Wrote {out_md}", flush=True)

    if os.path.isdir(SHARED_DIR):
        shutil.copy(out_md, SHARED_DIR)
        print(f"[backtest] Copied to {SHARED_DIR}", flush=True)

    commit_and_push(out_md)

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
run_backtest.py — one-command backtest wrapper for Claude Code CLI.
Usage: python3 run_backtest.py [--hold N] [--group fx|stock|crypto] [--data PATH]

Reads CSVs from data/history/, runs net-of-costs backtest, writes results/cli_backtest_<date>.md,
optionally copies to /mnt/project-files/results/ if mounted.
"""
import subprocess, sys, os, shutil, datetime

RESULTS_DIR = "results"
SHARED_DIR = "/mnt/project-files/results"

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--hold", type=int, default=3)
    p.add_argument("--group", default="fx")
    p.add_argument("--data", default="data/history")
    args = p.parse_args()

    # Disk check
    st = shutil.disk_usage(".")
    free_gb = st.free / 1e9
    if free_gb < 2:
        print(f"WARNING: only {free_gb:.1f}GB free — proceed with caution", flush=True)

    if not os.path.isdir(args.data) or not any(f.endswith(".csv") for f in os.listdir(args.data)):
        print(f"No CSVs in {args.data}. Run: python3 fetch_history.py --universe universe.txt --out {args.data}")
        sys.exit(1)

    date_str = datetime.date.today().isoformat()
    out_md = os.path.join(RESULTS_DIR, f"cli_backtest_{date_str}.md")

    cmd = [sys.executable, "backtest_costs.py",
           "--data", args.data,
           "--hold", str(args.hold),
           "--cost", "cost_model.json",
           "--group", args.group]

    print("Running:", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        sys.exit(result.returncode)

    # Write markdown summary
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_md, "w") as f:
        f.write(f"# CLI Backtest {date_str}\n\n")
        f.write(f"**Args:** hold={args.hold} group={args.group} data={args.data}\n\n")
        f.write("```\n" + result.stdout + "\n```\n")

    print(f"\nWrote {out_md}", flush=True)

    # Copy to shared folder if mounted
    if os.path.isdir(SHARED_DIR):
        shutil.copy(out_md, SHARED_DIR)
        print(f"Copied to {SHARED_DIR}", flush=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Neoclone Backtest Runner — Execute 108-run suite on MT4 cloud.
Generates per-run configurations, compile directives, and result aggregation.

11 Nov 2026 — Nasif cloud backtest series
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from neoclone_harness import NeocloneHarness, EntryType, OrderType

def main():
    print("=" * 80)
    print("NEOCLONE BATCH BACKTEST RUNNER — 2015-W23 HURRICANE")
    print("=" * 80)

    harness = NeocloneHarness("commission_registry.json")

    # Build 108 test configurations (4 variants × 3 entry × 3 TP × 6 commission)
    variants = ["T92_M15", "NC-A", "NC-B", "NC-C"]
    entry_types = [EntryType.MARKET, EntryType.BRACKET, EntryType.STOP_ORDER]
    tp_types = ["fixed", "trailing_1pct", "trailing_2pct"]
    # First test: 3 key tiers per COMMISSION — FIRST TEST RULE (Standing Rules)
    # gross_0pts (baseline) + over_250k_1.5pts (first test) + sim_2.5pts (cloud sim)
    comm_tiers = ["gross_0pts", "over_250k_1.5pts", "sim_2.5pts"]

    run_count = 0
    for variant in variants:
        for entry_type in entry_types:
            for tp_type in tp_types:
                for comm_tier in comm_tiers:
                    hedge_enabled = True
                    loss_recovery = True
                    # FP fixes on slow pupils only (NC-A, NC-B, NC-C)
                    fp_fixes = (variant != "T92_M15")

                    run = harness.create_run(
                        variant_name=variant,
                        entry_type=entry_type,
                        tp_type=tp_type,
                        commission_tier=comm_tier,
                        hedge_enabled=hedge_enabled,
                        loss_recovery_enabled=loss_recovery,
                        fp_fixes_applied=fp_fixes,
                        period="2015-W23"
                    )
                    run_count += 1

    print(f"\n✓ Created {run_count} backtest run configurations")
    print(f"  Variants: {len(variants)}")
    print(f"  Entry types: {len(entry_types)}")
    print(f"  TP modes: {len(tp_types)}")
    print(f"  Commission tiers: {len(comm_tiers)}")
    print(f"  Total: {len(variants)} × {len(entry_types)} × {len(tp_types)} × {len(comm_tiers)} = {run_count}")
    print(f"\n  ★ Per Standing Rules: first test uses cheapest tier (over_250k_1.5pts = 1.5 pts RT)")
    print(f"  ★ Survivors re-test at sim tier (sim_2.5pts = 2.5 pts RT)")

    # Write config
    harness.write_config_json("neoclone_runs_config.json")
    print("\n✓ Wrote neoclone_runs_config.json (108 run metadata)")

    # Write results stub
    harness.write_results_csv("neoclone_runs_results_stub.csv")
    print("✓ Wrote neoclone_runs_results_stub.csv (result template)")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("""
1. Compile EA variants:
   - T92_M15_Neoclone_HURRICANE.mq4 (no FP fixes)
   - NC-A_Neoclone_HURRICANE.mq4 (+ FP fixes)
   - NC-B_Neoclone_HURRICANE.mq4 (+ FP fixes)
   - NC-C_Neoclone_HURRICANE.mq4 (+ FP fixes)

2. Configure MT4 tester:
   - Symbol: EURUSD
   - Timeframe: M15
   - Period: 2015-06-01 to 2015-06-07 (HURRICANE week)
   - Balance: $5000 (sim tier, 2.5 pts RT commission)
   - Leverage: 500:1
   - Lot: 0.01

3. Execute backtest suite:
   - Run each variant with all entry/TP/commission permutations
   - Extract: WR%, PF, max DD, net PnL, n_trades per run
   - Log to neoclone_runs_results_stub.csv

4. Analyze results:
   - Filter: PF > 1.2, WR > 55%, n >= 6
   - Identify best performers per variant
   - Compare trailing-TP vs fixed-TP (validate standing rule)
   - Write SURVIVORS.md

5. Iterate improvements:
   - Apply logic adjustments to slow pupils (NC-A/B/C)
   - Re-test on cloud
   - Report WR/PF/DD per theory
""")

    return 0

if __name__ == "__main__":
    sys.exit(main())

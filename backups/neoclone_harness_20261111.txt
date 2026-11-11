#!/usr/bin/env python3
"""
Neoclone Batch Test Harness — 10 Nov 2026
Orchestrates trailing-stop, alternate-entry, loss-recovery, and high-DD hedge theories.
FP fixes (p=0.0001, NormalizeDouble) applied to slow_pupils only.
M1-resolved fill causality for all orders.
"""

import json
import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
from enum import Enum
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# ENUMS & TYPES
# ─────────────────────────────────────────────────────────────────────────────

class OrderType(Enum):
    BUY = 1
    SELL = -1

class EntryType(Enum):
    MARKET = "market"              # Standard market entry
    BRACKET = "bracket"            # Bracket order (entry + TP/SL in one)
    STRADDLE = "straddle"          # Both BUY & SELL limit orders, first fill wins
    STOP_ORDER = "stop"            # Entry via stop, not market
    LIMIT_ORDER = "limit"          # Entry via limit

class HedgeState(Enum):
    NO_HEDGE = 0
    HEDGE_TRIGGERED = 1
    HEDGE_FILLED = 2

@dataclass
class Trade:
    """Atomic trade record."""
    trade_id: int
    entry_type: EntryType
    order_type: OrderType
    entry_price: float
    entry_bar: int                  # M1 bar index
    entry_time: str

    tp_price: Optional[float] = None
    sl_price: Optional[float] = None
    tp_type: str = "fixed"          # "fixed" or "trailing"
    trailing_pct: Optional[float] = None  # For trailing TP

    exit_price: Optional[float] = None
    exit_bar: Optional[int] = None
    exit_time: Optional[str] = None
    exit_reason: str = "open"       # "tp", "sl", "hedge", "timeout"

    # Hedge info
    hedge_state: HedgeState = HedgeState.NO_HEDGE
    hedge_order_type: Optional[OrderType] = None
    hedge_entry_price: Optional[float] = None
    hedge_exit_price: Optional[float] = None

    # Stats
    gross_pnl_pts: Optional[float] = None
    net_pnl_pts: Optional[float] = None
    commission_pts: float = 0.0
    max_dd_pts: float = 0.0
    win: Optional[bool] = None

    # Loss recovery
    loss_recovery_attempt: bool = False
    is_recovery_trade: bool = False

@dataclass
class BacktestRun:
    """Single backtest configuration & results."""
    run_id: str
    variant_name: str
    entry_type: EntryType
    tp_type: str                    # "fixed" or "trailing"
    commission_tier: str            # "over_250k_1.5pts", "sim_2.5pts", etc.
    commission_pts: float
    hedge_enabled: bool
    loss_recovery_enabled: bool
    fp_fixes_applied: bool

    period: str                     # "2015-W23", "2020-22", etc.
    m1_data_source: str             # Path to M1 OHLCV CSV

    trades: List[Trade] = field(default_factory=list)

    # Results
    n_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate_pct: float = 0.0
    avg_net_pts_per_trade: float = 0.0
    pf: float = 0.0                 # Profit factor
    max_dd_pts: float = 0.0
    total_net_pnl_pts: float = 0.0

    status: str = "pending"         # "pending", "running", "completed", "failed"
    error_msg: Optional[str] = None

# ─────────────────────────────────────────────────────────────────────────────
# LOSS TRACKER & DD MONITOR
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LossTrackerState:
    """Tracks consecutive losses for recovery logic."""
    last_trade: Optional[Trade] = None
    last_order_type: Optional[OrderType] = None
    consecutive_losses: int = 0
    last_loss_time_str: Optional[str] = None

    def update(self, trade: Trade) -> None:
        """Update loss tracking after trade closes."""
        if trade.win is False:
            self.consecutive_losses += 1
            self.last_loss_time_str = trade.exit_time
        else:
            self.consecutive_losses = 0
        self.last_trade = trade
        self.last_order_type = trade.order_type

@dataclass
class DrawdownTracker:
    """Tracks intra-trade drawdown for hedge trigger logic."""
    entry_price: float
    entry_bar: int
    order_type: OrderType
    current_price: float = None
    max_dd_pts: float = 0.0
    dd_trigger_pct: float = 2.0     # Hedge at 2% DD

    def update(self, bar_price: float) -> Tuple[bool, float]:
        """
        Update with current bar price.
        Returns (hedge_triggered, dd_pct).
        """
        self.current_price = bar_price
        if self.order_type == OrderType.BUY:
            dd_pts = self.entry_price - bar_price
            dd_pct = (dd_pts / self.entry_price) * 100.0
        else:  # SELL
            dd_pts = bar_price - self.entry_price
            dd_pct = (dd_pts / self.entry_price) * 100.0

        self.max_dd_pts = max(self.max_dd_pts, dd_pts)
        hedge_triggered = dd_pct >= self.dd_trigger_pct
        return hedge_triggered, dd_pct

# ─────────────────────────────────────────────────────────────────────────────
# M1-RESOLVED FILL ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def m1_resolve_fill(
    order_type: OrderType,
    entry_price: float,
    bar_m1_data: Dict,  # {"open": o, "high": h, "low": l, "close": c}
    entry_type: EntryType = EntryType.MARKET,
    is_sl_first: bool = True
) -> Tuple[bool, float, str]:
    """
    M1-resolution causality: check if entry_price is reachable in bar.
    SL-first on ties (prevent lookahead bias).

    Returns (filled, fill_price, reason).
    """
    o, h, l, c = bar_m1_data["open"], bar_m1_data["high"], bar_m1_data["low"], bar_m1_data["close"]

    if entry_type == EntryType.MARKET:
        # Market entry at open
        return (True, o, "market_open")

    elif entry_type == EntryType.STOP_ORDER:
        # Stop order enters on breach of entry_price
        if order_type == OrderType.BUY:
            if l <= entry_price <= h:
                return (True, entry_price, "stop_fill")
        else:  # SELL
            if l <= entry_price <= h:
                return (True, entry_price, "stop_fill")
        return (False, None, "stop_not_touched")

    elif entry_type == EntryType.LIMIT_ORDER:
        # Limit order enters on touch of entry_price (never worse)
        if order_type == OrderType.BUY:
            if l <= entry_price <= h:
                return (True, entry_price, "limit_fill")
        else:  # SELL
            if l <= entry_price <= h:
                return (True, entry_price, "limit_fill")
        return (False, None, "limit_not_touched")

    elif entry_type == EntryType.BRACKET:
        # Bracket: entry at market, but instant SL & TP in effect
        return (True, o, "bracket_market")

    elif entry_type == EntryType.STRADDLE:
        # Straddle: whichever side fills first wins
        # (This is handled by the strategy, not here)
        return (True, o, "straddle_market")

    return (False, None, "unknown_entry_type")

def m1_resolve_exit(
    order_type: OrderType,
    tp_price: Optional[float],
    sl_price: Optional[float],
    bar_m1_data: Dict
) -> Tuple[str, float]:
    """
    M1-resolved exit causality: TP or SL hit first.
    SL-first on ties.

    Returns (exit_reason, exit_price).
    """
    o, h, l, c = bar_m1_data["open"], bar_m1_data["high"], bar_m1_data["low"], bar_m1_data["close"]

    # Check SL first (sl_price touched first on ambiguity)
    if order_type == OrderType.BUY:
        if sl_price is not None and l <= sl_price:
            return ("sl", sl_price)
        if tp_price is not None and h >= tp_price:
            return ("tp", tp_price)
    else:  # SELL
        if sl_price is not None and h >= sl_price:
            return ("sl", sl_price)
        if tp_price is not None and l <= tp_price:
            return ("tp", tp_price)

    return (None, None)

# ─────────────────────────────────────────────────────────────────────────────
# HEDGE ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_hedge_trigger(
    trade: Trade,
    dd_tracker: DrawdownTracker,
    current_dd_pct: float,
    hedge_config: Dict
) -> bool:
    """
    Evaluate if hedge should be triggered based on DD.
    """
    dd_trigger_pct = hedge_config.get("dd_trigger_pct", 2.0)
    return current_dd_pct >= dd_trigger_pct

def compute_hedge_lot_size(
    base_lot: float,
    dd_pct: float,
    hedge_config: Dict
) -> float:
    """
    Scale lot size down as DD increases.
    Default: at 2% DD, scale to 50% of base.
    """
    scale_factor = max(0.25, 1.0 - (dd_pct / 100.0) * 0.375)
    hedge_lot = base_lot * 0.5 * scale_factor
    return hedge_lot

# ─────────────────────────────────────────────────────────────────────────────
# MAIN HARNESS CLASS
# ─────────────────────────────────────────────────────────────────────────────

class NeocloneHarness:
    """Orchestrates backtest runs."""

    def __init__(self, commission_registry_path: str):
        with open(commission_registry_path) as f:
            self.commission_registry = json.load(f)
        self.runs: List[BacktestRun] = []

    def create_run(
        self,
        variant_name: str,
        entry_type: EntryType,
        tp_type: str,
        commission_tier: str,
        hedge_enabled: bool = False,
        loss_recovery_enabled: bool = False,
        fp_fixes_applied: bool = False,
        period: str = "2015-W23",
        m1_data_source: str = None
    ) -> BacktestRun:
        """Create a new backtest run configuration."""
        comm_tiers = self.commission_registry["commission_tiers"]
        comm_pts = comm_tiers[commission_tier]["rt_per_lot"]

        run_id = f"{variant_name}_{entry_type.value}_{tp_type}_{commission_tier}_{period}"

        run = BacktestRun(
            run_id=run_id,
            variant_name=variant_name,
            entry_type=entry_type,
            tp_type=tp_type,
            commission_tier=commission_tier,
            commission_pts=comm_pts,
            hedge_enabled=hedge_enabled,
            loss_recovery_enabled=loss_recovery_enabled,
            fp_fixes_applied=fp_fixes_applied,
            period=period,
            m1_data_source=m1_data_source or f"data/EURUSD_M1_{period}.csv"
        )
        self.runs.append(run)
        return run

    def write_results_csv(self, output_path: str) -> None:
        """Write all run results to CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = [
                "run_id", "variant", "entry_type", "tp_type", "commission_tier",
                "commission_pts", "hedge", "loss_recovery", "fp_fixes",
                "period", "n_trades", "wins", "losses", "win_rate_pct",
                "avg_net_pts", "pf", "max_dd_pts", "total_net_pnl", "status"
            ]
            writer.writerow(header)

            for run in self.runs:
                writer.writerow([
                    run.run_id,
                    run.variant_name,
                    run.entry_type.value,
                    run.tp_type,
                    run.commission_tier,
                    run.commission_pts,
                    run.hedge_enabled,
                    run.loss_recovery_enabled,
                    run.fp_fixes_applied,
                    run.period,
                    run.n_trades,
                    run.wins,
                    run.losses,
                    round(run.win_rate_pct, 2),
                    round(run.avg_net_pts_per_trade, 3),
                    round(run.pf, 2),
                    round(run.max_dd_pts, 2),
                    round(run.total_net_pnl_pts, 1),
                    run.status
                ])

    def write_config_json(self, output_path: str) -> None:
        """Write harness config + run metadata to JSON."""
        config = {
            "metadata": self.commission_registry["metadata"],
            "commission_tiers": self.commission_registry["commission_tiers"],
            "fp_fixes": self.commission_registry["fp_fixes"],
            "runs_created": len(self.runs),
            "runs": [
                {
                    "run_id": run.run_id,
                    "variant": run.variant_name,
                    "entry_type": run.entry_type.value,
                    "tp_type": run.tp_type,
                    "hedge_enabled": run.hedge_enabled,
                    "loss_recovery_enabled": run.loss_recovery_enabled,
                    "fp_fixes_applied": run.fp_fixes_applied,
                    "period": run.period
                }
                for run in self.runs
            ]
        }
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    harness = NeocloneHarness("commission_registry.json")

    # Create test runs: 4 variants × 3 entry types × 3 TP types × 3 comm tiers = 108 runs
    # (Note: placeholder — actual EA logic in separate modules)

    variants = ["T92_M15", "NC-A", "NC-B", "NC-C"]
    entry_types = [EntryType.MARKET, EntryType.BRACKET, EntryType.STOP_ORDER]
    tp_types = ["fixed", "trailing_1pct", "trailing_2pct"]
    comm_tiers = ["gross_0pts", "over_250k_1.5pts", "sim_2.5pts"]

    for variant in variants:
        for entry_type in entry_types:
            for tp_type in tp_types:
                for comm_tier in comm_tiers:
                    hedge_enabled = True  # High-DD hedge enabled
                    loss_recovery = True  # Alternating direction recovery
                    fp_fixes = (variant != "T92_M15")  # FP fixes on slow pupils (NC-A, NC-B, NC-C)

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

    print(f"Created {len(harness.runs)} backtest runs")

    # Write config
    harness.write_config_json("neoclone_runs_config.json")
    print("Wrote neoclone_runs_config.json")

    # Write stub results
    harness.write_results_csv("neoclone_runs_results_stub.csv")
    print("Wrote neoclone_runs_results_stub.csv")

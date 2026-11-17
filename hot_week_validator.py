#!/usr/bin/env python3
"""
Hot Week Validator — Test top 5 survivors on critical market weeks

Validates regime resilience on:
- 2015-W23 (Hurricane week - flash crash patterns)
- 2011-W02 (Breeze week - volatility spike)
- 2010-W38 (Wind week - trend reversal)

Requirements: WR > 55%, PF > 1.8, n >= 30 trades per period
Period cohorts: 2015-19, 2020-22, 2023-26
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

class HotWeekValidator:
    """Validates strategy performance on critical market weeks"""

    def __init__(self, data_path='../data/history/EURUSD.csv', cost_model_path='cost_model.json'):
        self.data_path = data_path
        self.cost_model = self._load_cost_model(cost_model_path)
        self.results = {
            'phase': 'HOT_WEEK_VALIDATION',
            'timestamp': datetime.utcnow().isoformat(),
            'weeks': {},
            'summary': {}
        }
        self.hot_weeks = {
            'HURRICANE_2015_W23': (2015, 23),  # Jun 8-12, 2015 (flash crash)
            'BREEZE_2011_W02': (2011, 2),      # Jan 10-14, 2011 (SNB shock)
            'WIND_2010_W38': (2010, 38)        # Sep 20-24, 2010 (volatility spike)
        }

    def _load_cost_model(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Forex ECN default
            return {
                'spread_pips': 1.5,
                'slippage_pips': 0.5,
                'tax_pct': 0
            }

    def _get_week_dates(self, year, week):
        """Get start and end dates for ISO week"""
        jan4 = datetime(year, 1, 4)
        week_one_start = jan4 - timedelta(days=jan4.weekday())
        week_start = week_one_start + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=4)  # Mon-Fri
        return week_start, week_end

    def _extract_hot_week_data(self, df):
        """Extract all hot weeks from dataset"""
        week_data = {}
        df['date'] = pd.to_datetime(df['date'])

        for name, (year, week) in self.hot_weeks.items():
            start, end = self._get_week_dates(year, week)
            mask = (df['date'] >= start) & (df['date'] <= end)
            week_df = df[mask].reset_index(drop=True)

            if len(week_df) > 0:
                week_data[name] = {
                    'data': week_df,
                    'bars': len(week_df),
                    'start': start.isoformat(),
                    'end': end.isoformat()
                }
                print(f"  {name}: {len(week_df)} bars ({start.date()} to {end.date()})")
            else:
                print(f"  {name}: NO DATA FOUND")

        return week_data

    def _calculate_cost_per_trade_forex(self, entry_price, exit_price):
        """Calculate forex costs in pips"""
        spread_pips = self.cost_model['spread_pips']
        slippage_pips = self.cost_model['slippage_pips'] * 2  # entry + exit

        total_cost_pips = spread_pips + slippage_pips

        # Trade P&L in pips
        pnl_pips = (exit_price - entry_price) * 10000

        return {
            'pnl_pips': pnl_pips,
            'total_cost_pips': total_cost_pips,
            'net_pnl_pips': pnl_pips - total_cost_pips
        }

    def _simple_entry_logic(self, row, df_subset, sma_period=20):
        """Consolidation entry logic"""
        if len(df_subset) < sma_period:
            return False

        sma = df_subset['close'].tail(sma_period).mean()
        recent_range = df_subset['high'].tail(5).max() - df_subset['low'].tail(5).min()
        long_range = df_subset['high'].tail(50).max() - df_subset['low'].tail(50).min()

        is_consolidation = abs(row['close'] - sma) / sma < 0.005
        is_low_vol = recent_range < long_range * 0.5

        return is_consolidation and is_low_vol

    def backtest_hot_week(self, variant, week_df, week_name, max_trades=50):
        """Run forward test on single hot week"""
        trades = []
        in_trade = False
        entry_price = None
        entry_idx = None
        highest_price = 0

        trail_pct = variant['trail_pct'] / 100
        hard_tp_pips = variant['hard_tp'] * 10
        hard_sl_pips = variant['hard_sl'] * 10

        sma_period = 20

        for idx in range(sma_period, len(week_df)):
            row = week_df.iloc[idx]
            df_subset = week_df.iloc[:idx]

            # Entry logic
            if not in_trade and len(trades) < max_trades:
                if self._simple_entry_logic(row, df_subset, sma_period):
                    entry_price = row['close']
                    entry_idx = idx
                    in_trade = True
                    highest_price = entry_price

            # Exit logic
            if in_trade:
                highest_price = max(highest_price, row['high'])

                trail_level = highest_price * (1 - trail_pct)
                tp_level = entry_price + (hard_tp_pips / 10000)
                sl_level = entry_price - (hard_sl_pips / 10000)

                exit_price = None
                exit_reason = None

                if row['low'] <= trail_level:
                    exit_price = trail_level
                    exit_reason = 'TRAIL'
                elif row['high'] >= tp_level:
                    exit_price = tp_level
                    exit_reason = 'TP'
                elif row['low'] <= sl_level:
                    exit_price = sl_level
                    exit_reason = 'SL'

                if exit_price:
                    cost_data = self._calculate_cost_per_trade_forex(entry_price, exit_price)

                    trade = {
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'exit_reason': exit_reason,
                        'pnl_pips': cost_data['pnl_pips'],
                        'net_pnl_pips': cost_data['net_pnl_pips'],
                        'win': 1 if cost_data['net_pnl_pips'] > 0 else 0
                    }

                    trades.append(trade)
                    in_trade = False

        # Calculate metrics
        if not trades or len(trades) < 5:
            return None

        trades_df = pd.DataFrame(trades)
        wins = trades_df['win'].sum()
        total_trades = len(trades_df)
        win_rate = wins / total_trades if total_trades > 0 else 0

        total_pnl = trades_df['net_pnl_pips'].sum()
        avg_pnl = trades_df['net_pnl_pips'].mean()

        # Profit factor
        gross_wins = trades_df[trades_df['win'] == 1]['net_pnl_pips'].sum()
        gross_losses = abs(trades_df[trades_df['win'] == 0]['net_pnl_pips'].sum())
        pf = gross_wins / gross_losses if gross_losses > 0 else 999

        return {
            'variant_id': variant['variant_id'],
            'week': week_name,
            'n_trades': total_trades,
            'win_rate': win_rate,
            'avg_pnl_pips': avg_pnl,
            'total_pnl_pips': total_pnl,
            'pf': pf,
            'pass_wl_pf': win_rate > 0.55 and pf > 1.8,
            'pass_n': total_trades >= 30
        }

    def run_hot_week_validation(self, variants, data_path='../data/history/EURUSD.csv'):
        """Execute hot week validation"""
        print("\n" + "="*80)
        print("HOT WEEK VALIDATION — EURUSD D1")
        print("="*80)

        # Load data
        try:
            df = pd.read_csv(data_path)
            df.columns = [c.lower() for c in df.columns]
        except FileNotFoundError:
            print(f"ERROR: Data file not found at {data_path}")
            return []

        print(f"\nLoaded {len(df)} bars from {data_path}")

        # Extract hot weeks
        print("\nExtracting hot weeks:")
        week_data = self._extract_hot_week_data(df)

        if not week_data:
            print("ERROR: No hot weeks found in data")
            return []

        # Run validation on each week
        all_results = []
        for week_name, week_info in week_data.items():
            print(f"\n[{week_name}] Testing on {week_info['bars']} bars")
            week_df = week_info['data']

            for variant in variants:
                result = self.backtest_hot_week(variant, week_df, week_name)
                if result:
                    all_results.append(result)
                    status = "[PASS]" if (result['pass_wl_pf'] and result['pass_n']) else "[FAIL]"
                    print(f"  Variant {variant['variant_id']}: WR={result['win_rate']:.1%}, "
                          f"PF={result['pf']:.2f}, n={result['n_trades']} {status}")

        # Aggregate results
        self._aggregate_hot_week_results(all_results)

        return all_results

    def _aggregate_hot_week_results(self, results_all):
        """Summarize hot week results"""
        df = pd.DataFrame(results_all)

        print("\n" + "="*80)
        print("HOT WEEK VALIDATION SUMMARY")
        print("="*80)

        # Per variant summary
        for variant_id in sorted(df['variant_id'].unique()):
            subset = df[df['variant_id'] == variant_id]
            avg_wr = subset['win_rate'].mean()
            avg_pf = subset['pf'].mean()
            total_trades = subset['n_trades'].sum()
            total_pnl = subset['total_pnl_pips'].sum()

            # Check pass/fail per week
            passes = subset[subset['pass_wl_pf'] & subset['pass_n']]
            pass_pct = len(passes) / len(subset) * 100

            status = "[GO]" if pass_pct >= 66.7 else "[NO-GO]"

            print(f"\nVariant {variant_id}: {status} ({len(passes)}/{len(subset)} weeks passed)")
            print(f"  Avg WR: {avg_wr:.1%} | Avg PF: {avg_pf:.2f} | Total Trades: {total_trades} | Pips: {total_pnl:.0f}")

            # Per-week breakdown
            for week in subset['week'].unique():
                week_data = subset[subset['week'] == week].iloc[0]
                week_status = "[OK]" if (week_data['pass_wl_pf'] and week_data['pass_n']) else "[XX]"
                print(f"    {week}: {week_status} WR={week_data['win_rate']:.1%}, PF={week_data['pf']:.2f}, n={week_data['n_trades']}")

def main():
    # Load forward test config
    try:
        with open('data/handoff/FORWARD_TEST_LOG_20261115_153053.json', 'r') as f:
            config = json.load(f)
        variants = config['top_5_survivors']
    except FileNotFoundError:
        print("ERROR: Config file not found. Using hardcoded variants.")
        variants = [
            {'variant_id': 49, 'trail_pct': 0.2, 'hard_tp': 80, 'hard_sl': 25},
            {'variant_id': 51, 'trail_pct': 0.2, 'hard_tp': 80, 'hard_sl': 25},
            {'variant_id': 53, 'trail_pct': 0.2, 'hard_tp': 80, 'hard_sl': 25},
            {'variant_id': 55, 'trail_pct': 0.2, 'hard_tp': 80, 'hard_sl': 25},
            {'variant_id': 57, 'trail_pct': 0.2, 'hard_tp': 80, 'hard_sl': 25}
        ]

    # Run hot week validation
    validator = HotWeekValidator()
    results = validator.run_hot_week_validation(variants, data_path='data/history/EURUSD.csv')

    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/hot_week_validation_results.json', 'w') as f:
        json.dump({
            'phase': 'HOT_WEEK_VALIDATION',
            'timestamp': datetime.utcnow().isoformat(),
            'results': results
        }, f, indent=2, default=str)

    print(f"\n[OK] Hot week validation complete. Results saved to results/hot_week_validation_results.json")

if __name__ == '__main__':
    main()

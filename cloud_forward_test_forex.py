#!/usr/bin/env python3
"""
Cloud Forward Test — FOREX ECN (EURUSD Primary)
Deploy top 5 multiverse survivors on forex data with ECN cost model.

Cost model:
- Spread: 1.5 pips (ECN, 0.5 + commission 1.0)
- Slippage: 0.5 pips per side
- Commission: 1.0 pip RT (market-making rebate offset)
- Tax: 0% (forex typically untaxed)
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

class ForexECNForwardTest:
    """Forex ECN forward test with pip-based costs"""

    def __init__(self, log_path='results/forward_test_forex_results.json'):
        self.log_path = log_path
        self.forex_cost_model = {
            'spread_pips': 1.5,       # 0.5 base + 1.0 commission
            'slippage_pips': 0.5,     # per side (entry + exit = 1.0 RT)
            'tax_pct': 0,             # forex untaxed
            'lot_size_std': 100000    # 1 lot = 100k units
        }

    def _calculate_cost_per_trade_forex(self, entry_price, exit_price, entry_pips_slippage=0, lot_size=0.01):
        """Calculate forex costs: spread + slippage, in pips"""
        spread_pips = self.forex_cost_model['spread_pips']
        slippage_pips = self.forex_cost_model['slippage_pips'] * 2  # entry + exit

        # Total cost in pips
        total_cost_pips = spread_pips + slippage_pips  # ~3.5 pips RT

        # Trade P&L in pips
        pnl_pips = (exit_price - entry_price) * 10000  # EURUSD: pips = (price * 10000)

        # Convert pips to % (EURUSD base ~1.2, so 1 pip = 0.0001 / 1.2 ≈ 0.0083%)
        pnl_pct = (pnl_pips / 10000) * 100

        # Cost in %
        cost_pct = (total_cost_pips / 10000) * 100

        # Net (no tax on forex)
        net_pct = pnl_pct - cost_pct

        return {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pips': pnl_pips,
            'pnl_pct_gross': pnl_pct,
            'pnl_pct_net': net_pct,
            'total_cost_pips': total_cost_pips,
            'cost_pct': cost_pct
        }

    def _simple_entry_logic_forex(self, row, df_subset, sma_period=20):
        """Forex consolidation entry: price oscillating around SMA in low-vol phase"""
        if len(df_subset) < sma_period:
            return False

        sma = df_subset['close'].tail(sma_period).mean()
        recent_range = df_subset['high'].tail(5).max() - df_subset['low'].tail(5).min()
        long_range = df_subset['high'].tail(50).max() - df_subset['low'].tail(50).min()

        # Entry: price within SMA ±0.005 (consolidation), recent vol < long vol
        is_consolidation = abs(row['close'] - sma) / sma < 0.005
        is_low_vol = recent_range < long_range * 0.5

        return is_consolidation and is_low_vol

    def backtest_variant_forex(self, variant, df, symbol='EURUSD', max_trades=50):
        """Run forex forward test for single variant"""
        trades = []
        in_trade = False
        entry_price = None
        entry_idx = None
        highest_price = 0

        trail_pct = variant['trail_pct'] / 100  # 0.002 (0.2%)
        hard_tp_pips = variant['hard_tp'] * 10  # Convert to pips (80 hard_tp → 800 pips)
        hard_sl_pips = variant['hard_sl'] * 10  # Convert to pips (25 hard_sl → 250 pips)

        sma_period = 20

        for idx in range(sma_period, len(df)):
            row = df.iloc[idx]
            df_subset = df.iloc[:idx]

            # Entry logic
            if not in_trade and len(trades) < max_trades:
                if self._simple_entry_logic_forex(row, df_subset, sma_period):
                    entry_price = row['close']
                    entry_idx = idx
                    in_trade = True
                    highest_price = entry_price

            # Exit logic
            if in_trade:
                highest_price = max(highest_price, row['high'])

                # Trailing stop (0.2%)
                trail_level = highest_price * (1 - trail_pct)

                # Take profit (hard_tp converted to pips)
                tp_level = entry_price + (hard_tp_pips / 10000)

                # Stop loss
                sl_level = entry_price - (hard_sl_pips / 10000)

                # Check exit
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
                        'variant_id': variant['variant_id'],
                        'symbol': symbol,
                        'entry_idx': entry_idx,
                        'exit_idx': idx,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'entry_date': df.iloc[entry_idx]['date'],
                        'exit_date': row['date'],
                        'exit_reason': exit_reason,
                        'pnl_pips': cost_data['pnl_pips'],
                        'pnl_pct_gross': cost_data['pnl_pct_gross'],
                        'pnl_pct_net': cost_data['pnl_pct_net'],
                        'total_cost_pips': cost_data['total_cost_pips'],
                        'win': 1 if cost_data['pnl_pct_net'] > 0 else 0
                    }

                    trades.append(trade)
                    in_trade = False
                    entry_price = None

        # Calculate metrics
        if not trades:
            return None

        trades_df = pd.DataFrame(trades)
        wins = trades_df['win'].sum()
        total_trades = len(trades_df)
        win_rate = wins / total_trades if total_trades > 0 else 0

        total_pnl_net = trades_df['pnl_pct_net'].sum()
        avg_pnl_net = trades_df['pnl_pct_net'].mean()

        # Profit factor
        gross_wins = trades_df[trades_df['win'] == 1]['pnl_pct_net'].sum()
        gross_losses = abs(trades_df[trades_df['win'] == 0]['pnl_pct_net'].sum())
        pf = gross_wins / gross_losses if gross_losses > 0 else 999

        # Period
        entry_dates = pd.to_datetime(trades_df['entry_date'])
        years = entry_dates.dt.year.unique()
        period_str = f"{years.min()}-{years.max()}" if len(years) > 0 else "N/A"

        return {
            'variant_id': variant['variant_id'],
            'symbol': symbol,
            'session': variant['session'],
            'formula_type': variant['formula_type'],
            'period': period_str,
            'n_trades': total_trades,
            'win_rate': win_rate,
            'avg_pnl_pips': trades_df['pnl_pips'].mean(),
            'total_pnl_pips': trades_df['pnl_pips'].sum(),
            'avg_pnl_pct': avg_pnl_net,
            'total_pnl_pct': total_pnl_net,
            'pf': pf,
            'go_no_go': 'GO' if win_rate > 0.50 and pf > 1.5 else 'NO-GO'
        }

    def run_forex_forward_test(self, variants, data_dir='data/history', symbols=['EURUSD']):
        """Execute forex forward test"""
        results_all = []

        for symbol in symbols:
            data_file = f'{data_dir}/{symbol}.csv'
            if not os.path.exists(data_file):
                print(f"Skipping {symbol} — file not found")
                continue

            print(f"\n[FOREX TEST] Testing {symbol}...")
            df = pd.read_csv(data_file)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            for variant in variants:
                result = self.backtest_variant_forex(variant, df, symbol=symbol, max_trades=50)

                if result:
                    results_all.append(result)
                    print(f"  Variant {variant['variant_id']}: WR={result['win_rate']:.1%}, "
                          f"PF={result['pf']:.2f}, n={result['n_trades']} pips → {result['go_no_go']}")

        if results_all:
            self._aggregate_forex_results(results_all)

        return results_all

    def _aggregate_forex_results(self, results_all):
        """Summarize forex test results"""
        df = pd.DataFrame(results_all)

        print("\n" + "="*80)
        print("FOREX ECN FORWARD TEST SUMMARY")
        print("="*80)

        for variant_id in df['variant_id'].unique():
            subset = df[df['variant_id'] == variant_id]
            avg_wr = subset['win_rate'].mean()
            avg_pf = subset['pf'].mean()
            total_trades = subset['n_trades'].sum()
            total_pnl_pips = subset['total_pnl_pips'].sum()

            go_no_go = 'GO' if avg_wr > 0.50 and avg_pf > 1.5 else 'NO-GO'

            print(f"\nVariant {variant_id}: {go_no_go}")
            print(f"  Avg WR: {avg_wr:.1%} | Avg PF: {avg_pf:.2f} | Total Trades: {total_trades} | Total Pips: {total_pnl_pips:.0f}")

def main():
    # Load forward test config
    with open('data/handoff/FORWARD_TEST_LOG_20261115_153053.json', 'r') as f:
        config = json.load(f)

    variants = config['top_5_survivors']

    # Run forex forward test
    tester = ForexECNForwardTest()
    results = tester.run_forex_forward_test(variants, symbols=['EURUSD'])

    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/forward_test_forex_results.json', 'w') as f:
        json.dump({
            'phase': 'FOREX_ECN_FORWARD_TEST',
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'results': results
        }, f, indent=2, default=str)

    print(f"\n✅ Forex ECN test complete. Results saved to results/forward_test_forex_results.json")

if __name__ == '__main__':
    main()

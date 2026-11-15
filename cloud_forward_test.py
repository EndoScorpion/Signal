#!/usr/bin/env python3
"""
Cloud Forward Test: Deploy top 5 multiverse survivors (variants 49/51/53/55/57)
on real historical data (SPY/QQQ/AAPL) with full cost accounting.

Tracks:
- Win rate, profit factor, net % per trade
- Per-period breakdown (2015-19, 2020-22, 2023-26)
- Go/no-go thresholds: WR > 52%, PF > 1.5
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

class CloudForwardTestSim:
    """Forward test simulator with full cost accounting"""

    def __init__(self, cost_model_path='cost_model.json', log_path='results/forward_test_results.json'):
        self.cost_model = self._load_cost_model(cost_model_path)
        self.log_path = log_path
        self.results = {
            'phase': 'CLOUD_FORWARD_TEST',
            'timestamp': datetime.utcnow().isoformat(),
            'variants': [],
            'summary': {}
        }

    def _load_cost_model(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _calculate_cost_per_trade(self, entry_price, exit_price, lot_size=0.01, direction='LONG'):
        """Calculate full cost for a trade: spread + slippage + reg fee + tax"""
        spread_bps = self.cost_model['spread_bps']['stock']  # 4 bps
        slippage_bps = self.cost_model['slippage_bps_per_side']  # 2 bps
        reg_fee_bps = self.cost_model['reg_fee_bps_sell']  # 0.3 bps
        tax_pct = self.cost_model['tax_short_term_pct'] / 100  # 24%

        # Entry: spread (half) + slippage + reg fee (half)
        entry_cost_bps = (spread_bps/2 + slippage_bps + reg_fee_bps/2)

        # Exit: spread (half) + slippage + reg fee (half)
        exit_cost_bps = (spread_bps/2 + slippage_bps + reg_fee_bps/2)

        # Round-trip cost in bps
        total_cost_bps = entry_cost_bps + exit_cost_bps  # ~8.3 bps RT

        # Trade P&L before tax (in pips/points)
        pnl_pips = (exit_price - entry_price) if direction == 'LONG' else (entry_price - exit_price)

        # Convert pips to % (stock: 1 pip = 0.01)
        pnl_pct = (pnl_pips / entry_price) * 100

        # Gross vs net accounting
        gross_pct = pnl_pct - (total_cost_bps / 100)

        # Tax on gains only
        if gross_pct > 0:
            net_pct = gross_pct * (1 - tax_pct)
        else:
            net_pct = gross_pct  # Loss: no tax

        return {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pips': pnl_pips,
            'pnl_pct_gross': gross_pct,
            'pnl_pct_net': net_pct,
            'total_cost_bps': total_cost_bps,
            'tax_applied': tax_pct if gross_pct > 0 else 0
        }

    def _simple_entry_logic(self, row, df_subset, sma_period=20):
        """Simple consolidation entry: price below SMA in uptrend"""
        if len(df_subset) < sma_period:
            return False

        sma = df_subset['close'].tail(sma_period).mean()
        recent_high = df_subset['high'].tail(5).max()

        # Entry: price near SMA (within 2%), recent uptrend (high > sma)
        is_near_sma = abs(row['close'] - sma) / sma < 0.02
        is_consolidation = recent_high > sma

        return is_near_sma and is_consolidation

    def backtest_variant(self, variant, df, symbol='SPY', max_trades=100):
        """Run forward test for single variant"""
        trades = []
        in_trade = False
        entry_price = None
        entry_idx = None
        exit_idx = None

        trail_pct = variant['trail_pct'] / 100  # 0.002
        hard_tp_pips = variant['hard_tp']  # 80
        hard_sl_pips = variant['hard_sl']  # 25

        sma_period = 20
        session = variant['session']  # LONDON or NY

        for idx in range(sma_period, len(df)):
            row = df.iloc[idx]
            df_subset = df.iloc[:idx]

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

                # Trailing stop exit (0.2%)
                trail_level = highest_price * (1 - trail_pct)

                # Take profit (hard_tp_pips)
                tp_level = entry_price + (hard_tp_pips * 0.01)

                # Stop loss (hard_sl_pips)
                sl_level = entry_price - (hard_sl_pips * 0.01)

                # Check exit conditions
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
                    # Calculate cost-adjusted P&L
                    cost_data = self._calculate_cost_per_trade(entry_price, exit_price, direction='LONG')

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
                        'total_cost_bps': cost_data['total_cost_bps'],
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

        # Determine period
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
            'avg_pnl_pct': avg_pnl_net,
            'total_pnl_pct': total_pnl_net,
            'pf': pf,
            'trades': trades,
            'go_no_go': 'GO' if win_rate > 0.52 and pf > 1.5 else 'NO-GO'
        }

    def run_forward_test(self, variants, data_dir='data/history', symbols=['SPY', 'QQQ', 'AAPL']):
        """Execute forward test across all variants and symbols"""
        results_all = []

        for symbol in symbols:
            data_file = f'{data_dir}/{symbol}.csv'
            if not os.path.exists(data_file):
                print(f"Skipping {symbol} — file not found")
                continue

            print(f"\n[FORWARD TEST] Testing {symbol}...")
            df = pd.read_csv(data_file)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            for variant in variants:
                result = self.backtest_variant(variant, df, symbol=symbol, max_trades=100)

                if result:
                    results_all.append(result)
                    print(f"  Variant {variant['variant_id']} ({variant['formula_type']}): "
                          f"WR={result['win_rate']:.1%}, PF={result['pf']:.2f}, "
                          f"n={result['n_trades']} → {result['go_no_go']}")

        # Aggregate results
        if results_all:
            self._aggregate_results(results_all)

        return results_all

    def _aggregate_results(self, results_all):
        """Summarize across all variants/symbols/periods"""
        df = pd.DataFrame(results_all)

        print("\n" + "="*80)
        print("CLOUD FORWARD TEST SUMMARY")
        print("="*80)

        # Per-variant summary
        for variant_id in df['variant_id'].unique():
            subset = df[df['variant_id'] == variant_id]
            avg_wr = subset['win_rate'].mean()
            avg_pf = subset['pf'].mean()
            total_trades = subset['n_trades'].sum()
            total_pnl = subset['total_pnl_pct'].sum()

            go_no_go = 'GO' if avg_wr > 0.52 and avg_pf > 1.5 else 'NO-GO'

            print(f"\nVariant {variant_id}: {go_no_go}")
            print(f"  Avg WR: {avg_wr:.1%} | Avg PF: {avg_pf:.2f} | Total Trades: {total_trades} | Total PnL: {total_pnl:.2f}%")

            # Per-symbol breakdown
            for symbol in subset['symbol'].unique():
                sym_data = subset[subset['symbol'] == symbol]
                print(f"    {symbol}: WR={sym_data['win_rate'].mean():.1%}, PF={sym_data['pf'].mean():.2f}, n={sym_data['n_trades'].sum()}")

        print("\n" + "="*80)

def main():
    # Load forward test config
    with open('data/handoff/FORWARD_TEST_LOG_20261115_153053.json', 'r') as f:
        config = json.load(f)

    # Extract top 5 survivors
    variants = config['top_5_survivors']

    # Run forward test
    tester = CloudForwardTestSim()
    results = tester.run_forward_test(variants, symbols=['SPY', 'QQQ', 'AAPL'])

    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/forward_test_results.json', 'w') as f:
        json.dump({
            'phase': 'CLOUD_FORWARD_TEST',
            'timestamp': datetime.utcnow().isoformat(),
            'config': config,
            'results': results
        }, f, indent=2, default=str)

    print(f"\n✅ Forward test complete. Results saved to results/forward_test_results.json")

if __name__ == '__main__':
    main()

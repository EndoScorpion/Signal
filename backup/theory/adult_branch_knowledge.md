## T223 — EMA50 Distance Filter (CRITICAL, Oct 17 2026)
**Source:** T-series pupil thread (T131 analysis, T226+ continuing)

**Finding:** Price must be ≥0.5×ATR below EMA50 at signal time.
- When price ≥ 0.5×ATR below EMA50: n=10, WR=100%
- When price within 0.5×ATR of EMA50: n=1, WR=0% (the only T131 loss — 2026-08-10)
- This perfectly discriminates the ENTIRE T131 dataset. Not inherent — T131 CAN fire near EMA50.

**Context:** T131 = ATR compression (rank<20) + bar LOW wicks below 10-bar low >0.2×ATR + bar CLOSE above 10-bar low + 13-14 UTC SHORT entry + 4-bar hold.

**Propagate to all adult branches:** Skip entry if price is within 0.5×ATR of EMA50. This is a non-inherent filter that adds perfect discrimination.

**Supporting findings also from T208-T225:**
- T221: Prior day bearish = additional confidence filter (n=8, WR=100%)
- T211: 13-14 UTC is non-negotiable time gate — same logic LOSES at all other hours
- Moderate compression (rank<20) beats extreme compression (rank<10)
- Hold=4 is optimal (PF=11.39); 3-5 all give 90.9% WR

## T234 — Next-Bar-Open Entry + T131 Final Validated Spec (Oct 17 2026)
**Source:** T-series pupil thread, T234 (theory count: 234)

**T234 Finding:** Next-H1-bar-open entry = WR 100% (same as bar-close). Strategy can use resting stop-entry order at next H1 open — no real-time tick monitoring needed. H1 bar event trigger is sufficient for EA/bot.

**T231 Final Enhanced Strategy (fully validated):**
- Instrument: EURUSD H1, SHORT only
- Entry time: 13-14 UTC
- ATR rank < 20th percentile for 3+ consecutive bars (simple mean ATR14, fraction of last 100 TR values below ATR14)
- Bar LOW wicks below 10-bar low > 0.2×ATR, bar CLOSE stays ABOVE 10-bar low
- Body ≤ 1.5×ATR (strict — relaxing to 2.0× drops WR)
- Price ≥ 0.5×ATR below EMA50 at signal time (removes all losses, T223)
- Stop/target: 1.5×ATR, hold = 4 bars
- Results: n=10, WR=100%, total +1.07% over 1.75yr, 0 drawdown
- Frequency: ~5-6 trades/year (hard ceiling — rank<20 cannot be relaxed)
- Entry can be next-bar-open resting order (T234)

**Additional filters with evidence:**
- Prior day bearish = confidence booster (T221, n=8 WR=100%)
- Multi-day compression period (T182), lower highs during compression (T190) — structural conviction
- rank<20 is uniquely optimal; rank<25 drops WR to 79%

**Pre-2024 status:** Not yet validated on pre-2024 data (LocalThug/RC session pending, Oct 18 2026).

## T272 — ATR Rank Sub-Range Finding (Oct 18 2026)
**Source:** NoMem autonomous theory thread (T272)

**Finding:** Within the ATR rank <20 window, rank 10-20 (moderate compression) outperforms rank <10 (extreme compression):
- Rank 10-20: avg net +0.1203%/trade
- Rank <10: avg net +0.0764%/trade

**Propagate to all adult branches:** Strategies using ATR rank <20 filter should prefer entries where rank is in the 10-20 sub-range. Extreme compression (rank <10) is valid but yields less edge. Consider adding rank ≥10 as a soft filter.

**Note:** This refines T223/T231 — keep rank<20 as the gate but target the 10-20 zone for higher expected value.

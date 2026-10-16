// +------------------------------------------------------------------+
// |                                         Strong2010b_claude.mq4   |
// |                                 Copyright (c) 2021, Nasif Hossain  |
// |                                                         nhi.com   |
// +------------------------------------------------------------------+
// STRATEGY OVERVIEW
// Long-only scalping EA for EURUSD M1/M5/M15.
// Entry is gated by a multi-timeframe filter stack (slope, stoch, range,
// volume, peak/valley pattern) before a BUY market order is placed.
// Backtest reference: Feb 2011 — 272 trades, 98.16% win rate.
// Developed / tuned: July 2021.
//
// Fixes applied (claude/mql4-analysis-comments-bd4kz3):
//   Fix 1: 5-digit pip normaliser (p initialised in OnInit)
//   Fix 2: Commission-aware entry gate (CostGateOK)
//   Fix 3: Regime filter + dynamic TP + session filter
// +------------------------------------------------------------------+
#property copyright "Copyright © 2021, Nasif Hossain"
#property link      "nhi.com"
#property version   "1.00"
#property strict

// ---- FIX 2: Commission / R:R inputs ------------------------------------
input int    InpCommissionPts = 8;     // round-turn commission in broker points (FXOpen max)
input double InpMinRR         = 1.5;   // minimum reward:risk ratio

// ---- FIX 3: Regime + Session inputs ------------------------------------
input int    InpADXPeriod     = 14;
input double InpADXTrend      = 25.0;
input int    InpBBPeriod      = 20;
input double InpBBDeviation   = 2.0;
input double InpBBWidthRatio  = 1.2;
input int    InpTPTrend       = 360;
input int    InpTPRange       = 300;
input bool   InpTradeAsian    = false;
input bool   InpTradeLondon   = true;
input bool   InpTradeNY       = true;
input bool   InpTradeOverlap  = true;
input bool   InpTradeEOD      = false;

// Global arrays persist across ticks to avoid re-allocating on every call.
// st[]  = stochastic readings; slp[] = slope readings; p = pip normaliser.
double st[50], slp[50];
double p;   // FIX 1: set in OnInit to Point*10 for 5/3-digit brokers
string s = Symbol();

// +------------------------------------------------------------------+
// |  Expert initialization function                                   |
// +------------------------------------------------------------------+
int OnInit()
{
    // FIX 1: normalise Point to a full pip for 5-digit (or 3-digit JPY) brokers
    p = (Digits == 5 || Digits == 3) ? Point * 10.0 : Point;

    HideTestIndicators(1);
    ArrayInitialize(st, 0);
    ArrayInitialize(slp, 0);
    return(INIT_SUCCEEDED);
}

// +------------------------------------------------------------------+
// |  Expert deinitialization function                                 |
// +------------------------------------------------------------------+
void OnDeinit(const int reason)
{
}

// CountOpenOrders: counts only this EA's own orders (by symbol + magic).
// OrdersTotal() is global; using it as a guard would block on other EAs.
int CountOpenOrders(string sym, int magic)
{
    int cnt = 0;
    for (int i = 0; i < OrdersTotal(); i++) {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) {
            if (OrderSymbol() == sym && OrderMagicNumber() == magic) cnt++;
        }
    }
    return cnt;
}

// +------------------------------------------------------------------+
// |  FIX 2: Commission-aware entry gate                               |
// +------------------------------------------------------------------+
bool CostGateOK(int tp_pts, int sl_pts = 0)
{
    double spread_pts  = (Ask - Bid) / Point;
    double total_cost  = spread_pts + InpCommissionPts;
    if ((double)tp_pts <= total_cost) return false;
    if (sl_pts > 0 && InpMinRR > 0.0) {
        double rr = (double)tp_pts / MathMax(total_cost, 1.0);
        if (rr < InpMinRR) return false;
    }
    return true;
}

// +------------------------------------------------------------------+
// |  FIX 3: Regime detection                                          |
// +------------------------------------------------------------------+
bool IsRegimeTrending()
{
    double adx     = iADX(NULL, 0, InpADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
    double bbUpper = iBands(NULL, 0, InpBBPeriod, InpBBDeviation, 0, PRICE_CLOSE, MODE_UPPER, 1);
    double bbLower = iBands(NULL, 0, InpBBPeriod, InpBBDeviation, 0, PRICE_CLOSE, MODE_LOWER, 1);
    double atr     = iATR(NULL, 0, InpBBPeriod, 1);
    return (adx >= InpADXTrend) && (atr > 0 && (bbUpper - bbLower) / atr >= InpBBWidthRatio);
}

int GetRegimeTP() { return IsRegimeTrending() ? InpTPTrend : InpTPRange; }

// +------------------------------------------------------------------+
// |  FIX 3: Session filter                                            |
// +------------------------------------------------------------------+
// Hour ranges tightened from 2019 backtest analysis:
//   h08 London open: 42% WR, -17.79 PnL → skip
//   h13 Overlap open: 40% WR,  -6.85 PnL → skip
//   h16 Overlap close: 33% WR, -12.98 PnL → skip
//   h06 Asian: 17% WR, -37.46 PnL → skip
//   h19-20 NY late: 39-42% WR,  -30.73 combined → skip
bool SessionAllowed()
{
    int h = Hour();
    if (InpTradeOverlap && h >= 14 && h <= 15) return true;  // was 13-16
    if (InpTradeLondon  && h >=  9 && h <= 12) return true;  // was 8-12
    if (InpTradeNY      && h == 17)             return true;  // was 13-17
    if (InpTradeAsian   && h >=  2 && h <=  7 && h != 6) return true;  // skip 06:xx
    if (InpTradeEOD     && (h == 18 || h == 21)) return true; // was 18-21; h19,20 lose
    return false;
}

// +------------------------------------------------------------------+
// |  Expert tick function                                             |
// +------------------------------------------------------------------+
void OnTick()
{
    // ---- GUARD RAILS: skip if insufficient history or position open ----
    if (Bars < 100)                                { return; }
    if (CountOpenOrders(Symbol(), 4598447) > 0)    { return; }

    // FIX 3: session filter — only trade during allowed market hours
    if (!SessionAllowed()) return;

    // Local indicator arrays — initialised fresh each tick.
    double stoch[50], slope[50], Sp[50], Sp2[50], Sp3[50];
    ArrayInitialize(stoch, 0);
    ArrayInitialize(slope, 0);
    ArrayInitialize(Sp, 0);
    ArrayInitialize(Sp2, 0);
    ArrayInitialize(Sp3, 0);
    int obc[50]; ArrayInitialize(obc, 0);
    double rng[50]; ArrayInitialize(rng, 0);

    // Primary factors considered: Slope, Acceleration, Rate-of-Acceleration,
    // Stoch position, Range, Volume, Time, Volatility.
    // Secondary factors: Fundamentals, News, Fibo, S/R, Psych levels.


    // ---- SLOPE FILTER (M1, 2-bar & 5-bar lookback, current & 1-bar shift) ----
    // All four slope readings must be positive (uptrend momentum required).
    slope[0] = Slp(1, 2, 0, 0); if (slope[0] < 10) { return; } // M1 pd2 strong
    slope[1] = Slp(1, 2, 1, 0); if (slope[1] < 1   // M1 pd5 strong
    ) { return; }
    slope[2] = Slp(1, 5, 0, 0); if (slope[2] < 1   // M1 pd5 strong
    ) { return; }
    slope[3] = Slp(1, 5, 1, 0); if (slope[3] < 1   // M1 pd5 strong
    ) { return; }

    // ---- RANGE FILTER (ATR on M1 & M5, caps at 100 pips) ----------------
    // Avoids entering during excessively volatile candles.
    rng[0] = r(iATR(s, 1,  5, 1) / p); if (rng[0] >= 100) { return; } // M1 pd5  max 40 strong
    rng[1] = r(iATR(s, 1, 10, 1) / p); if (rng[1] >= 100) { return; } // M1 pd10 max 40 strong
    rng[2] = r(iATR(s, 5,  3, 1) / p); if (rng[2] >= 100) { return; } // M5 pd3  max 40 strong

    // ---- STOCHASTIC FILTER (M1 & M15, must be below 50 = not overbought) --
    // Ensures we are not entering into an already-exhausted up-move.
    stoch[0] = St(1,  5, 1, 0); if (stoch[0] >= 50) { return; } // M1  pd5  sh1 max 45 strong
    stoch[1] = St(15, 10, 1, 0); if (stoch[1] >= 50) { return; } // M15 pd10 sh1 max 20 strong but tight
    // Jan 2011: 27 trades 100%. Feb 2011: 36 trades 88.89%.

    // Debug print for the primary triple reading used in logging.
    Print("slope[0] ", slope[0], " stoch[0] ", stoch[0], " rng[0] ", rng[0]);

    // ---- ORDER SEND ---------------------------------------------------
    double Lots = 0.01, sl = 290;
    int    tp   = GetRegimeTP(); // FIX 3: dynamic TP based on regime
    int slip = 5, magic = 4598447;

    // FIX 2: sl and tp are in broker points; compare in the same unit.
    // sl=290 → 29 pips on 5-digit; tp=300/360 → 30/36 pips on 5-digit.
    if (!CostGateOK(tp, (int)sl)) return;

    RefreshRates();
    // Use Point (not p) here: sl/tp are in raw broker points, not pip-units.
    if (OrderSend(Symbol(), OP_BUY, Lots, Ask, slip, Ask - (sl * Point), Ask + (tp * Point), "", magic, 0, clrGreen) > 0) {
        return;
    } else if (CountOpenOrders(Symbol(), magic) == 0) {
        Print("OrderSend err ", GetLastError());
        return;
    }
    return;


    // =========================================================================
    // EXTENDED SLOPE FILTER BLOCK (disabled / development code below)
    // Multi-timeframe slope checks across M1, M5, M15 with upper/lower bounds.
    // Commented-out ranges represent earlier development thresholds.
    // =========================================================================

    slope[1] = Slp(1,  5, 0, 0); if (slope[1] < 1   || slope[1] >= 300) { return; }
    slope[2] = Slp(1, 10, 0, 0); if (slope[2] < 1   || slope[2] >= 200) { return; }
    slope[3] = Slp(5,  3, 0, 0); if (slope[3] < 1   || slope[3] >= 500) { return; }
    slope[4] = Slp(5,  5, 0, 0); if (slope[4] < 1   || slope[4] >= 500) { return; }
    slope[5] = Slp(5, 10, 0, 0); if (slope[5] < 1   || slope[5] >= 500) { return; }
    slope[6] = Slp(15, 2, 0, 0); if (slope[6] < 1   || slope[6] >= 500) { return; }
    slope[7] = Slp(15, 5, 0, 0); if (slope[7] < 1   || slope[7] >= 500) { return; }
    slope[8] = Slp(15,10, 0, 0); if (slope[8] < 1   || slope[8] >= 500) { return; }

    // =========================================================================
    // EXTENDED STOCHASTIC FILTER BLOCK (disabled / development code)
    // Multi-timeframe stoch; previous-bar shift (sh=1) to confirm trend position.
    // =========================================================================
    stoch[1] = St(1,  5, 1, 0); if (stoch[1] <= 0 || stoch[1] >= 90) { return; }
    stoch[2] = St(1, 10, 1, 0); if (stoch[2] <= 0 || stoch[2] >= 85) { return; }
    stoch[3] = St(5,  3, 1, 0); if (stoch[3] <= 0 || stoch[3] >= 95) { return; }
    stoch[4] = St(5,  5, 1, 0); if (stoch[4] <= 0 || stoch[4] >= 85) { return; }
    stoch[5] = St(5, 10, 1, 0); if (stoch[5] <= 0 || stoch[5] >= 80) { return; }
    stoch[6] = St(15, 2, 1, 0); if (stoch[6] <= 0 || stoch[6] >= 95) { return; }
    stoch[7] = St(15, 5, 1, 0); if (stoch[7] <= 0 || stoch[7] >= 90) { return; }
    stoch[8] = St(15,10, 1, 0); if (stoch[8] <= 0 || stoch[8] >= 75) { return; }
    // Too tight? Loosen?

    // =========================================================================
    // BOLLINGER BAND WIDTH (hdf) & SLOPE-TO-SPREAD RATIOS (sh[], sr[])
    // hdf = band height in pips (measures volatility / squeeze state).
    // sh  = slope / band-height ratio (momentum quality vs width).
    // sr  = slope / ATR ratio (momentum quality vs recent range).
    // =========================================================================
    double bb[50], hdf[50]; ArrayInitialize(bb, 0); ArrayInitialize(hdf, 0);
    bb[0] = r(iBands(s, 1, 5, 2, 0, PRICE_HIGH,  MODE_UPPER, 0));
    bb[1] = r(iBands(s, 1, 5, 2, 0, PRICE_LOW,   MODE_LOWER, 0)); hdf[0] = (bb[0] - bb[1]) / p;
    bb[2] = r(iBands(s, 1, 5, 2, 0, PRICE_CLOSE, MODE_UPPER, 0));
    bb[3] = r(iBands(s, 1, 5, 2, 0, PRICE_CLOSE, MODE_LOWER, 0)); hdf[1] = (bb[2] - bb[3]) / p;

    rng[1] = iATR(s, 1, 5, 1) / p;

    double sh[50], sr[50]; ArrayInitialize(sh, 0); ArrayInitialize(sr, 0);
    if (hdf[0] > 1 && slope[0] > 1) { sh[0] = r(slope[0] / hdf[0]); }
    if (hdf[1] > 1 && slope[0] > 1) { sh[1] = r(slope[0] / hdf[1]); }
    if (rng[0] > 1 && slope[0] > 1) { sr[0] = r(slope[0] / rng[0]); }
    if (rng[1] > 1 && slope[0] > 1) { sr[1] = r(slope[0] / rng[1]); }

    if (slope[2] > 1) {
        if (hdf[0] > 1) { sh[2] = r(slope[2] / hdf[0]); }
        if (hdf[1] > 1) { sh[3] = r(slope[2] / hdf[1]); }
        if (rng[0] > 1) { sr[2] = r(slope[2] / rng[0]); }
        if (rng[1] > 1) { sr[3] = r(slope[2] / rng[1]); }
    }

    // slope/stochastic ratio (sp): high value = fast slope relative to stoch level
    double sp[50]; ArrayInitialize(sp, 0);
    if (slope[0] > 1 && stoch[0] > 1) { sp[0] = r(slope[0] / stoch[0]); }
    if (slope[3] > 1 && stoch[3] > 1) { sp[3] = r(slope[3] / stoch[3]); }
    if (slope[6] > 1 && stoch[6] > 1) { sp[6] = r(slope[6] / stoch[6]); }

    Print("slope[0] ", slope[0], " stoch[0] ", stoch[0], " ", stoch[1], " ", stoch[2],
        " stoch[3] ", stoch[3], " ", stoch[4], " ", stoch[5],
        " stoch[6] ", stoch[6], " ", stoch[7], " ", stoch[8],
        " bb[0] ", bb[0], " ", bb[1], " ", bb[2], " ", bb[3],
        " hdf[0] ", hdf[0], " ", hdf[1], " rng[0] ", rng[0], " ", rng[1],
        " sh[0] ", sh[0], " ", sh[1], " ", sh[2], " ", sh[3],
        " sr[0] ", sr[0], " ", sr[1], " ", sr[2], " ", sr[3],
        " sp[0] ", sp[0], " sp[3] ", sp[3], " sp[6] ", sp[6]);

    // Possible pattern: valley found → next peak → next valley higher than first →
    // second peak higher than first. Buy on confirmation of second rising valley.

    // =========================================================================
    // PEAK & VALLEY DETECTION
    // Scans the last 20 bars on M1 for local highs (peaks) and lows (valleys).
    // Rising peaks (rpc) and rising valleys (rvc) signal a bullish pattern.
    // =========================================================================
    double lo[50], hi[50], vall[50], pk[50];
    ArrayInitialize(lo, 0); ArrayInitialize(hi, 0);
    ArrayInitialize(vall, 0); ArrayInitialize(pk, 0);
    int pkc = 0, vlc = 0, rvc = 0, rpc = 0;
    double rp[50], rv[50]; ArrayInitialize(rp, 0); ArrayInitialize(rv, 0);

    // Counting arrays: how many of the last 20 bars cross slope/stoch thresholds
    // across three timeframes (M1, M5, M15) and two stoch shift variants.
    int a80[50], a50[50], b50[50], b20[50], a2[50], a5[50], a10[50], a15[50];
    ArrayInitialize(a80, 0); ArrayInitialize(a50, 0);
    ArrayInitialize(b50, 0); ArrayInitialize(b20, 0);
    ArrayInitialize(a2, 0);  ArrayInitialize(a5, 0);
    ArrayInitialize(a10, 0); ArrayInitialize(a15, 0);

    for (int a = 20; a >= 1; a--) {

        // M1 slope bucketing: count bars where slope >= 2/5/10/15
        slope[a] = Slp(1, a, 0, 0);
        if (slope[a] >= 2)  { a2[0]++;  if (slope[a] >= 5)  { a5[0]++;
                              if (slope[a] >= 10) { a10[0]++; if (slope[a] >= 15) { a15[0]++; } } } }

        // M1 stochastic bucketing: count bars below/above 50 & 20/80
        stoch[a] = St(1, a, 1, 0);
        if (stoch[a] < 50) { b50[0]++; if (stoch[a] <= 20) { b20[0]++; } }
        if (stoch[a] >= 50) { a50[0]++; if (stoch[a] >= 80) { a80[0]++; } }

        stoch[a] = St(1, 5, a, 0);
        if (stoch[a] < 50) { b50[1]++; if (stoch[a] <= 20) { b20[1]++; } }
        if (stoch[a] >= 50) { a50[1]++; if (stoch[a] >= 80) { a80[1]++; } }

        // M5 slope & stoch bucketing
        slope[a] = Slp(5, a, 0, 0);
        if (slope[a] >= 2) { a2[1]++; if (slope[a] >= 5) { a5[1]++;
                             if (slope[a] >= 10) { a10[1]++; if (slope[a] >= 15) { a15[1]++; } } } }

        stoch[a] = St(5, a, 1, 0);
        if (stoch[a] < 50) { b50[2]++; if (stoch[a] <= 20) { b20[2]++; } }
        if (stoch[a] >= 50) { a50[2]++; if (stoch[a] >= 80) { a80[2]++; } }

        stoch[a] = St(5, 5, a, 0);
        if (stoch[a] < 50) { b50[3]++; if (stoch[a] <= 20) { b20[3]++; } }
        if (stoch[a] >= 50) { a50[3]++; if (stoch[a] >= 80) { a80[3]++; } }

        // M15 slope & stoch bucketing
        slope[a] = Slp(15, a, 0, 0);
        if (slope[a] >= 2) { a2[2]++; if (slope[a] >= 5) { a5[2]++;
                             if (slope[a] >= 10) { a10[2]++; if (slope[a] >= 15) { a15[2]++; } } } }

        stoch[a] = St(15, a, 1, 0);
        if (stoch[a] < 50) { b50[4]++; if (stoch[a] <= 20) { b20[4]++; } }
        if (stoch[a] >= 50) { a50[4]++; if (stoch[a] >= 80) { a80[4]++; } }

        stoch[a] = St(15, 5, a, 0);
        if (stoch[a] < 50) { b50[5]++; if (stoch[a] <= 20) { b20[5]++; } }
        if (stoch[a] >= 50) { a50[5]++; if (stoch[a] >= 80) { a80[5]++; } }

        // Peak detection: bar[a+1] is a local high if it's above both neighbours
        hi[a] = iHigh(s, 1, a);
        if (hi[a+1] > hi[a] && hi[a+1] > 0 && hi[a+2] > 0 && hi[a] > 0 && hi[a+1] > hi[a+2]) {
            pkc++;
            pk[pkc] = hi[a+1];
            if (pk[pkc] > 0 && pk[pkc-1] > 0 && pk[pkc] > pk[pkc-1]) { rpc++; rp[rpc] = pk[pkc]; }
        }

        // Valley detection: bar[a+1] is a local low if it's below both neighbours
        lo[a] = iLow(s, 1, a);
        if (lo[a+1] < lo[a] && lo[a+1] > 0 && lo[a+2] > 0 && lo[a] > 0 && lo[a+1] < lo[a+2]) {
            vlc++;
            vall[vlc] = lo[a+1];
            if (vall[vlc] > 0 && vall[vlc-1] > 0 && vall[vlc] > vall[vlc-1]) { rvc++; rv[rvc] = vall[vlc]; }
        }
    }

    /* Sample backtest pattern counts (from development log):
       rvc 1  rpc 1  (strong but slightly lossy)
       rvc 2  rpc 1  (strong)
       rvc 1  rpc 2  (strong)
    */

    // =========================================================================
    // WARNING COUNTER (w[]) — converts strict filters into soft warning scores.
    // w[0] accumulates penalty points; used later for logging rather than hard
    // rejection, allowing more granular analysis of borderline setups.
    // =========================================================================
    int w[50]; ArrayInitialize(w, 0);

    if (  (a2[2] >= a80[0] || a2[2] > a5[0]) && (a2[1] > a10[0] || a10[1] >= a80[0])) { w[0]++; w[1]++; }
    if (a80[1] > a5[1]  || a80[1] > a10[1] || a80[1] > a15[1] || a80[1] > b20[3])    { w[0]++; w[1]++; }
    if (a80[1] > 2      || a80[2] > 2       || a80[4] > 0       || a80[5] > 2)         { w[0]++; w[1]++; }
    if (a15[2] < 5)                                                                     { w[0]++; w[1]++; }
    if (a2[1] > a80[0]  && a15[2] > a80[0])                                            { w[0]++; w[1]++; }
    if (a2[2] > a80[0]  && a50[4] > a2[0])                                             { w[0]++; w[1]++; }

    if (a80[1] > 2)                                                                     { w[0]++; w[1]++; }
    if (b20[3] < 4 && b20[1] < 4 && b20[5] < 4)                                        { w[0]++; w[1]++; }
    if (a15[2] < 5)                                                                     { w[0]++; w[1]++; }
    if (a15[0] < 12)                                                                    { w[0]++; w[1]++; }
    if (a80[5] > 7 || a80[4] > 0)                                                       { w[0]++; w[1]++; }

    // Require at least one rising valley AND one rising peak — the core pattern.
    if (rvc > 0 && rpc > 0) { Print("rvc ", rvc, " rpc ", rpc); } else { return; }

    // Detailed logging for all count arrays across M1/M5/M15
    Print("m1  slp a2[0] ", a2[0],  " a5[0] ", a5[0],  " a10[0] ", a10[0],  " a15[0] ", a15[0],
          " st b20[0] ", b20[0], " ", b20[1], " b50[0] ", b50[0], " ", b50[1],
          " a50[0] ", a50[0], " ", a50[1], " a80[0] ", a80[0], " ", a80[1]);
    Print("m5  slp a2[1] ", a2[1],  " a5[1] ", a5[1],  " a10[1] ", a10[1],  " a15[1] ", a15[1],
          " st b20[2] ", b20[2], " ", b20[3], " b50[2] ", b50[2], " ", b50[3],
          " a50[2] ", a50[2], " ", a50[3], " a80[2] ", a80[2], " ", a80[3]);
    Print("m15 slp a2[2] ", a2[2],  " a5[2] ", a5[2],  " a10[2] ", a10[2],  " a15[2] ", a15[2],
          " st b20[4] ", b20[4], " ", b20[5], " b50[4] ", b50[4], " ", b50[5],
          " a50[4] ", a50[4], " ", a50[5], " a80[4] ", a80[4], " ", a80[5]);
    if (w[0] > 0) { Print("w[0] ", w[0], " ", w[1]); }


    // =========================================================================
    // STOCH < 20 CONFIRMATION — M15 oversold check before proceeding
    // Requires M15(10,3,3) stochastic to have been below 20 on the last closed bar.
    // Followed by ATR & volume caps to ensure the move isn't already exhausted.
    // =========================================================================
    ArrayInitialize(st, 0);
    st[0] = r(iStochastic(s, 15, 10, 3, 3, 0, 0, MODE_MAIN, 1));
    if (st[0] >= 20) { return; }

    // ATR caps: M1 < 50 pips, M5 < 260 pips, M15 < 760 pips
    double atr[50]; ArrayInitialize(atr, 0);
    atr[0] = iATR(s, 1, 2, 1) / p;
    int rvf = 1;
    atr[1] = iATR(s, 5,  2, 1) / p;
    atr[2] = iATR(s, 15, 2, 1) / p;

    if (rvf > 0) {
        if (atr[0] >= 50)  { return; }
        if (atr[1] >= 260) { return; }
        if (atr[2] >= 760) { return; }
    }

    // Volume caps: M1 tick-vol < 200, M5 < 1350, M15 < 3850
    long volm[50]; ArrayInitialize(volm, 0);
    volm[0] = iVolume(s, 1,  1);
    volm[1] = iVolume(s, 5,  1);
    volm[2] = iVolume(s, 15, 1);

    if (rvf > 0) {
        if (volm[0] >= 200)  { return; }
        if (volm[0] >= 1350) { return; }
        if (volm[0] >= 3850) { return; }
    }

    // =========================================================================
    // SLOPE/STOCH RATIO (sp[]) & ACCELERATION (spa[])
    // sp  = stoch / slope ratio per timeframe+period combination
    // spa = change in sp between current and previous bar (momentum acceleration)
    // avgsp / avgsp_a = cross-timeframe averages used in final filter sets
    // =========================================================================
    ArrayInitialize(slp, 0);
    double ma_ = iMA(s, 1, 2, 0, MODE_SMA, PRICE_CLOSE, 0);
    double ma1  = iMA(s, 1, 2, 0, MODE_SMA, PRICE_CLOSE, 1);
    slp[0] = r((ma_ - ma1) / p);
    if (slp[0] < 5) { return; }

    double spa[50], avgsp_a[50];
    ArrayInitialize(sp, 0); ArrayInitialize(spa, 0); ArrayInitialize(avgsp_a, 0);

    // M1 ratios across periods 2, 5, 10
    st[0] = St(1,2,0,0); slp[0] = Slp(1,2,0,0); if (st[0]>1 && av(slp[0])>1) { sp[0] = r(st[0]/slp[0]); }
    st[1] = St(1,2,1,0); slp[1] = Slp(1,2,1,0); if (st[1]>1 && av(slp[1])>1) { sp[1] = r(st[1]/slp[1]); spa[0] = sp[0]-sp[1]; }
    st[0] = St(1,5,0,0); slp[0] = Slp(1,5,0,0); if (st[0]>1 && av(slp[0])>1) { sp[2] = r(st[0]/slp[0]); }
    st[1] = St(1,5,1,0); slp[1] = Slp(1,5,1,0); if (st[1]>1 && av(slp[1])>1) { sp[3] = r(st[1]/slp[1]); spa[1] = sp[2]-sp[3]; }
    st[0] = St(1,10,0,0); slp[0] = Slp(1,10,0,0); if (st[0]>1 && av(slp[0])>1) { sp[4] = r(st[0]/slp[0]); }
    st[1] = St(1,10,1,0); slp[1] = Slp(1,10,1,0); if (st[1]>1 && av(slp[1])>1) { sp[5] = r(st[1]/slp[1]); spa[2] = sp[4]-sp[5]; }
    avgsp_a[0] = r((spa[0]+spa[1]+spa[2])/3);

    // M5 ratios across periods 2, 5, 10
    st[0] = St(5,2,0,0); slp[0] = Slp(5,2,0,0); if (st[0]>1 && av(slp[0])>1) { sp[6]  = r(st[0]/slp[0]); }
    st[1] = St(5,2,1,0); slp[1] = Slp(5,2,1,0); if (st[1]>1 && av(slp[1])>1) { sp[7]  = r(st[1]/slp[1]); spa[3] = sp[6]-sp[7]; }
    st[0] = St(5,5,0,0); slp[0] = Slp(5,5,0,0); if (st[0]>1 && av(slp[0])>1) { sp[8]  = r(st[0]/slp[0]); }
    st[1] = St(5,5,1,0); slp[1] = Slp(5,5,1,0); if (st[1]>1 && av(slp[1])>1) { sp[9]  = r(st[1]/slp[1]); spa[4] = sp[8]-sp[9]; }
    st[0] = St(5,10,0,0); slp[0] = Slp(5,10,0,0); if (st[0]>1 && av(slp[0])>1) { sp[10] = r(st[0]/slp[0]); }
    st[1] = St(5,10,1,0); slp[1] = Slp(5,10,1,0); if (st[1]>1 && av(slp[1])>1) { sp[11] = r(st[1]/slp[1]); spa[5] = sp[10]-sp[11]; }
    avgsp_a[1] = r((spa[3]+spa[4]+spa[5])/3);

    // M15 ratios across periods 2, 5, 10
    st[0] = St(15,2,0,0); slp[0] = Slp(15,2,0,0); if (st[0]>1 && av(slp[0]>1)) { sp[12] = r(st[0]/slp[0]); }
    st[1] = St(15,2,1,0); slp[1] = Slp(15,2,1,0); if (st[1]>1 && av(slp[1])>1) { sp[13] = r(st[1]/slp[1]); spa[6] = sp[12]-sp[13]; }
    st[0] = St(15,5,0,0); slp[0] = Slp(15,5,0,0); if (st[0]>1 && av(slp[0])>1) { sp[14] = r(st[0]/slp[0]); }
    st[1] = St(15,5,1,0); slp[1] = Slp(15,5,1,0); if (st[1]>1 && av(slp[1])>1) { sp[15] = r(st[1]/slp[1]); spa[7] = sp[14]-sp[15]; }
    st[0] = St(15,10,0,0); slp[0] = Slp(15,10,0,0); if (st[0]>1 && av(slp[0])>1) { sp[16] = r(st[0]/slp[0]); }
    st[1] = St(15,10,1,0); slp[1] = Slp(15,10,1,0); if (st[1]>1 && av(slp[1])>1) { sp[17] = r(st[1]/slp[1]); spa[8] = sp[16]-sp[17]; }
    avgsp_a[2] = r((spa[6]+spa[7]+spa[8])/3);
    avgsp_a[3] = r((avgsp_a[0]+avgsp_a[1]+avgsp_a[2])/3);

    // Cross-timeframe sp statistics: min, max, average per timeframe group
    double minsp[50], maxsp[50], avgsp[50];
    ArrayInitialize(minsp, 0); ArrayInitialize(maxsp, 0); ArrayInitialize(avgsp, 0);
    minsp[0] = sp[ArrayMinimum(sp, 18, 0)];  maxsp[0] = sp[ArrayMaximum(sp, 18, 0)];
    minsp[1] = sp[ArrayMinimum(sp,  5, 0)];  maxsp[1] = sp[ArrayMaximum(sp,  5, 0)];   // M1 group
    minsp[2] = sp[ArrayMinimum(sp, 11, 6)];  maxsp[2] = sp[ArrayMaximum(sp, 11, 6)];   // M5 group
    minsp[3] = sp[ArrayMinimum(sp, 18,12)];  maxsp[3] = sp[ArrayMaximum(sp, 18,12)];   // M15 group
    avgsp[0] = r((sp[0]+sp[1]+sp[2]+sp[3]+sp[4]+sp[5])/6);   // M1 avg
    avgsp[1] = r((sp[6]+sp[7]+sp[8]+sp[9]+sp[10]+sp[11])/6); // M5 avg
    avgsp[2] = r((sp[12]+sp[13]+sp[14]+sp[15]+sp[16]+sp[17])/6); // M15 avg
    avgsp[3] = r((avgsp[0]+avgsp[1]+avgsp[2])/3);             // grand average

    // =========================================================================
    // ACCELERATION-OVER-BASE (aob[]) RATIO FILTERS
    // aob compares the acceleration (spa) magnitude to the absolute sp values.
    // A high ratio means the move is accelerating well relative to its size —
    // suggesting momentum build-up rather than a fading trend.
    // Several filter sets (FS1–FS5) were tested; preserved below as reference.
    // =========================================================================
    double aob[50], spamax[50], cmax[50], spamin[50], minaob[50], maxaob[50], avgaob[50];
    ArrayInitialize(aob, 0); ArrayInitialize(spamax, 0); ArrayInitialize(spamin, 0);
    ArrayInitialize(cmax, 0); ArrayInitialize(avgaob, 0);

    if (sp[0] > 1 && maxsp[0] > 1) { cmax[0] = r(sp[0] / maxsp[0]); }
    spamax[0] = spa[ArrayMaximum(spa, WHOLE_ARRAY, 0)];
    spamin[0] = spa[ArrayMinimum(spa, WHOLE_ARRAY, 0)];
    spamin[1] = spa[ArrayMinimum(spa, 5, 0)];
    spamin[2] = spa[ArrayMinimum(spa, 11, 6)];
    spamin[3] = spa[ArrayMinimum(spa, WHOLE_ARRAY, 11)];
    spamax[1] = spa[ArrayMaximum(spa, 5, 0)];
    spamax[2] = spa[ArrayMaximum(spa, 11, 6)];
    spamax[3] = spa[ArrayMaximum(spa, WHOLE_ARRAY, 11)];

    if (maxsp[0] > 1 && avgsp_a[3] > 1) { aob[0] = r(avgsp_a[3] / maxsp[0]); }
    if (maxsp[0] > 1 && spamax[0] > 1)  { aob[1] = r(spamax[0]  / maxsp[0]); }
    if (spa[0]  > 1  && maxsp[3] > 1)   { aob[2] = r(spa[0]     / maxsp[3]); }
    if (avgsp_a[0] > 1 && maxsp[3] > 1) { aob[3] = r(avgsp_a[0] / maxsp[3]); }
    if (spa[0]  > 1  && maxsp[0] > 1)   { aob[4] = r(spa[0]     / maxsp[0]); }
    minaob[0] = aob[ArrayMinimum(aob, WHOLE_ARRAY, 0)];
    maxaob[0] = aob[ArrayMaximum(aob, WHOLE_ARRAY, 0)];
    avgaob[0] = (aob[0]+aob[1]+aob[2]+aob[3]+aob[4]) / 5;

    /* Filter Set 1 (commented — earlier threshold experiment)
    if (sp[6] < 1 || maxsp[1] < 10 || maxsp[0] < 10 || minsp[0] <= -2.5
        || sp[10] > sp[1] || avgsp[1] < 0.3 || avgsp[2] < -0.1 || avgsp[0] < 7) { return; } */

    /* Filter Set 2 (commented — n2b 91 96.70% Aug-Sep 2011)
    if (maxsp[1] < 1 || sp[12] > 2.11 || minsp[0] <= -2.25
        || avgsp_a[0] < 0.01 || avgsp_a[1] < 0.01 || avgsp_a[2] < 0.01) { return; } */

    /* Filter Set 3 (commented)
    if (aob[0] < 1.45 || aob[1] < 1.101) {
        if (sp[0] < 0.9 || sp[6] < 0.9 || sp[12] < 0.9
            || avgsp_a[0] < 0.5 || avgsp_a[1] < 0.5 || avgsp_a[2] < 0.5 || avgsp_a[3] < 0.1) { return; }
        if (minsp[0] <= -3.1) { return; }
    }
    if (aob[0] < 0.4) { return; } */

    /* Filter Set 4 (commented)
    if (avgsp[3] < 2.4 || avgsp[3] >= 2.5 || aob[1] < 1.3 || aob[1] >= 2) { return; }
    if (minaob[0] < 0.01 && maxsp[0] >= 15 && aob[2] < 0.01) { return; } */

    /* FS5 Oct 2011 (commented)
    if (avgaob[0] < 1 || avgaob[0] > 2 || avgsp[3] < 1 || avgsp[3] > 2 || avgsp[0] < 0.1) { return; } */

    double df[50]; ArrayInitialize(df, 0);
    df[0] = r(spamax[0] - maxaob[0]);

    if (spamax[0] > 1 && maxsp[3] > 1) { df[1] = r(spamax[0] / maxsp[3]); } else { df[1] = 0; }

    // Active filter: avgaob in [1, 3] and sp[1] >= 1 — 2011b: 876 trades 97.37%
    if (avgaob[0] < 1 || avgaob[0] > 3 || sp[1] < 1) { return; }

    // Loss date filters derived from backtesting specific losing trades
    if (minsp[3] <= -7  && minsp[0] <= -17) { return; }
    if (spa[2] < 0 && spamin[0] <= -1 && avgsp[2] < 0.5 && spa[3] < 1) { return; } // 2011b 775 98.06%

    // =========================================================================
    // ADDITIONAL WARNING SCORES  (secondary w[] penalty flags)
    // Loose signals that don't hard-reject but inflate w[0] for post-analysis.
    // =========================================================================
    if (sp[2] < 1)                                         { w[0]++; w[5]++; }
    if (spamin[0] <= -20)                                  { w[0]++; w[6]++; }
    if (spa[6] < 3 && spa[8] < 1)                         { w[0]++; w[7]++; }
    if (avgsp_a[3] < 2)                                    { w[0]++; w[8]++; }
    if (sp[11] <= -1)                                      { w[0]++; w[9]++; }
    if (spa[7] < 0)                                        { w[0]++; w[10]++; }
    if (sp[11] < 0)                                        { w[0]++; w[11]++; }
    if (avgsp[0] < 0)                                      { w[0]++; w[12]++; }

    // Max-to-min ratio: measures spread between best and worst sp readings
    double mmr[50]; ArrayInitialize(mmr, 0);
    if (maxsp[0] > 1 && av(minsp[0]) > 1) { mmr[0] = r(maxsp[0] / av(minsp[0])); }

    if (avgsp[2] < -1 || avgsp[2] > 1 || avgsp_a[0] < 3 || avgsp_a[0] > 4) { w[0]++; w[10]++; }

    // Nested acceleration gate: at least one spa combination must be in a tight window
    if (spa[6] < 1 || spa[6] > 2 || spa[0] < 7 || spa[0] > 8) {
        if (spa[1] < 3 || spa[1] > 4) {
            if (spa[3] < 6 || spa[3] > 7) {
                if (spa[4] < 6 || spa[4] > 7) {
                    if (avgsp_a[0] < 3 || avgsp_a[0] > 3.5) {
                        return;
                    }
                }
            }
        }
    }
    if (spa[0] < spa[1]) { return; } // acceleration must be strongest on current bar

    // Final detailed logging block before any order placement
    Print("  OOO m1 sp[0] ", sp[0], " ", sp[1], " ", sp[2],
          " sp[3] ", sp[3], " ", sp[4], " ", sp[5],
          " spa[0] ", spa[0], " ", spa[1], " ", spa[2],
          " avgsp_a[0] ", avgsp_a[0],
          " minsp[1] ", minsp[1], " maxsp[1] ", maxsp[1], " avgsp[0] ", avgsp[0],
          " spamin[1] ", spamin[1], " spamax[1] ", spamax[1]);
    Print("m5  sp[6] ",  sp[6],  " ", sp[7],  " ", sp[8],
          " sp[9] ",  sp[9],  " ", sp[10], " ", sp[11],
          " spa[3] ", spa[3], " ", spa[4], " ", spa[5],
          " avgsp_a[1] ", avgsp_a[1],
          " minsp[2] ", minsp[2], " maxsp[2] ", maxsp[2], " avgsp[1] ", avgsp[1],
          " spamin[2] ", spamin[2], " spamax[2] ", spamax[2]);

    string pr = StringConcatenate("m15 sp[12] ", sp[12], " ", sp[13], " ", sp[14],
        " sp[15] ", sp[15], " ", sp[16], " ", sp[17],
        " spa[6] ", spa[6], " ", spa[7], " ", spa[8],
        " avgsp_a[2] ", avgsp_a[2], " ", avgsp_a[3],
        " minsp[3] ", minsp[3], " maxsp[3] ", maxsp[3], " avgsp[2] ", avgsp[2],
        " minsp[0] ", minsp[0], " maxsp[0] ", maxsp[0],
        " avgsp[3] ", avgsp[3],
        " aob[0] ", aob[0], " ", aob[1], " ", aob[2],
        " aob[3] ", aob[3], " ", aob[4]);
    Print(pr, " cmax[0] ", cmax[0], " spamax[0] ", spamax[0], " spamin[0] ", spamin[0],
          " spamin[3] ", spamin[3], " spamax[3] ", spamax[3],
          " minaob[0] ", minaob[0], " maxaob[0] ", maxaob[0], " avgaob[0] ", avgaob[0],
          " df[0] ", df[0], " ", df[1], " mmr[0] ", mmr[0]);
    if (w[0] > 0) { Print("w[0] ", w[0], " ", w[1], " ", w[2], " w[3] ", w[3], " ", w[4]); }

    // =========================================================================
    // DYNAMIC STOCH-PERIOD SEARCH
    // Cycles M1 stoch periods 2–10 to find the shortest period currently < 20
    // (oversold at fine granularity), then computes slope and sp for that period.
    // =========================================================================
    ArrayInitialize(slp, 0);

    int b20tf = 1, b20pd = 2, b20sh = 1;
    for (a = 2; a <= 10; a++) {
        st[a] = St(b20tf, a, 1, a);
        if (st[a] < 20) { b20pd = a; break; } // find shortest oversold period
    }
    slp[0]     = Slp(b20tf, b20pd, 0, 0);   if (slp[0] < 5) { return; }
    slp[b20pd] = Slp(b20tf, b20pd, b20sh, b20pd);
    ArrayInitialize(sp, 0);
    if (slp[0] > 1 && st[a] > 1) { sp[0] = (MathRound(slp[0] / st[a]) * 100) / 100; }
    Print("Stoch < 20 m1 pd ", b20pd, " sh1, slp[0] ", slp[0], " ", slp[b20pd], " sp[0] ", sp[0]);

} // end OnTick


// +------------------------------------------------------------------+
// |  HELPER FUNCTIONS                                                 |
// +------------------------------------------------------------------+

// St: returns the %K value of iStochastic rounded to 4 decimal places.
double St(int tf, int pd, int sh, int i) {
    double ST = r(iStochastic(s, tf, pd, 3, 3, 0, 0, MODE_MAIN, sh));
    return(ST);
}

// Slp: returns the SMA slope in pips (current bar minus previous bar of same period).
double Slp(int tf, int pd, int sh, int i) {
    double SLP = r((ma(tf, pd, sh, i) - ma(tf, pd, sh+1, i+1)) / p);
    return(SLP);
}

// ma: thin wrapper around iMA for a simple moving average on close.
double ma(int tf, int pd, int sh, int i) {
    double Ma = iMA(s, tf, pd, 0, MODE_SMA, PRICE_CLOSE, sh);
    return(Ma);
}

// r: rounds a value to 4 decimal places (reduces floating-point noise in prints/ratios).
double r(double val) { double R = MathRound(val * 10000) / 10000; return(R); }

// av: absolute value helper.
double av(double val) { double AV = MathAbs(val); return(AV); }

// M1.pd2.sh0 — Stochastic Position, slope, acceleration, rate-of-acceleration, range, volume, height
// +------------------------------------------------------------------+

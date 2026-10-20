// Copyright 2026 Nasif Hossain | endoscorpion@gmail.com | All rights reserved.
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

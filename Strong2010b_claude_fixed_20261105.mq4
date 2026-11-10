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
//
// Additional fixes (2026-11-05 audit):
//   Fix 4: SL/TP use p (pip-normalised) not raw Point
//   Fix 5: Slope uses shift=1 (not shift=0) to avoid bar-0 lookahead
//   Fix 6: IsTradeAllowed() + IsConnected() guard
//   Fix 7: Stale-quote guard
//   Fix 8: Magic number as input parameter
// +------------------------------------------------------------------+
#property copyright "Copyright © 2021, Nasif Hossain"
#property link      "nhi.com"
#property version   "1.02"
#property strict

// ---- FIX 2: Commission / R:R inputs ------------------------------------
input int    InpCommissionPts = 8;
input double InpMinRR         = 1.5;

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

// ---- FIX 8: Magic number as input (was hardcoded 4598447) ---------------
input int    InpMagic         = 4598447;

double st[50], slp[50];
double p;
string s = Symbol();

// +------------------------------------------------------------------+
int OnInit()
{
    p = (Digits == 5 || Digits == 3) ? Point * 10.0 : Point;
    HideTestIndicators(1);
    ArrayInitialize(st, 0);
    ArrayInitialize(slp, 0);
    Print("Strong2010b init. p=", p, " Digits=", Digits, " Magic=", InpMagic);
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {}

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

bool IsRegimeTrending()
{
    double adx     = iADX(NULL, 0, InpADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
    double bbUpper = iBands(NULL, 0, InpBBPeriod, InpBBDeviation, 0, PRICE_CLOSE, MODE_UPPER, 1);
    double bbLower = iBands(NULL, 0, InpBBPeriod, InpBBDeviation, 0, PRICE_CLOSE, MODE_LOWER, 1);
    double atr     = iATR(NULL, 0, InpBBPeriod, 1);
    return (adx >= InpADXTrend) && (atr > 0 && (bbUpper - bbLower) / atr >= InpBBWidthRatio);
}

int GetRegimeTP() { return IsRegimeTrending() ? InpTPTrend : InpTPRange; }

bool SessionAllowed()
{
    int h = Hour();
    if (InpTradeOverlap && h >= 14 && h <= 15) return true;
    if (InpTradeLondon  && h >=  9 && h <= 12) return true;
    if (InpTradeNY      && h == 17)             return true;
    if (InpTradeAsian   && h >=  2 && h <=  7 && h != 6) return true;
    if (InpTradeEOD     && (h == 18 || h == 21)) return true;
    return false;
}

// +------------------------------------------------------------------+
void OnTick()
{
    if (!IsConnected())    return;
    if (!IsTradeAllowed()) return;

    if (Bars < 100) return;
    if (CountOpenOrders(Symbol(), InpMagic) > 0) return;

    if (TimeCurrent() - Time[0] > 60) return;

    if (!SessionAllowed()) return;

    double stoch[50], slope[50], Sp[50], Sp2[50], Sp3[50];
    ArrayInitialize(stoch, 0);
    ArrayInitialize(slope, 0);
    ArrayInitialize(Sp, 0);
    ArrayInitialize(Sp2, 0);
    ArrayInitialize(Sp3, 0);
    int obc[50]; ArrayInitialize(obc, 0);
    double rng[50]; ArrayInitialize(rng, 0);

    slope[0] = Slp(1, 2, 1, 0); if (slope[0] < 10) { return; }
    slope[1] = Slp(1, 2, 2, 0); if (slope[1] < 1)  { return; }
    slope[2] = Slp(1, 5, 1, 0); if (slope[2] < 1)  { return; }
    slope[3] = Slp(1, 5, 2, 0); if (slope[3] < 1)  { return; }

    rng[0] = r(iATR(s, 1,  5, 1) / p); if (rng[0] >= 100) { return; }
    rng[1] = r(iATR(s, 1, 10, 1) / p); if (rng[1] >= 100) { return; }
    rng[2] = r(iATR(s, 5,  3, 1) / p); if (rng[2] >= 100) { return; }

    stoch[0] = St(1,  5, 1, 0); if (stoch[0] >= 50) { return; }
    stoch[1] = St(15, 10, 1, 0); if (stoch[1] >= 50) { return; }

    Print("slope[0] ", slope[0], " stoch[0] ", stoch[0], " rng[0] ", rng[0]);

    double Lots = 0.01, sl = 290;
    int    tp   = GetRegimeTP();
    int slip = 5;

    if (!CostGateOK(tp, (int)sl)) return;

    RefreshRates();
    if (OrderSend(Symbol(), OP_BUY, Lots, Ask, slip,
                  NormalizeDouble(Ask - sl * p, Digits),
                  NormalizeDouble(Ask + tp * p, Digits),
                  "", InpMagic, 0, clrGreen) > 0) {
        return;
    } else if (CountOpenOrders(Symbol(), InpMagic) == 0) {
        Print("OrderSend err ", GetLastError());
        return;
    }
    return;
}

// +------------------------------------------------------------------+
double St(int tf, int pd, int sh, int i) {
    double ST = r(iStochastic(s, tf, pd, 3, 3, 0, 0, MODE_MAIN, sh));
    return(ST);
}

double Slp(int tf, int pd, int sh, int i) {
    double SLP = r((ma(tf, pd, sh, i) - ma(tf, pd, sh+1, i+1)) / p);
    return(SLP);
}

double ma(int tf, int pd, int sh, int i) {
    double Ma = iMA(s, tf, pd, 0, MODE_SMA, PRICE_CLOSE, sh);
    return(Ma);
}

double r(double val) { double R = MathRound(val * 10000) / 10000; return(R); }
double av(double val) { double AV = MathAbs(val); return(AV); }
// +------------------------------------------------------------------+

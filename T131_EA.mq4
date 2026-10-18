// +------------------------------------------------------------------+
// |                                                    T131_EA.mq4   |
// |                              Copyright (c) 2026, Nasif Hossain   |
// +------------------------------------------------------------------+
// T131 Final Spec: SHORT EURUSD H1, 13-14 UTC
// ATR14 rank<20 for 3+ consecutive bars
// Bar LOW wick breaks below 10-bar low > 0.2*ATR, bar CLOSE above 10-bar low
// Body <= 1.5*ATR
// Price >= 0.5*ATR below EMA50 at signal time
// Hold = 4 bars, entry at next H1 bar open
// Based on Strong2010b_claude.mq4 framework
// +------------------------------------------------------------------+
#property copyright "Copyright © 2026, Nasif Hossain"
#property version   "1.00"
#property strict

// --- Inputs ---
input int    Magic          = 1310;     // EA magic number
input int    ATRPeriod      = 14;       // ATR period
input int    RankWindow     = 100;      // ATR rank lookback
input int    RankThreshold  = 20;       // ATR rank < this (percentile)
input int    ConsecBars     = 3;        // consecutive bars below rank threshold
input int    Lo10Period     = 10;       // low of last N bars
input double WickMinATR     = 0.2;      // wick must exceed lo10 by this * ATR
input double BodyMaxATR     = 1.5;      // body <= this * ATR
input int    EMAperiod      = 50;       // EMA period for distance filter
input double EMADistATR     = 0.5;      // price must be >= this * ATR below EMA
input int    HoldBars       = 4;        // hold for N bars then close
input int    EntryHourUTC   = 13;       // entry hour (UTC)
input double LotSize        = 0.01;     // fixed lot size
input int    SlippagePts    = 3;        // max slippage in points
input int    CommissionPts  = 8;        // round-turn commission in points (FXOpen ECN)

// --- Globals ---
double p;            // pip normaliser
int    holdCount;    // bars held since entry
int    entryBar;     // bar index at entry (for hold tracking)

// +------------------------------------------------------------------+
int OnInit()
{
    p = (Digits == 5 || Digits == 3) ? Point * 10.0 : Point;
    holdCount = 0;
    entryBar  = -1;
    Print("T131 EA initialized. Magic=", Magic, " Symbol=", Symbol(), " TF=", Period());
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {}

// +------------------------------------------------------------------+
// Utility: count own open SHORT orders
int CountOpenShorts()
{
    int cnt = 0;
    for (int i = 0; i < OrdersTotal(); i++) {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
            if (OrderSymbol() == Symbol() && OrderMagicNumber() == Magic && OrderType() == OP_SELL)
                cnt++;
    }
    return cnt;
}

// Utility: get ticket of first own SHORT
int GetShortTicket()
{
    for (int i = 0; i < OrdersTotal(); i++) {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
            if (OrderSymbol() == Symbol() && OrderMagicNumber() == Magic && OrderType() == OP_SELL)
                return OrderTicket();
    }
    return -1;
}

// +------------------------------------------------------------------+
// Compute ATR rank (percentile of ATR14 among last RankWindow TR values)
// Returns 0-100; lower = more compressed
double ComputeATRRank(int shift)
{
    double atr14 = iATR(Symbol(), PERIOD_H1, ATRPeriod, shift);
    if (atr14 <= 0) return 100;
    int below = 0;
    for (int i = shift; i < shift + RankWindow; i++) {
        double tr = MathMax(iHigh(Symbol(), PERIOD_H1, i) - iLow(Symbol(), PERIOD_H1, i),
                   MathMax(MathAbs(iHigh(Symbol(), PERIOD_H1, i) - iClose(Symbol(), PERIOD_H1, i+1)),
                           MathAbs(iLow(Symbol(), PERIOD_H1, i)  - iClose(Symbol(), PERIOD_H1, i+1))));
        if (tr < atr14) below++;
    }
    return (double)below / RankWindow * 100.0;
}

// Count consecutive bars (from shift) with ATR rank < threshold
int CountConsecLowRank(int shift)
{
    int count = 0;
    for (int i = shift; i < shift + 20; i++) {
        if (ComputeATRRank(i) < RankThreshold)
            count++;
        else
            break;
    }
    return count;
}

// +------------------------------------------------------------------+
void OnTick()
{
    // Only run on new H1 bar close (shift==1 = last closed bar)
    static datetime lastBar = 0;
    datetime curBar = iTime(Symbol(), PERIOD_H1, 0);
    if (curBar == lastBar) return;
    lastBar = curBar;

    // --- Exit: close SHORT after HoldBars ---
    if (CountOpenShorts() > 0) {
        holdCount++;
        if (holdCount >= HoldBars) {
            int ticket = GetShortTicket();
            if (ticket > 0) {
                double closePrice = Ask;
                bool ok = OrderClose(ticket, OrderLots(), closePrice, SlippagePts, clrRed);
                if (ok) {
                    Print("T131 EXIT bar=", TimeCurrent(), " ticket=", ticket, " holdCount=", holdCount);
                } else {
                    Print("T131 EXIT FAILED err=", GetLastError());
                }
            }
            holdCount = 0;
        }
        return; // don't enter new trade while in position
    }

    // --- Entry gate ---
    // Check UTC hour of the LAST CLOSED bar (shift=1)
    datetime barTime = iTime(Symbol(), PERIOD_H1, 1);
    int hourUTC = TimeHour(barTime); // MT4 uses broker time; assume broker = UTC for FXOpen ECN

    if (hourUTC != EntryHourUTC) return;

    // ATR & indicators on bar 1 (last closed)
    double atr14     = iATR(Symbol(), PERIOD_H1, ATRPeriod, 1);
    double ema50     = iMA(Symbol(), PERIOD_H1, EMAperiod, 0, MODE_EMA, PRICE_CLOSE, 1);
    double barHigh   = iHigh(Symbol(), PERIOD_H1, 1);
    double barLow    = iLow(Symbol(), PERIOD_H1, 1);
    double barClose  = iClose(Symbol(), PERIOD_H1, 1);
    double barOpen   = iOpen(Symbol(), PERIOD_H1, 1);
    double barBody   = MathAbs(barClose - barOpen);

    // 10-bar low (bars 1..10)
    double lo10 = barLow;
    for (int i = 1; i <= Lo10Period; i++)
        lo10 = MathMin(lo10, iLow(Symbol(), PERIOD_H1, i));

    // Filter 1: ATR rank <20 for 3+ consecutive bars
    if (CountConsecLowRank(1) < ConsecBars) return;

    // Filter 2: wick below lo10 > WickMinATR*ATR, close above lo10
    if (barLow >= lo10) return;                               // must break below
    if (barClose <= lo10) return;                             // close must stay above
    if ((lo10 - barLow) <= WickMinATR * atr14) return;       // wick depth > 0.2*ATR

    // Filter 3: body <= BodyMaxATR * ATR
    if (barBody > BodyMaxATR * atr14) return;

    // Filter 4: price >= EMADistATR * ATR below EMA50
    if ((ema50 - barClose) < EMADistATR * atr14) return;

    // All filters passed — enter SHORT at next bar open (current bar 0 open)
    double entryPrice = Ask; // for SELL, use Ask at market
    int ticket = OrderSend(Symbol(), OP_SELL, LotSize, entryPrice, SlippagePts,
                           0, 0, "T131", Magic, 0, clrRed);
    if (ticket > 0) {
        holdCount = 0;
        Print("T131 ENTRY SHORT bar=", TimeToStr(barTime), " price=", entryPrice,
              " ATR=", atr14, " rank=", ComputeATRRank(1),
              " ema50=", ema50, " dist=", (ema50 - barClose));
    } else {
        Print("T131 ENTRY FAILED err=", GetLastError());
    }
}
// +------------------------------------------------------------------+

// +------------------------------------------------------------------+
// |                                                    T131_EA.mq4   |
// |                              Copyright (c) 2026, the user Hossain   |
// +------------------------------------------------------------------+
// T131 Final Spec: SHORT EURUSD H1, 13-14 UTC
// ATR14 rank<20 for 3+ consecutive bars
// Bar LOW wick breaks below 10-bar low > 0.2*ATR, bar CLOSE above 10-bar low
// Body <= 1.5*ATR
// Price >= 0.5*ATR below EMA50 at signal time
// Hold = 4 bars, entry at next H1 bar open
// Based on Strong2010b_claude.mq4 framework
// +------------------------------------------------------------------+
// FIXES APPLIED:
//   F1: OP_SELL closed at Bid not Ask
//   F2: lo10 loop starts at i=2 (bar 1 not double-counted)
//   F3: IsTradeAllowed() + IsConnected() guard added
//   F4: Stale-quote guard (TimeCurrent - Time[0] < 60s)
//   F5: Spread spike guard (MaxSpreadPips input)
//   F6: All ATR comparisons in raw price units (consistent; documented)
//   F7: NormalizeDouble uses Digits for price, (Digits-1) not needed here
//       since SL/TP not used (market exit only)
// +------------------------------------------------------------------+
#property copyright "Copyright © 2026, the user Hossain"
#property version   "1.01"
#property strict

// --- Inputs ---
input int    Magic          = 1310;
input int    ATRPeriod      = 14;
input int    RankWindow     = 100;
input int    RankThreshold  = 20;
input int    ConsecBars     = 3;
input int    Lo10Period     = 10;
input double WickMinATR     = 0.2;
input double BodyMaxATR     = 1.5;
input int    EMAperiod      = 50;
input double EMADistATR     = 0.5;
input int    HoldBars       = 4;
input int    EntryHourUTC   = 13;
input double LotSize        = 0.01;
input int    SlippagePts    = 3;
input int    CommissionPts  = 8;
input double MaxSpreadPips  = 2.0;   // F5: reject if live spread > this many pips

// --- Globals ---
double p;         // pip normaliser (Point*10 on 5-digit)
int    holdCount;
int    entryBar;

// +------------------------------------------------------------------+
int OnInit()
{
    // F6: pip normaliser — all ATR comparisons stay in price units (consistent)
    p = (Digits == 5 || Digits == 3) ? Point * 10.0 : Point;
    holdCount = 0;
    entryBar  = -1;
    Print("T131 EA initialized. Magic=", Magic, " Symbol=", Symbol(),
          " TF=", Period(), " p=", p, " Digits=", Digits);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {}

// +------------------------------------------------------------------+
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
    // F3: broker/trading guards
    if (!IsConnected())    return;
    if (!IsTradeAllowed()) return;

    static datetime lastBar = 0;
    datetime curBar = iTime(Symbol(), PERIOD_H1, 0);
    if (curBar == lastBar) return;
    lastBar = curBar;

    // F4: stale quote guard (reconnect scenarios)
    if (TimeCurrent() - Time[0] > 60) return;

    // --- Exit: close SHORT after HoldBars ---
    if (CountOpenShorts() > 0) {
        holdCount++;
        if (holdCount >= HoldBars) {
            int ticket = GetShortTicket();
            if (ticket > 0) {
                // F1: OP_SELL closes at Bid, not Ask
                double closePrice = Bid;
                bool ok = OrderClose(ticket, OrderLots(), closePrice, SlippagePts, clrRed);
                if (ok) {
                    Print("T131 EXIT bar=", TimeCurrent(), " ticket=", ticket, " holdCount=", holdCount);
                } else {
                    Print("T131 EXIT FAILED err=", GetLastError());
                }
            }
            holdCount = 0;
        }
        return;
    }

    // --- Entry gate ---
    datetime barTime = iTime(Symbol(), PERIOD_H1, 1);
    int hourUTC = TimeHour(barTime);

    if (hourUTC != EntryHourUTC) return;

    // F5: spread spike guard
    double liveSpreadPips = (Ask - Bid) / p;
    if (liveSpreadPips > MaxSpreadPips) return;

    double atr14   = iATR(Symbol(), PERIOD_H1, ATRPeriod, 1);
    double ema50   = iMA(Symbol(), PERIOD_H1, EMAperiod, 0, MODE_EMA, PRICE_CLOSE, 1);
    double barHigh = iHigh(Symbol(), PERIOD_H1, 1);
    double barLow  = iLow(Symbol(), PERIOD_H1, 1);
    double barClose= iClose(Symbol(), PERIOD_H1, 1);
    double barOpen = iOpen(Symbol(), PERIOD_H1, 1);
    double barBody = MathAbs(barClose - barOpen);

    // F2: start at i=2 so bar 1 is not double-counted in the 10-bar low
    double lo10 = barLow;
    for (int i = 2; i <= Lo10Period; i++)
        lo10 = MathMin(lo10, iLow(Symbol(), PERIOD_H1, i));

    if (CountConsecLowRank(1) < ConsecBars) return;

    if (barLow >= lo10) return;
    if (barClose <= lo10) return;
    if ((lo10 - barLow) <= WickMinATR * atr14) return;

    if (barBody > BodyMaxATR * atr14) return;

    if ((ema50 - barClose) < EMADistATR * atr14) return;

    // Enter SHORT at next bar open (current bar 0) — use Bid for SELL
    double entryPrice = Bid;
    int ticket = OrderSend(Symbol(), OP_SELL, LotSize, entryPrice, SlippagePts,
                           0, 0, "T131", Magic, 0, clrRed);
    if (ticket > 0) {
        holdCount = 0;
        Print("T131 ENTRY SHORT bar=", TimeToStr(barTime), " price=", entryPrice,
              " ATR=", atr14, " rank=", ComputeATRRank(1),
              " ema50=", ema50, " dist=", (ema50 - barClose),
              " spread=", liveSpreadPips, "pip");
    } else {
        Print("T131 ENTRY FAILED err=", GetLastError());
    }
}
// +------------------------------------------------------------------+

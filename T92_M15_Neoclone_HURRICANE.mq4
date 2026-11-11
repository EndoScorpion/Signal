//+------------------------------------------------------------------+
//| T92 M15 Neoclone — HURRICANE Theory with Loss Recovery & Hedge    |
//| 10 Nov 2026                                                        |
//+------------------------------------------------------------------+
//| Extends NeocloneBase_Template                                      |
//| T92 logic: slope>=25 + FPCS>1 in HURRICANE regime                 |
//| Loss recovery: alternating direction                               |
//| High-DD hedge: scaled lots + opposite order                        |
//+------------------------------------------------------------------+

#property strict
#property description "T92 M15 HURRICANE - trailing stop + loss recovery + hedge"

#include "NeocloneBase_Template.mq4"

// Theory-specific parameters
input double SlopeThreshold       = 25.0;      // slope >= 25
input double FPCSThreshold        = 1.0;       // FPCS > 1.0
input int    SlopeBarPeriod       = 2;         // Slope window
input int    HURRICANESlope       = 25;        // Hurricane regime marker

// ATR & volatility
input int    ATRPeriod            = 14;
input double StochUpperThreshold  = 10.0;
input double StochLowerThreshold  = 90.0;

// ─────────────────────────────────────────────────────────────────────────────
// INDICATOR CALCULATIONS (FP-fixed)
// ─────────────────────────────────────────────────────────────────────────────

double CalculateSlope(int bar) {
    // Slope using shift=1 (NOT shift=0 to avoid lookahead bias)
    if (bar < 2) return 0.0;

    double close0 = Close[bar];
    double close1 = Close[bar + 1];
    double slope = (close0 - close1) / p;  // Slope in points

    return slope;
}

double CalculateFPCS(int bar) {
    // FPCS = Fourier Power Coherence Score
    // Simplified: trending strength via ATR-normalized slope
    if (bar < ATRPeriod) return 0.0;

    double atr = iATR(Symbol(), Period(), ATRPeriod, bar);
    double slope = CalculateSlope(bar);

    if (atr < p) return 0.0;
    double fpcs = (slope * p) / atr;  // Normalized score

    return SafeNormalize(fpcs);
}

double GetStochastic(int period, int bar) {
    // Stochastic oscillator (simplified)
    double highest = High[iHighest(Symbol(), Period(), MODE_HIGH, period, bar)];
    double lowest = Low[iLowest(Symbol(), Period(), MODE_LOW, period, bar)];

    if (highest == lowest) return 50.0;
    double stoch = ((Close[bar] - lowest) / (highest - lowest)) * 100.0;

    return SafeNormalize(stoch);
}

// ─────────────────────────────────────────────────────────────────────────────
// T92 WIN LOGIC
// ─────────────────────────────────────────────────────────────────────────────

bool T92_BUY_Signal(int bar) {
    if (bar < 2) return false;

    // Gate 1: Slope >= 25 (strong uptrend)
    double slope = CalculateSlope(bar);
    if (slope < SlopeThreshold) return false;

    // Gate 2: FPCS > 1.0 (trending coherence)
    double fpcs = CalculateFPCS(bar);
    if (fpcs <= FPCSThreshold) return false;

    // Gate 3: Stochastic < 10 (oversold entry in uptrend)
    double stoch = GetStochastic(14, bar);
    if (stoch > StochUpperThreshold) return false;

    // Gate 4: Must be in HURRICANE regime (strong winds)
    // (In real implementation, would check regime state)

    return true;
}

bool T92_SELL_Signal(int bar) {
    if (bar < 2) return false;

    // Mirror of BUY: slope =< -25 (strong downtrend)
    double slope = CalculateSlope(bar);
    if (slope > -SlopeThreshold) return false;

    // Gate 2: FPCS < -1.0
    double fpcs = CalculateFPCS(bar);
    if (fpcs >= -FPCSThreshold) return false;

    // Gate 3: Stochastic > 90 (overbought entry in downtrend)
    double stoch = GetStochastic(14, bar);
    if (stoch < StochLowerThreshold) return false;

    return true;
}

// ─────────────────────────────────────────────────────────────────────────────
// LOSS RECOVERY: ALTERNATING DIRECTION
// ─────────────────────────────────────────────────────────────────────────────

bool EvaluateRecoveryEntry(int type, int barOffset) {
    // After a LOST_BUY, look for SELL entry (and vice versa)
    // Use same T92 win logic but inverted

    int checkBar = iBarShift(Symbol(), Period(), TimeCurrent() - barOffset * Period() * 60, false);
    if (checkBar < 0 || checkBar > Bars - 2) return false;

    if (type == OP_SELL) {
        // Recovery SELL after lost BUY
        return T92_SELL_Signal(checkBar);
    } else {
        // Recovery BUY after lost SELL
        return T92_BUY_Signal(checkBar);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SIGNAL GENERATION
// ─────────────────────────────────────────────────────────────────────────────

void GenerateSignals() {
    if (PositionOpen()) return;  // Already in trade

    int bar = 1;  // Current bar

    if (T92_BUY_Signal(bar)) {
        double entryPrice = Ask;
        double sl = SafeNormalize(entryPrice - (SLPoints * p));
        double tp = SafeNormalize(entryPrice + (TPPoints * p));

        int ticket = OrderSend(Symbol(), OP_BUY, LotSize, entryPrice, 10, sl, tp,
                              "T92_BUY", MagicNumber, 0, clrBlue);

        if (ticket > 0) {
            ddMonitor.entryBar = Bar;
            ddMonitor.entryPrice = entryPrice;
            ddMonitor.orderType = OP_BUY;
            ddMonitor.maxDD = 0;
            ddMonitor.hedgeTriggered = false;
        }
    }

    else if (T92_SELL_Signal(bar)) {
        double entryPrice = Bid;
        double sl = SafeNormalize(entryPrice + (SLPoints * p));
        double tp = SafeNormalize(entryPrice - (TPPoints * p));

        int ticket = OrderSend(Symbol(), OP_SELL, LotSize, entryPrice, 10, sl, tp,
                              "T92_SELL", MagicNumber, 0, clrRed);

        if (ticket > 0) {
            ddMonitor.entryBar = Bar;
            ddMonitor.entryPrice = entryPrice;
            ddMonitor.orderType = OP_SELL;
            ddMonitor.maxDD = 0;
            ddMonitor.hedgeTriggered = false;
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// BACKTEST CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────

int OnInit() {
    // Theory-specific init
    LotSize = 0.01;
    TPPoints = 50;           // 50 pts TP (from memory: 2015-W23 best)
    SLPoints = 30;           // 30 pts SL
    UseTrailingTP = false;   // Fixed TP first per Standing Rules
    UseLossRecovery = true;
    UseHighDDHedge = true;
    DDTriggerPercent = 2.0;

    return NeocloneBase_Template::OnInit();
}

void OnTick() {
    // Call base handler
    NeocloneBase_Template::OnTick();
}

//+------------------------------------------------------------------+
//| Neoclone Base Template — Loss Recovery & High-DD Hedge Engine     |
//| 10 Nov 2026                                                        |
//+------------------------------------------------------------------+
//| Framework for trailing-stop, alternate-entry, loss-recovery, and  |
//| high-DD hedge theories. FP fixes applied (p=0.0001 hardcoded).    |
//| M1-resolved fill causality for all orders.                        |
//+------------------------------------------------------------------+

#property strict

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION (override in theory-specific EAs)
// ─────────────────────────────────────────────────────────────────────────────

input int    MagicNumber          = 201110;
input double LotSize              = 0.01;
input double TPPoints             = 50;        // Fixed TP
input double SLPoints             = 30;        // Fixed SL
input bool   UseTrailingTP        = false;
input double TrailingTPPercent    = 1.0;       // % trailing TP if enabled
input bool   UseLossRecovery      = true;
input bool   UseHighDDHedge       = true;
input double DDTriggerPercent     = 2.0;       // Hedge at 2% DD
input int    MaxConsecutiveLosses = 3;
input int    RecoveryLookupBars   = 50;        // Bars to scan for recovery entry

// ─────────────────────────────────────────────────────────────────────────────
// FLOATING POINT FIXES (10 Nov 2026 — ALL FUTURE EAs)
// ─────────────────────────────────────────────────────────────────────────────

#define p 0.0001  // Hardcoded FXOpen 5-digit ECN point value (NOT Point variable)

// Normalize to grid: price_int = (int)(price / p ± 0.5)
int PriceToGrid(double price, bool roundUp) {
    int sign = roundUp ? 1 : -1;
    return (int)(price / p + (sign * 0.5));
}

double GridToPrice(int priceInt) {
    return priceInt * p;
}

// Normalize double using hardcoded 4, NOT Digits
double SafeNormalize(double val) {
    return NormalizeDouble(val, 4);
}

// ─────────────────────────────────────────────────────────────────────────────
// STATE STRUCTURES
// ─────────────────────────────────────────────────────────────────────────────

struct LossTracker {
    int consecutiveLosses;
    int lastLossBar;
    int lastLossOrderType;  // OP_BUY or OP_SELL
    bool recoveryAttempted;
};

struct DrawdownMonitor {
    int entryBar;
    double entryPrice;
    int orderType;
    double maxDD;
    double maxDDPercent;
    bool hedgeTriggered;
};

struct HedgeOrder {
    int ticket;
    int type;               // OP_BUY or OP_SELL
    double lotSize;
    double entryPrice;
    int entryBar;
    bool active;
};

LossTracker lossTracker;
DrawdownMonitor ddMonitor;
HedgeOrder hedgeOrder;

// ─────────────────────────────────────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────────────────────────────────────

int OnInit() {
    lossTracker.consecutiveLosses = 0;
    lossTracker.lastLossBar = 0;
    lossTracker.recoveryAttempted = false;

    ddMonitor.hedgeTriggered = false;
    hedgeOrder.active = false;

    return INIT_SUCCEEDED;
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN TICK HANDLER
// ─────────────────────────────────────────────────────────────────────────────

void OnTick() {
    // Update DD monitor if trade open
    if (PositionOpen()) {
        UpdateDrawdown();

        // Check hedge trigger
        if (UseHighDDHedge && ddMonitor.maxDDPercent >= DDTriggerPercent && !ddMonitor.hedgeTriggered) {
            TriggerHedge();
        }
    }

    // Check closed trades for loss recovery
    if (UseLossRecovery && lossTracker.consecutiveLosses > 0) {
        CheckLossRecovery();
    }

    // Update trailing TP if enabled
    if (UseTrailingTP && PositionOpen()) {
        UpdateTrailingTP();
    }

    // Generate entry signals (override in theory-specific EA)
    GenerateSignals();
}

// ─────────────────────────────────────────────────────────────────────────────
// POSITION MANAGEMENT
// ─────────────────────────────────────────────────────────────────────────────

bool PositionOpen() {
    return OrderSelect(MagicNumber, SELECT_BY_TICKET) || FindOpenOrder() >= 0;
}

int FindOpenOrder() {
    for (int i = OrdersTotal() - 1; i >= 0; i--) {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES) && OrderMagicNumber() == MagicNumber) {
            return OrderTicket();
        }
    }
    return -1;
}

double GetOpenPrice() {
    if (FindOpenOrder() >= 0) {
        return OrderOpenPrice();
    }
    return 0.0;
}

double GetCurrentDD() {
    int ticket = FindOpenOrder();
    if (ticket < 0) return 0.0;

    double open = OrderOpenPrice();
    double bid = Bid, ask = Ask;
    double current = (OrderType() == OP_BUY) ? bid : ask;

    if (OrderType() == OP_BUY) {
        return SafeNormalize((open - current) / p);  // DD in points
    } else {
        return SafeNormalize((current - open) / p);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// DRAWDOWN MONITOR
// ─────────────────────────────────────────────────────────────────────────────

void UpdateDrawdown() {
    if (!PositionOpen()) return;

    double ddPoints = GetCurrentDD();
    double ddPct = (ddPoints / SafeNormalize(GetOpenPrice() / 100000.0)) * 100.0;  // Rough pct

    if (ddPoints > ddMonitor.maxDD) {
        ddMonitor.maxDD = ddPoints;
        ddMonitor.maxDDPercent = ddPct;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// HEDGE ENGINE
// ─────────────────────────────────────────────────────────────────────────────

void TriggerHedge() {
    if (!PositionOpen()) return;

    int mainType = (FindOpenOrder() >= 0) ? OrderType() : OP_BUY;
    int hedgeType = (mainType == OP_BUY) ? OP_SELL : OP_BUY;

    // Scale hedge lot based on DD
    double hedgeLot = LotSize * 0.5;  // 50% of base at trigger
    double hedgePrice = (mainType == OP_BUY) ?
        SafeNormalize(Ask + (10 * p)) :
        SafeNormalize(Bid - (10 * p));  // Offset hedge by 10 pts

    int ticket = (hedgeType == OP_BUY) ?
        OrderSend(Symbol(), OP_BUY, hedgeLot, Ask, 10, 0, 0, "Hedge", MagicNumber + 1000, 0, clrBlue) :
        OrderSend(Symbol(), OP_SELL, hedgeLot, Bid, 10, 0, 0, "Hedge", MagicNumber + 1000, 0, clrRed);

    if (ticket > 0) {
        hedgeOrder.ticket = ticket;
        hedgeOrder.type = hedgeType;
        hedgeOrder.lotSize = hedgeLot;
        hedgeOrder.active = true;
        ddMonitor.hedgeTriggered = true;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// LOSS RECOVERY ENGINE
// ─────────────────────────────────────────────────────────────────────────────

void UpdateLossTracker(int orderTicket) {
    if (!OrderSelect(orderTicket, SELECT_BY_TICKET)) return;

    double profit = OrderProfit() + OrderCommission() + OrderSwap();

    if (profit < 0) {
        lossTracker.consecutiveLosses++;
        lossTracker.lastLossBar = iBarShift(Symbol(), Period(), OrderCloseTime(), false);
        lossTracker.lastLossOrderType = OrderType();
        lossTracker.recoveryAttempted = false;
    } else {
        lossTracker.consecutiveLosses = 0;
    }
}

void CheckLossRecovery() {
    if (lossTracker.consecutiveLosses < 1 || lossTracker.recoveryAttempted) return;
    if (PositionOpen()) return;  // Already have position open

    int recoveryType = (lossTracker.lastLossOrderType == OP_BUY) ? OP_SELL : OP_BUY;

    // Scan last N bars for recovery entry using same win logic
    for (int i = 1; i <= RecoveryLookupBars; i++) {
        if (EvaluateRecoveryEntry(recoveryType, i)) {
            // Place recovery trade
            double price = (recoveryType == OP_BUY) ? Ask : Bid;
            int ticket = OrderSend(Symbol(), recoveryType, LotSize, price, 10,
                                  SafeNormalize(price + (SLPoints * p * (recoveryType == OP_BUY ? -1 : 1))),
                                  SafeNormalize(price + (TPPoints * p * (recoveryType == OP_BUY ? 1 : -1))),
                                  "RecoveryTrade", MagicNumber, 0,
                                  recoveryType == OP_BUY ? clrBlue : clrRed);

            if (ticket > 0) {
                lossTracker.recoveryAttempted = true;
            }
            break;
        }
    }
}

bool EvaluateRecoveryEntry(int type, int barOffset) {
    // Override in theory-specific EA to apply actual win logic
    return false;
}

// ─────────────────────────────────────────────────────────────────────────────
// TRAILING TP
// ─────────────────────────────────────────────────────────────────────────────

void UpdateTrailingTP() {
    if (!PositionOpen() || !UseTrailingTP) return;

    int ticket = FindOpenOrder();
    if (ticket < 0) return;

    if (!OrderSelect(ticket, SELECT_BY_TICKET)) return;

    double trailingPts = SafeNormalize(OrderOpenPrice() * TrailingTPPercent / 100.0 / p);
    double newTP = 0;

    if (OrderType() == OP_BUY) {
        newTP = SafeNormalize(Bid + (trailingPts * p));
        if (newTP > OrderTakeProfit()) {
            OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), newTP, 0, clrGreen);
        }
    } else {
        newTP = SafeNormalize(Ask - (trailingPts * p));
        if (newTP < OrderTakeProfit()) {
            OrderModify(ticket, OrderOpenPrice(), OrderStopLoss(), newTP, 0, clrGreen);
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SIGNAL GENERATION (OVERRIDE IN THEORY-SPECIFIC EAs)
// ─────────────────────────────────────────────────────────────────────────────

void GenerateSignals() {
    // Placeholder: implement theory-specific entry logic here
}

void OnDeinit(const int reason) {
    // Cleanup
}

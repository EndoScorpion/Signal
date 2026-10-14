//+------------------------------------------------------------------+
//| EMA_ATR_Scalper_M1.mq4                                           |
//| MT4 / MQL4 - EURUSD M1 scalper for FXOpen 5-digit ECN/STP         |
//| Entry : EMA(9) / EMA(21) crossover on CLOSED bars                 |
//| Exit  : ATR-based initial SL/TP + ATR dynamic trailing stop       |
//|                                                                  |
//| Backtest notes                                                   |
//|  - Signals are read on closed bars (shift 1 and 2) and only once  |
//|    per new bar, so "Every tick", "Control points" and "Open       |
//|    prices only" give the same entries; only exits/trailing differ.|
//|  - Sleep() does not pause the Strategy Tester, so the requote     |
//|    retry loop runs instantly there (requotes never occur in the   |
//|    tester anyway); it only matters on a live/demo account.        |
//|  - The tester uses the fixed spread from its settings, so the     |
//|    MaxSpreadAllowed filter only bites when that spread is higher. |
//+------------------------------------------------------------------+
#property copyright "Nasif"
#property version   "1.00"
#property strict

//--- user inputs ----------------------------------------------------
input int    MagicNumber           = 20261011; // unique id for this EA's orders
input double LotSize               = 0.01;     // fixed lot, used when RiskPercent = 0
input double RiskPercent           = 0.0;      // % of balance risked per trade (0 = fixed LotSize)
input double MaxSpreadAllowed      = 1.5;      // max spread in PIPS for new entries
input int    FastEMAPeriod         = 9;        // fast EMA
input int    SlowEMAPeriod         = 21;       // slow EMA
input int    ATRPeriod             = 14;       // ATR period (closed bars)
input double ATR_SL_Mult           = 1.5;      // initial SL = ATR x this
input double ATR_TP_Mult           = 2.0;      // initial TP = ATR x this (0 = no TP)
input double ATR_Trail_Mult        = 1.0;      // trailing distance = ATR x this (0 = no trailing)
input double TrailStartPips        = 3.0;      // profit in pips before trailing starts
input double TrailStepPips         = 0.5;      // minimum SL improvement per modify (limits modify spam)
input double SlippagePips          = 0.5;      // max slippage in pips
input double MinSLPips             = 3.0;      // floor for the ATR stop (very quiet M1 bars)
input bool   CloseOnOppositeSignal = true;     // close open position on the opposite cross
input int    MaxRetries            = 3;        // attempts for requote / busy errors
input int    RetryDelayMs          = 200;      // pause between attempts (live only)
input string TradeComment          = "EMAATR";

//+------------------------------------------------------------------+
//| CBroker: 4/5-digit normalization and symbol limits                |
//| On 3/5-digit quotes 1 pip = 10 points, on 2/4-digit 1 pip = 1.   |
//+------------------------------------------------------------------+
class CBroker
  {
private:
   int               m_pipFactor;   // points per pip (10 on 5-digit)
   double            m_pip;         // price value of one pip
public:
   void              Init()
     {
      m_pipFactor = (_Digits == 3 || _Digits == 5) ? 10 : 1;
      m_pip       = _Point * m_pipFactor;
     }
   double            Pip()                     const { return(m_pip); }
   double            PipsToPrice(double pips)  const { return(pips * m_pip); }
   int               PipsToPoints(double pips) const { return((int)MathRound(pips * m_pipFactor)); }
   double            SpreadPips()              const { return((Ask - Bid) / m_pip); }
   double            Norm(double price)        const { return(NormalizeDouble(price, _Digits)); }
   // broker minimum distance between price and SL/TP (stop level), plus one point margin
   double            StopLevel()               const { return((MarketInfo(_Symbol, MODE_STOPLEVEL) + 1) * _Point); }
   // freeze level: inside it the broker rejects modifies
   double            FreezeLevel()             const { return(MarketInfo(_Symbol, MODE_FREEZELEVEL) * _Point); }
  };

//+------------------------------------------------------------------+
//| CSignal: EMA crossover on closed bars                             |
//| returns OP_BUY, OP_SELL or -1 (no signal)                         |
//+------------------------------------------------------------------+
class CSignal
  {
public:
   int               Get() const
     {
      double f1 = iMA(_Symbol, PERIOD_CURRENT, FastEMAPeriod, 0, MODE_EMA, PRICE_CLOSE, 1);
      double s1 = iMA(_Symbol, PERIOD_CURRENT, SlowEMAPeriod, 0, MODE_EMA, PRICE_CLOSE, 1);
      double f2 = iMA(_Symbol, PERIOD_CURRENT, FastEMAPeriod, 0, MODE_EMA, PRICE_CLOSE, 2);
      double s2 = iMA(_Symbol, PERIOD_CURRENT, SlowEMAPeriod, 0, MODE_EMA, PRICE_CLOSE, 2);
      if(f2 <= s2 && f1 > s1) return(OP_BUY);    // fast crossed above slow on the last closed bar
      if(f2 >= s2 && f1 < s1) return(OP_SELL);   // fast crossed below slow
      return(-1);
     }
   double            ATR() const { return(iATR(_Symbol, PERIOD_CURRENT, ATRPeriod, 1)); } // closed bar: no repaint
  };

//+------------------------------------------------------------------+
//| error text for the journal                                        |
//+------------------------------------------------------------------+
string ErrText(int code)
  {
   switch(code)
     {
      case 0:   return("no error");
      case 1:   return("no error, nothing changed");
      case 2:   return("common error");
      case 3:   return("invalid trade parameters");
      case 4:   return("trade server busy");
      case 6:   return("no connection");
      case 8:   return("too frequent requests");
      case 64:  return("account disabled");
      case 128: return("trade timeout");
      case 129: return("invalid price");
      case 130: return("invalid stops");
      case 131: return("invalid trade volume");
      case 132: return("market closed");
      case 133: return("trade disabled");
      case 134: return("not enough money");
      case 135: return("price changed");
      case 136: return("off quotes");
      case 137: return("broker busy");
      case 138: return("requote");
      case 139: return("order locked");
      case 141: return("too many requests");
      case 145: return("modification denied, too close to market");
      case 146: return("trade context busy");
      case 148: return("too many open/pending orders");
      case 4108:return("invalid ticket");
      case 4109:return("trading not allowed in EA settings");
      case 4110:return("longs not allowed");
      case 4111:return("shorts not allowed");
     }
   return("unknown error");
  }

// errors worth another attempt: price moved or server/context busy
bool Retryable(int code)
  {
   return(code == 4 || code == 8 || code == 135 || code == 136 || code == 137 || code == 138 || code == 141 || code == 146);
  }

//+------------------------------------------------------------------+
//| CTrade: order execution, ECN two-step stops, sizing, trailing    |
//+------------------------------------------------------------------+
class CTrade
  {
private:
   CBroker          *m_b;

   bool              Mine() const { return(OrderSymbol() == _Symbol && OrderMagicNumber() == MagicNumber); }

public:
   void              Init(CBroker *b) { m_b = b; }

   //--- number of open market positions of this EA (type -1 = both)
   int               Count(int type = -1) const
     {
      int n = 0;
      for(int i = OrdersTotal() - 1; i >= 0; i--)
        {
         if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES) || !Mine()) continue;
         if(OrderType() > OP_SELL) continue;
         if(type < 0 || OrderType() == type) n++;
        }
      return(n);
     }

   //--- lot size: fixed, or risk % of balance over the SL distance
   double            Lots(double slDist) const
     {
      double lots = LotSize;
      if(RiskPercent > 0 && slDist > 0)
        {
         double tickVal  = MarketInfo(_Symbol, MODE_TICKVALUE);
         double tickSize = MarketInfo(_Symbol, MODE_TICKSIZE);
         if(tickVal > 0 && tickSize > 0)
           {
            double lossPerLot = slDist / tickSize * tickVal;          // money lost per 1.0 lot at SL
            lots = (AccountBalance() * RiskPercent / 100.0) / lossPerLot;
           }
        }
      double step = MarketInfo(_Symbol, MODE_LOTSTEP), mn = MarketInfo(_Symbol, MODE_MINLOT), mx = MarketInfo(_Symbol, MODE_MAXLOT);
      if(step <= 0) step = 0.01;
      lots = MathFloor(lots / step) * step;
      lots = MathMax(mn, MathMin(mx, lots));
      return(NormalizeDouble(lots, 2));
     }

   //--- modify SL/TP with retries; prices normalized and checked against stop level
   bool              Modify(int ticket, double sl, double tp)
     {
      for(int a = 1; a <= MaxRetries; a++)
        {
         if(!OrderSelect(ticket, SELECT_BY_TICKET)) { Print("MODIFY #", ticket, " select failed: ", GetLastError()); return(false); }
         RefreshRates();
         sl = m_b.Norm(sl); tp = m_b.Norm(tp);
         if(MathAbs(sl - OrderStopLoss()) < _Point && MathAbs(tp - OrderTakeProfit()) < _Point) return(true); // nothing to change
         ResetLastError();
         if(OrderModify(ticket, OrderOpenPrice(), sl, tp, 0, clrNONE))
           {
            Print("MODIFY #", ticket, " ok sl ", DoubleToString(sl, _Digits), " tp ", DoubleToString(tp, _Digits));
            return(true);
           }
         int err = GetLastError();
         Print("MODIFY #", ticket, " attempt ", a, " failed: ", err, " ", ErrText(err));
         if(!Retryable(err) && err != 128) return(false);
         Sleep(RetryDelayMs);
        }
      return(false);
     }

   //--- close a position at market with retries
   bool              Close(int ticket)
     {
      for(int a = 1; a <= MaxRetries; a++)
        {
         if(!OrderSelect(ticket, SELECT_BY_TICKET) || OrderCloseTime() > 0) return(true);
         RefreshRates();
         double px = m_b.Norm(OrderType() == OP_BUY ? Bid : Ask);
         ResetLastError();
         if(OrderClose(ticket, OrderLots(), px, m_b.PipsToPoints(SlippagePips), clrNONE))
           { Print("CLOSE #", ticket, " ok at ", DoubleToString(px, _Digits)); return(true); }
         int err = GetLastError();
         Print("CLOSE #", ticket, " attempt ", a, " failed: ", err, " ", ErrText(err));
         if(!Retryable(err)) return(false);
         Sleep(RetryDelayMs);
        }
      return(false);
     }

   //--- ECN market entry: send WITHOUT stops, then attach SL/TP from the real fill price
   bool              Open(int type, double slDist, double tpDist)
     {
      double lots = Lots(slDist);
      if(AccountFreeMarginCheck(_Symbol, type, lots) <= 0 || GetLastError() == 134)
        { Print("OPEN skipped: not enough free margin for ", DoubleToString(lots, 2), " lots"); return(false); }

      int ticket = -1;
      for(int a = 1; a <= MaxRetries && ticket < 0; a++)
        {
         RefreshRates();                                         // fresh quote every attempt
         double px = m_b.Norm(type == OP_BUY ? Ask : Bid);
         ResetLastError();
         ticket = OrderSend(_Symbol, type, lots, px, m_b.PipsToPoints(SlippagePips), 0, 0, TradeComment, MagicNumber, 0,
                            type == OP_BUY ? clrDodgerBlue : clrTomato);
         if(ticket >= 0) break;
         int err = GetLastError();
         Print("OPEN ", (type == OP_BUY ? "buy" : "sell"), " attempt ", a, " failed: ", err, " ", ErrText(err));
         if(!Retryable(err)) return(false);                    // 128 timeout is NOT retried: the order may exist
         Sleep(RetryDelayMs);
        }
      if(ticket < 0) return(false);
      if(!OrderSelect(ticket, SELECT_BY_TICKET)) { Print("OPEN #", ticket, " select failed: ", GetLastError()); return(false); }

      // stops from the actual fill price, pushed outside the broker stop level
      double open = OrderOpenPrice(), minD = m_b.StopLevel();
      slDist = MathMax(slDist, minD);
      if(tpDist > 0) tpDist = MathMax(tpDist, minD);
      double sl = (type == OP_BUY) ? open - slDist : open + slDist;
      double tp = 0;
      if(tpDist > 0) tp = (type == OP_BUY) ? open + tpDist : open - tpDist;
      Print("OPEN #", ticket, (type == OP_BUY ? " buy " : " sell "), DoubleToString(lots, 2), " at ", DoubleToString(open, _Digits));

      if(!Modify(ticket, sl, tp))
        {
         // never leave a naked position: if the stop cannot be attached, close it
         Print("OPEN #", ticket, " stops could not be attached -> closing for safety");
         Close(ticket);
         return(false);
        }
      return(true);
     }

   //--- close all positions of one type (opposite-signal exit)
   void              CloseType(int type)
     {
      for(int i = OrdersTotal() - 1; i >= 0; i--)
        {
         if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES) || !Mine() || OrderType() != type) continue;
         Close(OrderTicket());
        }
     }

   //--- ATR dynamic trailing stop, runs every tick
   void              Trail(double atr)
     {
      if(ATR_Trail_Mult <= 0 || atr <= 0) return;
      double dist = MathMax(atr * ATR_Trail_Mult, m_b.StopLevel());
      double start = m_b.PipsToPrice(TrailStartPips), step = m_b.PipsToPrice(TrailStepPips), frz = m_b.FreezeLevel();
      RefreshRates();
      for(int i = OrdersTotal() - 1; i >= 0; i--)
        {
         if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES) || !Mine()) continue;
         int t = OrderTicket();
         double sl = OrderStopLoss(), tp = OrderTakeProfit(), open = OrderOpenPrice();
         if(OrderType() == OP_BUY)
           {
            if(Bid - open < start) continue;                         // not enough profit yet
            double nsl = m_b.Norm(Bid - dist);
            if(sl > 0 && nsl < sl + step) continue;                  // only move forward, in steps
            if(Bid - sl <= frz && sl > 0) continue;                  // inside freeze level
            Modify(t, nsl, tp);
           }
         else if(OrderType() == OP_SELL)
           {
            if(open - Ask < start) continue;
            double nsl = m_b.Norm(Ask + dist);
            if(sl > 0 && nsl > sl - step) continue;
            if(sl - Ask <= frz && sl > 0) continue;
            Modify(t, nsl, tp);
           }
        }
     }
  };

//--- global objects -------------------------------------------------
CBroker  g_broker;
CSignal  g_signal;
CTrade   g_trade;
datetime g_lastBar = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   g_broker.Init();
   g_trade.Init(GetPointer(g_broker));
   if(FastEMAPeriod >= SlowEMAPeriod) { Print("INIT: FastEMAPeriod must be < SlowEMAPeriod"); return(INIT_PARAMETERS_INCORRECT); }
   if(_Period != PERIOD_M1) Print("INIT warning: designed for M1, attached to period ", _Period);
   Print("INIT: digits ", _Digits, " pip ", DoubleToString(g_broker.Pip(), _Digits), " stoplevel ", MarketInfo(_Symbol, MODE_STOPLEVEL),
         " pts, slippage ", g_broker.PipsToPoints(SlippagePips), " pts");
   g_lastBar = Time[0];   // do not trade a cross that happened before attach
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
void OnTick()
  {
   if(Bars < SlowEMAPeriod + ATRPeriod + 3) return;
   double atr = g_signal.ATR();

   // 1. manage open positions every tick
   g_trade.Trail(atr);

   // 2. new entries only once per bar (closed-bar signal, backtest consistent)
   if(Time[0] == g_lastBar) return;
   g_lastBar = Time[0];

   int sig = g_signal.Get();
   if(sig < 0) return;

   if(CloseOnOppositeSignal)
      g_trade.CloseType(sig == OP_BUY ? OP_SELL : OP_BUY);

   if(g_trade.Count() > 0) return;                              // one position at a time
   if(!IsTradeAllowed()) { Print("ENTRY skipped: trading not allowed"); return; }

   double spread = g_broker.SpreadPips();
   if(spread > MaxSpreadAllowed) { Print("ENTRY skipped: spread ", DoubleToString(spread, 1), " > ", DoubleToString(MaxSpreadAllowed, 1), " pips"); return; }

   double slDist = MathMax(atr * ATR_SL_Mult, g_broker.PipsToPrice(MinSLPips));
   double tpDist = ATR_TP_Mult > 0 ? atr * ATR_TP_Mult : 0;
   g_trade.Open(sig, slDist, tpDist);
  }
//+------------------------------------------------------------------+

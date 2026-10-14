//+------------------------------------------------------------------+
//| ChopBracket_h1a.mq4  - TEST EA, backtest only (12 Oct 2026)      |
//| Moving bracket around the recent range, re-placed every new bar. |
//| Mode 0 = FADE: limit orders just OUTSIDE the range edges,        |
//|          TP back toward mid-range (only when ADX is low=choppy). |
//| Mode 1 = BREAKOUT: stop orders just outside the range edges.     |
//| Pending orders are deleted and re-placed each bar (follows the   |
//| range). When one side fills, the other is deleted. Open trades   |
//| close at SL/TP or after MaxHoldBars bars. One trade at a time.   |
//+------------------------------------------------------------------+
#property strict

extern int    Mode          = 1;     // 0 fade (limits), 1 breakout (stops)
extern int    RangeBars     = 20;    // bars used for range high/low
extern int    BufferPts     = 20;    // points beyond the edge
extern int    SLPts         = 150;   // stop loss distance (points)
extern double TPRangeFrac   = 0.5;   // fade TP = this fraction of range
extern int    TPPts         = 150;   // breakout TP distance (points)
extern int    MaxADX        = 22;    // fade only when ADX(14) <= this
extern int    MaxHoldBars   = 16;    // time exit
extern int    MaxSpreadPts  = 40;    // skip if spread wider
extern double Lots          = 0.01;
extern int    Magic         = 5110;

datetime lastBar = 0;

int OpenCount()
{
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol() != Symbol() || OrderMagicNumber() != Magic) continue;
      if(OrderType() == OP_BUY || OrderType() == OP_SELL) n++;
   }
   return n;
}

void DeletePending()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol() != Symbol() || OrderMagicNumber() != Magic) continue;
      if(OrderType() > OP_SELL) OrderDelete(OrderTicket());
   }
}

void TimeExit()
{
   int secs = MaxHoldBars * PeriodSeconds();
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol() != Symbol() || OrderMagicNumber() != Magic) continue;
      if(OrderType() > OP_SELL) continue;
      if(TimeCurrent() - OrderOpenTime() >= secs)
      {
         if(OrderType() == OP_BUY)  OrderClose(OrderTicket(), OrderLots(), Bid, 3);
         else                       OrderClose(OrderTicket(), OrderLots(), Ask, 3);
      }
   }
}

void Place(int type, double price, double sl, double tp)
{
   OrderSend(Symbol(), type, Lots, NormalizeDouble(price, Digits), 3,
             NormalizeDouble(sl, Digits), NormalizeDouble(tp, Digits),
             "CB", Magic, 0, clrNONE);
}

int OnInit() { return(INIT_SUCCEEDED); }

void OnTick()
{
   // if a side filled, remove the opposite pending order right away
   if(OpenCount() > 0) { DeletePending(); }

   if(Time[0] == lastBar) return;      // act once per new bar
   lastBar = Time[0];

   TimeExit();
   DeletePending();                    // bracket follows the range: cancel old
   if(OpenCount() > 0) return;
   if(Bars < RangeBars + 20) return;
   if(MarketInfo(Symbol(), MODE_SPREAD) > MaxSpreadPts) return;

   double adx = iADX(NULL, 0, 14, PRICE_CLOSE, MODE_MAIN, 1);
   if(Mode == 0 && adx > MaxADX) return;   // fade only in chop

   int    hi = iHighest(NULL, 0, MODE_HIGH, RangeBars, 1);
   int    lo = iLowest (NULL, 0, MODE_LOW,  RangeBars, 1);
   double H = High[hi], L = Low[lo], R = H - L;
   if(R <= 0) return;

   double buf  = BufferPts * Point;
   double sl   = SLPts * Point;
   double minD = (MarketInfo(Symbol(), MODE_STOPLEVEL) + 2) * Point;

   if(Mode == 0)
   {
      double sellP = H + buf;            // sell limit above the highs
      double buyP  = L - buf;            // buy limit below the lows
      double tpD   = MathMax(R * TPRangeFrac, minD);
      if(sellP - Bid >= minD) Place(OP_SELLLIMIT, sellP, sellP + sl, sellP - tpD);
      if(Ask - buyP  >= minD) Place(OP_BUYLIMIT,  buyP,  buyP  - sl, buyP  + tpD);
   }
   else
   {
      double buyP  = H + buf;            // buy stop above the highs
      double sellP = L - buf;            // sell stop below the lows
      double tpD   = TPPts * Point;
      if(buyP  - Ask >= minD) Place(OP_BUYSTOP,  buyP,  buyP  - sl, buyP  + tpD);
      if(Bid - sellP >= minD) Place(OP_SELLSTOP, sellP, sellP + sl, sellP - tpD);
   }
}


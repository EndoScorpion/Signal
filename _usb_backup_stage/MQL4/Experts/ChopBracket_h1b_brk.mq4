//+------------------------------------------------------------------+
//| ChopBracket_h1b.mq4  - TEST EA, backtest only (12 Oct 2026)      |
//| Same moving-bracket idea as h1a, but sizes come from indicators: |
//|  Bollinger Bands -> bracket edges and width (the "space")        |
//|  ADX             -> choppy gate + widens margin when trending    |
//|  CCI             -> only the side price is pushing toward        |
//| Mode 0 = FADE (limit orders just outside the bands, TP to mid)   |
//| Mode 1 = BREAKOUT (stop orders just outside the bands)           |
//| Orders are deleted/re-placed every new bar. One trade at a time. |
//+------------------------------------------------------------------+
#property strict

extern int    Mode         = 1;     // 0 fade (limits), 1 breakout (stops)
extern int    BBPeriod     = 20;
extern double BBDev        = 2.0;
extern int    ADXPeriod    = 14;
extern int    MaxADX       = 22;    // fade only when ADX <= this (chop)
extern int    CCIPeriod    = 20;
extern double CCIEdge      = 50;    // sell side needs CCI >= +edge, buy side <= -edge
extern double MarginK      = 0.10;  // margin beyond band = MarginK * bandwidth
extern double MarginADXK   = 0.01;  // extra margin per ADX point above 15 (x bandwidth)
extern double SLK          = 0.60;  // stop distance = SLK * bandwidth
extern double TPFadeFrac   = 0.50;  // fade TP = this fraction of distance to mid band
extern double TPBreakK     = 0.50;  // breakout TP = TPBreakK * bandwidth
extern double MinWidthPts  = 80;    // skip if bandwidth smaller (points)
extern int    MaxHoldBars  = 16;
extern int    MaxSpreadPts = 40;
extern double Lots         = 0.01;
extern int    Magic        = 5120;

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
         if(OrderType() == OP_BUY) OrderClose(OrderTicket(), OrderLots(), Bid, 3);
         else                      OrderClose(OrderTicket(), OrderLots(), Ask, 3);
      }
   }
}

void Place(int type, double price, double sl, double tp)
{
   OrderSend(Symbol(), type, Lots, NormalizeDouble(price, Digits), 3,
             NormalizeDouble(sl, Digits), NormalizeDouble(tp, Digits),
             "CB2", Magic, 0, clrNONE);
}

int OnInit() { return(INIT_SUCCEEDED); }

void OnTick()
{
   if(OpenCount() > 0) { DeletePending(); }

   if(Time[0] == lastBar) return;
   lastBar = Time[0];

   TimeExit();
   DeletePending();
   if(OpenCount() > 0) return;
   if(Bars < BBPeriod + 30) return;
   if(MarketInfo(Symbol(), MODE_SPREAD) > MaxSpreadPts) return;

   double adx = iADX(NULL, 0, ADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
   if(Mode == 0 && adx > MaxADX) return;       // fade only in chop

   double up  = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_UPPER, 1);
   double lw  = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_LOWER, 1);
   double mid = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_MAIN,  1);
   double W   = up - lw;                        // bandwidth = the "space"
   if(W < MinWidthPts * Point) return;

   double cci = iCCI(NULL, 0, CCIPeriod, PRICE_TYPICAL, 1);

   double adxExtra = MathMax(0.0, adx - 15.0) * MarginADXK;
   double margin   = (MarginK + adxExtra) * W;  // gap beyond the band
   double sl       = SLK * W;                   // "height" of the stop
   double minD     = (MarketInfo(Symbol(), MODE_STOPLEVEL) + 2) * Point;

   double sellP = up + margin;
   double buyP  = lw - margin;

   if(Mode == 0)
   {
      // fade: sell limit above upper band if price is pushing up (CCI high);
      //       buy limit below lower band if pushing down (CCI low)
      if(cci >= CCIEdge && sellP - Bid >= minD)
      {
         double tpD = MathMax((sellP - mid) * TPFadeFrac, minD);
         Place(OP_SELLLIMIT, sellP, sellP + sl, sellP - tpD);
      }
      if(cci <= -CCIEdge && Ask - buyP >= minD)
      {
         double tpD = MathMax((mid - buyP) * TPFadeFrac, minD);
         Place(OP_BUYLIMIT, buyP, buyP - sl, buyP + tpD);
      }
   }
   else
   {
      // breakout: buy stop above upper band when CCI is positive;
      //           sell stop below lower band when CCI is negative
      double tpD = TPBreakK * W;
      if(cci >= CCIEdge && sellP - Ask >= minD)
         Place(OP_BUYSTOP, sellP, sellP - sl, sellP + tpD);
      if(cci <= -CCIEdge && Bid - buyP >= minD)
         Place(OP_SELLSTOP, buyP, buyP + sl, buyP - tpD);
   }
}


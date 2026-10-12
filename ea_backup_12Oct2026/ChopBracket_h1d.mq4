//+------------------------------------------------------------------+
//| ChopBracket_h1d.mq4  - TEST EA, backtest only (12 Oct 2026)      |
//| h1b + ATR and tick volume weighed into a choppiness score.       |
//|  Bollinger -> bracket edges and width (the "space")              |
//|  ADX       -> low ADX = chop (score) and wider margin when high  |
//|  CCI       -> which side price is pushing toward                 |
//|  ATR       -> volatility vs its long average (low = chop) and    |
//|               minimum margin/stop height                         |
//|  Volume    -> last bar tick volume vs 20-bar average (low = chop)|
//| Mode 0 = FADE (limits outside bands) needs score >= MinScore.    |
//| Mode 1 = BREAKOUT (stops outside bands) needs (1-score) >= Min.  |
//| Orders deleted/re-placed each new bar. One trade at a time.      |
//+------------------------------------------------------------------+
#property strict

extern int    Mode         = 0;     // 0 fade (limits), 1 breakout (stops)
extern int    BBPeriod     = 20;
extern double BBDev        = 2.0;
extern int    ADXPeriod    = 14;
extern int    MaxADX       = 30;    // ADX scaling for score (0 at/above this)
extern int    CCIPeriod    = 20;
extern double CCIEdge      = 50;
extern int    ATRFast      = 14;
extern int    ATRSlow      = 100;
extern int    VolBars      = 20;
extern double WADX         = 1.0;   // weights of the chop-score parts
extern double WATR         = 1.0;
extern double WVol         = 0.5;
extern double MinScore     = 0.50;  // 0..1, higher = pickier
extern double MarginK      = 0.10;  // x bandwidth
extern double MarginATRK   = 0.20;  // x ATR, added to margin
extern double SLK          = 0.35;  // x bandwidth
extern double SLATRK       = 1.00;  // x ATR (stop = larger of the two)
extern double TPFadeFrac   = 1.00;
extern double TPBreakK     = 0.50;
extern double MinWidthPts  = 80;
extern int    MaxHoldBars  = 16;
extern int    MaxSpreadPts = 40;
extern double Lots         = 0.01;
extern int    Magic        = 5140;

datetime lastBar = 0;

double Clip01(double x) { if(x < 0) return 0; if(x > 1) return 1; return x; }

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
             "CB3", Magic, 0, clrNONE);
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
   if(Bars < ATRSlow + 30) return;
   if(MarketInfo(Symbol(), MODE_SPREAD) > MaxSpreadPts) return;

   double adx  = iADX(NULL, 0, ADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
   double atrF = iATR(NULL, 0, ATRFast, 1);
   double atrS = iATR(NULL, 0, ATRSlow, 1);
   if(atrF <= 0 || atrS <= 0) return;

   double vsum = 0;
   for(int k = 2; k < 2 + VolBars; k++) vsum += (double)Volume[k];
   double vavg = vsum / VolBars;
   if(vavg <= 0) return;
   double vr = (double)Volume[1] / vavg;

   // choppiness score 0..1 (1 = very choppy / quiet)
   double sA = Clip01(1.0 - adx / MaxADX);          // low ADX
   double sB = Clip01(1.5 - atrF / atrS);           // ATR below its long average
   double sC = Clip01(1.5 - vr);                    // volume below average
   double score = (WADX * sA + WATR * sB + WVol * sC) / (WADX + WATR + WVol);

   if(Mode == 0 && score < MinScore) return;        // fade only when choppy
   if(Mode == 1 && (1.0 - score) < MinScore) return; // breakout only when expanding

   double up  = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_UPPER, 1);
   double lw  = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_LOWER, 1);
   double mid = iBands(NULL, 0, BBPeriod, BBDev, 0, PRICE_CLOSE, MODE_MAIN,  1);
   double W   = up - lw;
   if(W < MinWidthPts * Point) return;

   double cci = iCCI(NULL, 0, CCIPeriod, PRICE_TYPICAL, 1);

   double margin = MarginK * W + MarginATRK * atrF;
   double sl     = MathMax(SLK * W, SLATRK * atrF);
   double minD   = (MarketInfo(Symbol(), MODE_STOPLEVEL) + 2) * Point;

   double sellP = up + margin;
   double buyP  = lw - margin;

   if(Mode == 0)
   {
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
      double tpD = TPBreakK * W;
      if(cci >= CCIEdge && sellP - Ask >= minD)
         Place(OP_BUYSTOP, sellP, sellP - sl, sellP + tpD);
      if(cci <= -CCIEdge && Bid - buyP >= minD)
         Place(OP_SELLSTOP, buyP, buyP + sl, buyP - tpD);
   }
}


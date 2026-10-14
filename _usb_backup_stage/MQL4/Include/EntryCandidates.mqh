//+------------------------------------------------------------------+
//| EntryCandidates.mqh  - buy-only entry rules to test (MQL4)       |
//| Each rule is independent; select ONE via InpEntryRule.           |
//| All signals use CLOSED bars (shift 1) so tester == live.         |
//| Rule 0 = random baseline: every rule must beat it net of costs.  |
//+------------------------------------------------------------------+
#property strict

input int    InpEntryRule   = 1;    // 0=random 1=pullback-in-uptrend 2=sweep-reclaim 3=BB-touch+range
input int    InpTrendTF     = PERIOD_H1;
input int    InpTrendEMA    = 50;
input int    InpFastEMA     = 20;
input int    InpATRPeriod   = 14;
input int    InpSweepLookback = 20;  // bars defining the range low
input int    InpADXMax      = 25;   // rule 3 range filter
input double InpRandomProb  = 0.02; // rule 0: chance per bar

// Higher-timeframe trend: closed H1 bar above rising EMA50
bool HTFUp()
{
   double e1 = iMA(NULL, InpTrendTF, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double e2 = iMA(NULL, InpTrendTF, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 2);
   return iClose(NULL, InpTrendTF, 1) > e1 && e1 > e2;
}

// Rule 1: uptrend on H1, M-chart bar dips to/below EMA20 and closes back above it
bool Rule_Pullback()
{
   if(!HTFUp()) return false;
   double ema = iMA(NULL, 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   return Low[1] <= ema && Close[1] > ema && Close[1] > Open[1];
}

// Rule 2: bar 1 trades below the lowest low of the prior N bars, then closes back inside
bool Rule_SweepReclaim()
{
   int idx = iLowest(NULL, 0, MODE_LOW, InpSweepLookback, 2);
   double rangeLow = Low[idx];
   double atr = iATR(NULL, 0, InpATRPeriod, 1);
   return Low[1] < rangeLow && Close[1] > rangeLow
          && (rangeLow - Low[1]) < 0.5 * atr;    // shallow sweep, not a breakdown
}

// Rule 3: guide idea - closed bar below lower BB, ADX says ranging
bool Rule_BBRange()
{
   double lb  = iBands(NULL, 0, 20, 2.0, 0, PRICE_CLOSE, MODE_LOWER, 1);
   double adx = iADX(NULL, 0, 14, PRICE_CLOSE, MODE_MAIN, 1);
   return Close[1] < lb && adx < InpADXMax;
}

bool Rule_Random()
{
   return MathRand() / 32767.0 < InpRandomProb;
}

// Call once per new bar. Returns true when the selected rule fires.
bool EntrySignal()
{
   switch(InpEntryRule)
   {
      case 0: return Rule_Random();
      case 1: return Rule_Pullback();
      case 2: return Rule_SweepReclaim();
      case 3: return Rule_BBRange();
   }
   return false;
}

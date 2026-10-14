//+------------------------------------------------------------------+
//| SafeChunkCalculusMQL4.mq4                                        |
//| Velocity and acceleration of a blended chart/M15 price.          |
//| - Backward differences on closed bars: no future bars, no repaint.|
//| - M15 value = last CLOSED M15 bar at each chart bar's time.       |
//| - History capped at InpMaxBars; new bars cost O(1) per tick.      |
//+------------------------------------------------------------------+
#property strict
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_color1  clrCyan
#property indicator_color2  clrMagenta

input int    InpMaxBars  = 2000;   // bars computed on first load (safe chunk cap)
input double InpWeightTF = 0.6;    // weight of chart close; M15 gets 1 - this

double BufVel[], BufAcc[];

int OnInit()
  {
   SetIndexBuffer(0, BufVel); SetIndexStyle(0, DRAW_LINE); SetIndexLabel(0, "Velocity");
   SetIndexBuffer(1, BufAcc); SetIndexStyle(1, DRAW_LINE); SetIndexLabel(1, "Acceleration");
   IndicatorShortName("SafeChunk Calculus (chart+M15)");
   return(INIT_SUCCEEDED);
  }

// Blended price at chart bar i; returns false if M15 history is missing there.
bool Blend(int i, const datetime &time[], const double &close[], double &out)
  {
   int s = iBarShift(Symbol(), PERIOD_M15, time[i], false);
   if(s < 0) return(false);
   if(iTime(Symbol(), PERIOD_M15, s) + PeriodSeconds(PERIOD_M15) > time[i] + PeriodSeconds()) s++; // M15 bar still open at this bar's close -> use the previous closed one
   double m15 = iClose(Symbol(), PERIOD_M15, s);
   if(m15 <= 0) return(false);
   out = InpWeightTF * close[i] + (1.0 - InpWeightTF) * m15;
   return(true);
  }

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[],
                const long &tick_volume[], const long &volume[], const int &spread[])   // MQL4 signature
  {
   if(rates_total < 4) return(0);
   int start;
   if(prev_calculated <= 0)
     {
      ArrayInitialize(BufVel, EMPTY_VALUE); ArrayInitialize(BufAcc, EMPTY_VALUE);
      start = MathMin(InpMaxBars, rates_total - 4);                  // cap the first pass
     }
   else start = MathMin(rates_total - prev_calculated + 1, rates_total - 4); // new bar(s) + the forming bar

   for(int i = start; i >= 0; i--)
     {
      double p0, p1, p2;                                             // p0 = bar i, p1 = i+1 (older), p2 = i+2
      if(!Blend(i, time, close, p0) || !Blend(i + 1, time, close, p1) || !Blend(i + 2, time, close, p2))
        { BufVel[i] = EMPTY_VALUE; BufAcc[i] = EMPTY_VALUE; continue; }
      BufVel[i] = p0 - p1;                                           // backward first difference
      BufAcc[i] = p0 - 2.0 * p1 + p2;                                // backward second difference
     }
   return(rates_total);
  }

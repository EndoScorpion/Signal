// CalcProbe.mq4 - test helper: reads SafeChunkCalculusMQL4 via iCustom on every new bar and checks it updates.
#property strict
int nb = 0, nEmpty = 0, nChanged = 0; double lastV = 0; datetime lastBar = 0;
void OnTick()
  {
   if(Time[0] == lastBar) return; lastBar = Time[0]; nb++;
   double v = iCustom(Symbol(), 0, "SafeChunkCalculusMQL4", 2000, 0.6, 0, 1);   // velocity, last closed bar
   double a = iCustom(Symbol(), 0, "SafeChunkCalculusMQL4", 2000, 0.6, 1, 1);
   if(v == EMPTY_VALUE || a == EMPTY_VALUE) nEmpty++; else if(v != lastV) nChanged++;
   lastV = v;
   if(nb <= 3 || nb % 500 == 0) Print("PROBE bar ", TimeToString(Time[1]), " vel ", DoubleToString(v, 6), " acc ", DoubleToString(a, 6));
  }
void OnDeinit(const int r) { Print("PROBE SUMMARY bars ", nb, " empty ", nEmpty, " changed ", nChanged); }

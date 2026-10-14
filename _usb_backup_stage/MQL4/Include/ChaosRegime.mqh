//+------------------------------------------------------------------+
//| ChaosRegime.mqh  -  regime classifier, phase-space exhaustion,    |
//| closed-trade adaptive layer, break-even slide, circuit breaker.   |
//| Every feature is behind an input switch that defaults to false.   |
//| Formulas: see hst_out\ChaosRegime_MATH.txt (same text as below).  |
//|                                                                   |
//| HONEST NOTE: a layer that changes its own rules while trading     |
//| live will very likely overfit to recent noise. This file does NOT |
//| mutate itself. Changes to thresholds come only from the offline   |
//| test loop and ship as new default-off switches.                   |
//+------------------------------------------------------------------+
#property strict

// ---- switches (all default off) ----
extern bool   UseChaosRegime   = false; // classify regime by Hurst and use it as a filter / mode
extern int    CR_TF            = 15;    // timeframe in minutes for the Hurst window (5 or 15)
extern int    CR_Window        = 128;   // closes in the rolling Hurst window
extern double CR_TrendH        = 0.55;  // H above this = trending
extern double CR_RevertH       = 0.45;  // H below this = mean-reverting; between = no-memory (dead band)
extern bool   CR_FreezeNoMemory  = false; // no-memory regime (H near 0.5): no new sells
extern bool   CR_TrendOnly     = false; // only allow new sells in trending regime
extern bool   UseExhaustion    = false; // block new sells when down-move is exhausting (phase space)
extern int    PS_N             = 5;     // bars for velocity
extern double PS_Drop          = 0.5;   // exhausted when |v now| < PS_Drop * |v earlier|
extern bool   UseAdaptive      = false; // closed-trade adaptive lot fraction (bounded, gated)
extern int    AD_Window        = 30;    // closed trades used
extern double AD_LotMin        = 0.01;  // hard bounds for adaptive lot
extern double AD_LotMax        = 0.10;
extern bool   UseBESlide       = false; // move stop to entry + costs after a buffer profit
extern int    BE_Buffer        = 60;    // pts profit before the slide
extern int    BE_Costs         = 11;    // pts kept above entry: spread 2 + commission 9
extern bool   BE_HighFDOnly    = false; // only slide when Katz fractal dimension is high (choppy)
extern double BE_FDMin         = 1.8;
extern bool   UseCircuit       = false; // equity circuit breaker (cannot be changed by any adaptive code)
extern double CB_DailyDDPct    = 3.0;   // max loss today vs start-of-day equity, percent

// ---- state ----
int    crRegime = 0;          // 1 trend, -1 mean-reverting, 0 no-memory
double crH = 0.5;
datetime cbFrozenDay = 0; double cbDayEquity = 0; datetime cbDayStart = 0;

// Hurst by rescaled range. r_i = ln(C_i / C_{i-1}); for chunk size m in {8,16,32,64}:
// split r into k=floor(n/m) chunks; per chunk: mean mu, Y_t = sum_{s<=t}(r_s - mu), R = max Y - min Y,
// S = std dev of the chunk; RS_m = average of R/S over chunks. H = slope of ln(RS_m) on ln(m) (least squares).
double CR_Hurst(int tf, int win, int shift){
   double r[]; ArrayResize(r, win);
   for(int i=0;i<win;i++){ double a=iClose(Symbol(),tf,shift+i), b=iClose(Symbol(),tf,shift+i+1); if(a<=0||b<=0) return(0.5); r[win-1-i]=MathLog(a/b); }
   double xs[4], ys[4]; int np=0; int sz[4]={8,16,32,64};
   for(int q=0;q<4;q++){ int m=sz[q]; int k=win/m; if(k<1) continue; double sum=0; int cnt=0;
      for(int c=0;c<k;c++){ double mu=0; for(int t=0;t<m;t++) mu+=r[c*m+t]; mu/=m;
         double y=0, mx=-1e9, mn=1e9, v=0; for(int t2=0;t2<m;t2++){ y+=r[c*m+t2]-mu; mx=MathMax(mx,y); mn=MathMin(mn,y); v+=MathPow(r[c*m+t2]-mu,2); }
         double sd=MathSqrt(v/m); if(sd>0){ sum+=(mx-mn)/sd; cnt++; } }
      if(cnt>0){ xs[np]=MathLog(m); ys[np]=MathLog(sum/cnt); np++; } }
   if(np<2) return(0.5);
   double mxs=0,mys=0; for(int j=0;j<np;j++){ mxs+=xs[j]; mys+=ys[j]; } mxs/=np; mys/=np;
   double num=0,den=0; for(int j2=0;j2<np;j2++){ num+=(xs[j2]-mxs)*(ys[j2]-mys); den+=MathPow(xs[j2]-mxs,2); }
   return(den>0 ? num/den : 0.5);
}
// Katz fractal dimension over n closes: L = sum |C_i - C_{i-1}|, a = L/(n-1), d = max |C_i - C_first|,
// FD = log10(n-1) / (log10(n-1) + log10(d/L)).  ~1 smooth trend, ~2 very choppy.
double CR_Katz(int tf, int n, int shift){
   double L=0, d=0, c0=iClose(Symbol(),tf,shift+n-1);
   for(int i=0;i<n-1;i++){ L+=MathAbs(iClose(Symbol(),tf,shift+i)-iClose(Symbol(),tf,shift+i+1)); d=MathMax(d,MathAbs(iClose(Symbol(),tf,shift+i)-c0)); }
   if(L<=0||d<=0) return(1.5);
   return(MathLog10(n-1)/(MathLog10(n-1)+MathLog10(d/L)));
}
void CR_Update(){ crH=CR_Hurst(CR_TF,CR_Window,1); crRegime = crH>CR_TrendH ? 1 : (crH<CR_RevertH ? -1 : 0); }

// Phase space on M15 closes, ATR-normalised: v_t = (C_t - C_{t-n}) / n / ATR14; a_t = v_t - v_{t-n}.
// Down-move exhaustion (bad time to add sells): v_{t-n} < 0, |v_t| < PS_Drop*|v_{t-n}| and a_t > 0.
bool CR_DownExhausted(){
   double atr=iATR(Symbol(),PERIOD_M15,14,1); if(atr<=0) return(false); int n=PS_N;
   double v1=(iClose(Symbol(),PERIOD_M15,1)-iClose(Symbol(),PERIOD_M15,1+n))/n/atr;
   double v0=(iClose(Symbol(),PERIOD_M15,1+n)-iClose(Symbol(),PERIOD_M15,1+2*n))/n/atr;
   return(v0<0 && MathAbs(v1)<PS_Drop*MathAbs(v0) && (v1-v0)>0);
}
// Gate used by the EA's SellRegimeOK(). true = new sells allowed.
bool CR_SellAllowed(){
   if(UseChaosRegime){ CR_Update(); if(CR_FreezeNoMemory && crRegime==0) return(false); if(CR_TrendOnly && crRegime!=1) return(false); }
   if(UseExhaustion && CR_DownExhausted()) return(false);
   return(true);
}
// Adaptive lot from CLOSED trades only: wr = wins / last AD_Window closed trades of this magic.
// lot = AD_LotMin + (AD_LotMax-AD_LotMin) * clamp((wr-0.5)/0.2, 0, 1). Never above AD_LotMax.
double CR_AdaptiveLot(int mg, double baseLot){
   if(!UseAdaptive) return(baseLot);
   int n=0, w=0; for(int i=OrdersHistoryTotal()-1;i>=0 && n<AD_Window;i--){ if(!OrderSelect(i,SELECT_BY_POS,MODE_HISTORY)) continue; if(OrderMagicNumber()!=mg || OrderType()>OP_SELL) continue; n++; if(OrderProfit()+OrderCommission()+OrderSwap()>0) w++; }
   if(n<AD_Window) return(AD_LotMin);
   double k=MathMax(0,MathMin(1,((double)w/n-0.5)/0.2)); return(NormalizeDouble(AD_LotMin+(AD_LotMax-AD_LotMin)*k,2));
}
// Break-even slide: once profit >= BE_Buffer pts, stop goes to entry -/+ BE_Costs (locks costs). Optional high-FD condition.
void CR_BESlide(int mg){
   if(!UseBESlide) return; if(BE_HighFDOnly && CR_Katz(PERIOD_M15,64,1)<BE_FDMin) return;
   for(int i=OrdersTotal()-1;i>=0;i--){ if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue; if(OrderMagicNumber()!=mg || OrderSymbol()!=Symbol()) continue;
      if(OrderType()==OP_SELL && OrderOpenPrice()-Ask>=BE_Buffer*Point){ double ns=NormalizeDouble(OrderOpenPrice()-BE_Costs*Point,Digits); if(OrderStopLoss()==0 || OrderStopLoss()>ns+Point){ if(!OrderModify(OrderTicket(),OrderOpenPrice(),ns,OrderTakeProfit(),0)) Print("BE err ",GetLastError()); } }
      if(OrderType()==OP_BUY && Bid-OrderOpenPrice()>=BE_Buffer*Point){ double nb=NormalizeDouble(OrderOpenPrice()+BE_Costs*Point,Digits); if(OrderStopLoss()<nb-Point){ if(!OrderModify(OrderTicket(),OrderOpenPrice(),nb,OrderTakeProfit(),0)) Print("BE err ",GetLastError()); } } }
}
// Circuit breaker (fixed rule, no adaptive code may change it): if equity falls CB_DailyDDPct below the day's starting
// equity: close all positions, delete pendings, freeze new orders until the next server day. Returns true when frozen.
bool CR_Circuit(int mg){
   if(!UseCircuit) return(false); datetime d0=iTime(Symbol(),PERIOD_D1,0);
   if(d0!=cbDayStart){ cbDayStart=d0; cbDayEquity=AccountEquity(); }
   if(cbFrozenDay==d0) return(true);
   if(AccountEquity() < cbDayEquity*(1-CB_DailyDDPct/100.0)){
      for(int i=OrdersTotal()-1;i>=0;i--){ if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue; if(OrderMagicNumber()!=mg) continue;
         bool ok = OrderType()==OP_BUY ? OrderClose(OrderTicket(),OrderLots(),Bid,5) : OrderType()==OP_SELL ? OrderClose(OrderTicket(),OrderLots(),Ask,5) : OrderDelete(OrderTicket());
         if(!ok) Print("CB close err ",GetLastError()); }
      cbFrozenDay=d0; Print("CIRCUIT BREAKER: equity ",DoubleToStr(AccountEquity(),2)," below day start ",DoubleToStr(cbDayEquity,2)); return(true); }
   return(false);
}
string CR_LogLine(){ return("CR H "+DoubleToStr(crH,3)+" regime "+IntegerToString(crRegime)+" FD "+DoubleToStr(CR_Katz(PERIOD_M15,64,1),3)+" exh "+(CR_DownExhausted()?"1":"0")); }


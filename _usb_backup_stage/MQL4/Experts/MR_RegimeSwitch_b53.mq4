// b52 (2026-10-14): CLEAN-history EA. Clock: MT4 SERVER time = UTC+2, UTC+3 in US DST. Rollover spread spike is about 23:00-01:00 server time, so RollFrom=23..RollTo=1 (window wraps midnight). Warm-up check now counts H1 bars (regime SMA needs RegimePeriod H1 bars).
//+------------------------------------------------------------------+
//| MR_RegimeSwitch_b50.mq4 - z-score fade with long-regime switch    |
//| Copyright (c) Nasif Hossain <EndoScorpion@gmail.com>. All rights  |
//| reserved. Concept: mean-reversion fade (sell stretch up, buy      |
//| stretch down) with the H1 SMA regime deciding which side is       |
//| allowed. New clone branch; ancestors (b31, b42, b43) untouched.   |
//+------------------------------------------------------------------+
#property strict
extern int    MagicNumber    = 5350050;
extern double Lots           = 0.16;     // fixed lot (base sim sizes ~0.16 at 0.5% risk)
extern int    ZTF            = 15;       // timeframe (minutes) of the z-score
extern int    ZPeriod        = 10;       // closes in the z-score window
extern double ZTrigger       = 2.5;      // |z| needed to fade
extern int    HoldBars       = 48;       // time exit in ZTF bars
extern int    SideMode       = 0;        // 0 both, 1 sell only, 2 buy only
extern bool   UseRegime      = true;     // sell only below H1 SMA, buy only above it
extern int    RegimePeriod   = 2400;     // H1 SMA length
extern int    SLPts          = 600;      // stop loss in points (0 = none)
extern int    TPPts          = 0;        // take profit in points (0 = none)
extern double AtrCapPts      = 0;        // >0: skip when M15 ATR14 (points) above this
extern bool   BlockRollover  = true;     // skip server hours RollFrom..RollTo (spread spike)
extern int    RollFrom       = 23;
extern int    RollTo         = 1;
extern int    MaxSpreadPts   = 30;       // skip when spread above this (points)
extern int    TrailStartPts  = 0;        // >0: once profit reaches this many points, trail the stop (0 = no trailing)
extern int    TrailDistPts   = 250;      // trailing distance behind price in points
// b51: ZGate-style volume blend trigger, MMR gate, calm-tape gate (all default off). (c) Nasif Hossain <EndoScorpion@gmail.com>
extern bool   UseZBlend      = false;    // trigger uses Z = 0.7*z(price) + 0.3*z(tick volume) instead of price z only
extern bool   UseMmrGate     = false;    // require MmrMin <= MMR <= MmrMax (MMR = max/|min| of OLS slopes over 6, 12, 18 bars)
extern double MmrMin         = -1000;
extern double MmrMax         = 1000;
extern double CalmRvolMax    = 0;        // >0: skip when std-dev of 1-bar returns over 20 bars (points) is above this
extern double CalmPEMax      = 0;        // >0: skip when permutation entropy (order 3, 64 bars) is above this
datetime lastBar = 0;

int CountOpen(){ int c=0; for(int i=OrdersTotal()-1;i>=0;i--){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES) && OrderMagicNumber()==MagicNumber && OrderSymbol()==Symbol()){ c++; } } return(c); }

void TimeExit(){
   for(int i=OrdersTotal()-1;i>=0;i--){
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES) || OrderMagicNumber()!=MagicNumber || OrderSymbol()!=Symbol()){ continue; }
      if(OrderType()>OP_SELL){ continue; }
      if(TimeCurrent()-OrderOpenTime() >= HoldBars*ZTF*60){
         RefreshRates(); double px=(OrderType()==OP_BUY)?Bid:Ask;
         if(!OrderClose(OrderTicket(),OrderLots(),NormalizeDouble(px,Digits),20,clrNONE)){ Print("close err ",GetLastError()); } } } }

void TrailStops(){
   if(TrailStartPts<=0){ return; }
   for(int i=OrdersTotal()-1;i>=0;i--){
      if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES) || OrderMagicNumber()!=MagicNumber || OrderSymbol()!=Symbol() || OrderType()>OP_SELL){ continue; }
      double ns, cur=OrderStopLoss();
      if(OrderType()==OP_SELL){
         if(OrderOpenPrice()-Ask<TrailStartPts*Point){ continue; }
         ns=NormalizeDouble(Ask+TrailDistPts*Point,Digits);
         if(cur==0 || ns<cur){ if(!OrderModify(OrderTicket(),OrderOpenPrice(),ns,OrderTakeProfit(),0,clrNONE)){ Print("trail err ",GetLastError()); } }
      } else {
         if(Bid-OrderOpenPrice()<TrailStartPts*Point){ continue; }
         ns=NormalizeDouble(Bid-TrailDistPts*Point,Digits);
         if(cur==0 || ns>cur){ if(!OrderModify(OrderTicket(),OrderOpenPrice(),ns,OrderTakeProfit(),0,clrNONE)){ Print("trail err ",GetLastError()); } } } } }

double SlopePts(int w){ double sx=0,sy=0,sxy=0,sxx=0; for(int j=0;j<w;j++){ double y=iClose(Symbol(),ZTF,w-j); sx+=j; sy+=y; sxy+=j*y; sxx+=j*j; } double den=w*sxx-sx*sx; return(den==0?0:(w*sxy-sx*sy)/den/Point); }
double MmrNow(){ double a=SlopePts(6), b=SlopePts(12), c=SlopePts(18); double mx=MathMax(a,MathMax(b,c)), mn=MathMin(a,MathMin(b,c)); return(mn==0?EMPTY_VALUE:mx/MathAbs(mn)); }
double RvolNow(){ double sm=0,sq=0; for(int k=1;k<=20;k++){ double r=(iClose(Symbol(),ZTF,k)-iClose(Symbol(),ZTF,k+1))/Point; sm+=r; sq+=r*r; } double m=sm/20; return(MathSqrt(MathMax(0,sq/20-m*m))); }
double PermEntropyNow(){ int pc[8]; ArrayInitialize(pc,0); int tot=0; for(int s=1;s<=62;s++){ double pa=iClose(Symbol(),ZTF,s+2), pb=iClose(Symbol(),ZTF,s+1), pc2=iClose(Symbol(),ZTF,s); int code=(pa<pb?4:0)+(pb<pc2?2:0)+(pa<pc2?1:0); pc[code]++; tot++; } double h=0; for(int q=0;q<8;q++){ if(pc[q]>0){ double p=(double)pc[q]/tot; h-=p*MathLog(p); } } return(h/MathLog(6.0)); }
double ZScore(){
   if(UseZBlend){ int nb=MathMax(3,ZPeriod); double sp=0,qp=0,sv=0,qv=0; for(int k=1;k<=nb;k++){ double c=iClose(Symbol(),ZTF,k), v=(double)iVolume(Symbol(),ZTF,k); sp+=c; qp+=c*c; sv+=v; qv+=v*v; }
      double mp=sp/nb, mv=sv/nb, dp=MathSqrt(MathMax(0,qp/nb-mp*mp)), dv=MathSqrt(MathMax(0,qv/nb-mv*mv)); if(dp<=0||dv<=0){ return(0); }
      return(0.7*(iClose(Symbol(),ZTF,1)-mp)/dp+0.3*((double)iVolume(Symbol(),ZTF,1)-mv)/dv); }
   int n=MathMax(3,ZPeriod); double s=0,q=0;
   for(int k=1;k<=n;k++){ double c=iClose(Symbol(),ZTF,k); s+=c; q+=c*c; }
   double m=s/n, sd=MathSqrt(MathMax(0,q/n-m*m)); if(sd<=0){ return(0); }
   return((iClose(Symbol(),ZTF,1)-m)/sd); }

int OnInit(){ return(INIT_SUCCEEDED); }
// ---- b53 = b52 decisions UNCHANGED + SILENT REJECT AUDIT (add-only observer) ----
// Every raw z-trigger (|z|>=ZTrigger, any regime/gate) is logged to MQL4\Files\reject_audit_b53.csv with the FIRST gate that blocked it, or TAKEN.
// Columns: server_time (MT4 SERVER clock UTC+2, UTC+3 US DST), dir, z, bid, ask, spread_pts, gate. Outcome replay is offline (data\reject_audit.py): did the blocked signal later win?
// Never feeds back into trading. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>.
void RejLog(int dir,double z,string gate){
   int fh=FileOpen("reject_audit_b53.csv",FILE_CSV|FILE_READ|FILE_WRITE,',');
   if(fh<0){ return; }
   FileSeek(fh,0,SEEK_END);
   FileWrite(fh,TimeToStr(TimeCurrent(),TIME_DATE|TIME_MINUTES),dir,DoubleToStr(z,3),DoubleToStr(Bid,Digits),DoubleToStr(Ask,Digits),(int)MarketInfo(Symbol(),MODE_SPREAD),gate);
   FileClose(fh); }

int OnInit(){ return(INIT_SUCCEEDED); }

void OnTick(){
   if(iBars(Symbol(),PERIOD_H1)<RegimePeriod+10){ return; }
   TimeExit(); TrailStops();
   datetime bt=iTime(Symbol(),ZTF,0); if(bt==lastBar){ return; } lastBar=bt;   // evaluate once per new bar
   double z=ZScore(); int dir=0;
   if(z>=ZTrigger){ dir=-1; } else if(z<=-ZTrigger){ dir=1; }     // raw fade signal: -1 sell, +1 buy
   string why="";
   if(dir==0 && CountOpen()>0){ return; }
   if(dir==0){ return; }
   if(CountOpen()>0){ why="busy"; }
   else if(MarketInfo(Symbol(),MODE_SPREAD)>MaxSpreadPts){ why="spread"; }
   else if(BlockRollover && ((RollFrom<=RollTo)?(TimeHour(TimeCurrent())>=RollFrom && TimeHour(TimeCurrent())<=RollTo):(TimeHour(TimeCurrent())>=RollFrom || TimeHour(TimeCurrent())<=RollTo))){ why="rollover"; }
   else if(AtrCapPts>0 && iATR(Symbol(),PERIOD_M15,14,1)/Point>AtrCapPts){ why="atrcap"; }
   else if(UseMmrGate && (MmrNow()==EMPTY_VALUE || MmrNow()<MmrMin || MmrNow()>MmrMax)){ why="mmr"; }
   else if(CalmRvolMax>0 && RvolNow()>CalmRvolMax){ why="calm_rvol"; }
   else if(CalmPEMax>0 && PermEntropyNow()>CalmPEMax){ why="calm_pe"; }
   else if((dir<0 && SideMode==2) || (dir>0 && SideMode==1)){ why="sidemode"; }
   else if(UseRegime){ double ma=iMA(Symbol(),PERIOD_H1,RegimePeriod,0,MODE_SMA,PRICE_CLOSE,1), c1=iClose(Symbol(),PERIOD_H1,1); if(dir<0 && !(c1<ma)){ why="regime"; } if(dir>0 && !(c1>ma)){ why="regime"; } }
   if(why!=""){ RejLog(dir,z,why); return; }
   RejLog(dir,z,"TAKEN");
   int ty=(dir<0)?OP_SELL:OP_BUY;
   RefreshRates(); double pr=(ty==OP_SELL)?Bid:Ask, sl=0, tp=0;
   if(SLPts>0){ sl=(ty==OP_SELL)?pr+SLPts*Point:pr-SLPts*Point; }
   if(TPPts>0){ tp=(ty==OP_SELL)?pr-TPPts*Point:pr+TPPts*Point; }
   int t=OrderSend(Symbol(),ty,Lots,NormalizeDouble(pr,Digits),20,NormalizeDouble(sl,Digits),NormalizeDouble(tp,Digits),"b53",MagicNumber,0,clrNONE);
   if(t<0){ Print("OrderSend err ",GetLastError()); } }

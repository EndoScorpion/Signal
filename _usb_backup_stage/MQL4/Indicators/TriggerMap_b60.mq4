//+------------------------------------------------------------------+
//| TriggerMap_b60.mq4 - DISPLAY ONLY (no orders). Draws where the    |
//| next bar would trigger a mean-reversion fade, arrows where it     |
//| fired, and historical odds computed from this chart's own bars.   |
//| Copyright (c) Nasif Hossain <EndoScorpion@gmail.com>. All rights  |
//| reserved. Odds are past frequencies, NOT predictions. Attach to   |
//| an M15 chart. Backtest-derived: never live approval.              |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
extern int    ZPeriod       = 10;      // closes in the z-score window
extern double ZTrigger      = 2.5;     // |z| that triggers a fade
extern int    HoldBars      = 48;      // exit horizon in bars (odds are measured at this horizon)
extern bool   UseRegime     = true;    // sells only below the H1 SMA, buys only above it
extern int    RegimePeriod  = 2400;    // H1 SMA length
extern double CalmRvolMax   = 29.6;    // "calm tape": max std-dev of 1-bar returns over 20 bars (points)
extern double CalmAtrMax    = 45;      // "calm tape": max ATR14 (points)
extern double CostPts       = 6.4;     // commission 5 + typical spread, subtracted in the net odds
extern int    HistBars      = 60000;   // how much history the odds use (M15 bars)
extern int    ArrowBars     = 400;     // historical arrows drawn
extern bool   ShowFib       = true;    // Fibonacci retracement of the last FibBars-bar swing
extern int    FibBars       = 480;     // 5 days of M15
extern bool   ShowSR        = true;    // nearest two support / resistance levels from Williams fractals
extern bool   ShowTrend     = true;    // diagonal trendlines through the last two fractal highs / lows
extern int    FractalLookback = 400;   // bars searched for fractals
extern color  SellColor     = clrTomato;
extern color  BuyColor      = clrLimeGreen;
string P = "TM_"; datetime lastBar = 0; string oddsTxt[6]; int nOdds = 0;

double ZAt(int s){ double sm=0,sq=0; for(int k=0;k<ZPeriod;k++){ double c=Close[s+k]; sm+=c; sq+=c*c; } double m=sm/ZPeriod, sd=MathSqrt(MathMax(0,sq/ZPeriod-m*m)); return(sd>0?(Close[s]-m)/sd:0); }
double ZofC(double c){ double sm=c,sq=c*c; for(int k=1;k<ZPeriod;k++){ sm+=Close[k]; sq+=Close[k]*Close[k]; } double m=sm/ZPeriod, sd=MathSqrt(MathMax(0,sq/ZPeriod-m*m)); return(sd>0?(c-m)/sd:0); }
double RvolAt(int s){ double sm=0,sq=0; for(int k=0;k<20;k++){ double r=(Close[s+k]-Close[s+k+1])/Point; sm+=r; sq+=r*r; } double m=sm/20; return(MathSqrt(MathMax(0,sq/20-m*m))); }
bool RegimeAt(int s,int dir){
   if(!UseRegime){ return(true); }
   int h=iBarShift(NULL,PERIOD_H1,Time[s],false)+1; if(h<=0){ return(false); }
   double ma=iMA(NULL,PERIOD_H1,RegimePeriod,0,MODE_SMA,PRICE_CLOSE,h), c=iClose(NULL,PERIOD_H1,h);
   return(dir<0 ? c<ma : c>ma); }
bool CalmAt(int s){ return(RvolAt(s)<=CalmRvolMax && iATR(NULL,0,14,s)/Point<=CalmAtrMax); }

string Odds(int dir,bool calm){
   int n=0,w=0; double sum=0; int top=MathMin(HistBars,Bars-HoldBars-RegimePeriod-100);
   for(int s=top; s>HoldBars+1; s--){
      double z=ZAt(s);
      if((dir<0 && z>=ZTrigger) || (dir>0 && z<=-ZTrigger)){
         if(!RegimeAt(s,dir)){ continue; } if(calm && !CalmAt(s)){ continue; }
         double pts=dir*(Close[s-HoldBars]-Close[s])/Point; n++; if(pts>0){ w++; } sum+=pts; s-=HoldBars; } }
   if(n<5){ return("n="+IntegerToString(n)+" (too few)"); }
   return("n="+IntegerToString(n)+"  win "+DoubleToString(100.0*w/n,0)+"%  avg "+DoubleToString(sum/n,1)+" pts gross, "+DoubleToString(sum/n-CostPts,1)+" net"); }

void Txt(string name,string t,double price,datetime tm,color c){
   if(ObjectFind(0,name)<0){ ObjectCreate(0,name,OBJ_TEXT,0,tm,price); }
   ObjectSetString(0,name,OBJPROP_TEXT,t); ObjectSetInteger(0,name,OBJPROP_COLOR,c); ObjectSetInteger(0,name,OBJPROP_FONTSIZE,8);
   ObjectSetInteger(0,name,OBJPROP_TIME,tm); ObjectSetDouble(0,name,OBJPROP_PRICE,price); }
void Line(string name,double price,color c,int style){
   if(ObjectFind(0,name)<0){ ObjectCreate(0,name,OBJ_HLINE,0,0,price); }
   ObjectSetDouble(0,name,OBJPROP_PRICE,price); ObjectSetInteger(0,name,OBJPROP_COLOR,c); ObjectSetInteger(0,name,OBJPROP_STYLE,style); ObjectSetInteger(0,name,OBJPROP_WIDTH,1); }
void Lab(string name,string t,int y,color c){
   if(ObjectFind(0,name)<0){ ObjectCreate(0,name,OBJ_LABEL,0,0,0); ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER); ObjectSetInteger(0,name,OBJPROP_XDISTANCE,8); }
   ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y); ObjectSetString(0,name,OBJPROP_TEXT,t); ObjectSetInteger(0,name,OBJPROP_COLOR,c); ObjectSetInteger(0,name,OBJPROP_FONTSIZE,8); }
void Arrow(int s,int dir){
   string nm=P+"A"+IntegerToString((int)Time[s]); if(ObjectFind(0,nm)>=0){ return; }
   ObjectCreate(0,nm,OBJ_ARROW,0,Time[s],dir<0?High[s]+8*Point*10:Low[s]-8*Point*10);
   ObjectSetInteger(0,nm,OBJPROP_ARROWCODE,dir<0?234:233); ObjectSetInteger(0,nm,OBJPROP_COLOR,dir<0?SellColor:BuyColor); ObjectSetInteger(0,nm,OBJPROP_WIDTH,2); }

double Solve(int dir,double atr){
   double m0=0; for(int k=1;k<ZPeriod;k++){ m0+=Close[k]; } m0/=(ZPeriod-1);
   double lo=dir<0?m0:m0-30*atr, hi=dir<0?m0+30*atr:m0;
   double edge=dir<0?hi:lo; if(dir<0 && ZofC(edge)<ZTrigger){ return(0); } if(dir>0 && ZofC(edge)>-ZTrigger){ return(0); }
   for(int i=0;i<40;i++){ double mid=(lo+hi)/2, z=ZofC(mid);
      if(dir<0){ if(z>=ZTrigger){ hi=mid; } else { lo=mid; } } else { if(z<=-ZTrigger){ lo=mid; } else { hi=mid; } } }
   return(dir<0?hi:lo); }

void DrawFib(){
   if(!ShowFib){ return; }
   int fb=MathMax(10,MathMin(FibBars,5*1440/MathMax(1,Period()))); int hi=iHighest(NULL,0,MODE_HIGH,fb,1), lo=iLowest(NULL,0,MODE_LOW,fb,1); if(hi<0||lo<0){ return; }
   datetime t1,t2; double p1,p2;
   if(lo>hi){ t1=Time[lo]; p1=Low[lo]; t2=Time[hi]; p2=High[hi]; } else { t1=Time[hi]; p1=High[hi]; t2=Time[lo]; p2=Low[lo]; }
   string n=P+"FIB";
   if(ObjectFind(0,n)<0){ ObjectCreate(0,n,OBJ_FIBO,0,t1,p1,t2,p2); ObjectSetInteger(0,n,OBJPROP_COLOR,clrGray); ObjectSetInteger(0,n,OBJPROP_RAY_RIGHT,true); }
   else { ObjectSetInteger(0,n,OBJPROP_TIME1,t1); ObjectSetDouble(0,n,OBJPROP_PRICE1,p1); ObjectSetInteger(0,n,OBJPROP_TIME2,t2); ObjectSetDouble(0,n,OBJPROP_PRICE2,p2); } }

bool FracHi(int s){ return(High[s]>High[s-1] && High[s]>High[s-2] && High[s]>High[s+1] && High[s]>High[s+2]); }
bool FracLo(int s){ return(Low[s]<Low[s-1] && Low[s]<Low[s-2] && Low[s]<Low[s+1] && Low[s]<Low[s+2]); }

void DrawSR(){
   if(!ShowSR){ return; }
   double px=Bid, r1=0,r2=0,s1=0,s2=0; datetime tr=Time[0]+PeriodSeconds()*4;
   for(int s=3; s<FractalLookback && s+2<Bars; s++){
      if(FracHi(s)){ double h=High[s]; if(h>px){ if(r1==0||h<r1){ if(h!=r1){ r2=r1; r1=h; } } else if(h!=r1 && (r2==0||h<r2)){ r2=h; } } }
      if(FracLo(s)){ double l=Low[s]; if(l<px){ if(s1==0||l>s1){ if(l!=s1){ s2=s1; s1=l; } } else if(l!=s1 && (s2==0||l>s2)){ s2=l; } } } }
   if(r1>0){ Line(P+"R1",r1,clrOrange,STYLE_DASH); Txt(P+"R1t","R1 "+DoubleToString(r1,Digits)+" (+"+DoubleToString((r1-px)/Point,0)+")",r1,tr,clrOrange); }
   if(r2>0){ Line(P+"R2",r2,clrOrange,STYLE_DOT);  Txt(P+"R2t","R2 "+DoubleToString(r2,Digits),r2,tr,clrOrange); }
   if(s1>0){ Line(P+"S1",s1,clrDodgerBlue,STYLE_DASH); Txt(P+"S1t","S1 "+DoubleToString(s1,Digits)+" (-"+DoubleToString((px-s1)/Point,0)+")",s1,tr,clrDodgerBlue); }
   if(s2>0){ Line(P+"S2",s2,clrDodgerBlue,STYLE_DOT);  Txt(P+"S2t","S2 "+DoubleToString(s2,Digits),s2,tr,clrDodgerBlue); } }

void TrendLine(string nm,int sOld,int sNew,bool hi,color c){
   double pA=hi?High[sOld]:Low[sOld], pB=hi?High[sNew]:Low[sNew]; datetime tA=Time[sOld], tB=Time[sNew];
   if(ObjectFind(0,nm)<0){ ObjectCreate(0,nm,OBJ_TREND,0,tA,pA,tB,pB); ObjectSetInteger(0,nm,OBJPROP_RAY_RIGHT,true); ObjectSetInteger(0,nm,OBJPROP_WIDTH,1); }
   ObjectSetInteger(0,nm,OBJPROP_TIME1,tA); ObjectSetDouble(0,nm,OBJPROP_PRICE1,pA); ObjectSetInteger(0,nm,OBJPROP_TIME2,tB); ObjectSetDouble(0,nm,OBJPROP_PRICE2,pB); ObjectSetInteger(0,nm,OBJPROP_COLOR,c);
   double proj=pB+(pB-pA)*(double)(Time[0]-tB)/(double)(tB-tA);
   Txt(nm+"t",(hi?"down/up resistance now ":"trend support now ")+DoubleToString(proj,Digits)+" ("+DoubleToString((proj-Bid)/Point,0)+" pts)",proj,Time[0]+PeriodSeconds()*4,c); }

void DrawTrend(){
   if(!ShowTrend){ return; }
   int h1=0,h2=0,l1=0,l2=0;
   for(int s=3; s<FractalLookback && s+2<Bars; s++){
      if(FracHi(s)){ if(h1==0){ h1=s; } else if(h2==0){ h2=s; } }
      if(FracLo(s)){ if(l1==0){ l1=s; } else if(l2==0){ l2=s; } }
      if(h2>0 && l2>0){ break; } }
   if(h2>0){ TrendLine(P+"TH",h2,h1,true,High[h1]<High[h2]?clrTomato:clrGold); }
   if(l2>0){ TrendLine(P+"TL",l2,l1,false,Low[l1]>Low[l2]?clrLimeGreen:clrOrchid); } }

void Draw(){
   double atr=iATR(NULL,0,14,1); if(atr<=0){ return; }
   bool sellOK=RegimeAt(1,-1), buyOK=RegimeAt(1,1), calm=CalmAt(1);
   double sp=Solve(-1,atr), bp=Solve(1,atr); datetime tr=Time[0]+PeriodSeconds()*4;
   if(sp>0){ Line(P+"S",sp,SellColor,sellOK?STYLE_SOLID:STYLE_DOT); Txt(P+"St","SELL fade @ "+DoubleToString(sp,Digits)+" (+"+DoubleToString((sp-Bid)/Point,0)+" pts)"+(sellOK?"":" [regime blocks]"),sp,tr,SellColor); }
   if(bp>0){ Line(P+"B",bp,BuyColor,buyOK?STYLE_SOLID:STYLE_DOT); Txt(P+"Bt","BUY fade @ "+DoubleToString(bp,Digits)+" (-"+DoubleToString((Bid-bp)/Point,0)+" pts)"+(buyOK?"":" [regime blocks]"),bp,tr,BuyColor); }
   Lab(P+"L0","TriggerMap b60 - display only, past odds not predictions",14,clrSilver);
   Lab(P+"L1","Regime (H1 SMA "+IntegerToString(RegimePeriod)+"): sells "+(sellOK?"ALLOWED":"blocked")+", buys "+(buyOK?"ALLOWED":"blocked"),30,clrSilver);
   Lab(P+"L2","Tape now: rvol20 "+DoubleToString(RvolAt(1),1)+" pts, ATR "+DoubleToString(atr/Point,0)+" pts -> "+(calm?"CALM":"not calm")+"   z now "+DoubleToString(ZAt(1),2),46,calm?clrLimeGreen:clrOrange);
   Lab(P+"L3","SELL fade odds (all): "+oddsTxt[0],62,SellColor); Lab(P+"L4","SELL fade odds (calm only): "+oddsTxt[1],78,SellColor);
   Lab(P+"L7","Lines: ORANGE dash/dot = resistance R1/R2, BLUE = support S1/S2 (Williams fractals); GRAY = Fibonacci of last 5-day swing; thin diagonals = trendlines",126,clrSilver);
   Lab(P+"L5","BUY fade odds (all): "+oddsTxt[2],94,BuyColor); Lab(P+"L6","BUY fade odds (calm only): "+oddsTxt[3],110,BuyColor);
   DrawFib(); DrawSR(); DrawTrend(); }

int OnInit(){ IndicatorShortName("TriggerMap b60"); return(INIT_SUCCEEDED); }
void OnDeinit(const int reason){ ObjectsDeleteAll(0,P); }
int OnCalculate(const int rates_total,const int prev_calculated,const datetime &time[],const double &open[],const double &high[],const double &low[],const double &close[],const long &tick_volume[],const long &volume[],const int &spread[]){
   if(rates_total<RegimePeriod+HoldBars+200){ return(0); }
   if(nOdds==0){ oddsTxt[0]=Odds(-1,false); oddsTxt[1]=Odds(-1,true); oddsTxt[2]=Odds(1,false); oddsTxt[3]=Odds(1,true); nOdds=1;
      for(int s=ArrowBars; s>=1; s--){ double z=ZAt(s); if(z>=ZTrigger && RegimeAt(s,-1)){ Arrow(s,-1); } if(z<=-ZTrigger && RegimeAt(s,1)){ Arrow(s,1); } } }
   if(Time[0]!=lastBar){ lastBar=Time[0]; double z1=ZAt(1); if(z1>=ZTrigger && RegimeAt(1,-1)){ Arrow(1,-1); } if(z1<=-ZTrigger && RegimeAt(1,1)){ Arrow(1,1); } }
   Draw(); return(rates_total); }




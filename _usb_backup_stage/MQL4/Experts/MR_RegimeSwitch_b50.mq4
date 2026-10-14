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
extern int    RollFrom       = 20;
extern int    RollTo         = 22;
extern int    MaxSpreadPts   = 30;       // skip when spread above this (points)
extern int    TrailStartPts  = 0;        // >0: once profit reaches this many points, trail the stop (0 = no trailing)
extern int    TrailDistPts   = 250;      // trailing distance behind price in points
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

double ZScore(){
   int n=MathMax(3,ZPeriod); double s=0,q=0;
   for(int k=1;k<=n;k++){ double c=iClose(Symbol(),ZTF,k); s+=c; q+=c*c; }
   double m=s/n, sd=MathSqrt(MathMax(0,q/n-m*m)); if(sd<=0){ return(0); }
   return((iClose(Symbol(),ZTF,1)-m)/sd); }

int OnInit(){ return(INIT_SUCCEEDED); }

void OnTick(){
   if(Bars<RegimePeriod+10){ return; }
   TimeExit(); TrailStops();
   datetime bt=iTime(Symbol(),ZTF,0); if(bt==lastBar){ return; } lastBar=bt;   // evaluate once per new bar
   if(CountOpen()>0){ return; }
   if(MarketInfo(Symbol(),MODE_SPREAD)>MaxSpreadPts){ return; }
   if(BlockRollover){ int h=TimeHour(TimeCurrent()); if(h>=RollFrom && h<=RollTo){ return; } }
   if(AtrCapPts>0 && iATR(Symbol(),PERIOD_M15,14,1)/Point>AtrCapPts){ return; }
   double z=ZScore(); bool below=true, above=true;
   if(UseRegime){ double ma=iMA(Symbol(),PERIOD_H1,RegimePeriod,0,MODE_SMA,PRICE_CLOSE,1), c1=iClose(Symbol(),PERIOD_H1,1); below=(c1<ma); above=(c1>ma); }
   int ty=-1;
   if(z>=ZTrigger && SideMode!=2 && below){ ty=OP_SELL; }
   if(z<=-ZTrigger && SideMode!=1 && above){ ty=OP_BUY; }
   if(ty<0){ return; }
   RefreshRates(); double pr=(ty==OP_SELL)?Bid:Ask, sl=0, tp=0;
   if(SLPts>0){ sl=(ty==OP_SELL)?pr+SLPts*Point:pr-SLPts*Point; }
   if(TPPts>0){ tp=(ty==OP_SELL)?pr-TPPts*Point:pr+TPPts*Point; }
   int t=OrderSend(Symbol(),ty,Lots,NormalizeDouble(pr,Digits),20,NormalizeDouble(sl,Digits),NormalizeDouble(tp,Digits),"b50",MagicNumber,0,clrNONE);
   if(t<0){ Print("OrderSend err ",GetLastError()); } }

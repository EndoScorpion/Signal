//+------------------------------------------------------------------+
//| MR_RegimeSwitch_b50.mq5 - MT5 port of the b50 z-score fade EA     |
//| Copyright (c) Nasif Hossain <EndoScorpion@gmail.com>. All rights  |
//| reserved. Sell below / buy above the long H1 SMA regime, fade a   |
//| |z| stretch, time exit, optional stop and trailing stop.         |
//| Backtest-only until proven; never live approval.                  |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>
input long   MagicNumber   = 5350050;
input double Lots          = 0.16;
input ENUM_TIMEFRAMES ZTF  = PERIOD_M15;
input int    ZPeriod       = 10;
input double ZTrigger      = 2.5;
input int    HoldBars      = 48;
input int    SideMode      = 0;        // 0 both, 1 sell only, 2 buy only
input bool   UseRegime     = true;
input int    RegimePeriod  = 2400;     // H1 SMA length
input int    SLPts         = 600;
input int    TPPts         = 0;
input double AtrCapPts     = 0;
input bool   BlockRollover = true;
input int    RollFrom      = 20;
input int    RollTo        = 22;
input int    MaxSpreadPts  = 30;
input int    TrailStartPts = 0;
input int    TrailDistPts  = 250;
CTrade trade; datetime lastBar=0; int hMA=INVALID_HANDLE, hATR=INVALID_HANDLE;

int OnInit(){
   trade.SetExpertMagicNumber(MagicNumber);
   hMA=iMA(_Symbol,PERIOD_H1,RegimePeriod,0,MODE_SMA,PRICE_CLOSE); hATR=iATR(_Symbol,PERIOD_M15,14);
   return((hMA==INVALID_HANDLE||hATR==INVALID_HANDLE)?INIT_FAILED:INIT_SUCCEEDED); }

int CountMine(){ int c=0; for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(t>0 && PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==MagicNumber){ c++; } } return(c); }

void Manage(){
   for(int i=PositionsTotal()-1;i>=0;i--){
      ulong t=PositionGetTicket(i); if(t==0 || PositionGetString(POSITION_SYMBOL)!=_Symbol || PositionGetInteger(POSITION_MAGIC)!=MagicNumber){ continue; }
      long type=PositionGetInteger(POSITION_TYPE); double open=PositionGetDouble(POSITION_PRICE_OPEN), sl=PositionGetDouble(POSITION_SL), tp=PositionGetDouble(POSITION_TP);
      if(TimeCurrent()-(datetime)PositionGetInteger(POSITION_TIME) >= HoldBars*PeriodSeconds(ZTF)){ trade.PositionClose(t); continue; }
      if(TrailStartPts<=0){ continue; }
      double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      if(type==POSITION_TYPE_SELL){ if((open-ask)/_Point<TrailStartPts){ continue; } double ns=NormalizeDouble(ask+TrailDistPts*_Point,_Digits); if(sl==0||ns<sl){ trade.PositionModify(t,ns,tp); } }
      else { if((bid-open)/_Point<TrailStartPts){ continue; } double ns=NormalizeDouble(bid-TrailDistPts*_Point,_Digits); if(sl==0||ns>sl){ trade.PositionModify(t,ns,tp); } } } }

double ZScore(){
   int n=MathMax(3,ZPeriod); double s=0,q=0;
   for(int k=1;k<=n;k++){ double c=iClose(_Symbol,ZTF,k); s+=c; q+=c*c; }
   double m=s/n, sd=MathSqrt(MathMax(0,q/n-m*m)); if(sd<=0){ return(0); }
   return((iClose(_Symbol,ZTF,1)-m)/sd); }

void OnTick(){
   if(Bars(_Symbol,PERIOD_H1)<RegimePeriod+10){ return; }
   Manage();
   datetime bt=iTime(_Symbol,ZTF,0); if(bt==lastBar){ return; } lastBar=bt;
   if(CountMine()>0){ return; }
   if(SymbolInfoInteger(_Symbol,SYMBOL_SPREAD)>MaxSpreadPts){ return; }
   MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
   if(BlockRollover && dt.hour>=RollFrom && dt.hour<=RollTo){ return; }
   double atr[1]; if(CopyBuffer(hATR,0,1,1,atr)!=1){ return; }
   if(AtrCapPts>0 && atr[0]/_Point>AtrCapPts){ return; }
   double z=ZScore(); bool below=true, above=true;
   if(UseRegime){ double ma[1]; if(CopyBuffer(hMA,0,1,1,ma)!=1){ return; } double c1=iClose(_Symbol,PERIOD_H1,1); below=(c1<ma[0]); above=(c1>ma[0]); }
   bool sell=(z>=ZTrigger && SideMode!=2 && below), buy=(z<=-ZTrigger && SideMode!=1 && above);
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   if(sell){ double sl=SLPts>0?NormalizeDouble(bid+SLPts*_Point,_Digits):0, tp=TPPts>0?NormalizeDouble(bid-TPPts*_Point,_Digits):0; trade.Sell(Lots,_Symbol,bid,sl,tp,"b50"); }
   else if(buy){ double sl=SLPts>0?NormalizeDouble(ask-SLPts*_Point,_Digits):0, tp=TPPts>0?NormalizeDouble(ask+TPPts*_Point,_Digits):0; trade.Buy(Lots,_Symbol,ask,sl,tp,"b50"); } }

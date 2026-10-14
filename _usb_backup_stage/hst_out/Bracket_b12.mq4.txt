//+------------------------------------------------------------------+
//| Bracket_b12.mq4 - daily range breakout bracket (buy stop + sell stop), OCO
//| Test EA. Flat before midnight (no swap). Spread filter, Friday block.
//+------------------------------------------------------------------+
#property strict
input double Lots        = 0.01;
input int    StartHour   = 7;     // server hour: place bracket at this bar open
input int    RangeBars   = 8;     // bars before StartHour that form the range
input int    OffsetPts   = 20;    // points beyond range high/low
input double TPmult      = 1.0;   // TP = range * TPmult from entry
input double SLmult      = 1.0;   // SL = range * SLmult from entry (1.0 = other side)
input int    MinRangePts = 80;
input int    MaxRangePts = 400;
input int    Layers      = 1;     // extra stop orders stepped by half range further out
input int    ExpireHour  = 12;    // delete unfilled pendings
input int    CloseHour   = 21;    // close open trades (before midnight swap)
input int    MaxSpread   = 20;    // points
input int    FridayStop  = 16;    // no new bracket Friday at/after this hour
input int    Magic       = 1212;
datetime lastDay=0;

int OnInit(){ return(INIT_SUCCEEDED); }

int CountType(int t){ int n=0; for(int i=OrdersTotal()-1;i>=0;i--) if(OrderSelect(i,SELECT_BY_POS) && OrderMagicNumber()==Magic && OrderSymbol()==Symbol() && OrderType()==t) n++; return n; }

void DeleteType(int t){ for(int i=OrdersTotal()-1;i>=0;i--) if(OrderSelect(i,SELECT_BY_POS) && OrderMagicNumber()==Magic && OrderSymbol()==Symbol() && OrderType()==t) if(!OrderDelete(OrderTicket())) Print("del err ",GetLastError()); }

void CloseAll(){ for(int i=OrdersTotal()-1;i>=0;i--) if(OrderSelect(i,SELECT_BY_POS) && OrderMagicNumber()==Magic && OrderSymbol()==Symbol()){
   if(OrderType()==OP_BUY)  { if(!OrderClose(OrderTicket(),OrderLots(),Bid,5)) Print("close err ",GetLastError()); }
   else if(OrderType()==OP_SELL) { if(!OrderClose(OrderTicket(),OrderLots(),Ask,5)) Print("close err ",GetLastError()); }
   else if(!OrderDelete(OrderTicket())) Print("del err ",GetLastError()); } }

void OnTick(){
   int h=TimeHour(TimeCurrent());
   // OCO: once one side is filled, remove the other side's pendings
   if(CountType(OP_BUY)>0)  DeleteType(OP_SELLSTOP);
   if(CountType(OP_SELL)>0) DeleteType(OP_BUYSTOP);
   if(h>=ExpireHour){ DeleteType(OP_BUYSTOP); DeleteType(OP_SELLSTOP); }
   if(h>=CloseHour){ CloseAll(); return; }
   datetime today=iTime(NULL,PERIOD_D1,0);
   if(today==lastDay || h!=StartHour) return;
   if(DayOfWeek()==5 && h>=FridayStop) return;
   if((Ask-Bid)/Point>MaxSpread) return;
   lastDay=today;
   double hi=High[iHighest(NULL,0,MODE_HIGH,RangeBars,1)], lo=Low[iLowest(NULL,0,MODE_LOW,RangeBars,1)];
   double rng=hi-lo; if(rng/Point<MinRangePts || rng/Point>MaxRangePts) return;
   double off=OffsetPts*Point, stp=MarketInfo(Symbol(),MODE_STOPLEVEL)*Point;
   for(int k=0;k<Layers;k++){
      double eb=NormalizeDouble(hi+off+k*rng*0.5,Digits), es=NormalizeDouble(lo-off-k*rng*0.5,Digits);
      if(eb-Ask>stp) if(OrderSend(Symbol(),OP_BUYSTOP,Lots,eb,3,NormalizeDouble(eb-rng*SLmult,Digits),NormalizeDouble(eb+rng*TPmult,Digits),"b12",Magic,0,clrBlue)<0) Print("bs err ",GetLastError());
      if(Bid-es>stp) if(OrderSend(Symbol(),OP_SELLSTOP,Lots,es,3,NormalizeDouble(es+rng*SLmult,Digits),NormalizeDouble(es-rng*TPmult,Digits),"b12",Magic,0,clrRed)<0) Print("ss err ",GetLastError());
   }
}

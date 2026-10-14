//+------------------------------------------------------------------+
//| MonthlyTouch_b61.mq4 - SIGNAL-ONLY helper (NEVER trades)         |
//| Reminds when it is a cheap/calm moment to place the monthly      |
//| minimum 0.01-lot trade required by FXOpen (no trade this month   |
//| = penalty). You place and close the trade yourself.              |
//| CLOCK: MT4 SERVER time (UTC+2, UTC+3 in US DST). All hours below |
//| are server hours. Rollover spread spike = 23:00-01:00 server.    |
//| Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>              |
//+------------------------------------------------------------------+
#property copyright "Nasif Hossain <EndoScorpion@gmail.com>"
#property strict
extern int    GoodFromHour   = 10;     // server hour window start (London/NY liquid, tight spread)
extern int    GoodToHour     = 18;     // server hour window end (inclusive)
extern int    MaxSpreadPts   = 2;      // alert only when bid/ask spread <= this (points, 5-digit)
extern double CalmAtrRatio   = 1.0;    // M15 ATR14 must be <= this x its 100-bar average (calm tape)
extern int    UrgentDaysLeft = 3;      // in the last N days of the month: ignore calm/hour filters, only spread matters
extern bool   UseAlert       = true;   // pop-up
extern bool   UsePush        = true;   // phone push (needs MetaQuotes ID in Tools>Options>Notifications)
extern int    MinRepeatMin   = 120;    // minutes between repeat alerts
datetime lastAlert=0, lastBar=0;
int OnInit(){ EventSetTimer(30); return(INIT_SUCCEEDED); }
void OnDeinit(const int r){ EventKillTimer(); Comment(""); }
bool DoneThisMonth(){
   datetime ms=StrToTime(TimeToStr(TimeCurrent(),TIME_DATE)); int d=TimeDay(ms)-1; ms-=d*86400;      // first day 00:00 server
   for(int i=OrdersTotal()-1;i>=0;i--) if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES) && OrderType()<=OP_SELL && OrderOpenTime()>=ms) return(true);
   for(int j=OrdersHistoryTotal()-1;j>=0;j--) if(OrderSelect(j,SELECT_BY_POS,MODE_HISTORY) && OrderType()<=OP_SELL && OrderOpenTime()>=ms) return(true);
   return(false); }
double AtrRatio(){ double a=iATR(Symbol(),PERIOD_M15,14,1), s=0; for(int k=1;k<=100;k++) s+=iATR(Symbol(),PERIOD_M15,14,k); s/=100.0; return(s>0?a/s:9); }
int DaysLeft(){ int y=TimeYear(TimeCurrent()), m=TimeMonth(TimeCurrent()); datetime nm=StrToTime(StringFormat("%d.%02d.01",(m==12?y+1:y),(m==12?1:m+1))); return((int)((nm-TimeCurrent())/86400)); }
void OnTimer(){
   bool done=DoneThisMonth(); int left=DaysLeft(); double sp=MarketInfo(Symbol(),MODE_SPREAD); int h=TimeHour(TimeCurrent()); int dow=TimeDayOfWeek(TimeCurrent());
   double ar=AtrRatio(); bool urgent=(left<=UrgentDaysLeft);
   bool hourOk=(h>=GoodFromHour && h<=GoodToHour && dow>=1 && dow<=4);     // Mon-Thu, avoids Friday close and Sunday open gaps
   bool calm=(ar<=CalmAtrRatio); bool spreadOk=(sp<=MaxSpreadPts);
   string st=done?"DONE this month - no action needed":("NOT DONE - "+IntegerToString(left)+" days left"+(urgent?" (URGENT)":""));
   Comment("MonthlyTouch_b61 (signal only)\nMonthly trade: ",st,"\nSpread ",sp," pts | ATR ratio ",DoubleToStr(ar,2),(calm?" calm":" busy")," | server hour ",h,(hourOk?" in window":" outside window"));
   if(done) return;
   bool good = spreadOk && (urgent || (hourOk && calm));
   if(!good) return;
   if(TimeCurrent()-lastAlert < MinRepeatMin*60) return;
   lastAlert=TimeCurrent();
   string msg="MonthlyTouch: good moment for your monthly minimum trade on "+Symbol()+": spread "+DoubleToStr(sp,0)+" pts, "+(calm?"calm tape":"busy tape")+", server "+TimeToStr(TimeCurrent(),TIME_MINUTES)+". Place 0.01 lot (any side), close after a few minutes. Est. cost ~ spread + commission ~"+DoubleToStr(sp+8,0)+" pts (~$0.10).";
   if(UseAlert) Alert(msg); if(UsePush) SendNotification(msg); Print(msg); }
void OnTick(){}

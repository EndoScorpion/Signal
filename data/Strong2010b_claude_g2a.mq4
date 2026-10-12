//---- Strong2010b_claude_g2a : g1a + no sell-stop/ladder placement 12-16 and 20-24 server time. Based on b20legs_g1a : clone of Strong2010b_claude_b20 (legs_2526 build), SellOnly=1
//objective: improve odds. 

// old 2011a 524 98.28%

//new config 

//2011a jan 1 to apr 27 215 98.60% 


//+------------------------------------------------------------------+
//|                                              Mar 3 2019 Test.mq4 |
//|                                               Copyright 2019, NH |
//|                                              https://www.nhi.com |
//+------------------------------------------------------------------+
#property copyright "Copyright Â© 2019, Nasif Hossain" 
#property link      "https://www.nhi.com"
#property version   "1.00-claude_b4"
#property strict

//--- input parameters 

 //---- Behavioral Switches, triggers, filts, etc. 
 
extern bool SwapHelp=1; 

// need 2 different kinds of swap help

extern int SwapHour=22;

extern bool FriBlock=1;

extern int FriHour=19;

extern double tp=7; 

//---- claude_b1 additions (original logic above/below is unchanged) ----
// BranchMode: 0 = original entries, just LOG branch flags (one run gives all branch data)
//             1 = require Branch A (M15 SARA/PRV >= BrA_SaraPrv)
//             2 = require Branch B (M5 SARA >= BrB_M5Sara AND M15 ROA >= BrB_M15Roa)
//             3 = require Branch C (M15 StochK >= BrC_M15K AND H1 K-D >= BrC_H1KD)
//             4 = require any one of A, B, C
extern int    BranchMode=0;
extern double BrA_SaraPrv=0.22;
extern double BrB_M5Sara=51.2;
extern double BrB_M15Roa=9.32;
extern double BrC_M15K=90.2;
extern double BrC_H1KD=14.5;
// Flat entry (new, untested): buy after low/flat slopes, small MMR, low range & volume, stoch mid, green close. Comment "4".
extern bool   UseFlatEntry=1;
// M15 EMA20 slope average over 6 bars, pts/bar
extern double FlatSlopeMin=-3;
extern double FlatSlopeMax=3;
// min/max close-slope ratio over 12 bars; more negative = big recent down bar
extern double FlatMmrMin=-1.5;
// bar volume / 20-bar average
extern double FlatVolRelMax=1;
extern double FlatKMin=20, FlatKMax=70;
// Signal-app rules as M15 buy entries (tested on history 2011/12/19/21: both LOSE more than random with this exit; default OFF)
// Trailing stop (replay of your 2011-12 and 2019 entries on M5 bars: trail 5 after +10 turned them positive; needs a real tester run)
// 1 = after price is TrailStart pts up, keep SL TrailStep pts below the best Bid; TP stays as is
extern bool   UseTrail=0;
extern int    TrailStart=10;
extern int    TrailStep=5;
// 1 = when trailing starts, move TP far away so the trail decides the exit
extern bool   TrailRemoveTP=1;
// Clone branches of the ORIGINAL entry with a different first slope threshold (original is 2). Comment stays "" (Type 0).
// smaller = more entries (try 1, 1.5), larger = fewer (try 3, 4)
extern double EntrySlopeMin=2;
// S2: RSI(14) < 25 on closed M15 bar. Comment "5".
extern bool   UseS2Entry=0;
// S4: close below lower Bollinger(20,2) and raw Stoch(14) < 10, EMA50 > EMA200. Comment "6".
extern bool   UseS4Entry=0;
// ---- b5 INVERTED branches. Replay of your 2011-12 and 2019 entries on M5 bars: sells after a FAILED buy were positive
// in 2011, 2012 and 2019 (random sells with the same exits were not). Both default OFF; buys stay exactly as before.
// Sell stop SellStopDist pts under the Bid right after every buy; expires after SellStopExpiryMin minutes. Comment "7".
extern bool   UseSellStop=1;
extern int    SellStopDist=20;
extern int    SellStopTP=300;
extern int    SellStopSL=300;
extern int    SellStopExpiryMin=120;
// Hedge: when an open buy is HedgeTrigger pts under water, open one market sell for it. Comment "8".
extern bool   UseHedgeSell=1;
extern int    HedgeTrigger=30;
extern int    HedgeTP=300;
extern int    HedgeSL=300;
int hedgedTicket=0;
// ---- b6 ratio log: after every buy, print the raw building blocks of your ratios (slope, accel, rate of accel, stoch position,
// ATR range, volume, height = high-close, distance of close above the SMA) for M1/M5/M15/H1 x SMA period 2/5/10/15 x the last
// 5 CLOSED candles. One "RLOG #ticket tf pd" line per tf/pd; the hash tables (SP, AP, SR, AR, SSR, ASR, ACH, SH, MMR, SARA/PRV)
// are built from these lines offline. Each line ends with || DFL20 DFL50 bars-since-stoch<=20. 16 lines per buy.
extern bool   UseRatioLog=1;
// ---- b7 SELL REGIME: the sell branches (7 and 8) only when the last CLOSED H1 bar closed below the H1 SMA(1200), about 50 trading days.
// Real tester runs: sells below that line were positive in 2019 (+21.8/trade, 535), 2017 (+38.9, 119), 2020 (+78.7, 65) and the
// 2011-12 replay; sells above it lost in 2017 and 2020. 1 = on (default), 0 = sells in any regime as in b6. SellRegimePeriod = SMA length.
extern bool   UseSellRegime=1;
// b13: quiet-market gate for sells. When on, sell stops, ladder, hedge and bracket sells are placed only if H1 20-bar range over 20*ATR14 is below QuietRR and M15 ADX14 is below QuietADX (closed bars)
extern bool   UseQuietGate=0;
// b13: maximum H1 range ratio for the quiet gate
extern double QuietRR=0.17;
// b13: maximum M15 ADX for the quiet gate
extern double QuietADX=17.5;
// b14: park the buys. The buy signal still fires, but no buy order is sent; the sell stop and ladder are placed from the signal instead
extern bool   UseParkBuys=1;
// b14: minutes a parked (virtual) buy counts as open, so new buy signals are throttled like a real open buy
extern int    ParkHoldMin=3;
datetime parkUntil=0; int parkN=0;
// b15: magic number of this EA copy. Give each clone on its own chart a different value
extern int    MagicNumber=5348893;
// b15: risk guard on every new order (buys, sell stops, ladder, hedge, news orders)
extern bool   UseRiskGuard=0;
// b15: maximum open plus pending orders on this symbol
extern int    MaxOpenOrders=8;
// b15: maximum total stop-loss risk of all orders, percent of balance
extern double MaxRiskPct=10;
// b15: free margin that must remain after a new order, percent of balance
extern double MarginReservePct=50;
// b15: no new orders for the day once realised loss today reaches this percent of balance (0 = off)
extern double DailyLossPct=5;
// b15: size orders from risk instead of fixed 0.01 lot
extern bool   UseLotSim=0;
// b15: simulated deposit in USD (0 = use AccountBalance)
extern double SimDeposit=0;
// b15: simulated leverage (0 = use AccountLeverage)
extern int    SimLeverage=0;
// b15: percent of balance risked per order when UseLotSim is on
extern double RiskPct=0.5;
// b15: largest lot size allowed when UseLotSim is on
extern double MaxLots=0.5;
// b15: percent of balance that all margin may use when UseLotSim is on
extern double MarginUsePct=30;
// b15: no sell stops, ladder, hedge or bracket sells within this many hours of an NFP, CPI or FOMC release
extern bool   UseNewsDayBlock=0;
// b15: hours either side of a release for the news day block
extern int    NewsBlockHours=24;
// b15: CPI straddle: a buy stop and a sell stop placed two minutes before each CPI release
extern bool   UseNewsStraddle=0;
// b15: straddle distance from price in points
extern int    NewsStraddleDist=20;
// b15: straddle take profit in points
extern int    NewsStraddleTP=100;
// b15: straddle stop loss in points
extern int    NewsStraddleSL=50;
// b15: minutes before the unfilled straddle orders expire
extern int    NewsStraddleExpiryMin=30;
// b15: NFP fade: five minutes after each NFP release trade against the direction of the first 5-minute bar
extern bool   UseNewsFade=0;
// b15: fade take profit in points
extern int    NewsFadeTP=100;
// b15: fade stop loss in points
extern int    NewsFadeSL=50;
// b15: draw small and large fibonacci levels, support and resistance on the chart (visual only)
extern bool   UseChartDraw=0;
// b15: timeframe in minutes of the small fibonacci swing and the fractal lines
extern int    DrawTF=60;
// b15: bars of DrawTF for the small swing
extern int    SwingBars=48;
// b15: H4 bars for the large swing
extern int    LargeSwingBars=200;
// b15: number of fractal support and resistance lines
extern int    SRLines=3;
// b15: small and large levels within this many points count as a confluence
extern int    ConfTolPts=15;
string NFPd="2011.02.04 2011.03.04 2011.04.01 2011.05.06 2011.06.03 2011.07.08 2011.08.05 2011.09.02 2011.10.07 2011.11.04 2011.12.02 2012.01.06 2012.02.03 2012.03.09 2012.04.06 2012.05.04 2012.06.01 2012.07.06 2012.08.03 2012.09.07 2012.10.05 2012.11.02 2012.12.07 2017.02.03 2017.03.10 2017.04.07 2017.05.05 2017.06.02 2017.07.07 2017.08.04 2017.09.01 2017.10.06 2017.11.03 2017.12.08 2019.02.01 2019.03.08 2019.04.05 2019.05.03 2019.06.07 2019.07.05 2019.08.02 2019.09.06 2019.10.04 2019.11.01 2019.12.06 2020.01.10 2020.02.07 2020.03.06 2020.04.03 2020.05.08 2020.06.05 2020.07.02 2020.08.07 2020.09.04 2020.10.02 2020.11.06 2020.12.04 2021.01.08 2021.02.05 2021.03.05 2021.04.02 2021.05.07 2021.06.04 2021.07.02 2021.08.06 2021.09.03 2021.10.08 2021.11.05 2021.12.03";
string CPId="2011.02.17 2011.03.17 2011.04.15 2011.05.13 2011.06.15 2011.07.15 2011.08.18 2011.09.15 2011.10.19 2011.11.16 2011.12.16 2012.01.19 2012.02.17 2012.03.16 2012.04.13 2012.05.15 2012.06.14 2012.07.17 2012.08.15 2012.09.14 2012.10.16 2012.11.15 2012.12.14 2017.02.15 2017.03.15 2017.04.14 2017.05.12 2017.06.14 2017.07.14 2017.08.11 2017.09.14 2017.10.13 2017.11.15 2017.12.13 2019.02.13 2019.03.12 2019.04.10 2019.05.10 2019.06.12 2019.07.11 2019.08.13 2019.09.12 2019.10.10 2019.11.13 2019.12.11 2020.01.14 2020.02.13 2020.03.11 2020.04.10 2020.05.12 2020.06.10 2020.07.14 2020.08.12 2020.09.11 2020.10.13 2020.11.12 2020.12.10 2021.01.13 2021.02.10 2021.03.10 2021.04.13 2021.05.12 2021.06.10 2021.07.13 2021.08.11 2021.09.14 2021.10.13 2021.11.10 2021.12.10";
string FOMCd="2011.01.26 2011.03.15 2011.04.27 2011.06.22 2011.08.09 2011.09.21 2011.11.02 2011.12.13 2012.01.25 2012.03.13 2012.04.25 2012.06.20 2012.08.01 2012.09.13 2012.10.24 2012.12.12 2017.02.01 2017.03.15 2017.05.03 2017.06.14 2017.07.26 2017.09.20 2017.11.01 2017.12.13 2019.01.30 2019.03.20 2019.05.01 2019.06.19 2019.07.31 2019.09.18 2019.10.30 2019.12.11 2020.01.29 2020.04.29 2020.06.10 2020.07.29 2020.09.16 2020.11.05 2020.12.16 2021.01.27 2021.03.17 2021.04.28 2021.06.16 2021.07.28 2021.09.22 2021.11.03 2021.12.15";
datetime newsT[256]; int newsTy[256]; int newsN=0; datetime lastNewsS=0, lastNewsF=0;
double fibLvS[7], fibLvL[7];
// b15: a parked buy is tracked as a virtual buy (entry, TP, SL); while it lives it blocks new buys and can trigger the hedge sell like a real buy
extern bool   UseVirtualBuy=1;
double vPrice=0, vTP=0, vSL=0; int vHedged=0, vN=0;
// b16: virtual buy exit. 0 = TP BuyTPpts (b15v), 1 = close at first profit of VFirstPts, 2 = TP VTPpts
extern int    VExitMode=0;
// b16: first-profit points for VExitMode 1
extern int    VFirstPts=2;
// b16: take profit points for VExitMode 2
extern int    VTPpts=10;
// b17: ladder order type. 0 = sell stops below (b12), 1 = buy stops above, 2 = buy limits below, 3 = one market buy with LadderTP/LadderSL
extern int    LadderMode=0;
// b17: ladder regime gate. 0 = H1 below SMA (sell regime, b12), 1 = H1 above SMA (up regime)
extern int    LadderRegime=0;
// b17: take profit and stop loss points for ladder modes 1-3
extern int    LadderTP=300;
extern int    LadderSL=300;
// b18: seconds to wait after the signal before the ladder is placed (0 = at once, as b17)
extern int    LadderDelaySec=0;
datetime ladderDue=0; bool ladderFire=false;
// b19: M15 low-reversal buy: close at the LowRevBars low with at most LowRevMaxBull bullish candles, market buy, own TP/SL, time stop
extern bool   UseLowRevBuy=0;
extern int    LowRevBars=15;
extern int    LowRevMaxBull=6;
// b19: H1 EMA cross buy: EMA fast crosses above EMA slow on the last closed H1 bar
extern bool   UseEmaCrossBuy=0;
extern int    CrossFast=20;
extern int    CrossSlow=50;
// b19: take profit, stop loss (points), time stop (hours) and max open orders for both new buys
extern int    NBuyTP=300;
extern int    NBuySL=150;
extern int    NBuyHoldH=12;
extern int    NBuyMax=3;
// b19: close new buys at/after this server hour to avoid swap (0 = off)
extern int    NBuyCloseHour=0;
datetime nbLastM15=0, nbLastH1=0;
// b20: sell block: no new sell orders (stops, ladder, hedges) when M15 ADX14 is above BlockADX or the server hour is below BlockHour
extern bool   UseSellBlock=1;
extern int    BlockADX=28;
extern int    BlockHour=2;
// b20: counter-hedge: when an open sell is CHTrigger pts against, open one opposite buy (mode 0 market, 1 buy stop 20 pts above) with CHTP/CHSL
extern bool   UseCounterHedge=0;
extern int    CHTrigger=250;
extern int    CHMode=0;
extern int    CHTP=150;
extern int    CHSL=150;
int chDone[256]; int chN=0;
extern int    SellRegimePeriod=1200;
// ---- b8 WIDE BUY (default off): the same buy entries but TP 300 / SL 100 instead of 15 / 290, and only when the last CLOSED H1 bar
// is ABOVE the H1 SMA(SellRegimePeriod) (mirror of the sell gate). History replay: +19 (2017), +12 (2019), +2 (2020) per trade, -15 in 2011-12.
// Win rate about 30%, so expect long losing runs. 1 = on, 0 = off (buys as in b7).
extern bool   UseWideBuy=0;
extern int    WideBuyTP=300;
extern int    WideBuySL=100;
// ---- b8 ROUND-NUMBER BUY LIMIT (default off, comment "9"): a buy limit at the .00 / .50 level at least RoundMinDist pts below Ask,
// placed when no "9" order exists and RoundReplaceMin minutes passed since the last one, RoundExpiryMin expiry, TP/SL RoundTP/RoundSL,
// stop moved to break-even after +RoundBreakEven pts, closed after RoundMaxHours. Only when H1 is ABOVE the SMA(SellRegimePeriod).
// Sell-side research on history: +31/+21/+1.8/+6.4/+7.4 per trade in 2011/2012/2017/2019/2021 (2019 only 18 trades). A filled "9" buy
// blocks the normal buy entries until it closes.
extern bool   UseRoundBuyLimit=0;
extern int    RoundMinDist=100;
extern int    RoundReplaceMin=240;
extern int    RoundExpiryMin=120;
extern int    RoundTP=200;
extern int    RoundSL=300;
extern int    RoundBreakEven=50;
extern int    RoundMaxHours=24;
datetime roundLast=0;
extern bool   UseSellLadder=1;
extern int    Ladder1=20;
extern int    Ladder2=50;
extern int    Ladder3=100;
extern bool   UseBracket=0;
extern int    BracketH=50;
extern int    BracketTP=300;
extern int    BracketSL=300;
extern int    BracketExpiryMin=120;
extern bool   BracketOCO=1;
extern bool   BracketRegime=0;
extern bool   BracketRearm=0;
int rearmDone=0;
// ---- b9 ROUND-LIMIT RA FILTER (default off): place the "9" buy limit only when the M15 EMA(2) rate-of-accel of the last closed bar
// is above 0. Sell-side history: the one filter of 2,286 weighted SARA formulas that held all five years (2019 +20.6 vs -30.4 without).
extern bool   UseRoundBuyRA=0;
double bf_slope,bf_accel,bf_roa,bf_sara,bf_slopeavg,bf_mmr,bf_rng,bf_vrel,bf_K,bf_D,bf_prv,bf_sara_prv; datetime flatLastBar=0;
//---- end claude_b1 inputs ----


//as of May 2019, commission is 6 points. 
int  w[50],LastModTicket2=0,OrdersSent=0,OrdersCounted=0,FC[50],LastModTicket=0,magic=5348893,acss=0,slip=10,obc[50],osc[50],
 psc[50],
nsc[50],pac[50],nac[50],pra[50],nra[50]; //default slip 5 
long v[50]; 
string s=Symbol(),disp[50];
double rm[50],rmd[50],MinSlopeAllowed= -5,MSA=0,tkp=0,sra[50],aob[50],Wins[50],Losses[50],NeededTP=0,p=Point,ma[50],slp[50],
 r[50],h[50],ra[50],st[50],sp[50],sr[50],ac[50],ap[50],ar[50],
 acs[50],slh[50],ach[50];
//--- input parameters end



//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit(){ Print("init1"); magic=MagicNumber;

 //----Prerequisites  // Comment("Init test"); 
   if(AccountNumber()!=892151){return(0);}   HideTestIndicators(1);  
   
 //--- Initialize Wide Access Arrays
   ArrayInitialize(FC,0); ArrayInitialize(Wins,0);ArrayInitialize(Losses,0); 
   ArrayInitialize(ra,0);  ArrayInitialize(ma,0);  ArrayInitialize(slp,0); ArrayInitialize(r,0); ArrayInitialize(h,0); ArrayInitialize(st,0);
    ArrayInitialize(sp,0); ArrayInitialize(sr,0); ArrayInitialize(ac,0); ArrayInitialize(ap,0); ArrayInitialize(ar,0);ArrayInitialize(acs,0);
     ArrayInitialize(slh,0); ArrayInitialize(ach,0); ArrayInitialize(v,0);

 //--- Exit
   return(INIT_SUCCEEDED); return(0);}
   
   
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason){ DrawDeinit(); 
  if(OrdersSent>0 || OrdersHistoryTotal()>0){
  int a=0,i=0;
   if(FC[0]>0){
       for(a=0; a<=49; a++){
          if(FC[a]>0){Print("Filter # ",a," count: ",FC[a]); } } }
   //Comment("deInit test");
//---



  for(a=0; a<=OrdersHistoryTotal(); a++){
     if(OrderSelect(a,SELECT_BY_TICKET,MODE_HISTORY)){  if(OrderComment()!="0"){ 
        if(OrderProfit()>(MathAbs(OrderCommission())+MathAbs(OrderSwap()))){
            i=StrToInteger(OrderComment()); 
                 Wins[i]++; OrdersCounted++; 
               }else{Losses[i]++; OrdersCounted++; } }} }}

double T=0,Odds=0; string oddss="";
if(OrdersCounted>0){
    for(int a=0; a<=49; a++){
    
   //incorrect index, dont use a
        if(Wins[a]>0 || Losses[a]>0){ //array out of range 
              T=Wins[a]+Losses[a];  Odds=(Wins[a]/T)*100; oddss=sd(Odds,2);
                Print("Type ",a," ",Wins[a]," / ",T," ",oddss," %"); } }} return; }
                
                
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
//---- g1 sell-only clone: every real buy order (market/stop/limit) is blocked; parked/virtual buy signals still drive the sell legs
extern bool   SellOnly=1;
extern bool   UseStopHourBlock=1;   //g2: skip sell-stop/ladder placement in blocked server hours
extern int    StopBlock1From=12;
extern int    StopBlock1To=16;
extern int    StopBlock2From=20;
extern int    StopBlock2To=24;
extern bool   UseHedgeHourBlock=0;
extern int    HedgeBlockFrom=20;
extern int    HedgeBlockTo=24;
bool InHours(int a,int b){ int h=TimeHour(TimeCurrent()); return(h>=a && h<b); }
bool StopHourBlocked(){ return(UseStopHourBlock==1 && (InHours(StopBlock1From,StopBlock1To) || InHours(StopBlock2From,StopBlock2To))); }
int OrderSendSO(string sym,int cmd,double vol,double price,int slp,double sl,double tpx,string cm,int mg,datetime ex,color clr){
   if(SellOnly==1 && (cmd==OP_BUY || cmd==OP_BUYSTOP || cmd==OP_BUYLIMIT)){ return(-1); }
   return(OrderSend(sym,cmd,vol,price,slp,sl,tpx,cm,mg,ex,clr)); }
#define OrderSend OrderSendSO
void OnTick(){ if(UseCounterHedge==1){ CHMng(); } if(UseLowRevBuy==1 || UseEmaCrossBuy==1){ NBuyMng(); } if(ladderDue>0 && TimeCurrent()>=ladderDue){ ladderDue=0; ladderFire=true; PlaceLadder(); } if(UseChartDraw==1){ ChartDraw(); } NewsMng(); if(UseVirtualBuy==1){ VirtualMng(); } if(UseBracket==1){ BracketMng(); } if(UseRoundBuyLimit==1){ RoundBuyLimit(); } if(OrdersTotal()>0){ OrderMng(); if(BuysOpen()>0 || (UseSellStop==0 && UseHedgeSell==0 && UseRoundBuyLimit==0)){ return; } } //b8: a pending "9" limit does not block buys //b5: open sells no longer block buys
 if(FriBlock==1){  if(DayOfWeek()==5){ if(Hour()>=FriHour){ return; }}} //sun 0  m 1   tu 2   w 3   thur 4   fri 5 ,  
       // as of Mar 2019, FXOT is 23 US EST is 16 so +7 hr difference
   if(SwapHelp==1){if(Hour()>=SwapHour){return;}} // need 2 different kinds of swap help
     if(BuysOpen()==0){ if(Bars<100){return;} if(UseWideBuy==1 && !BuyRegimeOK()){ return; } //b8 wide-buy regime gate
       double spr=MarketInfo(Symbol(),MODE_SPREAD);
        if(spr>8){ return;}//default >5
        //---- claude_b1 flat entry: checked once per closed M15 bar, before the original slope filter
        if(UseFlatEntry==1 && iTime(s,PERIOD_M15,0)!=flatLastBar){ flatLastBar=iTime(s,PERIOD_M15,0);
           BrFeat(PERIOD_M15);
           if(bf_slopeavg>=FlatSlopeMin && bf_slopeavg<=FlatSlopeMax && bf_mmr>=FlatMmrMin && bf_vrel<=FlatVolRelMax
              && bf_rng<iATR(s,PERIOD_M15,14,1)/p && bf_K>=FlatKMin && bf_K<=FlatKMax && iClose(s,PERIOD_M15,1)>iOpen(s,PERIOD_M15,1)){
              Print("FLAT m15 slopeavg ",sd(bf_slopeavg,2)," mmr ",sd(bf_mmr,2)," rng ",sd(bf_rng,1)," vrel ",sd(bf_vrel,2)," K ",sd(bf_K,1)," sara ",sd(bf_sara,1)," prv ",sd(bf_prv,1));
              RefreshRates(); int tkf=BuySend("4",clrBlue); if(tkf>0){
                 RatioLog(tkf); RatioLog2(tkf); if(UseSellStop==1){ PlaceSellStop(); } if(UseSellLadder==1){ PlaceLadder(); } if(UseBracket==1){ PlaceBracket(); } OrdersSent++; OrderMng(); return; } else { Print("FLAT OrderSend err ",GetLastError()); } } }
        //---- end flat entry
        //---- claude_b1 Signal-app entries S2 / S4 (once per closed M15 bar)
        static datetime sLastBar=0;
        if((UseS2Entry==1 || UseS4Entry==1) && iTime(s,PERIOD_M15,0)!=sLastBar){ sLastBar=iTime(s,PERIOD_M15,0);
           double rsi1=iRSI(s,PERIOD_M15,14,PRICE_CLOSE,1), bbl=iBands(s,PERIOD_M15,20,2,0,PRICE_CLOSE,MODE_LOWER,1);
           double stK=iStochastic(s,PERIOD_M15,14,3,1,MODE_SMA,STO_LOWHIGH,MODE_MAIN,1);
           bool up=iMA(s,PERIOD_M15,50,0,MODE_EMA,PRICE_CLOSE,1)>iMA(s,PERIOD_M15,200,0,MODE_EMA,PRICE_CLOSE,1);
           string sc="";
           if(UseS2Entry==1 && rsi1<25){ sc="5"; }
           if(sc=="" && UseS4Entry==1 && iClose(s,PERIOD_M15,1)<bbl && stK<10 && up){ sc="6"; }
           if(sc!=""){ Print("SIGNAL S",sc," rsi ",sd(rsi1,1)," stK ",sd(stK,1)," bbl ",sd(bbl,Digits)," up ",up);
              RefreshRates(); int tks=BuySend(sc,clrMagenta); if(tks>0){
                 RatioLog(tks); RatioLog2(tks); if(UseSellStop==1){ PlaceSellStop(); } if(UseSellLadder==1){ PlaceLadder(); } if(UseBracket==1){ PlaceBracket(); } OrdersSent++; OrderMng(); return; } else { Print("SIGNAL OrderSend err ",GetLastError()); } } }
        //---- end S2/S4
         double slope=Slp(1,2,0); if(slope<EntrySlopeMin //claude_b1: was literal 2. default 1 2 0 <5 <3 <2
           ){ FC[0]++; FC[4]++; return;} MSA=MinSlopeAllowed;  acss=0;
         // double slope2=Slp(1,4,0);  // && slope2<2
      
  double Stoch[50];  ArrayInitialize(Stoch,0); ArrayInitialize(w,0);
   Stoch[0]=sto(15,10,2); if(Stoch[0]>80 //default 15 10 2 >50 >60
        ){ FC[0]++; FC[1]++; return; } 
        
//---- Restrictions: Slope / Position ratio, acceleration, rate of acceleration, dynamics, rate of change, etc. 
 // First set is direct sp ratios, 2nd set is indirect. 
    ArrayInitialize(sp,0); sp[0]=SP(1,1,2,2,0,0); if(sp[0]<0.33 //default <0.5 or 0.35555 or 0.34
     || sp[0]>5 //default >2
    ){return;}
    sp[1]=SP(1,1,2,2,0,1); if(sp[1]<0.00001  //default <0.1
    || sp[1]>5 //default >0.9
    ){return;}
     sp[2]=SP(1,1,2,10,0,0); if(sp[2]<0.00001 //default <0.1
      || sp[2]>5 //default >0.9
      ){return;}
      sp[3]=SP(1,1,2,10,0,1); if(sp[3]<0.00001  //default <0.1 
      || sp[3]>5 // default >0.9
      ){return;}
    
    sp[4]=SP(1,15,2,2,0,0); if(sp[4]<0.00001 //default <0.1
     || sp[4]>5 //default >0.9
     ){return;}
     sp[5]=SP(1,15,2,10,0,1); 
    
    sp[6]=SP(1,1,5,5,0,0); 
     sp[7]=SP(1,1,10,10,0,0);
     
     
    
    sp[8]=SP(5,5,3,3,0,0);    
     sp[9]=SP(5,5,5,5,0,0);   
      sp[10]=SP(5,5,10,10,0,0);  
      
    sp[11]=SP(15,15,2,2,0,0); 
    sp[12]=SP(15,15,5,5,0,0);   //make your bed, build a team, failure can lead to success. 
    sp[13]=SP(15,15,10,10,0,0); 
    
    
   
      double Minsp=sp[ArrayMinimum(sp,14,0)];  double Maxsp=sp[ArrayMaximum(sp,14,0)];
       ArrayInitialize(sr,0);
sr[0]=SR(1,1,2,2,0,0); sr[1]=SR(1,1,2,2,0,1);  sr[2]=SR(1,1,2,10,0,0); sr[3]=SR(1,1,2,10,0,1); sr[4]=SR(1,15,2,2,0,0);
 sr[5]=SR(1,15,2,10,0,1); sr[6]=SR(1,1,5,5,0,0); sr[7]=SR(1,1,10,10,0,0); sr[8]=SR(5,5,3,3,0,0);  sr[9]=SR(5,5,5,5,0,0);
  sr[10]=SR(5,5,10,10,0,0); sr[11]=SR(15,15,2,2,0,0); sr[12]=SR(15,15,5,5,0,0); sr[13]=SR(15,15,10,10,0,0); 
      double Minsr=sr[ArrayMinimum(sr,14,0)]; double Maxsr=sr[ArrayMaximum(sr,14,0)];
      double df[50]; ArrayInitialize(df,0); df[0]=sp[0]-sr[0]; df[1]=sp[1]-sr[1]; df[2]=sp[2]-sr[2];
        df[14]=Maxsr-Minsr;
      
       df[3]=sp[3]-sr[3];
       df[4]=sp[4]-sr[4];  df[5]=sp[5]-sr[5];  df[6]=sp[6]-sr[6];  df[7]=sp[7]-sr[7];  df[8]=sp[8]-sr[8];  df[9]=sp[9]-sr[9];
         df[10]=sp[10]-sr[10];  df[11]=sp[11]-sr[11];  df[12]=sp[12]-sr[12];  df[13]=sp[13]-sr[13]; 
             double Mindf=df[ArrayMinimum(df,14,0)]; double Maxdf=df[ArrayMaximum(df,14,0)];
             
             
  
    //ovb losses
ArrayInitialize(st,0); ArrayInitialize(obc,0);
st[0]=sto(1,2,0); if(st[0]>=80){ obc[0]++; if(st[0]>=90){ obc[2]++; }} st[1]=sto(1,2,1);  if(st[1]>=80){ obc[0]++; obc[1]++; } 
 st[2]=sto(1,5,0); if(st[2]>=80){ obc[0]++; if(st[2]>=90){ obc[2]++; }} st[3]=sto(1,5,1); if(st[3]>=80){ obc[0]++;  obc[1]++; } 
  st[4]=sto(1,10,0); if(st[4]>=80){ obc[0]++; if(st[4]>=90){ obc[2]++; }} st[5]=sto(1,10,1); if(st[5]>=80){ obc[0]++; obc[1]++; }
   
st[6]=sto(5,3,0); if(st[6]>=80){ obc[0]++; if(st[6]>=90){ obc[2]++; }} st[7]=sto(5,3,1); if(st[7]>=80){ obc[0]++;  obc[1]++; } 
 st[8]=sto(5,5,0); if(st[8]>=80){ obc[0]++; if(st[8]>=90){ obc[2]++; }} st[9]=sto(5,5,1); if(st[9]>=80){ obc[0]++; obc[1]++;  }  
  st[10]=sto(5,10,0); if(st[10]>=80){ obc[0]++; if(st[10]>=90){ obc[2]++; }} st[11]=sto(5,10,1); if(st[11]>=80){ obc[0]++; obc[1]++;  } 
    
st[12]=sto(15,2,0); if(st[12]>=80){ obc[0]++; if(st[12]>=90){ obc[2]++; }} st[13]=sto(15,2,1); if(st[13]>=80){ obc[0]++;  obc[1]++; }  
 st[14]=sto(15,5,0); if(st[14]>=80){ obc[0]++; if(st[14]>=90){ obc[2]++; }} st[15]=sto(15,5,1); if(st[15]>=80){ obc[0]++;  obc[1]++; } 
  st[16]=sto(15,10,0); if(st[16]>=80){ obc[0]++; if(st[16]>=90){ obc[2]++; }} st[17]=sto(15,10,1); if(st[17]>=80){ obc[0]++; obc[1]++;  } 
      
    //ovb loss risk
   
    /*strong?
    
sp[0] 0.72 0.78 0.71 sp[3] 0.84 0.76 0.90 sp[6] 0.35 0.16 0.82 sp[9] 0.37 0.45 0.84 0.54 0.23 Minsp 0.16 Maxsp 0.90
sr[0] 0.72 1.07 1.15 sr[3] 1.29 0.39 0.44 sr[6] 0.52 0.26 0.53 sr[9] 0.27 0.33 0.44 0.23 0.13 Minsr 0.13 Maxsr 1.29
df[0] 0.00 -0.29 -0.44 df[3] -0.45 0.36 0.46 df[6] -0.17 -0.10 0.29 df[9] 0.10 0.12 0.40 0.31 0.10 Mindf -0.45 Maxdf 0.46
     
sp[0] 0.57 0.61 0.56 sp[3] 0.57 0.68 0.88 sp[6] 0.24 0.14 0.52 sp[9] 0.25 0.16 0.70 0.26 0.18 Minsp 0.14 Maxsp 0.88
sr[0] 0.99 3.18 3.14 sr[3] 5.74 0.57 0.92 sr[6] 0.81 0.80 0.93 sr[9] 0.49 0.38 0.60 0.27 0.22 Minsr 0.22 Maxsr 5.74
df[0] -0.42 -2.56 -2.58 df[3] -5.18 0.10 -0.05 df[6] -0.58 -0.65 -0.41 df[9] -0.23 -0.21 0.11 -0.01 -0.04 Mindf -5.18 Maxdf 0.11  
    */
    
    /* lossy 
    
sp[0] 0.34 0.30 0.28 sp[3] 0.28 0.29 0.30 sp[6] 0.46 0.22 0.84 sp[9] 0.37 0.53 0.90 0.82 0.25 Minsp 0.22 Maxsp 0.90
sr[0] 0.65 0.48 0.54 sr[3] 0.54 0.15 0.20 sr[6] 0.67 0.43 0.48 sr[9] 0.26 0.43 0.45 0.39 0.17 Minsr 0.15 Maxsr 0.67
df[0] -0.31 -0.18 -0.26 df[3] -0.26 0.15 0.11 df[6] -0.21 -0.21 0.37 df[9] 0.11 0.11 0.45 0.42 0.08 Mindf -0.31 Maxdf 0.45

loss above 

obc lossy obc 16 8 8  smallest needed 6 3 1  6 2 2   
    */
    
    //weak sr is lossy. 
    
   
    if(sr[8]<0.9 || sp[5]<0.9){//good softener
if(Minsp<0.14 || sr[4]<0.3 || sp[10]<0.5){//good softener
    
  if(sr[4]<0.3 || sp[10]<0.5){//good softener 
if(obc[0]>=6 && obc[2]>0  //strong group, but tight
    && Minsr>0.1 && sr[3]<1  //strong group, but tight
    ){return;}

if(obc[0]>=10 && obc[2]>=2  //strong group, but tight
  && Minsr>0.01    //strong group, but tight
     ){return;}}
//2010b 279 98.21% using strong groups only 

 
//aug 19 2010 ovb loss
if(obc[0]>=6 && obc[1]>=2 && Minsr<0.2 && Maxsr<2 && Mindf> -1 &&  sr[1]<1){return;}

//aug 20 2010 ovb loss
if(obc[0]>=6 && obc[1]>=2 && Minsr<0.25 && Maxsr<2 && Mindf> -1 &&  sr[4]<0.3){return;}

//strong group
 if(Minsp<0.14){ return; } if(sp[8]<0.00001 || sp[8]>0.9){return;} if(sp[9]<0.00001 || sp[9]>0.9){return;} 
   if(sp[10]<0.00001 || sp[10]>0.9){return;}}
   
   
    //strong group
     if( sr[5]<0.4 && sr[1]<1 && sr[2]<1 && (Maxsr<0.7 || Maxsr<Maxsp || sr[3]<1) && Mindf> -1.2 // > -1.1 strong but tight
          ){ return; } // Strong 2010b 522 97.13% with no softener,these 4 together
if(sr[1]<1 || sr[2]<1 || sr[3]<1 || Maxsr<1 || Maxsr<Maxsp || Mindf> -1.2){    // strong group below
 //strong group, exp softener above           
 if(sp[11]<0.00001 || sp[11]>0.9){ return; }  if(sp[12]<0.00001 || sp[12]>0.9){ return; } 
  if(sp[13]<0.00001 || sp[13]>0.9){ return; }  }
    
    
    
    //strong group on its own, not usually inside of a softener, but is now
     if(sp[5]<0.00001 || 
     sp[5]>5 // default >0.9
     ){return;} 
     if(sp[6]<0.00001 || sp[6]>5 //>0.9
    ){return;}
      if(sp[7]<0.00001 || sp[7]>5 //>0.9
     ){return;}
     
   }



Print("sp[0] ",sd(sp[0],2)," ",sd(sp[1],2)," ",sd(sp[2],2)," sp[3] ",sd(sp[3],2)," ",sd(sp[4],2)," ",sd(sp[5],2),
 " sp[6] ",sd(sp[6],2)," ",sd(sp[7],2)," ",sd(sp[8],2)," sp[9] ",sd(sp[9],2)," ",sd(sp[10],2)," ",sd(sp[11],2),
 " sd[12] ",sd(sp[12],2),
  " ",sd(sp[13],2)," Minsp ",sd(Minsp,2)," Maxsp ",sd(Maxsp,2));

Print("sr[0] ",sd(sr[0],2)," ",sd(sr[1],2)," ",sd(sr[2],2)," sr[3] ",sd(sr[3],2)," ",sd(sr[4],2)," ",sd(sr[5],2),
 " sr[6] ",sd(sr[6],2)," ",sd(sr[7],2)," ",sd(sr[8],2)," sr[9] ",sd(sr[9],2)," ",sd(sr[10],2)," ",sd(sr[11],2),
 " sr[12] ",sd(sr[12],2),
  " ",sd(sr[13],2)," Minsr ",sd(Minsr,2)," Maxsr ",sd(Maxsr,2));
  
Print("df[0] ",sd(df[0],2)," ",sd(df[1],2)," ",sd(df[2],2)," df[3] ",sd(df[3],2)," ",sd(df[4],2)," ",sd(df[5],2),
 " df[6] ",sd(df[6],2)," ",sd(df[7],2)," ",sd(df[8],2)," df[9] ",sd(df[9],2)," ",sd(df[10],2)," ",sd(df[11],2),
 " df[12] ",sd(df[12],2),
  " ",sd(df[13],2)," ",sd(df[14],2)," Mindf ",sd(Mindf,2)," Maxdf ",sd(Maxdf,2));
  if(obc[0]>0){ Print("obc[0] ",obc[0]," ",obc[1]," ",obc[2]); }
  
  //default tp = 8 
  //---- claude_b1 branch flags: computed and logged for every original entry; enforced only when BranchMode>0
  BrFeat(PERIOD_M15); double A_sp=bf_sara_prv, m15roa=bf_roa, m15K=bf_K, m15sav=bf_slopeavg, m15mmr=bf_mmr, m15vrel=bf_vrel, m15rng=bf_rng, m15sara=bf_sara, m15prv=bf_prv;
  BrFeat(PERIOD_M5);  double m5sara=bf_sara, m5sav=bf_slopeavg, m5mmr=bf_mmr;
  BrFeat(PERIOD_H1);  double h1kd=bf_K-bf_D, h1sav=bf_slopeavg;
  int brA=(A_sp>=BrA_SaraPrv), brB=(m5sara>=BrB_M5Sara && m15roa>=BrB_M15Roa), brC=(m15K>=BrC_M15K && h1kd>=BrC_H1KD);
  Print("BR A ",brA," B ",brB," C ",brC," | m15 sara ",sd(m15sara,1)," prv ",sd(m15prv,1)," sara_prv ",sd(A_sp,3)," roa ",sd(m15roa,1)," slopeavg ",sd(m15sav,2)," mmr ",sd(m15mmr,2),
        " rng ",sd(m15rng,1)," vrel ",sd(m15vrel,2)," K ",sd(m15K,1)," | m5 sara ",sd(m5sara,1)," slopeavg ",sd(m5sav,2)," mmr ",sd(m5mmr,2)," | h1 KD ",sd(h1kd,1)," slopeavg ",sd(h1sav,2));
  if(BranchMode==1 && brA==0){ FC[0]++; FC[41]++; return; }
  if(BranchMode==2 && brB==0){ FC[0]++; FC[42]++; return; }
  if(BranchMode==3 && brC==0){ FC[0]++; FC[43]++; return; }
  if(BranchMode==4 && brA==0 && brB==0 && brC==0){ FC[0]++; FC[44]++; return; }
  //---- end branch flags
 RefreshRates();  int tk0=BuySend("",clrGreen);
 if(tk0>0){ RatioLog(tk0); RatioLog2(tk0); if(UseSellStop==1){ PlaceSellStop(); } if(UseSellLadder==1){ PlaceLadder(); } if(UseBracket==1){ PlaceBracket(); } } //b5/b6
 if(tk0==1){ 
  if(OrdersTotal()>0){  OrdersSent++; OrderMng();   }  return;  }else if(OrdersTotal()==0){ 
       Print("OrderSend err ",GetLastError());  return; } return;
        //range and volume restrictions?
           if(rng(1,2,1)<5 // default  1 2 1 <10 <5
            ){ FC[0]++; FC[2]++; return;}
           if(vol(1,1)<5 // default 1 1 <15 <10 <5
            ){ FC[0]++; FC[3]++; return;}
      //Previous low position, low/narrow range, low/flat slope, low/flat acceleration,
      // current high slope, high acceleration, increasing range, properly increasing position
      //need a full function that calculates stochastics, slopes, slope/position ratios, varying shifts, and spits out the odds.
      //consider displaying types, odds,etc. in the comments, charts, etc. 


       
       
      if(slope>=5){  //>=5 >=3
       Stoch[1]=sto(15,5,2); if(Stoch[1]>80 //default 15 5 2 >50 >60 >70
        ){ FC[0]++; FC[5]++; return;}
        
        Stoch[2]=sto(15,2,2); if(Stoch[2]>80 //default 15 2 2 >50 >60 >70
         ){ FC[0]++; FC[6]++; return;}
         
        if(Slp(1,5,0)<1 // default 1 5 0 <4  <3 <1 
           ){ FC[0]++; FC[7]++; return;  }
         
//sp restriction, chart needed
//low performance, low adaptability, weak 

//loss dates 2011 Apr 18 28 29 May 27 Jun 8 15 
 if(Slp(1,5,0)<1 // default 1 5 0 <4  <3 <1 
  ){ FC[0]++; FC[8]++; return;}  
  
   ArrayInitialize(sp,0); if( slope>1){ 
   if(Stoch[0]>1 ){   sp[0]=slope/Stoch[0]; } //m 15,pd 10,sh 2
   
   //sp ranges, ac, ra
     //sp min           sp max  
   //===============================
    // if(sp[0]<0.75      || sp[0]>0.8 ){return;}//default <0.4    2011a jan feb mar apr
      //if(sp[0]<0.75      || sp[0]>1.5 ){return;} 
       //if(sp[0]<0.4      || sp[0]>0.9 ){return;}//default <0.4 //2011 Apr May Jun Jul 
          
           
       
    if(Stoch[2]>1 ){ sp[1]=slope/Stoch[2]; } //m 15, pd 2, sh 2
    
      //sp min           sp max  
       //===============================
     //  if(sp[1]<0.2    || sp[1]>0.5  ){return;} //default <0.4. <0.01 too low   2011a jan feb mar apr
        //if(sp[1]<0.15    || sp[1]>0.8  ){return;} //2011 Apr May Jun Jul
          }//default <0.4. <0.01 too low
           
       
       //multiple sp needed asap
       
      Stoch[3]=sto(15,5,2); if(Stoch[3]>1){ slp[3]=Slp(1,2,0); } if(slp[3]>1){sp[3]=slp[3]/Stoch[3];}
      
            //sp min          sp max 
         //===============================
        //if(sp[3]<0.2     ||    sp[3]>0.5){return;} //2011a jan feb mar apr
       // if(sp[3]<0.2     ||    sp[3]>0.6){return;}  
        
         //if(sp[3]<0.15     ||    sp[3]>0.8){return;} //2011 Apr May Jun Jul
        
        
         //sp min    sp max 
         
         
   
    // if(sp[0]<0.6  || sp[0]>2 || sp[1]<0.1 || sp[1]>0.9 || sp[3]<0.1 || sp[3]>0.9){return;} // 2011a jan feb mar apr
     // if(sp[0]<0.1  || sp[0]>2 || sp[1]<0.1 || sp[1]>0.9 || sp[3]<0.1 || sp[3]>0.9){return;}
  //sp[0] 0.76898  0.36990  0.0 0.48555 
 ArrayInitialize(rm,0); ArrayInitialize(rmd,0);
   ArrayInitialize(sra,0);   ArrayInitialize(aob,0); ArrayInitialize(obc,0); ArrayInitialize(osc,0); 
   ArrayInitialize(acs,0);  ArrayInitialize(psc,0); ArrayInitialize(nsc,0); ArrayInitialize(pac,0); ArrayInitialize(nra,0); 
       ArrayInitialize(nac,0); ArrayInitialize(pra,0); ArrayInitialize(nra,0);   ArrayInitialize(w,0); 
         Data(1,2,0,0);  //if(acs[4]<0.2){return;} if(sr[0]<0.2){return;}
          // if(ac[0]<10 || ra[0]<10){return;}//important Jan 2011  // 2011a jan feb mar apr
           //if(ac[0]<1 || ra[0]<1){ return; } //2011 Apr May Jun Jul
             
                 Data(15,10,0,4);  //if(sp[4]<0.01 || sp[4]>0.5){return;}
            Data(5,3,0,1); 
          
          //this filter may be too strong
           //if(ac[1]<1 && ra[1]<1){return;} //2011 Apr May Jun Jul 
           
           
           
            // if(sra[1]<1){return;} //2011 Apr May Jun Jul
            
             Data(15,2,0,2);
          // if(ac[2]<1 && ra[2]<1){return;}  //2011 Apr May Jun Jul
           
          // if(acs[2]<1){return;} //2011 Apr May Jun Jul
              // if(ach[2]<1){return;} //2011 Apr May Jun Jul
           
           Data(15,5,0,3);  
            double minslp[50]; ArrayInitialize(minslp,0); minslp[0]=slp[ArrayMinimum(slp,18,0)];
            


//average sp, ac, ra
double avgslp[50],avgsp[50],avgra[50],avgac[50];  ArrayInitialize(avgslp,0);ArrayInitialize(avgsp,0);  ArrayInitialize(avgra,0); 
  ArrayInitialize(avgac,0); 
//note that the sp values get changed when the data functions start 
avgslp[0]=(slp[0]+slp[1]+slp[2])/3; avgslp[1]=(slp[0]+slp[1]+slp[2]+slp[3]+slp[4])/5; 
avgsp[0]=(sp[0]+sp[1]+sp[2])/3; avgsp[1]=(sp[0]+sp[1]+sp[2]+sp[3]+sp[4])/5; 
avgra[0]=(ra[0]+ra[1]+ra[2])/3; avgra[1]=(ra[0]+ra[1]+ra[2]+ra[3]+ra[4])/5;
avgac[0]=(ac[0]+ac[1]+ac[2])/3; avgac[1]=(ac[0]+ac[1]+ac[2]+ac[3]+ac[4])/5;

/* strong? 
1.2.0.0 st 61.11 slp 19.50 ac 29.50 ra 57.00 r 46.00 h 44.20 v 38.00 sp 0.32 sr 0.42 ap 0.48 ar 0.64 acs 1.51 sra 0.34 slh 0.44 ach 0.67  
5.3.0.1 st 58.13 slp 13.67 ac 19.00 ra 22.00 r 91.67 h 65.60 v 122.00 sp 0.24 sr 0.15 ap 0.33 ar 0.21 acs 1.39 sra 0.62 slh 0.21 ach 0.29  
15.2.0.2 st 48.18 slp 57.00 ac 96.00 ra 95.50 r 135.50 h 66.60 v 222.00 sp 1.18 sr 0.42 ap 1.99 ar 0.71 acs 1.68 sra 0.60 slh 0.86 ach 1.44  
15.5.0.3 st 42.86 slp 4.20 ac 20.20 ra 15.60 r 105.60 h 66.60 v 222.00 sp 0.10 sr 0.04 ap 0.47 ar 0.19 acs 4.81 sra 0.27 slh 0.06 ach 0.30  
15.10.0.4 st 33.33 slp 4.20 ac 32.80 ra 28.30 r 122.20 h 66.60 v 222.00 sp 0.13 sr 0.03 ap 0.98 ar 0.27 acs 7.81 sra 0.15 slh 0.06 ach 0.49  
sp[0] 0.32 0.24 1.18 0.10 minslp -33.10 avgsp[0] 0.58 0.39 avgac 48.17 39.50 avgra 58.17 43.68
*/
if(minslp[0]<= -5 && avgsp[0]<0.3 && sra[1]<0.2 && sra[2]<0.2 && sra[3]<0.2 && sra[4]<0.2  ){ w[0]++; w[1]++;  }
 if(avgra[0]<avgac[0] || avgra[0]<avgslp[0]){ w[0]++; w[2]++;  }
  //if(w[0]>=2){return;}
  



if(minslp[0]<= -40 && sp[0]<0.3 && ap[0]<0.5 && sp[4]<0.2 && acs[3]<0.2 && sra[3]<0.2 
 && sra[4]<0.2){ w[0]++; w[3]++;   }//2011 Apr May Jun Jul
  if(slp[3]<5 && acs[4]<0.2 && sra[4]<0.2 && sp[4]<0.2 && slp[4]<1 && sp[3]<0.5
    && sr[0]<1){w[0]++; w[4]++;  }//too strong
 
// Apr May Jun  178 98.88% 
           /*
         loss too high ap acs ach   
         
1.2.0.0 st 70.14 slp 31.50 ac 16.50 ra 13.50 r 40.00 h 41.40 v 1.00 sp 0.45 sr 0.79 ap 0.24 ar 0.41 acs 0.52 sra 2.33 slh 0.76 ach 0.40  
5.3.0.1 st 61.62 slp 28.33 ac 49.33 ra 56.33 r 94.00 h 51.80 v 242.00 sp 0.46 sr 0.30 ap 0.80 ar 0.52 acs 1.74 sra 0.50 slh 0.55 ach 0.95  
15.2.0.2 st 54.73 slp 22.00 ac 92.00 ra 218.00 r 175.50 h 51.40 v 1246.00 sp 0.40 sr 0.13 ap 1.68 ar 0.52 acs 4.18 sra 0.10 slh 0.43 ach 1.79  
15.5.0.3 st 57.17 slp 33.60 ac 22.40 ra 14.40 r 187.00 h 51.40 v 1246.00 sp 0.59 sr 0.18 ap 0.39 ar 0.12 acs 0.67 sra 2.33 slh 0.65 ach 0.44  
15.10.0.4 st 46.40 slp -7.50 ac 8.00 ra -1.30 r 172.10 h 51.40 v 1246.00 sp 0.00 sr 0.16 ap 0.17 ar 0.05 acs 0.00 sra 0.00 slh 0.15 ach 0.16  
 too high ap acs ach 
sp[0] 0.45 0.46 0.40 0.59 minslp -24.80 avgslp[0] 27.28 21.59 avgsp[0] 0.44 0.38 avgac 52.61 37.65 avgra 95.94 60.19
  
           
           
           strong?  sra is high, everything else is low 
1.2.0.0 st 73.05 slp 32.50 ac 25.50 ra 18.50 r 42.50 h 50.00 v 34.00 sp 0.44 sr 0.76 ap 0.35 ar 0.60 acs 0.78 sra 1.76 slh 0.65 ach 0.51  
5.3.0.1 st 76.29 slp 17.33 ac 6.00 ra 19.00 r 60.67 h 57.80 v 122.00 sp 0.23 sr 0.29 ap 0.08 ar 0.10 acs 0.35 sra 0.91 slh 0.30 ach 0.10  
15.2.0.2 st 75.29 slp 45.50 ac 42.50 ra 87.50 r 71.00 h 83.60 v 122.00 sp 0.60 sr 0.64 ap 0.56 ar 0.60 acs 0.93 sra 0.52 slh 0.54 ach 0.51  
15.5.0.3 st 86.89 slp 58.60 ac 23.60 ra -12.40 r 118.20 h 83.60 v 122.00 sp 0.67 sr 0.50 ap 0.27 ar 0.20 acs 0.40 sra 0.00 slh 0.70 ach 0.28  
15.10.0.4 st 65.73 slp -1.00 ac 6.00 ra -2.30 r 139.80 h 83.60 v 122.00 sp 0.00 sr 0.03 ap 0.09 ar 0.04 acs 0.00 sra 0.00 slh 0.04 ach 0.07  

sp[0] 0.44 0.23 0.60 0.67 minslp -15.30 avgslp[0] 31.78 30.59 avgsp[0] 0.42 0.39 avgac 24.67 20.72 avgra 41.67 22.06

slp[0] 23.50 ac[0] 15.5 ra[0] 48 sr[0] 0.68 acs[0] 0.66 
slp[1] 80.33 ac[1] 23.33 sp[1] 0.85 sr[1] 0.71 sra[1] 48.39
slp[2] 113 ac[2] 180 sp[2] 1.9 ap[2] 3.03 ar[2] 0.91 acs[2] 1.59 sra[2] 0.7 slh[2] 0.86 ach[2] 1.37


           */
          
           double maxsra[50]; ArrayInitialize(maxsra,0); maxsra[0]=sra[ArrayMaximum(sra,18,0)];
           
//if(sra[0]<1 || ap[2]<0.5){ return; }
           
//high sra risks ovb loss. 


          // if(maxsra[0]<1){return;} //has dependencies, conditions, etc.  
            // if(maxsra[0]<sp[0]){return;}  //dependencies above
             //sra greater than the others?
             
         
            // if(rm[0]>sra[0]){return;}        if(rm[1]>sra[1]){return;}     // if(rm[2]>sra[2]){return;}   
                // if(rm[3]>sra[3]){return;}      if(rm[4]>sra[4]){return;}   
               // if(sra[0]<1 || sra[0]>2){return;}
               
          
               //if(ra[2]<1 || slp[1]<1 || ra[2]>=(slp[2]*2) ){ return; }
                
               //sra on its own has an overbought risk. 
                
                /*
                strong?

1.2.0.0 st 87.78 slp 34.00 ac 17.50 ra 11.50 r 41.50 h 51.60 v 80.00 sp 0.39 sr 0.82 ap 0.20 ar 0.42 acs 0.51 sra 2.96 slh 0.66 ach 0.34   rm 2.96 rmd 0.00
5.3.0.1 st 94.94 slp 74.33 ac 23.33 ra -28.00 r 99.33 h 114.20 v 80.00 sp 0.78 sr 0.75 ap 0.25 ar 0.23 acs 0.31 sra 0.00 slh 0.65 ach 0.20   rm 0.78 rmd -0.78
15.2.0.2 st 76.33 slp 63.00 ac 45.50 ra -3.50 r 157.00 h 99.60 v 1227.00 sp 0.83 sr 0.40 ap 0.60 ar 0.29 acs 0.72 sra 0.00 slh 0.63 ach 0.46   rm 0.83 rmd -0.83
15.5.0.3 st 42.39 slp -10.00 ac 21.80 ra 13.60 r 142.80 h 99.60 v 1227.00 sp 1.79 sr 0.37 ap 0.51 ar 0.15 acs 0.00 sra 0.00 slh 0.33 ach 0.22   rm 1.79 rmd -1.79
15.10.0.4 st 42.16 slp 25.30 ac 19.50 ra 24.40 r 153.50 h 99.60 v 1227.00 sp 0.60 sr 0.16 ap 0.46 ar 0.13 acs 0.77 sra 1.04 slh 0.25 ach 0.20   rm 1.04 rmd 0.00
sp[0] 0.39 0.78 0.83 1.79 minslp -10.00 avgslp[0] 57.11 37.33 avgsp[0] 0.67 0.88 avgac 28.78 25.53 avgra -6.67 3.60
 
                */
  double rmdmax=rmd[ArrayMaximum(rmd,5,0)];  double rmdmin=rmd[ArrayMinimum(rmd,5,0)];  double rmmax=rm[ArrayMaximum(rm,5,0)];
       // if(rmdmax<0 || rmdmin<= -2){return;}     if(rmmax<1.7){return;}    if(avgra[0]<1){return;}
          
       
Print("\n",disp[0],"\n",disp[1],"\n",disp[2],"\n",disp[3],"\n",disp[4],"\n",
 "sp[0] ",sd(sp[0],2)," ",sd(sp[1],2)," ",sd(sp[2],2)," ",sd(sp[3],2)," minslp ",sd(minslp[0],2)," avgslp[0] ",sd(avgslp[0],2),
  " ",sd(avgslp[1],2)," avgsp[0] ",sd(avgsp[0],2)," ",sd(avgsp[1],2)," avgac ",sd(avgac[0],2)," ",sd(avgac[1],2),
   " avgra ",sd(avgra[0],2)," ",sd(avgra[1],2));
  
  //slow test speed, consider sp restrictions?
    RefreshRates();  
     if(OrderSend(Symbol(),OP_BUY,0.01,Ask,slip,Ask-(290*Point),Ask+(8*Point),"",magic,0,clrGreen)==1)
              {  if(OrdersTotal()>0){ 
                 OrdersSent++; OrderMng();   }
                return; 

                 }else if(OrdersTotal()==0){ Print("OrderSend err ",GetLastError());  return;
              }
           
       
  return;
  
  
  
  
  
  
  

  
  
  
   
      if(slp[0]<MSA){return;}  Data(5,3,0,6);  if(slp[6]<MSA){return;} Data(15,2,0,12);   if(slp[12]<MSA){return;}
        Data(1,2,1,1);  if(slp[1]<MSA){return;}   Data(1,5,0,2);if(slp[2]<MSA){return;}
         Data(1,5,1,3);    if(slp[3]<MSA){return;}     Data(1,10,0,4); if(slp[4]<MSA){return;}
         Data(1,10,1,5); if(slp[5]<MSA){return;}
          
        
 //M15 Data
     Data(15,2,1,13); if(slp[13]<MSA){return;} Data(15,5,0,14);  if(slp[14]<MSA){return;}

  //---- Warning: NormalizeDouble is shitty and buggy in MQL5, 
    //  a lot of small numbers are being added after the desired digits after the decimal point.
      //Fix the rounding / normalization. 
      
  //WARNING: MQL5 fucking sucks. Try to do well anyway. Don't just use sp restrictions.
  //add maxht and min slp filts. 
  
     
//M5 Data
  Data(5,3,1,7); if(slp[7]<MSA){return;} Data(5,5,0,8);   if(slp[8]<MSA){return;}
   double min=0.05;  Data(5,5,1,9); if(slp[9]<MSA){return;} Data(5,10,0,10); if(slp[10]<MSA){return;}
   Data(5,10,1,11); if(slp[11]<MSA){return;} Data(15,5,1,15);  if(slp[15]<MSA){return;}
    Data(15,10,0,16); if(slp[16]<MSA){return;}
  
  
 //default min 0.1
   if(ar[16]<min && sp[16]<min){ w[0]++; w[4]++; } Data(15,10,1,17); 
      ArrayInitialize(minslp,0); minslp[0]=slp[ArrayMinimum(slp,18,0)]; if(minslp[0]<= -210){ FC[0]++; FC[9]++;   return;}
     if(minslp[0]<MSA){ FC[0]++; FC[9]++;   return;}
   double maxh[50]; ArrayInitialize(maxh,0); maxh[0]=h[ArrayMaximum(h,18,0)];  if(maxh[0]>=210){ FC[0]++; FC[10]++;   return;}
   
   double maxslh=slh[ArrayMaximum(slh,18,0)]; 
     ArrayInitialize(avgslp,0);  avgslp[0]=(slp[0]+slp[1])/2;   if(avgslp[0]<1){return;}
     avgslp[1]=(slp[6]+slp[7])/2;   if(avgslp[1]<1){return;}  avgslp[2]=(slp[12]+slp[13])/2;     if(avgslp[2]<0){return;}
     
  double avgap[50]; ArrayInitialize(avgap,0);  avgap[0]=(ap[0]+ap[1])/2; if(avgap[0]<0.2){return;}
       avgap[1]=(ap[6]+ap[7])/2; if(avgap[1]<0.2){return;}  avgap[2]=(ap[12]+ap[13])/2; if(avgap[2]<0.2){return;}
         
     if(sp[12]<1 || sp[12]>=1.7){ w[0]++; w[1]++; } 
//M1 Data
    if(ar[4]<0.1){ w[0]++; w[1]++;  } if(sp[4]<0.1){ w[0]++; w[2]++; }   if(ar[8]<min && sp[8]<min){ w[0]++; w[3]++; }
     
     /*strong
     1.2.0.0 st 74.16 slp 4.00 ac -3.00 ra 9.50 r 7.50 h 17.80 v 9.00 sp 0.05 sr 0.53 ap 0.18 ar 0.48 acs 0.00 sra 0.42 slh 0.22 ach 0.35  
1.2.1.1 st 86.67 slp 7.00 ac -12.50 ra -4.50 r 19.00 h 31.60 v 91.00 sp 0.08 sr 0.37 ap 0.18 ar 0.49 acs 0.00 sra 0.00 slh 0.22 ach 0.27  
1.5.0.2 st 90.53 slp 13.80 ac -0.40 ra -2.20 r 20.20 h 17.80 v 9.00 sp 0.15 sr 0.68 ap 0.02 ar 0.08 acs 0.00 sra 0.00 slh 0.78 ach 0.06  
1.5.1.3 st 92.07 slp 14.20 ac 1.80 ra -2.00 r 23.80 h 31.60 v 91.00 sp 0.15 sr 0.60 ap 0.02 ar 0.08 acs 0.13 sra 0.00 slh 0.45 ach 0.06  
1.10.0.4 st 91.39 slp 8.10 ac -0.10 ra -2.00 r 20.10 h 17.80 v 9.00 sp 0.09 sr 0.40 ap 0.02 ar 0.09 acs 0.00 sra 0.00 slh 0.46 ach 0.06  
1.10.1.5 st 92.83 slp 8.20 ac 1.90 ra 1.10 r 22.20 h 31.60 v 91.00 sp 0.09 sr 0.37 ap 0.02 ar 0.09 acs 0.23 sra 7.45 slh 0.26 ach 0.06  
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15: 
5.3.0.6 st 70.75 slp 16.33 ac 10.33 ra -11.00 r 44.67 h 47.80 v 403.00 sp 0.23 sr 0.37 ap 0.15 ar 0.23 acs 0.63 sra 0.00 slh 0.34 ach 0.22  
5.3.1.7 st 41.95 slp 6.00 ac 21.33 ra 30.99 r 35.33 h 50.20 v 777.00 sp 0.14 sr 0.17 ap 0.51 ar 0.60 acs 3.56 sra 0.19 slh 0.12 ach 0.42  
5.5.0.8 st 48.08 slp 2.40 ac 5.40 ra -10.80 r 43.20 h 47.80 v 403.00 sp 0.05 sr 0.06 ap 0.11 ar 0.13 acs 2.25 sra 0.00 slh 0.05 ach 0.11  
5.5.1.9 st 25.98 slp -3.00 ac 16.20 ra 25.40 r 41.80 h 50.20 v 777.00 sp 0.28 sr 0.37 ap 0.62 ar 0.39 acs 0.00 sra 0.00 slh 1.26 ach 0.32  
5.10.0.10 st 33.94 slp -2.80 ac 7.70 ra 5.90 r 47.20 h 47.80 v 403.00 sp 0.03 sr 0.02 ap 0.23 ar 0.16 acs 0.00 sra 0.00 slh 0.14 ach 0.16  
5.10.1.11 st 18.42 slp -10.50 ac 1.80 ra 2.30 r 46.60 h 50.20 v 777.00 sp 0.08 sr 0.06 ap 0.10 ar 0.04 acs 0.00 sra 0.00 slh 2.43 ach 0.04  
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15: 
15.2.0.12 st 39.63 slp 32.50 ac 75.00 ra 71.00 r 50.50 h 13.20 v 403.00 sp 0.82 sr 0.64 ap 1.89 ar 1.49 acs 2.31 sra 0.46 slh 2.46 ach 5.68  
15.2.1.13 st 31.25 slp -42.50 ac 4.00 ra 35.00 r 79.00 h -0.60 v 2586.00 sp 0.83 sr 0.33 ap 0.13 ar 0.05 acs 0.00 sra 0.00 slh 0.04 ach 2.86  
15.5.0.14 st 23.57 slp -13.80 ac -12.40 ra -37.20 r 64.60 h 13.20 v 403.00 sp 0.25 sr 0.13 ap 1.02 ar 0.29 acs 0.00 sra 0.00 slh 0.71 ach 1.40  
15.5.1.15 st 24.21 slp -1.40 ac 24.80 ra 40.40 r 84.60 h -0.60 v 2586.00 sp 0.13 sr 0.06 ap 1.02 ar 0.29 acs 0.00 sra 0.00 slh 0.52 ach 17.71  
15.10.0.16 st 36.07 slp 2.10 ac 4.20 ra -0.40 r 96.10 h 13.20 v 403.00 sp 0.06 sr 0.02 ap 0.12 ar 0.04 acs 2.00 sra 0.00 slh 0.16 ach 0.32  
15.10.1.17 st 39.38 slp -2.10 ac 4.60 ra 2.90 r 98.90 h -0.60 v 2586.00 sp 0.51 sr 0.15 ap 0.12 ar 0.05 acs 0.00 sra 0.00 slh 0.10 ach 3.29 
 obc 5 4 5 obc[3] 4 0 0 0 0 aob 2 2 psc 11 8 6 psc[3] 5 3 2 2 1 pac 13 7 2 pac[3] 0 6 5 5 2  pra 10 7 2 pra[3] 1 4 1 4 1 nsc 7 3 0 
 nsc[3] 0 3 1 4 2
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15: maxsp 0.83 (1.38)  0.15 0.83 0.83 0.23 0.83 0.83
 maxsr 0.68 (0.6)  0.68 0.64 0.64 0.68 0.64 0.33 maxap 1.89 (0.9)  0.18 1.89 1.89 maxar 1.49 (0.6)  0.49 1.49 1.49 
 avgac -7.75 (8)  11.07 (10)  1.75 (4)  avgra 2.50 (9)  9.99 (6)  53.00 (1+)  spd -0.18 -0.60 -0.01
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15: pnr 1.0 (17)  2.0 (16)  0.0 0.0 1.0 2.0 0.0 (5)  0.0 (4)  
maxpnr 2.0 (17)  pna 2.0 (3)  3.0 (3)  0.0 (5)  0.0 0.0 0.0 5.0 (1)  2.0 (1)  maxpna 5.0 maxh 50.20 31.60 50.20 13.20 (5)  
minslp -13.80 4.00 -13.80 -13.80 maxslp 14.2 (28)  14.2 (16)  6.3 2.1 maxacs 3.56 (1.7)  0.23 (1.8)  3.56 2.31 
maxslh 2.46 (0.7)  0.78 (0.5)  2.46 2.46 minac -12.50 -12.50 -12.40 minra -37.2 2.5 -4.5
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15:  acr 0.00 (2)  0.00 0.00 
mmr 1.03 (2)  3.55 (5)  0.46 (2)  0.15 (1)  avgmmr 1.39 (2.9)  maxmmr  3.55 minmmr 0.15 mma 1.98 0.15 2.00 2.00 avgmma 1.38 (2.76)  
maxmma  2.00 (4)  minmma 0.15 (0.27) ssr 0.57 (1.05)  0.63 (1.11)  1.67 (0.33)  -1.43 (0.5)  avgssr 0.29 (1.96)  maxssr 1.90 (1.46) 
 minssr -1.43 (0.26) acss 4 avgar 0.24 (0.21)  0.42 (0.56)  0.77 (0.3)  avgsr 0.52 (0.55)  0.27 (0.54)  0.49 (0.52) 
  avgsra 0.08 (2)  0.10 (0.9)  0.23 (0.4)  avgsp 0.10 (0.16)  0.19 (0.37)  0.83 (0.66)  maxavgsr 0.52 (0.55)  maxavgsra 0.23 (3)  
  maxavgsp 0.83 (0.66)  avgacs 0.00 (0.86)  2.09 (0.43)  1.15 (0.49)  avgslp 5.50 (10+)  6.15 (10+)  -12.05 (3+)  
  avgap 0.18 (0.1)  0.33 (0.15)  1.01 (0.3)  
0	23:00:23.248	2011.07.07 21:18:00  May 23 2019 d ratio restriction EURUSD,M15:   w 43 2 1 w[3] 0 0 0 w[6] 1 0 1 w[9] 1 1 1 w[12] 0 0 0 
w[15] 0 1 0 w[18] 0 0 0 w[21] 1 1 0 w[24] 1 0 1 0 0 0  w[30] 0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0  w2 1 0 0 w2[3] 0 0 0 w2[6] 0 1 0 
w2[9] 0 0  nac 5 2 4 1 0 0 1 1 nra 9 4 5 nra[3] 1 2 2 2 1 t 6
     */
        //max ac, max/min slope ratio mmr, min slope absval
    double maxac[50],minac[50]; ArrayInitialize(maxac,0); ArrayInitialize(minac,0); maxac[0]=ac[ArrayMaximum(ac,18,0)];  
       maxac[1]=ac[ArrayMaximum(ac,6,0)]; maxac[2]=ac[ArrayMaximum(ac,12,6)]; maxac[3]=ac[ArrayMaximum(ac,18,12)];
      
       minac[0]=ac[ArrayMinimum(ac,18,0)];   minac[1]=ac[ArrayMinimum(ac,6,0)]; minac[2]=ac[ArrayMinimum(ac,12,6)]; 
         minac[3]=ac[ArrayMinimum(ac,18,12)];
      double mma[50],maa[50]; ArrayInitialize(mma,0);  ArrayInitialize(maa,0);  maa[0]=abs(minac[0]); if(maa[0]!=0){ mma[0]=maxac[0]/maa[0]; }
     maa[1]=abs(minac[1]); if(maa[1]!=0){ mma[1]=maxac[1]/maa[1]; } 
         maa[2]=abs(minac[2]); if(maa[2]!=0){ mma[2]=maxac[2]/maa[2]; }
          maa[3]=abs(minac[3]); if(maa[3]!=0){ mma[3]=maxac[3]/maa[3]; }    
          
           double ssr[50]; ArrayInitialize(ssr,0); if(slp[1]!=0){ssr[0]=slp[0]/slp[1];} if(slp[6]!=0){ssr[1]=slp[0]/slp[6];} 
  if(slp[8]!=0){ssr[2]=slp[0]/slp[8];}  if(slp[10]!=0){ssr[3]=slp[0]/slp[10];}  if(slp[12]!=0){ssr[4]=slp[0]/slp[12];}  
if(slp[14]!=0){ssr[5]=slp[0]/slp[14];}  if(slp[16]!=0){ssr[6]=slp[0]/slp[16];}
double minssr=ssr[ArrayMinimum(ssr,7,0)]; if(minssr<= -2 //<= -1.4
   ){ FC[0]++; FC[12]++; return;} 
  double maxssr=ssr[ArrayMaximum(ssr,7,0)];    if(maxssr<1){return;}
 double avgssr=(ssr[1]+ssr[2]+ssr[3])/3;
 
     
    
   double minslh=slh[ArrayMinimum(slh,18,0)];
   
    double maxslh2=slh[ArrayMaximum(slh,6,0)]; double minslh2=slh[ArrayMinimum(slh,6,0)];
    
    double maxslh3=slh[ArrayMaximum(slh,12,6)]; double minslh3=slh[ArrayMinimum(slh,12,6)];
    
    double maxslh4=slh[ArrayMaximum(slh,18,12)]; double minslh4=slh[ArrayMinimum(slh,18,12)];
       ArrayInitialize(avgra,0);  avgra[0]=(ra[0]+ra[1])/2;  avgra[1]=(ra[6]+ra[7])/2;  avgra[2]=(ra[12]+ra[13])/2;
     
       double minra=ra[ArrayMinimum(ra,18,0)]; double minra2=avgra[ArrayMinimum(avgra,3,0)];    double minra3=ra[ArrayMinimum(ra,6,0)];   
      minslp[1]=slp[ArrayMinimum(slp,6,0)]; minslp[2]=slp[ArrayMinimum(slp,12,6)]; 
         minslp[3]=slp[ArrayMinimum(slp,18,12)]; if((minslp[0]<= -1 //<= -5 
         || minra<= -1 //<= -5
         ) && minra2<= -1 //<= -5
         ){ FC[0]++; FC[11]++; return; }
         
             if(avgssr>=10  ){ w[0]++; } //>=2
         
      double acr[50]; ArrayInitialize(acr,0); //accel vs accel ratio
       ArrayInitialize(avgsp,0); 
       if(ac[0]>0  ){
        if( ac[2]>1){acr[0]=ac[0]/ac[2]; } // careful, sometimes the program tries to CHEAT and CHANGE the accel values.
         if( ac[4]>1){acr[1]=ac[0]/ac[4]; } if( ac[6]>1){acr[2]=ac[0]/ac[6]; }}
 
     ArrayInitialize(avgac,0);  avgac[0]=(ac[0]+ac[1])/2;  avgac[1]=(ac[6]+ac[7])/2;  avgac[2]=(ac[12]+ac[13])/2;
     
       
    avgsp[0]=(sp[0]+sp[1]+sp[2]+sp[3]+sp[4])/5;  avgsp[1]=(sp[6]+sp[7])/2;  
      avgsp[2]=(sp[12]+sp[13])/2;  double maxavgsp=avgsp[ArrayMaximum(avgsp,3,0)];
       double avgacs[50]; ArrayInitialize(avgacs,0);  avgacs[0]=(acs[0]+acs[1])/2;  avgacs[1]=(acs[6]+acs[7])/2; 
        
        avgacs[2]=(acs[12]+acs[13])/2; 
          maxh[1]=h[ArrayMaximum(h,6,0)];  maxh[2]=h[ArrayMaximum(h,12,6)]; maxh[3]=h[ArrayMaximum(h,18,12)];
          
  
    double pna[50]; ArrayInitialize(pna,0); //max 7 ?
    
   if(pac[0]!=0 && nac[0]!=0){ pna[0]=pac[0]/nac[0]; }  if(pac[1]!=0 && nac[1]!=0){ pna[1]=pac[1]/nac[1]; }
   if(pac[2]!=0 && nac[2]!=0){ pna[2]=pac[2]/nac[2]; }  if(pac[3]!=0 && nac[3]!=0){ pna[3]=pac[3]/nac[3]; }
    if(pac[4]!=0 && nac[4]!=0){ pna[4]=pac[4]/nac[4]; }  if(pac[5]!=0 && nac[5]!=0){ pna[5]=pac[5]/nac[5]; }
     if(pac[6]!=0 && nac[6]!=0){ pna[6]=pac[6]/nac[6]; }  if(pac[7]!=0 && nac[7]!=0){ pna[7]=pac[7]/nac[7]; }
     
     
  double pnr[50]; ArrayInitialize(pnr,0); //max 7 ?
   if(psc[0]!=0 && nsc[0]!=0){ pnr[0]=psc[0]/nsc[0]; }  if(psc[1]!=0 && nsc[1]!=0){ pnr[1]=psc[1]/nsc[1]; }
   if(psc[2]!=0 && nsc[2]!=0){ pnr[2]=psc[2]/nsc[2]; }  if(psc[3]!=0 && nsc[3]!=0){ pnr[3]=psc[3]/nsc[3]; }
    if(psc[4]!=0 && nsc[4]!=0){ pnr[4]=psc[4]/nsc[4]; }  if(psc[5]!=0 && nsc[5]!=0){ pnr[5]=psc[5]/nsc[5]; }
     if(psc[6]!=0 && nsc[6]!=0){ pnr[6]=psc[6]/nsc[6]; }  if(psc[7]!=0 && nsc[7]!=0){ pnr[7]=psc[7]/nsc[7]; }
     
     
  double maxpnr=pnr[ArrayMaximum(pnr,8,0)];  double maxpna=pna[ArrayMaximum(pna,8,0)];   double avgar[50]; ArrayInitialize(avgar,0);
   avgar[0]=(ar[0]+ar[1]+ar[2]+ar[3]+ar[4])/5; if(avgar[0]>ar[5]){}else{w[0]++; w[5]++;}
    avgar[1]=(ar[6]+ar[7])/2;    if(avgar[1]>ar[7]){}else{w[0]++; w[6]++;}
     avgar[2]=(ar[12]+ar[13])/2;  if(avgar[2]>ar[15]){}else{w[0]++; w[7]++;}
     
    double avgsr[50]; ArrayInitialize(avgsr,0); avgsr[0]=(sr[0]+sr[1]+sr[2]+sr[3]+sr[4])/5;   avgsr[1]=(sr[6]+sr[7])/2;  
      avgsr[2]=(sr[12]+sr[13])/2;   double maxavgsr=avgsr[ArrayMaximum(avgsr,3,0)];
      
       double avgsra[50]; ArrayInitialize(avgsra,0); avgsra[0]=(sra[0]+sra[1]+sra[2]+sra[3]+sra[4])/5;   avgsra[1]=(sra[6]+sra[7])/2;  
      avgsra[2]=(sra[12]+sra[13])/2;   double maxavgsra=avgsra[ArrayMaximum(avgsra,3,0)];
       
      if(sr[16]<0.1 && maxavgsr<0.7 && maxavgsp<0.9){ w[0]++; }
          if(avgar[2]>=0.4 && avgsr[0]>=0.7 && avgsr[2]>=0.7 && avgsp[2]>=0.7){}else{w[0]++;}
           

           
//max slope, max/min slope ratio mmr, min slope absval
   double maxslp[50]; ArrayInitialize(maxslp,0); maxslp[0]=slp[ArrayMaximum(slp,18,0)];  
    maxslp[1]=slp[ArrayMaximum(slp,6,0)]; maxslp[2]=slp[ArrayMaximum(slp,12,6)]; maxslp[3]=slp[ArrayMaximum(slp,18,12)];
    
double mmr[50],msa[50]; ArrayInitialize(mmr,0);  ArrayInitialize(msa,0);  msa[0]=abs(minslp[0]); if(msa[0]!=0){ mmr[0]=maxslp[0]/msa[0]; }
     msa[1]=abs(minslp[1]); if(msa[1]!=0){ mmr[1]=maxslp[1]/msa[1]; } 
         msa[2]=abs(minslp[2]); if(msa[2]!=0){ mmr[2]=maxslp[2]/msa[2]; }
          msa[3]=abs(minslp[3]); if(msa[3]!=0){ mmr[3]=maxslp[3]/msa[3]; } double maxmmr=mmr[ArrayMaximum(mmr,4,0)];
           double avgmmr=(mmr[1]+mmr[2]+mmr[3])/3;  double minmmr=mmr[ArrayMinimum(mmr,4,0)];
             

          
          double maxmma=mma[ArrayMaximum(mma,4,0)];
           double avgmma=(mma[1]+mma[2]+mma[3])/3;  double minmma=mma[ArrayMinimum(mma,4,0)];
              if(avgmmr>=10 && avgmmr<=12 && avgssr>=0.6 && avgssr<=3){}else{ w[0]++; }
            
  //acs
   double maxacs[50]; ArrayInitialize(maxacs,0); maxacs[0]=acs[ArrayMaximum(acs,18,0)];  maxacs[1]=acs[ArrayMaximum(acs,6,0)];
  maxacs[2]=acs[ArrayMaximum(acs,12,6)]; maxacs[3]=acs[ArrayMaximum(acs,18,12)];
  
  //---- Each and every filter should have a position clause, a speed /slope/velocity clause, acceleration, and range
       if(maxacs[0]>=12 //default >=2 >=10
       ){ w[0]++; }
  
  //add pnr mmr ssr ASAP
  
 //ap
 double maxap[50]; ArrayInitialize(maxap,0); maxap[0]=ap[ArrayMaximum(ap,18,0)];  maxap[1]=ap[ArrayMaximum(ap,6,0)];
  maxap[2]=ap[ArrayMaximum(ap,12,6)]; maxap[3]=ap[ArrayMaximum(ap,18,12)];
 
 //ar
 double maxar[50]; ArrayInitialize(maxar,0); maxar[0]=ar[ArrayMaximum(ar,18,0)];  maxar[1]=ar[ArrayMaximum(ar,6,0)];
  maxar[2]=ar[ArrayMaximum(ar,12,6)]; maxar[3]=ar[ArrayMaximum(ar,18,12)];
 
 //sp
  double maxsp[50]; 
 ArrayInitialize(maxsp,0); maxsp[0]=sp[ArrayMaximum(sp,18,0)];  maxsp[1]=sp[ArrayMaximum(sp,6,0)];
  maxsp[2]=sp[ArrayMaximum(sp,12,6)]; maxsp[3]=sp[ArrayMaximum(sp,18,12)];
    maxsp[4]=sp[ArrayMaximum(sp,5,2)];   maxsp[5]=sp[ArrayMaximum(sp,11,7)];  maxsp[6]=sp[ArrayMaximum(sp,17,13)]; 
 //sr
 double maxsr[50]; ArrayInitialize(maxsr,0); maxsr[0]=sr[ArrayMaximum(sr,18,0)];  maxsr[1]=sr[ArrayMaximum(sr,6,0)];
  maxsr[2]=sr[ArrayMaximum(sr,12,6)]; maxsr[3]=sr[ArrayMaximum(sr,18,12)];
   maxsr[4]=sr[ArrayMaximum(sr,5,2)];   maxsr[5]=sr[ArrayMaximum(sr,11,7)];  maxsr[6]=sr[ArrayMaximum(sr,17,13)]; 
 
 
 double Min[50],Max[50]; ArrayInitialize(Min,0); ArrayInitialize(Max,0); 
  Min[0]=0.9; //default 1
   Max[0]=4; Max[1]=4; //defaults 4 3 
    
  
  double spd[50]; ArrayInitialize(spd,0);   spd[0]=sp[0]-maxsp[4];  spd[1]=sp[6]-maxsp[5];  spd[2]=sp[12]-maxsp[6];
  
 //critical 
 double SPD=0.2; //default 0.5, 0.25 might be too low
 double max[50]; ArrayInitialize(max,0); max[0]=avgar[ArrayMaximum(avgar,3,0)];  max[1]=avgsr[ArrayMaximum(avgsr,3,0)]; 
  max[2]=avgsp[ArrayMaximum(avgsp,3,0)];   max[3]=avgacs[ArrayMaximum(avgacs,3,0)];  // max[4]=avgslp[ArrayMaximum(avgslp,3,0)]; 
    max[4]=avgap[ArrayMaximum(avgap,3,0)];     max[5]=max[ArrayMaximum(max,6,0)];     
       
 
  double rmin=1.01; 
    double rmax=5; //default 5, 10 risky
 
 
  if(sp[6]>=(maxsp[1]+SPD)){}else{   w[0]++; w[8]++; }
   if(sp[12]>=(maxsp[3]+SPD)){}else{     w[0]++; w[9]++; } // strong but tight, use for notation, expansion, branching into
  
   if((sp[6]>=(maxsp[1]+SPD) || sp[6]>=(sp[7]+SPD))
     || (sp[12]>=(maxsp[3]+SPD)|| sp[12]>=(sp[13]+SPD))){}else{  w[0]++; w[10]++; }
   // the ar and sp filts also. 
   
  
  //strong but tight
  
 if(psc[7]>=2 && pac[3]>=2 && pra[4]>=2 && nsc[0]<=5 && maxsr[0]>=0.5 && maxap[0]>=0.5 && maxar[0]>=0.5){}else{ w[0]++; w[11]++; }
 
 if(obc[7]>0 && pac[3]<=5){ w[0]++; w[12]++; }
 if(maxap[0]>=2 && obc[3]>=4 && pac[3]<5 && ra[6]<1){ w[0]++; w[13]++; }
 

 if(st[7]<50 && st[14]<50 && st[15]<50 && st[16]<50 && st[17]<50){}else{ w[0]++; w[14]++;} //20 50 20 30 20
 //if(w[5]>0){ //w[5] is critical but it's unknown if it is strong/adaptable all the time. 
  if(maxsp[0]>=0.7 && maxsp[0]<2){}else{ w[0]++; w[15]++;}//1.41    1.65
  
  //maxsr 
  if(maxsr[0]>=0.7 && maxsr[0]<2){}else{ w[0]++; w[16]++;} //0.9    1.65
     //maxap 
       if(maxap[0]>=0.7 && maxap[0]<2){}else{ w[0]++; w[17]++;} //1.41    1.65
    
    //maxar 
       if(maxar[0]>=0.7 && maxar[0]<2){}else{ w[0]++; w[18]++;} //0.7    1.65
  
    if(pac[1]<6 && pra[1]<10 && psc[0]<10){ w[0]++; w[19]++; }
    if(maxpna<=0 && maxpnr<=0){ w[0]++; w[20]++; }
    
    //untested
 if(avgmmr>=1 && avgmmr<=150 //<=100
  && avgssr>=1 && avgssr<=150 //<=100
  ){}else{ w[0]++; w[21]++; }//weak
 
 //untested
 if(avgmmr>=1 && avgmmr<=25 //>=1 <=20
  && avgssr>=1 && avgssr<=25 //>=1 <=20
  ){}else{ w[0]++; w[22]++; }//weak ovb losses
if(acss>=1){}else{ w[0]++; w[23]++; } if(acs[0]>=(acs[13]+0.1 // +0.2
)){}else{ w[0]++; w[24]++; }
if(maxpna>=1 && maxpnr>=1){}else{ w[0]++; w[25]++; }

if(acs[2]>=(acs[7]+0.1 //+0.2
)){}else{ w[0]++; w[26]++; }

if(acs[6]>=(acs[14]+0.1 // +0.2
)){}else{ w[0]++; w[27]++; }

 if(avgar[2]>=0.1 //defaule >=0.5 >=0.2
 && acs[12]>=0.1 //default >=1 >=0.5
 ){}else{ w[0]++; w[28]++; }

if(sr[6]>=0.1 //default >=0.5 >=0.3
 && sr[6]<15 //default <1 <3 <10
   ){}else{ w[0]++; w[29]++; }

if(avgsr[0]>=0.1 //>=0.2
 && avgsr[2]>=0.1 //>=0.2
 && avgar[0]>=0.1  //>=0.2
 && avgar[2]>=0.1 //>=0.2
 ){}else{ w[0]++; w[30]++; }
//need averages for each timeframe
if(avgsp[0]>=0.1  // default >=0.19
&& avgsp[1]>=0.1  // >=0.2
&& avgsp[2]>=0.1 // >=1.2
){}else{ w[0]++; w[31]++; }
if(obc[0]>=6 //>=6
 && nac[0]>=2 //>=2
  && avgac[0]<5  // <5
  && avgac[2]<1 //<1
  ){w[0]++; } //may 10 2011
if(sr[15]>=0.001 //>=0.01
 && sr[15]<=2 //<=0.02
 ){}else{ w[0]++; w[32]++;  }
// avgac 9.50 -1.55 -7.50 avgmmr 0.60 (2.9)  avgssr 2.02 (1.96)  avgar 0.23 0.22 0.28 avgsr 0.30 0.27 0.37 avgsp 0.13 0.19 0.42 
 // maxavgsr 0.37 maxavgsp 0.42 avgacs 0.84 0.32 0.40 avgslp 12.50 6.57 7.75
 
 // avgac 11.25 11.37 -4.90  avgar 0.27 0.40 0.24 avgsr 0.49 0.41 0.42 avgsp 0.26 0.42 0.75 avgacs 0.27 1.24 0.02 avgslp 29.75 9.14 11.25 
 // avgap 0.23 0.43 0.54
 
 
 //needs work on avg slope, avg ac, avg sp, etc., avoid weak slopes, 
 //avoid ovb 
 
 //avgacs
   
  if(avgacs[0]<10 // <2 
   && avgacs[0]>=0.1 //>=0.1
      ){}else{ w[0]++;  w[33]++; } //0.7
      
//avg ar 
if(avgar[0]<10 && avgar[0]>=0.1){}else{ w[0]++; w[34]++;  }//>=0.4
    if(avgar[1]<5 && avgar[1]>=0.01 //>=0.1
      ){}else{ w[0]++; w[35]++;  } //0.7
      
    //avgsp 
   
 if(avgsp[0]<10 && avgsp[0]>=0.1){}else{ w[0]++; w[36]++;  } //0.7
   if(avgsp[1]<5 && avgsp[1]>=0.01//>=0.1
     ){}else{ w[0]++;  w[37]++; } //0.7
     
 //avgsr 
 
 if(avgsr[0]<10 && avgsr[0]>=0.1){}else{ w[0]++;  w[38]++; } //0.7
   if(avgsr[1]<5 && avgsr[1]>=0.01 //>=0.1
     ){}else{ w[0]++; w[39]++;  } //0.7
     
// 1 EUR / USD X 

// 1 EUR / USD x   1 EUR  / USD x    1 EUR / USD x 
//pnr 17.0 15.0 5.0 5.0 0.0 0.0 0.0 0.0 maxpnr 17.0 pna 1.0 4.0 0.0 1.0 1.0 3.0 5.0 0.0 
if((pnr[0]>=2 || pnr[1]>=2)//>=10
 && (pnr[0]>pnr[1] || pnr[1]>pnr[2])){}else{ w[0]++;  w[40]++; }

if((pna[0]>=2 || pna[1]>=2) //>=10
 && (pna[0]>pna[1] || pna[1]>pna[2])){}else{  w[0]++; w[41]++; }


if(w[0]>=15 && obc[0]>=5 && obc[1]>=3 && nac[0]>=3 && nac[1]>=2 && ra[8]<1){  w[0]++; w[42]++;} //ovbf jan 7 2011

if(nac[0]>=5 && nac[1]>=2 && ra[12]<1 && (slp[4]<5 || ac[4]<5) && maxssr>=10 && minslp[0]<= -5 ){  w[0]++; w[43]++;
  } //negslope jan 27 2011
  
     if(avgar[2]<1.5  //<1
          && avgar[2]>=0.01 //>=0.1
                ){}else{    w[0]++; w[44]++; } //0.7
                
        if(avgsp[2]<1.5 //<1
        && avgsp[2]>=0.01 //>=0.1
             ){}else{    w[0]++; w[45]++; } //0.7
             
    if(avgsr[2]<1.5 //<1
       && avgsr[2]>=0.01 //>=0.1
         ){}else{   w[0]++; w[46]++;} //0.7
         
            if(avgacs[1]<5 //<2
    && avgacs[1]>=0.01 //>=0.1
      ){}else{   w[0]++; w[47]++; } //0.7
   
      if(avgacs[2]<1 //<2
        && avgacs[2]>=0.01 //>=0.1
          ){}else{    w[0]++; w[48]++; } //0.7
          

          if(max[3]>=0.9 //>=1
  && max[3]<=2.1 //<=2
  ){}else{   w[0]++; w[49]++;}
  
  int w2[50]; ArrayInitialize(w2,0); 
   if(max[3]>=max[5]  && max[3]>=0.01){}else{   w2[0]++; w2[1]++; } 
    if(nsc[0]>=6   //>=5
    && nsc[1]>=6  //>=5
    && nsc[7]>=6 //>=5
     && nac[0]>=5 //>=2
      ){  w2[0]++; w2[2]++; }
        if(avgsp[0]<0.1 //<0.2
         && avgsp[1]<0.1 //<0.2
         && avgac[0]<0.5 //<1
         ){  w2[0]++; w2[3]++;  }
          if(avgacs[1]<0.05 //<0.1
          ){   w2[0]++; w2[4]++;  }  if(avgslp[0]<0.5 //<1
  ){  w2[0]++; w2[5]++; }
     if(avgslp[1]<0.9 //<1
     ){ w2[0]++; w2[6]++; }      if(avgslp[2]<0.9 //<1
     ){  w2[0]++; w2[7]++; } 
          
if(avgssr>=0.1 //>=1
  && avgssr<=5 //<=2 <=2.8
   ){}else{ w2[0]++; w2[8]++; }

//losing streak feb 2 feb 23 2011, may be at least 1 ovb loss. 
if(obc[0]>=2  && mmr[0]<maxmmr && mmr[1]<maxmmr && ssr[0]<5 && ssr[1]<5){ w2[0]++; w2[9]++; }

if(ra[12]<0 && ra[0]<0 && avgac[1]<0 && mmr[3]<1 && pnr[1]<1 && minslp[0]<= -12){ w2[0]++; w2[10]++; } //feb 22 2011

w[0]=w[0]+w2[0]+obc[0]+nac[0]+nra[0]; 

   int type=0;
        
    if(avgsp[2]>0 && avgsp[2]<0.25){ type=1; 
     }else if(avgsp[2]>=0.25 && avgsp[2]<0.5){ type=2;  
       }else if(avgsp[2]>=0.5 && avgsp[2]<0.75){ type=3; 
         }else if(avgsp[2]>=0.75 && avgsp[2]<1){ type=4; 
           }else if(avgsp[2]>=1){ type=5; }else{type=0;}
       
       //work on types 4 and 5
       
  if(type==4){
           if(avgsp[0]>0 && avgsp[0]<0.25){ type=6; 
     }else if(avgsp[0]>=0.25 && avgsp[0]<0.5){ type=7;  
       }else if(avgsp[0]>=0.5 && avgsp[0]<0.75){ type=8; 
         }else if(avgsp[0]>=0.75 && avgsp[0]<1){ type=9; 
           }else if(avgsp[0]>=1){ type=10; } 
         }
         
          if(type==5){
           if(avgsp[0]>0 && avgsp[0]<0.25){ type=11; 
     }else if(avgsp[0]>=0.25 && avgsp[0]<0.5){ type=12;  
       }else if(avgsp[0]>=0.5 && avgsp[0]<0.75){ type=13; 
         }else if(avgsp[0]>=0.75 && avgsp[0]<1){ type=14; 
           }else if(avgsp[0]>=1){ type=15; } 
         }
       
    //use type assignments, assign filters to types, and measure odds of m15 stat groupings with m1 stat groupings. 
    
    //ovb loss date: feb 2 2011 
      
    
    
   if(pnr[0]<5 || avgsra[0]<2 || avgacs[0]<0.5 || avgacs[0]>=1.5){ //exp softener
    
   if(nac[0]>1){ if(type==7){ if(nac[0]>=5){ w[0]++; }} if(type==3){ if(nac[0]>=5){ w[0]++; }} 
     //before: no nac softener, no 2 top filts.  before 2011a 385 97.66%  after 3 mods: 2011a 538 98.14% 
     
     
     
     if(avgmmr<0.5 //default <1
  || avgmmr>5){FC[0]++; FC[12]++;  w[0]++; } 
 if(avgmma<0.5 //default <1
 || avgmma>5){ FC[0]++; FC[13]++;  w[0]++; } 
 if(avgssr<0.2 || avgssr>5 ){ FC[0]++; FC[14]++;  w[0]++; } 
 
 if(avgar[2]<0.2 || avgar[2]>5){ FC[0]++; FC[15]++;  w[0]++; } 
 
 if(avgacs[2]<0.2 || avgacs[2]>10 //default >5
 ){ w[0]++; } 
 if(avgap[2]<0.2 || avgap[2]>5){ FC[0]++; FC[16]++;  w[0]++; } 
 if(avgslp[2]<1 || avgslp[2]>10){ FC[0]++; FC[17]++;  w[0]++; } 
 if(avgsr[2]<0.2 || avgsr[2]>5){ FC[0]++; FC[18]++;  w[0]++; } 
 if(avgsp[2]<0.2 || 
 avgsp[2]>10 //default >3
 ){ FC[0]++; FC[19]++;  w[0]++;  }  }
 
 
 //loss date 2011  ovb jan 6 7 mar 15 apr 1 apr 5 15 may 23 25,   jun 22 negslope   jun 24   ovb 
  
 //negslope protection
  if(avgslp[0]<1 && avgslp[1]<5 && pnr[0]<5 && pna[0]<5 && maxsp[0]<1){ FC[0]++; FC[20]++;  w[0]++; } //jun 22 2011 negslope
 
 //ovb protection
  if(pnr[0]<5 && obc[0]>=5 && obc[1]>=5 && obc[7]>0 && avgra[2]<1){ FC[0]++; FC[21]++;  w[0]++; }
  
  
  
  if(pnr[0]<5 && pnr[1]<5 && minra<= -10 && minac[0]<= -10 && avgacs[1]<0.4 && avgar[1]<0.5 ){ FC[0]++; FC[22]++;  w[0]++; }
  
   //2011 lossy ovb period jul 15 - aug 25 
  //ovb protection
  if(minra<= -15 && minac[0]<= -30  && avgsra[0]<2  ){ FC[0]++; FC[23]++;  w[0]++; }
  if(minra<= -15 && minac[0]<= -10 &&  ra[6]<1 &&    obc[0]>=5 && obc[4]>=2 && minra2<= -2){  FC[0]++; FC[24]++;  w[0]++; }
  if(minra<= -15 && minac[0]<= -5 &&   nac[0]>=2 &&   ra[0]<1 && nra[0]>=5 &&  obc[0]>=5 && obc[4]>=2 
  && minra2<= -1){  FC[0]++; FC[25]++;  w[0]++; }
  
  if(minra<= -10 && obc[1]>=5 && pnr[0]<10 && 
        minac[0]<= -12 &&   nac[0]>=2 &&   ra[6]<1 && nra[0]>=5 &&  obc[0]>=5 && obc[4]>=1 && minra3<= -1){ FC[0]++; FC[26]++;   w[0]++; }
        
        //needs work
    if(minra<= -10 && obc[1]>=5 && pnr[0]<10 && 
        minac[0]<= -12 &&   nac[0]>=2 &&   ra[6]<1 && nra[0]>=5 &&  obc[0]>=5 && obc[4]>=1 && minra3<= -1){  FC[0]++; FC[27]++;  w[0]++; }    
        
             
    if(minra<= -20 && obc[0]>=5 && pnr[0]<10 && 
        minac[0]<= -2 &&   nac[0]>=1 &&   ra[0]<1 && ra[12]<1 && nra[0]>=5 &&  obc[0]>=5 && obc[3]>=2 
        && minra3<= -20){ FC[0]++; FC[28]++;   w[0]++; } 
        
          if(minra<= -10 && obc[0]>=5 && pnr[0]<10 && ra[10]<1 && 
            minac[0]<= -12 &&   nac[0]>=3 &&   ra[6]<1 && maxsp[0]<1 && nra[0]>=5 &&  obc[1]>=3 && obc[3]>=2 
            && minra3<= -5){  FC[0]++; FC[29]++;  w[0]++; }  
  
  if(maxslh<1 && minra<= -20 && obc[0]>=5 && pnr[0]<10 && ra[10]<1 && ra[0]<1 && pna[0]<1 && 
            minac[0]<= -2 &&   ac[10]<5 &&   ra[12]<1 && maxsp[0]<1 && nra[0]>=5 &&  obc[1]>=2 && obc[3]>=2
             && minra3<= -15){  FC[0]++; FC[30]++;  w[0]++; }  }      

//strong? avgslp 11.25 9.04 5.35

if(avgslp[0]>(avgslp[1]+1) //default +2
 && avgslp[1]>(avgslp[2]+1) //default +3
  && avgslp[0]>1 && avgslp[1]>1 && avgslp[2]>1){}else{ w[0]++; }
 
if(minslp[0]<= -5 // default <= -1, <= -5 works sometimes
){  w[0]++;  }
  //ALWAYS LIMIT MINSLOPE minslp[0]
  
  //ovb loss obc 10 2 5 obc[3] 2 4 0 1 0  pac 10 7 1 pac[3] 1 4 2 5 4  pra 9 7 3 pra[3] 3 3 3 3 2 accel ? 
   //aob?  Accel vs ovb ratio?   pac[0] 10 pra[0] 9 obc[0] 10 
 
    if(ssr[0]<0.5 //default <1
     && mmr[1]<5   //default <5
       && mmr[3]<5  //default <5
        && aob[0]<=1   //default <=1
         && aob[1]<0.9  //default <=0.9
           ){  w[0]++;  }
  
 
  
  if(avgsp[2]<0.75   //default <1
    || avgsp[2]>1.6  //default >1.5
     ){  w[0]++;  }
  
  
  if(avgsr[1]<0.5   //default <0.6
    || avgsr[1]>0.75   //default >0.75
     ){ w[0]++;  }
     
   
    
    //ALWAYS LIMIT MINSLOPE
    
    
    int fs[50],Ws[50]; //filter /warning switches
     fs[0]=0; Ws[0]=1;
     
     if(Ws[0]>0){
    
     if(maxmma<1.1 && ssr[0]<2 && maxssr<2 && mma[0]<1.1){  
     //not enough
 if(maxap[0]>=rmin //>=1 >=2 strong but tight
 && maxap[0]<rmax //<1.5 
 ){}else{ w[0]++; }
 if(mmr[1]>=rmin //>=10 2 
  && mmr[1]<=rmax // <=15 
   ){}else{ w[0]++; }
    if(ssr[1]>=rmin //>=2
     && ssr[1]<=rmax //<=3
      ){}else{ w[0]++; }
    
   if(maxap[3]>=rmin //>=1
    && maxap[3]<rmax //<2
    ){}else{ w[0]++; }
 if(mmr[3]>=rmin //>=10 0.5
  && mmr[3]<=rmax //<=2
    ){}else{ w[0]++; }
    if(ssr[3]>=rmin  //>=1
    && ssr[3]<=rmax  //<=2
       ){}else{ w[0]++; }}}
    
     
  /*strong
  
  1.2.0.0 st 83.84 slp 16.50 ac 10.50 ra 4.00 r 33.50 h 27.80 v 62.00 sp 0.20 sr 0.49 ap 0.13 ar 0.31 acs 0.64 sra 4.13 slh 0.59 ach 0.38  
1.2.1.1 st 75.68 slp 6.00 ac 6.50 ra 14.00 r 26.00 h 37.20 v 144.00 sp 0.08 sr 0.23 ap 0.09 ar 0.25 acs 1.08 sra 0.43 slh 0.16 ach 0.17  
1.5.0.2 st 86.67 slp 9.40 ac 4.00 ra 2.40 r 23.20 h 27.80 v 62.00 sp 0.11 sr 0.41 ap 0.05 ar 0.17 acs 0.43 sra 3.92 slh 0.34 ach 0.14  
1.5.1.3 st 81.44 slp 5.40 ac 1.60 ra 1.20 r 20.40 h 37.20 v 144.00 sp 0.07 sr 0.26 ap 0.02 ar 0.08 acs 0.30 sra 4.50 slh 0.15 ach 0.04  
1.10.0.4 st 87.18 slp 3.30 ac -1.60 ra -3.00 r 19.80 h 27.80 v 62.00 sp 0.04 sr 0.17 ap 0.02 ar 0.06 acs 0.00 sra 0.00 slh 0.12 ach 0.09  
1.10.1.5 st 85.25 slp 4.90 ac 1.40 ra 3.00 r 22.20 h 37.20 v 144.00 sp 0.06 sr 0.22 ap 0.02 ar 0.06 acs 0.29 sra 1.63 slh 0.13 ach 0.04  
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15: 
5.3.0.6 st 88.63 slp 28.00 ac 17.67 ra 14.34 r 60.00 h 50.20 v 244.00 sp 0.32 sr 0.47 ap 0.20 ar 0.29 acs 0.63 sra 1.95 slh 0.56 ach 0.35  
5.3.1.7 st 72.62 slp 10.33 ac 3.33 ra -1.67 r 56.67 h 64.40 v 371.00 sp 0.14 sr 0.18 ap 0.05 ar 0.06 acs 0.32 sra 0.00 slh 0.16 ach 0.05  
5.5.0.8 st 88.63 slp 14.20 ac 2.80 ra -4.20 r 47.80 h 50.20 v 244.00 sp 0.16 sr 0.30 ap 0.03 ar 0.06 acs 0.20 sra 0.00 slh 0.28 ach 0.06  
5.5.1.9 st 72.62 slp 11.40 ac 7.00 ra -0.60 r 48.40 h 64.40 v 371.00 sp 0.16 sr 0.24 ap 0.10 ar 0.14 acs 0.61 sra 0.00 slh 0.18 ach 0.11  
5.10.0.10 st 88.63 slp 4.70 ac 3.00 ra 1.70 r 37.20 h 50.20 v 244.00 sp 0.05 sr 0.13 ap 0.03 ar 0.08 acs 0.64 sra 2.76 slh 0.09 ach 0.06  
5.10.1.11 st 66.09 slp 1.70 ac 1.30 ra -2.60 r 34.30 h 64.40 v 371.00 sp 0.03 sr 0.05 ap 0.02 ar 0.04 acs 0.76 sra 0.00 slh 0.03 ach 0.02  
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15: 
15.2.0.12 st 63.29 slp 45.00 ac 58.00 ra 53.00 r 89.00 h 61.20 v 1517.00 sp 0.71 sr 0.51 ap 0.92 ar 0.65 acs 1.29 sra 0.85 slh 0.74 ach 0.95  
15.2.1.13 st 30.64 slp -13.00 ac 5.00 ra 36.50 r 44.50 h 78.20 v 1333.00 sp 1.65 sr 0.63 ap 0.16 ar 0.11 acs 0.00 sra 0.00 slh 0.53 ach 0.06  
15.5.0.14 st 40.59 slp 17.00 ac 29.60 ra 23.00 r 63.80 h 61.20 v 1517.00 sp 0.42 sr 0.27 ap 0.73 ar 0.46 acs 1.74 sra 0.74 slh 0.28 ach 0.48  
15.5.1.15 st 13.89 slp -12.60 ac 6.60 ra 19.20 r 59.00 h 78.20 v 1333.00 sp 0.86 sr 0.48 ap 0.48 ar 0.11 acs 0.00 sra 0.00 slh 0.36 ach 0.08  
15.10.0.16 st 21.66 slp 0.00 ac 9.30 ra 7.10 r 87.80 h 61.20 v 1517.00 sp 0.06 sr 0.03 ap 0.43 ar 0.11 acs 0.00 sra 0.00 slh 0.86 ach 0.15  
15.10.1.17 st 9.04 slp -9.30 ac 2.20 ra 14.90 r 79.00 h 78.20 v 1333.00 sp 0.28 sr 0.13 ap 0.24 ar 0.03 acs 0.00 sra 0.00 slh 8.22 ach 0.03 
 obc 8 0 5 obc[3] 0 3 0 0 0 aob 2 1 psc 14 10 6 psc[3] 4 6 4 2 2 pac 17 9 5 pac[3] 2 6 2 6 5  pra 13 8 5 pra[3] 4 2 1 6 2 nsc 3 3 0 nsc[3] 0 0 0 3 3
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15:  maxsp 1.65 (1.38)  0.20 1.65 1.65 0.32 1.65 1.65 maxsr 0.63 0.49 0.63 0.63 0.47 0.63 0.63 maxap 0.92 0.13 0.92 0.92 maxar 0.65 0.31 0.65 0.65 avgac 8.50 10.50 4.45 avgra 9.00 6.34 44.75 (1+)  spd -0.12 -1.33 -0.94
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15: pnr 4.0 (17)  3.0 (16)  0.0 0.0 0.0 0.0 0.0 (5)  0.0 (4)  maxpnr 4.0 (17)  pna 17.0 (3)  0.0 (3)  5.0 (5)  0.0 0.0 0.0 0.0 (1)  0.0 (1)  maxpna 17.0 maxh 78.20 37.20 78.20 78.20 (5)  minslp -12.60 3.30 -12.60 -12.60 maxslp 28.0 16.5 28.0 17.0 maxacs 1.74 1.08 1.74 1.74 minac -1.60 -1.60 1.30 minra -4.2 6.335 -3
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15:  acr 2.63 0.00 0.59 mmr 2.22 5.00 2.22 1.35 avgmmr 2.86 (2.9)  maxmmr  5.00 minmmr 1.35 mma 18.50 6.56 22.77 2.33 avgmma 10.55 (2.76)  maxmma  22.77 (4)  minmma 2.33 (0.27) ssr 2.75 (1.05)  0.59 (1.11)  1.16 (0.33)  3.51 (0.5)  avgssr 1.75 (1.96)  maxssr 41.25 (1.46)  minssr 0.00 (0.26) acss 3 avgar 0.17 (0.21)  0.18 (0.56)  0.38 (0.3)  avgsr 0.31 (0.55)  0.32 (0.54)  0.57 (0.52)  avgsra 2.59 0.98 0.42 avgsp 0.10 (0.16)  0.23 (0.37)  1.18 (0.66)  maxavgsr 0.57 (0.55)  maxavgsra 2.59 maxavgsp 1.18 (0.66)  avgacs 0.86 0.48 (0.43)  0.64 (0.49)  avgslp 11.25 (10+)  19.17 (10+)  -1.55 (3+)  avgap 0.11 0.13 0.54
0	18:52:52.094	2011.07.19 01:57:29  May 22 2019 b EURUSD,M15:   w 32 2 1 w[3] 0 0 0 w[6] 0 0 1 w[9] 1 1 0 w[12] 0 0 1 w[15] 0 1 0 w[18] 1 0 0 w[21] 0 0 0 w[24] 0 0 0 1 0 0  w[30] 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  w2 2 1 0 w2[3] 0 0 0 w2[6] 0 1 0 w2[9] 0 0  nac 1 0 1 0 0 0 0 0 nra 5 0 1 nra[3] 0 4 0 0 0 t 11

  */
  
  // 2011a 360 99.17% 
  
  
 
           
        /*
        strong
        
        1.2.0.0 st 94.57 slp 19.00 ac 10.00 ra 2.00 r 25.50 h 33.20 v 56.00 sp 0.20 sr 0.75 ap 0.11 ar 0.39 acs 0.53 sra 9.50 slh 0.57 ach 0.30  
1.2.1.1 st 81.54 slp 9.00 ac 8.00 ra 8.00 r 20.00 h 42.20 v 86.00 sp 0.11 sr 0.45 ap 0.10 ar 0.40 acs 0.89 sra 1.13 slh 0.21 ach 0.19  
1.5.0.2 st 90.60 slp 9.00 ac 1.00 ra -0.20 r 18.40 h 33.20 v 56.00 sp 0.10 sr 0.49 ap 0.01 ar 0.05 acs 0.11 sra 0.00 slh 0.27 ach 0.03  
1.5.1.3 st 79.31 slp 8.00 ac 1.20 ra 1.40 r 20.60 h 42.20 v 86.00 sp 0.10 sr 0.39 ap 0.02 ar 0.06 acs 0.15 sra 5.71 slh 0.19 ach 0.03  
1.10.0.4 st 94.07 slp 7.20 ac 1.90 ra 0.40 r 17.70 h 33.20 v 56.00 sp 0.08 sr 0.41 ap 0.02 ar 0.11 acs 0.26 sra 0.00 slh 0.22 ach 0.06  
1.10.1.5 st 85.85 slp 5.30 ac 1.50 ra 1.70 r 16.80 h 42.20 v 86.00 sp 0.06 sr 0.32 ap 0.02 ar 0.09 acs 0.28 sra 3.12 slh 0.13 ach 0.04  
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15: 
5.3.0.6 st 86.46 slp 26.00 ac 2.67 ra -14.66 r 33.00 h 56.60 v 56.00 sp 0.30 sr 0.79 ap 0.03 ar 0.08 acs 0.10 sra 0.00 slh 0.46 ach 0.05  
5.3.1.7 st 65.22 slp 23.33 ac 17.33 ra 21.33 r 44.00 h 73.20 v 403.00 sp 0.36 sr 0.53 ap 0.27 ar 0.39 acs 0.74 sra 1.09 slh 0.32 ach 0.24  
5.5.0.8 st 88.52 slp 16.60 ac 0.00 ra -12.40 r 36.60 h 56.60 v 56.00 sp 0.19 sr 0.45 ap 0.17 ar 0.33 acs 0.00 sra 0.00 slh 0.29 ach 0.26  
5.5.1.9 st 72.20 slp 16.60 ac 12.40 ra 12.00 r 37.80 h 73.20 v 403.00 sp 0.23 sr 0.44 ap 0.17 ar 0.33 acs 0.75 sra 1.38 slh 0.23 ach 0.17  
5.10.0.10 st 90.55 slp 8.70 ac -0.60 ra -3.70 r 33.50 h 56.60 v 56.00 sp 0.10 sr 0.26 ap 0.04 ar 0.09 acs 0.00 sra 0.00 slh 0.15 ach 0.06  
5.10.1.11 st 76.00 slp 9.30 ac 3.10 ra -3.00 r 35.50 h 73.20 v 403.00 sp 0.12 sr 0.26 ap 0.04 ar 0.09 acs 0.33 sra 0.00 slh 0.13 ach 0.04  
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15: 
15.2.0.12 st 88.84 slp 47.50 ac 17.00 ra -17.50 r 51.00 h 62.60 v 56.00 sp 0.53 sr 0.93 ap 0.19 ar 0.33 acs 0.36 sra 0.00 slh 0.76 ach 0.27  
15.2.1.13 st 79.63 slp 30.50 ac 34.50 ra 35.00 r 63.00 h 78.40 v 1156.00 sp 0.38 sr 0.48 ap 0.43 ar 0.55 acs 1.13 sra 0.87 slh 0.39 ach 0.44  
15.5.0.14 st 74.39 slp 15.80 ac 8.40 ra -17.20 r 48.80 h 62.60 v 56.00 sp 0.21 sr 0.32 ap 0.11 ar 0.17 acs 0.53 sra 0.00 slh 0.25 ach 0.13  
15.5.1.15 st 50.26 slp 7.40 ac 25.60 ra 34.60 r 53.20 h 78.40 v 1156.00 sp 0.15 sr 0.14 ap 0.51 ar 0.48 acs 3.46 sra 0.21 slh 0.09 ach 0.33  
15.10.0.16 st 53.08 slp 5.40 ac 7.70 ra -6.20 r 54.60 h 62.60 v 56.00 sp 0.10 sr 0.10 ap 0.15 ar 0.14 acs 1.43 sra 0.00 slh 0.09 ach 0.12  
15.10.1.17 st 32.09 slp -2.30 ac 13.90 ra 18.90 r 61.10 h 78.40 v 1156.00 sp 0.18 sr 0.02 ap 0.43 ar 0.23 acs 0.00 sra 0.00 slh 0.15 ach 0.18 
 obc 9 4 5 obc[3] 3 3 1 1 0 aob 1 1 psc 17 17 6 psc[3] 6 6 6 5 5 pac 16 10 6 pac[3] 2 4 2 6 6  pra 10 6 5 pra[3] 5 2 2 3 2 nsc 1 0 0 nsc[3] 0 0 0 1 0
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15: maxsp 0.53 (1.38)  0.20 0.53 0.53 0.30 0.53 0.38 maxsr 0.93 (0.6)  0.75 0.93 0.93 0.79 0.93 0.48 maxap 0.51 (0.9)  0.11 0.51 0.51 maxar 0.55 (0.6)  0.40 0.55 0.55 avgac 9.00 (8)  10.00 (10)  20.30 (4)  avgra 5.00 (9)  3.33 (6)  8.75 (1+)  spd -0.10 -0.23 0.15
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15: pnr 17.0 (17)  0.0 (16)  0.0 0.0 0.0 0.0 5.0 (5)  0.0 (4)  maxpnr 17.0 (17)  pna 16.0 (3)  0.0 (3)  0.0 (5)  0.0 4.0 0.0 0.0 (1)  0.0 (1)  maxpna 16.0 maxh 78.40 42.20 78.40 78.40 (5)  minslp -2.30 5.30 -2.30 -16.20 maxslp 26.0 (28)  19.0 (16)  26.0 15.8 maxacs 3.46 (1.7)  0.89 (1.8)  3.46 3.46 maxslh 0.76 0.57 0.76 0.76 minac -0.60 1.00 -0.60 minra -17.5 3.334999999999999 -0.2
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15:  acr 0.00 (2)  5.26 3.75 mmr 11.30 (2)  3.58 (5)  11.30 (2)  0.98 (1)  avgmmr 5.29 (2.9)  maxmmr  11.30 minmmr 0.98 mma 57.50 10.00 57.50 6.90 avgmma 24.80 (2.76)  maxmma  57.50 (4)  minmma 6.90 (0.27) ssr 2.11 (1.05)  0.73 (1.11)  1.14 (0.33)  2.18 (0.5)  avgssr 1.35 (1.96)  maxssr 3.52 (1.46)  minssr 0.73 (0.26) acss 3 avgar 0.20 (0.21)  0.24 (0.56)  0.44 (0.3)  avgsr 0.50 (0.55)  0.66 (0.54)  0.71 (0.52)  avgsra 3.27 (2)  0.55 (0.9)  0.44 (0.4)  avgsp 0.12 (0.16)  0.33 (0.37)  0.46 (0.66)  maxavgsr 0.71 (0.55)  maxavgsra 3.27 maxavgsp 0.46 (0.66)  avgacs 0.71 (0.86)  0.42 (0.43)  0.74 (0.49)  avgslp 14.00 (10+)  24.67 (10+)  3.15 (3+)  avgap 0.11 0.15 0.31
0	14:49:12.862	2011.11.22 02:15:23  May 23 2019 b EURUSD,M15:   w 37 1 1 w[3] 0 0 0 w[6] 1 1 1 w[9] 1 1 0 w[12] 0 0 1 w[15] 1 0 1 w[18] 1 0 0 w[21] 0 0 0 w[24] 1 0 1 1 0 0  w[30] 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1   nac 1 0 0 0 1 0 0 0 nra 8 5 1 nra[3] 0 4 2 3 3 t 2

strong?

1.2.0.0 st 71.05 slp 22.50 ac 17.50 ra 8.00 r 32.50 h 31.00 v 81.00 sp 0.32 sr 0.69 ap 0.25 ar 0.54 acs 0.78 sra 2.81 slh 0.73 ach 0.56  
1.2.1.1 st 62.14 slp 5.00 ac 9.50 ra 19.50 r 31.50 h 39.60 v 93.00 sp 0.08 sr 0.16 ap 0.15 ar 0.30 acs 1.90 sra 0.26 slh 0.13 ach 0.24  
1.5.0.2 st 82.72 slp 8.60 ac -3.20 ra -8.80 r 30.00 h 31.00 v 81.00 sp 0.10 sr 0.29 ap 0.06 ar 0.35 acs 0.00 sra 0.00 slh 0.28 ach 0.15  
1.5.1.3 st 80.98 slp 11.80 ac 5.60 ra 13.40 r 32.00 h 39.60 v 93.00 sp 0.15 sr 0.37 ap 0.07 ar 0.18 acs 0.47 sra 0.88 slh 0.30 ach 0.14  
1.10.0.4 st 88.00 slp 7.90 ac 1.20 ra -1.70 r 26.70 h 31.00 v 81.00 sp 0.09 sr 0.30 ap 0.01 ar 0.04 acs 0.15 sra 0.00 slh 0.25 ach 0.04  
1.10.1.5 st 84.34 slp 6.70 ac 2.90 ra 4.10 r 24.80 h 39.60 v 93.00 sp 0.08 sr 0.27 ap 0.03 ar 0.12 acs 0.43 sra 1.63 slh 0.17 ach 0.07  
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15: 
5.3.0.6 st 80.80 slp 27.33 ac 3.00 ra -35.00 r 51.00 h 68.20 v 255.00 sp 0.34 sr 0.54 ap 0.04 ar 0.06 acs 0.11 sra 0.00 slh 0.40 ach 0.04  
5.3.1.7 st 59.83 slp 24.33 ac 38.00 ra 37.67 r 49.00 h 80.40 v 615.00 sp 0.41 sr 0.50 ap 0.64 ar 0.78 acs 1.56 sra 0.65 slh 0.30 ach 0.47  
5.5.0.8 st 75.32 slp 12.20 ac 10.60 ra 0.40 r 52.20 h 68.20 v 255.00 sp 0.16 sr 0.23 ap 0.14 ar 0.20 acs 0.87 sra 0.00 slh 0.18 ach 0.16  
5.5.1.9 st 51.34 slp 1.60 ac 10.20 ra 16.60 r 51.80 h 80.40 v 615.00 sp 0.03 sr 0.03 ap 0.20 ar 0.20 acs 6.37 sra 0.10 slh 0.02 ach 0.13  
5.10.0.10 st 71.12 slp 10.90 ac 2.70 ra -2.00 r 49.90 h 68.20 v 255.00 sp 0.15 sr 0.22 ap 0.04 ar 0.05 acs 0.25 sra 0.00 slh 0.16 ach 0.04  
5.10.1.11 st 54.09 slp 8.20 ac 4.70 ra 2.40 r 46.60 h 80.40 v 615.00 sp 0.15 sr 0.18 ap 0.09 ar 0.10 acs 0.57 sra 3.42 slh 0.10 ach 0.06  
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15: 
15.2.0.12 st 60.06 slp 30.50 ac 46.00 ra 88.00 r 82.50 h 73.60 v 870.00 sp 0.51 sr 0.37 ap 0.77 ar 0.56 acs 1.51 sra 0.35 slh 0.41 ach 0.63  
15.2.1.13 st 51.97 slp -15.50 ac -42.00 ra -47.50 r 67.50 h 96.20 v 1120.00 sp 0.29 sr 0.34 ap 0.24 ar 0.28 acs 0.00 sra 0.00 slh 0.22 ach 0.18  
15.5.0.14 st 68.31 slp 22.60 ac 18.60 ra 24.80 r 71.80 h 73.60 v 870.00 sp 0.33 sr 0.31 ap 0.27 ar 0.26 acs 0.82 sra 0.91 slh 0.31 ach 0.25  
15.5.1.15 st 55.91 slp 4.00 ac -6.20 ra -18.00 r 60.40 h 96.20 v 1120.00 sp 0.07 sr 0.07 ap 0.59 ar 0.36 acs 0.00 sra 0.00 slh 0.04 ach 0.23  
15.10.0.16 st 55.66 slp 0.00 ac 11.30 ra 22.20 r 65.20 h 73.60 v 870.00 sp 0.09 sr 0.06 ap 0.20 ar 0.17 acs 0.00 sra 0.00 slh 0.05 ach 0.15  
15.10.1.17 st 41.12 slp -11.30 ac -10.90 ra -19.70 r 61.00 h 96.20 v 1120.00 sp 0.10 sr 0.09 ap 0.40 ar 0.14 acs 0.00 sra 0.00 slh 0.05 ach 0.10 
 obc 5 0 4 obc[3] 0 1 0 0 0 aob 2 2 psc 15 13 6 psc[3] 6 6 5 3 2 pac 14 9 5 pac[3] 3 6 3 3 3  pra 11 8 4 pra[3] 4 4 3 3 2 nsc 2 2 0 nsc[3] 0 0 0 2 2
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15: maxsp 0.51 (1.38)  0.32 0.51 0.51 0.34 0.51 0.33 maxsr 0.69 (0.6)  0.69 0.54 0.37 0.54 0.50 0.34 maxap 0.77 (0.9)  0.25 0.77 0.77 maxar 0.78 (0.6)  0.54 0.78 0.56 avgac 13.50 (8)  18.40 (10)  -19.85 (4)  avgra 13.75 (9)  1.34 (6)  20.25 (1+)  spd -0.02 -0.17 0.18
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15: pnr 7.0 (17)  6.0 (16)  0.0 0.0 0.0 0.0 1.0 (5)  1.0 (4)  maxpnr 7.0 (17)  pna 3.0 (3)  3.0 (3)  5.0 (5)  0.0 0.0 0.0 1.0 (1)  1.0 (1)  maxpna 5.0 maxh 96.20 39.60 96.20 96.20 (5)  minslp -11.30 5.00 -11.30 -11.30 maxslp 24.33 (28)  22.5 (16)  24.33 22.6 maxacs 6.37 (1.7)  1.90 (1.8)  6.37 1.51 maxslh 0.73 (0.7)  0.73 (0.5)  0.41 0.41 minac -42.00 -3.20 -42.00 minra -47.5 1.335000000000001 -8.800000000000001
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15:  acr 0.00 (2)  14.58 0.00 mmr 2.15 (2)  4.50 (5)  2.15 (2)  2.00 (1)  avgmmr 2.88 (2.9)  maxmmr  4.50 minmmr 2.00 mma 0.90 5.47 0.90 0.44 avgmma 2.27 (2.76)  maxmma  5.47 (4)  minmma 0.44 (0.27) ssr 4.50 (1.05)  5.92 (1.11)  1.84 (0.33)  2.06 (0.5)  avgssr 3.28 (1.96)  maxssr 6.43 (1.46)  minssr 0.00 (0.26) acss 4 avgar 0.28 (0.21)  0.42 (0.56)  0.42 (0.3)  avgsr 0.36 (0.55)  0.52 (0.54)  0.36 (0.52)  avgsra 0.79 (2)  0.32 (0.9)  0.17 (0.4)  avgsp 0.15 (0.16)  0.38 (0.37)  0.40 (0.66)  maxavgsr 0.52 (0.55)  maxavgsra 0.79 (3)  maxavgsp 0.40 (0.66)  avgacs 1.34 (0.86)  0.84 (0.43)  0.75 (0.49)  avgslp 13.75 (10+)  14.07 (10+)  2.35 (3+)  avgap 0.20 (0.1)  0.34 (0.15)  0.51 (0.3)  
0	10:37:15.465	2011.07.08 09:07:30  May 24 2019 b ratio restriction EURUSD,M15:   w 35 2 1 w[3] 0 0 0 w[6] 1 0 1 w[9] 1 0 0 w[12] 0 0 1 w[15] 1 1 0 w[18] 0 0 0 w[21] 0 0 0 w[24] 0 0 1 1 0 0  w[30] 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0   nac 4 3 1 0 0 0 3 3 nra 7 5 2 nra[3] 1 2 1 3 3 t 2


        */
  
string ws2="",wsb="",wsc=""; if(w2[0]>0){wsc=StringConcatenate(" w2 ",w2[0]," ",w2[1]," ",w2[2]," w2[3] ",w2[3]," ",w2[4]," ",
w2[5],
 " w2[6] ",w2[6]," ",w2[7]," ",w2[8]," w2[9] ",w2[9]," ",w2[10]); }
 
string ws=""; if(w[0]>0){ws=StringConcatenate(" w ",w[0]," ",w[1]," ",w[2]," w[3] ",w[3]," ",w[4]," ",w[5]," w[6] ",w[6]," ",
w[7]," ",w[8],
" w[9] ",w[9]," ",w[10]," ",w[11]," w[12] ",w[12]," ",w[13]," ",w[14]," w[15] ",w[15]," ",w[16]," ",w[17]," w[18] ",w[18]," ",
w[19]," ",w[20],
  " w[21] ",w[21]," ",w[22]," ",w[23]," w[24] ",w[24]," ",w[25]," ",w[26]," ",w[27]," ",w[28]," ",w[29]);
  
    wsb=StringConcatenate(" w[30] ",w[30]," ",w[31]," ",w[32],
  " ",w[33]," ",w[34]," ",w[35]," ",w[36]," ",w[37]," ",w[38]," ",w[39]," ",w[40]," ",w[41]," ",w[42]," ",w[43]," ",w[44]," ",
  w[45]," ",w[46],
   " ",w[47]," ",w[48]," ",w[49]," ",wsc);
  
     ws2=StringConcatenate(" nac ",nac[0],
      " ",nac[1]," ",nac[2]," ",nac[3]," ",nac[4]," ",nac[5]," ",nac[6]," ",nac[7]," nra ",nra[0]," ",nra[1]," ",nra[2],
      " nra[3] ",nra[3]," ",
      nra[4],
       " ",nra[5]," ",nra[6]," ",nra[7]);}
       string maxhs=StringConcatenate(sd(maxh[0],2)," ",sd(maxh[1],2)," ",sd(maxh[2],2)," ",sd(maxh[3],2));
    
    
 Print("\n",disp[0],"\n",disp[1],"\n",disp[2],"\n",disp[3],"\n",disp[4],"\n",disp[5]); 
  Print("\n",disp[6],"\n",disp[7],"\n",disp[8],"\n",disp[9],"\n",disp[10],"\n",disp[11]); 
 
 string spds=sd(spd[0],2); string spds1=sd(spd[1],2); string spds2=sd(spd[2],2);
 string mmrs=StringConcatenate(sd(mmr[0],2)," (2)  ",sd(mmr[1],2)," (5)  ",sd(mmr[2],2)," (2)  ",
  sd(mmr[3],2)," (1)  avgmmr ",sd(avgmmr,2)," (2.9)  maxmmr  ",sd(maxmmr,2)," minmmr ",sd(minmmr,2)," mma ",sd(mma[0],2)," ",
  sd(mma[1],2),
   " ",sd(mma[2],2)," ",sd(mma[3],2)," avgmma ",sd(avgmma,2)," (2.76)  maxmma  ",sd(maxmma,2)," (4)  minmma ",sd(minmma,2),
   " (0.27)");
 
  string ssrs=StringConcatenate(sd(ssr[0],2)," (1.05)  ",sd(ssr[1],2)," (1.11)  ",sd(ssr[2],2)," (0.33)  ",
   sd(ssr[3],2)," (0.5)  avgssr ",sd(avgssr,2)," (1.96)  maxssr ",sd(maxssr,2)," (1.46)  minssr ",sd(minssr,2)," (0.26)"); 
  
 Print("\n",disp[12],"\n",disp[13],"\n",disp[14],"\n",disp[15],"\n",disp[16],"\n",
 disp[17]);
 
 Print("maxsp ",sd(maxsp[0],2)," (1.38)  ",sd(maxsp[1],2)," ",
 sd(maxsp[2],2)," ",sd(maxsp[3],2)," ",sd(maxsp[4],2)," ",sd(maxsp[5],2)," ",sd(maxsp[6],2)," maxsr ",sd(maxsr[0],2)," (0.6)  ",
 sd(maxsr[1],2),
 " ",
  sd(maxsr[2],2)," ",sd(maxsr[3],2)," ",sd(maxsr[4],2)," ",sd(maxsr[5],2)," ",sd(maxsr[6],2),
   " maxap ",sd(maxap[0],2)," (0.9)  ",sd(maxap[1],2)," ",sd(maxap[2],2)," ",sd(maxap[3],2),
    " maxar ",sd(maxar[0],2)," (0.6)  ",sd(maxar[1],2)," ",sd(maxar[2],2)," ",sd(maxar[3],2)," avgac ",sd(avgac[0],2)," (8)  ",
    sd(avgac[1],2),
    " (10)  ",
     sd(avgac[2],2)," (4)  avgra ",sd(avgra[0],2)," (9)  ",sd(avgra[1],2)," (6)  ",sd(avgra[2],2)," (1+)  spd ",spds," ",spds1,
     " ",spds2); 
   
    string Acs=StringConcatenate(" maxslh ",maxslh," (0.7)  ",maxslh2," (0.5)  ",maxslh3," ",maxslh4," minac ",sd(minac[0],2),
    " ",sd(minac[1],2)," ",
    sd(minac[2],2)," minra ",sd(minra,2)," ",sd(minra2,2)," ",sd(minra3,2));
 Print("pnr ",pnr[0]," (17)  ",pnr[1]," (16)  ",pnr[2]," ",pnr[3]," ",pnr[4]," ",pnr[5]," ",pnr[6]," (5)  ",pnr[7],
 " (4)  maxpnr ",maxpnr,
  " (17)  pna ",pna[0]," (3)  ",pna[1]," (3)  ",pna[2]," (5)  ",pna[3]," ",pna[4]," ",pna[5]," ",pna[6]," (1)  ",pna[7],
  " (1)  maxpna ",
  maxpna," maxh ",maxhs,
    " (5)  minslp ",sd(minslp[0],2)," ",sd(minslp[1],2)," ",sd(minslp[2],2)," ",sd(minslp[3],2)," maxslp ",maxslp[0]," (28)  ",
    maxslp[1],
    " (16)  ",
    maxslp[2],
     " ",maxslp[3]," maxacs ",sd(maxacs[0],2),
      " (1.7)  ",sd(maxacs[1],2)," (1.8)  ",sd(maxacs[2],2)," ",sd(maxacs[3],2),Acs);
     double LongSwap=MarketInfo(s,MODE_SWAPLONG);
     
    
Print(" acr ",sd(acr[0],2)," (2)  ",sd(acr[1],2)," ",sd(acr[2],2)," mmr ",mmrs," ssr ",ssrs," acss ",acss," avgar ",sd(avgar[0],2),
" (0.21)  ",
 sd(avgar[1],2)," (0.56)  ",sd(avgar[2],2)," (0.3)  avgsr ",sd(avgsr[0],2)," (0.55)  ",sd(avgsr[1],2)," (0.54)  ",sd(avgsr[2],2),
 
 " (0.52)  avgsra ",sd(avgsra[0],2)," (2)  ",sd(avgsra[1],2)," (0.9)  ",sd(avgsra[2],2)," (0.4)  avgsp ",sd(avgsp[0],2)," (0.16)  ",
 sd(avgsp[1],2),  
  " (0.37)  ",sd(avgsp[2],2)," (0.66)  maxavgsr ",sd(maxavgsr,2)," (0.55)  maxavgsra ",sd(maxavgsra,2)," (3)  maxavgsp ",
  sd(maxavgsp,2),
   " (0.66)  avgacs ",sd(avgacs[0],2)," (0.86)  ",sd(avgacs[1],2)," (0.43)  ",sd(avgacs[2],2)," (0.49)  avgslp ",sd(avgslp[0],2),
   " (10+)  ",
    sd(avgslp[1],2)," (10+)  ",sd(avgslp[2],2)," (3+)  avgap ",sd(avgap[0],2)," (0.1)  ",sd(avgap[1],2)," (0.15)  ",sd(avgap[2],2),
    " (0.3)  ");
     
    Print(" ",ws," ",wsb," ",ws2," t ",type);
    
     //" LSwap ",LongSwap," bar ",Bars," Mnth ",Month()," Yr ",Year()
    
 
string comment="NH"; double stoploss=290; //double tp=8; //take profit of 8 is a safety measure. Current default is 6 to cover
// ECN commission. 
   //swap protection
   
   // longswap says -12.1 as of Mar 2019.
   
   //however, in back testing for Jan 2011 it is -0.363.

   double HistSwap[50]; ArrayInitialize(HistSwap,0);
    if(Hour()>=20){ HistSwap[1]=10; //jan 2011
     tp=tp+10; comment="swap";
    // as of mar 2019, jan 2011 swap is listed as swap -0.363
     }else{tp=8; comment="NH";}
     
 //string DoubleToStrMorePrecision(double p){ return( DoubleToStr(p,8) ); }
 string point=DoubleToStrMorePrecision(Point);
 
 //Print("Ask ",Ask," spr ",spr," p ",p," tp ",Ask+(tp*p)," point ",point);

  double Lots=0.1; if(IsTesting()){Lots=0.1;}else{Lots=0.01;}//Sometimes tester only allows 0.1 lots. 
    //FXOpen ECN real live allows 0.01 lots. 
    
    //comment will overwrite swap comment above
      if(type!=0){  comment=IntegerToString(type,0,0);  }
  RefreshRates();  if(tp!=8){tp=8;} Lots=0.01; if(p!=Point){p=Point;}
  
  //TP Verification 1/2
    tkp=Ask+(tp*p); if(tkp<Ask+(tp*p)){tkp=Ask+(tp*p);}
  
      if(tkp!=(Ask+(8*Point) )){ tkp=Ask+(8*Point); }
  Print("Attempting buy entry @ Ask ",Ask," ",sd(Ask,Digits)," tp ",tkp," ",sd(tp,Digits)," spr ",spr," slip ",slip);
  
   if(OrderSend(Symbol(),OP_BUY,Lots,Ask,slip,Ask-(stoploss*p),Ask+(8*Point),comment,magic,0,clrGreen)==1)
              {  if(OrdersTotal()>0){ 
                 OrdersSent++; OrderMng();   }
                return; 

                 }else if(OrdersTotal()==0){ Print("OrderSend err ",GetLastError());  return;
              }
           
        }
     }
//---
return;
  }
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
//double OnTester() {   // double ret=0.0;
  
//---
 
//---

//---
   //return(ret);}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
string Data(int tf,int pd,int sh,int i)
  { disp[i]=""; 
  
//---- Basic / raw values 
  
  // Slope, acceleration
  slp[i]=Slp(tf,pd,sh); //if(slp[i]<MSA){return("");}
  slp[i]=nd(slp[i],2); 
    if(slp[i]>0){ psc[0]++;  if(slp[i]>=5){ psc[1]++; }   
        if(tf==1){ psc[2]++; if(slp[i]>=5){ psc[3]++; } }
          if(tf==5){ psc[4]++; if(slp[i]>=5){ psc[5]++; } }
            if(tf==15){ psc[6]++; if(slp[i]>=5){ psc[7]++; } }}
    if(slp[i]<0){ nsc[0]++;  if(slp[i]<= -5){ nsc[1]++; }   
        if(tf==1){ nsc[2]++; if(slp[i]<= -5){ nsc[3]++; } }
          if(tf==5){ nsc[4]++; if(slp[i]<= -5){ nsc[5]++; } }
            if(tf==15){ nsc[6]++; if(slp[i]<= -5){ nsc[7]++; } }}
  
   
  slp[i+1]=nd((Slp(tf,pd,sh+1)),2);  
  slp[i+2]=nd((Slp(tf,pd,sh+2)),2);   
  ac[i]=nd((slp[i]-slp[i+1]),2);  
   if(ac[i]>0){ pac[0]++;  if(ac[i]>=5){ pac[1]++; }   
        if(tf==1){ pac[2]++; if(ac[i]>=5){ pac[3]++; } }
          if(tf==5){ pac[4]++; if(ac[i]>=5){ pac[5]++; } }
            if(tf==15){ pac[6]++; if(ac[i]>=5){ pac[7]++; } }}
            
      if(ac[i]<0){ nac[0]++;  if(ac[i]<= -5){ nac[1]++; }   
        if(tf==1){ nac[2]++; if(ac[i]<= -5){ nac[3]++; } }
          if(tf==5){ nac[4]++; if(ac[i]<= -5){ nac[5]++; } }
            if(tf==15){ nac[6]++; if(ac[i]<= -5){ nac[7]++; } }}
            
      if(ra[i]<0){ nra[0]++;  if(ra[i]<= -5){ nra[1]++; }   
        if(tf==1){ nra[2]++; if(ra[i]<= -5){ nra[3]++; } }
          if(tf==5){ nra[4]++; if(ra[i]<= -5){ nra[5]++; } }
            if(tf==15){ nra[6]++; if(ra[i]<= -5){ nra[7]++; } }}
            
   
      ac[i+1]=nd((slp[i+1]-slp[i+2]),2); 
      
      ra[i]=nd((ac[i]-ac[i+1]),2);   if(slp[i]>1 && ra[i]>1){ sra[i]=slp[i]/ra[i]; }
       if(ra[i]>0){ pra[0]++;  if(ra[i]>=5){ pra[1]++; }   
        if(tf==1){ pra[2]++; if(slp[i]>=5){ pra[3]++; } }
          if(tf==5){ pra[4]++; if(slp[i]>=5){ pra[5]++; } }
            if(tf==15){ pra[6]++; if(slp[i]>=5){ pra[7]++; } }}
      
  //range, height, volume 
      r[i]=nd((rng(tf,pd,sh)),2); double lo=iMA(s,tf,5,0,MODE_SMA,PRICE_CLOSE,sh); h[i]=nd(((Ask-lo)/p),2);
      
       v[i]=vol(tf,sh); //volume may be broker and server specific only. 
   
  //stoch (position)    
    st[i]=nd(sto(tf,pd,sh),2); // not sure if this is correct. 
      
     if(st[i]>=80){ obc[0]++;  if(st[i]>=90){ obc[1]++; }   
        if(tf==1){obc[2]++; if(st[i]>=90){ obc[3]++; } }
          if(tf==5){obc[4]++; if(st[i]>=90){ obc[5]++; } }
            if(tf==15){obc[6]++; if(st[i]>=90){ obc[7]++; } } }
    
     
//---- Ratios: Sometimes, ratios are more helpful if ratios are only based on positive integers that are >1, but >=1 might also
// help.
         // At the very least, avoid dividing by zero. 

   if(slp[i]>=1){  
     if(st[i]>=1){ sp[i]=nd((slp[i]/st[i]),2); }  if(r[i]>=1){ sr[i]=nd((slp[i]/r[i]),2); } 
     if(h[i]>=1){slh[i]=nd((slp[i]/h[i]),2);}   }
    
      if(ac[i]>=1){ if(slp[i]>=1){ nd((acs[i]=ac[i]/slp[i]),2);  }
        if(acs[i]>=1){acss++;}
         if(st[i]>=1){ ap[i]=nd((ac[i]/st[i]),2); } if(r[i]>=1){ ar[i]=nd((ac[i]/r[i]),2); }  
         if(h[i]>=1){ach[i]=nd((ac[i]/h[i]),2);} }
         
  rm[i]=MathMax(sp[i],MathMax(sr[i],MathMax(ap[i],MathMax(ar[i],MathMax(acs[i],MathMax(sra[i],MathMax(slh[i],ach[i])))))));       
         
        rmd[i]=sra[i]-rm[i];
         
string sts=sd(st[i],2); string slps=sd(slp[i],2); string Acs=sd(ac[i],2);   string ras=sd(ra[i],2);
      string rng=sd(r[i],2); string hs=sd(h[i],2); string vs=sd(v[i],2); string sps=sd(sp[i],2); string srs=sd(sr[i],2);
      string aps=sd(ap[i],2); string ars=sd(ar[i],2); string Acs2=sd(acs[i],2);
      string slhs=sd(slh[i],2); string achs=sd(ach[i],2);string obcs="",pacs="",pras="",str="",str2=""; 
       if(obc[0]!=0){ aob[0]=pac[0]/obc[0]; aob[1]=pra[0]/obc[0]; }
      if(i==17){
    
 if(obc[0]>0 || psc[0]>0 || pac[0]>0 || pra[0]>0 || nsc[0]>0){  str=StringConcatenate("\n"," obc ",obc[0]," ",obc[1]," ",obc[2],
  " obc[3] ",obc[3]," ",obc[4]," ",obc[5]," ",obc[6], " ",obc[7]," aob ",aob[0]," ",aob[1]," psc ",psc[0]," ",psc[1]," ",psc[2],
  " psc[3] ",psc[3]," ",psc[4]," ",psc[5],
   " ",psc[6]," ",psc[7]," pac ",pac[0]," ",pac[1]," ",pac[2]," pac[3] ",pac[3]," ",pac[4]," ",pac[5],
    " ",pac[6]," ",pac[7]);
   
   str2=StringConcatenate(" pra ",pra[0]," ",pra[1]," ",pra[2]," pra[3] ",pra[3]," ",pra[4]," ",pra[5]," ",pra[6]," ",pra[7],
    " nsc ",nsc[0]," ",nsc[1]," ",nsc[2]," nsc[3] ",nsc[3]," ",nsc[4]," ",nsc[5]," ",nsc[6]," ",nsc[7]);}}
      
disp[i]=StringConcatenate(tf,".",pd,".",sh,".",i,
" st ",sts,
//" sstd ",sstd," subsst ",subsst," subsst2 ",subsst2," sst2 ",sst2," stl ",stl," stl2 ",stl2," sts ",sts,
" slp ",slps," ac ",Acs," ra ",ras," r ",rng,
" h ",hs," v ",vs," sp ",sps," sr ",srs," ap ",aps," ar ",ars," acs ",Acs2," sra ",sd(sra[i],2)," slh ",slhs,
" ach ",achs," ",str," ",str2," rm ",sd(rm[i],2)," rmd ",sd(rmd[i],2));

   return(disp[i]);
  }
  
//+------------------------------------------------------------------+
//| Slope                                                            |
//+------------------------------------------------------------------+
double Slp(int tf,int pd,int sh) {double SLP=0; double Ma=iMA(s,tf,pd,0,MODE_SMA,PRICE_CLOSE,sh);  
 double Ma1=iMA(s,tf,pd,0,MODE_SMA,PRICE_CLOSE,sh+1); SLP=nd(((Ma-Ma1)/p),2); return(SLP);}
  double nd(double val, int dig){  return(NormalizeDouble(val,dig));      }
    string DoubleToStrMorePrecision(double p2){ return( DoubleToStr(p2,8) ); }

//Slope / Position Ratio: Default design is to only accept, process, and output positive integers >1
double SP(int tf, int tf2, int pd, int pd2, int sh, int sh2){ double Sp=0,ST=0,SLP=Slp(tf,pd,sh); if(SLP>1){
 ST=sto(tf2,pd2,sh2); } if(ST>1){Sp=SLP/ST;}else{Sp=0;} return(Sp); }

//Slope / Range Ratio: Default design is to only accept, process, and output positive integers >1
double SR(int tf, int tf2, int pd, int pd2, int sh, int sh2){ double Sr=0,RNG=0,SLP=Slp(tf,pd,sh); if(SLP>1){
 RNG=rng(tf2,pd2,sh2); } if(RNG>1){Sr=SLP/RNG;}else{Sr=0;} return(Sr); }

//+------------------------------------------------------------------+

//---- b7 regime helper: true when sells are allowed
bool QuietOK(){ if(UseQuietGate!=1){ return(true); } double atr=iATR(s,PERIOD_H1,14,1); if(atr<=0){ return(false); } double rr=(iHigh(s,PERIOD_H1,iHighest(s,PERIOD_H1,MODE_HIGH,20,1))-iLow(s,PERIOD_H1,iLowest(s,PERIOD_H1,MODE_LOW,20,1)))/(atr*20); return(rr<QuietRR && iADX(s,PERIOD_M15,14,PRICE_CLOSE,MODE_MAIN,1)<QuietADX); } //b13
bool SellRegimeOK(){ if(!QuietOK()){ return(false); } if(UseSellBlock==1 && (iADX(Symbol(),PERIOD_M15,14,PRICE_CLOSE,MODE_MAIN,1)>BlockADX || TimeHour(TimeCurrent())<BlockHour)){ return(false); } if(UseNewsDayBlock==1 && NewsNear(NewsBlockHours)){ return(false); } if(UseSellRegime!=1){ return(true); } return(iClose(s,PERIOD_H1,1)<iMA(s,PERIOD_H1,SellRegimePeriod,0,MODE_SMA,PRICE_CLOSE,1)); }
//---- b6 ratio log helpers
//---- b8 helpers
bool BuyRegimeOK(){ return(iClose(s,PERIOD_H1,1)>iMA(s,PERIOD_H1,SellRegimePeriod,0,MODE_SMA,PRICE_CLOSE,1)); }
int BuySLpts(){ if(UseWideBuy==1){ return(WideBuySL); } return(290); }
int BuyTPpts(){ if(UseWideBuy==1){ return(WideBuyTP); } return(15); }
int RoundCount(int type){ int n=0; for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()==type && StringSubstr(OrderComment(),0,1)=="9"){ n++; } } } return n; }
void RoundBuyLimit(){ if(TimeCurrent()-roundLast<RoundReplaceMin*60){ return; } if(RoundCount(OP_BUYLIMIT)>0 || RoundCount(OP_BUY)>0){ return; }
   if(Bars<SellRegimePeriod+5){ return; } if(!BuyRegimeOK()){ return; } if(UseRoundBuyRA==1 && RA15e2()<=0){ return; } RefreshRates(); double step=500*p; double lvl=NormalizeDouble(MathFloor((Ask-RoundMinDist*p)/step)*step,Digits);
   int t=OrderSend(Symbol(),OP_BUYLIMIT,0.01,lvl,slip,NormalizeDouble(lvl-RoundSL*p,Digits),NormalizeDouble(lvl+RoundTP*p,Digits),"9",magic,TimeCurrent()+RoundExpiryMin*60,clrAqua);
   roundLast=TimeCurrent(); if(t>0){ Print("ROUNDLIMIT #",t," at ",DoubleToStr(lvl,Digits)," Ask ",DoubleToStr(Ask,Digits)); RatioLog(t); RatioLog2(t); } else { Print("ROUNDLIMIT err ",GetLastError()); } }
// ---- b8 RLOG2: one line per order (buys, sell stops, hedges, round limits): ADX14 (+DI, -DI), CCI14, 20-bar range / (ATR14 x 20)
// (low = ranging, high = trending) on M15 and H1; up-bar and down-bar tick volume of the last 20 M1 bars; server hour.
void RatioLog2(int ticket){ if(UseRatioLog!=1){ return; } string ln="RLOG2 #"+IntegerToString(ticket); int tfs2[2]; tfs2[0]=15; tfs2[1]=60;
   for(int i=0;i<2;i++){ int tf=tfs2[i]; double adx=iADX(s,tf,14,PRICE_CLOSE,MODE_MAIN,1), dip=iADX(s,tf,14,PRICE_CLOSE,MODE_PLUSDI,1), dim=iADX(s,tf,14,PRICE_CLOSE,MODE_MINUSDI,1);
      double cci=iCCI(s,tf,14,PRICE_TYPICAL,1); double atr=iATR(s,tf,14,1); double rr=0; if(atr>0){ rr=(iHigh(s,tf,iHighest(s,tf,MODE_HIGH,20,1))-iLow(s,tf,iLowest(s,tf,MODE_LOW,20,1)))/(atr*20); }
      ln=ln+" tf"+IntegerToString(tf)+" adx "+DoubleToStr(adx,1)+" "+DoubleToStr(dip,1)+" "+DoubleToStr(dim,1)+" cci "+DoubleToStr(cci,1)+" rr "+DoubleToStr(rr,3)+" |"; }
   double vu=0, vd=0; for(int k=1;k<=20;k++){ if(iClose(s,PERIOD_M1,k)>=iOpen(s,PERIOD_M1,k)){ vu+=iVolume(s,PERIOD_M1,k); } else { vd+=iVolume(s,PERIOD_M1,k); } }
   ln=ln+" volup "+DoubleToStr(vu,0)+" voldn "+DoubleToStr(vd,0)+" hour "+IntegerToString(Hour())+" ra15e2 "+DoubleToStr(RA15e2(),2); Print(ln); FibCalc(); Print("RLOG3 #",ticket," fibS ",DoubleToStr(FibDistS(),0)," fibL ",DoubleToStr(FibDistL(),0)," conf ",IntegerToString(FibConf())); }
double ESlp(int tf,int pd,int sh){ return((iMA(s,tf,pd,0,MODE_EMA,PRICE_CLOSE,sh)-iMA(s,tf,pd,0,MODE_EMA,PRICE_CLOSE,sh+1))/p); }
double RA15e2(){ double s1=ESlp(15,2,1), s2=ESlp(15,2,2), s3=ESlp(15,2,3); return((s1-s2)-(s2-s3)); } //b9: M15 EMA2 rate of accel, closed bars
//---- b15 helpers
double SimBal(){ if(UseLotSim==1 && SimDeposit>0){ return(SimDeposit); } return(AccountBalance()); }
double SimLev(){ if(UseLotSim==1 && SimLeverage>0){ return((double)SimLeverage); } return((double)AccountLeverage()); }
double MarginPerLot(){ double m=MarketInfo(Symbol(),MODE_MARGINREQUIRED); if(m<=0){ return(100000.0*Bid/SimLev()); } return(m*AccountLeverage()/SimLev()); }
double LotSize(int slpts){ if(UseLotSim!=1){ return(0.01); } double tv=MarketInfo(Symbol(),MODE_TICKVALUE); if(tv<=0){ tv=1; } double lots=(SimBal()*RiskPct/100.0)/(MathMax(slpts,1)*tv); double byMargin=(SimBal()*MarginUsePct/100.0)/MarginPerLot(); lots=MathMin(lots,MathMin(byMargin,MaxLots)); double st=MarketInfo(Symbol(),MODE_LOTSTEP); if(st<=0){ st=0.01; } lots=MathFloor(lots/st)*st; double mn=MarketInfo(Symbol(),MODE_MINLOT); if(mn<=0){ mn=0.01; } if(lots<mn){ lots=mn; } double mx=MarketInfo(Symbol(),MODE_MAXLOT); if(mx>0 && lots>mx){ lots=mx; } return(NormalizeDouble(lots,2)); }
bool Guard(double lots,int slpts){ if(UseRiskGuard!=1){ return(true); } double bal=SimBal(); int n=0; double risk=0, used=0; double tv=MarketInfo(Symbol(),MODE_TICKVALUE); if(tv<=0){ tv=1; }
   for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderSymbol()!=Symbol()){ continue; } n++; used+=OrderLots()*MarginPerLot(); if(OrderStopLoss()>0){ risk+=OrderLots()*MathAbs(OrderOpenPrice()-OrderStopLoss())/Point*tv; } } }
   if(n+1>MaxOpenOrders){ Print("GUARD: max orders ",n); return(false); }
   if(risk+lots*slpts*tv>bal*MaxRiskPct/100.0){ Print("GUARD: risk cap"); return(false); }
   if(bal-used-lots*MarginPerLot()<bal*MarginReservePct/100.0){ Print("GUARD: margin reserve"); return(false); }
   if(DailyLossPct>0){ double dl=0; datetime d0=iTime(Symbol(),PERIOD_D1,0); int ht=OrdersHistoryTotal(); for(int k=ht-1;k>=MathMax(0,ht-300);k--){ if(!OrderSelect(k,SELECT_BY_POS,MODE_HISTORY)){ continue; } if(OrderCloseTime()<d0){ continue; } if(OrderType()<=OP_SELL){ dl+=OrderProfit()+OrderSwap()+OrderCommission(); } } if(dl<-bal*DailyLossPct/100.0){ Print("GUARD: daily loss stop ",DoubleToStr(dl,2)); return(false); } }
   return(true); }
void NewsInit(){ string a[]; int k=StringSplit(NFPd,32,a); for(int i=0;i<k && newsN<256;i++){ newsT[newsN]=StringToTime(a[i]+" 15:30"); newsTy[newsN]=1; newsN++; }
   k=StringSplit(CPId,32,a); for(int j=0;j<k && newsN<256;j++){ newsT[newsN]=StringToTime(a[j]+" 15:30"); newsTy[newsN]=2; newsN++; }
   k=StringSplit(FOMCd,32,a); for(int m=0;m<k && newsN<256;m++){ newsT[newsN]=StringToTime(a[m]+" 21:00"); newsTy[newsN]=3; newsN++; } }
bool NewsNear(int hrs){ if(newsN==0){ NewsInit(); } datetime now=TimeCurrent(); for(int i=0;i<newsN;i++){ if(MathAbs((double)(now-newsT[i]))<=hrs*3600.0){ return(true); } } return(false); }
bool IsNewsCmt(string c){ string t=StringSubstr(c,0,2); return(t=="BN" || t=="SN"); }
int NewsOpenPos(){ int n=0; for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()<=OP_SELL && IsNewsCmt(OrderComment())){ n++; } } } return(n); }
void NewsDelPend(){ for(int i=OrdersTotal()-1;i>=0;i--){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()>OP_SELL && IsNewsCmt(OrderComment())){ if(!OrderDelete(OrderTicket())){ Print("NEWS delete err ",GetLastError()); } } } } }
void NewsMng(){ if(UseNewsStraddle!=1 && UseNewsFade!=1){ return; } if(newsN==0){ NewsInit(); } datetime now=TimeCurrent();
   if(UseNewsStraddle==1 && NewsOpenPos()>0){ NewsDelPend(); }
   for(int i=0;i<newsN;i++){
      if(UseNewsStraddle==1 && newsTy[i]==2 && now>=newsT[i]-120 && now<newsT[i] && lastNewsS!=newsT[i]){ lastNewsS=newsT[i]; RefreshRates(); double lt=LotSize(NewsStraddleSL);
         if(Guard(lt*2,NewsStraddleSL)){ double lb=NormalizeDouble(Ask+NewsStraddleDist*p,Digits), ls=NormalizeDouble(Bid-NewsStraddleDist*p,Digits); datetime ex=TimeCurrent()+NewsStraddleExpiryMin*60;
            int t1=OrderSend(Symbol(),OP_BUYSTOP,lt,lb,slip,NormalizeDouble(lb-NewsStraddleSL*p,Digits),NormalizeDouble(lb+NewsStraddleTP*p,Digits),"BN",magic,ex,clrBlue);
            int t2=OrderSend(Symbol(),OP_SELLSTOP,lt,ls,slip,NormalizeDouble(ls+NewsStraddleSL*p,Digits),NormalizeDouble(ls-NewsStraddleTP*p,Digits),"SN",magic,ex,clrRed);
            Print("NEWS straddle CPI ",TimeToStr(newsT[i])," ",t1," ",t2); if(t1>0){ RatioLog2(t1); } } }
      if(UseNewsFade==1 && newsTy[i]==1 && now>=newsT[i]+300 && now<newsT[i]+420 && lastNewsF!=newsT[i]){ lastNewsF=newsT[i]; int sh=iBarShift(Symbol(),PERIOD_M5,newsT[i]); double mv=iClose(Symbol(),PERIOD_M5,sh)-iOpen(Symbol(),PERIOD_M5,sh); double lf=LotSize(NewsFadeSL);
         if(mv!=0 && Guard(lf,NewsFadeSL)){ RefreshRates(); int tf2=-1;
            if(mv>0){ tf2=OrderSend(Symbol(),OP_SELL,lf,Bid,slip,NormalizeDouble(Bid+NewsFadeSL*p,Digits),NormalizeDouble(Bid-NewsFadeTP*p,Digits),"SN",magic,0,clrRed); }
            else { tf2=OrderSend(Symbol(),OP_BUY,lf,Ask,slip,NormalizeDouble(Ask-NewsFadeSL*p,Digits),NormalizeDouble(Ask+NewsFadeTP*p,Digits),"BN",magic,0,clrBlue); }
            Print("NEWS fade NFP ",TimeToStr(newsT[i])," ",tf2); } } } }
void FibLv(int tf,int n,double &lv[]){ int hi=iHighest(Symbol(),tf,MODE_HIGH,n,1), lo=iLowest(Symbol(),tf,MODE_LOW,n,1); double ph=iHigh(Symbol(),tf,hi), pl=iLow(Symbol(),tf,lo); double r[7]={0,0.236,0.382,0.5,0.618,0.786,1.0};
   for(int i=0;i<7;i++){ if(hi>lo){ lv[i]=ph-(ph-pl)*r[i]; } else { lv[i]=pl+(ph-pl)*r[i]; } } }
void FibCalc(){ FibLv(DrawTF,SwingBars,fibLvS); FibLv(PERIOD_H4,LargeSwingBars,fibLvL); }
double FibDistS(){ double m=1e9; for(int i=0;i<7;i++){ m=MathMin(m,MathAbs(fibLvS[i]-Ask)/Point); } return(m); }
double FibDistL(){ double m=1e9; for(int i=0;i<7;i++){ m=MathMin(m,MathAbs(fibLvL[i]-Ask)/Point); } return(m); }
int FibConf(){ for(int i=0;i<7;i++){ for(int j=0;j<7;j++){ if(MathAbs(fibLvS[i]-fibLvL[j])/Point<=ConfTolPts && MathAbs(fibLvS[i]-Ask)/Point<=20){ return(1); } } } return(0); }
void CdLine(string name,double price,color c,int style){ if(ObjectFind(name)<0){ ObjectCreate(name,OBJ_HLINE,0,0,price); } ObjectSet(name,OBJPROP_PRICE1,price); ObjectSet(name,OBJPROP_COLOR,c); ObjectSet(name,OBJPROP_STYLE,style); ObjectSet(name,OBJPROP_BACK,true); }
void DrawDeinit(){ for(int i=ObjectsTotal()-1;i>=0;i--){ string n=ObjectName(i); if(StringSubstr(n,0,3)=="CD_"){ ObjectDelete(n); } } }
datetime lastDrawBar=0;
void ChartDraw(){ datetime bt=iTime(Symbol(),DrawTF,0); if(bt==lastDrawBar){ return; } lastDrawBar=bt; FibCalc();
   for(int i=0;i<7;i++){ CdLine("CD_s"+IntegerToString(i),fibLvS[i],clrGold,STYLE_DASH); CdLine("CD_l"+IntegerToString(i),fibLvL[i],clrOrange,STYLE_SOLID); }
   int nc=0; for(int a=0;a<7;a++){ for(int b=0;b<7;b++){ if(MathAbs(fibLvS[a]-fibLvL[b])/Point<=ConfTolPts && nc<49){ CdLine("CD_c"+IntegerToString(nc),fibLvS[a],clrDodgerBlue,STYLE_SOLID); nc++; } } }
   for(int d=nc;d<49;d++){ if(ObjectFind("CD_c"+IntegerToString(d))>=0){ ObjectDelete("CD_c"+IntegerToString(d)); } }
   int nh=0, nl=0; for(int k=3;k<SwingBars+3 && (nh<SRLines || nl<SRLines);k++){ double fh=iFractals(Symbol(),DrawTF,MODE_UPPER,k), fl=iFractals(Symbol(),DrawTF,MODE_LOWER,k);
      if(fh>0 && nh<SRLines){ CdLine("CD_res"+IntegerToString(nh),fh,clrRed,STYLE_DOT); nh++; } if(fl>0 && nl<SRLines){ CdLine("CD_sup"+IntegerToString(nl),fl,clrGreen,STYLE_DOT); nl++; } }
   string txt="Regime: "+(SellRegimeOK()?"SELL (H1<SMA1200)":"BUY side (H1>SMA1200)")+"  fibS "+DoubleToStr(FibDistS(),0)+" fibL "+DoubleToStr(FibDistL(),0)+" conf "+IntegerToString(FibConf());
   if(ObjectFind("CD_lbl")<0){ ObjectCreate("CD_lbl",OBJ_LABEL,0,0,0); ObjectSet("CD_lbl",OBJPROP_CORNER,1); ObjectSet("CD_lbl",OBJPROP_XDISTANCE,10); ObjectSet("CD_lbl",OBJPROP_YDISTANCE,20); }
   ObjectSetText("CD_lbl",txt,10,"Arial",clrWhite); }
//---- b12 helpers
int CountCmt(string c,int type){ int n=0; for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()==type && StringSubstr(OrderComment(),0,1)==c){ n++; } } } return n; }
void DeletePendings(string c){ for(int i=OrdersTotal()-1;i>=0;i--){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()>OP_SELL && StringSubstr(OrderComment(),0,1)==c){ if(!OrderDelete(OrderTicket())){ Print("BRACKET delete err ",GetLastError()); } } } } }
//---- b20 counter-hedge ("H" orders: own TP/SL, excluded from OrderMng buy handling)
bool CHHas(int tk){ for(int i=0;i<chN;i++){ if(chDone[i]==tk){ return(true); } } return(false); }
void CHMng(){ RefreshRates(); for(int i=OrdersTotal()-1;i>=0;i--){ if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ continue; } if(OrderMagicNumber()!=magic || OrderSymbol()!=Symbol() || OrderType()!=OP_SELL){ continue; }
   int tk=OrderTicket(); if(CHHas(tk) || Ask<OrderOpenPrice()+CHTrigger*p){ continue; } double lt=OrderLots(); if(!Guard(lt,CHSL)){ continue; }
   if(chN>=256){ chN=0; } chDone[chN]=tk; chN++; int t=-1;
   if(CHMode==0){ t=OrderSend(Symbol(),OP_BUY,lt,Ask,slip,NormalizeDouble(Ask-CHSL*p,Digits),NormalizeDouble(Ask+CHTP*p,Digits),"H",magic,0,clrAqua); }
   else { double lv=NormalizeDouble(Ask+20*p,Digits); t=OrderSend(Symbol(),OP_BUYSTOP,lt,lv,slip,NormalizeDouble(lv-CHSL*p,Digits),NormalizeDouble(lv+CHTP*p,Digits),"H",magic,TimeCurrent()+7200,clrAqua); }
   if(t>0){ Print("CHEDGE #",t," for sell #",tk); } else { Print("CHEDGE err ",GetLastError()); } } }
//---- b19 new buys ("L" low reversal, "X" ema cross); own TP/SL, excluded from OrderMng buy handling
int CountC(string c){ int n=0; for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()==OP_BUY && StringSubstr(OrderComment(),0,1)==c){ n++; } } } return n; }
void NBuySend(string c){ if(CountC(c)>=NBuyMax){ return; } if(!Guard(LotSize(NBuySL),NBuySL)){ return; } RefreshRates(); int t=OrderSend(Symbol(),OP_BUY,LotSize(NBuySL),Ask,slip,NormalizeDouble(Ask-NBuySL*p,Digits),NormalizeDouble(Ask+NBuyTP*p,Digits),c,magic,0,clrLime); if(t>0){ RatioLog2(t); } else { Print("NBUY ",c," err ",GetLastError()); } }
void NBuyMng(){ for(int i=OrdersTotal()-1;i>=0;i--){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ string c=StringSubstr(OrderComment(),0,1); if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()==OP_BUY && (c=="L" || c=="X") && (TimeCurrent()-OrderOpenTime()>=NBuyHoldH*3600 || (NBuyCloseHour>0 && TimeHour(TimeCurrent())>=NBuyCloseHour))){ if(!OrderClose(OrderTicket(),OrderLots(),Bid,slip,clrGray)){ Print("NBUY close err ",GetLastError()); } } } }
   datetime m15=iTime(Symbol(),PERIOD_M15,0); if(UseLowRevBuy==1 && m15!=nbLastM15){ nbLastM15=m15; int lo=iLowest(Symbol(),PERIOD_M15,MODE_LOW,LowRevBars,1); int bull=0; for(int k=1;k<=LowRevBars;k++){ if(iClose(Symbol(),PERIOD_M15,k)>iOpen(Symbol(),PERIOD_M15,k)){ bull++; } }
      if(iClose(Symbol(),PERIOD_M15,1)<=iLow(Symbol(),PERIOD_M15,lo) && bull<=LowRevMaxBull){ NBuySend("L"); } }
   datetime h1=iTime(Symbol(),PERIOD_H1,0); if(UseEmaCrossBuy==1 && h1!=nbLastH1){ nbLastH1=h1; double f1=iMA(Symbol(),PERIOD_H1,CrossFast,0,MODE_EMA,PRICE_CLOSE,1), s1=iMA(Symbol(),PERIOD_H1,CrossSlow,0,MODE_EMA,PRICE_CLOSE,1), f2=iMA(Symbol(),PERIOD_H1,CrossFast,0,MODE_EMA,PRICE_CLOSE,2), s2=iMA(Symbol(),PERIOD_H1,CrossSlow,0,MODE_EMA,PRICE_CLOSE,2);
      if(f1>s1 && f2<=s2){ NBuySend("X"); } } }
//---- b17 inverted ladder
void PlaceLadder2(){ bool ok=(LadderRegime==0)?SellRegimeOK():BuyRegimeOK(); if(!ok){ Print("LADDER2 skipped: regime"); return; } if(!Guard(LotSize(LadderSL)*3,LadderSL)){ return; } int lv[3]; lv[0]=Ladder1; lv[1]=Ladder2; lv[2]=Ladder3; RefreshRates();
   if(LadderMode==3){ int tm=OrderSend(Symbol(),OP_BUY,LotSize(LadderSL),Ask,slip,NormalizeDouble(Ask-LadderSL*p,Digits),NormalizeDouble(Ask+LadderTP*p,Digits),"7",magic,0,clrBlue); if(tm>0){ RatioLog2(tm); } else { Print("LADDER2 err ",GetLastError()); } return; }
   for(int i=0;i<3;i++){ if(lv[i]<=0){ continue; } int ty=(LadderMode==1)?OP_BUYSTOP:OP_BUYLIMIT; double lvl=(LadderMode==1)?NormalizeDouble(Ask+lv[i]*p,Digits):NormalizeDouble(Ask-lv[i]*p,Digits);
      int t=OrderSend(Symbol(),ty,LotSize(LadderSL),lvl,slip,NormalizeDouble(lvl-LadderSL*p,Digits),NormalizeDouble(lvl+LadderTP*p,Digits),"7",magic,TimeCurrent()+SellStopExpiryMin*60,clrBlue);
      if(t>0){ Print("LADDER2 #",t," at ",DoubleToStr(lvl,Digits)); } else { Print("LADDER2 err ",GetLastError()); } } }
void PlaceLadder(){ if(StopHourBlocked()){ ladderFire=false; return; } if(LadderDelaySec>0 && !ladderFire){ ladderDue=TimeCurrent()+LadderDelaySec; return; } ladderFire=false; //b18
   if(LadderMode!=0 || LadderRegime!=0){ PlaceLadder2(); return; } if(!SellRegimeOK()){ Print("LADDER skipped: regime up"); return; } if(!Guard(LotSize(SellStopSL)*3,SellStopSL)){ return; } int lv[3]; lv[0]=Ladder1; lv[1]=Ladder2; lv[2]=Ladder3; RefreshRates();
   for(int i=0;i<3;i++){ if(lv[i]<=0){ continue; } double lvl=NormalizeDouble(Bid-lv[i]*p,Digits);
      int t=OrderSend(Symbol(),OP_SELLSTOP,LotSize(SellStopSL),lvl,slip,NormalizeDouble(lvl+SellStopSL*p,Digits),NormalizeDouble(lvl-SellStopTP*p,Digits),"7",magic,TimeCurrent()+SellStopExpiryMin*60,clrRed);
      if(t>0){ Print("LADDER #",t," at ",DoubleToStr(lvl,Digits)); } else { Print("LADDER err ",GetLastError()); } } }
void PlaceLeg(string c,double ref){ RefreshRates(); int t=-1;
   if(c=="B"){ double lb=NormalizeDouble(ref+BracketH*p,Digits); t=OrderSend(Symbol(),OP_BUYSTOP,0.01,lb,slip,NormalizeDouble(lb-BracketSL*p,Digits),NormalizeDouble(lb+BracketTP*p,Digits),"B",magic,TimeCurrent()+BracketExpiryMin*60,clrBlue); }
   else { double ls=NormalizeDouble(ref-BracketH*p,Digits); t=OrderSend(Symbol(),OP_SELLSTOP,0.01,ls,slip,NormalizeDouble(ls+BracketSL*p,Digits),NormalizeDouble(ls-BracketTP*p,Digits),"S",magic,TimeCurrent()+BracketExpiryMin*60,clrRed); }
   if(t>0){ Print("BRACKET ",c," #",t); RatioLog2(t); } else { Print("BRACKET ",c," err ",GetLastError()); } }
void PlaceBracket(){ RefreshRates(); rearmDone=0;
   if(BracketRegime!=1 || BuyRegimeOK()){ PlaceLeg("B",Ask); }
   if(BracketRegime!=1 || SellRegimeOK()){ PlaceLeg("S",Bid); } }
void BracketMng(){ int bOpen=CountCmt("B",OP_BUY), sOpen=CountCmt("S",OP_SELL);
   if(bOpen>0 && BracketOCO==1 && CountCmt("S",OP_SELLSTOP)>0){ DeletePendings("S"); Print("BRACKET OCO: S deleted"); }
   if(sOpen>0 && BracketOCO==1 && CountCmt("B",OP_BUYSTOP)>0){ DeletePendings("B"); Print("BRACKET OCO: B deleted"); }
   if(BracketRearm==1 && rearmDone==0){ RefreshRates();
      if(bOpen>0 && CountCmt("S",OP_SELLSTOP)==0 && sOpen==0){ rearmDone=1; PlaceLeg("S",Bid); Print("BRACKET rearm S"); }
      else if(sOpen>0 && CountCmt("B",OP_BUYSTOP)==0 && bOpen==0){ rearmDone=1; PlaceLeg("B",Ask); Print("BRACKET rearm B"); } } }double RSlp(int tf,int pd,int sh){ return((iMA(s,tf,pd,0,MODE_SMA,PRICE_CLOSE,sh)-iMA(s,tf,pd,0,MODE_SMA,PRICE_CLOSE,sh+1))/p); }
void RatioLog(int ticket){ if(UseRatioLog!=1){ return; } int tfs[4]; tfs[0]=1; tfs[1]=5; tfs[2]=15; tfs[3]=60; int pds[4]; pds[0]=2; pds[1]=5; pds[2]=10; pds[3]=15;
   for(int ia=0; ia<4; ia++){ for(int ib=0; ib<4; ib++){ string ln="RLOG #"+IntegerToString(ticket)+" tf"+IntegerToString(tfs[ia])+" pd"+IntegerToString(pds[ib]);
      for(int sh=1; sh<=5; sh++){ double s0=RSlp(tfs[ia],pds[ib],sh), s1=RSlp(tfs[ia],pds[ib],sh+1), s2=RSlp(tfs[ia],pds[ib],sh+2);
         double ac=s0-s1, ra=ac-(s1-s2);
         double st=iStochastic(s,tfs[ia],pds[ib],3,3,MODE_SMA,STO_LOWHIGH,MODE_MAIN,sh), rg=iATR(s,tfs[ia],pds[ib],sh)/p;
         double vol=iVolume(s,tfs[ia],sh), ht=(iHigh(s,tfs[ia],sh)-iClose(s,tfs[ia],sh))/p, dm=(iClose(s,tfs[ia],sh)-iMA(s,tfs[ia],pds[ib],0,MODE_SMA,PRICE_CLOSE,sh))/p;
         ln=ln+" |"+DoubleToStr(s0,2)+" "+DoubleToStr(ac,2)+" "+DoubleToStr(ra,2)+" "+DoubleToStr(st,1)+" "+DoubleToStr(rg,1)+" "+DoubleToStr(vol,0)+" "+DoubleToStr(ht,1)+" "+DoubleToStr(dm,1); }
      // tail: distance of last close above the lowest low of 20 and 50 bars (DFL), bars since Stoch(pd) dipped <= 20 (max 60)
      double c1=iClose(s,tfs[ia],1); double dfl20=(c1-iLow(s,tfs[ia],iLowest(s,tfs[ia],MODE_LOW,20,1)))/p, dfl50=(c1-iLow(s,tfs[ia],iLowest(s,tfs[ia],MODE_LOW,50,1)))/p;
      int bsd=60; for(int k=1; k<=60; k++){ if(iStochastic(s,tfs[ia],pds[ib],3,3,MODE_SMA,STO_LOWHIGH,MODE_MAIN,k)<=20){ bsd=k; break; } }
      ln=ln+" ||"+DoubleToStr(dfl20,1)+" "+DoubleToStr(dfl50,1)+" "+IntegerToString(bsd);
      Print(ln); } } }
//---- b5 helpers
int BuySend(string cm,color c){ if(UseParkBuys==1){ parkUntil=TimeCurrent()+ParkHoldMin*60; parkN++; if(UseVirtualBuy==1){ vPrice=Ask; vTP=Ask+BuyTPpts()*Point; vSL=Ask-BuySLpts()*Point; vHedged=0; } Print("PARKED buy signal ",parkN," at ",DoubleToStr(Ask,Digits)); return(9000000+parkN); } if(!Guard(LotSize(BuySLpts()),BuySLpts())){ return(-1); } RefreshRates(); return(OrderSend(Symbol(),OP_BUY,LotSize(BuySLpts()),Ask,slip,Ask-(BuySLpts()*Point),Ask+(BuyTPpts()*Point),cm,magic,0,c)); } //b14
void VirtualMng(){ if(vPrice<=0){ return; } RefreshRates(); double vt=vTP; if(VExitMode==1){ vt=vPrice+VFirstPts*Point; } if(VExitMode==2){ vt=vPrice+VTPpts*Point; } if(Bid>=vt || Bid<=vSL){ vPrice=0; return; } //b15 b16
   if(UseHedgeSell==1 && vHedged==0 && Bid<=vPrice-HedgeTrigger*p){ vHedged=1; if(!SellRegimeOK()){ Print("VHEDGE skipped: regime up"); return; }
      int ht=-1; if(!(UseHedgeHourBlock==1 && InHours(HedgeBlockFrom,HedgeBlockTo)) && Guard(LotSize(HedgeSL),HedgeSL)){ ht=OrderSend(Symbol(),OP_SELL,LotSize(HedgeSL),Bid,slip,NormalizeDouble(Bid+HedgeSL*p,Digits),NormalizeDouble(Bid-HedgeTP*p,Digits),"8",magic,0,clrRed); } vN++;
      if(ht>0){ Print("VHEDGE sell #",ht," n ",vN); RatioLog2(ht); } else { Print("VHEDGE err ",GetLastError()); } } }
int BuysOpen(){ int n=0; if(UseParkBuys==1 && (TimeCurrent()<parkUntil || vPrice>0)){ n++; } for(int i=0;i<OrdersTotal();i++){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES)){ if(OrderMagicNumber()==magic && OrderSymbol()==Symbol() && OrderType()==OP_BUY && StringSubstr(OrderComment(),0,1)!="B" && StringSubstr(OrderComment(),0,1)!="7" && StringSubstr(OrderComment(),0,1)!="L" && StringSubstr(OrderComment(),0,1)!="X" && StringSubstr(OrderComment(),0,1)!="H"){ n++; } } } return n; }
void PlaceSellStop(){ if(StopHourBlocked()){ return; } if(!SellRegimeOK()){ Print("SELLSTOP skipped: regime up"); return; } if(!Guard(LotSize(SellStopSL),SellStopSL)){ return; } RefreshRates(); double lvl=NormalizeDouble(Bid-SellStopDist*p,Digits);
   int t=OrderSend(Symbol(),OP_SELLSTOP,LotSize(SellStopSL),lvl,slip,NormalizeDouble(lvl+SellStopSL*p,Digits),NormalizeDouble(lvl-SellStopTP*p,Digits),"7",magic,TimeCurrent()+SellStopExpiryMin*60,clrRed);
   if(t>0){ Print("SELLSTOP #",t," at ",DoubleToStr(lvl,Digits)," expires ",TimeToStr(TimeCurrent()+SellStopExpiryMin*60)); RatioLog2(t); } else { Print("SELLSTOP err ",GetLastError()); } }
void OrderMng(){
if(OrdersTotal()>0){
 for(int a=0; a<=OrdersTotal(); a++){
     if(OrderSelect(a,SELECT_BY_POS,MODE_TRADES)==1){
         if(OrderMagicNumber()==magic){
           if(OrderType()==OP_BUY){ 
           if(StringSubstr(OrderComment(),0,1)=="B" || StringSubstr(OrderComment(),0,1)=="7" || StringSubstr(OrderComment(),0,1)=="L" || StringSubstr(OrderComment(),0,1)=="X" || StringSubstr(OrderComment(),0,1)=="H"){ continue; } //b12: bracket buys keep their own TP/SL
           //---- b8 round-number buy ("9"): break-even after +RoundBreakEven pts, closed after RoundMaxHours; no hedge/trail on it
           if(StringSubstr(OrderComment(),0,1)=="9"){ RefreshRates();
              if(TimeCurrent()-OrderOpenTime()>=RoundMaxHours*3600){ if(OrderClose(OrderTicket(),OrderLots(),Bid,slip,clrAqua)){ Print("ROUND closed by time #",OrderTicket()," at ",DoubleToStr(Bid,Digits)); } else { Print("ROUND close err ",GetLastError()); } continue; }
              if(Bid>=OrderOpenPrice()+RoundBreakEven*p && OrderStopLoss()<OrderOpenPrice()){ if(OrderModify(OrderTicket(),OrderOpenPrice(),NormalizeDouble(OrderOpenPrice()+1*p,Digits),OrderTakeProfit(),0,clrAqua)){ Print("ROUND break-even #",OrderTicket()); } else { Print("ROUND BE err ",GetLastError()); } }
              continue; }
           //---- b5 hedge sell: once per buy, when it is HedgeTrigger pts under water
           if(UseHedgeSell==1 && OrderTicket()!=hedgedTicket){ RefreshRates();
              if(Bid<=OrderOpenPrice()-HedgeTrigger*p){ hedgedTicket=OrderTicket(); if(!SellRegimeOK()){ Print("HEDGE skipped: regime up, buy #",hedgedTicket); continue; }
                 int ht=-1; if(!(UseHedgeHourBlock==1 && InHours(HedgeBlockFrom,HedgeBlockTo)) && Guard(LotSize(HedgeSL),HedgeSL)){ ht=OrderSend(Symbol(),OP_SELL,LotSize(HedgeSL),Bid,slip,NormalizeDouble(Bid+HedgeSL*p,Digits),NormalizeDouble(Bid-HedgeTP*p,Digits),"8",magic,0,clrRed); }
                 if(ht>0){ Print("HEDGE sell #",ht," for buy #",hedgedTicket," at ",DoubleToStr(Bid,Digits)); RatioLog2(ht); } else { Print("HEDGE err ",GetLastError()); }
                 continue; } }
           //---- claude_b1 trailing stop (b4: with TrailRemoveTP the 10-pt TP is removed at open, so the trail decides the exit)
           if(UseTrail==1){ RefreshRates(); double up=(Bid-OrderOpenPrice())/p;
              if(TrailRemoveTP==1 && OrderTicket()!=LastModTicket2 && OrderTakeProfit()<OrderOpenPrice()+1000*p){
                 if(OrderModify(OrderTicket(),OrderOpenPrice(),OrderStopLoss(),NormalizeDouble(OrderOpenPrice()+2000*p,Digits),0,clrOrange)){
                    LastModTicket2=OrderTicket(); Print("Trail: TP removed for #",OrderTicket()); } else { Print("Trail TP-remove err ",GetLastError()); } continue; }
              if(up>=TrailStart){ double newsl=NormalizeDouble(Bid-TrailStep*p,Digits);
                 if(newsl>OrderStopLoss()+0.5*p){ double newtp=OrderTakeProfit(); if(TrailRemoveTP==1){ newtp=NormalizeDouble(OrderOpenPrice()+2000*p,Digits); }
                    if(!OrderModify(OrderTicket(),OrderOpenPrice(),newsl,newtp,0,clrOrange)){ Print("Trail modify err ",GetLastError()); }
                    else { LastModTicket2=OrderTicket(); } continue; } } }
           //---- end trailing stop

           
          
         if(OrderTicket()!=LastModTicket2 && UseWideBuy!=1){ //b10: with UseWideBuy the original TP-to-10 modify is skipped so wide buys keep WideBuyTP  
          //Print("Buy order # ",OrderTicket()," found @ ",OrderOpenPrice()," ",sd(OrderOpenPrice(),Digits),
           //" tp ",OrderTakeProfit()," ",sd(OrderTakeProfit(),Digits)); 
            //tp verify 2/2
                RefreshRates();  if(OrderTakeProfit()<(OrderOpenPrice()+(10*Point)) ||  //default 7
                OrderTakeProfit()>(OrderOpenPrice()+(8*Point))   
                  ){ tkp=OrderOpenPrice()+(tp*p); 
                
                    
     //Modify the order when the tp is wrong, or when the swap goes into effect.               
if(OrderModify(OrderTicket(),OrderOpenPrice(),OrderStopLoss(),(OrderOpenPrice()+(10 //default 8
*Point)),0,clrYellow)){ //Works in tester, 
 // just need the right amount of points. 
                    
                    LastModTicket2=OrderTicket(); 
                       Print("TP Change for Order # ",OrderTicket()," to ",tkp," ",OrderTakeProfit()," ",sd(tkp,Digits)," Comm: ",OrderCommission(),
                       " complete ");
                        }else{ 
                         double diff=tkp-OrderOpenPrice();
                        Print("TP Change err ",GetLastError()," OOP ",OrderOpenPrice()," tp ",tkp," ",sd(tkp,Digits)," diff ",diff," Comm: ",OrderCommission()); }  }}
         
          if(SwapHelp==1){
            if(OrderProfit()<0 || OrderSwap()!=0){ 
                  //FXOpen usually expresses swap in points. 
                  
                  if(OrderSwap()!=0){ if(OrderTicket()!=LastModTicket){ double osp=MathCeil(MathAbs(OrderSwap())/OrderLots()); 
                  if(NeededTP==0){ NeededTP=OrderOpenPrice()+(osp*p); //wrong?
                    }
                    
                    Print("Order: ",OrderTicket()," swap: ",OrderSwap()," osp ",osp," OTP ",OrderTakeProfit()," NeededTP ",NeededTP); 
                if(OrderTakeProfit()<NeededTP){
                   if(OrderModify(OrderTicket(),Ask,OrderStopLoss(),NeededTP,0,clrYellow)==1){ NeededTP=0; LastModTicket=OrderTicket();
                       }else{Print("OrderMod Err ",GetLastError()); } }
                   }}
                 } 
            }
         
        double spr=MarketInfo(s,MODE_SPREAD);   double pricediff=(Ask-OrderOpenPrice())/p;
            
            //major loss unexplained jan 5 2011 
            double maop=MathAbs(OrderProfit())/OrderLots();  double Ratio=0; if(maop!=0){ Ratio=MathAbs(pricediff)/maop;}
             
//if(OrderProfit()<0){Print("OrderTicket ",OrderTicket()," OrderOpenPrice ",OrderOpenPrice()," Ask ",Ask," OrderTakeProfit ",OrderTakeProfit(),
 //" OrderComm ",OrderCommission()," OrderProf ",OrderProfit()," OrderSwap ",OrderSwap()," OrderComment ",OrderComment(),
 // " OrderLots ",OrderLots()," spr ",spr," pricediff ",pricediff," Ratio ",Ratio); }
            
if(UseWideBuy!=1 && OrderProfit()>= MathAbs(OrderSwap())+(MathAbs(OrderCommission())+ (spr*OrderLots()))   ){ //b11: with UseWideBuy the close-at-first-profit exit is skipped so the 300/100 targets decide
   if(OrderClose(OrderTicket(),OrderLots(),Ask,slip,clrYellow)==1){}else{Print("OrderClose err ",GetLastError()); return; }  
            }
            if(OrdersTotal()>0){
              //if broker doesn't allow you to send orders with very tight take profits, but does allow you to 
              //modify the order to have a tight tp after the order opens, then put in some 
              // ordermodify code here and test it out. 
            }
            
         }
      }
  }}
}
return;}

string sd(double val, int len){  double Val=0;  double Val2=MathPow(10,Digits); double Val3=val*Val2;
 double Val4=MathFloor(Val3);  double Val5=Val4/Val2; 
  if(len==Digits){ //Print("Val ",Val," val ",val," Val2 ",Val2," Digits ",Digits," Val3 ",Val3," Val4 ",Val4," Val5 ",Val5);
  Val=((MathFloor(val*(MathPow(10,Digits))))/Digits); }

//it's better to take the values after the decimal point, then use MathRound. 

//you have the value, multiply by 100, do the mathround

//get the difference between the raw value and the rounded value?

//2019.03.21 18:13:10.792	2011.01.03 17:53:20  Mar 21 2019 Beta Test EURUSD,M15: 
//val 0.8100000000000001 len 2 val2 81.0 val3 81.0 val4 81.0 val5 81.0 val6 0.8100000000000001
string ShortString="";
if(Val==0){
double val2=val*100; double val3=MathRound(val2);  double val4=MathFloor(val2);   double val5=MathCeil(val2); 
 double val6=val/100;   double val7=val2/100; double val3b=val3/100; string val3s=DoubleToStr(val3b,len); return(val3s); 
  string InputString=DoubleToStr(nd(val,len),len);
if(StringLen(InputString)>=4){Print("val ",val," len ",len," val2 ",val2," val3 ",val3," val3s ",val3s," val3b ",val3b,
" val4 ",val4," val5 ",
val5," val6 ",val6," val7 ",val7); } 
 int dec=StringFind(InputString,".",0); int len2=StringLen(InputString);   int len3=(len2-dec);  
  string subsst=StringSubstr(InputString,0,dec); string subsst2=StringSubstr(InputString,dec,len3);  
   if(subsst2=="00"){subsst2="";} 
    ShortString=StringConcatenate(subsst,subsst2);  }
 // if(Hour()==0){ 
  // Print("val ",val," Input String ",InputString," dec ",dec," len2 ",len2," len3 ",len3," subsst ",subsst,
  // " subsst ",subsst2," ShortString ",ShortString); }
  if(Val!=0){ShortString=DoubleToStr(Val);}
   return(ShortString); }
   
double sto(int tf, int pd, int sh){ return(iStochastic(s,tf,pd,3,3,MODE_SMA,STO_LOWHIGH,MODE_MAIN,sh)); 
   //close / close method tends to hit the upper and lower extremes faster 
   }
 
double abs(double val){  return(MathAbs(val)); }

long vol(int tf, int sh){return(iVolume(s,tf,sh));} 

double rng(int tf, int pd, int sh){return(iATR(s,tf,pd,sh)/p);}


//---- claude_b1 feature function: fills bf_* globals from CLOSED bars of timeframe tf (bar 1 = last closed) ----
void BrFeat(int tf){
   double e[8]; for(int k=0;k<8;k++){ e[k]=iMA(s,tf,20,0,MODE_EMA,PRICE_CLOSE,k+1); }
   double s0=(e[0]-e[1])/p, s1=(e[1]-e[2])/p, s2=(e[2]-e[3])/p;
   bf_slope=s0; bf_accel=s0-s1; bf_roa=bf_accel-(s1-s2); bf_sara=bf_slope+bf_accel+bf_roa;
   bf_slopeavg=0; for(int k2=0;k2<6;k2++){ bf_slopeavg+=(e[k2]-e[k2+1])/p; } bf_slopeavg/=6;
   double mx=-1e9, mn=1e9; for(int k3=0;k3<12;k3++){ double d=(iClose(s,tf,k3+1)-iClose(s,tf,k3+2))/p; if(d>mx){mx=d;} if(d<mn){mn=d;} }
   if(mx>0){ bf_mmr=mn/mx; } else { bf_mmr=-9; }
   bf_rng=(iHigh(s,tf,1)-iLow(s,tf,1))/p;
   double va=0; for(int k4=2;k4<=21;k4++){ va+=iVolume(s,tf,k4); } va/=20; if(va<1){va=1;} bf_vrel=iVolume(s,tf,1)/va;
   bf_K=iStochastic(s,tf,14,3,1,MODE_SMA,STO_LOWHIGH,MODE_MAIN,1); bf_D=iStochastic(s,tf,14,3,1,MODE_SMA,STO_LOWHIGH,MODE_SIGNAL,1);
   bf_prv=bf_rng+bf_vrel*10+(bf_K-bf_D)+bf_K/10; if(bf_prv!=0){ bf_sara_prv=bf_sara/bf_prv; } else { bf_sara_prv=0; } }
//---- end claude_b1 ----

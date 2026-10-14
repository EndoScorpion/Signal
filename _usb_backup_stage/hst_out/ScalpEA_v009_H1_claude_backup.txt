//+------------------------------------------------------------------+
//| ScalpEA_v009_H1_claude.mq4  - fresh H1/H4 signals, buy AND sell   |
//| Run on an EURUSD H1 chart. One plain run tests 24 variants:       |
//|   signal {1 H4-trend + H1 pullback, 2 H1 RSI extreme, 3 H1 20-bar |
//|   breakout} x direction {buy, sell} x target {200,400} x trail    |
//|   {0,100}. Stop 300 pts, time exit after MaxBars H1 bars.         |
//| Each variant: own magic 8000000+v, max one open order.            |
//| RULESUMMARY lines printed at the end (read from tester log).      |
//+------------------------------------------------------------------+
#property strict
extern int SLpts=300;
extern int MaxBars=120;      // 5 trading days on H1
extern int TrendEMA=50;      // H4
extern int PullEMA=20;       // H1
extern int RSIlow=30;
extern int RSIhigh=70;
extern int BreakBars=20;
int gTP[2]={200,400}; int gTR[2]={0,100};
datetime lastBar=0;

bool H4Up(){ double e1=iMA(NULL,PERIOD_H4,TrendEMA,0,MODE_EMA,PRICE_CLOSE,1), e2=iMA(NULL,PERIOD_H4,TrendEMA,0,MODE_EMA,PRICE_CLOSE,2); return iClose(NULL,PERIOD_H4,1)>e1 && e1>e2; }
bool H4Dn(){ double e1=iMA(NULL,PERIOD_H4,TrendEMA,0,MODE_EMA,PRICE_CLOSE,1), e2=iMA(NULL,PERIOD_H4,TrendEMA,0,MODE_EMA,PRICE_CLOSE,2); return iClose(NULL,PERIOD_H4,1)<e1 && e1<e2; }

// sig 1: trend pullback. buy: H4 up, H1 bar dipped to EMA20 and closed back above it. sell: mirror.
bool Sig1(int dir){ double e=iMA(NULL,0,PullEMA,0,MODE_EMA,PRICE_CLOSE,1);
 if(dir==0) return H4Up() && Low[1]<=e && Close[1]>e && Close[1]>Open[1];
 return H4Dn() && High[1]>=e && Close[1]<e && Close[1]<Open[1]; }
// sig 2: RSI extreme mean reversion. buy: RSI(14) crosses back above RSIlow. sell: crosses back below RSIhigh.
bool Sig2(int dir){ double r1=iRSI(NULL,0,14,PRICE_CLOSE,1), r2=iRSI(NULL,0,14,PRICE_CLOSE,2);
 if(dir==0) return r2<RSIlow && r1>=RSIlow;
 return r2>RSIhigh && r1<=RSIhigh; }
// sig 3: breakout momentum. buy: H1 close above highest high of prior BreakBars bars. sell: below lowest low.
bool Sig3(int dir){ if(dir==0){ int h=iHighest(NULL,0,MODE_HIGH,BreakBars,2); return Close[1]>High[h]; }
 int l=iLowest(NULL,0,MODE_LOW,BreakBars,2); return Close[1]<Low[l]; }

bool Fires(int s,int dir){ if(s==1) return Sig1(dir); if(s==2) return Sig2(dir); return Sig3(dir); }
bool VOpen(int v){ for(int i=OrdersTotal()-1;i>=0;i--){ if(OrderSelect(i,SELECT_BY_POS,MODE_TRADES) && OrderMagicNumber()==8000000+v) return true; } return false; }
// v = ((s-1)*2+dir)*4 + ti*2 + ri
void Decode(int v,int &s,int &dir,int &ti,int &ri){ ri=v%2; ti=(v/2)%2; dir=(v/4)%2; s=v/8+1; }

int OnInit(){ return(INIT_SUCCEEDED); }

void OnTick(){
 Manage();
 if(Time[0]==lastBar) return; lastBar=Time[0];
 if(DayOfWeek()==5 && Hour()>=19) return;             // keep the Friday late block
 for(int v=0;v<24;v++){ int s,dir,ti,ri; Decode(v,s,dir,ti,ri); if(VOpen(v)) continue; if(!Fires(s,dir)) continue; int t=-1;
  if(dir==0) t=OrderSend(Symbol(),OP_BUY,0.01,Ask,5,Ask-SLpts*Point,Ask+gTP[ti]*Point,"v"+IntegerToString(v),8000000+v,0,clrGreen);
  else       t=OrderSend(Symbol(),OP_SELL,0.01,Bid,5,Bid+SLpts*Point,Bid-gTP[ti]*Point,"v"+IntegerToString(v),8000000+v,0,clrRed);
  if(t<0) Print("OrderSend err ",GetLastError()," v=",v); } }

void Manage(){ for(int i=OrdersTotal()-1;i>=0;i--){ if(!OrderSelect(i,SELECT_BY_POS,MODE_TRADES)) continue; int v=OrderMagicNumber()-8000000; if(v<0||v>23) continue;
  int s,dir,ti,ri; Decode(v,s,dir,ti,ri);
  int age=iBarShift(NULL,0,OrderOpenTime(),false);
  if(MaxBars>0 && age>=MaxBars){ bool ok=(OrderType()==OP_BUY)?OrderClose(OrderTicket(),OrderLots(),Bid,5,clrGray):OrderClose(OrderTicket(),OrderLots(),Ask,5,clrGray); if(!ok) Print("time close err ",GetLastError()); continue; }
  int tr=gTR[ri]; if(tr<=0) continue;
  if(OrderType()==OP_BUY){ double nsl=Bid-tr*Point; if(nsl>OrderOpenPrice() && nsl>OrderStopLoss()+Point) if(!OrderModify(OrderTicket(),OrderOpenPrice(),nsl,OrderTakeProfit(),0,clrBlue)) Print("trail err ",GetLastError()); }
  else { double nsl2=Ask+tr*Point; if(nsl2<OrderOpenPrice() && nsl2<OrderStopLoss()-Point) if(!OrderModify(OrderTicket(),OrderOpenPrice(),nsl2,OrderTakeProfit(),0,clrBlue)) Print("trail err ",GetLastError()); } } }

void OnDeinit(const int reason){ int n[24],w[24]; double net[24],gp[24],gl[24]; ArrayInitialize(n,0); ArrayInitialize(w,0); ArrayInitialize(net,0); ArrayInitialize(gp,0); ArrayInitialize(gl,0);
 for(int i=0;i<OrdersHistoryTotal();i++){ if(!OrderSelect(i,SELECT_BY_POS,MODE_HISTORY)) continue; int v=OrderMagicNumber()-8000000; if(v<0||v>23||OrderType()>OP_SELL) continue;
  double pnl=OrderProfit()+OrderCommission()+OrderSwap(); n[v]++; net[v]+=pnl; if(pnl>0){w[v]++; gp[v]+=pnl;}else{gl[v]-=pnl;} }
 for(int v=0;v<24;v++){ int s,dir,ti,ri; Decode(v,s,dir,ti,ri); double pf=0; if(gl[v]>0) pf=gp[v]/gl[v];
  Print("RULESUMMARY sig=",s," dir=",(dir==0?"buy":"sell")," tp=",gTP[ti]," trail=",gTR[ri]," sl=",SLpts," trades=",n[v]," wins=",w[v]," net=",DoubleToStr(net[v],2)," perTrade=",DoubleToStr(n[v]>0?net[v]/n[v]:0,3)," pf=",DoubleToStr(pf,2)); } }

// BranchSwitch.mqh - b35 bounded branch switcher. OFF by default.
// Reads MQL4\Files\<BranchFile>: one branch per line  name;Key=Val;Key=Val...   ('#' = comment)
// Only branches already backtested belong in the file. Values are applied as-is; the EA never invents or tunes thresholds.
// Attribution: each closed SELL is credited to the branch that was active when it OPENED. Score = sum of its last BsWindow trades.
// Switch only if: active branch has >= BsWindow trades, its score < BsLossLimit, and >= BsCooldownHrs since last switch.
// Next branch = best stored score among the others (untried branches score 0). Hysteresis: must beat active by BsHyst $.
extern bool   UseBranchSwitch=0;
extern string BranchFile="branches.txt";
extern int    BsWindow=20;
extern double BsLossLimit=-10;
extern double BsHyst=2;
extern int    BsCooldownHrs=72;
string   bsName[20]; string bsSet[20]; int bsN=0, bsActive=0; datetime bsLastSwitch=0;
double   bsPnl[20][50]; int bsCnt[20]; datetime bsFrom[200]; int bsWho[200]; int bsHist=0; int bsLastHistTotal=0;
void BsApply(int b){ string kv[]; int n=StringSplit(bsSet[b],';',kv);
   for(int i=0;i<n;i++){ string p[]; if(StringSplit(kv[i],'=',p)!=2){ continue; } string k=StringTrimLeft(StringTrimRight(p[0])); double v=StringToDouble(p[1]);
      if(k=="UseChaosErGate"){ UseChaosErGate=(v!=0); } else if(k=="ErPer"){ ErPer=(int)v; } else if(k=="ErMax"){ ErMax=v; }
      else if(k=="UseZGate"){ UseZGate=(v!=0); } else if(k=="ZTF"){ ZTF=(int)v; } else if(k=="ZPeriod"){ ZPeriod=(int)v; } else if(k=="ZMax"){ ZMax=v; }
      else if(k=="UseDailyRangeFilter"){ UseDailyRangeFilter=(v!=0); } else if(k=="RangeAtrPeriod"){ RangeAtrPeriod=(int)v; } else if(k=="MaxRangeAtrMultiplier"){ MaxRangeAtrMultiplier=v; }
      else if(k=="UseAHRateGate"){ UseAHRateGate=(v!=0); } else if(k=="AHRPer"){ AHRPer=(int)v; } else if(k=="AHRateMax"){ AHRateMax=v; }
      else if(k=="UseFdGate"){ UseFdGate=(v!=0); } else if(k=="FdPer"){ FdPer=(int)v; } else if(k=="FdMin"){ FdMin=v; }
      else if(k=="UseMpErGate"){ UseMpErGate=(v!=0); } else if(k=="MpErTF"){ MpErTF=(int)v; } else if(k=="MpErPer"){ MpErPer=(int)v; } else if(k=="MpErMax"){ MpErMax=v; }
      else if(k=="UseMpFadeGate"){ UseMpFadeGate=(v!=0); } else if(k=="MpFadeTF"){ MpFadeTF=(int)v; } else if(k=="MpFadePer"){ MpFadePer=(int)v; } else if(k=="MpFadeMin"){ MpFadeMin=v; }
      else if(k=="UseMpFracGate"){ UseMpFracGate=(v!=0); } else if(k=="MpFracTF"){ MpFracTF=(int)v; } else if(k=="MpFracPer"){ MpFracPer=(int)v; } else if(k=="MpFracMax"){ MpFracMax=v; }
      else if(k=="UseMpZGate"){ UseMpZGate=(v!=0); } else if(k=="MpZTF"){ MpZTF=(int)v; } else if(k=="MpZPer"){ MpZPer=(int)v; } else if(k=="MpZMax"){ MpZMax=v; }
      else if(k=="UseMpRangeGate"){ UseMpRangeGate=(v!=0); } else if(k=="MpRangeTF"){ MpRangeTF=(int)v; } else if(k=="MpRangePer"){ MpRangePer=(int)v; } else if(k=="MpRangeMax"){ MpRangeMax=v; }
      else { Print("b35 BranchSwitch: unknown key ignored: ",k); } }
   Print("b35 BranchSwitch: active branch = ",bsName[b]); }
void BsReset(){ UseChaosErGate=0; UseZGate=0; UseDailyRangeFilter=0; UseAHRateGate=0; UseFdGate=0; UseMpErGate=0; UseMpFadeGate=0; UseMpFracGate=0; UseMpZGate=0; UseMpRangeGate=0; }
void BranchSwitchInit(){ int h=FileOpen(BranchFile,FILE_READ|FILE_TXT|FILE_ANSI); if(h==INVALID_HANDLE){ Print("b35 BranchSwitch: cannot open ",BranchFile," - switcher off"); UseBranchSwitch=0; return; }
   while(!FileIsEnding(h) && bsN<20){ string ln=StringTrimLeft(StringTrimRight(FileReadString(h))); if(StringLen(ln)<3 || StringGetChar(ln,0)=='#'){ continue; }
      int c=StringFind(ln,";"); if(c<1){ continue; } bsName[bsN]=StringSubstr(ln,0,c); bsSet[bsN]=StringSubstr(ln,c+1); bsCnt[bsN]=0; bsN++; }
   FileClose(h); if(bsN==0){ UseBranchSwitch=0; Print("b35 BranchSwitch: no branches - off"); return; }
   bsActive=0; BsReset(); BsApply(0); bsLastSwitch=TimeCurrent(); bsFrom[0]=TimeCurrent(); bsWho[0]=0; bsHist=1; bsLastHistTotal=OrdersHistoryTotal(); }
int BsOwner(datetime t){ int w=bsWho[0]; for(int i=0;i<bsHist;i++){ if(bsFrom[i]<=t){ w=bsWho[i]; } } return(w); }
double BsScore(int b){ if(bsCnt[b]==0){ return(0); } int n=MathMin(bsCnt[b],BsWindow); double s=0; for(int i=0;i<n;i++){ s+=bsPnl[b][(bsCnt[b]-1-i)%50]; } return(s); }
void BranchSwitchTick(){ int ht=OrdersHistoryTotal(); if(ht==bsLastHistTotal){ return; }
   for(int j=bsLastHistTotal;j<ht;j++){ if(!OrderSelect(j,SELECT_BY_POS,MODE_HISTORY) || OrderSymbol()!=Symbol() || OrderType()!=OP_SELL || OrderMagicNumber()!=magic){ continue; }
      int b=BsOwner(OrderOpenTime()); bsPnl[b][bsCnt[b]%50]=OrderProfit()+OrderSwap()+OrderCommission(); bsCnt[b]++; }
   bsLastHistTotal=ht;
   if(bsN<2 || bsCnt[bsActive]<BsWindow || TimeCurrent()-bsLastSwitch<BsCooldownHrs*3600){ return; }
   double cur=BsScore(bsActive); if(cur>=BsLossLimit){ return; }
   int best=-1; double bs=-1e9; for(int i=0;i<bsN;i++){ if(i==bsActive){ continue; } double s=BsScore(i); if(s>bs){ bs=s; best=i; } }
   if(best<0 || bs<cur+BsHyst || bsHist>=200){ return; }
   Print("b35 BranchSwitch: ",bsName[bsActive]," score ",DoubleToString(cur,2)," -> ",bsName[best]," score ",DoubleToString(bs,2));
   bsActive=best; BsReset(); BsApply(best); bsLastSwitch=TimeCurrent(); bsFrom[bsHist]=TimeCurrent(); bsWho[bsHist]=best; bsHist++; bsCnt[best]=0; }

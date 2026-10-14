// WinGates_b34.mqh - GEN b34 multi-period gate clones (inputs + logic). Included by b35+.
// b34 multi-period gate clones (TF in minutes: 1,5,15,60,240). ATR = ATR(14) on the gate's own TF. Closed bars only.
extern bool   UseMpErGate=0;      // efficiency ratio over MpErPer bars of MpErTF <= MpErMax  (branch #6: H1/25/0.16)
extern int    MpErTF=60;
extern int    MpErPer=25;
extern double MpErMax=0.16;
extern bool   UseMpFadeGate=0;    // (Close1-Close[1+MpFadePer])/ATR >= MpFadeMin  (M5/30/-1.9 or M1/150/-2.33)
extern int    MpFadeTF=5;
extern int    MpFadePer=30;
extern double MpFadeMin=-1.9;
extern bool   UseMpFracGate=0;    // (highest high of MpFracPer bars - Close1)/ATR <= MpFracMax  (M15/150/10.4 or M1/150/7.8)
extern int    MpFracTF=15;
extern int    MpFracPer=150;
extern double MpFracMax=10.4;
extern bool   UseMpZGate=0;       // 0.7*price z + 0.3*volume z over MpZPer bars <= MpZMax  (H1/75/1.04 or M15/250/1.15)
extern int    MpZTF=60;
extern int    MpZPer=75;
extern double MpZMax=1.04;
extern bool   UseMpRangeGate=0;   // bar1 range / avg true range of MpRangePer bars <= MpRangeMax  (H1/150/1.26)
extern int    MpRangeTF=60;
extern int    MpRangePer=150;
extern double MpRangeMax=1.26;

//---- b34 multi-period gate clones
double Atr34(int tf){ double a=iATR(Symbol(),tf,14,1); if(a<=0){ a=Point; } return(a); }
bool Gates34(){
   if(UseMpErGate==1){ int t=MpErTF; double s=0; for(int i=1;i<=MpErPer;i++){ s+=MathAbs(iClose(Symbol(),t,i)-iClose(Symbol(),t,i+1)); }
      if(s>0 && MathAbs(iClose(Symbol(),t,1)-iClose(Symbol(),t,MpErPer+1))/s>MpErMax){ return(false); } }
   if(UseMpFadeGate==1){ int t2=MpFadeTF; if((iClose(Symbol(),t2,1)-iClose(Symbol(),t2,1+MpFadePer))/Atr34(t2)<MpFadeMin){ return(false); } }
   if(UseMpFracGate==1){ int t3=MpFracTF; double hh=iHigh(Symbol(),t3,iHighest(Symbol(),t3,MODE_HIGH,MpFracPer,1));
      if((hh-iClose(Symbol(),t3,1))/Atr34(t3)>MpFracMax){ return(false); } }
   if(UseMpZGate==1){ int t4=MpZTF,n=MpZPer; double m=0,vm=0; for(int j=1;j<=n;j++){ m+=iClose(Symbol(),t4,j); vm+=(double)iVolume(Symbol(),t4,j); } m/=n; vm/=n;
      double v=0,vv=0; for(int k=1;k<=n;k++){ double d=iClose(Symbol(),t4,k)-m,dv=(double)iVolume(Symbol(),t4,k)-vm; v+=d*d; vv+=dv*dv; }
      double sd=MathSqrt(v/n),svd=MathSqrt(vv/n); double z=0,zv=0; if(sd>0){ z=(iClose(Symbol(),t4,1)-m)/sd; } if(svd>0){ zv=((double)iVolume(Symbol(),t4,1)-vm)/svd; }
      if(0.7*z+0.3*zv>MpZMax){ return(false); } }
   if(UseMpRangeGate==1){ int t5=MpRangeTF; double tr=0; for(int r=1;r<=MpRangePer;r++){ tr+=MathMax(iHigh(Symbol(),t5,r),iClose(Symbol(),t5,r+1))-MathMin(iLow(Symbol(),t5,r),iClose(Symbol(),t5,r+1)); } tr/=MpRangePer;
      if(tr>0 && (iHigh(Symbol(),t5,1)-iLow(Symbol(),t5,1))/tr>MpRangeMax){ return(false); } }
   return(true); }

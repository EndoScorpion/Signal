// WinGates_b38.mqh - slope smoothness gates (2025-26 sweep). OFF by default. Slope = SMA(Per) bar-to-bar change on TF (minutes), closed bars.
extern bool   UseSlopeJitterGate=0; // jitter = stdev(last JitN slopes)/mean|slope|; sell only if jitter >= JitMin (choppy slope)  M15/100/10 >= 0.177
extern int    JitTF=15;
extern int    JitPer=100;
extern int    JitN=10;
extern double JitMin=0.177;
extern bool   UseSameSignGate=0;    // share of last SsN slopes with same sign as previous; sell only if <= SsMax (slope keeps flipping)  H1/20/10 <= 0.90
extern int    SsTF=60;
extern int    SsPer=20;
extern int    SsN=10;
extern double SsMax=0.90;
double Sl38(int tf,int per,int sh){ return(iMA(Symbol(),tf,per,0,MODE_SMA,PRICE_CLOSE,sh)-iMA(Symbol(),tf,per,0,MODE_SMA,PRICE_CLOSE,sh+1)); }
bool Gates38(){
   if(UseSlopeJitterGate==1){ double s=0,s2=0,a=0; for(int i=1;i<=JitN;i++){ double v=Sl38(JitTF,JitPer,i); s+=v; s2+=v*v; a+=MathAbs(v); }
      double m=s/JitN, sd=MathSqrt(MathMax(0,s2/JitN-m*m)*JitN/MathMax(1,JitN-1)); a/=JitN; if(a>0 && sd/a<JitMin){ return(false); } }
   if(UseSameSignGate==1){ int same=0; for(int j=1;j<=SsN;j++){ double v1=Sl38(SsTF,SsPer,j),v0=Sl38(SsTF,SsPer,j+1); if((v1>0&&v0>0)||(v1<0&&v0<0)||(v1==0&&v0==0)){ same++; } }
      if((double)same/SsN>SsMax){ return(false); } }
   return(true); }

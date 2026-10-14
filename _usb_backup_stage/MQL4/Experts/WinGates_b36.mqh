// WinGates_b36.mqh - b36 gates from the CCI/ADX/AD sweep (2025-26 sells). OFF by default. TF in minutes, closed bar 1.
// Note: MT4 iADX smooths with EMA(Per); the sweep used Wilder(n) ~ EMA(2n-1), so AdxPer=299 matches the sweep's 150.
extern bool   UseAdxLowGate=0;    // sell only in a weak trend: ADX(AdxPer) on AdxTF <= AdxMax   (sweep M5/150 -> 299, <= 7.6)
extern int    AdxTF=5;
extern int    AdxPer=299;
extern double AdxMax=7.6;
extern bool   UseAdxSlopeGate=0;  // ADX(AdxSlPer) 3-bar change on AdxSlTF >= AdxSlMin (ADX not rising fast)  (M5/100 -> 199, >= -0.097)
extern int    AdxSlTF=5;
extern int    AdxSlPer=199;
extern double AdxSlMin=-0.097;
extern bool   UseCciFloorGate=0;  // CCI(CciPer) on CciTF >= CciMin (not already deeply oversold)  (M15/250, >= -56)
extern int    CciFTF=15;
extern int    CciFPer=250;
extern double CciFMin=-56;
bool Gates36(){
   if(UseAdxLowGate==1 && iADX(Symbol(),AdxTF,AdxPer,PRICE_CLOSE,MODE_MAIN,1)>AdxMax){ return(false); }
   if(UseAdxSlopeGate==1 && iADX(Symbol(),AdxSlTF,AdxSlPer,PRICE_CLOSE,MODE_MAIN,1)-iADX(Symbol(),AdxSlTF,AdxSlPer,PRICE_CLOSE,MODE_MAIN,4)<AdxSlMin){ return(false); }
   if(UseCciFloorGate==1 && iCCI(Symbol(),CciFTF,CciFPer,PRICE_TYPICAL,1)<CciFMin){ return(false); }
   return(true); }

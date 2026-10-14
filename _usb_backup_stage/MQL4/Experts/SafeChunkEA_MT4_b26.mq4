//+------------------------------------------------------------------+
//|                                         SafeChunkEA_MT4_b26.mq4  |
//|                                  Copyright 2026, AlgoArchitect   |
//| Gemini Canvas v3 pasted by Nasif 2026-10-11 14:15 (verbatim      |
//| logic; only forward declarations added so it compiles in order). |
//+------------------------------------------------------------------+
#property strict

input double   InpPercentRisk        = 1.5;
input double   InpMinLotSize         = 0.01;
input double   InpMaxLotSize         = 10.0;
input int      InpAccountLeverage    = 500;
input int      InpProcessingChunk    = 1000;
input int      InpAtrPeriod          = 14;
input double   InpMultiplierSL       = 1.5;
input double   InpMultiplierTP       = 3.0;
input double   InpThresholdMultiplier = 0.5;
input int      InpMaxSpreadPoints    = 30.0;
input int      InpMaxOrderRetries    = 3;
input int      InpOrderSlippage      = 2;
input int      InpSystemMagic        = 882026;
input int      InpStartHour          = 9;
input int      InpStartMinute        = 0;
input int      InpEndHour            = 16;
input int      InpEndMinute          = 30;

double         glLocalStealthSL      = 0.0;
double         glLocalStealthTP      = 0.0;
bool           glTrackingStateActive = false;

void UpdateStealthGlobalVariable(int ticket, double targetSlValue);
void ManageActiveStealthTracking();
void ExecuteECNOrderSequence(int orderType, double allocatedLots, double slDistanceValue, double tpDistanceValue);

int OnInit()
{
   glTrackingStateActive = false; glLocalStealthSL = 0.0; glLocalStealthTP = 0.0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == InpSystemMagic)
         {
            int ticket = OrderTicket();
            string gvName = "EA_STEALTH_SL_" + IntegerToString(ticket);
            if(GlobalVariableCheck(gvName))
            {
               glLocalStealthSL = GlobalVariableGet(gvName);
               double instantAtrValue = iATR(Symbol(), PERIOD_CURRENT, InpAtrPeriod, 1);
               double calculatedTpDistance = instantAtrValue * InpMultiplierTP;
               if(OrderType() == OP_BUY)  glLocalStealthTP = NormalizeDouble(OrderOpenPrice() + calculatedTpDistance, Digits);
               if(OrderType() == OP_SELL) glLocalStealthTP = NormalizeDouble(OrderOpenPrice() - calculatedTpDistance, Digits);
               glTrackingStateActive = true;
               Print("[RESTORE LIVED] Rebuilt stealth state from disk GlobalVariable. Ticket: ", ticket, " SL: ", glLocalStealthSL);
            }
            else
            {
               double instantAtrValue = iATR(Symbol(), PERIOD_CURRENT, InpAtrPeriod, 1);
               double calculatedSlDistance = instantAtrValue * InpMultiplierSL;
               double calculatedTpDistance = instantAtrValue * InpMultiplierTP;
               if(OrderType() == OP_BUY)
               { glLocalStealthSL = NormalizeDouble(OrderOpenPrice() - calculatedSlDistance, Digits); glLocalStealthTP = NormalizeDouble(OrderOpenPrice() + calculatedTpDistance, Digits); }
               else if(OrderType() == OP_SELL)
               { glLocalStealthSL = NormalizeDouble(OrderOpenPrice() + calculatedSlDistance, Digits); glLocalStealthTP = NormalizeDouble(OrderOpenPrice() - calculatedTpDistance, Digits); }
               glTrackingStateActive = true;
               UpdateStealthGlobalVariable(ticket, glLocalStealthSL);
               Print("[FALLBACK STATE] Recalculated memory limits from ATR baseline. Saved to disk. Ticket: ", ticket);
            }
            break;
         }
      }
   }
   return(INIT_SUCCEEDED);
}

void UpdateStealthGlobalVariable(int ticket, double targetSlValue)
{
   string gvName = "EA_STEALTH_SL_" + IntegerToString(ticket);
   GlobalVariableSet(gvName, targetSlValue);
}

bool IsWithinTradingSession()
{
   if(TimeDayOfWeek(TimeCurrent()) == 0 || TimeDayOfWeek(TimeCurrent()) == 6) return(false);
   int currentMinutesStamp = (TimeHour(TimeCurrent()) * 60) + TimeMinute(TimeCurrent());
   int sessionStartBoundary = (InpStartHour * 60) + InpStartMinute;
   int sessionEndBoundary   = (InpEndHour * 60) + InpEndMinute;
   return(currentMinutesStamp >= sessionStartBoundary && currentMinutesStamp <= sessionEndBoundary);
}

double CalculateDynamicLotSize(double slDistancePoints)
{
   if(slDistancePoints <= 0.0) return(InpMinLotSize);
   double accountEquity = AccountEquity();
   double tickValue     = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tickSize      = MarketInfo(Symbol(), MODE_TICKSIZE);
   double lotStep       = MarketInfo(Symbol(), MODE_LOTSTEP);
   if(tickSize == 0.0 || tickValue == 0.0) return(InpMinLotSize);
   double totalRiskCash = accountEquity * (InpPercentRisk / 100.0);
   double riskPerLot = (slDistancePoints * (tickValue / tickSize)) * Point;
   if(riskPerLot <= 0.0) return(InpMinLotSize);
   double calculatedLots = totalRiskCash / riskPerLot;
   calculatedLots = MathFloor(calculatedLots / lotStep) * lotStep;
   if(calculatedLots < InpMinLotSize) calculatedLots = InpMinLotSize;
   if(calculatedLots > InpMaxLotSize) calculatedLots = InpMaxLotSize;
   return(NormalizeDouble(calculatedLots, 2));
}

int GetActiveStrategyPositionCount()
{
   int strategyTotal = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == InpSystemMagic) strategyTotal++;
   return(strategyTotal);
}

void OnTick()
{
   ManageActiveStealthTracking();
   if(!IsWithinTradingSession()) return;
   if(GetActiveStrategyPositionCount() > 0) return;
   double currentSpread = (double)MarketInfo(Symbol(), MODE_SPREAD);
   if(currentSpread > InpMaxSpreadPoints) return;
   int barsToCalculate = MathMin(Bars, InpProcessingChunk);
   if(barsToCalculate < 50) return;
   long currentCompletedVolume = iVolume(Symbol(), PERIOD_CURRENT, 1);
   long priorCompletedVolume   = iVolume(Symbol(), PERIOD_CURRENT, 2);
   if(currentCompletedVolume <= priorCompletedVolume) return;
   double close1 = iClose(Symbol(), PERIOD_CURRENT, 1);
   double close2 = iClose(Symbol(), PERIOD_CURRENT, 2);
   double close3 = iClose(Symbol(), PERIOD_CURRENT, 3);
   double dy_dt = (close1 - close3) / 2.0;
   double d2y_dt2 = (close1 - (2.0 * close2) + close3);
   double momentumScore = (dy_dt * 0.7) + (d2y_dt2 * 0.3);
   double instantAtrValue = iATR(Symbol(), PERIOD_CURRENT, InpAtrPeriod, 1);
   double pointsValue     = MarketInfo(Symbol(), MODE_POINT);
   double calculatedSlPoints = (instantAtrValue * InpMultiplierSL) / pointsValue;
   double calculatedTpPoints = (instantAtrValue * InpMultiplierTP) / pointsValue;
   calculatedSlPoints += currentSpread;
   double minStopLevelPoints = MarketInfo(Symbol(), MODE_STOPLEVEL);
   if(calculatedSlPoints < minStopLevelPoints) calculatedSlPoints = minStopLevelPoints + 10.0;
   if(calculatedTpPoints < minStopLevelPoints) calculatedTpPoints = minStopLevelPoints + 10.0;
   double finalLotSize = CalculateDynamicLotSize(calculatedSlPoints);
   if(AccountFreeMarginCheck(Symbol(), OP_BUY, finalLotSize) <= 0 || GetLastError() == 134)
   {
      Print("[SAFETY WARNING] Insufficient free margin calculated for Lot Size: ", finalLotSize, ". Aborting order.");
      return;
   }
   double dynamicThreshold = InpThresholdMultiplier * instantAtrValue;
   if(momentumScore > dynamicThreshold) ExecuteECNOrderSequence(OP_BUY, finalLotSize, calculatedSlPoints * pointsValue, calculatedTpPoints * pointsValue);
   else if(momentumScore < -dynamicThreshold) ExecuteECNOrderSequence(OP_SELL, finalLotSize, calculatedSlPoints * pointsValue, calculatedTpPoints * pointsValue);
}

void ExecuteECNOrderSequence(int orderType, double allocatedLots, double slDistanceValue, double tpDistanceValue)
{
   string orderLabel = (orderType == OP_BUY) ? "b26 Guarded Long" : "b26 Guarded Short";
   int ticket = -1;
   for(int attempt = 1; attempt <= InpMaxOrderRetries; attempt++)
   {
      double entryPrice = (orderType == OP_BUY) ? Ask : Bid;
      color orderColor = (orderType == OP_BUY) ? clrCyan : clrMagenta;
      ticket = OrderSend(Symbol(), orderType, allocatedLots, entryPrice, InpOrderSlippage, 0.0, 0.0, orderLabel, InpSystemMagic, 0, orderColor);
      if(ticket > 0) { Print("[SUCCESS] ECN Position established. Ticket: ", ticket); break; }
      else
      {
         int error = GetLastError();
         Print("[RETRY EXCEPTION] Entry failed. Attempt: ", attempt, " Code: ", error);
         if(error == 135 || error == 138) { RefreshRates(); continue; }
         break;
      }
   }
   if(ticket > 0 && OrderSelect(ticket, SELECT_BY_TICKET))
   {
      double emergencyBrokerSL = 0.0;
      if(OrderType() == OP_BUY)
      {
         glLocalStealthSL = NormalizeDouble(OrderOpenPrice() - slDistanceValue, Digits);
         glLocalStealthTP = NormalizeDouble(OrderOpenPrice() + tpDistanceValue, Digits);
         emergencyBrokerSL = NormalizeDouble(OrderOpenPrice() - (slDistanceValue * 1.5), Digits);
      }
      else if(OrderType() == OP_SELL)
      {
         glLocalStealthSL = NormalizeDouble(OrderOpenPrice() + slDistanceValue, Digits);
         glLocalStealthTP = NormalizeDouble(OrderOpenPrice() - tpDistanceValue, Digits);
         emergencyBrokerSL = NormalizeDouble(OrderOpenPrice() + (slDistanceValue * 1.5), Digits);
      }
      UpdateStealthGlobalVariable(ticket, glLocalStealthSL);
      glTrackingStateActive = true;
      bool modificationLocked = false;
      for(int modAttempt = 1; modAttempt <= InpMaxOrderRetries; modAttempt++)
      {
         if(OrderModify(ticket, OrderOpenPrice(), emergencyBrokerSL, 0.0, 0, clrRed))
         { Print("[SAFETY LOCKED] Hard emergency broker stop deployed to broker server at: ", emergencyBrokerSL); modificationLocked = true; break; }
         else { Print("[RETRY WARNING] Emergency broker stop failed to register. Attempt: ", modAttempt, " Error: ", GetLastError()); RefreshRates(); }
      }
      if(!modificationLocked)
      {
         Print("[CRITICAL FALLBACK] Hard SL failed to attach after ", InpMaxOrderRetries, " attempts. Evicting position immediately.");
         double closePrice = (OrderType() == OP_BUY) ? Bid : Ask;
         if(OrderClose(ticket, OrderLots(), closePrice, InpOrderSlippage * 2, clrOrange))
         {
            string gvName = "EA_STEALTH_SL_" + IntegerToString(ticket);
            if(GlobalVariableCheck(gvName)) GlobalVariableDel(gvName);
            glTrackingStateActive = false;
            Print("[EMERGENCY TERMINATION] Position liquidated cleanly due to structural modification failures.");
         }
      }
   }
}

void ManageActiveStealthTracking()
{
   if(!glTrackingStateActive) return;
   bool positionFound = false;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == InpSystemMagic)
         {
            positionFound = true;
            int ticket = OrderTicket();
            double currentBid = MarketInfo(Symbol(), MODE_BID);
            double currentAsk = MarketInfo(Symbol(), MODE_ASK);
            double instantPrice = (OrderType() == OP_BUY) ? currentBid : currentAsk;
            double atrCurrent = iATR(Symbol(), PERIOD_CURRENT, InpAtrPeriod, 1);
            if(OrderType() == OP_BUY)
            {
               if(instantPrice <= glLocalStealthSL || instantPrice >= glLocalStealthTP)
               {
                  if(OrderClose(ticket, OrderLots(), currentBid, InpOrderSlippage, clrYellow))
                  { string gvName = "EA_STEALTH_SL_" + IntegerToString(ticket); if(GlobalVariableCheck(gvName)) GlobalVariableDel(gvName); glTrackingStateActive = false; Print("[STEALTH LIQUIDATION] Long stealth criteria reached. Order cleanly exited."); }
                  return;
               }
               double trailActivationBoundary = OrderOpenPrice() + (atrCurrent * 1.0);
               if(instantPrice > trailActivationBoundary)
               {
                  double tentativeNewSL = NormalizeDouble(instantPrice - (atrCurrent * 0.5), Digits);
                  if(tentativeNewSL > glLocalStealthSL) { glLocalStealthSL = tentativeNewSL; UpdateStealthGlobalVariable(ticket, glLocalStealthSL); Print("[STEALTH TRAIL UPDATE] Hidden Long SL shifted and saved to disk: ", glLocalStealthSL); }
               }
            }
            else if(OrderType() == OP_SELL)
            {
               if(instantPrice >= glLocalStealthSL || instantPrice <= glLocalStealthTP)
               {
                  if(OrderClose(ticket, OrderLots(), currentAsk, InpOrderSlippage, clrYellow))
                  { string gvName = "EA_STEALTH_SL_" + IntegerToString(ticket); if(GlobalVariableCheck(gvName)) GlobalVariableDel(gvName); glTrackingStateActive = false; Print("[STEALTH LIQUIDATION] Short stealth criteria reached. Order cleanly exited."); }
                  return;
               }
               double trailActivationBoundary = OrderOpenPrice() - (atrCurrent * 1.0);
               if(instantPrice < trailActivationBoundary)
               {
                  double tentativeNewSL = NormalizeDouble(instantPrice + (atrCurrent * 0.5), Digits);
                  if(tentativeNewSL < glLocalStealthSL || glLocalStealthSL == 0.0) { glLocalStealthSL = tentativeNewSL; UpdateStealthGlobalVariable(ticket, glLocalStealthSL); Print("[STEALTH TRAIL UPDATE] Hidden Short SL shifted and saved to disk: ", glLocalStealthSL); }
               }
            }
            break;
         }
      }
   }
   if(!positionFound) glTrackingStateActive = false;
}

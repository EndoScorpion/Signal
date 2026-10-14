//+------------------------------------------------------------------+
//|                                         SafeChunkEA_MT4_b25.mq4  |
//|                                  Copyright 2026, AlgoArchitect   |
//| Gemini Canvas version pasted by Nasif 2026-10-11 14:06.          |
//| Only change: "#property property_strict" -> "#property strict".  |
//+------------------------------------------------------------------+
#property strict

// ---- User Input Parameters ----
input int      InpProcessingChunk   = 1000;    // Maximum calculation block depth
input int      InpAtrPeriod         = 14;      // Average True Range evaluation period
input double   InpMultiplierSL      = 1.5;     // ATR Stop-Loss multiplier factor
input double   InpMultiplierTP      = 3.0;     // ATR Take-Profit multiplier factor
input double   InpMaxSpreadPoints   = 35.0;    // Maximum spread threshold allowed for entries
input double   InpBaseLotSize       = 0.10;    // Standard transaction execution volume
input int      InpMaxOrderRetries   = 3;       // Number of order routing execution attempts
input int      InpOrderSlippage     = 3;       // Allowed transaction slip points
input int      InpSystemMagic       = 882026;  // Isolated strategy tracking signature

// ---- Session Filter Parameters ----
input int      InpStartHour         = 9;       // Daily execution window open hour
input int      InpStartMinute       = 0;       // Daily execution window open minute
input int      InpEndHour           = 16;      // Daily execution window close hour
input int      InpEndMinute         = 30;      // Daily execution window close minute

bool IsWithinTradingSession()
{
   if(TimeDayOfWeek(TimeCurrent()) == 0 || TimeDayOfWeek(TimeCurrent()) == 6) return(false);
   int currentMinutesStamp = (TimeHour(TimeCurrent()) * 60) + TimeMinute(TimeCurrent());
   int sessionStartBoundary = (InpStartHour * 60) + InpStartMinute;
   int sessionEndBoundary   = (InpEndHour * 60) + InpEndMinute;
   return(currentMinutesStamp >= sessionStartBoundary && currentMinutesStamp <= sessionEndBoundary);
}

int GetActiveStrategyPositionCount()
{
   int strategyTotal = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == InpSystemMagic) strategyTotal++;
      }
   }
   return(strategyTotal);
}

void ExecuteECNOrderSequence(int orderType, double slDistance, double tpDistance);

void OnTick()
{
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
   double calculatedSlDistance = instantAtrValue * InpMultiplierSL;
   double calculatedTpDistance = instantAtrValue * InpMultiplierTP;
   calculatedSlDistance += (currentSpread * pointsValue);
   double minStopLevel = MarketInfo(Symbol(), MODE_STOPLEVEL) * pointsValue;
   if(calculatedSlDistance < minStopLevel) calculatedSlDistance = minStopLevel + (10.0 * pointsValue);
   if(calculatedTpDistance < minStopLevel) calculatedTpDistance = minStopLevel + (10.0 * pointsValue);
   double executionThreshold = 5.0 * pointsValue;
   if(momentumScore > executionThreshold) ExecuteECNOrderSequence(OP_BUY, calculatedSlDistance, calculatedTpDistance);
   else if(momentumScore < -executionThreshold) ExecuteECNOrderSequence(OP_SELL, calculatedSlDistance, calculatedTpDistance);
}

void ExecuteECNOrderSequence(int orderType, double slDistance, double tpDistance)
{
   string orderLabel = (orderType == OP_BUY) ? "b25 Long" : "b25 Short";
   int ticket = -1;
   for(int attempt = 1; attempt <= InpMaxOrderRetries; attempt++)
   {
      double entryPrice = (orderType == OP_BUY) ? Ask : Bid;
      color  orderColor = (orderType == OP_BUY) ? clrCyan : clrMagenta;
      ticket = OrderSend(Symbol(), orderType, InpBaseLotSize, entryPrice, InpOrderSlippage, 0.0, 0.0, orderLabel, InpSystemMagic, 0, orderColor);
      if(ticket > 0) { Print("[SUCCESS] Position established. Ticket: ", ticket); break; }
      else
      {
         int error = GetLastError();
         Print("[RETRY ERROR] Order entry failed. Attempt: ", attempt, " Code: ", error);
         if(error == 135 || error == 138) { RefreshRates(); continue; }
         break;
      }
   }
   if(ticket > 0 && OrderSelect(ticket, SELECT_BY_TICKET))
   {
      double stopLossTarget = 0.0, takeProfitTarget = 0.0;
      if(OrderType() == OP_BUY) { stopLossTarget = NormalizeDouble(OrderOpenPrice() - slDistance, Digits); takeProfitTarget = NormalizeDouble(OrderOpenPrice() + tpDistance, Digits); }
      else if(OrderType() == OP_SELL) { stopLossTarget = NormalizeDouble(OrderOpenPrice() + slDistance, Digits); takeProfitTarget = NormalizeDouble(OrderOpenPrice() - tpDistance, Digits); }
      for(int modAttempt = 1; modAttempt <= InpMaxOrderRetries; modAttempt++)
      {
         if(OrderModify(ticket, OrderOpenPrice(), stopLossTarget, takeProfitTarget, 0, clrYellow)) { Print("[SUCCESS] Protection brackets successfully bound to Ticket: ", ticket); break; }
         else { Print("[RETRY ERROR] Bracket allocation failed. Error Code: ", GetLastError()); RefreshRates(); }
      }
   }
}

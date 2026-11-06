//objective: improve odds. 

// old 2011a 524 98.28%

//new config 

//2011a jan 1 to apr 27 215 98.60% 


//+------------------------------------------------------------------+
//|                                              Mar 3 2019 Test.mq4 |
//|                                               Copyright 2019, NH |
//|                                              https://www.nhi.com |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2019, Nasif Hossain" 
#property link      "https://www.nhi.com"
#property version   "1.01-claude_b4"
#property strict
// +------------------------------------------------------------------+
// Fixes applied (2026-11-05 audit):
//   FixG1: SL/TP in raw-entry OrderSend use p (pip-normalised), not Point
//           Ask-(290*Point) -> Ask-(290*p), Ask+(8*Point) -> Ask+(8*p)
//   FixG2: 2000*p TrailRemoveTP offset parameterised as InpNoTPOffset (default 2000)
//   FixG3: IsTradeAllowed() + IsConnected() guard added to OnTick
//   FixG4: Stale-quote guard added (TimeCurrent - Time[0] > 60s)
// +------------------------------------------------------------------+

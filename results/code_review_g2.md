# Code Review — g2a/g2d/g2e risk (Strong2010b_claude_g2a.mq4)
_Reviewer: signal-61 cloud session, 2026-10-12. Read-only. g2d/g2e not in repo (PC only); g2d/g2e analysis is inferred from g2a source + HUB_STATE._

---

## Issue 1 — Duplicate sell stop at Ladder1 == SellStopDist (HIGH)
**Lines:** 78 (`SellStopDist=20`), 237 (`Ladder1=20`), 1837-1838 (PlaceSellStop), 1802-1803 (PlaceLadder)
Each signal places PlaceSellStop (at Bid-20p) AND PlaceLadder leg 0 (also at Bid-20p). Two pending sell stops at identical price per signal. In tester, the second is rejected (duplicate price) → silent miss. In live, both may open → doubles the lot at that level without intent.
**Patch:** Change `Ladder1=20` to `Ladder1=30` (or 25) so PlaceSellStop and Ladder1 never share the same price.

## Issue 2 — No order-count guard; sell stack unbounded (HIGH)
**Lines:** 111 (`UseRiskGuard=0`), 113 (`MaxOpenOrders=8`), 1800-1804, 1837-1838
UseRiskGuard=0 disables Guard(). Per signal: 1 sell stop + 3 ladder legs = 4 pending sells. SellStopExpiryMin=120; if a second signal fires within 2 hours, 8 pending sells accumulate. Hedge adds 1 more per virtual buy. Explains why g2e (MaxOpenOrders=4) is queued.
**Patch for g2e:** Set `UseRiskGuard=1; MaxOpenOrders=4;`. This caps orders and makes Guard() active for all new placements. Do NOT set MaxOpenOrders=3 — the 3-ladder set alone hits that.

## Issue 3 — HedgeTrigger=30pts fires within 3 pips on every signal (MEDIUM)
**Lines:** 84 (`HedgeTrigger=30`), 1833-1834 (VirtualMng hedge), 1853-1855 (real-buy hedge)
On 5-digit EURUSD, 30pts = 3 pips. Normal spread + any adverse tick triggers the hedge almost every time. Effectively turns the hedge into a second market entry per signal. Each new virtual buy resets vHedged=0 (line 1831), so every signal can spawn a hedge even while prior hedges are open.
**Patch:** Raise `HedgeTrigger` to 80-120 (8-12 pips). This limits hedge to genuine adverse moves. Also set `UseHedgeHourBlock=1; HedgeBlockFrom=20; HedgeBlockTo=24;` to align with the g2a stop-hour policy.

## Issue 4 — g2d inference (no pending sells 00-04): no code risk, low impact
g2d adds `StopBlock2From=0; StopBlock2To=4;` (inferred). This extends StopHourBlocked() to also cover 00-04. No new order-stacking risk. However, 2021 OOS showed the 2019 hour block did not hold; adding a third block risks cutting more OOS trades.

## Issue 5 — g2a 2021 OOS failure root cause (not a code bug)
g2a filtered 12-16 and 20-24 exits because 2019 IS showed losses in those hours. In 2021 OOS: 328 trades, PF 0.87 (vs g1a 568 trades PF 1.05). The filter blocked OOS trades that would have been net positive in 2021's regime. 2019 hour-block benefit was IS-specific (runs z=-21 → dependent trades; day-block p=0.17-0.33 → not significant). This is overfitting, not a code defect. Gate verdict: g2a FAILS.

---
_Source: data/Strong2010b_claude_g2a.mq4. g2d/g2e reviewed by inference from g2a + HUB_STATE.md._

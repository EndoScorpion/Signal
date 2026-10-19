# Theory Queue Coordinator — Instructions for Cloud Fable Session
# Created 2026-10-18

## Your job
Poll `coordination/theory_queue.json` on the Signal relay branch for new entries.
For each entry with status="pending":
1. Reason through the theory (parameter change, logic hypothesis, filter idea)
2. Design a test: which .set file to base on, what to change, expected outcome
3. Write result to `coordination/theory_results.json` with status="designed" or "reject" + reasoning
4. Push both files back to relay branch

## Queue entry format
{
  "id": "theory_001",
  "status": "pending",
  "type": "adaptive_logic" | "filter" | "entry" | "exit",
  "description": "human-readable theory",
  "base_set": "b31_zrfb",   // optional
  "params": {}               // optional suggested params
}

## Result entry format
{
  "id": "theory_001",
  "status": "designed",      // or "reject"
  "verdict": "worth testing",
  "set_changes": {"UseAtrTrail": 1},
  "expected": "reduces losing trades by locking profits earlier",
  "risk": "may cut winners short on trending days",
  "new_convention_name": "MKT-FL-LO-b31+ZG+FB+AtrTrl",
  "reasoning": "..."
}

## Files
- Queue:   coordination/theory_queue.json
- Results: coordination/theory_results.json
- Name map: coordination/win_logic_naming.md (ref for naming)
- Repo: https://github.com/EndoScorpion/Signal branch: relay

## Current theories to seed (add these to queue as pending)
1. UseAtrTrail=1 on b31+ZG+FB — lock profits with ATR trailing stop
2. UseAdaptWpr=1 AdaptLosses=3 — shorten WPR period after 3 consecutive losses
3. UseLowRevBuy=1 LowRevBars=15 — catch swing-low reversals
4. SS-PT-ATR14-LO-E7+NG OOS validation plan — design 2019/2022 OOS test for C67 candidate

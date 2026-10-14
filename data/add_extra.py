import json
p = r"C:\Users\endos\Signal\data\extra_candidates.json"
cur = json.load(open(p))
P = {"_expert": "MR_RegimeSwitch_b51", "UseRegime": "true", "RegimePeriod": 2400, "SLPts": 600, "HoldBars": 48, "ZPeriod": 10, "ZTrigger": 2.5, "SideMode": 1}
def c(name, why, **kw):
    d = dict(P); d.update(kw); return {"name": name, "why": why, "patch": d}
new = [
 c("m5_sell_atr60", "b50 winner + ATR cap 60 pts (lab best filter)", AtrCapPts=60),
 c("m5_sell_calm", "b50 winner + calm tape: rvol<=29.6 and perm entropy<=0.945", CalmRvolMax=29.6, CalmPEMax=0.9452),
 c("m5_sell_calm_rvol", "b50 winner + block high realised vol (rvol<=45.6)", CalmRvolMax=45.6),
 c("m5_sell_mmr_low", "b50 winner, only when MMR <= 0.421 (low quintiles)", UseMmrGate="true", MmrMin=-1000, MmrMax=0.421),
 c("m5_sell_mmr_mid", "b50 winner, only when 0.421 < MMR <= 1.693", UseMmrGate="true", MmrMin=0.421, MmrMax=1.693),
 c("m5_sell_mmr_high", "b50 winner, only when MMR > 1.693", UseMmrGate="true", MmrMin=1.693, MmrMax=1000),
 c("m5_sell_blend15", "ZGate-style trigger: Z = 0.7 z(price) + 0.3 z(volume), 20 bars, fade at Z>=1.5", UseZBlend="true", ZPeriod=20, ZTrigger=1.5),
 c("m5_sell_blend20", "ZGate-style trigger, fade at Z>=2.0", UseZBlend="true", ZPeriod=20, ZTrigger=2.0),
 c("m5_both_blend15", "ZGate-style trigger both sides (sell below / buy above regime)", UseZBlend="true", ZPeriod=20, ZTrigger=1.5, SideMode=0),
 c("m5_sell_trail100", "b50 winner + trailing stop (start 100, 150 behind)", TrailStartPts=100, TrailDistPts=150),
 c("m5_sell_r4800", "b50 winner with ~200-day regime", RegimePeriod=4800),
 c("m5_sell_h96", "b50 winner holding 96 bars", HoldBars=96),
 c("m5_sell_sl300", "b50 winner with 300 pt stop", SLPts=300),
 c("m5_sell_sl1000", "b50 winner with 1000 pt stop", SLPts=1000),
 c("m5_sell_n20z2", "b50 winner, 20-bar z at 2.0", ZPeriod=20, ZTrigger=2.0),
 c("m5_sell_noregime", "control: b50 sell fade without regime", UseRegime="false"),
]
names = {x["name"] for x in cur}
json.dump([x for x in new if x["name"] not in names] + cur, open(p, "w"), indent=1)
print(len(new), "added; file now", len(json.load(open(p))), "entries")

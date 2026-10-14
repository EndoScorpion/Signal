"""yield_estimator.py - estimated gain on a stablecoin savings balance with a quoted APY (e.g. USDC at 7%/7.5%, Coinstancy-style, UNVERIFIED terms).
Usage: python -E -P yield_estimator.py [principal] [apy_pct] [days] [loss_prob_pct_per_year] [loss_severity_pct]
APY is the effective annual yield with continuous (per-second) accrual and auto-compounding, so growth over d days = (1+APY)^(d/365).
Also prints a risk-adjusted view: expected gain minus (annual loss probability x severity) prorated to the period. NOT investment advice; not a promise of returns.
Pre-tax, ignores network/on-off-ramp fees and any rate revision. Concepts (c) Nasif Hossain <EndoScorpion@gmail.com>."""
import sys
NOM = "--nominal" in sys.argv   # treat the rate as a NOMINAL yearly rate compounded per second (continuous) instead of an effective APY`nimport math`na = [x for x in sys.argv[1:] if x != "--nominal"]; g = lambda i, d: float(a[i]) if len(a) > i else d
import sys, math
NOM = "--nominal" in sys.argv   # treat rate as a NOMINAL yearly rate compounded per second (continuous) instead of an effective APY
a = [x for x in sys.argv[1:] if x != "--nominal"]; g = lambda i, d: float(a[i]) if len(a) > i else d
P, APY, D, LP, LS = g(0, 1000.0), g(1, 7.0) / 100, g(2, 30), g(3, 0.0) / 100, g(4, 100.0) / 100
if NOM: APY = math.exp(APY) - 1
def gain(p, apy, d): return p * ((1 + apy) ** (d / 365) - 1)
gr = gain(P, APY, D)
print(f"principal ${P:,.2f}  APY {APY*100:.2f}%  days {D:g}")
print(f"  gross gain  ${gr:,.2f}  ({100*gr/P:.3f}%)   end balance ${P+gr:,.2f}   simple-interest check ${P*APY*D/365:,.2f}")
exp_loss = P * LP * LS * D / 365
print(f"  risk view: {LP*100:.1f}%/yr chance of a {LS*100:.0f}% loss => expected loss over period ${exp_loss:,.2f}; expected net ${gr-exp_loss:,.2f}")
print("\nmonth (30d) table, by principal and APY (gross, pre-tax):")
apys = sorted({3.0, 5.0, 7.0, 7.5, round(APY * 100, 4)})
print("principal      " + "  ".join(f"{x:5.1f}%" for x in apys))
for p in (100, 500, 1000, 5000, 10000, 25000, 50000):
    print(f"${p:>9,}   " + "  ".join(f"{gain(p, x/100, 30):7.2f}" for x in apys))
print("\nbreak-even yearly loss probability for a total loss (100%) at this APY:", f"{100*((1+APY)-1)/(1+APY):.2f}% per year (above this, expected return is negative before opportunity cost)")





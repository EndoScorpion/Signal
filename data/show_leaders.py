import json
s = json.load(open(r"C:\Users\endos\Signal\data\loop_state.json")); b = s["base"]; ys = sorted(b)
print("year       " + " ".join(f"{y:>7}" for y in ys))
print("base       " + " ".join(f"{b[y]['profit']:7.0f}" for y in ys))
for n in ("u_regime_2400", "k_hurst_trend"):
    o = s["tested"][n]["oos"]
    print(f"{n[:10]:10} " + " ".join((f"{o[y]['profit']:7.0f}" if y in o else "      -") for y in ys))
    print("   trades " + " ".join((f"{o[y]['trades']:7d}" if y in o else "      -") for y in ys))
    print("   PF     " + " ".join((f"{o[y]['pf']:7.2f}" if y in o else "      -") for y in ys))
    print("   DD%    " + " ".join((f"{o[y]['dd']:7.1f}" if y in o else "      -") for y in ys))
print("years with base:", ys)

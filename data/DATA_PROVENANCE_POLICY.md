# Data Provenance & Validity Policy
**Effective: 17 Oct 2026 | Applies to: Signal + MQL repos | Owner: Nasif**

---

## PRIMARY DATA REQUIREMENT

All backtests, rule tests, and win-logic evaluations **MUST** be run on:

> **FXOpen ECN — EUR/USD — 5-digit (5 decimal place) data**

This is the only data source accepted for the main test queue.

- Tick size: 0.00001 (5th decimal)
- Broker: FXOpen ECN
- Instrument: EUR/USD
- Source: QuotesDownloader export from laptop (user-supplied)
- Expected path once copied: `data/fxopen_eurusd/` in each repo

---

## VERIFICATION STATUS OF EXISTING DATA

| Data | Source | FXOpen ECN? | Status |
|------|--------|-------------|--------|
| `Signal/data/history/*.csv` (SPY, QQQ, AAPL, etc.) | Yahoo Finance / Stooq (split-adjusted) | ❌ No | **FLAWED — reference only** |
| `Signal/data/crypto_h1/*.csv` (ADA, DOT, AVAX) | Unknown (0-volume rows, likely Hyperliquid/synthetic) | ❌ No | **FLAWED — reference only** |
| `MQL/data/HYPE_*.json` | Hyperliquid API (Binance candlesnap format) | ❌ No — crypto perp | **FLAWED — reference only** |
| `MQL/data/history_*_webull.csv` | Webull MCP (stocks: AAPL, AMZN, etc.) | ❌ No | **FLAWED — reference only** |
| `MQL/data/slc_win2_ext.json` / `slc_win2_hl.json` | Webull MCP (source field = "wb") | ❌ No | **FLAWED — reference only** |
| `MQL/data/wb/*.json` (raw Webull bars) | Webull (stocks/ETFs) | ❌ No | **FLAWED — reference only** |
| QuotesDownloader EUR/USD from laptop | FXOpen ECN (user-stated) | ✅ **Claimed yes** | **PENDING VERIFICATION** |

**No FXOpen EUR/USD data has been found in the cloud repos.**
The laptop copy has not been verified as present here yet.

---

## WHAT TO DO WITH OLD TEST RESULTS

| File | Classification |
|------|----------------|
| `all_backtest_results_*.json` | ⚠️ FLAWED — non-FXOpen data → **reference tier only** |
| `winners_retest_8pt_build048.md` | ⚠️ FLAWED — Webull/Yahoo data |
| `winlogic_totals_8pt_*.md` | ⚠️ FLAWED — Webull/Yahoo data |
| `baseline_8pt_commission_*.md` | ⚠️ FLAWED — Webull/Yahoo data |
| `HYPE_backtest_results_*.json` | ⚠️ FLAWED — Hyperliquid (crypto perp, not FXOpen) |

These files are **not deleted** — they may serve as:
- Cross-reference / sanity checks in later rounds
- Baseline for detecting data discrepancies
- Non-primary supplementary evidence only

They must **never** be cited as main-queue results without an explicit `[NON-FXOPEN DATA]` tag.

---

## RULES FOR ALL AGENTS / SUBAGENTS (MANDATORY)

```
DATA_SOURCE_RULE_v1:
1. Before ANY backtest: confirm data source = FXOpen ECN EUR/USD 5-decimal.
   - Check file header or metadata for broker/source tag.
   - If not confirmed → label result FLAWED, move to reference tier.
2. If FXOpen data is not present in data/fxopen_eurusd/:
   - STOP the backtest.
   - Report: "FXOpen EUR/USD data not found. Awaiting user upload."
   - Do NOT fall back to Yahoo/Webull/Hyperliquid for main queue.
3. Spread model: use FXOpen ECN typical EUR/USD spread (0.1–0.3 pip raw,
   add 0.5 pip conservative buffer) — do NOT use generic/synthetic spreads.
4. Price format: 5 decimal places required (e.g. 1.09842). 4-decimal data
   is a different feed — flag and reject for main queue.
5. Existing test files: any result file without "fxopen" in its source
   metadata is automatically FLAWED for main-queue purposes.
6. Matching check: even if prices happen to match another source,
   non-FXOpen data cannot be used alone in the main queue.
   It may be retained as reference only.
```

---

## HOW TO VERIFY THE LAPTOP DATA

When user copies QuotesDownloader data:
1. Check first price row — should be 5 decimal EUR/USD (e.g. 1.08423)
2. Check spread column if present — ECN spreads typically 0–3 pips raw
3. Check broker tag in file header (QuotesDownloader embeds source broker)
4. Cross-check 3 random timestamps against a known FXOpen price source
5. If all pass → tag file with `# SOURCE: FXOpen ECN EUR/USD 5-digit VERIFIED`

---

## PENDING ACTION

> **User: please copy the QuotesDownloader EUR/USD FXOpen data to:**
> `data/fxopen_eurusd/` in the MQL repo (and optionally Signal repo)
> 
> Once present, this session will verify the format and begin the first
> FXOpen-native backtest run.


# RESUME.md - Nasif's MT4 / EURUSD / Claude agent system (backup 2026-10-12)

Purpose: rebuild everything if the laptop or this USB stick is lost. NO passwords or tokens are in this backup.
Re-create logins by hand: claude.ai (endoscorpion@gmail.com), FXOpen/SoftFX QuoteStore login (get from FXOpen account), MT4 broker login.

## 1. What is in this backup
- MQL4\Experts|Include|Scripts|Indicators : EA source (Strong2010b family, claude_* variants b7..b31, g-series). Copy back to <MT4 data folder>\MQL4 and compile in MetaEditor.
- claude\memory : Claude auto-memory notes (RAM limits, master hub, "NEED YOU" marker, Sonnet-only cap). claude\skills, claude\settings.json.
- ClaudeHub, ClaudeLauncher : master controller (hub.ps1, start_master.ps1/bat, launch_sequence.ps1, CLAUDE.md).
- Signal\scripts, Signal\data, results, analysis : job watcher (ps_watcher), job_*.ps1 pipeline, EA results (g5_summary, commission_repricing.md, chopbracket, adx sweeps).
- MT4_Backtest : run_queue.ps1, watch_queue.ps1, queue.txt, done.csv, HUB_STATE.md, master_resume files, reports (.htm).
- hst_out : run_tester.ps1, run_b23.ps1, run_tester_visual.ps1, logs, small reports. (Big .hst/.fxt files NOT included.)

## 2. Hard rules learned (do not forget)
- PC has 5.8 GB usable RAM. Each Claude CLI costs ~0.5 GB. Gates: MT4 needs >=1.0 GB free; new CLI clone needs >=1.5 GB.
- Start Claude CLIs NON-ADMIN in Windows Terminal. Admin windows can't be pasted into, can't be seen by ListAgents, and can't message other sessions. Shift+Insert paste is broken on that PC.
- Scoring commission = 8 pts/trade (set 2026-10-11). Older 6-pt runs are not comparable (e.g. g4b PASS PF 1.46 was at 6).
- MT4 must run MINIMIZED, NO ACTIVATION (ShowWindow=7 via Win32_Process.Create), TestVisualEnable=false, TestShutdownTerminal=true. Turn off Tools>Options>Events sounds by hand.
- MT4_Backtest\PAUSE file = global pause. run_queue.ps1, run_tester.ps1, run_b23.ps1 and the Signal watcher refuse to start MT4 while it exists. Delete the file to resume.
- QuotesDownloader (SoftFX) leaks memory (1 -> 2.3 GB). Run in short chunks (~3 months), non-parallel with MT4. Watchdog: Signal\scripts\qd_watchdog.ps1 kills it >1200 MB or free RAM <400 MB.
- Data: EURUSD M1 bars from 2010-06-23 (FXOpen ECN, 5-digit). Partial tick CSV 2020-08-10..2021-08-18 (last line truncated; drop it).

## 3. Resume the Claude agents (in this order)
1. Install Claude Code CLI and Claude desktop app; sign in as endoscorpion@gmail.com. Phone: Claude Android app > Code tab shows sessions with Remote Control on.
2. Restore folders from this backup to the same paths (C:\Users\endos\ClaudeHub, ...\Signal, ...\MT4_Backtest, ...\Desktop\hst_out) and EA files into the MT4 MQL4 folder.
3. Master CLI (non-admin, Windows Terminal): run C:\Users\endos\ClaudeHub\start_master.bat (or MT4_Backtest\master_resume.cmd). If the old transcript exists: `claude --resume f7efebdd-8d88-4823-86eb-cefeb3cd5d0c` from C:\Users\endos. Otherwise start fresh and tell it: "Read C:\Users\endos\ClaudeHub\CLAUDE.md and MT4_Backtest\HUB_STATE.md".
4. Signal CLI (remote-controlled): `claude --remote-control Signal` from C:\Users\endos\Signal (launcher: ClaudeLauncher\claude_signal_v4_12Oct2026.ps1).
5. Job watcher (headless, non-admin): `powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\endos\Signal\scripts\ps_watcher_v1_12Oct2026.ps1`. It runs any .ps1 dropped in Signal\inbox and writes output to Signal\outbox. Delete MT4_Backtest\PAUSE only when RAM is healthy.
6. Link to phone: new sessions auto-connect to Remote Control (app setting "Connect new sessions to Remote Control"). In a plain CLI use /remote-control. If the QR looks inverted (black theme), use /theme light or open the Code tab in the app instead.

## 4. Clone / agent architecture
- Master hub CLI owns the MT4 queue and spawns clone CLIs (hub.ps1 does the launching with RAM gates). Clones are normal `claude` CLIs in their own folders; they report via files (HUB_STATE.md, Signal\outbox) and SendMessage.
- Slave/headless: the PowerShell inbox watcher (above) is the headless autonomous worker: Claude writes job_*.ps1 into Signal\inbox, the watcher runs it, results land in outbox. A Node.js equivalent would just poll that folder; same contract.
- Cloud sessions are one-way: SendMessage or the Signal repo git bridge (branch claude/mql4-analysis-comments-bd4kz3: data/ out, results/ in).
- Self-improvement loop (EA): generate EA variant (b-series/g-series) -> add to queue.txt (EA|Period|From|To|Spread[|Deposit]) -> run_queue.ps1 runs ONE job under a lock + RAM gate -> done.csv + reports -> summarize (g*_summary.txt) -> OOS gate (run_oos_gate_v3: PASS/FAIL by PF, commission 8) -> keep winners, mutate parameters (ADX sweeps, chop/bracket, regime/session filters) -> repeat. Always rescore at 8-pt commission. Never run two backtests at once.

## 5. EA win logic (EURUSD, FXOpen ECN, 5-digit)
- Symbol EURUSD, 5-digit quotes: 1 pip = 10 points. Spread/commission in the queue are in points; "8 pts/trade" = 0.8 pip.
- Strong2010b_claude_* : trend/regime EA family with session and chop filters. See MQL4\Experts source and Signal\data\*summary*.txt for per-variant results; commission_repricing.md explains rescoring.
- Judge a variant by out-of-sample years, profit factor at 8 pts, drawdown, and trade count. A single good year is not a pass.

## 6. Non-forex logic
- The user asked for non-forex "win logic" to be backed up too. No separate non-forex strategy files were found in the folders scanned (only Game folder "Sid Meier's Pirates" session, unrelated). Put any such notes in a folder named NONFOREX\ here when available.

## 7. Offline math AI (for later)
Goal: an offline "math server / math LLM" for formulas and indicator math.
- Easiest start: Ollama is already installed on this PC (Ollama.lnk in Startup). Pull a small local model that fits 5.8 GB RAM (e.g. a 1-4B model; larger models will thrash). Use it for formula drafting only, and verify numerically.
- Deterministic math (preferred over an LLM): Python + numpy, pandas, scipy, sympy (symbolic), TA-Lib or pandas-ta (indicators), nolds (Hurst, Lyapunov, fractal dimension), statsmodels. An LLM writes the code, the library computes the answer.
- Reference formulas to implement/test:
  * Williams %R(n) = -100 * (HighestHigh(n) - Close) / (HighestHigh(n) - LowestLow(n)); range -100..0; overbought > -20, oversold < -80.
  * Bill Williams Fractal: up fractal = a bar whose High is higher than the 2 bars before and 2 after; down fractal = Low lower than 2 before and 2 after. Signals confirm 2 bars late (no repaint after confirmation).
  * Alligator: median price (H+L)/2; Jaws = SMMA(13) shifted +8; Teeth = SMMA(8) shifted +5; Lips = SMMA(5) shifted +3. Lines intertwined = sleeping/ranging; fanned out = trending.
  * Chaos / complex systems: Hurst exponent H (0.5 random, >0.5 trending, <0.5 mean-reverting); fractal dimension D = 2 - H; largest Lyapunov exponent > 0 suggests chaos; use as regime filters (trade trend EA only when H > ~0.55 / Alligator awake).
  * Self-improvement: walk-forward optimisation, rescoring at fixed commission, out-of-sample gate, and parameter-stability checks (a good optimum should have good neighbours).
- Keep all of this OFFLINE-friendly: save results as CSV/TXT, and let the EA read only precomputed regime flags if MQL4 can't run the heavy math.

## 7b. Honest limits
Backtests are not guarantees. Markets change; keep position sizing small and always verify on unseen data.

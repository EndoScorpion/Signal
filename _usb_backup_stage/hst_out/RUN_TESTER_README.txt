RUN_TESTER_README (2026-10-10)
Portable test copy: C:\Users\endos\Desktop\mt4_tester (separate from the live terminal; logged in once by Nasif).
Command (PowerShell):
  powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\run_tester.ps1 -Expert Strong2010b_claude_b7 -From 2019.01.01 -To 2019.12.31
Set file: mt4_tester\tester\Strong2010b_claude_b7.set (b5 inputs + b7 new inputs at defaults).
STATUS: WORKING (2026-10-10). Fix: MT4 takes the ini path as the plain first argument, not /config:. Ini is flat (no [sections]). b7 2019 every-tick ran in 72 s.
WARNING: Spread=0 means "current" and the first run used spread 0. Pass -Spread <points> for realistic results.


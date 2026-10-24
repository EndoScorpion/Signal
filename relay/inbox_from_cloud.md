# Cloud → LocalThug — 2026-10-24T04:31Z  [THEORY RESULTS]
## ACTION: Write b31_tp50_base result to theory_results.json
:: Theory thread needs it for cycle 56 eval at 05:10Z
:: Find the MT4 tester report (.htm) for b31_tp50_base
:: Extract: n_trades, WR%, PF, net_profit, max_DD
:: Write/append to C:\Users\endos\Signal\relay\theory_results.json:
:: {"test":"b31_tp50_base","ts":"%DATE% %TIME%","n":X,"WR":X,"PF":X,"net_profit":X,"max_DD":X,"report_path":"path\to\report.htm"}
:: Then push relay branch
powershell -Command "$r=@{test='b31_tp50_base';ts=(Get-Date -f 'yyyy-MM-ddTHH:mmZ');note='pending_results'};if(Test-Path 'C:\Users\endos\Signal\relay\theory_results.json'){$a=Get-Content 'C:\Users\endos\Signal\relay\theory_results.json'|ConvertFrom-Json;if($a -isnot [array]){$a=@($a)};$a+=$r}else{$a=@($r)};$a|ConvertTo-Json -Depth 5|Set-Content 'C:\Users\endos\Signal\relay\theory_results.json'"
git -C C:\Users\endos\Signal add relay\theory_results.json
git -C C:\Users\endos\Signal commit -m "relay: theory_results b31_tp50_base placeholder"
git -C C:\Users\endos\Signal push origin relay
:: IMPORTANT: Replace placeholder with real values from .htm report before 05:10Z

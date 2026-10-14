$py = 'C:\Users\endos\AppData\Local\Programs\Python\Python312\python.exe'
$d = 'C:\Users\endos\Signal\agent_readonly'
$h = 'C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server\EURUSD1.hst'
$p = Start-Process $py -ArgumentList '-I', "$d\gap_audit.py", "`"$h`"", "$d\gap_audit_result.txt" -PassThru -WindowStyle Hidden -RedirectStandardOutput "$d\gap_stdout.txt" -RedirectStandardError "$d\gap_stderr.txt"
$p.PriorityClass = 'Idle'
"started pid " + $p.Id

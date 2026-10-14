$py = 'C:\Users\endos\AppData\Local\Programs\Python\Python312\python.exe'
$d = 'C:\Users\endos\Signal\agent_readonly'
$h = 'C:\Users\endos\Desktop\mt4_tester2\history\FXOpenEU-ECN Live Server\EURUSD1.hst'
$p = Start-Process $py -ArgumentList '-I', "$d\gap_audit.py", "`"$h`"", "$d\gap_audit_tester2_result.txt" -PassThru -WindowStyle Hidden -RedirectStandardOutput "$d\gap2_stdout.txt" -RedirectStandardError "$d\gap2_stderr.txt"
$p.PriorityClass = 'Idle'
"started pid " + $p.Id

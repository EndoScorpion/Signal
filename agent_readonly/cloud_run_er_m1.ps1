$py = 'C:\Users\endos\AppData\Local\Programs\Python\Python312\python.exe'
$d = 'C:\Users\endos\Signal\agent_readonly'
$h = 'C:\Users\endos\Desktop\mt4_tester\history\FXOpenEU-ECN Live Server\EURUSD1.hst'
$p = Start-Process $py -ArgumentList '-I', "$d\er_m1.py", "`"$h`"", "$d\er_m1_result.txt" -PassThru -WindowStyle Hidden -RedirectStandardOutput "$d\er_m1_stdout.txt" -RedirectStandardError "$d\er_m1_stderr.txt"
$p.PriorityClass = 'Idle'
"started pid " + $p.Id

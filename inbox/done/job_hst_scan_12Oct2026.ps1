Get-ChildItem "$env:APPDATA\MetaQuotes\Terminal","C:\Users\endos\MT4_Backtest" -Recurse -Filter "EURUSD*.hst" -ErrorAction SilentlyContinue | Select FullName,Length,LastWriteTime | Format-Table -Auto | Out-String -Width 250
"Free RAM KB: " + (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory

$src="C:\Users\endos\AppData\Roaming\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\history\FXOpenEU-ECN Live Server\EURUSD60.hst"
Copy-Item $src "C:\Users\endos\Signal\data\EURUSD60_copy_12Oct2026.hst" -Force
"copied " + (Get-Item "C:\Users\endos\Signal\data\EURUSD60_copy_12Oct2026.hst").Length

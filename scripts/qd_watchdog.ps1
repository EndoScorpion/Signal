# Kills QuotesDownloader if it exceeds 1200 MB or free RAM < 400 MB. Writes ticks.csv.bak is NOT touched.
while ($true) {
  $free=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024
  Get-Process QuotesDownloader -EA 0 | % {
    $mb=$_.WS/1MB
    if ($mb -gt 1200 -or $free -lt 400) {
      Stop-Process -Id $_.Id -Force
      "$(Get-Date -f s) KILLED QuotesDownloader at $([int]$mb) MB, free $([int]$free) MB" | Add-Content C:\Users\endos\Signal\outbox\qd_watchdog.log
    }
  }
  Start-Sleep 5
}

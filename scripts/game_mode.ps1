# game_mode.ps1 - suspends background tasks, trims RAM, boosts Stellaris
# Usage: game_mode.ps1 -On   (before game)
#        game_mode.ps1 -Off  (after game)
param([switch]$On, [switch]$Off)

$suspendTasks = @('BoardWatcher','CliRelayPoll','CloudCmdPoller','CloudCmdPollerGH',
                  'Cloud_DC_Watchdog','Cloud_SpaceSaver','Cloud_TrimRamHogs','DcWatchdog',
                  'EA Daily Summary','LocalThug_PopupBlock','LocalThug_RamTrim',
                  'RamCheck','SignalAutoBackup','SignalAutoSync','SLC_KeepAwake',
                  'SLC_TrimWatch','WatchdogPollers','DcCloneServer','ClaudeRendererWatchdog')

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Diagnostics;
public class ProcUtil {
  [DllImport("kernel32.dll")] static extern IntPtr OpenProcess(uint a,bool b,int p);
  [DllImport("kernel32.dll")] static extern bool SetProcessWorkingSetSize(IntPtr h,UIntPtr mn,UIntPtr mx);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h);
  [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);
  public static void Trim(int pid){var h=OpenProcess(0x1F0FFF,false,pid);if(h!=IntPtr.Zero){SetProcessWorkingSetSize(h,UIntPtr.Zero-1,UIntPtr.Zero-1);CloseHandle(h);}}
  public static void Suspend(int pid){var h=OpenProcess(0x1F0FFF,false,pid);if(h!=IntPtr.Zero){NtSuspendProcess(h);CloseHandle(h);}}
  public static void Resume(int pid){var h=OpenProcess(0x1F0FFF,false,pid);if(h!=IntPtr.Zero){NtResumeProcess(h);CloseHandle(h);}}
}
'@

if ($On) {
    Write-Host "=== GAME MODE ON ==="
    # Stop background scheduled tasks
    foreach ($t in $suspendTasks) {
        Stop-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue
    }
    # Stop background PS processes (non-current, non-Claude-session)
    Get-Process powershell,pwsh -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $PID } | ForEach-Object {
        $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmd -notmatch 'hub|claude_code|game_mode') { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
    }
    # Trim all non-Stellaris processes
    Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne 'stellaris' } | ForEach-Object {
        try { [ProcUtil]::Trim($_.Id) } catch {}
    }
    # Purge standby list
    $b = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(4)
    [System.Runtime.InteropServices.Marshal]::WriteInt32($b, 0, 80)
    Add-Type -MemberDefinition '[DllImport("ntdll.dll")] public static extern uint NtSetSystemInformation(int c,IntPtr b,int s);' -Name NTM -Namespace NTM -ErrorAction SilentlyContinue
    try { [NTM.NTM]::NtSetSystemInformation(3, $b, 4) } catch {}
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($b)
    [GC]::Collect()
    # Boost Stellaris to high priority, fullscreen-friendly
    Get-Process stellaris -ErrorAction SilentlyContinue | ForEach-Object {
        $_.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
    }
    $os = Get-CimInstance Win32_OperatingSystem
    Write-Host "RAM free: $([math]::Round($os.FreePhysicalMemory/1MB,2))GB - Stellaris priority: High"
}

if ($Off) {
    Write-Host "=== GAME MODE OFF ==="
    # Restart background tasks
    foreach ($t in $suspendTasks) {
        Start-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue
    }
    # Restore Claude priority
    Get-Process claude -ErrorAction SilentlyContinue | ForEach-Object {
        $_.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::Normal
    }
    Write-Host "Background tasks restarted, priorities restored"
}

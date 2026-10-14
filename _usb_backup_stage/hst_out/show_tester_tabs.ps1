# show_tester_tabs.ps1 - watcher: when the TEST copy (Desktop\mt4_tester) terminal runs a test, bring it to the front
# and click its tester panel's Graph tab (live balance/equity line). MT4 tabs are custom-drawn (no SysTabControl32),
# so this moves the mouse and clicks the tab (real click) at the tab's position near the bottom-left of the Tester panel. Never touches the live terminal.
#   powershell -ExecutionPolicy Bypass -File C:\Users\endos\Desktop\hst_out\show_tester_tabs.ps1 [-TabX 148]
param([int]$TabX=170,[int]$FromBottom=34)
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class TT { public delegate bool P(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, P f, IntPtr l);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, int m, IntPtr w, IntPtr l);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
 [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
 public static bool RealClick(IntPtr top,int x,int fromBottom){ RECT r; if(!GetWindowRect(top,out r)) return false; SetCursorPos(r.L+x, r.B-fromBottom); mouse_event(2,0,0,0,0); mouse_event(4,0,0,0,0); return true; }
 public static IntPtr Tester(IntPtr top){ IntPtr f=IntPtr.Zero; EnumChildWindows(top,(h,l)=>{ var c=new StringBuilder(64); GetClassName(h,c,64); var t=new StringBuilder(64); GetWindowText(h,t,64); if(c.ToString().StartsWith("Afx:") && t.ToString()=="Tester"){ f=h; return false; } return true; },IntPtr.Zero); return f; }
 public static bool Click(IntPtr h,int x,int fromBottom){ RECT r; if(!GetClientRect(h,out r)) return false; int y=r.B-fromBottom; IntPtr lp=(IntPtr)((y<<16)|(x&0xFFFF)); PostMessage(h,0x201,(IntPtr)1,lp); PostMessage(h,0x202,IntPtr.Zero,lp); return true; } }
"@
$P='C:\Users\endos\Desktop\mt4_tester'; $seen=0
while($true){
  $pr = Get-Process terminal -EA 0 | ? { $_.Path -like "$P*" -and $_.MainWindowHandle -ne 0 } | select -First 1
  if($pr -and $pr.Id -ne $seen){ Start-Sleep 3; $seen=$pr.Id; [TT]::ShowWindow($pr.MainWindowHandle,9) | Out-Null; [TT]::SetForegroundWindow($pr.MainWindowHandle) | Out-Null
    Start-Sleep 1; $ok=[TT]::RealClick($pr.MainWindowHandle,$TabX,$FromBottom); "$(Get-Date -f HH:mm:ss) test pid $($pr.Id): Graph click sent=$ok" }
  Start-Sleep 2
}


@echo off
echo ===== PC-ANDROID BRIDGE SETUP =====
echo Run as Administrator

echo [1/5] Checking ADB...
where adb >nul 2>nul
if %errorlevel%==0 (
    echo ADB found in PATH.
) else (
    echo ADB not in PATH. Checking common locations...
    if exist "C:\platform-tools\adb.exe" (
        echo Found at C:\platform-tools
        set "PATH=%PATH%;C:\platform-tools"
    ) else if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" (
        echo Found in Android SDK
        set "PATH=%PATH%;%LOCALAPPDATA%\Android\Sdk\platform-tools"
    ) else (
        echo ADB not found. Download platform-tools from:
        echo https://developer.android.com/tools/releases/platform-tools
        echo Extract to C:\platform-tools and re-run.
        goto :adb_skip
    )
)

echo.
echo [2/5] Connected ADB devices:
adb devices

echo.
echo [3/5] Enabling WiFi ADB on connected device (port 5555)...
adb tcpip 5555
echo Done. Now disconnect USB and connect via: adb connect DEVICE_IP:5555

:adb_skip
echo.
echo [4/5] Starting Python blackboard server on port 8080...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Trying py...
    py --version >nul 2>nul
    if %errorlevel% neq 0 (
        echo Python not available. Skipping blackboard server.
        goto :py_skip
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo Writing blackboard_server.py to C:\Signal\...
if not exist "C:\Signal" mkdir "C:\Signal"
(
echo import http.server, json, os, datetime
echo BOARD_FILE = r'C:\Signal\blackboard.json'
echo if not os.path.exists^(BOARD_FILE^): open^(BOARD_FILE,'w'^).write^('[]'^)
echo class H^(http.server.BaseHTTPRequestHandler^):
echo     def do_GET^(self^):
echo         data = open^(BOARD_FILE^).read^(^)
echo         self.send_response^(200^); self.send_header^('Content-Type','application/json'^); self.send_header^('Access-Control-Allow-Origin','*'^); self.end_headers^(^)
echo         self.wfile.write^(data.encode^(^)^)
echo     def do_POST^(self^):
echo         n = int^(self.headers.get^('Content-Length',0^)^)
echo         body = self.rfile.read^(n^).decode^(^)
echo         msgs = json.loads^(open^(BOARD_FILE^).read^(^)^)
echo         msgs.insert^(0,{'ts':datetime.datetime.utcnow^(^).isoformat^(^)+'Z','body':body}^)
echo         open^(BOARD_FILE,'w'^).write^(json.dumps^(msgs[:50],indent=2^)^)
echo         self.send_response^(200^); self.end_headers^(^); self.wfile.write^(b'OK'^)
echo     def do_OPTIONS^(self^):
echo         self.send_response^(200^); self.send_header^('Access-Control-Allow-Origin','*'^); self.send_header^('Access-Control-Allow-Methods','GET,POST'^); self.end_headers^(^)
echo     def log_message^(self,*a^): pass
echo http.server.HTTPServer^(^('',8080^),H^).serve_forever^(^)
) > "C:\Signal\blackboard_server.py"

start "BlackboardServer" /min cmd /c "%PYTHON% C:\Signal\blackboard_server.py"
echo Blackboard server running on port 8080.
echo Read: http://10.30.30.80:8080
echo Post: curl -X POST http://10.30.30.80:8080 -d "your message"

:py_skip
echo.
echo [5/5] Checking for cloudflared (for public tunnel)...
where cloudflared >nul 2>nul
if %errorlevel%==0 (
    echo cloudflared found. Starting tunnel on port 8080...
    start "CloudflareTunnel" /min cmd /c "cloudflared tunnel --url http://localhost:8080"
    echo Tunnel starting... check the CloudflareTunnel window for the public URL.
) else (
    echo cloudflared not found. For public access from outside LAN:
    echo Download: https://github.com/cloudflare/cloudflared/releases/latest
    echo Run: cloudflared tunnel --url http://localhost:8080
    echo.
    echo On LAN (same WiFi): phone can use http://10.30.30.80:8080 directly.
)

echo.
echo ===== BRIDGE SETUP COMPLETE =====
echo Blackboard: http://10.30.30.80:8080 (LAN only)
echo ADB WiFi: adb connect PHONE_IP:5555
echo.
pause

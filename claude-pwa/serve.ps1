# Claude Local PWA - Local Server
# Run this script to serve the PWA locally at http://localhost:3000
# Then open Chrome and navigate to http://localhost:3000 to install as PWA

param([int]$Port = 3000)

$webRoot = $PSScriptRoot
Write-Host "Claude Local PWA server starting on http://localhost:$Port" -ForegroundColor Cyan
Write-Host "Open Chrome → navigate to http://localhost:$Port → click install icon in address bar`n" -ForegroundColor Green

Add-Type -AssemblyName System.Net.Http

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()

$mimeTypes = @{
  '.html' = 'text/html; charset=utf-8'
  '.js'   = 'application/javascript'
  '.css'  = 'text/css'
  '.json' = 'application/json'
  '.png'  = 'image/png'
  '.ico'  = 'image/x-icon'
  '.svg'  = 'image/svg+xml'
}

Write-Host "Listening… Press Ctrl+C to stop`n" -ForegroundColor Gray

while ($listener.IsListening) {
  try {
    $ctx   = $listener.GetContext()
    $req   = $ctx.Request
    $resp  = $ctx.Response

    $urlPath = $req.Url.AbsolutePath
    if ($urlPath -eq '/') { $urlPath = '/index.html' }

    $filePath = Join-Path $webRoot $urlPath.TrimStart('/')

    if (Test-Path $filePath -PathType Leaf) {
      $ext  = [System.IO.Path]::GetExtension($filePath)
      $mime = if ($mimeTypes[$ext]) { $mimeTypes[$ext] } else { 'application/octet-stream' }
      $bytes = [System.IO.File]::ReadAllBytes($filePath)
      $resp.ContentType   = $mime
      $resp.ContentLength64 = $bytes.Length
      $resp.Headers.Add('Cache-Control', 'no-cache')
      $resp.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host "200  $urlPath" -ForegroundColor DarkGray
    } else {
      $resp.StatusCode = 404
      $bytes = [System.Text.Encoding]::UTF8.GetBytes("Not found: $urlPath")
      $resp.OutputStream.Write($bytes, 0, $bytes.Length)
      Write-Host "404  $urlPath" -ForegroundColor DarkRed
    }
    $resp.OutputStream.Close()
  } catch {
    if ($_.Exception.Message -notmatch 'thread') {
      Write-Host "Error: $_" -ForegroundColor Red
    }
  }
}

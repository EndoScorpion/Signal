<#
  ClaudeHub - one controller for Claude CLI sessions and their node MCP helpers.

  Usage (PowerShell):
    .\hub.ps1 status                         # RAM + every claude/node process, grouped by owner
    .\hub.ps1 add "prompt text" -Dir <path> [-Tools "Read,Grep,Glob"] [-Name label]
    .\hub.ps1 list                           # tasks in pending / running / done / failed
    .\hub.ps1 run-once                       # run the oldest pending task IF RAM allows
    .\hub.ps1 watch [-Every 60]              # loop: snapshot status + run-once
    .\hub.ps1 stop -Id <pid> -Force          # kill a process tree (requires -Force; never the master)
    .\hub.ps1 spawn "prompt" -Name <label>   # start a background clone (claude --bg) IF RAM allows
    .\hub.ps1 agents                         # list background clones (claude agents)

  Cloud / non-CLI sessions (git bridge, repo C:\Users\endos\Signal):
    .\hub.ps1 post "task text" -To <session> # write data/tasks/<id>.md, commit, push
    .\hub.ps1 sync                           # pull, write data/HUB_LIVE.md, commit+push bridge paths only
    .\hub.ps1 results                        # list results/ files cloud sessions pushed back

  Safety: one hub task/clone at a time, only when free RAM >= -MinFreeMB.
  Clones run on -Model (Sonnet 5.5) with read-only tools unless -Tools widens them.
  The master (this script's ancestor claude.exe) is never stopped. MT4 stays with run_queue.ps1.
#>
param(
  [Parameter(Position=0)][ValidateSet('status','add','list','run-once','watch','stop','spawn','agents','post','sync','results')][string]$Cmd = 'status',
  [Parameter(Position=1)][string]$Prompt,
  [string]$Dir = "$env:APPDATA\MetaQuotes\Terminal\6278E353D77D4E501C6775ACEC85F415\MQL4",
  [string]$Tools = 'Read,Grep,Glob',
  [string]$Name = 'task',
  [int]$MinFreeMB = 1500,
  [int]$Every = 60,
  [int]$Id,
  [string]$Model = 'claude-sonnet-5-5',
  [string]$To = 'any',
  [string]$Repo = 'C:\Users\endos\Signal',
  [string]$Branch = 'claude/mql4-analysis-comments-bd4kz3',
  [int]$SyncEvery = 300,
  [switch]$Force
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Q = @{}; foreach ($s in 'pending','running','done','failed') { $Q[$s] = Join-Path $Root "queue\$s"; New-Item -ItemType Directory -Force $Q[$s] | Out-Null }
$Logs = Join-Path $Root 'logs'; New-Item -ItemType Directory -Force $Logs | Out-Null
$Lock = Join-Path $Root 'worker.lock'

function Get-FreeMB { [int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1KB) }

function Get-Inventory {
  $all = @{}; Get-CimInstance Win32_Process | ForEach-Object { $all[[int]$_.ProcessId] = $_ }
  $owner = {
    param($p)
    $x = $p; for ($i = 0; $i -lt 6 -and $x; $i++) {
      $x = $all[[int]$x.ParentProcessId]
      if ($x -and $x.Name -eq 'claude.exe') { return $x.ProcessId }
    }; return $null
  }
  $all.Values | Where-Object { $_.Name -in 'claude.exe','node.exe' } | ForEach-Object {
    $c = "$($_.CommandLine)"
    $kind = if ($_.Name -eq 'node.exe') {
              if ($c -match 'server-pdf') {'mcp:pdf'} elseif ($c -match 'desktop-commander') {'mcp:desktop-commander'} else {'node:other'}
            } elseif ($c -match '\.local\\bin\\claude\.exe') {'cli:terminal'}
              elseif ($c -match 'stream-json') {'cli:desktop-session'}
              elseif ($c -match '--type=') {'desktop:electron'} else {'desktop:main'}
    [pscustomobject]@{
      PID = $_.ProcessId; Kind = $kind; MB = [int]($_.WorkingSetSize / 1MB)
      Owner = if ($_.Name -eq 'node.exe') { & $owner $_ } else { '' }
      Started = $_.CreationDate
    }
  } | Sort-Object Kind, PID
}

function Show-Status {
  $os = Get-CimInstance Win32_OperatingSystem
  "RAM: {0:N0} MB free of {1:N0} MB  (hub needs {2} MB free to start a task)" -f ($os.FreePhysicalMemory/1KB), ($os.TotalVisibleMemorySize/1KB), $MinFreeMB
  $inv = Get-Inventory
  $inv | Format-Table -AutoSize | Out-String -Width 200
  $inv | Group-Object Kind | ForEach-Object { "{0,-24} x{1,-3} {2,6} MB" -f $_.Name, $_.Count, ($_.Group | Measure-Object MB -Sum).Sum }
  "pending={0} running={1} done={2} failed={3}" -f (gci $Q.pending).Count, (gci $Q.running).Count, (gci $Q.done).Count, (gci $Q.failed).Count
}

function Add-Task {
  if (-not $Prompt) { throw 'add needs a prompt' }
  $id = '{0:yyyyMMdd-HHmmss}-{1}' -f (Get-Date), ($Name -replace '[^\w-]','_')
  @{ id=$id; prompt=$Prompt; dir=$Dir; tools=$Tools; created=(Get-Date).ToString('s') } |
    ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $Q.pending "$id.json")
  "queued $id"
}

function Invoke-RunOnce {
  if (Test-Path $Lock) {
    $lp = [int](Get-Content $Lock -EA SilentlyContinue)
    if ($lp -and (Get-Process -Id $lp -EA SilentlyContinue)) { return "busy: task worker PID $lp still running" }
    Remove-Item $Lock -Force
  }
  $next = Get-ChildItem $Q.pending -Filter *.json | Sort-Object Name | Select-Object -First 1
  if (-not $next) { return 'idle: queue empty' }
  $free = Get-FreeMB
  if ($free -lt $MinFreeMB) { return "waiting: only $free MB free (< $MinFreeMB)" }

  $t = Get-Content $next.FullName -Raw | ConvertFrom-Json
  $run = Join-Path $Q.running $next.Name; Move-Item $next.FullName $run
  $out = Join-Path $Logs "$($t.id).out.txt"
  $claude = (Get-Command claude -EA Stop).Source
  # PS 5.1 Start-Process does not quote array args, so quote each one ourselves
  $cliArgs = @('-p', $t.prompt, '--model', $Model, '--output-format', 'text', '--allowedTools', $t.tools) |
               ForEach-Object { '"' + ($_ -replace '"','\"') + '"' }
  $p = Start-Process -FilePath $claude -ArgumentList ($cliArgs -join ' ') -WorkingDirectory $t.dir `
         -RedirectStandardOutput $out -RedirectStandardError "$out.err" -NoNewWindow -PassThru
  $p.Id | Set-Content $Lock
  $p.WaitForExit()
  Remove-Item $Lock -Force -EA SilentlyContinue
  $dest = if ($p.ExitCode -eq 0) { $Q.done } else { $Q.failed }
  Move-Item $run (Join-Path $dest $next.Name)
  "finished $($t.id) exit=$($p.ExitCode) -> $out"
}

function Get-MasterPids {
  # every claude.exe above this script = the master; stop must never touch these
  $ids = @(); $x = Get-CimInstance Win32_Process -Filter "ProcessId=$PID"
  for ($i = 0; $i -lt 10 -and $x; $i++) {
    if ($x.Name -eq 'claude.exe') { $ids += [int]$x.ProcessId }
    $x = Get-CimInstance Win32_Process -Filter "ProcessId=$($x.ParentProcessId)"
  }; $ids
}

function Start-Clone {
  if (-not $Prompt) { throw 'spawn needs a prompt' }
  if (Test-Path $Lock) { return 'refused: a hub task is running (one at a time)' }
  $free = Get-FreeMB
  if ($free -lt $MinFreeMB) { return "refused: only $free MB free (< $MinFreeMB)" }
  $label = 'hub-' + ($Name -replace '[^\w-]','_')
  Push-Location $Dir
  try { claude --bg -n $label --model $Model --allowedTools $Tools $Prompt } finally { Pop-Location }
  "spawned $label on $Model ($free MB was free). Check: claude agents / claude logs $label"
}

function Invoke-Git { git -C $Repo -c user.name=EndoScorpion -c user.email=301392096+EndoScorpion@users.noreply.github.com @args }

function Sync-Bridge([string]$Msg = 'hub: sync') {
  if ((Invoke-Git branch --show-current) -ne $Branch) { return "refused: $Repo is not on $Branch" }
  Invoke-Git pull --ff-only origin $Branch | Out-Null
  if ($LASTEXITCODE) { return 'pull failed (local commits or conflicts) - fix by hand, nothing pushed' }
  $tasks = Join-Path $Repo 'data\tasks'; New-Item -ItemType Directory -Force $tasks | Out-Null
  @("# Hub live snapshot (auto, written by ClaudeHub hub.ps1 sync - do not edit)",
    "Updated: $(Get-Date -Format 's') local", '```', (Show-Status | Out-String).Trim(), '```',
    'Open tasks: ' + ((Get-ChildItem $tasks -Filter *.md -Name) -join ', ')) |
    Set-Content -Encoding utf8 (Join-Path $Repo 'data\HUB_LIVE.md')
  $paths = @('data/HUB_LIVE.md'); if (Get-ChildItem $tasks -Filter *.md) { $paths += 'data/tasks' }
  Invoke-Git add -- @paths
  Invoke-Git diff --cached --quiet -- @paths
  if (-not $LASTEXITCODE) { return 'sync: nothing new to push' }
  Invoke-Git commit -q -m $Msg -- @paths
  if ($LASTEXITCODE) { return 'sync: commit failed, nothing pushed' }
  foreach ($wait in 0,2,4,8,16) {
    Start-Sleep $wait; Invoke-Git push -q origin $Branch
    if (-not $LASTEXITCODE) { return "sync: pushed ($Msg)" }
  }
  'sync: push failed after retries (commit kept locally)'
}

function Post-Task {
  if (-not $Prompt) { throw 'post needs task text' }
  $id = '{0:yyyyMMdd-HHmmss}-{1}' -f (Get-Date), ($Name -replace '[^\w-]','_')
  $tasks = Join-Path $Repo 'data\tasks'; New-Item -ItemType Directory -Force $tasks | Out-Null
  @("# Task $id", "to: $To", 'status: open', "posted: $(Get-Date -Format 's')", '',
    $Prompt, '', "Reply by pushing results/$id.md (5 lines max). Read-only on the PC side.") |
    Set-Content -Encoding utf8 (Join-Path $tasks "$id.md")
  Sync-Bridge "hub: task $id for $To"
}

switch ($Cmd) {
  'status'   { Show-Status }
  'add'      { Add-Task }
  'list'     { foreach ($s in 'pending','running','done','failed') { "[$s]"; gci $Q[$s] -Name } }
  'run-once' { Invoke-RunOnce }
  'spawn'    { Start-Clone }
  'agents'   { claude agents --json }
  'post'     { Post-Task }
  'sync'     { Sync-Bridge }
  'results'  { Invoke-Git pull -q --ff-only origin $Branch; Get-ChildItem (Join-Path $Repo 'results') -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object LastWriteTime, Name }
  'watch'    {
    $lastSync = [datetime]::MinValue
    while ($true) {
      Show-Status | Set-Content -Encoding utf8 (Join-Path $Logs 'status.txt')
      $r = Invoke-RunOnce; "$(Get-Date -f s) $r" | Tee-Object -Append (Join-Path $Logs 'watch.log')
      if (((Get-Date) - $lastSync).TotalSeconds -ge $SyncEvery) {
        "$(Get-Date -f s) $(Sync-Bridge)" | Tee-Object -Append (Join-Path $Logs 'watch.log'); $lastSync = Get-Date
      }
      Start-Sleep -Seconds $Every
    }
  }
  'stop'     {
    if (-not $Id) { throw 'stop needs -Id <pid>' }
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$Id"
    if (-not $p) { return "no process $Id" }
    if ($Id -in (Get-MasterPids)) { return "refused: $Id is the master session" }
    if (-not $Force) { return "would kill $Id ($($p.Name)) and its children; re-run with -Force" }
    taskkill /PID $Id /T /F
  }
}

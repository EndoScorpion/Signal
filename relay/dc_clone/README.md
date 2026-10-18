# DC Clone — shared device MCP bridge

Replaces DC Remote. One Windows service; unlimited cloud sessions connect simultaneously via the GitHub relay.

## Architecture

```
Cloud session A ─┐
Cloud session B ─┤──► tasks/dc_queue.json (GitHub relay branch)
Cloud session C ─┘         │
                            ▼
                    server.js on Lenovo
                    polls every 5 s, executes, writes
                            │
                            ▼
                    tasks/dc_results/{id}.json
                            │
                    cloud session polls & reads result
```

No inbound connections. No ngrok. Works behind NAT on a locked PC.

## Device setup (once)

1. `git pull` the relay branch on the Lenovo.
2. Set your GitHub token: `$env:GITHUB_TOKEN = "ghp_xxx"` (or put it in `%USERPROFILE%\.github_token`).
3. Run as Admin:
   ```powershell
   Set-Location "C:\Users\endos\Desktop\hst_work\Signal\relay\dc_clone"
   powershell -ExecutionPolicy Bypass -File install.ps1 -Token ghp_xxx
   ```
4. The Task Scheduler task `DcCloneServer` starts now and at every logon.
5. Check log: `relay\dc_clone\dc_clone.log`

## Cloud usage

From any cloud session with `GITHUB_TOKEN` set:

```bash
python3 relay/dc_clone/enqueue.py read_file '{"path":"C:\\Users\\endos\\Desktop\\hst_work\\Signal\\CLAUDE.md"}'
python3 relay/dc_clone/enqueue.py execute_powershell '{"command":"Get-Date"}'
python3 relay/dc_clone/enqueue.py write_file '{"path":"C:\\Users\\endos\\Desktop\\test.txt","content":"hello"}'
python3 relay/dc_clone/enqueue.py list_dir '{"path":"C:\\Users\\endos\\Desktop\\hst_work\\Signal"}'
```

Result is printed as JSON to stdout. Timeout: 60 s.

## Supported tools

| Tool | Args |
|------|------|
| `read_file` | `path` |
| `write_file` | `path`, `content` |
| `list_dir` | `path` |
| `execute_powershell` | `command` (string) |

## Notes

- Multiple sessions can enqueue simultaneously; server processes one at a time (atomic claim via GitHub sha).
- Results stay in `tasks/dc_results/` — clean up old files periodically.
- No NSSM required — pure Task Scheduler.

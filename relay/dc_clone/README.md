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

## Cloud usage (Claude sessions — MCP tools)

Cloud sessions inside claude.ai use `mcp__github__` tools directly (the proxy blocks raw GitHub writes):

```python
# 1. Read current queue
mcp__github__get_file_contents(owner="EndoScorpion", repo="Signal",
    path="tasks/dc_queue.json", ref="relay")

# 2. Append your job and write back (sha required)
mcp__github__create_or_update_file(owner="EndoScorpion", repo="Signal",
    path="tasks/dc_queue.json", branch="relay",
    content="[{...}]", sha="<sha from step 1>",
    message="enqueue <id>")

# 3. Poll for result
mcp__github__get_file_contents(owner="EndoScorpion", repo="Signal",
    path="tasks/dc_results/<id>.json", ref="relay")
```

## Device / local usage (enqueue.py CLI)

From the Lenovo (or any machine with a write-scoped PAT in `GITHUB_TOKEN`):

```bash
python3 relay/dc_clone/enqueue.py read_file '{"path":"C:\\Users\\endos\\Desktop\\hst_work\\Signal\\CLAUDE.md"}'
python3 relay/dc_clone/enqueue.py execute_powershell '{"command":"Get-Date"}'
python3 relay/dc_clone/enqueue.py write_file '{"path":"C:\\Users\\endos\\Desktop\\test.txt","content":"hello"}'
python3 relay/dc_clone/enqueue.py list_dir '{"path":"C:\\Users\\endos\\Desktop\\hst_work\\Signal"}'
```

> **Note:** Cloud GITHUB_TOKEN is read-only (proxy restriction). enqueue.py uses `gh api`
> which also fails from cloud. From cloud, use the MCP pattern above.

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

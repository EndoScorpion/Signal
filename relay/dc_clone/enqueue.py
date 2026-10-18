#!/usr/bin/env python3
"""
Cloud-side helper — enqueue a tool call and wait for the result.
Any number of cloud sessions can call this concurrently.

Uses `gh api` CLI for writes (has OAuth write access); urllib for reads.

Usage:
  python3 enqueue.py read_file '{"path":"C:\\\\Users\\\\endos\\\\Desktop\\\\hst_work\\\\Signal\\\\CLAUDE.md"}'
  python3 enqueue.py execute_powershell '{"command":"Get-Date"}'
"""
import sys, json, time, uuid, os, urllib.request, urllib.error, base64, subprocess

OWNER  = "EndoScorpion"
REPO   = "Signal"
BRANCH = "relay"
QUEUE  = "tasks/dc_queue.json"
RESULTS_DIR = "tasks/dc_results"
TIMEOUT_S = 60
POLL_S  = 3
TOKEN  = os.environ.get("GITHUB_TOKEN", "")

HDR = {"Authorization": f"token {TOKEN}", "User-Agent": "dc-clone-enqueue",
       "Accept": "application/vnd.github+json"}

def gh_get(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers=HDR)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get_file(p):
    try:
        r = gh_get(f"/repos/{OWNER}/{REPO}/contents/{p}?ref={BRANCH}")
        return base64.b64decode(r["content"]).decode(), r["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404: return None, None
        raise

def put_file_gh_cli(p, content, sha, msg):
    """Write file via gh api CLI (has OAuth write access)."""
    encoded = base64.b64encode(content.encode()).decode()
    body = {"message": msg, "content": encoded, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    result = subprocess.run(
        ["gh", "api", f"/repos/{OWNER}/{REPO}/contents/{p}",
         "-X", "PUT", "--input", "-"],
        input=json.dumps(body).encode(),
        capture_output=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api PUT failed: {result.stderr.decode()}")
    return json.loads(result.stdout)

def enqueue(tool, args):
    req_id = str(uuid.uuid4())[:8]
    for _ in range(5):  # retry on race
        content, sha = get_file(QUEUE)
        queue = json.loads(content) if content else []
        queue.append({"id": req_id, "tool": tool, "args": args, "status": "pending",
                       "queued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        try:
            put_file_gh_cli(QUEUE, json.dumps(queue, indent=2), sha, f"enqueue {req_id}")
            return req_id
        except Exception as e:
            if "422" in str(e) or "409" in str(e):
                time.sleep(1)
                continue
            raise
    raise RuntimeError("failed to enqueue after retries")

def wait_result(req_id):
    deadline = time.time() + TIMEOUT_S
    result_path = f"{RESULTS_DIR}/{req_id}.json"
    while time.time() < deadline:
        content, _ = get_file(result_path)
        if content:
            return json.loads(content)["result"]
        time.sleep(POLL_S)
    raise TimeoutError(f"no result for {req_id} after {TIMEOUT_S}s")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    tool = sys.argv[1]
    args = json.loads(sys.argv[2])
    req_id = enqueue(tool, args)
    print(f"queued {req_id}, waiting...", file=sys.stderr)
    result = wait_result(req_id)
    print(json.dumps(result, indent=2))

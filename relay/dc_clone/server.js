#!/usr/bin/env node
/**
 * DC Clone — shared GitHub-relay MCP executor
 * Runs on Nasif's Lenovo. Polls dc_queue.json, executes tools, writes results.
 * Multiple cloud sessions write to the queue; this service processes all of them.
 *
 * Tools exposed: read_file, write_file, execute_powershell, list_dir
 */

const https = require("https");
const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

// ── Config ──────────────────────────────────────────────────────────────────
const OWNER = "EndoScorpion";
const REPO  = "Signal";
const BRANCH = "relay";
const QUEUE_PATH  = "tasks/dc_queue.json";
const RESULTS_DIR = "tasks/dc_results";
const POLL_MS = 10000;          // base poll interval (10s)
const BACKOFF_MIN  = 30000;     // 30s min on error
const BACKOFF_MAX  = 300000;    // 5min max
const TOKEN = process.env.GITHUB_TOKEN || (() => {
  try { return fs.readFileSync(path.join(os.homedir(), ".github_token"), "utf8").trim(); } catch { return ""; }
})();

if (!TOKEN) { console.error("GITHUB_TOKEN not set"); process.exit(1); }

let errorBackoff = 0; // ms; 0 = no error, use POLL_MS

// ── GitHub helpers ───────────────────────────────────────────────────────────
function ghGet(apiPath) {
  return new Promise((res, rej) => {
    const opts = {
      hostname: "api.github.com", path: apiPath,
      headers: { Authorization: `token ${TOKEN}`, "User-Agent": "dc-clone", Accept: "application/vnd.github+json" }
    };
    https.get(opts, r => {
      let d = ""; r.on("data", c => d += c); r.on("end", () => {
        try { res(JSON.parse(d)); } catch { rej(new Error(d)); }
      });
    }).on("error", rej);
  });
}

function ghPut(apiPath, body) {
  const data = JSON.stringify(body);
  return new Promise((res, rej) => {
    const opts = {
      hostname: "api.github.com", path: apiPath, method: "PUT",
      headers: {
        Authorization: `token ${TOKEN}`, "User-Agent": "dc-clone",
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data)
      }
    };
    const req = https.request(opts, r => {
      let d = ""; r.on("data", c => d += c); r.on("end", () => {
        try { res(JSON.parse(d)); } catch { rej(new Error(d)); }
      });
    });
    req.on("error", rej); req.write(data); req.end();
  });
}

async function getFile(filePath) {
  const r = await ghGet(`/repos/${OWNER}/${REPO}/contents/${filePath}?ref=${BRANCH}`);
  if (r.message) return null;
  return { content: Buffer.from(r.content, "base64").toString("utf8"), sha: r.sha };
}

async function putFile(filePath, content, sha, msg) {
  return ghPut(`/repos/${OWNER}/${REPO}/contents/${filePath}`, {
    message: msg, content: Buffer.from(content).toString("base64"),
    branch: BRANCH, ...(sha ? { sha } : {})
  });
}

// ── Tool executor ────────────────────────────────────────────────────────────
async function runTool(req) {
  const name = req.tool;
  // Support both req.args.X and req.X (top-level shorthand used by cloud sessions)
  const args = Object.assign({}, req.args || {}, {
    path:    req.path    || (req.args && req.args.path),
    content: req.content || (req.args && req.args.content),
    command: req.command || (req.args && req.args.command),
  });

  if (name === "read_file") {
    if (!args.path) return { error: "path required" };
    try { return { content: fs.readFileSync(args.path, "utf8") }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "write_file") {
    if (!args.path || args.content == null) return { error: "path and content required" };
    try { fs.mkdirSync(path.dirname(args.path), { recursive: true }); fs.writeFileSync(args.path, args.content, "utf8"); return { ok: true }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "list_dir") {
    const p = args.path || ".";
    try { return { entries: fs.readdirSync(p) }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "execute_powershell") {
    if (!args.command) return { error: "command required" };
    return new Promise(res => {
      execFile("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", args.command],
        { timeout: 60000 }, (err, stdout, stderr) => {
          res({ stdout: stdout || "", stderr: stderr || "", exit: err ? err.code : 0 });
        });
    });
  }
  return { error: `unknown tool: ${name}` };
}

// ── Main poll loop ────────────────────────────────────────────────────────────
async function poll() {
  try {
    const qf = await getFile(QUEUE_PATH);
    if (!qf) { errorBackoff = 0; scheduleNext(); return; }

    let queue;
    try { queue = JSON.parse(qf.content); } catch { scheduleNext(); return; }
    if (!Array.isArray(queue) || queue.length === 0) { errorBackoff = 0; scheduleNext(); return; }

    const idx = queue.findIndex(r => !r.status || r.status === "pending");
    if (idx === -1) { errorBackoff = 0; scheduleNext(); return; }

    const item = queue[idx];
    queue[idx] = { ...item, status: "claimed", claimed_at: new Date().toISOString() };

    try {
      await putFile(QUEUE_PATH, JSON.stringify(queue, null, 2), qf.sha, `claim ${item.id}`);
    } catch { scheduleNext(); return; }

    console.log(`[dc-clone] executing ${item.id}: ${item.tool}`);
    const result = await runTool(item);

    const resultPath = `${RESULTS_DIR}/${item.id}.json`;
    const resultContent = JSON.stringify({ id: item.id, tool: item.tool, result, completed_at: new Date().toISOString() }, null, 2);
    const existing = await getFile(resultPath);
    await putFile(resultPath, resultContent, existing?.sha || undefined, `result ${item.id}`);

    const qf2 = await getFile(QUEUE_PATH);
    if (qf2) {
      try {
        const q2 = JSON.parse(qf2.content).filter(r => r.id !== item.id);
        await putFile(QUEUE_PATH, JSON.stringify(q2, null, 2), qf2.sha, `done ${item.id}`);
      } catch { /* non-fatal */ }
    }
    console.log(`[dc-clone] done ${item.id}`);
    errorBackoff = 0;
  } catch (e) {
    errorBackoff = errorBackoff === 0
      ? BACKOFF_MIN
      : Math.min(errorBackoff * 2, BACKOFF_MAX);
    console.error(`[dc-clone] poll error (backoff ${errorBackoff}ms):`, e.message);
  }
  scheduleNext();
}

function scheduleNext() {
  setTimeout(poll, errorBackoff > 0 ? errorBackoff : POLL_MS);
}

console.log("[dc-clone] starting, polling every", POLL_MS, "ms");
poll();

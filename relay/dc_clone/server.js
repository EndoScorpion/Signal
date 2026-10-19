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
const POLL_MS = 5000;
const TOKEN = process.env.GITHUB_TOKEN || (() => {
  try { return fs.readFileSync(path.join(os.homedir(), ".github_token"), "utf8").trim(); } catch { return ""; }
})();

if (!TOKEN) { console.error("GITHUB_TOKEN not set"); process.exit(1); }

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
async function runTool(name, args) {
  if (name === "read_file") {
    const p = args.path;
    if (!p) return { error: "path required" };
    try { return { content: fs.readFileSync(p, "utf8") }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "write_file") {
    const { path: p, content } = args;
    if (!p || content == null) return { error: "path and content required" };
    try { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, content, "utf8"); return { ok: true }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "list_dir") {
    const p = args.path || ".";
    try { return { entries: fs.readdirSync(p) }; }
    catch (e) { return { error: e.message }; }
  }
  if (name === "execute_powershell") {
    const { command } = args;
    if (!command) return { error: "command required" };
    return new Promise(res => {
      execFile("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", command],
        { timeout: 30000 }, (err, stdout, stderr) => {
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
    if (!qf) { scheduleNext(); return; }

    let queue;
    try { queue = JSON.parse(qf.content); } catch { scheduleNext(); return; }
    if (!Array.isArray(queue) || queue.length === 0) { scheduleNext(); return; }

    // Claim first pending item
    const idx = queue.findIndex(r => r.status === "pending");
    if (idx === -1) { scheduleNext(); return; }

    const req = queue[idx];
    queue[idx] = { ...req, status: "claimed", claimed_at: new Date().toISOString() };

    // Write claimed queue back (optimistic lock via sha)
    try {
      await putFile(QUEUE_PATH, JSON.stringify(queue, null, 2), qf.sha, `claim ${req.id}`);
    } catch { scheduleNext(); return; } // another poller won the race

    console.log(`[dc-clone] executing ${req.id}: ${req.tool}`);
    const result = await runTool(req.tool, req.args || {});

    // Write result file
    const resultPath = `${RESULTS_DIR}/${req.id}.json`;
    const resultContent = JSON.stringify({ id: req.id, tool: req.tool, result, completed_at: new Date().toISOString() }, null, 2);
    const existing = await getFile(resultPath);
    await putFile(resultPath, resultContent, existing?.sha || undefined, `result ${req.id}`);

    // Remove from queue
    const qf2 = await getFile(QUEUE_PATH);
    if (qf2) {
      try {
        const q2 = JSON.parse(qf2.content).filter(r => r.id !== req.id);
        await putFile(QUEUE_PATH, JSON.stringify(q2, null, 2), qf2.sha, `done ${req.id}`);
      } catch { /* non-fatal */ }
    }
    console.log(`[dc-clone] done ${req.id}`);
  } catch (e) {
    console.error("[dc-clone] poll error:", e.message);
  }
  scheduleNext();
}

function scheduleNext() { setTimeout(poll, POLL_MS); }

console.log("[dc-clone] starting, polling every", POLL_MS, "ms");
poll();

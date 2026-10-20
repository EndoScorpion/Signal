// Slack Socket Mode bridge — runs on LocalThug only, not in cloud sandbox
// Requires: npm install @slack/bolt node-fetch
// Env vars: SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET, GITHUB_RELAY_TOKEN
// Optional: GITHUB_REPO (default: EndoScorpion/Signal), GITHUB_BRANCH (default: relay), AUTHORIZED_SLACK_USER

const { App } = require('@slack/bolt');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Load .env file if present
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [k, ...v] = line.split('=');
    if (k && v.length) process.env[k.trim()] = v.join('=').trim();
  });
}

const REPO = process.env.GITHUB_REPO || 'EndoScorpion/Signal';
const BRANCH = process.env.GITHUB_BRANCH || 'relay';
const AUTHORIZED_USER = process.env.AUTHORIZED_SLACK_USER || '';

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  appToken: process.env.SLACK_APP_TOKEN,
  socketMode: true,
});

function githubApi(method, endpoint, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = https.request({
      hostname: 'api.github.com',
      path: endpoint,
      method,
      headers: {
        'Authorization': `token ${process.env.GITHUB_RELAY_TOKEN}`,
        'User-Agent': 'slack-bolt-bridge',
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
    }, res => {
      let buf = '';
      res.on('data', d => buf += d);
      res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(buf || '{}') }));
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function getFile(filePath) {
  const r = await githubApi('GET', `/repos/${REPO}/contents/${filePath}?ref=${BRANCH}`);
  if (r.status === 404) return { content: [], sha: null };
  const content = JSON.parse(Buffer.from(r.body.content, 'base64').toString());
  return { content, sha: r.body.sha };
}

async function putFile(filePath, content, sha) {
  const body = {
    message: `relay: slack bridge update ${filePath}`,
    content: Buffer.from(JSON.stringify(content, null, 2)).toString('base64'),
    branch: BRANCH,
    ...(sha ? { sha } : {}),
  };
  return githubApi('PUT', `/repos/${REPO}/contents/${filePath}`, body);
}

async function queueCommand(text, username) {
  const { content: queue, sha } = await getFile('relay/cmd_queue.json');
  const entry = {
    id: `slack_${Date.now()}`,
    command: text,
    shell: 'slack',
    status: 'pending',
    ts: new Date().toISOString(),
    source: 'slack:dm',
    from: username,
  };
  queue.push(entry);
  await putFile('relay/cmd_queue.json', queue, sha);
  return entry.id;
}

async function pollResults(since, say) {
  try {
    const { content: results } = await getFile('relay/cmd_results.json');
    const fresh = results.filter(r => r.status === 'done' && r.ts > since && r.source === 'slack:dm');
    for (const r of fresh) {
      await say(`[${r.id}] ${r.output || '(no output)'}`);
    }
  } catch (e) { /* silent */ }
}

app.message(async ({ message, say }) => {
  if (message.bot_id) return;
  if (AUTHORIZED_USER && message.user !== AUTHORIZED_USER) return;
  const text = message.text || '';
  const since = new Date().toISOString();
  try {
    const id = await queueCommand(text, message.user);
    await say(`Queued as ${id}. Polling for result...`);
    // Poll 3 times over 90s
    for (let i = 0; i < 3; i++) {
      await new Promise(r => setTimeout(r, 30000));
      await pollResults(since, say);
    }
  } catch (e) {
    await say(`Bridge error: ${e.message}`);
  }
});

app.event('app_mention', async ({ event, say }) => {
  if (AUTHORIZED_USER && event.user !== AUTHORIZED_USER) return;
  const text = (event.text || '').replace(/<@[^>]+>/g, '').trim();
  const id = await queueCommand(text, event.user);
  await say(`<@${event.user}> Queued as ${id}.`);
});

(async () => {
  await app.start();
  console.log('Slack Socket Mode bridge running. Waiting for messages...');
})();

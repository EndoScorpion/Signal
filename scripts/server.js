const http = require('http');
const fs   = require('fs');
const path = require('path');

const FILE_PATH = path.join(__dirname, 'local_chalkboard.json');
const BAK_PATH  = FILE_PATH + '.bak';
const TMP_PATH  = FILE_PATH + '.tmp';
const MAX_MSG   = 200;
const PORT      = 8080;

// Shared secret — set SLC_RELAY_SECRET env var before starting.
// GET /board is always open; POST /write requires X-Token header.
const SECRET = process.env.SLC_RELAY_SECRET || '';

function loadBoard() {
    for (const p of [FILE_PATH, BAK_PATH]) {
        try {
            const obj = JSON.parse(fs.readFileSync(p, 'utf8'));
            if (obj && Array.isArray(obj.messages)) return obj;
        } catch (_) {}
    }
    return { system_state: {}, messages: [] };
}

function saveBoard(json) {
    // Atomic write: tmp -> backup -> rename
    fs.writeFileSync(TMP_PATH, JSON.stringify(json, null, 2));
    if (fs.existsSync(FILE_PATH)) fs.copyFileSync(FILE_PATH, BAK_PATH);
    fs.renameSync(TMP_PATH, FILE_PATH);
}

if (!fs.existsSync(FILE_PATH)) saveBoard({ system_state: {}, messages: [] });

const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Token');

    if (req.method === 'OPTIONS') { res.writeHead(200); return res.end(); }

    if (req.method === 'GET' && req.url === '/ping') {
        res.writeHead(200); return res.end('pong');
    }

    if (req.method === 'GET' && req.url === '/board') {
        try {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(loadBoard()));
        } catch (e) { res.writeHead(500); res.end('err'); }
        return;
    }

    if (req.method === 'POST' && req.url === '/write') {
        // Auth check — skip if no secret configured
        if (SECRET && req.headers['x-token'] !== SECRET) {
            res.writeHead(401); return res.end('Unauthorized');
        }
        let body = '';
        req.on('data', c => { if (body.length < 4096) body += c.toString(); });
        req.on('end', () => {
            try {
                const inc = JSON.parse(body);
                const json = loadBoard();
                if (inc.message) {
                    json.messages.push({
                        id: Date.now().toString(36) + Math.random().toString(36).slice(2,5),
                        sender: String(inc.sender || 'unknown').slice(0, 32),
                        text:   String(inc.message).slice(0, 256),
                        ts:     new Date().toISOString()
                    });
                    if (json.messages.length > MAX_MSG) json.messages = json.messages.slice(-MAX_MSG);
                }
                if (inc.system_state) json.system_state = { ...json.system_state, ...inc.system_state };
                saveBoard(json);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, n: json.messages.length }));
            } catch (e) { res.writeHead(400); res.end('Bad JSON'); }
        });
        return;
    }

    res.writeHead(404); res.end();
});

server.on('error', e => { console.error(e.message); process.exit(1); });
process.on('uncaughtException', e => console.error('Uncaught:', e.message));
server.listen(PORT, '127.0.0.1', () => console.log('Blackboard :' + PORT));

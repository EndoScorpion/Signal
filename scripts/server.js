const http = require('http');
const fs = require('fs');
const path = require('path');

const FILE_PATH = path.join(__dirname, 'local_chalkboard.json');
const BAK_PATH  = FILE_PATH + '.bak';
const TMP_PATH  = FILE_PATH + '.tmp';
const MAX_MSG   = 200;
const PORT      = 8080;

function loadBoard() {
    for (const p of [FILE_PATH, BAK_PATH]) {
        try {
            const raw = fs.readFileSync(p, 'utf8');
            const obj = JSON.parse(raw);
            if (obj && Array.isArray(obj.messages)) return obj;
        } catch (_) {}
    }
    return { system_state: {}, messages: [] };
}

function saveBoard(json) {
    const data = JSON.stringify(json, null, 2);
    // Atomic: write tmp -> rename (avoids partial-write corruption)
    fs.writeFileSync(TMP_PATH, data);
    if (fs.existsSync(FILE_PATH)) fs.copyFileSync(FILE_PATH, BAK_PATH);
    fs.renameSync(TMP_PATH, FILE_PATH);
}

// Init
if (!fs.existsSync(FILE_PATH)) saveBoard({ system_state: {}, messages: [] });

const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') { res.writeHead(200); return res.end(); }

    if (req.method === 'GET' && req.url === '/board') {
        try {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(loadBoard()));
        } catch (e) {
            res.writeHead(500); res.end('Read error');
        }

    } else if (req.method === 'POST' && req.url === '/write') {
        let body = '';
        req.on('data', c => body += c.toString());
        req.on('end', () => {
            try {
                const inc = JSON.parse(body);
                const json = loadBoard();
                if (inc.message) {
                    json.messages.push({
                        id: Date.now().toString(36) + Math.random().toString(36).slice(2,5),
                        sender: (inc.sender || 'unknown').slice(0, 32),
                        text: String(inc.message).slice(0, 256), // cap length
                        ts: new Date().toISOString()
                    });
                    if (json.messages.length > MAX_MSG) json.messages = json.messages.slice(-MAX_MSG);
                }
                if (inc.system_state) json.system_state = { ...json.system_state, ...inc.system_state };
                saveBoard(json);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, n: json.messages.length }));
            } catch (e) {
                res.writeHead(400); res.end('Bad request');
            }
        });

    } else if (req.method === 'GET' && req.url === '/ping') {
        res.writeHead(200); res.end('pong');
    } else {
        res.writeHead(404); res.end();
    }
});

server.on('error', e => { console.error('Server error:', e.message); process.exit(1); });
process.on('uncaughtException', e => { console.error('Uncaught:', e.message); });

server.listen(PORT, '127.0.0.1', () => console.log('Blackboard :' + PORT));

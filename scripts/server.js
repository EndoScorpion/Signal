const http = require('http');
const fs = require('fs');
const path = require('path');

const FILE_PATH = path.join(__dirname, 'local_chalkboard.json');

if (!fs.existsSync(FILE_PATH)) {
    fs.writeFileSync(FILE_PATH, JSON.stringify({ system_state: {}, messages: [] }, null, 2));
}

const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        return res.end();
    }

    if (req.method === 'GET' && req.url === '/board') {
        fs.readFile(FILE_PATH, 'utf8', (err, data) => {
            if (err) { res.writeHead(500); return res.end("Error reading blackboard."); }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        });
    } else if (req.method === 'POST' && req.url === '/write') {
        let body = '';
        req.on('data', chunk => body += chunk.toString());
        req.on('end', () => {
            try {
                const incoming = JSON.parse(body);
                // VAGUE ONLY: sender, message (codes: WR/WP/PF/n), system_state
                fs.readFile(FILE_PATH, 'utf8', (err, data) => {
                    let json = err ? { system_state: {}, messages: [] } : JSON.parse(data);
                    if (incoming.message) {
                        json.messages.push({
                            id: Date.now() + Math.random().toString(36).substr(2, 5),
                            sender: incoming.sender || 'unknown',
                            text: incoming.message,
                            timestamp: new Date().toISOString()
                        });
                        // Keep last 200 messages only
                        if (json.messages.length > 200) json.messages = json.messages.slice(-200);
                    }
                    if (incoming.system_state) {
                        json.system_state = { ...json.system_state, ...incoming.system_state };
                    }
                    fs.writeFile(FILE_PATH, JSON.stringify(json, null, 2), (writeErr) => {
                        if (writeErr) { res.writeHead(500); return res.end("Write failed."); }
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ status: "ok", count: json.messages.length }));
                    });
                });
            } catch (e) {
                res.writeHead(400);
                res.end("Invalid JSON.");
            }
        });
    } else {
        res.writeHead(404);
        res.end();
    }
});

server.listen(8080, '127.0.0.1', () => {
    console.log("Blackboard on http://127.0.0.1:8080");
});

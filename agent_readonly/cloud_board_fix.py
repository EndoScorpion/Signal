import json, os, shutil, time
p = r'C:\Users\endos\Signal\data\agent_board.json'
bak = r'C:\Users\endos\Signal\data\agent_board.bak_BOM_14Oct2026.json'
m0 = os.path.getmtime(p); raw = open(p, 'rb').read()
if raw[:3] != b'\xef\xbb\xbf': print('no BOM, nothing to do'); raise SystemExit
if not os.path.exists(bak): shutil.copy2(p, bak)
d = json.loads(raw.decode('utf-8-sig'))
tmp = p + '.tmp_fix'
open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(d, indent=1))
if os.path.getmtime(p) != m0: os.remove(tmp); print('file changed during fix, aborted (no changes)'); raise SystemExit
os.replace(tmp, p)
chk = json.load(open(p, encoding='utf-8')); print('fixed: jobs', len(chk['jobs']), 'backup', bak, os.path.getsize(bak), 'bytes')
try:
    json.load(open(p)); print('plain json.load (as agent_board.py does) OK')
except Exception as e: print('plain load still fails', e)

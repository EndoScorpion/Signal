import json, os, sys, glob
for p in [r'C:\Users\endos\Signal\data\agent_board.json'] + glob.glob(r'C:\Users\endos\Signal\**\agent_board.json', recursive=True):
    if not os.path.exists(p): continue
    raw = open(p, 'rb').read()
    print(p, len(raw), 'bytes', 'BOM' if raw[:3] == b'\xef\xbb\xbf' else 'noBOM', 'mtime', os.path.getmtime(p))
    try:
        d = json.loads(raw.decode('utf-8-sig')); print('  valid, jobs', len(d.get('jobs', [])))
    except Exception as e:
        print('  ERROR', e)
        pos = getattr(e, 'pos', 0)
        print('  context:', repr(raw[max(0, pos - 80):pos + 80]))

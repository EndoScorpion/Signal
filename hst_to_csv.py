#!/usr/bin/env python3
"""MT4 .hst -> compact CSV (read-only; never modifies the input). Handles format 400 and 401.
Output rows: YYYY.MM.DD,HH:MM,open,high,low,close,tick_volume,spread_points   (spread only in v401)
Usage: python hst_to_csv.py EURUSD1.hst out_dir [--from 2023-01-01] [--to 2026-12-31] [--split-year]
Tip: copy the .hst somewhere else first (e.g. Desktop), ideally with MT4 closed, and run this on the copy."""
import sys,os,struct,argparse,datetime,zipfile
ap=argparse.ArgumentParser();ap.add_argument("hst");ap.add_argument("out");ap.add_argument("--from",dest="frm");ap.add_argument("--to");ap.add_argument("--split-year",action="store_true");ap.add_argument("--zip",action="store_true")
a=ap.parse_args();os.makedirs(a.out,exist_ok=True)
f=open(a.hst,"rb");hd=f.read(148);ver=struct.unpack("<i",hd[:4])[0];sym=hd[68:80].split(b"\0")[0].decode(errors="ignore");per,dig=struct.unpack("<ii",hd[80:88])
if ver not in(400,401):sys.exit(f"unsupported .hst version {ver}")
fmt,size=("<qddddqiq",60) if ver==401 else ("<iddddd",44)  # v400 field order is open,low,high,close,volume
lo=datetime.datetime.fromisoformat(a.frm).timestamp() if a.frm else 0;hi=datetime.datetime.fromisoformat(a.to).timestamp()+86400 if a.to else 1e18
outs={};n=0;first=last=None
def w(year):
    k=year if a.split_year else "all"
    if k not in outs:
        p=os.path.join(a.out,f"{sym}{per}_{k}.csv");outs[k]=open(p,"w",newline="")
    return outs[k]
while True:
    buf=f.read(size*50000)
    if not buf:break
    for r in struct.iter_unpack(fmt,buf[:len(buf)//size*size]):
        t=r[0]
        if t<lo or t>=hi:continue
        d=datetime.datetime.fromtimestamp(t,datetime.timezone.utc)
        if ver==401:o,h,l,c,tv,sp,_=r[1:]
        else:o,l,h,c,tv=r[1:];sp=""
        w(d.year).write(f"{d:%Y.%m.%d,%H:%M},{o:.{dig}f},{h:.{dig}f},{l:.{dig}f},{c:.{dig}f},{tv},{sp}\n");n+=1
        first=first or d;last=d
for o in outs.values():o.close()
print(f"{sym} M{per} v{ver} digits={dig}: {n} bars {first} .. {last} -> {len(outs)} file(s) in {a.out}")
if a.zip:
    z=os.path.join(a.out,f"{sym}{per}_csv.zip")
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(os.listdir(a.out)):
            if p.endswith(".csv"):zf.write(os.path.join(a.out,p),p)
    print("zip:",z,round(os.path.getsize(z)/1e6,1),"MB")

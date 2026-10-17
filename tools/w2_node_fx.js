// w2_node_fx.js — Win Logic v2 runner with FX-specific signal extensions
// Adds T3 (session divergence: Asian-close vs London-open reversal) and
// T7 (ATR compression breakout: low-ATR-rank + 10-bar range break, 13-17 UTC).
// Run: W2_EXT=<eurusd_ext.json> node tools/w2_node_fx.js <module.html> <page_nostock.html> <empty_seed.json> <out.json>
// node tools/w2_node.js args are identical; BASE_FX seeds are added on top of BASE.

const fs=require('fs');
const [mod,page,seedF,out]=process.argv.slice(2);
const m=fs.readFileSync(mod,'utf8');

// ---- cost classes (original + forex ECN) ----
eval(m.slice(m.indexOf('var CLS='),m.indexOf('var COSTS=')));
// FXOpen ECN: 0.1pip spread (~0.001%), $4/lot RT commission (~0.004% per side), no fee, small swap
CLS.forex={pts:0,comm:0.004,fee:0,spread:0.001,swap:0.0001,tax:24,
  n:"Forex ECN FXOpen EURUSD: 0.1pip spread, $4/lot RT comm, 24% tax"};
let COSTS=JSON.parse(JSON.stringify(CLS));

function clsOf(se){return se.cls||(se.src==="hl"?"perp":(/USD[TC]?$/.test(se.s)&&se.s.length>4?"crypto":"stock"))}
const PTS=process.env.W2_PTS;
function ptOf(px){return px>=10?0.01:px>=1?0.001:px>=0.01?0.0001:0.00001}
function costOf(se){
  const c=COSTS[clsOf(se)]||COSTS.stock;
  const p=PTS!=null?+PTS:(c.pts==null?0:+c.pts);
  if(!p)return c;
  if(se._mc==null){let mc=0;se.b.forEach(x=>mc+=x.c);se._mc=mc/se.b.length}
  return Object.assign({},c,{comm:(+c.comm||0)+p*ptOf(se._mc)/2/se._mc*100})
}

// ---- engine (nb, rs, TFM, indicators, sigOf patched with T3/T7, metrics, passes) ----
eval(m.slice(m.indexOf('function nb(r)'),m.indexOf('var SC=null')));
// Patch the engine eval string to inject T3/T7 into sigOf before metrics() is defined
// This ensures metrics() calls the patched sigOf, not the original
var _engineSrc=m.slice(m.indexOf('/* ---------- indicators'),m.indexOf('var RUN={on:false'));
// Inject T3/T7 handler at the start of sigOf's switch/if block
// Find the sigOf function body and prepend our custom cases
var _T3T7code=`
// T3: London-open session-divergence (Asian bearish → London bullish reversal)
if(sp.k==="T3"){
  var _n=b.length,_en=new Uint8Array(_n),_ex=new Uint8Array(_n);
  for(var _i=3;_i<_n;_i++){
    var _d=new Date(b[_i].t),_h=_d.getUTCHours(),_dow=_d.getUTCDay();
    if(_h<7||_h>9)continue;
    if(sp.dow&&_dow!==1&&_dow!==4)continue;
    var _today=_d.getUTCDate(),_todayM=_d.getUTCMonth(),_todayY=_d.getUTCFullYear();
    var _asOpen=null,_asClose=null;
    for(var _j=_i-1;_j>=0;_j--){
      var _jd=new Date(b[_j].t);
      if(_jd.getUTCDate()!==_today||_jd.getUTCMonth()!==_todayM||_jd.getUTCFullYear()!==_todayY)break;
      var _jh=_jd.getUTCHours();
      if(_jh<7){if(_asClose===null)_asClose=b[_j];_asOpen=b[_j]}
    }
    if(!_asClose||!_asOpen)continue;
    var _asRet=(_asClose.c-_asOpen.o)/_asOpen.o;
    if(_asRet>=0)continue;
    if(b[_i].c<=b[_i].o)continue;
    var _ok=1;
    for(var _q=1;_q<=(sp.n||1);_q++){if(_i-_q>=0&&b[_i-_q+1]&&b[_i-_q]&&b[_i-_q+1].c<=b[_i-_q].c)_ok=0}
    _en[_i]=_ok;
  }
  return{en:_en,ex:_ex};
}
// T7: ATR compression breakout (NY overlap 13-17 UTC)
if(sp.k==="T7"){
  var _n=b.length,_en=new Uint8Array(_n),_ex=new Uint8Array(_n);
  var _atrN=I(b,"atr",sp.rk_n||20),_brkN=sp.brk_n||10,_rkN=sp.rk_n||20,_pct=(sp.atr_pct||80)/100;
  for(var _i=_rkN+_brkN;_i<_n;_i++){
    var _dT=new Date(b[_i].t),_hT=_dT.getUTCHours();
    if(_hT<13||_hT>17)continue;
    if(_atrN[_i]==null)continue;
    var _sumA=0,_cnt=0;
    for(var _jA=_i-_rkN;_jA<_i;_jA++){if(_jA>=0&&_atrN[_jA]!=null){_sumA+=_atrN[_jA];_cnt++}}
    if(_cnt<5)continue;
    if(_atrN[_i]>=_pct*(_sumA/_cnt))continue;
    var _hhP=b[_i-1].h;
    for(var _jH=_i-_brkN;_jH<_i;_jH++){if(_jH>=0&&b[_jH].h>_hhP)_hhP=b[_jH].h}
    _en[_i]=b[_i].c>_hhP?1:0;
  }
  return{en:_en,ex:_ex};
}
`;
// Find the start of sigOf function body and inject after the opening brace
var _sigOfStart=_engineSrc.indexOf('function sigOf(');
var _sigOfBrace=_engineSrc.indexOf('{',_sigOfStart);
_engineSrc=_engineSrc.slice(0,_sigOfBrace+1)+_T3T7code+_engineSrc.slice(_sigOfBrace+1);
eval(_engineSrc);

// (sigOf now handles T3/T7 natively — no separate override needed)
// Keep a no-op block so the rest of the file structure is unchanged:
if(false){var _sigOfOrig=sigOf;sigOf=function(sp,b){
  var n=b.length,en=new Uint8Array(n),ex=new Uint8Array(n),i,c=b.map(function(x){return x.c});

  if(sp.k==="T3"){
    // Asian session close (last bar before 07:00 UTC) vs London open (bars 07-09 UTC)
    var atr14=I(b,"atr",14);
    for(i=3;i<n;i++){
      var d=new Date(b[i].t),h=d.getUTCHours(),dow=d.getUTCDay();
      // Only fire during London open hours
      if(h<7||h>9)continue;
      // Day filter: sp.dow=1 → Mon(1) and Thu(4) only
      if(sp.dow&&dow!==1&&dow!==4)continue;
      if(atr14[i]==null)continue;
      // Find Asian session bars (same UTC date, hours 0-6)
      var today=d.getUTCDate(),todayM=d.getUTCMonth(),todayY=d.getUTCFullYear();
      var asOpen=null,asClose=null;
      for(var j=i-1;j>=0;j--){
        var jd=new Date(b[j].t);
        if(jd.getUTCDate()!==today||jd.getUTCMonth()!==todayM||jd.getUTCFullYear()!==todayY)break;
        var jh=jd.getUTCHours();
        if(jh<7){if(asClose===null)asClose=b[j];asOpen=b[j]}
      }
      if(!asClose||!asOpen)continue;
      // Asian session net direction: bearish (close < open) = reversal candidate
      var asRet=(asClose.c-asOpen.o)/asOpen.o;
      if(asRet>=0)continue; // only enter after bearish Asian session
      // London open bar is bullish
      if(b[i].c<=b[i].o)continue;
      // Confirmation: last sp.n bars are consecutive higher closes
      var ok=1;
      for(var q=1;q<=sp.n;q++){if(c[i-q+1]<=c[i-q])ok=0}
      en[i]=ok;
      ex[i]=0; // rely on exit specs
    }
    return{en:en,ex:ex};
  }

  if(sp.k==="T7"){
    // ATR compression breakout during NY overlap (13-17 UTC)
    var atrN=I(b,"atr",sp.rk_n||20);
    var brkN=sp.brk_n||10;
    var pct=(sp.atr_pct||80)/100;
    var rkN=sp.rk_n||20;
    for(i=rkN+brkN;i<n;i++){
      var dT=new Date(b[i].t),hT=dT.getUTCHours();
      if(hT<13||hT>17)continue;
      if(atrN[i]==null)continue;
      // Rolling average ATR over rk_n bars before i
      var sumA=0,cnt=0;
      for(var jA=i-rkN;jA<i;jA++){if(jA>=0&&atrN[jA]!=null){sumA+=atrN[jA];cnt++}}
      if(cnt<5)continue;
      var avgA=sumA/cnt;
      if(atrN[i]>=pct*avgA)continue;
      // Rolling high over brk_n bars before i (manual)
      var hhPrev=b[i-1].h;
      for(var jH=i-brkN;jH<i;jH++){if(jH>=0&&b[jH].h>hhPrev)hhPrev=b[jH].h}
      en[i]=b[i].c>hhPrev?1:0;
      ex[i]=0;
    }
    return{en:en,ex:ex};
  }

  return _sigOfOrig(sp,b);
}} // end if(false) dead block

// ---- FX-specific BASE specs ----
// T3/T7 have no signal-based exit; use hold-N exits so bt2 closes positions
const BASE_FX=[
  // T3 session divergence — hold 4-8 H1 bars (4-8 hours)
  {k:"T3",n:1,dow:0,x:{hold:4}},{k:"T3",n:1,dow:0,x:{hold:8}},
  {k:"T3",n:2,dow:0,x:{hold:4}},{k:"T3",n:2,dow:0,x:{hold:8}},
  {k:"T3",n:1,dow:1,x:{hold:4}},{k:"T3",n:1,dow:1,x:{hold:8}},
  // T7 ATR compression breakout — hold 4-8 H1 bars
  {k:"T7",atr_pct:80,rk_n:20,brk_n:10,x:{hold:4}},
  {k:"T7",atr_pct:80,rk_n:20,brk_n:10,x:{hold:8}},
  {k:"T7",atr_pct:70,rk_n:20,brk_n:10,x:{hold:4}},
  {k:"T7",atr_pct:80,rk_n:30,brk_n:10,x:{hold:4}},
  {k:"T7",atr_pct:80,rk_n:20,brk_n:15,x:{hold:4}},
  // RSI/CCI FX-tuned (signal-based exit — no hold needed)
  {k:"RSI",n:7,lo:25,hi:55},
  {k:"RSI",n:10,lo:28,hi:58},
  {k:"RSI",n:21,lo:32,hi:60},
  {k:"CCI",n:10,lo:80,hi:100},
  {k:"CCI",n:14,lo:90,hi:100},
  {k:"STD",n:5,s:3,lo:20,hi:75},
  {k:"STD",n:8,s:3,lo:22,hi:75},
];

// ---- extend neighbours() to handle T3/T7 variation ----
var _nbOrig=neighbours;
neighbours=function(sp){
  if(sp.k==="T3"){
    return[
      Object.assign({},sp,{n:Math.max(1,sp.n-1)}),
      Object.assign({},sp,{n:sp.n+1}),
    ].filter(function(s){return s.n>=1&&s.n<=3});
  }
  if(sp.k==="T7"){
    return[
      Object.assign({},sp,{atr_pct:Math.max(60,sp.atr_pct-10)}),
      Object.assign({},sp,{atr_pct:Math.min(95,sp.atr_pct+10)}),
      Object.assign({},sp,{brk_n:Math.max(5,sp.brk_n-5)}),
      Object.assign({},sp,{brk_n:sp.brk_n+5}),
    ];
  }
  return _nbOrig(sp);
};

// ---- series loading (identical to w2_node.js) ----
const NEW=typeof BASE2!=='undefined',T3=typeof tierOf==='function',T4=m.indexOf('function memGet(')>=0,T5=typeof BASE4!=='undefined';
const S=[],seen={},BAD={};
function add(s,tf,arr,src,cls){var b=arr.map(nb).filter(Boolean);if(b.length<150||seen[s+"|"+tf])return;seen[s+"|"+tf]=1;var mx=0;for(var i=1;i<b.length;i++){var d=Math.abs(b[i].c/b[i-1].c-1);if(d>mx)mx=d}if(mx>0.25){BAD[s+" "+tf]=(mx*100).toFixed(0)+"%";return}S.push({s:s,tf:tf,m:TFM[tf]||60,b:b,src:src,cls:cls})}
const HL=JSON.parse(fs.readFileSync(seedF,'utf8'));Object.keys(HL).forEach(k=>{const p=k.split('|');if(Array.isArray(HL[k]))add(p[0],p[1],HL[k],'hl')});
const extF=process.env.W2_EXT||'data/slc_win2_ext.json';if(!process.env.W2_NOEXT&&fs.existsSync(extF)){const EX=JSON.parse(fs.readFileSync(extF,'utf8'));Object.keys(EX).forEach(k=>{const p=k.split('|'),e=EX[k];if(e&&Array.isArray(e.b)&&p.length===2)add(p[0],p[1],e.b,e.src||'ext',e.cls)})}
const h=fs.readFileSync(page,'utf8');const i0=h.indexOf('var BARS_S=')+'var BARS_S='.length;let d=0,i=i0;for(;i<h.length;i++){const ch=h[i];if(ch==='{')d++;else if(ch==='}'){d--;if(d===0)break}}
const BS=JSON.parse(h.slice(i0,i+1));Object.keys(BS).forEach(s=>{const b=BS[s].map(nb).filter(Boolean);if(b.length<150)return;let mx=0;for(let j=1;j<b.length;j++){const q=Math.abs(b[j].c/b[j-1].c-1);if(q>mx)mx=q}if(mx>0.25){BAD[s]=(mx*100).toFixed(0)+"%";return}add(s,"M60",b,"emb");add(s,"M120",rs(b,120),"emb");add(s,"H4",rs(b,240),"emb")});

// ---- generation (mirror of runAll, BASE augmented with BASE_FX) ----
const t0=Date.now();let all=[],nJobs=0;
function run(specs,label){const o=[];specs.forEach(sp=>S.forEach(se=>o.push(metrics(sp,se))));nJobs+=o.length;all=all.concat(o);console.error(label+': '+specs.length+' specs x '+S.length+' series = '+o.length+' backtests ('+(Date.now()-t0)+' ms)');return o}

// Merge BASE_FX into BASE before generation (augment, do not replace)
const BASE_ALL=BASE.concat(typeof BASE2!=='undefined'?BASE2:[],typeof BASE3!=='undefined'?BASE3:[],typeof BASE4!=='undefined'?BASE4:[],BASE_FX);

let A=BASE_ALL.concat.apply(BASE_ALL,BASE_ALL.map(neighbours));
A=uniqSpecs(A);
const rA=run(A,'Gen A (BASE+FX)');

const topG=T3?tierTop(rA,0,12).concat(tierTop(rA,1,8),tierTop(rA,2,6)):NEW?topSpecs(rA.filter(r=>isLeg(r.spec)),12).concat(topSpecs(rA.filter(r=>!isLeg(r.spec)),8)):topSpecs(rA,12);
let top=topG,BGN={};
if(T4){const TFS={};S.forEach(se=>TFS[se.tf]=1);let topX=[];Object.keys(TFS).forEach(tf=>{const rT=rA.filter(r=>r.tf===tf);topX=topX.concat(tierTop(rT,0,3),tierTop(rT,1,2),tierTop(rT,2,1))});let top4=[];if(T5){top4=tierTop(rA,3,6);Object.keys(TFS).forEach(tf=>{top4=top4.concat(tierTop(rA.filter(r=>r.tf===tf),3,1))})}top=uniqSpecs(topG.concat(topX,top4))}

let B=[];top.forEach(sp=>{const g=topG.indexOf(sp)>=0;(T5?EXITS.concat(EXITS2,EXITS3,EXITS4):T3?EXITS.concat(EXITS2,EXITS3):NEW?EXITS.concat(EXITS2):EXITS).forEach(x=>{const c=JSON.parse(JSON.stringify(sp));c.x=x;B.push(c);if(g)BGN[nm(c)]=1})});const rB=run(uniqSpecs(B),'Gen B');
let Cm=[];const tg4=T5?topG.concat(tierTop(rA,3,6)):topG;for(let p=0;p<tg4.length;p++)for(let q=p+1;q<tg4.length;q++)Cm.push({k:"MIX",a:tg4[p],b:tg4[q],w:3});const rC=run(Cm,'Gen C');

const rBG=rB.filter(r=>BGN[r.sig]);
let D=[],seed=T4?top.concat(tierUpTo(rBG,0,6),tierUpTo(rC,0,4),tierUpTo(rBG,1,6),tierUpTo(rC,1,4),topSpecs(rBG,6),topSpecs(rC,4),topSpecs(rB,6),T5?tierUpTo(rB,3,6):[],T5?tierUpTo(rC,3,4):[]):T3?top.concat(tierUpTo(rB,0,6),tierUpTo(rC,0,4),tierUpTo(rB,1,6),tierUpTo(rC,1,4),topSpecs(rB,6),topSpecs(rC,4)):NEW?top.concat(topSpecs(rB.filter(r=>isLeg(r.spec)),6),topSpecs(rC.filter(r=>isLeg(r.spec)),4),topSpecs(rB,6),topSpecs(rC,4)):top.concat(topSpecs(rB,6),topSpecs(rC,4));
seed.forEach(sp=>(T5?REGS2.concat(REGS3,REGS4):T3?REGS2.concat(REGS3):NEW?REGS2:["quiet","trend"]).forEach(rg=>{const c=JSON.parse(JSON.stringify(sp));c.reg=rg;D.push(c)}));const rD=run(uniqSpecs(D),'Gen D');

// ---- fin() mirror ----
const win=all.filter(passes);win.sort((a,b)=>(b.hwp-a.hwp)||(b.wp-a.wp)||(T3?(tierOf(a.spec)-tierOf(b.spec)):NEW?((isLeg(b.spec)?1:0)-(isLeg(a.spec)?1:0)):0));
const sn={},uniq=[];win.forEach(r=>{const k=r.s+"|"+r.tf+"|"+r.ent;if(sn[k])return;sn[k]=1;uniq.push(r)});
const idx={};uniq.forEach(r=>{const k=r.sig+"|"+r.s+"|"+r.tf;if(!idx[k])idx[k]=r});
const winners=Object.keys(idx).map(k=>idx[k]).sort((a,b)=>(b.hwp-a.hwp)||(b.wp-a.wp)).slice(0,+process.env.W2_CAP||5000).map(r=>({key:r.sig+"|"+r.s+"|"+r.tf,sig:r.sig,spec:r.spec,s:r.s,tf:r.tf,cls:r.cls,src:r.src,t:r.t,w:r.w,wp:+r.wp.toFixed(1),g:+r.g.toFixed(2),k:+r.k.toFixed(2),x:+r.x.toFixed(2),a:+r.a.toFixed(2),mdd:+r.mdd.toFixed(2),add:+r.add.toFixed(2),tdd:+r.tdd.toFixed(2),hmdd:+r.hmdd.toFixed(2),acm:+r.acm.toFixed(3),afe:+r.afe.toFixed(3),asp:+r.asp.toFixed(3),asw:+r.asw.toFixed(4),atx:+r.atx.toFixed(3),ht:r.ht,hwp:+r.hwp.toFixed(1),hnet:+r.hnet.toFixed(2),ha:+r.ha.toFixed(2),avgb:+r.avgb.toFixed(1),ddok:r.ddok==null?null:!!r.ddok,ent:r.ent,leg:NEW?isLeg(r.spec):true,tier:T3?tierOf(r.spec):(NEW?(isLeg(r.spec)?0:1):0)}));
const byTf={};all.forEach(r=>{const o=byTf[r.tf]=byTf[r.tf]||{n:0,w:0,u:0};o.n++;if(passes(r))o.w++});uniq.forEach(r=>byTf[r.tf].u++);
const res={engine:mod,when:new Date().toISOString(),ms:Date.now()-t0,series:S.length,bad:BAD,jobs:nJobs,passes:win.length,uniq:uniq.length,clones:win.length-uniq.length,inMemory:winners.length,byTf:byTf,costs:COSTS,winners:winners,BASE_FX_seeds:BASE_FX.length};
fs.writeFileSync(out,JSON.stringify(res));
console.log(JSON.stringify({engine:mod,series:S.length,jobs:nJobs,passes:win.length,uniq:uniq.length,inMemory:winners.length,ms:res.ms,byTf:byTf,bad:BAD,BASE_FX_seeds:BASE_FX.length}));

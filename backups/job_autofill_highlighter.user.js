// ==UserScript==
// @name         Job Form Autofill + Keyword Highlighter v2
// @namespace    https://github.com/EndoScorpion
// @version      2.0.0
// @description  Auto-fill forms, highlight + tag keywords, track history, keyword cloud
// @author       EndoScorpion
// @match        *://www.indeed.com/*
// @match        *://www.ziprecruiter.com/*
// @match        *://www.linkedin.com/*
// @match        *://careers.*.com/*
// @match        *://jobs.*.com/*
// @match        *://*/*apply*
// @match        *://*/*job*
// @match        file:///*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// ==/UserScript==

(function () {
  'use strict';

  // ─── RESUME DATA ──────────────────────────────────────────────────────────
  const RESUME = {
    name:    'EndoScorpion',
    email:   'endoscorpion@gmail.com',
    phone:   '9045244100',
    location:'',
    github:  'https://github.com/EndoScorpion',
    website: '',
    summary: 'Algorithmic trading systems developer with expertise in Python, MQL4/MQL5, and automated backtesting frameworks.',
    education: '',
    experience: '5+',
    resumeText: `
      Algorithmic trading systems developer. Expertise in MQL4/MQL5 Expert Advisors,
      backtesting frameworks, Python, pandas, numpy, scipy, yfinance.
      Signal processing, technical analysis, EURUSD forex strategies.
      JavaScript, Tampermonkey, HTML, CSS, automation, data pipelines.
      Git, GitHub, CI/CD, Linux, Windows, MT4/MT5.
      Financial data analysis, pattern recognition, risk management.
      Node.js, bash scripting, REST APIs, JSON.
    `,
    skills: [
      'Python','pandas','numpy','scipy','yfinance',
      'JavaScript','HTML','CSS','Node.js',
      'MQL4','MQL5','MT4','MT5','MetaTrader',
      'algorithmic trading','backtesting','forex','EURUSD',
      'technical analysis','risk management','data analysis',
      'Git','GitHub','Linux','bash','REST API','JSON',
      'automation','signal processing','CI/CD',
      'Excel','SQL','matplotlib',
    ],
  };

  // ─── GENERIC TECH KEYWORDS (gap detection) ────────────────────────────────
  const GENERIC_TECH = [
    'React','Vue','Angular','TypeScript','GraphQL','Docker','Kubernetes',
    'AWS','Azure','GCP','Terraform','Ansible','Jenkins','CircleCI',
    'PostgreSQL','MongoDB','Redis','Elasticsearch','Kafka',
    'machine learning','deep learning','NLP','LLM','OpenAI',
    'Agile','Scrum','Kanban','JIRA','Confluence',
    'C\\+\\+','Java','Rust','Go','Swift','Kotlin','Ruby','PHP',
    'PyTorch','Keras','scikit-learn','XGBoost','Spark','Hadoop',
    'Tableau','Power BI','Looker','dbt','Airflow',
    'microservices','serverless','API gateway','OAuth','JWT',
  ];

  // ─── CUSTOM HTML ELEMENT DEFINITIONS ─────────────────────────────────────
  // <kw-match> = resume match (green)
  // <kw-gap>   = skill gap (amber)
  // <kw-hot>   = trending hot keyword (red/orange, seen across multiple jobs)
  if (!customElements.get('kw-match')) customElements.define('kw-match', class extends HTMLElement {});
  if (!customElements.get('kw-gap'))   customElements.define('kw-gap',   class extends HTMLElement {});
  if (!customElements.get('kw-hot'))   customElements.define('kw-hot',   class extends HTMLElement {});

  // ─── LOCALSTORAGE HISTORY ─────────────────────────────────────────────────
  const STORE_KEY = 'job_kw_history_v2';

  function loadHistory() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || '{}'); } catch { return {}; }
  }

  function saveHistory(h) {
    localStorage.setItem(STORE_KEY, JSON.stringify(h));
  }

  function recordKeywords(kwList) {
    const h = loadHistory();
    const today = new Date().toISOString().slice(0,10);
    kwList.forEach(kw => {
      const k = kw.toLowerCase();
      if (!h[k]) h[k] = { count: 0, lastSeen: today, firstSeen: today, dates: [] };
      h[k].count++;
      h[k].lastSeen = today;
      if (!h[k].dates.includes(today)) h[k].dates.push(today);
    });
    saveHistory(h);
    return h;
  }

  function getHotKeywords(h, minCount = 2) {
    return Object.entries(h)
      .filter(([,v]) => v.count >= minCount)
      .sort((a,b) => b[1].count - a[1].count)
      .map(([k]) => k);
  }

  // ─── RESUME KEYWORD EXTRACTION ────────────────────────────────────────────
  function extractResumeKeywords() {
    const words = new Set(RESUME.skills.map(s => s.toLowerCase()));
    const tokens = RESUME.resumeText.match(/\b[A-Za-z][A-Za-z0-9+#\-\.]{2,}\b/g) || [];
    tokens.forEach(t => { if (t.length > 3) words.add(t.toLowerCase()); });
    return [...words];
  }

  const resumeKeywords = extractResumeKeywords();

  // ─── FIELD AUTOFILL ───────────────────────────────────────────────────────
  const FIELD_MAP = [
    { keys: ['first.*name','fname','given'], value: () => RESUME.name.split(' ')[0] || RESUME.name },
    { keys: ['last.*name','lname','surname','family'], value: () => RESUME.name.split(' ').slice(1).join(' ') || RESUME.name },
    { keys: ['full.*name','your.*name','^name$'], value: () => RESUME.name },
    { keys: ['email','e-mail'], value: () => RESUME.email },
    { keys: ['phone','mobile','cell','telephone'], value: () => RESUME.phone },
    { keys: ['location','city','address','zip','postal'], value: () => RESUME.location },
    { keys: ['linkedin'], value: () => '' },
    { keys: ['github','portfolio','website','url'], value: () => RESUME.website || RESUME.github },
    { keys: ['years.*exp','experience.*years','how.*many.*years'], value: () => RESUME.experience },
    { keys: ['summary','objective','about','cover','intro'], value: () => RESUME.summary },
    { keys: ['education','degree','university','college','school'], value: () => RESUME.education },
    { keys: ['skills','competenc','technolog'], value: () => RESUME.skills.join(', ') },
  ];

  function matchesKey(str, keys) {
    const s = str.toLowerCase().replace(/[_\-\s]+/g,'');
    return keys.some(k => new RegExp(k.replace(/\s/g,'')).test(s));
  }

  function fillField(el, value) {
    if (!value) return;
    const tag = el.tagName.toLowerCase();
    if (tag === 'select') {
      for (const opt of el.options) {
        if (opt.text.toLowerCase().includes(value.toLowerCase())) {
          opt.selected = true; el.dispatchEvent(new Event('change',{bubbles:true})); return;
        }
      }
      return;
    }
    if (tag === 'textarea' || (tag === 'input' && !['checkbox','radio','file','submit','button'].includes(el.type))) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value') ||
                           Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value');
      if (nativeSetter?.set) nativeSetter.set.call(el, value);
      else el.value = value;
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change',{bubbles:true}));
    }
  }

  function getLabel(el) {
    if (el.id) { const l = document.querySelector(`label[for="${el.id}"]`); if (l) return l.textContent.trim(); }
    return el.getAttribute('aria-label') || el.placeholder || el.name || el.closest('label')?.textContent.trim() || '';
  }

  function autofillForms() {
    let filled = 0;
    document.querySelectorAll('input,textarea,select').forEach(el => {
      const label = getLabel(el);
      if (!label) return;
      for (const rule of FIELD_MAP) {
        if (matchesKey(label, rule.keys)) {
          fillField(el, rule.value());
          filled++;
          el.style.outline = '2px solid #00e676';
          break;
        }
      }
    });
    return filled;
  }

  // ─── KEYWORD HIGHLIGHT + TAG INJECTION ────────────────────────────────────
  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

  const SKIP_TAGS = new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','INPUT','SELECT',
                              'KW-MATCH','KW-GAP','KW-HOT','MARK','CODE','PRE']);

  function wrapInTag(node, re, tagName) {
    const text = node.nodeValue;
    re.lastIndex = 0;
    if (!re.test(text)) return [];
    re.lastIndex = 0;
    const frag = document.createDocumentFragment();
    const found = [];
    let last = 0, m;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      const el = document.createElement(tagName);
      el.textContent = m[0];
      frag.appendChild(el);
      found.push(m[0].toLowerCase());
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    node.parentNode.replaceChild(frag, node);
    return found;
  }

  function highlightJobPosting() {
    const h = loadHistory();
    const hotKws = getHotKeywords(h, 2);

    // Build regexes: hot first (highest priority), then resume match, then generic gap
    const notInResume = GENERIC_TECH.filter(k => !resumeKeywords.includes(k.toLowerCase()));
    const reHot    = hotKws.length ? new RegExp(`\\b(${hotKws.map(escapeRe).join('|')})\\b`, 'gi') : null;
    const reResume = new RegExp(`\\b(${[...RESUME.skills].sort((a,b)=>b.length-a.length).map(escapeRe).join('|')})\\b`, 'gi');
    const reGap    = new RegExp(`\\b(${notInResume.sort((a,b)=>b.length-a.length).map(escapeRe).join('|')})\\b`, 'gi');

    const jobBody = document.querySelector(
      '[class*="job-desc"],[class*="jobDescription"],[class*="description"],' +
      '[id*="job-desc"],[id*="jobDescription"],main,article,.content'
    ) || document.body;

    const walker = document.createTreeWalker(jobBody, NodeFilter.SHOW_TEXT, {
      acceptNode: n => SKIP_TAGS.has(n.parentElement?.tagName) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    const nodes = [];
    let n;
    while ((n = walker.nextNode())) nodes.push(n);

    const allFound = [];
    nodes.forEach(node => {
      if (reHot && reHot.test(node.nodeValue)) {
        reHot.lastIndex = 0;
        const found = wrapInTag(node, reHot, 'kw-hot');
        allFound.push(...found);
      } else if (reResume.test(node.nodeValue)) {
        reResume.lastIndex = 0;
        const found = wrapInTag(node, reResume, 'kw-match');
        allFound.push(...found);
      } else if (reGap.test(node.nodeValue)) {
        reGap.lastIndex = 0;
        wrapInTag(node, reGap, 'kw-gap');
      }
    });

    // Record found keywords to history + log this job post
    if (allFound.length) {
      recordKeywords(allFound);
      const jobText = (document.body.innerText||'').toLowerCase();
      const matched = RESUME.skills.filter(k => jobText.includes(k.toLowerCase()));
      const pct = Math.round(matched.length / RESUME.skills.length * 100);
      logJobPost(allFound, pct);
    }

    return {
      matches: document.querySelectorAll('kw-match').length,
      gaps:    document.querySelectorAll('kw-gap').length,
      hot:     document.querySelectorAll('kw-hot').length,
    };
  }

  // ─── JOB POST HISTORY LOG ────────────────────────────────────────────────
  const JOB_LOG_KEY = 'job_post_history_v2';

  function extractJobMeta() {
    const title = (
      document.querySelector('h1,h2,[class*="job-title"],[class*="jobTitle"],[data-testid*="title"]')?.textContent ||
      document.title || 'Unknown Title'
    ).trim().slice(0, 120);
    const company = (
      document.querySelector('[class*="company"],[class*="employer"],[data-testid*="company"]')?.textContent || ''
    ).trim().slice(0, 80);
    return { title, company, url: location.href.slice(0, 200) };
  }

  function logJobPost(matchedKws, matchPct) {
    const meta = extractJobMeta();
    const entry = {
      date: new Date().toISOString().slice(0,10),
      time: new Date().toTimeString().slice(0,5),
      title: meta.title,
      company: meta.company,
      url: meta.url,
      matchPct,
      keywords: matchedKws.slice(0,30),
    };
    const log = JSON.parse(localStorage.getItem(JOB_LOG_KEY) || '[]');
    log.unshift(entry);
    if (log.length > 500) log.length = 500;
    localStorage.setItem(JOB_LOG_KEY, JSON.stringify(log));
    return entry;
  }

  function exportJobLogTxt() {
    const log = JSON.parse(localStorage.getItem(JOB_LOG_KEY) || '[]');
    if (!log.length) { alert('No job history yet.'); return; }
    const lines = log.map(e =>
      `[${e.date} ${e.time}] ${e.company ? e.company + ' — ' : ''}${e.title}\n` +
      `  Match: ${e.matchPct}% | Keywords: ${e.keywords.join(', ')}\n` +
      `  URL: ${e.url}\n`
    );
    const txt = `JOB POST HISTORY — ${log.length} entries\n${'='.repeat(60)}\n\n` + lines.join('\n');
    const a = document.createElement('a');
    a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(txt);
    a.download = `job_history_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
  }

  // ─── KEYWORD CLOUD ────────────────────────────────────────────────────────
  function buildKeywordCloud(container) {
    const h = loadHistory();
    const entries = Object.entries(h).sort((a,b) => b[1].count - a[1].count).slice(0, 60);
    if (!entries.length) { container.textContent = 'No keyword history yet.'; return; }
    const maxCount = entries[0][1].count;
    container.innerHTML = '';
    entries.forEach(([kw, data]) => {
      const size = 10 + Math.round((data.count / maxCount) * 22);
      const isMatch = resumeKeywords.includes(kw);
      const color = isMatch ? '#00e676' : '#ffd740';
      const span = document.createElement('span');
      span.textContent = kw;
      span.title = `Seen ${data.count}× | First: ${data.firstSeen} | Last: ${data.lastSeen}`;
      span.style.cssText = `font-size:${size}px;color:${color};margin:3px 6px;display:inline-block;cursor:default;opacity:0.9;`;
      container.appendChild(span);
    });
  }

  // ─── INDEX PAGE BUTTON ────────────────────────────────────────────────────
  function openIndexPage() {
    const h = loadHistory();
    const rows = Object.entries(h)
      .sort((a,b) => b[1].count - a[1].count)
      .map(([kw, data]) => {
        const isMatch = resumeKeywords.includes(kw) ? '✓' : '—';
        return `<tr>
          <td>${kw}</td>
          <td>${data.count}</td>
          <td>${isMatch}</td>
          <td>${data.firstSeen}</td>
          <td>${data.lastSeen}</td>
          <td>${(data.dates||[]).length}</td>
        </tr>`;
      }).join('');
    const jobLog = JSON.parse(localStorage.getItem(JOB_LOG_KEY) || '[]');
    const logRows = jobLog.slice(0,100).map(e =>
      `<tr><td>${e.date} ${e.time}</td><td>${e.company||'—'}</td><td>${e.title}</td>` +
      `<td>${e.matchPct}%</td><td>${(e.keywords||[]).slice(0,8).join(', ')}</td></tr>`
    ).join('');
    const html = `<!DOCTYPE html><html><head><title>Job Keyword Index</title>
    <style>
      body{background:#111;color:#eee;font:13px monospace;padding:20px}
      h1{color:#00e676}
      table{border-collapse:collapse;width:100%}
      th{background:#222;color:#ffd740;padding:8px;text-align:left;border-bottom:1px solid #333}
      td{padding:6px 8px;border-bottom:1px solid #222}
      tr:hover td{background:#1e1e1e}
      .cloud{margin:20px 0;padding:16px;background:#161616;border-radius:8px;line-height:2.2}
    </style></head><body>
    <h1>📊 Job Keyword Index</h1>
    <p>Tracking ${Object.keys(h).length} keywords from your job search history.</p>
    <div class="cloud" id="cloud"></div>
    <table><thead><tr>
      <th>Keyword</th><th>Count</th><th>Resume?</th><th>First Seen</th><th>Last Seen</th><th>Job Days</th>
    </tr></thead><tbody>${rows}</tbody></table>
    <h2 style="color:#ffd740;margin-top:24px">📝 Job Post History (last 100)</h2>
    <table><thead><tr>
      <th>Date/Time</th><th>Company</th><th>Title</th><th>Match%</th><th>Keywords (sample)</th>
    </tr></thead><tbody>${logRows}</tbody></table>
    <script>
      const h = ${JSON.stringify(h)};
      const rk = ${JSON.stringify(resumeKeywords)};
      const entries = Object.entries(h).sort((a,b)=>b[1].count-a[1].count).slice(0,60);
      const max = entries[0]?.[1].count||1;
      const cloud = document.getElementById('cloud');
      entries.forEach(([kw,data])=>{
        const size=10+Math.round((data.count/max)*22);
        const color=rk.includes(kw)?'#00e676':'#ffd740';
        const s=document.createElement('span');
        s.textContent=kw;s.title='Seen '+data.count+'×';
        s.style.cssText='font-size:'+size+'px;color:'+color+';margin:3px 8px;display:inline-block;cursor:default;';
        cloud.appendChild(s);
      });
    <\/script></body></html>`;
    const w = window.open('', '_blank');
    w.document.write(html);
    w.document.close();
  }

  // ─── STYLES ───────────────────────────────────────────────────────────────
  GM_addStyle(`
    kw-match {
      background: #00e67633;
      border-bottom: 2px solid #00e676;
      border-radius: 2px;
      padding: 0 1px;
      cursor: help;
    }
    kw-match::after { content: '✓'; font-size: 0.65em; color: #00e676; vertical-align: super; margin-left:1px; }
    kw-gap {
      background: #ffd74033;
      border-bottom: 2px solid #ffd740;
      border-radius: 2px;
      padding: 0 1px;
    }
    kw-gap::after { content: '?'; font-size: 0.65em; color: #ffd740; vertical-align: super; margin-left:1px; }
    kw-hot {
      background: #ff6d0033;
      border-bottom: 2px solid #ff6d00;
      border-radius: 3px;
      padding: 0 2px;
      font-weight: bold;
    }
    kw-hot::after { content: '🔥'; font-size: 0.65em; vertical-align: super; margin-left:1px; }
    #jab-panel {
      position: fixed; bottom: 20px; right: 20px; z-index: 999999;
      background: #1a1a2e; color: #eee; border: 1px solid #444;
      border-radius: 10px; padding: 12px 16px; font: 12px/1.6 monospace;
      min-width: 240px; box-shadow: 0 4px 24px rgba(0,0,0,0.6);
    }
    #jab-panel h4 { margin: 0 0 8px; color: #00e676; font-size: 13px; }
    #jab-panel button {
      display: block; width: 100%; margin: 3px 0; padding: 5px 10px;
      background: #263238; color: #eee; border: 1px solid #555;
      border-radius: 5px; cursor: pointer; font: 11px monospace; text-align: left;
    }
    #jab-panel button:hover { background: #37474f; }
    #jab-status { font-size: 11px; color: #aaa; margin-top: 6px; min-height: 16px; }
    #jab-cloud { margin-top: 8px; border-top: 1px solid #333; padding-top: 8px; line-height: 1.8; max-height: 100px; overflow-y:auto; }
    #jab-legend { font-size: 10px; margin-top: 6px; border-top: 1px solid #333; padding-top:6px; }
    #jab-legend span { display: block; }
    #jab-toggle { float:right; cursor:pointer; color:#666; font-size:14px; }
  `);

  // ─── FLOATING PANEL ───────────────────────────────────────────────────────
  function buildPanel() {
    const panel = document.createElement('div');
    panel.id = 'jab-panel';
    panel.innerHTML = `
      <h4>🤖 Job Assistant <span id="jab-toggle">▼</span></h4>
      <div id="jab-body">
        <button id="btn-fill">⚡ Auto-fill Form</button>
        <button id="btn-hl">🏷️ Tag &amp; Highlight</button>
        <button id="btn-both">▶ Do Both</button>
        <button id="btn-score">📊 Match Score</button>
        <button id="btn-index">📋 Open Keyword Index</button>
        <button id="btn-export">💾 Export Job History (.txt)</button>
        <div id="jab-status">Ready.</div>
        <div id="jab-cloud"></div>
        <div id="jab-legend">
          <span style="color:#00e676">■ &lt;kw-match&gt; Resume match ✓</span>
          <span style="color:#ffd740">■ &lt;kw-gap&gt; Skill gap ?</span>
          <span style="color:#ff6d00">■ &lt;kw-hot&gt; Trending 🔥</span>
        </div>
      </div>
    `;
    document.body.appendChild(panel);

    // Collapse toggle
    document.getElementById('jab-toggle').onclick = () => {
      const body = document.getElementById('jab-body');
      body.style.display = body.style.display === 'none' ? '' : 'none';
    };

    const status = el => { document.getElementById('jab-status').textContent = el; };

    document.getElementById('btn-fill').onclick = () => {
      status(`Filled ${autofillForms()} field(s).`);
    };

    document.getElementById('btn-hl').onclick = () => {
      const r = highlightJobPosting();
      status(`${r.matches} matches · ${r.gaps} gaps · ${r.hot} hot`);
      buildKeywordCloud(document.getElementById('jab-cloud'));
    };

    document.getElementById('btn-both').onclick = () => {
      const n = autofillForms();
      const r = highlightJobPosting();
      status(`Filled ${n} · ${r.matches} match · ${r.gaps} gap · ${r.hot} hot`);
      buildKeywordCloud(document.getElementById('jab-cloud'));
    };

    document.getElementById('btn-score').onclick = () => {
      const jobText = (document.body.innerText||'').toLowerCase();
      const matched = RESUME.skills.filter(k => jobText.includes(k.toLowerCase()));
      const pct = Math.round(matched.length / RESUME.skills.length * 100);
      status(`Match ${pct}% — ${matched.length}/${RESUME.skills.length} skills`);
    };

    document.getElementById('btn-index').onclick = openIndexPage;
    document.getElementById('btn-export').onclick = exportJobLogTxt;

    // Initial mini cloud from history
    buildKeywordCloud(document.getElementById('jab-cloud'));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildPanel);
  } else {
    buildPanel();
  }

})();

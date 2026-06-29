"""
api.py — FastAPI Gateway | Heuristic OS V3.1
AquaHeuristic Platform
"""

from __future__ import annotations

import logging
import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator

from brain import ConceptReport, process_concept

# ── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── APP ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Heuristic OS",
    version="3.1.0",
    description="Strategic Heuristic Analysis Engine — AquaHeuristic Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── UI ─────────────────────────────────────────────────────────────────────
UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Heuristic OS — V3.1 | AquaHeuristic</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#060810;--surface:#080D18;--surface-2:#0A1020;--terminal:#03050B;
      --border:#162035;--border-lit:#1F2F48;--brand:#5F57FF;--brand-soft:#8B83FF;
      --brand-dim:#3A33CC;--brand-bg:rgba(95,87,255,.10);--green:#00D68F;
      --green-bg:rgba(0,214,143,.08);--orange:#FF8C42;--red:#FF5470;
      --text-1:#EEF4FF;--text-2:#C8D8EC;--text-3:#4A6280;--text-4:#253040;--text-5:#162035;
    }
    html,body{height:100%}
    body{background:var(--bg);color:var(--text-2);font-family:'JetBrains Mono','Courier New',monospace;font-size:13px;line-height:1.6;min-height:100vh;overflow-x:hidden}
    body::before{content:'';position:fixed;inset:0;z-index:0;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:52px 52px;opacity:.3;pointer-events:none}
    @keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
    @keyframes shimmer{from{left:-50%}to{left:120%}}
    @keyframes scan{0%{top:0;opacity:.7}90%{opacity:.7}100%{top:100%;opacity:0}}
    .blink{animation:blink 1.1s step-end infinite}
    .pulse{animation:pulse 2.2s ease-in-out infinite}
    .pulse2{animation:pulse 2.2s ease-in-out .5s infinite}
    .pulse3{animation:pulse 2.2s ease-in-out 1s infinite}
    .pulse4{animation:pulse 2.2s ease-in-out 1.5s infinite}
    nav{position:sticky;top:0;z-index:100;height:54px;background:rgba(6,8,16,.92);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);padding:0 28px;display:flex;align-items:center;justify-content:space-between}
    .nav-brand{display:flex;align-items:center;gap:12px}
    .brand-ring{position:relative;width:14px;height:14px;display:flex;align-items:center;justify-content:center}
    .brand-ring-core{width:8px;height:8px;border-radius:50%;background:var(--brand);position:absolute}
    .brand-ring-orbit{width:14px;height:14px;border-radius:50%;border:1px solid var(--brand);position:absolute;opacity:.35;animation:pulse 2.2s ease-in-out infinite}
    .brand-name{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:16px;letter-spacing:.12em;color:var(--text-1)}
    .brand-name span{color:var(--brand)}
    .brand-badge{font-size:11px;padding:2px 9px;background:var(--brand-bg);border:1px solid rgba(95,87,255,.4);color:var(--brand-soft);border-radius:3px;letter-spacing:.08em}
    .brand-sub{font-size:11px;color:var(--text-4);letter-spacing:.04em}
    .nav-right{display:flex;align-items:center;gap:28px}
    .nav-kv{display:flex;flex-direction:column;align-items:flex-end}
    .nav-kv-lbl{font-size:10px;color:var(--text-4);letter-spacing:.12em;text-transform:uppercase;margin-bottom:1px}
    .nav-kv-val{font-size:11px;color:var(--text-3);letter-spacing:.04em}
    .nav-kv-val.green{color:var(--green)}
    .nav-kv-val.brand{color:var(--brand-soft)}
    .status-pill{display:flex;align-items:center;gap:7px;padding:5px 12px;background:var(--green-bg);border:1px solid rgba(0,214,143,.2);border-radius:4px}
    .status-dot{width:6px;height:6px;border-radius:50%;background:var(--green)}
    .status-pill span{font-size:11px;color:var(--green);letter-spacing:.08em}
    main{position:relative;z-index:1;max-width:1280px;margin:0 auto;padding:22px 28px 60px}
    .stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--border);border-radius:6px;overflow:hidden;margin-bottom:20px}
    .stat{background:var(--surface);padding:14px 22px;border-right:1px solid var(--border)}
    .stat:last-child{border-right:none}
    .stat-lbl{font-size:10px;color:var(--text-4);letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px}
    .stat-val{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:22px;color:var(--text-1)}
    .stat-val.brand{color:var(--brand-soft)}
    .stat-val.green{color:var(--green)}
    .stat-val.small{font-size:15px;padding-top:4px}
    .cmd-grid{display:grid;grid-template-columns:200px 1fr 1fr;border:1px solid var(--border);border-radius:6px;overflow:hidden;margin-bottom:14px;min-height:480px}
    .sidebar{border-right:1px solid var(--border);padding:14px;display:flex;flex-direction:column;gap:12px;background:rgba(8,13,24,.6)}
    .mini-panel{border:1px solid var(--border);border-radius:4px;overflow:hidden}
    .mini-hd{background:var(--surface-2);padding:5px 10px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
    .mini-hd-lbl{font-size:10px;color:var(--text-4);letter-spacing:.12em;text-transform:uppercase}
    .mini-hd-live{font-size:10px;color:var(--green)}
    .mini-body{background:var(--terminal);padding:9px 10px}
    canvas#wave{display:block;width:100%}
    .wave-foot{background:var(--surface-2);padding:4px 10px;display:flex;justify-content:space-between}
    .wave-foot span:first-child{font-size:10px;color:var(--text-4)}
    .wave-foot span:last-child{font-size:10px;color:var(--brand-soft)}
    .metric-row{margin-bottom:9px}
    .metric-row:last-child{margin-bottom:0}
    .metric-head{display:flex;justify-content:space-between;margin-bottom:3px}
    .metric-head span:first-child{font-size:10px;color:var(--text-3)}
    .metric-head span:last-child{font-size:10px}
    .bar-track{height:3px;background:var(--border);border-radius:2px}
    .bar-fill{height:3px;border-radius:2px;transition:width 1s ease}
    .node-row{display:flex;align-items:center;gap:7px;margin-bottom:8px}
    .node-row:last-child{margin-bottom:0}
    .node-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
    .node-lbl{font-size:10px;color:var(--text-3);flex:1}
    .node-val{font-size:10px}
    .input-col{border-right:1px solid var(--border);padding:14px;display:flex;flex-direction:column;gap:12px}
    .terminal-card{border:1px solid var(--border);border-radius:4px;overflow:hidden;flex:1;display:flex;flex-direction:column}
    .term-hd{background:var(--surface-2);padding:7px 14px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
    .term-hd-lbl{font-size:10px;color:var(--text-4);letter-spacing:.12em;text-transform:uppercase}
    .mac-dots{display:flex;gap:5px}
    .mac-dots span{width:10px;height:10px;border-radius:50%;display:block}
    .term-body{background:var(--terminal);padding:12px;flex:1;display:flex;flex-direction:column}
    .term-comment{font-size:11px;color:var(--text-4);margin-bottom:8px;letter-spacing:.04em}
    textarea#inp{flex:1;min-height:160px;background:transparent;border:none;outline:none;color:var(--text-1);resize:none;font-family:'JetBrains Mono','Courier New',monospace;font-size:13px;line-height:1.7;caret-color:var(--brand-soft);width:100%}
    textarea#inp::placeholder{color:var(--text-4)}
    .term-ft{background:var(--surface-2);padding:5px 14px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
    .term-hint{font-size:10px;color:var(--text-4)}
    .term-hint kbd{background:var(--border);border:1px solid var(--border-lit);padding:0 5px;border-radius:3px;font-family:inherit;font-size:9px;color:var(--text-3)}
    .btn{width:100%;padding:13px;background:var(--brand);color:#fff;border:none;border-radius:4px;font-family:'JetBrains Mono','Courier New',monospace;font-size:11px;font-weight:500;letter-spacing:.16em;cursor:pointer;position:relative;overflow:hidden;transition:background .2s}
    .btn:hover{background:var(--brand-dim)}
    .btn:active{transform:scale(.99)}
    .btn:disabled{opacity:.45;cursor:not-allowed}
    .btn-shim{position:absolute;top:0;height:100%;width:40%;background:rgba(255,255,255,.1);animation:shimmer 1.1s linear infinite}
    .err-box{margin-top:10px;padding:10px 14px;background:rgba(255,84,112,.07);border:1px solid rgba(255,84,112,.25);border-radius:4px;color:var(--red);font-size:11px;display:none}
    .err-box.show{display:block}
    .output-col{padding:14px;display:flex;flex-direction:column;gap:12px}
    .conf-card{border:1px solid var(--border);border-radius:4px;overflow:hidden}
    .conf-hd{background:var(--surface-2);padding:7px 14px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
    .conf-hd-lbl{font-size:10px;color:var(--text-4);letter-spacing:.12em;text-transform:uppercase}
    .status-tag{font-size:10px;padding:1px 8px;border:1px solid rgba(95,87,255,.3);color:var(--brand-soft);border-radius:3px;letter-spacing:.08em}
    .conf-body{background:var(--terminal);padding:14px;display:flex;align-items:center;gap:16px}
    .ring-wrap{position:relative;width:84px;height:84px;flex-shrink:0}
    .ring-svg{transform:rotate(-90deg);display:block}
    .ring-track{fill:none;stroke:var(--border-lit);stroke-width:5}
    .ring-arc{fill:none;stroke:var(--brand);stroke-width:5;stroke-linecap:round;stroke-dasharray:226.2;stroke-dashoffset:226.2;transition:stroke-dashoffset 1.5s cubic-bezier(.22,.61,.36,1)}
    .ring-center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
    .ring-num{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:16px;color:var(--text-1);line-height:1}
    .ring-sub{font-size:10px;color:var(--text-4);margin-top:2px;letter-spacing:.05em}
    .conf-meta{flex:1;display:flex;flex-direction:column;gap:7px}
    .meta-row{display:flex;justify-content:space-between;align-items:center}
    .meta-k{font-size:10px;color:var(--text-4);text-transform:uppercase;letter-spacing:.1em}
    .meta-v{font-size:11px;color:var(--text-3)}
    .meta-v.ok{color:var(--green)}
    .meta-v.bad{color:var(--red)}
    .out-card{border:1px solid var(--border);border-radius:4px;overflow:hidden;flex:1}
    .out-hd{background:var(--surface-2);padding:7px 14px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between}
    .out-hd-lbl{font-size:10px;color:var(--text-4);letter-spacing:.12em;text-transform:uppercase}
    .out-hd-hash{font-size:10px;color:var(--text-4);letter-spacing:.06em}
    .out-body{background:var(--terminal);padding:14px;position:relative;min-height:180px}
    .scan-line{position:absolute;left:0;right:0;height:1px;background:var(--brand);top:0;display:none;opacity:.6}
    .scan-line.active{display:block;animation:scan 1.5s linear infinite}
    pre#out{font-family:'JetBrains Mono','Courier New',monospace;font-size:11.5px;line-height:1.9;color:var(--text-4);white-space:pre-wrap;word-break:break-word}
    pre#out.done{color:var(--text-3)}
    .tele{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:8px 18px;display:flex;align-items:center;gap:4px;flex-wrap:wrap}
    .tk{font-size:10px;color:var(--text-4);text-transform:uppercase;letter-spacing:.1em}
    .tv{font-size:11px;color:var(--text-3);margin:0 10px 0 4px}
    .tv.ok{color:var(--green)}
    .tv.bad{color:var(--red)}
    .tsep{font-size:11px;color:var(--text-5)}
    @media(max-width:900px){.cmd-grid{grid-template-columns:1fr}.sidebar,.input-col{border-right:none;border-bottom:1px solid var(--border)}.stats{grid-template-columns:repeat(2,1fr)}}
  </style>
</head>
<body>
<nav>
  <div class="nav-brand">
    <div class="brand-ring"><div class="brand-ring-core"></div><div class="brand-ring-orbit"></div></div>
    <span class="brand-name">HEURISTIC<span>_OS</span></span>
    <span class="brand-badge">V3.1</span>
    <span class="brand-sub">&#9656; AQUAHEURISTIC PLATFORM</span>
  </div>
  <div class="nav-right">
    <div class="nav-kv"><span class="nav-kv-lbl">Uptime</span><span class="nav-kv-val" id="upt">00:00:00</span></div>
    <div class="nav-kv"><span class="nav-kv-lbl">Requests</span><span class="nav-kv-val green" id="rcount">0</span></div>
    <div class="nav-kv"><span class="nav-kv-lbl">UTC</span><span class="nav-kv-val" id="clk">--:--:--</span></div>
    <div class="nav-kv"><span class="nav-kv-lbl">Build</span><span class="nav-kv-val brand">563a65a</span></div>
    <div class="status-pill"><div class="status-dot pulse"></div><span>ONLINE</span></div>
  </div>
</nav>
<main>
  <div class="stats">
    <div class="stat"><div class="stat-lbl">Confidence Floor</div><div class="stat-val brand">98.4<span style="font-size:14px;color:var(--brand);">%</span></div></div>
    <div class="stat"><div class="stat-lbl">Engine Status</div><div class="stat-val green">ACTIVE</div></div>
    <div class="stat"><div class="stat-lbl">Target Latency</div><div class="stat-val">&lt;100<span style="font-size:14px;">ms</span></div></div>
    <div class="stat"><div class="stat-lbl">Architecture</div><div class="stat-val small">FastAPI &middot; Python 3.12 &middot; Render</div></div>
  </div>
  <div class="cmd-grid">
    <div class="sidebar">
      <div class="mini-panel">
        <div class="mini-hd"><span class="mini-hd-lbl">Signal Feed</span><span class="mini-hd-live blink">&#9679; LIVE</span></div>
        <div style="background:var(--terminal);padding:6px"><canvas id="wave" width="172" height="64"></canvas></div>
        <div class="wave-foot"><span>FREQ</span><span>432 Hz</span></div>
      </div>
      <div class="mini-panel">
        <div class="mini-hd"><span class="mini-hd-lbl">Sys Metrics</span></div>
        <div class="mini-body">
          <div class="metric-row"><div class="metric-head"><span>PROC_LOAD</span><span id="cpu-v" style="color:var(--green)">34%</span></div><div class="bar-track"><div id="cpu-b" class="bar-fill" style="background:var(--green);width:34%"></div></div></div>
          <div class="metric-row"><div class="metric-head"><span>MEM_ALLOC</span><span id="mem-v" style="color:var(--brand-soft)">61%</span></div><div class="bar-track"><div id="mem-b" class="bar-fill" style="background:var(--brand);width:61%"></div></div></div>
          <div class="metric-row"><div class="metric-head"><span>NET_IO</span><span id="net-v" style="color:var(--orange)">47%</span></div><div class="bar-track"><div id="net-b" class="bar-fill" style="background:var(--orange);width:47%"></div></div></div>
        </div>
      </div>
      <div class="mini-panel">
        <div class="mini-hd"><span class="mini-hd-lbl">Node Status</span></div>
        <div class="mini-body">
          <div class="node-row"><div class="node-dot pulse" style="background:var(--green)"></div><span class="node-lbl">API_GATEWAY</span><span class="node-val" style="color:var(--green)">OK</span></div>
          <div class="node-row"><div class="node-dot pulse2" style="background:var(--green)"></div><span class="node-lbl">HEUR_ENGINE</span><span class="node-val" style="color:var(--green)">OK</span></div>
          <div class="node-row"><div class="node-dot pulse3" style="background:var(--brand)"></div><span class="node-lbl">BRAIN_CORE</span><span class="node-val" style="color:var(--brand-soft)">PROC</span></div>
          <div class="node-row"><div class="node-dot pulse4" style="background:var(--green)"></div><span class="node-lbl">RENDER_HOST</span><span class="node-val" style="color:var(--green)">OK</span></div>
        </div>
      </div>
    </div>
    <div class="input-col">
      <div class="terminal-card">
        <div class="term-hd">
          <span class="term-hd-lbl">Input Terminal</span>
          <div class="mac-dots"><span style="background:var(--red)"></span><span style="background:#FFB800"></span><span style="background:var(--green)"></span></div>
        </div>
        <div class="term-body">
          <div class="term-comment">// Enter concept, strategy, or analysis target</div>
          <textarea id="inp" placeholder="Enter sequence&#8230;"></textarea>
        </div>
        <div class="term-ft">
          <span class="term-hint"><kbd>Ctrl</kbd> + <kbd>Enter</kbd> to execute</span>
          <span class="blink" style="font-size:14px;color:var(--brand-soft);line-height:1">&#9612;</span>
        </div>
      </div>
      <button id="btn" class="btn" onclick="run()">INITIALIZE_ANALYSIS</button>
      <div class="err-box" id="err"></div>
    </div>
    <div class="output-col">
      <div class="conf-card">
        <div class="conf-hd"><span class="conf-hd-lbl">Confidence Matrix</span><span class="status-tag" id="stag">IDLE</span></div>
        <div class="conf-body">
          <div class="ring-wrap">
            <svg class="ring-svg" width="84" height="84" viewBox="0 0 84 84">
              <circle class="ring-track" cx="42" cy="42" r="36"/>
              <circle class="ring-arc" cx="42" cy="42" r="36" id="ring"/>
            </svg>
            <div class="ring-center"><span class="ring-num" id="rnum">&#8212;</span><span class="ring-sub">CONF</span></div>
          </div>
          <div class="conf-meta">
            <div class="meta-row"><span class="meta-k">Depth</span><span class="meta-v">STRATEGIC_ANALYSIS</span></div>
            <div class="meta-row"><span class="meta-k">Server time</span><span class="meta-v" id="m-srv">&#8212;</span></div>
            <div class="meta-row"><span class="meta-k">Status</span><span class="meta-v" id="m-st">IDLE</span></div>
            <div class="meta-row"><span class="meta-k">Validated</span><span class="meta-v" id="m-val">&#8212;</span></div>
          </div>
        </div>
      </div>
      <div class="out-card">
        <div class="out-hd"><span class="out-hd-lbl">Heuristic Output</span><span class="out-hd-hash">POST /explain &middot; v3.1</span></div>
        <div class="out-body"><div class="scan-line" id="scan"></div><pre id="out">System ready. Awaiting input sequence&#8230;</pre></div>
      </div>
    </div>
  </div>
  <div class="tele">
    <span class="tk">Confidence</span><span class="tv" id="t-conf">[N/A]</span>
    <span class="tsep">&#9656;</span>
    <span class="tk">Server</span><span class="tv" id="t-srv">[&#8212;]</span>
    <span class="tsep">&#9656;</span>
    <span class="tk">Client RTT</span><span class="tv" id="t-rtt">[&#8212;]</span>
    <span class="tsep">&#9656;</span>
    <span class="tk">Status</span><span class="tv" id="t-st">IDLE</span>
    <span class="tsep">&#9656;</span>
    <span class="tk">Endpoint</span><span class="tv">POST /explain</span>
    <span class="tsep">&#9656;</span>
    <span class="tk">Core</span><span class="tv" style="color:var(--brand-soft)">HEURISTIC_CORE v3.1</span>
    <div style="margin-left:auto;display:flex;align-items:center;gap:6px">
      <div class="blink" style="width:5px;height:5px;border-radius:50%;background:var(--green)"></div>
      <span style="font-size:10px;color:var(--text-3)">NOMINAL</span>
    </div>
  </div>
</main>
<script>
  const CIRC=226.2;
  let busy=false,startMs=Date.now(),totalReq=0;
  function pad(n){return String(n).padStart(2,'0')}
  function tick(){
    const n=new Date();
    document.getElementById('clk').textContent=pad(n.getUTCHours())+':'+pad(n.getUTCMinutes())+':'+pad(n.getUTCSeconds());
    const e=Math.floor((Date.now()-startMs)/1000);
    document.getElementById('upt').textContent=pad(Math.floor(e/3600))+':'+pad(Math.floor((e%3600)/60))+':'+pad(e%60);
  }
  setInterval(tick,1000);tick();
  function jitter(b,r){return Math.max(5,Math.min(94,b+(Math.random()-.5)*r))}
  function updateMetrics(){
    const c=jitter(34,20),m=jitter(61,14),n=jitter(47,22);
    document.getElementById('cpu-v').textContent=Math.round(c)+'%';document.getElementById('cpu-b').style.width=c+'%';
    document.getElementById('mem-v').textContent=Math.round(m)+'%';document.getElementById('mem-b').style.width=m+'%';
    document.getElementById('net-v').textContent=Math.round(n)+'%';document.getElementById('net-b').style.width=n+'%';
  }
  setInterval(updateMetrics,2600);
  const cv=document.getElementById('wave'),cx=cv.getContext('2d');
  cv.width=172;cv.height=64;
  let ph=0;
  function drawWave(){
    cx.clearRect(0,0,172,64);
    cx.strokeStyle='#5F57FF';cx.lineWidth=1.8;cx.beginPath();
    for(let x=0;x<172;x++){const y=32+Math.sin((x/172)*Math.PI*6+ph)*15+Math.sin((x/172)*Math.PI*11+ph*1.4)*5;x===0?cx.moveTo(x,y):cx.lineTo(x,y)}
    cx.stroke();
    cx.strokeStyle='#5F57FF44';cx.lineWidth=1;cx.beginPath();
    for(let x=0;x<172;x++){const y=32+Math.sin((x/172)*Math.PI*4+ph*.6)*8;x===0?cx.moveTo(x,y):cx.lineTo(x,y)}
    cx.stroke();
    ph+=0.055;requestAnimationFrame(drawWave);
  }
  drawWave();
  function typeText(text,el,onDone){
    let i=0;el.className='';el.style.color='var(--text-3)';
    function step(){if(i<text.length){el.textContent=text.slice(0,++i)+(i<text.length?'\u258c':'');setTimeout(step,14)}else{el.textContent=text;el.className='done';if(onDone)onDone()}}
    setTimeout(step,80);
  }
  function setTag(t,c,b){const el=document.getElementById('stag');el.textContent=t;el.style.color=c;el.style.borderColor=(b||c)+'55'}
  function setRing(p){document.getElementById('ring').style.strokeDashoffset=CIRC*(1-p/100);document.getElementById('rnum').textContent=p>0?p.toFixed(1)+'%':'\u2014'}
  async function run(){
    if(busy)return;
    const input=document.getElementById('inp').value.trim();
    const outEl=document.getElementById('out'),errEl=document.getElementById('err'),btn=document.getElementById('btn'),scan=document.getElementById('scan');
    errEl.className='err-box';
    if(!input){errEl.textContent='> INPUT ERROR: Sequence cannot be empty.';errEl.className='err-box show';return}
    busy=true;btn.disabled=true;btn.innerHTML='PROCESSING\u2026 <div class="btn-shim"></div>';
    setTag('PROCESSING\u2026','var(--brand-soft)');
    document.getElementById('m-st').textContent='PROCESSING\u2026';document.getElementById('m-st').style.color='var(--brand-soft)';
    document.getElementById('t-st').textContent='PROCESSING\u2026';document.getElementById('t-st').className='tv';
    setRing(0);scan.className='scan-line active';
    outEl.className='';outEl.style.color='var(--text-4)';
    outEl.textContent='> Initializing heuristic core\u2026\n> Validating input sequence\u2026\n> Engaging strategic analysis layer\u2026';
    document.getElementById('m-val').textContent='\u2014';document.getElementById('m-val').className='meta-v';
    document.getElementById('m-srv').textContent='\u2014';
    const t0=performance.now();
    try{
      const res=await fetch('/explain',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:input})});
      if(!res.ok){const e=await res.json().catch(()=>({detail:res.statusText}));throw new Error('HTTP '+res.status+': '+(e.detail||'Unknown error'))}
      const data=await res.json();const rtt=Math.round(performance.now()-t0);
      scan.className='scan-line';
      typeText(data.result,outEl,()=>{
        setRing(data.confidence);setTag('VALIDATED','var(--green)');
        document.getElementById('m-st').textContent='VALIDATED';document.getElementById('m-st').style.color='var(--green)';
        document.getElementById('t-st').textContent='OK';document.getElementById('t-st').className='tv ok';
        const mv=document.getElementById('m-val');mv.textContent='\u2713 YES';mv.className='meta-v ok';
        document.getElementById('m-srv').textContent=data.processing_time_ms+'ms';
        document.getElementById('t-conf').textContent='['+data.confidence+'%]';document.getElementById('t-conf').className='tv ok';
        document.getElementById('t-srv').textContent='['+data.processing_time_ms+'ms]';
        document.getElementById('t-rtt').textContent='['+rtt+'ms]';
        totalReq++;document.getElementById('rcount').textContent=totalReq;
        btn.disabled=false;btn.textContent='INITIALIZE_ANALYSIS';busy=false;
      });
    }catch(e){
      scan.className='scan-line';setRing(0);setTag('ERROR','var(--red)');
      document.getElementById('m-st').textContent='ERROR';document.getElementById('m-st').style.color='var(--red)';
      document.getElementById('t-st').textContent='FAILED';document.getElementById('t-st').className='tv bad';
      outEl.textContent='';errEl.textContent='> ERROR: '+e.message;errEl.className='err-box show';
      document.getElementById('t-conf').textContent='[N/A]';document.getElementById('t-conf').className='tv bad';
      btn.disabled=false;btn.textContent='INITIALIZE_ANALYSIS';busy=false;
    }
  }
  document.getElementById('inp').addEventListener('keydown',e=>{if(e.ctrlKey&&e.key==='Enter')run()});
</script>
</body>
</html>"""

# ── SCHEMAS ────────────────────────────────────────────────────────────────
class RequestData(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("'text' must not be empty or whitespace.")
        return v.strip()


class ExplainResponse(BaseModel):
    result: str
    confidence: float
    processing_time_ms: float


# ── ROUTES ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root() -> HTMLResponse:
    return HTMLResponse(content=UI_HTML)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "3.1.0"}


@app.post("/explain", response_model=ExplainResponse)
async def explain_text(data: RequestData) -> ExplainResponse:
    t0 = time.perf_counter()
    logger.info("POST /explain | input_length=%d", len(data.text))
    try:
        result_data: ConceptReport = process_concept(data.text)
    except ValueError as exc:
        logger.warning("POST /explain | 422 | %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("POST /explain | 500 | %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Heuristic processing failed.")
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info("POST /explain | 200 | confidence=%.1f | time=%.1fms", result_data["confidence"], elapsed_ms)
    return ExplainResponse(result=result_data["text"], confidence=result_data["confidence"], processing_time_ms=elapsed_ms)


# ── ENTRYPOINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info", reload=False)
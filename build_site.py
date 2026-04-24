import base64, os, json

ROOT = os.path.dirname(os.path.abspath(__file__))

pages = [
    {"id": "t-1",  "title": "Short Var, Basics Part 2, Control Structures", "file": "README.md"},
    {"id": "t-2",  "title": "Short Var & Control Structures — Deep Dive",   "file": "Day-2/README.md"},
    {"id": "t-3",  "title": "Functions, Parameters, Pointers, Structs",     "file": "Day-3/README.md"},
    {"id": "t-4",  "title": "Interfaces & Error Handling",                   "file": "Day-4/README.md"},
    {"id": "t-5",  "title": "Concurrency, Goroutines, Channels, Select",    "file": "Day-5/README.md"},
    {"id": "t-6",  "title": "Intro to REST APIs & HTTP in Go",              "file": "Day-6/README.md"},
    {"id": "t-7",  "title": "Project Structure & Fundamentals",             "file": "Day-7/README.md"},
    {"id": "t-8",  "title": "Basic CRUD",                                   "file": "Day-8/README.md"},
    {"id": "t-9",  "title": "JWT Authentication",                           "file": "Day-9/README.md"},
    {"id": "t-10", "title": "File Upload & Static Serving",                 "file": "Day-10/README.md"},
    {"id": "t-11", "title": "Rate Limiting & Caching",                      "file": "Day-11/README.md"},
    {"id": "t-12", "title": "Dockerfile & docker-compose",                  "file": "Day-12/README.md"},
    {"id": "t-13", "title": "Production-Ready E-commerce API",              "file": "Day-13/README.md"},
]

# map id -> source folder so image src can be fixed at runtime
id_to_folder = {
    "t-1": "",
    "t-2": "Day-2", "t-3": "Day-3", "t-4": "Day-4", "t-5": "Day-5",
    "t-6": "Day-6", "t-7": "Day-7", "t-8": "Day-8", "t-9": "Day-9",
    "t-10": "Day-10", "t-11": "Day-11", "t-12": "Day-12", "t-13": "Day-13",
}

data = []
for p in pages:
    path = os.path.join(ROOT, p["file"])
    with open(path, "rb") as f:
        raw = f.read()
    data.append({
        "id": p["id"],
        "title": p["title"],
        "folder": id_to_folder.get(p["id"], ""),
        "content_b64": base64.b64encode(raw).decode("ascii"),
    })

data_json = json.dumps(data, ensure_ascii=False)

html = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Go Mastery — Study Notes</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link id="hljs-dark"  rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">
<link id="hljs-light" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css" disabled>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/go.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/bash.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/json.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/yaml.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/dockerfile.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/sql.min.js"></script>
<style>
  :root, [data-theme="dark"]{
    --bg:#0a0b10;
    --bg-2:#0d0f16;
    --panel:#12151f;
    --panel-2:#171a26;
    --panel-hi:#1c2030;
    --border:#1e2433;
    --border-2:#2a3145;
    --text:#e8ecf4;
    --text-2:#c9d0e0;
    --muted:#7b8499;
    --faint:#4a5266;
    --accent:#00ADD8;
    --accent-2:#29BEB0;
    --accent-hi:#7ee7f5;
    --accent-bg:rgba(0,173,216,.08);
    --accent-border:rgba(0,173,216,.28);
    --code-bg:#0d1017;
    --mono-color:#ffc66d;
    --topbar-bg:rgba(10,11,16,.75);
    --shadow:0 4px 24px -8px rgba(0,0,0,.6);
    --shadow-lg:0 20px 60px -20px rgba(0,0,0,.8);
    --ring:0 0 0 3px rgba(0,173,216,.18);
    --spotlight:rgba(0,173,216,.14);
    --hljs-theme:"github-dark";
  }
  [data-theme="light"]{
    --bg:#f6f8fc;
    --bg-2:#ffffff;
    --panel:#ffffff;
    --panel-2:#f1f4fa;
    --panel-hi:#e7ecf5;
    --border:#e2e7f0;
    --border-2:#d0d6e2;
    --text:#0f1626;
    --text-2:#384056;
    --muted:#6a7388;
    --faint:#a9b0c0;
    --accent:#0087a8;
    --accent-2:#1a9e93;
    --accent-hi:#006b87;
    --accent-bg:rgba(0,135,168,.08);
    --accent-border:rgba(0,135,168,.35);
    --code-bg:#f3f6fb;
    --mono-color:#ad5700;
    --shadow:0 4px 18px -6px rgba(15,22,38,.08);
    --shadow-lg:0 20px 50px -18px rgba(15,22,38,.18);
    --ring:0 0 0 3px rgba(0,135,168,.18);
    --spotlight:rgba(0,135,168,.13);
    --topbar-bg:rgba(246,248,252,.82);
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0;height:100%;background:var(--bg);color:var(--text);font-family:"Inter","Segoe UI",system-ui,-apple-system,sans-serif;font-size:15px;line-height:1.65;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;transition:background-color .28s ease, color .28s ease}
  body::before{
    content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
    background:
      radial-gradient(800px 500px at 0% -10%, rgba(0,173,216,.08), transparent 60%),
      radial-gradient(700px 400px at 100% 10%, rgba(41,190,176,.06), transparent 60%);
    transition:opacity .28s;
  }
  [data-theme="light"] body::before{
    background:
      radial-gradient(800px 500px at 0% -10%, rgba(0,135,168,.07), transparent 60%),
      radial-gradient(700px 400px at 100% 10%, rgba(26,158,147,.06), transparent 60%);
  }

  /* Cursor spotlight — soft glow following the pointer */
  .spotlight{
    position:fixed;pointer-events:none;z-index:2;
    width:520px;height:520px;border-radius:50%;
    background:radial-gradient(circle, var(--spotlight) 0%, transparent 60%);
    transform:translate(-50%,-50%);
    opacity:0;transition:opacity .4s ease;
    will-change:left,top,opacity;
    mix-blend-mode:screen;
  }
  [data-theme="light"] .spotlight{mix-blend-mode:normal;opacity:0}
  [data-theme="light"] .spotlight.visible{opacity:.7}
  .spotlight.visible{opacity:1}
  a{color:var(--accent-hi);text-decoration:none;transition:color .15s}
  a:hover{color:var(--accent)}
  button{font-family:inherit}

  /* Layout */
  .app{display:grid;grid-template-columns:280px 1fr;height:100vh;overflow:hidden;position:relative;z-index:1}

  /* Sidebar */
  .sidebar{background:linear-gradient(180deg, var(--bg-2), var(--bg));border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden}
  .brand{padding:22px 22px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;cursor:pointer;user-select:none}
  .brand .logo{
    width:38px;height:38px;border-radius:10px;
    background:linear-gradient(135deg,var(--accent) 0%,var(--accent-2) 100%);
    display:flex;align-items:center;justify-content:center;
    font-weight:800;font-size:16px;color:#002734;letter-spacing:-.5px;
    box-shadow:0 8px 20px -8px rgba(0,173,216,.45);
    transition:transform .25s cubic-bezier(.2,.8,.2,1);
  }
  .brand:hover .logo{transform:rotate(-8deg) scale(1.06)}
  .brand .ttl{margin:0;font-size:15.5px;font-weight:700;letter-spacing:-.2px}
  .brand .sub{font-size:11px;color:var(--muted);margin-top:2px;letter-spacing:.02em}

  /* Command search */
  .cmd-wrap{padding:14px 14px 8px}
  .cmd{
    display:flex;align-items:center;gap:10px;
    padding:9px 12px;background:var(--panel);
    border:1px solid var(--border);border-radius:10px;
    cursor:text;transition:all .18s;
  }
  .cmd:hover, .cmd.focused{border-color:var(--accent-border);background:var(--panel-2);box-shadow:var(--ring)}
  .cmd .icon{width:15px;height:15px;color:var(--muted)}
  .cmd input{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:13px;font-family:inherit}
  .cmd input::placeholder{color:var(--muted)}
  .cmd kbd{font-family:"JetBrains Mono",monospace;font-size:10.5px;background:var(--panel-hi);color:var(--muted);padding:2px 6px;border-radius:4px;border:1px solid var(--border-2)}

  /* Nav */
  .nav{overflow-y:auto;padding:8px 10px 24px;flex:1}
  .nav .group{color:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.16em;padding:14px 12px 8px;font-weight:600}
  .nav a.item{
    display:grid;grid-template-columns:28px 1fr;align-items:center;gap:10px;
    padding:9px 12px;border-radius:8px;color:var(--text-2);cursor:pointer;
    user-select:none;border:1px solid transparent;margin-bottom:1px;
    position:relative;transition:all .15s;
  }
  .nav a.item:hover{background:var(--panel);color:var(--text);text-decoration:none;transform:translateX(2px)}
  .nav a.item.active{
    background:var(--accent-bg);border-color:var(--accent-border);
    color:var(--text);
  }
  .nav a.item.active::before{
    content:"";position:absolute;left:-10px;top:8px;bottom:8px;width:3px;
    border-radius:0 2px 2px 0;background:linear-gradient(180deg,var(--accent),var(--accent-2));
  }
  .nav a.item .num{
    width:28px;height:28px;border-radius:7px;
    background:var(--panel-hi);color:var(--text-2);
    display:flex;align-items:center;justify-content:center;
    font-size:12px;font-weight:700;font-family:"JetBrains Mono",monospace;
    transition:all .15s;border:1px solid var(--border);
  }
  .nav a.item.active .num{
    background:linear-gradient(135deg,var(--accent),var(--accent-2));
    color:#002734;border-color:transparent;
    box-shadow:0 4px 12px -4px rgba(0,173,216,.45);
  }
  .nav a.item .meta{min-width:0}
  .nav a.item .meta .t{font-size:13.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .nav a.item .meta .s{font-size:11.5px;color:var(--muted);margin-top:1px;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

  .sidebar-footer{padding:12px 16px;border-top:1px solid var(--border);font-size:11px;color:var(--muted);display:flex;align-items:center;gap:8px}
  .sidebar-footer .dot{width:6px;height:6px;border-radius:50%;background:var(--accent-2);box-shadow:0 0 8px var(--accent-2)}

  /* Main */
  .main{overflow:auto;position:relative}
  .topbar{
    position:sticky;top:0;z-index:10;
    background:var(--topbar-bg);backdrop-filter:saturate(1.4) blur(14px);-webkit-backdrop-filter:saturate(1.4) blur(14px);
    border-bottom:1px solid var(--border);
    padding:12px 28px;display:flex;align-items:center;gap:14px;
  }
  .crumbs{color:var(--muted);font-size:13px;display:flex;align-items:center;gap:8px}
  .crumbs .sep{color:var(--faint)}
  .crumbs b{color:var(--text);font-weight:600}
  .topbar .actions{margin-left:auto;display:flex;gap:8px}
  .btn{
    padding:7px 12px;border-radius:8px;background:var(--panel);
    border:1px solid var(--border);color:var(--text-2);font-size:12.5px;
    cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;gap:6px;
  }
  .btn:hover{background:var(--panel-2);border-color:var(--accent-border);color:var(--text)}
  .btn .k{font-family:"JetBrains Mono",monospace;font-size:10.5px;color:var(--muted);background:var(--panel-hi);padding:1px 5px;border-radius:4px;border:1px solid var(--border-2)}

  .content{max-width:940px;margin:0 auto;padding:36px 36px 80px;position:relative}
  .content.fade{animation:pageIn .32s cubic-bezier(.2,.8,.2,1)}
  @keyframes pageIn{
    from{opacity:0;transform:translateY(8px)}
    to{opacity:1;transform:translateY(0)}
  }

  .page-head{margin:0 0 28px;padding-bottom:22px;border-bottom:1px solid var(--border)}
  .page-head .kicker{
    color:var(--accent);font-size:11.5px;font-weight:700;letter-spacing:.22em;
    text-transform:uppercase;display:inline-flex;align-items:center;gap:8px;
  }
  .page-head .kicker::before{content:"";width:20px;height:1px;background:var(--accent)}
  .page-head h1{margin:10px 0 6px;font-size:30px;letter-spacing:-.5px;font-weight:700;line-height:1.25}
  .page-head .tag{color:var(--muted);font-size:14px}

  /* Markdown */
  .md h1,.md h2,.md h3,.md h4{line-height:1.3;margin:1.8em 0 .6em;font-weight:700;letter-spacing:-.3px;scroll-margin-top:80px}
  .md h1{font-size:24px;border-bottom:1px solid var(--border);padding-bottom:10px;color:var(--text)}
  .md h2{font-size:21px;color:var(--text)}
  .md h3{font-size:16.5px;color:var(--text)}
  .md h4{font-size:14.5px;color:var(--text-2);text-transform:uppercase;letter-spacing:.08em}
  .md p{margin:.7em 0;color:var(--text-2)}
  .md strong{color:var(--text);font-weight:600}
  .md ul,.md ol{padding-left:1.4em;color:var(--text-2)}
  .md li{margin:.3em 0}
  .md li::marker{color:var(--accent-2)}
  .md blockquote{
    border-left:3px solid var(--accent);background:linear-gradient(90deg,var(--accent-bg),transparent 40%);
    margin:1em 0;padding:12px 16px;border-radius:0 10px 10px 0;color:var(--text-2);
  }
  .md code{
    background:var(--panel);padding:2px 7px;border-radius:5px;font-size:.9em;
    color:var(--mono-color);font-family:"JetBrains Mono",ui-monospace,Consolas,monospace;
    border:1px solid var(--border);
  }
  .md pre{
    background:var(--code-bg) !important;border:1px solid var(--border);border-radius:10px;
    padding:16px 18px;overflow-x:auto;font-size:13.2px;margin:1.1em 0;
    box-shadow:var(--shadow);position:relative;
  }
  .md pre code{background:transparent;padding:0;color:inherit;font-size:13.2px;border:none;font-family:"JetBrains Mono",ui-monospace,Consolas,monospace}
  .md pre .copy-btn{
    position:absolute;top:8px;right:8px;
    padding:4px 10px;font-size:11px;
    background:var(--panel-2);color:var(--muted);
    border:1px solid var(--border);border-radius:6px;cursor:pointer;
    opacity:0;transition:opacity .15s, all .15s;font-family:inherit;
  }
  .md pre:hover .copy-btn{opacity:1}
  .md pre .copy-btn:hover{color:var(--text);border-color:var(--accent-border)}
  .md pre .copy-btn.copied{color:var(--accent-2);border-color:var(--accent-2)}
  .md table{border-collapse:collapse;margin:1em 0;width:100%;font-size:14px;border-radius:8px;overflow:hidden}
  .md th,.md td{border:1px solid var(--border);padding:9px 13px;text-align:left}
  .md th{background:var(--panel);font-weight:600;color:var(--text)}
  [data-theme="light"] .md strong{color:#0b1220}
  [data-theme="light"] .md blockquote{color:#2c3244}
  .md tr:nth-child(even) td{background:rgba(255,255,255,.015)}
  .md hr{border:none;border-top:1px solid var(--border);margin:2em 0}
  .md img{max-width:100%;border-radius:10px;border:1px solid var(--border);box-shadow:var(--shadow)}

  /* Heading anchor */
  .md h2 .anchor, .md h3 .anchor{
    opacity:0;margin-left:8px;color:var(--muted);font-size:.75em;transition:opacity .15s;
  }
  .md h2:hover .anchor, .md h3:hover .anchor{opacity:1}

  /* TOC */
  .toc{
    position:sticky;top:66px;float:right;width:220px;
    margin:16px -240px 0 0;padding:0 0 0 16px;
    border-left:1px solid var(--border);
    font-size:12.5px;max-height:calc(100vh - 96px);overflow-y:auto;
  }
  .toc .t{color:var(--muted);text-transform:uppercase;letter-spacing:.14em;font-size:10.5px;margin-bottom:10px;font-weight:600}
  .toc a{display:block;color:var(--text-2);padding:4px 0 4px 10px;margin-left:-12px;border-left:2px solid transparent;line-height:1.4;transition:all .15s}
  .toc a.h3{padding-left:22px;color:var(--muted);font-size:12px}
  .toc a:hover{color:var(--text);border-left-color:var(--border-2);text-decoration:none}
  .toc a.active{color:var(--accent);border-left-color:var(--accent);font-weight:500}

  /* Pager */
  .pager{display:flex;justify-content:space-between;gap:14px;margin-top:44px;padding-top:24px;border-top:1px solid var(--border)}
  .pager .p{
    flex:1;padding:16px 18px;background:var(--panel);
    border:1px solid var(--border);border-radius:12px;cursor:pointer;min-width:0;
    transition:all .2s;
  }
  .pager .p:hover{border-color:var(--accent-border);transform:translateY(-2px);box-shadow:var(--shadow)}
  .pager .p .dir{color:var(--muted);font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:600}
  .pager .p .ttl{font-weight:600;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text);font-size:14px}
  .pager .p.next{text-align:right}
  .pager .p.disabled{opacity:.35;pointer-events:none}

  /* Command palette (global search modal) */
  .palette-overlay{
    position:fixed;inset:0;background:rgba(4,5,8,.6);backdrop-filter:blur(6px);
    z-index:100;display:none;align-items:flex-start;justify-content:center;padding:10vh 20px;
    animation:fadeIn .18s;
  }
  .palette-overlay.open{display:flex}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  .palette{
    width:100%;max-width:640px;background:var(--panel);border:1px solid var(--border-2);
    border-radius:14px;box-shadow:var(--shadow-lg);overflow:hidden;
    animation:paletteIn .22s cubic-bezier(.2,.8,.2,1);
  }
  @keyframes paletteIn{from{opacity:0;transform:translateY(-12px) scale(.98)}to{opacity:1;transform:none}}
  .palette-input{
    display:flex;align-items:center;gap:12px;padding:14px 18px;
    border-bottom:1px solid var(--border);
  }
  .palette-input svg{color:var(--muted);width:18px;height:18px;flex:0 0 18px}
  .palette-input input{
    flex:1;background:none;border:none;outline:none;color:var(--text);
    font-size:15px;font-family:inherit;
  }
  .palette-input input::placeholder{color:var(--muted)}
  .palette-input kbd{font-family:"JetBrains Mono",monospace;font-size:10.5px;background:var(--panel-hi);color:var(--muted);padding:3px 7px;border-radius:5px;border:1px solid var(--border-2)}

  .palette-results{max-height:60vh;overflow-y:auto;padding:6px}
  .palette-group{padding:8px 14px 4px;color:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.14em;font-weight:600}
  .palette-item{
    display:flex;align-items:center;gap:12px;padding:10px 14px;
    border-radius:8px;cursor:pointer;transition:all .1s;
  }
  .palette-item:hover, .palette-item.selected{background:var(--panel-hi)}
  .palette-item .lvl{
    font-family:"JetBrains Mono",monospace;font-size:10px;
    padding:2px 6px;border-radius:4px;flex:0 0 auto;font-weight:600;
    background:var(--panel-hi);color:var(--muted);border:1px solid var(--border);
  }
  .palette-item.h2 .lvl{color:var(--accent);border-color:var(--accent-border)}
  .palette-item.h3 .lvl{color:var(--accent-2);border-color:rgba(41,190,176,.28)}
  .palette-item .ttl{flex:1;min-width:0;font-size:14px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .palette-item .ttl mark{background:rgba(0,173,216,.18);color:var(--accent-hi);padding:0 2px;border-radius:3px}
  .palette-item .day{font-size:11.5px;color:var(--muted);flex:0 0 auto;padding:2px 8px;border-radius:5px;background:var(--panel-2);border:1px solid var(--border)}
  .palette-empty{padding:30px 20px;text-align:center;color:var(--muted);font-size:13.5px}
  .palette-footer{
    padding:10px 16px;border-top:1px solid var(--border);
    display:flex;align-items:center;gap:14px;font-size:11.5px;color:var(--muted);
  }
  .palette-footer kbd{font-family:"JetBrains Mono",monospace;font-size:10px;background:var(--panel-hi);color:var(--muted);padding:2px 6px;border-radius:4px;border:1px solid var(--border-2)}

  /* Scroll progress */
  .progress{position:fixed;top:0;left:0;right:0;height:2px;background:transparent;z-index:50;pointer-events:none}
  .progress .bar{height:100%;width:0;background:linear-gradient(90deg,var(--accent),var(--accent-2));transition:width .08s linear;box-shadow:0 0 10px var(--accent)}

  /* Mobile */
  .menu-toggle{display:none}
  @media (max-width: 980px){
    .app{grid-template-columns:1fr}
    .sidebar{position:fixed;inset:0 30% 0 0;z-index:40;transform:translateX(-100%);transition:transform .24s cubic-bezier(.2,.8,.2,1)}
    .sidebar.open{transform:none}
    .menu-toggle{display:inline-flex;align-items:center;gap:6px}
    .toc{display:none}
    .content{padding:24px 22px 60px}
  }

  ::-webkit-scrollbar{width:10px;height:10px}
  ::-webkit-scrollbar-thumb{background:#232b42;border-radius:10px}
  ::-webkit-scrollbar-thumb:hover{background:#334067}
  ::-webkit-scrollbar-track{background:transparent}

  .focus-ring:focus-visible{outline:none;box-shadow:var(--ring);border-color:var(--accent-border)}
</style>
</head>
<body>
<div class="spotlight" id="spotlight"></div>
<div class="progress"><div class="bar" id="progressBar"></div></div>

<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand" onclick="location.hash='#t-1'">
      <div class="logo">Go</div>
      <div>
        <div class="ttl">Go Mastery</div>
        <div class="sub">Study Notes</div>
      </div>
    </div>
    <div class="cmd-wrap">
      <div class="cmd" id="cmdOpen">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input readonly placeholder="Search topics…"/>
        <kbd>⌘K</kbd>
      </div>
    </div>
    <nav class="nav" id="nav">
      <div class="group">Topics</div>
      <div id="nav-items"></div>
    </nav>
    <div class="sidebar-footer">
      <span class="dot"></span> 13 topics · 12,000+ lines of notes
    </div>
  </aside>

  <main class="main" id="main">
    <div class="topbar">
      <button class="btn menu-toggle" id="menuBtn">☰</button>
      <div class="crumbs">Go Mastery <span class="sep">/</span> <b id="crumb">—</b></div>
      <div class="actions">
        <button class="btn" id="cmdBtn"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>Search <span class="k">⌘K</span></button>
        <button class="btn" id="themeBtn" title="Toggle theme"><span id="themeIcon">🌙</span><span id="themeLabel">Dark</span></button>
        <button class="btn" id="topBtn">↑ Top</button>
      </div>
    </div>
    <div class="content fade" id="content">
      <div class="page-head">
        <div class="kicker" id="kicker">Topic</div>
        <h1 id="title">Loading…</h1>
        <div class="tag" id="subtitle"></div>
      </div>
      <aside class="toc" id="toc"><div class="t">On this page</div><div id="toc-items"></div></aside>
      <article class="md" id="md"></article>
      <div class="pager">
        <a class="p prev" id="prev"><div class="dir">← Previous</div><div class="ttl">—</div></a>
        <a class="p next" id="next"><div class="dir">Next →</div><div class="ttl">—</div></a>
      </div>
    </div>
  </main>
</div>

<!-- Command Palette -->
<div class="palette-overlay" id="palette">
  <div class="palette">
    <div class="palette-input">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="paletteInput" placeholder="Search topics across all 13 days…" autocomplete="off"/>
      <kbd>Esc</kbd>
    </div>
    <div class="palette-results" id="paletteResults"></div>
    <div class="palette-footer">
      <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
      <span><kbd>↵</kbd> open</span>
      <span><kbd>Esc</kbd> close</span>
    </div>
  </div>
</div>

<script id="pages-data" type="application/json">__DATA_JSON__</script>
<script>
(function(){
  const PAGES = JSON.parse(document.getElementById('pages-data').textContent);

  function b64decode(b64){
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i=0;i<bin.length;i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder('utf-8').decode(bytes);
  }

  function slugify(s){
    return s.toLowerCase()
      .replace(/[`~!@#$%^&*()+=\[\]{};:'",.<>?\/\\|]/g,'')
      .replace(/[^\w\s-]/g,'')
      .trim().replace(/\s+/g,'-');
  }

  // Decode all markdown upfront
  PAGES.forEach(p => {
    p.md = b64decode(p.content_b64);
    // Build topic index from markdown headings
    const lines = p.md.split('\n');
    const topics = [];
    let inFence = false;
    lines.forEach(line => {
      const fenceMatch = line.match(/^\s*```/);
      if (fenceMatch) { inFence = !inFence; return; }
      if (inFence) return;
      const m = line.match(/^(#{1,4})\s+(.+?)\s*$/);
      if (m){
        const level = m[1].length;
        const text = m[2].replace(/[*_`]/g,'').trim();
        if (level >= 1 && level <= 3){
          topics.push({ level, text, id: slugify(text) });
        }
      }
    });
    p.topics = topics;
  });

  marked.setOptions({
    breaks:false, gfm:true,
    highlight: function(code, lang){
      try {
        if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, {language:lang}).value;
        return hljs.highlightAuto(code).value;
      } catch(e){ return code; }
    }
  });

  // Build sidebar
  const navItems = document.getElementById('nav-items');
  PAGES.forEach((p, idx) => {
    const a = document.createElement('a');
    a.className = 'item';
    a.dataset.id = p.id;
    a.href = '#' + p.id;
    a.innerHTML = `<div class="num">${String(idx+1).padStart(2,'0')}</div><div class="meta"><div class="t">${p.title}</div></div>`;
    navItems.appendChild(a);
  });

  // Cache DOM
  const mdEl = document.getElementById('md');
  const titleEl = document.getElementById('title');
  const subtitleEl = document.getElementById('subtitle');
  const kickerEl = document.getElementById('kicker');
  const crumbEl = document.getElementById('crumb');
  const tocItems = document.getElementById('toc-items');
  const prevEl = document.getElementById('prev');
  const nextEl = document.getElementById('next');
  const contentEl = document.getElementById('content');
  const mainEl = document.getElementById('main');

  function buildToc(){
    tocItems.innerHTML = '';
    const headers = mdEl.querySelectorAll('h2, h3');
    headers.forEach(h => {
      if (!h.id) h.id = slugify(h.textContent);
      const a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent.trim();
      a.className = h.tagName.toLowerCase() === 'h3' ? 'h3' : '';
      a.dataset.target = h.id;
      a.addEventListener('click', ev => {
        ev.preventDefault();
        const t = document.getElementById(h.id);
        if (t) t.scrollIntoView({behavior:'smooth', block:'start'});
        history.replaceState(null,'', '#' + currentPage.id + '::' + h.id);
      });
      tocItems.appendChild(a);
    });
  }

  function addCopyButtons(){
    mdEl.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.copy-btn')) return;
      const btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        const code = pre.querySelector('code');
        try {
          await navigator.clipboard.writeText(code ? code.innerText : pre.innerText);
          btn.textContent = 'Copied';
          btn.classList.add('copied');
          setTimeout(()=>{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1400);
        } catch(e){}
      });
      pre.appendChild(btn);
    });
  }

  let currentPage = null;

  function render(id){
    const idx = PAGES.findIndex(p => p.id === id);
    const p = idx >= 0 ? PAGES[idx] : PAGES[0];
    currentPage = p;

    document.querySelectorAll('.nav .item').forEach(el => {
      el.classList.toggle('active', el.dataset.id === p.id);
    });

    kickerEl.textContent = 'Topic ' + String(idx+1).padStart(2,'0');
    titleEl.textContent = p.title;
    subtitleEl.textContent = 'Study notes';
    crumbEl.textContent = p.title;
    document.title = 'Go Mastery — ' + p.title;

    mdEl.innerHTML = marked.parse(p.md);
    mdEl.querySelectorAll('pre code').forEach(block => { try { hljs.highlightElement(block); } catch(e){} });

    // slug all headings so palette can jump to them
    mdEl.querySelectorAll('h1, h2, h3, h4').forEach(h => {
      if (!h.id) h.id = slugify(h.textContent);
    });

    // add # anchor link beside H2/H3
    mdEl.querySelectorAll('h2, h3').forEach(h => {
      const a = document.createElement('a');
      a.href = '#' + currentPage.id + '::' + h.id;
      a.className = 'anchor';
      a.textContent = '#';
      a.addEventListener('click', e => { e.preventDefault(); h.scrollIntoView({behavior:'smooth'}); history.replaceState(null,'','#' + currentPage.id + '::' + h.id); });
      h.appendChild(a);
    });

    // image paths relative to folder
    mdEl.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src') || '';
      if (!/^https?:/i.test(src) && !src.startsWith('/')){
        const folder = p.folder ? (p.folder + '/') : '';
        img.src = folder + src;
      }
    });

    addCopyButtons();
    buildToc();

    const prev = PAGES[idx-1], next = PAGES[idx+1];
    prevEl.classList.toggle('disabled', !prev);
    nextEl.classList.toggle('disabled', !next);
    prevEl.querySelector('.ttl').textContent = prev ? prev.title : '—';
    nextEl.querySelector('.ttl').textContent = next ? next.title : '—';
    prevEl.onclick = prev ? (e)=>{e.preventDefault();go(prev.id);} : null;
    nextEl.onclick = next ? (e)=>{e.preventDefault();go(next.id);} : null;

    // replay fade animation
    contentEl.classList.remove('fade');
    void contentEl.offsetWidth;
    contentEl.classList.add('fade');

    mainEl.scrollTo({top:0});
  }

  function go(id, hash){
    history.replaceState(null,'', '#' + id + (hash ? '::' + hash : ''));
    render(id);
    if (hash){
      setTimeout(()=>{ const t=document.getElementById(hash); if(t) t.scrollIntoView({behavior:'smooth'}); }, 60);
    }
    document.getElementById('sidebar').classList.remove('open');
  }

  navItems.addEventListener('click', e => {
    const a = e.target.closest('a.item');
    if (!a) return;
    e.preventDefault();
    go(a.dataset.id);
  });

  // TOC active highlight on scroll
  function updateTocActive(){
    const headers = Array.from(mdEl.querySelectorAll('h2, h3'));
    if (!headers.length) return;
    const scrollY = mainEl.scrollTop + 100;
    let activeId = headers[0].id;
    for (const h of headers){
      if (h.offsetTop <= scrollY) activeId = h.id;
      else break;
    }
    document.querySelectorAll('.toc a').forEach(a => {
      a.classList.toggle('active', a.dataset.target === activeId);
    });
  }

  // Scroll progress bar
  const progressBar = document.getElementById('progressBar');
  mainEl.addEventListener('scroll', () => {
    const total = mainEl.scrollHeight - mainEl.clientHeight;
    const pct = total > 0 ? (mainEl.scrollTop / total) * 100 : 0;
    progressBar.style.width = pct + '%';
    updateTocActive();
  });

  document.getElementById('topBtn').onclick = ()=> mainEl.scrollTo({top:0, behavior:'smooth'});
  document.getElementById('menuBtn').onclick = ()=> document.getElementById('sidebar').classList.toggle('open');

  // ====== Theme toggle ======
  const themeBtn = document.getElementById('themeBtn');
  const themeIcon = document.getElementById('themeIcon');
  const themeLabel = document.getElementById('themeLabel');
  const hljsDark = document.getElementById('hljs-dark');
  const hljsLight = document.getElementById('hljs-light');

  function applyTheme(t){
    document.documentElement.setAttribute('data-theme', t);
    if (t === 'light'){
      themeIcon.textContent = '☀️';
      themeLabel.textContent = 'Light';
      hljsDark.disabled = true; hljsLight.disabled = false;
    } else {
      themeIcon.textContent = '🌙';
      themeLabel.textContent = 'Dark';
      hljsDark.disabled = false; hljsLight.disabled = true;
    }
    try { localStorage.setItem('gm-theme', t); } catch(e){}
  }

  const savedTheme = (function(){
    try { return localStorage.getItem('gm-theme'); } catch(e){ return null; }
  })();
  applyTheme(savedTheme || 'dark');

  themeBtn.onclick = ()=>{
    const cur = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(cur === 'dark' ? 'light' : 'dark');
  };

  // ====== Cursor spotlight — fades in on move, out when cursor leaves ======
  const spotlight = document.getElementById('spotlight');
  let spotlightVisible = false;
  let hideTimer = null;
  let rafPending = false;
  let tx = 0, ty = 0;

  function scheduleSpotlight(){
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(()=>{
      spotlight.style.left = tx + 'px';
      spotlight.style.top  = ty + 'px';
      rafPending = false;
    });
  }

  window.addEventListener('pointermove', e => {
    tx = e.clientX; ty = e.clientY;
    if (!spotlightVisible){
      spotlight.classList.add('visible');
      spotlightVisible = true;
    }
    if (hideTimer){ clearTimeout(hideTimer); hideTimer = null; }
    scheduleSpotlight();

    // hide if mouse idle for 2s
    hideTimer = setTimeout(()=>{
      spotlight.classList.remove('visible');
      spotlightVisible = false;
    }, 2000);
  }, {passive:true});

  // fade out when pointer leaves the window entirely
  document.addEventListener('pointerleave', ()=>{
    spotlight.classList.remove('visible');
    spotlightVisible = false;
  });
  window.addEventListener('blur', ()=>{
    spotlight.classList.remove('visible');
    spotlightVisible = false;
  });

  // ====== Command Palette (topic-level search) ======
  const palette = document.getElementById('palette');
  const paletteInput = document.getElementById('paletteInput');
  const paletteResults = document.getElementById('paletteResults');
  let paletteSelected = 0;
  let paletteItems = [];

  function openPalette(){
    palette.classList.add('open');
    paletteInput.value = '';
    renderPaletteResults('');
    setTimeout(()=>paletteInput.focus(), 30);
  }
  function closePalette(){ palette.classList.remove('open'); }

  document.getElementById('cmdBtn').onclick = openPalette;
  document.getElementById('cmdOpen').onclick = openPalette;
  palette.addEventListener('click', e => { if (e.target === palette) closePalette(); });

  document.addEventListener('keydown', e => {
    const k = e.key.toLowerCase();
    if ((e.metaKey || e.ctrlKey) && k === 'k'){
      e.preventDefault(); openPalette();
    } else if (k === 'escape' && palette.classList.contains('open')){
      closePalette();
    } else if (k === '/' && !palette.classList.contains('open') && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){
      e.preventDefault(); openPalette();
    }
  });

  function escapeHtml(s){ return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function highlightMatch(text, query){
    if (!query) return escapeHtml(text);
    const safe = escapeHtml(text);
    const q = query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    return safe.replace(new RegExp('(' + q + ')','ig'), '<mark>$1</mark>');
  }

  function renderPaletteResults(query){
    const q = query.trim().toLowerCase();
    paletteResults.innerHTML = '';
    paletteItems = [];

    // Build flat topic list
    const matches = [];
    PAGES.forEach(p => {
      p.topics.forEach(t => {
        if (!q || t.text.toLowerCase().includes(q)){
          matches.push({ page: p, topic: t });
        }
      });
    });

    if (!matches.length){
      paletteResults.innerHTML = '<div class="palette-empty">No topics match "' + escapeHtml(query) + '"</div>';
      return;
    }

    // Group by day
    const byDay = new Map();
    matches.forEach(m => {
      if (!byDay.has(m.page.id)) byDay.set(m.page.id, { page: m.page, items: [] });
      byDay.get(m.page.id).items.push(m.topic);
    });

    byDay.forEach(({page, items}) => {
      const hdr = document.createElement('div');
      hdr.className = 'palette-group';
      hdr.textContent = page.title;
      paletteResults.appendChild(hdr);

      items.forEach(t => {
        const row = document.createElement('div');
        row.className = 'palette-item h' + t.level;
        row.innerHTML = `
          <span class="lvl">H${t.level}</span>
          <span class="ttl">${highlightMatch(t.text, q)}</span>
        `;
        row.addEventListener('click', ()=>{
          closePalette();
          go(page.id, t.id);
        });
        paletteResults.appendChild(row);
        paletteItems.push(row);
      });
    });

    paletteSelected = 0;
    updatePaletteSelection();
  }

  function updatePaletteSelection(){
    paletteItems.forEach((el,i) => el.classList.toggle('selected', i === paletteSelected));
    const el = paletteItems[paletteSelected];
    if (el) el.scrollIntoView({block:'nearest'});
  }

  paletteInput.addEventListener('input', e => renderPaletteResults(e.target.value));
  paletteInput.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown'){ e.preventDefault(); paletteSelected = Math.min(paletteSelected+1, paletteItems.length-1); updatePaletteSelection(); }
    else if (e.key === 'ArrowUp'){ e.preventDefault(); paletteSelected = Math.max(paletteSelected-1, 0); updatePaletteSelection(); }
    else if (e.key === 'Enter'){
      e.preventDefault();
      const el = paletteItems[paletteSelected];
      if (el) el.click();
    }
  });

  // initial
  function loadFromHash(){
    const raw = location.hash.slice(1);
    const [id, hash] = raw.split('::');
    const valid = PAGES.some(p => p.id === id);
    render(valid ? id : 't-1');
    if (hash){
      setTimeout(()=>{ const t=document.getElementById(hash); if(t) t.scrollIntoView({behavior:'smooth'}); }, 100);
    }
  }
  window.addEventListener('hashchange', () => { loadFromHash(); });
  loadFromHash();
})();
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json.replace("</", "<\\/"))

out_path = os.path.join(ROOT, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {out_path}  ({len(html)//1024} KB, {len(pages)} pages)")

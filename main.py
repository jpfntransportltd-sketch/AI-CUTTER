import os, uuid, json
from flask import Flask, request, send_file, render_template_string, session, redirect, jsonify
import yt_dlp, imageio_ffmpeg

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aicutter2026')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
os.makedirs("dl", exist_ok=True)
os.makedirs("static", exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
CFG = "config.json"

def load_cfg():
    if os.path.exists(CFG):
        try:
            with open(CFG) as f: return json.load(f)
        except: pass
    return {
        "site_name": "AI Cutter",
        "tagline": "Download · Play · Share",
        "logo_url": "",
        "home_title": "Welcome to AI Cutter",
        "home_text": "Download videos, extract MP3, cut ringtones, and watch everything in your Library.",
        "footer_text": "© 2026 AI Cutter"
    }

def save_cfg(c):
    with open(CFG, 'w') as f: json.dump(c, f, indent=2)

def base_html(cfg, content):
    logo = f'<img src="{cfg["logo_url"]}" style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:3px solid #FFD700;box-shadow:0 4px 12px rgba(255,215,0,0.4)">' if cfg.get("logo_url") else '<div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#FFD700,#FFED4E);display:flex;align-items:center;justify-content:center;font-size:26px;border:3px solid #fff;box-shadow:0 4px 12px rgba(255,215,0,0.4)">🎬</div>'
    return f"""<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>{cfg['site_name']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,sans-serif;-webkit-tap-highlight-color:transparent}}
body{{background:#FFFDF5;color:#4B5563;padding-bottom:40px;min-height:100vh}}
@keyframes flow{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
@keyframes pop{{0%{{transform:scale(0.9);opacity:0}}100%{{transform:scale(1);opacity:1}}}}
.topbar{{background:linear-gradient(90deg,#FFD700,#FFED4E,#93C5FD,#FFD700);background-size:400% 400%;animation:flow 10s ease infinite;padding:16px 18px;display:flex;align-items:center;gap:14px;box-shadow:0 4px 20px rgba(255,215,0,0.3);position:sticky;top:0;z-index:100}}
.topbar-text h1{{font-size:20px;font-weight:800;color:#374151}}
.topbar-text p{{font-size:11px;color:#4B5563;font-weight:600;margin-top:2px}}
.menu-btn{{margin-left:auto;background:rgba(255,255,255,0.9);border:none;width:42px;height:42px;border-radius:12px;font-size:22px;cursor:pointer}}
.drawer{{position:fixed;top:0;right:-300px;width:280px;height:100vh;background:#FFFDF5;z-index:200;box-shadow:-4px 0 20px rgba(0,0,0,0.1);transition:right 0.3s;padding:24px 20px;overflow-y:auto}}
.drawer.open{{right:0}}
.ov{{position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:150;display:none}}
.ov.open{{display:block}}
.drawer h3{{font-size:14px;color:#F59E0B;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;font-weight:800}}
.drawer a{{display:block;padding:14px 16px;color:#4B5563;text-decoration:none;font-size:15px;font-weight:600;border-radius:12px;margin-bottom:6px;background:#fff;border:2px solid #FDE68A}}
.drawer a.admin{{background:linear-gradient(135deg,#FFD700,#FFED4E);border-color:#FFD700}}
.close-x{{position:absolute;top:16px;right:16px;background:none;border:none;font-size:26px;color:#9CA3AF}}
.langs{{display:flex;gap:8px;padding:14px 16px;background:#FFF9E6;overflow-x:auto}}
.langs button{{padding:8px 16px;border:2px solid #FDE68A;background:#fff;border-radius:20px;font-size:13px;font-weight:700;color:#6B7280;white-space:nowrap}}
.langs button.on{{background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151;border-color:#FFD700}}
.tabs{{display:flex;gap:6px;padding:10px 12px;background:#FFF9E6;overflow-x:auto}}
.tabs button{{flex:1;padding:12px 8px;border:2px solid transparent;background:#fff;border-radius:12px;font-size:12px;font-weight:700;color:#9CA3AF;white-space:nowrap;min-width:72px}}
.tabs button.on{{background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151}}
.wrap{{padding:16px}}
.hero{{background:linear-gradient(135deg,#FFFDF5,#FFF9E6);border:2px solid #FDE68A;border-radius:20px;padding:24px;margin-bottom:16px;text-align:center;box-shadow:0 4px 16px rgba(255,215,0,0.15)}}
.hero h2{{font-size:20px;color:#374151;margin-bottom:8px}}
.hero p{{font-size:13px;color:#6B7280;line-height:1.6}}
.card{{background:linear-gradient(135deg,#FFFDF5,#FFF9E6);border:2px solid #FDE68A;border-radius:20px;padding:22px;margin-bottom:16px;box-shadow:0 4px 16px rgba(255,215,0,0.15)}}
.card h2{{font-size:19px;color:#374151;margin-bottom:16px;font-weight:800}}
input[type=text],input[type=number],input[type=password],textarea{{width:100%;padding:14px;border:2px solid #FDE68A;border-radius:12px;font-size:15px;margin-bottom:12px;background:#fff;outline:none;color:#4B5563;font-family:inherit}}
input:focus,textarea:focus{{border-color:#FFD700;box-shadow:0 0 0 3px rgba(255,215,0,0.15)}}
textarea{{resize:vertical;min-height:80px}}
input[type=file]{{width:100%;padding:14px;border:2px dashed #FDE68A;border-radius:12px;font-size:14px;margin-bottom:12px;background:#FFFDF5;color:#6B7280}}
.btn{{width:100%;padding:16px;background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151;border:none;border-radius:12px;font-size:16px;font-weight:800;margin-top:4px;cursor:pointer;box-shadow:0 4px 12px rgba(255,215,0,0.3)}}
.btn:active{{transform:scale(0.98)}}
.btn:disabled{{opacity:0.6}}
.btn.blue{{background:linear-gradient(135deg,#60A5FA,#93C5FD);color:#fff}}
.btn.dark{{background:#4B5563;color:#fff}}
.res{{margin-top:14px;padding:14px;border-radius:12px;font-size:14px;display:none;word-break:break-word;line-height:1.5}}
.res.ok{{background:#D1FAE5;color:#065F46;display:block;border-left:4px solid #10B981}}
.res.err{{background:#FEE2E2;color:#991B1B;display:block;border-left:4px solid #EF4444}}
.res.info{{background:#FEF3C7;color:#92400E;display:block;border-left:4px solid #F59E0B}}
.res a{{color:#065F46;font-weight:800;display:block;margin-top:10px;padding:12px;background:#fff;border-radius:8px;text-align:center;text-decoration:none;border:2px solid #10B981}}
.res a.blue{{color:#1E40AF;border-color:#60A5FA}}
.hide{{display:none}}
.feature{{padding:12px 0;border-bottom:1px solid #FDE68A;font-size:14px;display:flex;gap:12px;align-items:center;color:#4B5563}}
.feature:last-child{{border:none}}
.feature-icon{{font-size:22px;min-width:30px}}
.page{{background:#FFFDF5;padding:20px}}
.page h2{{font-size:22px;color:#374151;margin-bottom:16px;padding-bottom:12px;border-bottom:3px solid #FFD700}}
.page h3{{font-size:16px;color:#F59E0B;margin:16px 0 8px;font-weight:800}}
.page p,.page li{{font-size:14px;line-height:1.7;color:#4B5563;margin-bottom:10px}}
.page ul{{padding-left:20px}}
.back{{display:inline-block;padding:10px 18px;background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151;border-radius:10px;font-weight:700;font-size:14px;text-decoration:none;margin-bottom:16px}}
.footer{{text-align:center;padding:24px 16px;color:#9CA3AF;font-size:12px}}
.footer a{{color:#F59E0B;text-decoration:none;margin:0 8px;font-weight:700}}

/* LIBRARY STYLES */
.lib-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}}
.lib-head h2{{font-size:19px;color:#374151;font-weight:800}}
.refresh-btn{{background:linear-gradient(135deg,#FFD700,#FFED4E);border:none;width:38px;height:38px;border-radius:10px;font-size:18px;cursor:pointer}}
.gallery{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}
.item{{background:#fff;border:2px solid #FDE68A;border-radius:14px;overflow:hidden;box-shadow:0 3px 10px rgba(255,215,0,0.15)}}
.thumb{{width:100%;height:130px;background:#FFF9E6;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}}
.thumb video,.thumb img{{width:100%;height:100%;object-fit:cover}}
.thumb .icon{{font-size:48px}}
.play-overlay{{position:absolute;inset:0;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:36px;color:#fff}}
.item-info{{padding:10px}}
.item-name{{font-size:12px;font-weight:700;color:#374151;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:8px}}
.item-actions{{display:flex;gap:6px}}
.item-actions button,.item-actions a{{flex:1;padding:8px;border:none;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;text-align:center;text-decoration:none;display:flex;align-items:center;justify-content:center}}
.act-play{{background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151}}
.act-save{{background:#D1FAE5;color:#065F46}}
.act-share{{background:#DBEAFE;color:#1E40AF}}
.act-del{{background:#FEE2E2;color:#991B1B}}
.empty{{text-align:center;padding:40px 20px;color:#9CA3AF}}
.empty .icon{{font-size:60px;margin-bottom:12px}}

/* PLAYER MODAL */
.player-modal{{position:fixed;inset:0;background:rgba(0,0,0,0.95);z-index:500;display:none;flex-direction:column;align-items:center;justify-content:center;padding:20px}}
.player-modal.open{{display:flex}}
.player-modal video,.player-modal img{{max-width:100%;max-height:70vh;border-radius:12px}}
.player-modal audio{{width:100%;max-width:400px}}
.player-close{{position:absolute;top:20px;right:20px;background:linear-gradient(135deg,#FFD700,#FFED4E);border:none;width:44px;height:44px;border-radius:50%;font-size:22px;font-weight:800;color:#374151;cursor:pointer}}
.player-title{{color:#FFD700;font-size:15px;font-weight:700;margin-bottom:16px;text-align:center;padding:0 60px}}
.player-actions{{display:flex;gap:10px;margin-top:20px}}
.player-actions button,.player-actions a{{padding:12px 20px;border:none;border-radius:12px;font-size:14px;font-weight:800;cursor:pointer;text-decoration:none;background:linear-gradient(135deg,#FFD700,#FFED4E);color:#374151}}
</style>
</head><body>

<div class="topbar">
{logo}
<div class="topbar-text"><h1>{cfg['site_name']}</h1><p>{cfg['tagline']}</p></div>
<button class="menu-btn" onclick="tm()">☰</button>
</div>

<div class="ov" id="ov" onclick="tm()"></div>
<div class="drawer" id="dr">
<button class="close-x" onclick="tm()">✕</button>
<h3>Menu</h3>
<a href="/">🏠 Home</a>
<a href="/about">📚 About</a>
<a href="/privacy">🔒 Privacy</a>
<a href="/disclaimer">⚠️ Disclaimer</a>
<a href="/contact">📧 Contact</a>
<a href="/admin" class="admin">⚙️ Admin Panel</a>
</div>

{content}

<div class="footer">
<a href="/about">About</a>
<a href="/privacy">Privacy</a>
<a href="/disclaimer">Disclaimer</a>
<a href="/contact">Contact</a>
<p style="margin-top:14px;color:#D1D5DB">{cfg['footer_text']}</p>
</div>

<!-- PLAYER MODAL -->
<div class="player-modal" id="player">
<button class="player-close" onclick="closePlayer()">✕</button>
<div class="player-title" id="ptitle"></div>
<div id="pmedia"></div>
<div class="player-actions">
<a id="psave" download>📥 Save</a>
<button onclick="pShare()">📤 Share</button>
</div>
</div>

<script>
function tm(){{
  document.getElementById('dr').classList.toggle('open');
  document.getElementById('ov').classList.toggle('open');
}}
let currentFile = '';
function playFile(name, type){{
  currentFile = name;
  document.getElementById('ptitle').textContent = name;
  const url = '/api/file/' + encodeURIComponent(name);
  const m = document.getElementById('pmedia');
  m.innerHTML = '';
  if(type === 'video'){{
    const v = document.createElement('video');
    v.src = url; v.controls = true; v.autoplay = true; v.playsInline = true;
    m.appendChild(v);
  }} else if(type === 'image'){{
    const i = document.createElement('img');
    i.src = url; m.appendChild(i);
  }} else if(type === 'audio'){{
    const a = document.createElement('audio');
    a.src = url; a.controls = true; a.autoplay = true; m.appendChild(a);
  }}
  document.getElementById('psave').href = url;
  document.getElementById('player').classList.add('open');
}}
function closePlayer(){{
  document.getElementById('player').classList.remove('open');
  document.getElementById('pmedia').innerHTML = '';
}}
function pShare(){{
  const url = window.location.origin + '/api/file/' + encodeURIComponent(currentFile);
  if(navigator.share){{
    navigator.share({{title: currentFile, url: url}}).catch(()=>{{}});
  }} else {{
    navigator.clipboard.writeText(url);
    alert('Link copied!');
  }}
}}
</script>
</body></html>"""

HOME = """
<div style="padding:20px 16px 8px">
<div class="hero">
<h2>{HOME_TITLE}</h2>
<p>{HOME_TEXT}</p>
</div>
</div>

<div class="langs">
<button class="on" onclick="L('en',this)">English</button>
<button onclick="L('pa',this)">ਪੰਜਾਬੀ</button>
<button onclick="L('hi',this)">हिंदी</button>
<button onclick="L('es',this)">Español</button>
</div>

<div class="tabs">
<button class="on" onclick="T('v',this)">🎬 Video</button>
<button onclick="T('a',this)">🎵 MP3</button>
<button onclick="T('r',this)">✂️ Ringtone</button>
<button onclick="T('l',this)">📚 Library</button>
<button onclick="T('i',this)">📋 Info</button>
</div>

<div class="wrap">

<div id="tab-v">
<div class="card">
<h2>🎬 <span id="h1">Download Video</span></h2>
<input type="text" id="vurl" placeholder="Paste video URL...">
<button class="btn" id="b1" onclick="dl('video')">⬇️ <span id="b1t">Download</span></button>
<div class="res" id="r1"></div>
</div>
</div>

<div id="tab-a" class="hide">
<div class="card">
<h2>🎵 <span id="h2">Download MP3</span></h2>
<input type="text" id="aurl" placeholder="Paste URL for MP3...">
<button class="btn" id="b2" onclick="dl('mp3')">🎵 <span id="b2t">Extract MP3</span></button>
<div class="res" id="r2"></div>
</div>
</div>

<div id="tab-r" class="hide">
<div class="card">
<h2>✂️ <span id="h3">Ringtone Cutter</span></h2>
<input type="file" id="rf" accept="audio/*">
<input type="number" id="rs" placeholder="Start sec" value="0">
<input type="number" id="re" placeholder="End sec" value="30">
<button class="btn" id="b3" onclick="cut()">✂️ <span id="b3t">Cut</span></button>
<div class="res" id="r3"></div>
</div>
</div>

<div id="tab-l" class="hide">
<div class="card">
<div class="lib-head">
<h2>📚 My Library</h2>
<button class="refresh-btn" onclick="loadLib()">🔄</button>
</div>
<div id="lib-list" class="gallery"></div>
<div id="lib-empty" class="empty">
<div class="icon">📁</div>
<div>No files yet. Download something!</div>
</div>
</div>
</div>

<div id="tab-i" class="hide">
<div class="card">
<h2>📋 Features</h2>
<div class="feature"><span class="feature-icon">🎬</span><span>Video download & play</span></div>
<div class="feature"><span class="feature-icon">🎵</span><span>MP3 extraction</span></div>
<div class="feature"><span class="feature-icon">✂️</span><span>Ringtone cutter</span></div>
<div class="feature"><span class="feature-icon">📚</span><span>Library auto-save</span></div>
<div class="feature"><span class="feature-icon">▶️</span><span>Built-in player</span></div>
<div class="feature"><span class="feature-icon">📤</span><span>Share anywhere</span></div>
<div class="feature"><span class="feature-icon">🌐</span><span>Multi-language</span></div>
</div>
</div>

</div>

<script>
const TT={{
en:{{h1:"Download Video",b1:"Download",h2:"Download MP3",b2:"Extract MP3",h3:"Ringtone Cutter",b3:"Cut"}},
pa:{{h1:"ਵੀਡੀਓ ਡਾਊਨਲੋਡ",b1:"ਡਾਊਨਲੋਡ",h2:"MP3 ਡਾਊਨਲੋਡ",b2:"ਕੱਢੋ",h3:"ਰਿੰਗਟੋਨ ਕਟਰ",b3:"ਕੱਟੋ"}},
hi:{{h1:"वीडियो डाउनलोड",b1:"डाउनलोड",h2:"MP3 डाउनलोड",b2:"निकालें",h3:"रिंगटोन कटर",b3:"काटें"}},
es:{{h1:"Descargar Video",b1:"Descargar",h2:"Descargar MP3",b2:"Extraer MP3",h3:"Cortador",b3:"Cortar"}}
}};
function L(l,e){{
document.querySelectorAll('.langs button').forEach(b=>b.classList.remove('on'));
e.classList.add('on');
const t=TT[l];
document.getElementById('h1').textContent=t.h1;
document.getElementById('b1t').textContent=t.b1;
document.getElementById('h2').textContent=t.h2;
document.getElementById('b2t').textContent=t.b2;
document.getElementById('h3').textContent=t.h3;
document.getElementById('b3t').textContent=t.b3;
}}
function T(n,e){{
document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('on'));
e.classList.add('on');
['v','a','r','l','i'].forEach(x=>document.getElementById('tab-'+x).classList.add('hide'));
document.getElementById('tab-'+n).classList.remove('hide');
if(n==='l') loadLib();
}}

async function dl(f){{
const u=f==='video'?document.getElementById('vurl').value:document.getElementById('aurl').value;
const r=f==='video'?document.getElementById('r1'):document.getElementById('r2');
const b=f==='video'?document.getElementById('b1'):document.getElementById('b2');
if(!u){{r.className='res err';r.textContent='⚠️ Paste a URL';return;}}
b.disabled=true;const o=b.innerHTML;b.innerHTML='⏳...';
r.className='res info';r.textContent='⏳ Downloading...';
try{{
const x=await fetch('/api/download?url='+encodeURIComponent(u)+'&format='+f,{{method:'POST'}});
const d=await x.json();
if(d.ok){{
r.className='res ok';
r.innerHTML='✅ '+d.title+'<a href="/api/file/'+d.filename+'" download>📥 Save to Phone</a>';
}}
else{{r.className='res err';r.textContent='❌ '+d.error;}}
}}catch(e){{r.className='res err';r.textContent='❌ Error';}}
b.disabled=false;b.innerHTML=o;
}}

async function cut(){{
const f=document.getElementById('rf').files[0];
const r=document.getElementById('r3');
if(!f){{r.className='res err';r.textContent='⚠️ Select file';return;}}
r.className='res info';r.textContent='⏳ Cutting...';
const fd=new FormData();fd.append('file',f);
fd.append('start',document.getElementById('rs').value);
fd.append('end',document.getElementById('re').value);
try{{
const x=await fetch('/api/ringtone',{{method:'POST',body:fd}});
const d=await x.json();
if(d.ok){{r.className='res ok';r.innerHTML='✅ Ready<a href="/api/file/'+d.filename+'" download>📥 Save</a>';}}
else{{r.className='res err';r.textContent='❌ '+d.error;}}
}}catch(e){{r.className='res err';r.textContent='❌ Error';}}
}}

async function loadLib(){{
const list=document.getElementById('lib-list');
const empty=document.getElementById('lib-empty');
list.innerHTML='<div style="grid-column:1/3;text-align:center;padding:20px;color:#9CA3AF">⏳ Loading...</div>';
try{{
const x=await fetch('/api/library');
const d=await x.json();
list.innerHTML='';
if(!d.files || d.files.length===0){{
empty.style.display='block';
return;
}}
empty.style.display='none';
d.files.forEach(f=>{{
const item=document.createElement('div');
item.className='item';
let thumb='';
if(f.type==='video'){{
thumb='<div class="thumb"><video src="/api/file/'+encodeURIComponent(f.name)+'#t=0.5" preload="metadata" muted></video><div class="play-overlay">▶️</div></div>';
}} else if(f.type==='image'){{
thumb='<div class="thumb"><img src="/api/file/'+encodeURIComponent(f.name)+'"></div>';
}} else if(f.type==='audio'){{
thumb='<div class="thumb"><div class="icon">🎵</div></div>';
}} else {{
thumb='<div class="thumb"><div class="icon">📄</div></div>';
}}
const shortName = f.name.length > 22 ? f.name.substring(0,20)+'...' : f.name;
item.innerHTML = thumb + '<div class="item-info"><div class="item-name" title="'+f.name+'">'+shortName+'</div><div class="item-actions"><button class="act-play" onclick="playFile(\\''+f.name.replace(/'/g,"\\\\'")+'\\',\\''+f.type+'\\')">▶</button><a class="act-save" href="/api/file/'+encodeURIComponent(f.name)+'" download>📥</a><button class="act-del" onclick="delFile(\\''+f.name.replace(/'/g,"\\\\'")+'\\')">🗑</button></div></div>';
list.appendChild(item);
}});
}}catch(e){{
list.innerHTML='<div style="grid-column:1/3;text-align:center;padding:20px;color:#EF4444">❌ Load failed</div>';
}}
}}

async function delFile(name){{
if(!confirm('Delete '+name+' ?')) return;
try{{
await fetch('/api/delete/'+encodeURIComponent(name),{{method:'POST'}});
loadLib();
}}catch(e){{}}
}}

// Auto-load library on page open
window.addEventListener('load', ()=>{{ setTimeout(loadLib, 500); }});
</script>
"""

def page(t, b):
    return f'<div class="page"><a class="back" href="/">← Back</a><h2>{t}</h2>{b}</div>'

@app.route("/")
def home():
    c = load_cfg()
    content = HOME.replace("{HOME_TITLE}", c['home_title']).replace("{HOME_TEXT}", c['home_text'])
    return render_template_string(base_html(c, content))

@app.route("/about")
def about():
    c = load_cfg()
    b = """<p>AI Cutter is an all-in-one media toolkit with built-in player and library.</p>
<h3>✨ Features</h3>
<ul><li>Video download & play</li><li>MP3 extraction</li><li>Ringtone cutter</li><li>Library auto-save</li><li>Share anywhere</li></ul>
<h3>📧 Contact</h3><p>support@aicutter.app</p>"""
    return render_template_string(base_html(c, page("📚 About", b)))

@app.route("/privacy")
def privacy():
    c = load_cfg()
    b = """<h3>1. Data</h3><p>No personal data collected. Files stored on server for your library.</p>
<h3>2. Cookies</h3><p>Only for admin login session.</p>
<h3>3. Security</h3><p>HTTPS encryption used.</p>
<h3>4. Contact</h3><p>privacy@aicutter.app</p>"""
    return render_template_string(base_html(c, page("🔒 Privacy Policy", b)))

@app.route("/disclaimer")
def disclaimer():
    c = load_cfg()
    b = """<h3>1. Copyright</h3><p>We don't host any media. Only provide download tool.</p>
<h3>2. User Responsibility</h3><ul><li>Download only content you have rights to</li></ul>
<h3>3. No Liability</h3><p>Users are responsible for their actions.</p>
<h3>4. DMCA</h3><p>dmca@aicutter.app</p>"""
    return render_template_string(base_html(c, page("⚠️ Disclaimer", b)))

@app.route("/contact")
def contact():
    c = load_cfg()
    b = """<h3>📧 Support</h3><p>support@aicutter.app</p>
<h3>🐛 Bugs</h3><p>bugs@aicutter.app</p>"""
    return render_template_string(base_html(c, page("📧 Contact", b)))

LOGIN = """<div class="wrap" style="max-width:500px;margin:40px auto">
<div class="card">
<h2>🔐 Admin Login</h2>
<form method="POST">
<input type="password" name="password" placeholder="Enter admin password" required>
<button type="submit" class="btn">Login</button>
{ERR}
</form>
</div></div>"""

PANEL = """<div class="wrap" style="max-width:700px;margin:20px auto">
<div class="card">
<h2>⚙️ Admin Panel</h2>
<form method="POST" enctype="multipart/form-data" action="/admin/save">
<label style="font-size:13px;font-weight:700">Site Name</label>
<input type="text" name="site_name" value="{SITE_NAME}" required>
<label style="font-size:13px;font-weight:700">Tagline</label>
<input type="text" name="tagline" value="{TAGLINE}">
<label style="font-size:13px;font-weight:700">Logo</label>
<input type="file" name="logo" accept="image/*">
{LOGO}
<label style="font-size:13px;font-weight:700">Home Title</label>
<input type="text" name="home_title" value="{HT}">
<label style="font-size:13px;font-weight:700">Home Description</label>
<textarea name="home_text">{HX}</textarea>
<label style="font-size:13px;font-weight:700">Footer</label>
<input type="text" name="footer_text" value="{FT}">
<button type="submit" class="btn">💾 Save</button>
</form>
<div style="margin-top:12px;display:flex;gap:8px">
<a href="/" class="btn blue" style="text-decoration:none;text-align:center;flex:1">🏠 Site</a>
<a href="/admin/logout" class="btn dark" style="text-decoration:none;text-align:center;flex:1">🚪 Logout</a>
</div>
</div></div>"""

@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("admin"): return redirect("/admin/panel")
    e = ""
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")
        e = '<div class="res err" style="display:block">❌ Wrong password</div>'
    return render_template_string(base_html(load_cfg(), LOGIN.replace("{ERR}", e)))

@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"): return redirect("/admin")
    c = load_cfg()
    lg = f'<img src="{c["logo_url"]}" style="width:80px;height:80px;border-radius:12px;object-fit:cover;margin-bottom:12px">' if c.get("logo_url") else ""
    p = (PANEL.replace("{SITE_NAME}", c["site_name"]).replace("{TAGLINE}", c["tagline"])
        .replace("{LOGO}", lg).replace("{HT}", c["home_title"])
        .replace("{HX}", c["home_text"]).replace("{FT}", c["footer_text"]))
    return render_template_string(base_html(c, p))

@app.route("/admin/save", methods=["POST"])
def admin_save():
    if not session.get("admin"): return redirect("/admin")
    c = load_cfg()
    c["site_name"] = request.form.get("site_name", c["site_name"])
    c["tagline"] = request.form.get("tagline", c["tagline"])
    c["home_title"] = request.form.get("home_title", c["home_title"])
    c["home_text"] = request.form.get("home_text", c["home_text"])
    c["footer_text"] = request.form.get("footer_text", c["footer_text"])
    l = request.files.get("logo")
    if l and l.filename:
        ext = os.path.splitext(l.filename)[1].lower()
        if ext in [".png",".jpg",".jpeg",".gif",".webp",".svg"]:
            fn = "logo_" + str(uuid.uuid4())[:8] + ext
            l.save(os.path.join("static", fn))
            c["logo_url"] = "/static/" + fn
    save_cfg(c)
    return redirect("/admin/panel")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/static/<path:f>")
def static_files(f): return send_file(os.path.join("static", f))

# ============ LIBRARY API ============
@app.route("/api/library")
def api_library():
    files = []
    if os.path.exists("dl"):
        for name in sorted(os.listdir("dl"), reverse=True):
            path = os.path.join("dl", name)
            if not os.path.isfile(path): continue
            if name.endswith(".part") or name.startswith("."): continue
            ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
            ftype = "other"
            if ext in ["mp4","mov","webm","mkv","avi","m4v"]: ftype = "video"
            elif ext in ["mp3","m4a","aac","wav","ogg","opus"]: ftype = "audio"
            elif ext in ["m4r"]: ftype = "audio"
            elif ext in ["jpg","jpeg","png","gif","webp","bmp"]: ftype = "image"
            elif ext in ["pdf"]: ftype = "pdf"
            files.append({
                "name": name,
                "type": ftype,
                "size": os.path.getsize(path),
                "time": os.path.getmtime(path)
            })
    return jsonify({"files": files})

@app.route("/api/delete/<name>", methods=["POST"])
def api_delete(name):
    try:
        path = os.path.join("dl", name)
        if os.path.exists(path):
            os.remove(path)
            return {"ok": True}
        return {"ok": False, "error": "Not found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ============ DOWNLOAD ============
@app.route("/api/download", methods=["POST"])
def api_dl():
    url = request.args.get("url")
    fmt = request.args.get("format", "video")
    j = str(uuid.uuid4())[:8]
    o = {'outtmpl': f'dl/{j}_%(title)s.%(ext)s', 'ffmpeg_location': FF, 'quiet': True}
    if os.path.exists("cookies.txt"): o['cookiefile'] = "cookies.txt"
    if fmt == "mp3":
        o['format'] = 'bestaudio/best'
        o['postprocessors'] = [{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]
    else:
        o['format'] = 'best[ext=mp4]/best'
    try:
        with yt_dlp.YoutubeDL(o) as y:
            i = y.extract_info(url, download=True)
            fn = y.prepare_filename(i)
            if fmt == "mp3": fn = os.path.splitext(fn)[0] + ".mp3"
            return {"ok": True, "title": i.get('title','video'), "filename": os.path.basename(fn)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.route("/api/ringtone", methods=["POST"])
def api_ring():
    try:
        f = request.files["file"]
        s = float(request.form["start"])
        e = float(request.form["end"])
        j = str(uuid.uuid4())[:8]
        inp = f"dl/{j}_in"
        f.save(inp)
        out = f"{j}_ring.m4r"
        os.system(f'"{FF}" -y -i "{inp}" -ss {s} -t {e-s} -c copy "dl/{out}"')
        if os.path.exists(inp): os.remove(inp)
        return {"ok": True, "filename": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.route("/api/file/<n>")
def api_file(n): return send_file(os.path.join("dl", n), as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
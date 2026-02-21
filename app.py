import os, asyncio, uuid, time
from datetime import datetime
from quart import Quart, render_template_string, request, session, redirect, url_for, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import firebase_admin
from firebase_admin import credentials, db

app = Quart(__name__)
app.secret_key = "VIAH_BASS_KING_PERMANENT_V4"

# --- FIREBASE PERMANENT STORAGE SETUP ---
if not firebase_admin._apps:
    # Ensure serviceAccountKey.json is in your GitHub root
    cred = credentials.Certificate('serviceAccountKey.json') 
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://aipkey-d117c-default-rtdb.firebaseio.com'
    })

ref = db.reference('/')

# --- TELETHON CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = os.environ.get("SESSION") 
GROUP_ID = -5274822277 
ADMIN_ID = "king"
ADMIN_PASS = "king123"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- MODERN WEB-APP UI (Tailwind CSS) ---

BASE_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Viah Bass | Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
        .nav-item-active { color: #3b82f6; border-bottom: 3px solid #3b82f6; }
        body { -webkit-tap-highlight-color: transparent; }
    </style>
</head>
<body class="bg-[#0b0f1a] text-slate-200 font-sans select-none">
    {% if session.logged_in %}
    <div class="fixed bottom-0 left-0 right-0 glass h-16 flex items-center justify-around z-50 rounded-t-3xl border-t border-blue-500/20">
        <a href="/" class="flex flex-col items-center p-2"><i class="fas fa-home"></i><span class="text-[10px] mt-1">Home</span></a>
        <a href="/creator" class="flex flex-col items-center p-2"><i class="fas fa-plus-circle"></i><span class="text-[10px] mt-1">Create</span></a>
        <a href="/analytics" class="flex flex-col items-center p-2"><i class="fas fa-chart-bar"></i><span class="text-[10px] mt-1">Stats</span></a>
        <a href="/logout" class="flex flex-col items-center p-2 text-red-400"><i class="fas fa-power-off"></i><span class="text-[10px] mt-1">Exit</span></a>
    </div>
    {% endif %}

    <div class="max-w-md mx-auto min-h-screen pb-20">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
{% extends "base" %}
{% block content %}
<div class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="w-full glass p-8 rounded-[40px] shadow-2xl text-center">
        <div class="w-20 h-20 bg-blue-600 rounded-full mx-auto mb-6 flex items-center justify-center shadow-lg shadow-blue-500/50">
            <i class="fas fa-shield-alt text-3xl"></i>
        </div>
        <h1 class="text-3xl font-black tracking-tighter italic text-white mb-2">VIAH BASS</h1>
        <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-8">Authorised Admin Access Only</p>
        <form action="/login" method="post" class="space-y-4">
            <input type="text" name="id" placeholder="Admin ID" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 transition-all text-sm font-bold">
            <input type="password" name="pass" placeholder="Password" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 transition-all text-sm font-bold">
            <button type="submit" class="w-full bg-blue-600 py-4 rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl active:scale-95 transition-transform">Unlock Console</button>
        </form>
    </div>
</div>
{% endblock %}
"""

DASHBOARD_CONTENT = """
{% extends "base" %}
{% block content %}
<header class="p-6 flex justify-between items-center">
    <div>
        <p class="text-slate-500 text-[10px] font-black uppercase">Welcome Back</p>
        <h2 class="text-2xl font-black italic">KING OMEGA</h2>
    </div>
    <div class="relative">
        <div class="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
            <i class="fas fa-crown text-white"></i>
        </div>
    </div>
</header>

<div class="p-6 space-y-6">
    <div class="grid grid-cols-2 gap-4">
        <div class="glass p-5 rounded-[30px]">
            <p class="text-[10px] font-black text-slate-500 uppercase">Live Keys</p>
            <h3 class="text-3xl font-black text-blue-400 mt-1">{{api_count}}</h3>
        </div>
        <div class="glass p-5 rounded-[30px]">
            <p class="text-[10px] font-black text-slate-500 uppercase">System Ping</p>
            <h3 class="text-3xl font-black text-green-400 mt-1">32ms</h3>
        </div>
    </div>

    <div class="glass p-6 rounded-[30px]">
        <h4 class="text-sm font-black uppercase mb-4 text-slate-400"><i class="fas fa-bolt mr-2 text-yellow-400"></i> Traffic Analytics</h4>
        <canvas id="trafficChart" class="h-40"></canvas>
    </div>

    <div class="space-y-3">
        <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2">Module Monitoring</h4>
        {% for mod in ['Number', 'Aadhar', 'PAN', 'IP Trace'] %}
        <div class="glass p-4 rounded-2xl flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center"><i class="fas fa-database text-blue-400 text-xs"></i></div>
                <span class="text-sm font-bold">{{mod}} Sync</span>
            </div>
            <span class="text-[9px] font-black bg-green-500/20 text-green-400 px-2 py-1 rounded-full uppercase tracking-tighter">Running</span>
        </div>
        {% endfor %}
    </div>
</div>

<script>
    const ctx = document.getElementById('trafficChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1h', '2h', '3h', '4h', '5h', '6h'],
            datasets: [{
                data: [12, 19, 15, 25, 22, 30],
                borderColor: '#3b82f6',
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 0,
                fill: true,
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            }]
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { display: false }, x: { grid: { display: false } } } }
    });
</script>
{% endblock %}
"""

CREATOR_CONTENT = """
{% extends "base" %}
{% block content %}
<div class="p-6">
    <h2 class="text-2xl font-black italic mb-8">API CREATOR <span class="text-blue-500 text-sm">V4</span></h2>
    
    <form action="/create_api" method="post" class="space-y-5">
        <div class="space-y-2">
            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2">Assignee</label>
            <input type="text" name="user_name" placeholder="User Name" required class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 transition-all font-bold">
        </div>
        
        <div class="space-y-2">
            <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2">Select Target Database</label>
            <select name="module" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 font-bold appearance-none">
                <option value="num">📞 Mobile Registry</option>
                <option value="aadhar">🆔 Aadhar Registry</option>
                <option value="pan">💳 Financial PAN</option>
                <option value="vehicle">🚗 RTO Database</option>
            </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
                <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Start Date</label>
                <input type="date" name="start" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none text-xs font-bold">
            </div>
            <div class="space-y-2">
                <label class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Expiry Date</label>
                <input type="date" name="expiry" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none text-xs font-bold">
            </div>
        </div>

        <button type="submit" class="w-full bg-blue-600 py-5 rounded-[30px] font-black uppercase tracking-widest shadow-xl active:scale-95 transition-all mt-4">Generate Permanent Key</button>
    </form>

    <div class="mt-12 space-y-4">
        <h4 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] px-2">Active Database Keys</h4>
        {% for key, data in apis.items() %}
        <div class="glass p-5 rounded-[30px] space-y-4 border-l-4 border-blue-500">
            <div class="flex justify-between items-center">
                <div>
                    <h5 class="font-black text-white italic underline underline-offset-4 decoration-blue-500">{{data.user}}</h5>
                    <p class="text-[9px] font-mono text-slate-500 mt-2">{{key}}</p>
                </div>
                <div class="flex space-x-1">
                    <form action="/pause_api" method="post"><input type="hidden" name="key" value="{{key}}"><button class="w-8 h-8 bg-yellow-500/10 text-yellow-500 rounded-full flex items-center justify-center"><i class="fas fa-pause text-[10px]"></i></button></form>
                    <form action="/delete_api" method="post"><input type="hidden" name="key" value="{{key}}"><button class="w-8 h-8 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center"><i class="fas fa-trash text-[10px]"></i></button></form>
                </div>
            </div>
            <div class="flex justify-between items-center bg-black/40 p-3 rounded-xl border border-white/5">
                <span class="text-[9px] font-bold text-slate-400">Hits: <span class="text-blue-400">{{data.hits}}</span></span>
                <span class="text-[9px] font-bold text-green-500 uppercase">{{data.status}}</span>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# --- CORE LOGIC & FIREBASE SYNC ---

@app.route('/')
async def index():
    if not session.get('logged_in'): 
        return await render_template_string(BASE_UI.replace('{% block content %}{% endblock %}', LOGIN_CONTENT))
    
    # Firebase se live stats uthana
    apis = ref.child('apis').get() or {}
    return await render_template_string(BASE_UI.replace('{% block content %}{% endblock %}', DASHBOARD_CONTENT), api_count=len(apis))

@app.route('/login', methods=['POST'])
async def login():
    form = await request.form
    if form.get('id') == ADMIN_ID and form.get('pass') == ADMIN_PASS:
        session['logged_in'] = True
        return redirect('/')
    return "ACCESS DENIED"

@app.route('/creator')
async def creator():
    if not session.get('logged_in'): return redirect('/')
    apis = ref.child('apis').get() or {}
    return await render_template_string(BASE_UI.replace('{% block content %}{% endblock %}', CREATOR_CONTENT), apis=apis)

@app.route('/create_api', methods=['POST'])
async def create_api():
    if not session.get('logged_in'): return redirect('/')
    form = await request.form
    new_key = f"VB-{uuid.uuid4().hex[:6].upper()}"
    
    # Firebase Sync
    ref.child('apis').child(new_key).set({
        "user": form.get('user_name'),
        "module": form.get('module'),
        "start": form.get('start'),
        "expiry": form.get('expiry'),
        "status": "active",
        "hits": 0
    })
    return redirect('/creator')

# --- INTELLIGENT 3-SECOND FETCH ENGINE ---
@app.route('/api/fetch')
async def api_fetch():
    api_key = request.args.get('key')
    target = request.args.get('input')
    
    # 1. Firebase Key Validation
    api_data = ref.child('apis').child(api_key).get()
    if not api_data:
        return jsonify({"status": "error", "reason": "Unauthorised API Key"}), 403
    
    if api_data['status'] == 'paused':
        return jsonify({"status": "error", "reason": "API Paused: Maintenance Mode"}), 403

    # 2. Intelligent Delay (Animation feel)
    await asyncio.sleep(3.5)
    
    if not client.is_connected(): await client.connect()
    
    # 3. Telethon Deep Fetch
    cmd = f"/{api_data['module']} {target}"
    sent = await client.send_message(GROUP_ID, cmd)
    
    # 4. Smart Branding & Source Filter
    final_resp = "No match found in secure registry."
    for _ in range(10):
        await asyncio.sleep(1)
        msgs = await client.get_messages(GROUP_ID, limit=5)
        for m in msgs:
            if m.id > sent.id and m.text:
                # Remove Bot traces
                clean = m.text.replace("Bot:", "").replace("@bot", "").strip()
                final_resp = clean
                break
        if "match" not in final_resp: break

    # 5. Permanent Hit Counter
    ref.child('apis').child(api_key).update({"hits": api_data['hits'] + 1})

    return jsonify({
        "engine": "VIAH BASS V4",
        "branding": "POWERED BY KING OMEGA",
        "module": api_data['module'],
        "timestamp": str(datetime.now()),
        "data": final_resp
    })

@app.route('/logout')
async def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    async def main():
        await client.start()
        port = int(os.environ.get("PORT", 9900))
        await app.run_task(host='0.0.0.0', port=port)
    asyncio.run(main())

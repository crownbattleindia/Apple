import os, asyncio, uuid, time, re
from datetime import datetime
from quart import Quart, render_template_string, request, session, redirect, url_for, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import firebase_admin
from firebase_admin import credentials, db

# --- INITIALIZATION ---
app = Quart(__name__)
app.secret_key = "VIAH_BASS_MASTER_KING_V4"

# --- FIREBASE PERMANENT SYNC ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json') 
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://aipkey-d117c-default-rtdb.firebaseio.com'
        })
    ref = db.reference('/')
except Exception as e:
    print(f"CRITICAL: Firebase Sync Failed -> {e}")

# --- TELETHON SESSION CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = os.environ.get("SESSION") 
GROUP_ID = -5274822277 
ADMIN_ID = "king"
ADMIN_PASS = "king123"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- ADVANCED WEB-APP UI (FULL CUSTOMIZATION) ---
MASTER_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Viah Bass | Master Console</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #020617; -webkit-tap-highlight-color: transparent; }
        .glass-card { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(59, 130, 246, 0.2); }
        .gradient-text { background: linear-gradient(to right, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .bottom-nav { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border-top: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body class="text-slate-200 font-sans pb-24">

    {% if not session.logged_in %}
    <div class="flex items-center justify-center min-h-screen p-6">
        <div class="w-full max-w-sm glass-card p-10 rounded-[50px] text-center shadow-[0_0_60px_-15px_rgba(59,130,246,0.4)]">
            <h1 class="text-4xl font-black italic tracking-tighter gradient-text mb-2">VIAH BASS</h1>
            <p class="text-slate-500 text-[10px] uppercase font-black tracking-[0.3em] mb-10">V4 Master Intelligence</p>
            <form action="/login" method="post" class="space-y-4">
                <input type="text" name="id" placeholder="Admin ID" required class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 font-bold transition-all">
                <input type="password" name="pass" placeholder="Password" required class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 font-bold transition-all">
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 py-5 rounded-2xl font-black uppercase text-sm tracking-widest active:scale-95 transition-all">Authenticate</button>
            </form>
        </div>
    </div>
    {% else %}

    <header class="p-8 flex justify-between items-center sticky top-0 z-50 bg-[#020617]/80 backdrop-blur-lg">
        <div>
            <h2 class="text-3xl font-black italic tracking-tighter">CONTROL</h2>
            <div class="flex items-center space-x-2 mt-1">
                <span class="w-2 h-2 bg-green-500 rounded-full animate-ping"></span>
                <span class="text-green-500 text-[10px] font-black uppercase tracking-widest">System Online</span>
            </div>
        </div>
        <div class="flex items-center space-x-4">
            <div class="text-right hidden sm:block">
                <p class="text-[10px] font-black text-slate-500 uppercase">Admin Role</p>
                <p class="text-sm font-bold">King Omega</p>
            </div>
            <div class="w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/20">
                <i class="fas fa-crown text-white text-xl"></i>
            </div>
        </div>
    </header>

    <main class="p-6 space-y-8">
        
        <section class="glass-card p-8 rounded-[40px] shadow-2xl">
            <div class="flex items-center space-x-3 mb-6">
                <i class="fas fa-plus-circle text-blue-500 text-xl"></i>
                <h3 class="text-sm font-black text-slate-300 uppercase tracking-widest">Generate RP Interface</h3>
            </div>
            <form action="/create_api" method="post" class="space-y-5">
                <div class="space-y-2">
                    <label class="text-[10px] font-black text-slate-500 uppercase ml-2">Assigned User</label>
                    <input type="text" name="user" placeholder="Enter Full Name" required class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none focus:border-blue-500 font-bold">
                </div>
                <div class="space-y-2">
                    <label class="text-[10px] font-black text-slate-500 uppercase ml-2">Target Command</label>
                    <select name="module" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none text-blue-400 font-black">
                        <option value="num">📞 Number Lookup (/num)</option>
                        <option value="aadhar">🆔 Aadhar Registry (/aadhar)</option>
                        <option value="pan">💳 PAN Database (/pan)</option>
                        <option value="vehicle">🚗 RC Details (/vehicle)</option>
                        <option value="ip">🌐 IP Geolocation (/ip)</option>
                        <option value="mail">📧 Email Search (/mail)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-blue-600 py-5 rounded-3xl font-black uppercase text-sm tracking-widest shadow-xl shadow-blue-600/20 hover:scale-[1.02] active:scale-95 transition-all">Secure Key Creation</button>
            </form>
        </section>

        <section class="space-y-4">
            <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] px-4 flex justify-between">
                <span>Active Intelligence Nodes</span>
                <span>Total: {{api_count}}</span>
            </h3>
            {% for key, data in apis.items() %}
            <div class="glass-card p-6 rounded-[35px] border-l-4 border-blue-500 group">
                <div class="flex justify-between items-start">
                    <div class="max-w-[65%]">
                        <h4 class="text-xl font-black text-white italic group-hover:text-blue-400 transition-colors">{{data.user}}</h4>
                        <div class="flex items-center space-x-2 mt-2">
                            <code class="text-[10px] font-mono text-slate-500 bg-black/30 px-2 py-1 rounded">{{key}}</code>
                            <i class="fas fa-copy text-slate-600 cursor-pointer hover:text-white" onclick="navigator.clipboard.writeText('{{key}}')"></i>
                        </div>
                        <div class="mt-4 flex flex-wrap gap-2">
                            <span class="text-[9px] font-black bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full border border-blue-500/20 uppercase tracking-tighter">{{data.module}} Active</span>
                            <span class="text-[9px] font-black bg-green-500/10 text-green-400 px-3 py-1 rounded-full border border-green-500/20 uppercase">Firebase Synced</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-3xl font-black text-white leading-none">{{data.hits}}</p>
                        <p class="text-[9px] font-black text-slate-500 uppercase mt-1 tracking-widest">Total Hits</p>
                        <div class="mt-4 flex space-x-2 justify-end">
                            <button class="w-8 h-8 rounded-full bg-yellow-500/10 text-yellow-500 flex items-center justify-center border border-yellow-500/20"><i class="fas fa-pause text-[10px]"></i></button>
                            <button class="w-8 h-8 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center border border-red-500/20"><i class="fas fa-trash text-[10px]"></i></button>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </section>
    </main>

    <nav class="fixed bottom-0 left-0 right-0 h-20 bottom-nav z-50 rounded-t-[40px] flex items-center justify-around px-6">
        <a href="/" class="flex flex-col items-center text-blue-500"><i class="fas fa-home text-lg"></i><span class="text-[9px] font-black uppercase mt-1">Core</span></a>
        <a href="/creator" class="flex flex-col items-center text-slate-500 hover:text-blue-400"><i class="fas fa-plus-circle text-lg"></i><span class="text-[9px] font-black uppercase mt-1">New API</span></a>
        <a href="/analytics" class="flex flex-col items-center text-slate-500 hover:text-blue-400"><i class="fas fa-chart-line text-lg"></i><span class="text-[9px] font-black uppercase mt-1">Traffic</span></a>
        <a href="/logout" class="flex flex-col items-center text-red-500/50 hover:text-red-500"><i class="fas fa-power-off text-lg"></i><span class="text-[9px] font-black uppercase mt-1">Kill</span></a>
    </nav>
    {% endif %}
</body>
</html>
"""

# --- CORE BACKEND LOGIC ---

@app.route('/')
async def index():
    # Firebase se data live fetch karna
    apis = ref.child('apis').get() or {}
    return await render_template_string(MASTER_UI, apis=apis, api_count=len(apis))

@app.route('/login', methods=['POST'])
async def login():
    form = await request.form
    if form.get('id') == ADMIN_ID and form.get('pass') == ADMIN_PASS:
        session['logged_in'] = True
    return redirect('/')

@app.route('/create_api', methods=['POST'])
async def create_api():
    if not session.get('logged_in'): return redirect('/')
    form = await request.form
    new_key = f"VB-{uuid.uuid4().hex[:6].upper()}"
    
    # Firebase Permanent Database Storage
    ref.child('apis').child(new_key).set({
        "user": form.get('user'),
        "module": form.get('module'),
        "status": "active",
        "hits": 0,
        "created_at": str(datetime.now())
    })
    return redirect('/')

# --- THE MASTER INTELLIGENCE ENGINE (RP INTERFACE) ---
@app.route('/api/fetch')
async def api_fetch():
    api_key = request.args.get('key')
    target = request.args.get('input')
    
    # 1. Firebase Validation
    api_data = ref.child('apis').child(api_key).get()
    if not api_data:
        return jsonify({"status": "error", "reason": "Unauthorised Key Access Denied"}), 403

    # 2. Intelligent Search Delay (Anti-Spam & Animation)
    await asyncio.sleep(3.8) # Point-to-point data analysis time
    
    if not client.is_connected(): await client.connect()
    
    # 3. Dynamic Module Command Execution
    module_cmd = api_data['module']
    full_command = f"/{module_cmd} {target}"
    sent = await client.send_message(GROUP_ID, full_command)
    
    # 4. Strict Dual-Layer Filtering
    final_resp = "Analysis complete. Point-to-point match not found in registry."
    for _ in range(12):
        await asyncio.sleep(1.2)
        msgs = await client.get_messages(GROUP_ID, limit=5)
        for m in msgs:
            if m.id > sent.id and m.text:
                # Filter: Username removal, Bot traces, and cleaning
                clean = re.sub(r'@[A-Za-z0-9_]+', '', m.text) # Links/Usernames filter
                clean = clean.replace("Bot:", "").replace("Searching...", "").strip()
                
                # Security Trim: Block prevention
                if len(clean) > 480:
                    clean = clean[:480] + "... [Security Truncated]"
                
                final_resp = clean
                break
        if "Analysis" not in final_resp: break

    # 5. Firebase Hit Synchronisation
    ref.child('apis').child(api_key).update({"hits": api_data['hits'] + 1})

    return jsonify({
        "status": "success",
        "node": "VIAH BASS V4 MASTER ENGINE",
        "branding": "POWERED BY KING OMEGA",
        "module": api_data['module'],
        "timestamp": str(datetime.now()),
        "data_packet": final_resp
    })

@app.route('/logout')
async def logout():
    session.clear()
    return redirect('/')

# --- STARTUP ENGINE ---
if __name__ == '__main__':
    async def main():
        try:
            await client.start()
            port = int(os.environ.get("PORT", 9900))
            await app.run_task(host='0.0.0.0', port=port)
        except Exception as e:
            print(f"Server Startup Failed: {e}")
    asyncio.run(main())

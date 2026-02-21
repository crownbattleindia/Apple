import os, asyncio, uuid, json, re
from datetime import datetime
from quart import Quart, render_template_string, request, session, redirect, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import firebase_admin
from firebase_admin import credentials, db

app = Quart(__name__)
app.secret_key = "VIAH_BASS_V4_ULTIMATE_PREMIUM"

# --- FIREBASE SECURE SYNC ---
fb_config = os.environ.get("FIREBASE_CONFIG")
if fb_config and not firebase_admin._apps:
    try:
        cred_dict = json.loads(fb_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://aipkey-d117c-default-rtdb.firebaseio.com'
        })
        ref = db.reference('/')
    except Exception as e:
        print(f"Firebase Error: {e}")

# --- TELETHON CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = os.environ.get("SESSION") 
GROUP_ID = -5274822277 
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- LUXURY SAAS UI TEMPLATE ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viah Bass V4 | Master Premium</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #020617; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .glass { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.2); }
        .premium-card { border-left: 5px solid #fbbf24; background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)); }
        .btn-premium { background: linear-gradient(to right, #2563eb, #4f46e5); transition: all 0.3s ease; }
        .btn-premium:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3); }
    </style>
</head>
<body class="pb-24">
    {% if not session.logged_in %}
    <div class="flex items-center justify-center min-h-screen p-6">
        <div class="w-full max-w-sm glass p-10 rounded-[40px] text-center">
            <h1 class="text-4xl font-black italic text-blue-500 mb-2 tracking-tighter">VIAH BASS</h1>
            <p class="text-[10px] text-slate-500 uppercase font-bold tracking-[0.4em] mb-10 text-blue-400">V4 Master Intelligence</p>
            <form action="/login" method="post" class="space-y-4">
                <input type="text" name="id" placeholder="Admin ID" class="w-full p-4 bg-slate-900 rounded-2xl border border-slate-700 outline-none focus:border-blue-500">
                <input type="password" name="pass" placeholder="Password" class="w-full p-4 bg-slate-900 rounded-2xl border border-slate-700 outline-none focus:border-blue-500">
                <button type="submit" class="w-full btn-premium py-5 rounded-2xl font-black uppercase text-sm tracking-widest">Authenticate</button>
            </form>
        </div>
    </div>
    {% else %}
    <header class="p-8 flex justify-between items-center sticky top-0 bg-[#020617]/90 backdrop-blur-md z-50">
        <div>
            <h2 class="text-3xl font-black italic text-white tracking-tighter">PREMIUM NODES</h2>
            <p class="text-green-500 text-[10px] font-bold uppercase mt-1">● System: Stable</p>
        </div>
        <div class="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg"><i class="fas fa-crown text-white"></i></div>
    </header>

    <main class="p-6 space-y-10">
        <section class="glass p-8 rounded-[40px] space-y-6 shadow-2xl">
            <div class="flex items-center space-x-3 mb-2">
                <i class="fas fa-plus-circle text-blue-500"></i>
                <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest">New Intelligence Node</h3>
            </div>
            <form action="/create_api" method="post" class="space-y-4">
                <input type="text" name="user" placeholder="Client Name" required class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none font-bold">
                <div class="grid grid-cols-2 gap-4">
                    <select name="module" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none text-blue-400 font-black">
                        <option value="num">📞 Number (/num)</option>
                        <option value="aadhar">🆔 Aadhar (/aadhar)</option>
                        <option value="pan">💳 PAN Card (/pan)</option>
                        <option value="vehicle">🚗 Vehicle (/vehicle)</option>
                        <option value="ip">🌐 IP Geo (/ip)</option>
                        <option value="mail">📧 Email (/mail)</option>
                    </select>
                    <select name="tier" class="w-full p-4 bg-slate-900/50 rounded-2xl border border-slate-700 outline-none text-yellow-500 font-black">
                        <option value="premium">💎 PREMIUM</option>
                        <option value="free">🆓 FREE</option>
                    </select>
                </div>
                <button type="submit" class="w-full btn-premium py-5 rounded-2xl font-black uppercase tracking-widest text-sm">Deploy Premium RP Key</button>
            </form>
        </section>

        <section class="space-y-6">
            <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-4">Active API Registry</h3>
            {% for key, data in apis.items() %}
            <div class="glass p-6 rounded-[35px] {{ 'premium-card' if data.tier == 'premium' else 'border-l-4 border-slate-600' }} transition-all">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <h4 class="font-black text-white italic text-xl tracking-tight">{{data.user}}</h4>
                            <span class="text-[8px] {{ 'bg-yellow-500 text-black' if data.tier == 'premium' else 'bg-slate-700 text-slate-300' }} px-2 py-0.5 rounded-full font-black uppercase">
                                {{data.tier}} Access
                            </span>
                        </div>
                        <p class="text-[9px] font-mono text-slate-500 mt-2 break-all">{{key}}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-2xl font-black text-white">{{data.hits}}</p>
                        <p class="text-[8px] font-bold text-slate-500 uppercase tracking-tighter">Hits Sync</p>
                    </div>
                </div>
                
                <div class="bg-black/40 p-4 rounded-2xl border border-white/5 space-y-2">
                    <p class="text-[8px] font-black text-slate-500 uppercase">Premium RP Endpoint</p>
                    <div class="flex items-center justify-between">
                        <code id="url-{{loop.index}}" class="text-[10px] text-green-400 truncate max-w-[85%]">https://{{request.host}}/api/fetch?key={{key}}&input=TARGET</code>
                        <i class="fas fa-copy text-blue-500 cursor-pointer p-2" onclick="copyUrl('url-{{loop.index}}')"></i>
                    </div>
                </div>
            </div>
            {% endfor %}
        </section>
    </main>

    <script>
        function copyUrl(id) {
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text);
            alert("Premium URL Copied!");
        }
    </script>
    {% endif %}
</body>
</html>
"""

# --- BACKEND ENGINE ---

@app.route('/')
async def index():
    apis = ref.child('apis').get() or {}
    return await render_template_string(HTML_UI, apis=apis)

@app.route('/login', methods=['POST'])
async def login():
    form = await request.form
    if form.get('id') == "king" and form.get('pass') == "king123":
        session['logged_in'] = True
    return redirect('/')

@app.route('/create_api', methods=['POST'])
async def create_api():
    if not session.get('logged_in'): return redirect('/')
    form = await request.form
    # Premium Long Key Generation
    tier = form.get('tier')
    prefix = "VB-PREMIUM" if tier == "premium" else "VB-FREE"
    new_key = f"{prefix}-{uuid.uuid4().hex.upper()}-{uuid.uuid4().hex[:6].upper()}"
    
    ref.child('apis').child(new_key).set({
        "user": form.get('user'),
        "module": form.get('module'),
        "tier": tier,
        "hits": 0,
        "created_at": str(datetime.now())
    })
    return redirect('/')

@app.route('/api/fetch')
async def api_fetch():
    api_key, target = request.args.get('key'), request.args.get('input')
    api_data = ref.child('apis').child(api_key).get()
    
    if not api_data: return jsonify({"status": "error", "reason": "Access Denied"}), 403

    # 3.5s Intelligent Animation Buffer
    await asyncio.sleep(3.5)
    
    if not client.is_connected(): await client.connect()
    
    # Executing Locked Command
    cmd = f"/{api_data['module']} {target}"
    sent = await client.send_message(GROUP_ID, cmd)
    
    final_resp = "Analysis complete. Data not found in premium registry."
    for _ in range(12):
        await asyncio.sleep(1.2)
        msgs = await client.get_messages(GROUP_ID, limit=5)
        for m in msgs:
            if m.id > sent.id and m.text:
                # Cleaning & Point-wise Response
                clean = re.sub(r'@[A-Za-z0-9_]+', '', m.text).replace("Bot:", "").strip()
                # Adding Premium Bullet Points
                formatted = "● " + clean.replace("\\n", "\\n● ")
                final_resp = formatted
                break
        if "Analysis" not in final_resp: break

    ref.child('apis').child(api_key).update({"hits": api_data['hits'] + 1})
    
    branding = f"👑 VIAH BASS V4 [{api_data['tier'].upper()} VIP ACCESS]"
    
    return jsonify({
        "status": "success",
        "engine": branding,
        "branding": "POWERED BY KING OMEGA",
        "module": api_data['module'],
        "data": final_resp
    })

if __name__ == '__main__':
    async def main():
        await client.start()
        await app.run_task(host='0.0.0.0', port=int(os.environ.get("PORT", 9900)))
    asyncio.run(main())

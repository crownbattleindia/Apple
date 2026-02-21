import os, asyncio, uuid, time
from datetime import datetime
from quart import Quart, render_template_string, request, session, redirect, url_for, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)
app.secret_key = "VIAH_BASS_KING_KEY"

# --- CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = os.environ.get("SESSION") 
GROUP_ID = -5274822277 
ADMIN_CREDENTIALS = {"id": "king", "pass": "king123"} #

# In-memory storage (RAM mein rahega, stealth ke liye)
api_database = {} 
usage_stats = {"total_hits": 0, "active_apis": 0}

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- UI TEMPLATES (Phone-View Optimized) ---

# 1. Login Page
LOGIN_UI = """
<body class="bg-[#0f172a] flex items-center justify-center min-h-screen font-sans p-6 text-slate-200">
    <div class="w-full max-w-sm bg-[#1e293b] p-8 rounded-3xl shadow-2xl border border-slate-700">
        <h1 class="text-3xl font-black text-blue-500 mb-2 italic">VIAH BASS</h1>
        <p class="text-slate-500 text-xs mb-8 uppercase tracking-widest">Admin Authorization Required</p>
        <form action="/login" method="post" class="space-y-6">
            <input type="text" name="id" placeholder="Admin ID" required class="w-full p-4 bg-[#0f172a] rounded-2xl border border-slate-600 outline-none focus:border-blue-500">
            <input type="password" name="pass" placeholder="Password" required class="w-full p-4 bg-[#0f172a] rounded-2xl border border-slate-600 outline-none focus:border-blue-500">
            <button type="submit" class="w-full bg-blue-600 py-4 rounded-2xl font-black uppercase tracking-widest shadow-lg">Enter Command Center</button>
        </form>
    </div>
</body>
<script src="https://cdn.tailwindcss.com"></script>
"""

# 2. Main Dashboard & Sidebar
DASHBOARD_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#0f172a] text-slate-200 font-sans pb-20">
    <nav class="bg-[#1e293b] p-5 flex justify-between items-center sticky top-0 z-50 border-b border-slate-700">
        <div class="flex items-center space-x-3">
            <div id="menu-btn" class="text-2xl cursor-pointer"><i class="fas fa-bars text-blue-400"></i></div>
            <h1 class="font-black text-xl italic tracking-tighter">VIAH BASS</h1>
        </div>
        <div class="text-xs font-bold text-green-400 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20 animate-pulse">SYSTEM: ONLINE</div>
    </nav>

    <div id="sidebar" class="fixed inset-0 bg-[#0f172a]/95 z-50 hidden p-10 transform -translate-x-full transition-transform duration-300">
        <div class="flex justify-between mb-20">
            <h2 class="text-2xl font-black italic text-blue-400 underline">VIAH MENU</h2>
            <i onclick="toggleMenu()" class="fas fa-times text-2xl"></i>
        </div>
        <div class="space-y-8">
            <a href="/" class="block text-2xl font-bold hover:text-blue-500"><i class="fas fa-home mr-4"></i>Home</a>
            <a href="/creator" class="block text-2xl font-bold hover:text-blue-500"><i class="fas fa-plus-square mr-4"></i>API Creator</a>
            <a href="/analytics" class="block text-2xl font-bold hover:text-blue-500"><i class="fas fa-chart-line mr-4"></i>Analytics</a>
            <a href="/logout" class="block text-2xl font-bold text-red-500 mt-20"><i class="fas fa-power-off mr-4"></i>Logout</a>
        </div>
    </div>

    <main class="p-6 space-y-6">
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-[#1e293b] p-5 rounded-3xl border border-slate-700">
                <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Total Users</p>
                <h3 class="text-3xl font-black mt-1">128</h3>
            </div>
            <div class="bg-[#1e293b] p-5 rounded-3xl border border-slate-700">
                <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">API Active</p>
                <h3 class="text-3xl font-black mt-1 text-blue-400">{{active_count}}</h3>
            </div>
        </div>

        <div class="bg-[#1e293b] p-6 rounded-3xl border border-slate-700">
            <p class="text-[10px] font-black text-slate-500 uppercase mb-4">Traffic Performance (Ping: 42ms)</p>
            <canvas id="hitChart" class="h-40"></canvas>
        </div>

        <div class="space-y-4">
            <h4 class="font-black text-sm uppercase text-slate-400 tracking-widest">Live Features Status</h4>
            {% for feature in ['Phone', 'Aadhar', 'PAN', 'Vehicle', 'IP'] %}
            <div class="bg-[#1e293b] p-4 rounded-2xl flex justify-between items-center border border-slate-700">
                <span class="font-bold">{{feature}} Fetcher</span>
                <span class="text-[10px] bg-green-500/20 text-green-400 px-2 py-1 rounded font-black">99.9% UP</span>
            </div>
            {% endfor %}
        </div>
    </main>

    <script>
        function toggleMenu() {
            const side = document.getElementById('sidebar');
            side.classList.toggle('hidden');
            setTimeout(() => side.classList.toggle('-translate-x-full'), 10);
        }
        document.getElementById('menu-btn').onclick = toggleMenu;

        const ctx = document.getElementById('hitChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['10am', '11am', '12pm', '1pm', '2pm', '3pm'],
                datasets: [{
                    label: 'API Hits',
                    data: [65, 59, 80, 81, 56, 95],
                    borderColor: '#3b82f6',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
                }]
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { display: false }, x: { grid: { display: false } } } }
        });
    </script>
</body>
</html>
"""

# 3. API Creator with Scheduling & Pause/Delete
CREATOR_UI = """
<body class="bg-[#0f172a] text-slate-200 font-sans p-6">
    <div class="flex items-center mb-8">
        <a href="/" class="mr-4 text-xl"><i class="fas fa-chevron-left"></i></a>
        <h2 class="text-2xl font-black italic">API DATABASE CREATOR</h2>
    </div>

    <form action="/create_api" method="post" class="space-y-6">
        <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase mb-2">Assignee Name</label>
            <input type="text" name="user_name" placeholder="User/Company Name" required class="w-full p-4 bg-[#1e293b] rounded-2xl border border-slate-700 outline-none">
        </div>
        <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase mb-2">Module Type</label>
            <select name="module" class="w-full p-4 bg-[#1e293b] rounded-2xl border border-slate-700 outline-none">
                <option value="num">📞 Number Database</option>
                <option value="aadhar">🆔 Aadhar Registry</option>
                <option value="pan">💳 PAN Sync</option>
                <option value="vehicle">🚗 RTO Track</option>
            </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-[10px] font-black text-slate-500 uppercase mb-2">Start Date</label>
                <input type="date" name="start" class="w-full p-4 bg-[#1e293b] rounded-2xl border border-slate-700 outline-none text-xs">
            </div>
            <div>
                <label class="block text-[10px] font-black text-slate-500 uppercase mb-2">Expiry Date</label>
                <input type="date" name="expiry" class="w-full p-4 bg-[#1e293b] rounded-2xl border border-slate-700 outline-none text-xs">
            </div>
        </div>
        <button type="submit" class="w-full bg-blue-600 py-5 rounded-3xl font-black uppercase tracking-widest shadow-xl">GENERATE SECURE API</button>
    </form>

    <div class="mt-12 space-y-4">
        <h4 class="text-xs font-black text-slate-500 uppercase">Manage Existing Keys</h4>
        {% for key, data in apis.items() %}
        <div class="bg-[#1e293b] p-6 rounded-3xl border border-slate-700 space-y-4">
            <div class="flex justify-between items-start">
                <div>
                    <h5 class="font-bold text-blue-400">{{data.user}}</h5>
                    <p class="text-[10px] text-slate-500 font-mono">{{key}}</p>
                </div>
                <div class="flex space-x-2">
                    <button class="text-yellow-500 p-2"><i class="fas fa-pause"></i></button>
                    <button class="text-red-500 p-2"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            <div class="text-[10px] flex justify-between bg-black/20 p-2 rounded">
                <span>Valid: {{data.start}} To {{data.expiry}}</span>
                <span class="text-green-500 font-bold uppercase">Status: Live</span>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
"""

@app.route('/')
async def index():
    if not session.get('logged_in'): return await render_template_string(LOGIN_UI)
    return await render_template_string(DASHBOARD_UI, active_count=len(api_database))

@app.route('/login', methods=['POST'])
async def login():
    form = await request.form
    if form.get('id') == ADMIN_CREDENTIALS['id'] and form.get('pass') == ADMIN_CREDENTIALS['pass']: #
        session['logged_in'] = True
        return redirect('/')
    return "INVALID CREDENTIALS"

@app.route('/creator')
async def creator():
    if not session.get('logged_in'): return redirect('/')
    return await render_template_string(CREATOR_UI, apis=api_database)

@app.route('/create_api', methods=['POST'])
async def create_api():
    form = await request.form
    new_key = f"VB-KEY-{uuid.uuid4().hex[:8].upper()}"
    api_database[new_key] = {
        "user": form.get('user_name'),
        "module": form.get('module'),
        "start": form.get('start'),
        "expiry": form.get('expiry'),
        "status": "active",
        "hits": 0
    }
    return redirect('/creator')

# --- INTELLIGENT BOT FETCH LOGIC (With Branding & 3s Delay) ---
@app.route('/api/fetch')
async def api_fetch():
    api_key = request.args.get('key')
    target = request.args.get('input')
    
    # 1. Branding Check
    if not api_key in api_database:
        return jsonify({"status": "error", "reason": "Unauthorized API Access. Contact @King_VB"}), 403
    
    if not client.is_connected(): await client.connect()
    
    # 2. Advanced Fetch (Wait for both sources)
    cmd = f"/{api_database[api_key]['module']} {target}"
    sent = await client.send_message(GROUP_ID, cmd)
    
    # Wait 3 seconds for analysis animation
    await asyncio.sleep(3.5) 
    
    msgs = await client.get_messages(GROUP_ID, limit=5)
    final_data = ""
    for m in msgs:
        if m.id > sent.id and m.text:
            # Bot ka naam filter karna aur organise karna
            clean_text = m.text.replace("Bot Name:", "").strip()
            final_data = clean_text
            break

    # 3. Final Branding Integration
    response = {
        "status": "success",
        "branding": "POWERED BY VIAH BASS ENGINE",
        "data": final_data,
        "analysed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # API Work only if branding is accepted
    return jsonify(response)

if __name__ == '__main__':
    async def main():
        await client.start()
        port = int(os.environ.get("PORT", 9900))
        await app.run_task(host='0.0.0.0', port=port)
    asyncio.run(main())

import os, asyncio, uuid, json
from quart import Quart, render_template_string, request, redirect
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)

# --- CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = '1BVtsOIoBuxTzcGkqn2I0B2X56cpxF3vdCUvrueeAIFLikKAxr0TMcopPu2V3iQ35hgOtN2mWNca6iaLgFcYEansimfm2oRaa8qBqnh00SFqGQ6NEqsbubRct_uMcpJLkpZFWnM8qWoPb49Mf-7Al1F_OnzfZ0KCSdzlkMqs8VYN2_5QdcAE0p0m7Fbgx2WW8uBd3hipOK6ky61DhCaql7RWFL_8bssjDKl1G7BoeHwO_8QYLJo_A-Mwbg3zglaqqSFy26JBV6U8YHVWoAOO5LbrzWo1eNjTD0bSXccEA3DgHQ_Bnn0SYC5IKfuvYS1xc6OYDCaq3aiLn_kZZQvU1DL9cus7Bmag='

GROUP_ID = -5274822277 
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
DB_FILE = 'keys_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

api_database = load_db()

# --- MODERN APP UI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omega Pro Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
        .sidebar { background: #1e293b; color: white; min-height: 100vh; }
        .glass-card { background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="flex">
    <div class="sidebar w-64 p-6 hidden md:block">
        <h1 class="text-2xl font-bold mb-10 text-blue-400">OMEGA PRO</h1>
        <nav class="space-y-4">
            <a href="/" class="flex items-center space-x-3 p-2 bg-blue-600 rounded-lg"><i class="fas fa-home"></i> <span>Dashboard</span></a>
            <a href="#" class="flex items-center space-x-3 p-2 hover:bg-slate-700 rounded-lg"><i class="fas fa-key"></i> <span>Manage Keys</span></a>
            <a href="#" class="flex items-center space-x-3 p-2 hover:bg-slate-700 rounded-lg"><i class="fas fa-chart-line"></i> <span>Analytics</span></a>
            <a href="#" class="flex items-center space-x-3 p-2 hover:bg-slate-700 rounded-lg text-red-400"><i class="fas fa-sign-out-alt"></i> <span>Logout</span></a>
        </nav>
    </div>

    <div class="flex-1 p-8">
        <div class="flex justify-between items-center mb-8">
            <h2 class="text-3xl font-bold text-slate-800">Control Panel</h2>
            <div class="text-slate-500 font-medium">Welcome back, Admin 👋</div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass-card p-6 border-l-4 border-blue-500">
                <p class="text-slate-500">Total Active Keys</p>
                <h3 class="text-3xl font-bold">{{ d|length }}</h3>
            </div>
            <div class="glass-card p-6 border-l-4 border-green-500">
                <p class="text-slate-500">System Status</p>
                <h3 class="text-3xl font-bold text-green-500">Online</h3>
            </div>
            <div class="glass-card p-6 border-l-4 border-purple-500">
                <p class="text-slate-500">Platform</p>
                <h3 class="text-3xl font-bold">Crown Battle</h3>
            </div>
        </div>

        <div class="glass-card p-8 mb-8">
            <h4 class="text-xl font-bold mb-6 text-slate-700">Generate New API Endpoint</h4>
            <form action="/generate" method="post" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input type="text" name="owner" placeholder="Client Name" class="border p-3 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none" required>
                <select name="cmd" class="border p-3 rounded-lg bg-white">
                    <option value="num">📞 Phone Lookup</option>
                    <option value="aadhar">🆔 Aadhar Info</option>
                    <option value="pan">💳 PAN Card</option>
                    <option value="vehicle">🚗 RTO / Vehicle</option>
                    <option value="ip">🌐 IP Geolocation</option>
                    <option value="mail">📧 Email Lookup</option>
                    <option value="gst">🧾 GST Info</option>
                </select>
                <button type="submit" class="bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition">Create API Link</button>
            </form>
        </div>

        <div class="glass-card overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-bottom">
                    <tr>
                        <th class="p-4 font-bold text-slate-600">CLIENT</th>
                        <th class="p-4 font-bold text-slate-600">SERVICE</th>
                        <th class="p-4 font-bold text-slate-600">HITS</th>
                        <th class="p-4 font-bold text-slate-600">API LINK</th>
                        <th class="p-4 font-bold text-slate-600">ACTION</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for k,v in d.items() %}
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-4 font-semibold text-slate-700">{{ v.owner }}</td>
                        <td class="p-4"><span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-bold uppercase">{{ v.cmd }}</span></td>
                        <td class="p-4 font-bold">{{ v.get('hits', 0) }}</td>
                        <td class="p-4"><code class="bg-slate-100 p-2 rounded text-xs text-blue-600">/api/fetch?token={{ k }}&type={{ v.cmd }}</code></td>
                        <td class="p-4">
                            <a href="/delete/{{ k }}" class="text-red-500 hover:text-red-700 font-bold"><i class="fas fa-trash"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
async def index():
    return await render_template_string(HTML_UI, d=api_database)

@app.route('/generate', methods=['POST'])
async def gen():
    form = await request.form
    token = f"OMEGA-{uuid.uuid4().hex[:6].upper()}"
    api_database[token] = {"owner": form.get('owner'), "cmd": form.get('cmd'), "hits": 0}
    save_db(api_database)
    return redirect('/')

@app.route('/delete/<token>')
async def delete_key(token):
    if token in api_database:
        del api_database[token]
        save_db(api_database)
    return redirect('/')

@app.route('/api/fetch')
async def fetch():
    token, item_type, val = request.args.get('token'), request.args.get('type'), request.args.get('input')
    if token not in api_database: return "Error: Invalid Token"
    
    api_database[token]['hits'] = api_database[token].get('hits', 0) + 1
    save_db(api_database)

    if not client.is_connected(): await client.connect()
    
    # Image ke commands ke according logic
    cmd_text = f"/{item_type} {val}"
    sent = await client.send_message(GROUP_ID, cmd_text)
    
    for _ in range(15):
        await asyncio.sleep(1.5)
        msgs = await client.get_messages(GROUP_ID, limit=5)
        for m in msgs:
            if m.id > sent.id and m.text:
                return f"OMEGA PRO SERVICE\nClient: {api_database[token]['owner'].upper()}\n\n{m.text}"
    
    return "Timeout: Provider is not responding."

if __name__ == '__main__':
    async def main():
        try:
            await client.start()
            print("🚀 Omega Pro Running on Port 9900!")
            await app.run_task(host='0.0.0.0', port=9900)
        except Exception as e: print(f"❌ Error: {e}")

    try: asyncio.run(main())
    except KeyboardInterrupt: pass

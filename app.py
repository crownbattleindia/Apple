import os, asyncio, uuid
from quart import Quart, render_template_string, request, session, redirect, url_for
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)
app.secret_key = "VIAH_BASS_ULTIMATE_SECRET"

# --- CONFIG ---
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
STRING_SESSION = os.environ.get("SESSION") 
GROUP_ID = -5274822277 

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- DASHBOARD UI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viah Bass | Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#0f172a] text-slate-200 font-sans">

    <div class="flex min-h-screen">
        
        <div class="w-64 bg-[#1e293b] border-r border-slate-700 hidden md:block">
            <div class="p-6">
                <h1 class="text-xl font-black text-blue-400 tracking-tighter italic underline decoration-2">VIAH BASS</h1>
                <p class="text-[10px] text-slate-500 font-bold uppercase mt-1">Enterprise Node v4.0</p>
            </div>
            <nav class="mt-6 space-y-1 px-4">
                <a href="#" class="flex items-center space-x-3 p-3 bg-blue-600 rounded-lg text-white font-bold transition">
                    <i class="fas fa-th-large w-5"></i><span>Dashboard</span>
                </a>
                <a href="#" class="flex items-center space-x-3 p-3 hover:bg-slate-700 rounded-lg transition">
                    <i class="fas fa-user w-5 text-slate-400"></i><span>My Profile</span>
                </a>
                <a href="#" class="flex items-center space-x-3 p-3 hover:bg-slate-700 rounded-lg transition">
                    <i class="fas fa-key w-5 text-slate-400"></i><span>API Management</span>
                </a>
                <a href="#" class="flex items-center space-x-3 p-3 hover:bg-slate-700 rounded-lg transition text-red-400 mt-20">
                    <i class="fas fa-power-off w-5"></i><span>Logout</span>
                </a>
            </nav>
        </div>

        <div class="flex-1">
            <header class="bg-[#1e293b]/50 backdrop-blur-md border-b border-slate-700 p-4 sticky top-0 z-10 flex justify-between items-center">
                <div class="flex items-center space-x-4">
                    <span class="bg-green-500/10 text-green-400 text-[10px] px-2 py-1 rounded border border-green-500/20 font-bold animate-pulse">SYSTEM LIVE</span>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm font-semibold text-slate-400">Welcome, Omega</span>
                    <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center font-bold text-sm">OP</div>
                </div>
            </header>

            <main class="p-8 space-y-8">
                
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    <div class="lg:col-span-1 bg-gradient-to-br from-blue-900 to-indigo-900 p-6 rounded-3xl shadow-xl border border-blue-400/20">
                        <div class="flex justify-between items-start mb-6">
                            <h3 class="font-black text-lg text-white">GENERATE API</h3>
                            <i class="fas fa-code text-blue-300"></i>
                        </div>
                        <p class="text-blue-100 text-xs mb-6 leading-relaxed">Create a secure endpoint for external data integration and third-party sync.</p>
                        <button onclick="alert('API Key Generated: VB-'+Math.random().toString(36).substring(7).toUpperCase())" 
                                class="w-full bg-white text-blue-900 font-black py-3 rounded-xl hover:bg-blue-50 transition shadow-lg text-sm">
                            CREATE NEW API KEY
                        </button>
                    </div>

                    <div class="bg-[#1e293b] p-6 rounded-3xl border border-slate-700 flex flex-col justify-between">
                        <p class="text-slate-500 text-[10px] font-black uppercase tracking-widest">Active Connection</p>
                        <h4 class="text-4xl font-black text-white tracking-tighter mt-2">TELETHON <span class="text-blue-500">v2</span></h4>
                        <div class="mt-4 flex space-x-2">
                            <span class="h-1 flex-1 bg-blue-600 rounded-full"></span>
                            <span class="h-1 flex-1 bg-slate-600 rounded-full"></span>
                        </div>
                    </div>

                    <div class="bg-[#1e293b] p-6 rounded-3xl border border-slate-700 flex flex-col justify-between">
                        <p class="text-slate-500 text-[10px] font-black uppercase tracking-widest">Global Sync Count</p>
                        <h4 class="text-4xl font-black text-white tracking-tighter mt-2">1,204 <span class="text-sm text-slate-500">Hits</span></h4>
                        <p class="text-[10px] text-green-400 mt-4">+12% from last session</p>
                    </div>
                </div>

                <div class="bg-[#1e293b] rounded-3xl shadow-2xl border border-slate-700 overflow-hidden">
                    <div class="p-6 border-b border-slate-700 bg-slate-800/30">
                        <h3 class="font-black text-lg flex items-center">
                            <i class="fas fa-shield-halved mr-3 text-blue-400"></i> ASSET LOOKUP ENGINE
                        </h3>
                    </div>
                    <div class="p-8">
                        <form action="/fetch" method="get" class="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div class="space-y-2">
                                <label class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Module Selection</label>
                                <select name="type" class="w-full p-4 bg-[#0f172a] border border-slate-600 rounded-2xl focus:border-blue-500 outline-none text-sm font-bold appearance-none">
                                    <option value="num">📞 Number Verification</option>
                                    <option value="aadhar">🆔 Aadhar Registry</option>
                                    <option value="pan">💳 Financial PAN Sync</option>
                                    <option value="vehicle">🚗 RTO/Vehicle Trace</option>
                                    <option value="ip">🌐 IP Geolocation</option>
                                    <option value="mail">📧 Electronic Mail Trace</option>
                                </select>
                            </div>
                            <div class="space-y-2">
                                <label class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Target Identifier</label>
                                <input type="text" name="input" placeholder="Input Value..." required 
                                       class="w-full p-4 bg-[#0f172a] border border-slate-600 rounded-2xl focus:border-blue-500 outline-none text-sm font-medium">
                            </div>
                            <div class="md:col-span-2 mt-4">
                                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-5 rounded-2xl shadow-xl transition-all uppercase tracking-widest text-sm">
                                    Execute Secure Data Fetch
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

            </main>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
async def index():
    return await render_template_string(HTML_UI)

@app.route('/fetch')
async def fetch():
    if not STRING_SESSION:
        return "CRITICAL: SESSION Variable Missing in Settings"
    
    item_type = request.args.get('type')
    val = request.args.get('input')
    
    if not client.is_connected(): await client.connect()
    
    cmd_text = f"/{item_type} {val}"
    sent = await client.send_message(GROUP_ID, cmd_text)
    
    response_text = "❌ TIMEOUT: Provider node not responding."
    for _ in range(15):
        await asyncio.sleep(1.5)
        msgs = await client.get_messages(GROUP_ID, limit=5)
        for m in msgs:
            if m.id > sent.id and m.text:
                response_text = m.text
                break
        if "TIMEOUT" not in response_text: break

    return f"""
    <body style="background:#0f172a; padding:40px; color:#e2e8f0; font-family:monospace;">
        <div style="background:#1e293b; padding:30px; border-radius:30px; max-width:900px; margin:auto; border:1px solid #334155; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);">
            <h2 style="color:#60a5fa; border-bottom:2px solid #334155; padding-bottom:15px; margin-bottom:20px; font-weight:900;">NODE RESPONSE LOGS</h2>
            <pre style="white-space: pre-wrap; font-size:14px; background:#0f172a; padding:25px; border-radius:20px; border:1px solid #334155; line-height:1.8; color:#94a3b8;">{response_text}</pre>
            <br>
            <button onclick="window.history.back()" style="background:#3b82f6; color:white; padding:15px 30px; border:none; border-radius:15px; cursor:pointer; font-weight:900; text-transform:uppercase; letter-spacing:1px; font-size:12px;">Initiate New Query</button>
        </div>
    </body>
    """

if __name__ == '__main__':
    async def main():
        try:
            await client.start()
            port = int(os.environ.get("PORT", 9900))
            await app.run_task(host='0.0.0.0', port=port)
        except Exception as e: print(f"Error: {e}")
    asyncio.run(main())

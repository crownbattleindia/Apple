import os, asyncio
from quart import Quart, render_template_string, request
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)

# --- CONFIG (Environment Se Uthayega) ---
# Yahan humne string hata di hai taaki koi leak na ho
API_ID = 35717345
API_HASH = 'db33bd6a35e54a1aec297d3e28262b2a'
# Render ki settings mein 'SESSION' naam ka variable banana
STRING_SESSION = os.environ.get("SESSION") 

GROUP_ID = -5274822277 
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- PROFESSIONAL VIAH BASS UI ---
HTML_UI = """
<body style="background:#f0f2f5; font-family:sans-serif; margin:0;">
    <div style="background:#1e3a8a; color:white; padding:20px; text-align:center;">
        <h1 style="margin:0; font-size:24px;">VIAH BASS - Internal Asset Query</h1>
    </div>
    <div style="max-width:600px; margin:40px auto; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        <p style="color:#666; font-size:14px; margin-bottom:20px;">System Status: <span style="color:green;">● Online</span></p>
        <form action="/fetch" method="get">
            <div style="margin-bottom:15px;">
                <label style="display:block; font-weight:bold; margin-bottom:5px;">Service Module:</label>
                <select name="type" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px;">
                    <option value="num">Phone Verification</option>
                    <option value="aadhar">Identity Check</option>
                    <option value="pan">Tax ID Verify</option>
                    <option value="vehicle">RTO Asset Sync</option>
                </select>
            </div>
            <div style="margin-bottom:20px;">
                <label style="display:block; font-weight:bold; margin-bottom:5px;">Query ID:</label>
                <input type="text" name="input" placeholder="Enter details..." required style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box;">
            </div>
            <button type="submit" style="width:100%; background:#1e3a8a; color:white; padding:12px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">START REAL-TIME SYNC</button>
        </form>
    </div>
</body>
"""

@app.route('/')
async def index():
    return await render_template_string(HTML_UI)

@app.route('/fetch')
async def fetch():
    if not STRING_SESSION:
        return "Error: Environment Variable 'SESSION' missing! 😡"
    
    item_type = request.args.get('type')
    val = request.args.get('input')
    
    if not client.is_connected(): await client.connect()
    
    cmd_text = f"/{item_type} {val}"
    sent = await client.send_message(GROUP_ID, cmd_text)
    
    response_text = "❌ Timeout: Provider is not responding."
    for _ in range(12):
        await asyncio.sleep(1.5)
        msgs = await client.get_messages(GROUP_ID, limit=3)
        for m in msgs:
            if m.id > sent.id and m.text:
                response_text = m.text
                break
        if "Timeout" not in response_text: break

    return f"""
    <div style="font-family:monospace; padding:20px; background:#f8f9fa;">
        <h3 style="color:#1e3a8a;">LIVE QUERY RESULT</h3>
        <pre style="white-space: pre-wrap;">{response_text}</pre>
        <hr>
        <button onclick="window.history.back()">Back</button>
    </div>
    """

if __name__ == '__main__':
    async def main():
        await client.start()
        port = int(os.environ.get("PORT", 9900))
        await app.run_task(host='0.0.0.0', port=port)

    try:
        asyncio.run(main())
    except KeyboardInterrupt: pass


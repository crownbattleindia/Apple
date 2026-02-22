import os
import json
import time
import asyncio
import re
import random
import string
import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from telethon import TelegramClient
from telethon.sessions import StringSession
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# ========== CONFIG - आपकी दी हुई VALUES ==========
API_ID = 30142881
API_HASH = 'e7bb86fade6290a73ae6bb35a85f3725'
SESSION_STR = '1BVtsOIoBuxTzcGkqn2I0B2X56cpxF3vdCUvrueeAIFLikKAxr0TMcopPu2V3iQ35hgOtN2mWNca6iaLgFcYEansimfm2oRaa8qBqnh00SFqGQ6NEqsbubRct_uMcpJLkpZFWnM8qWoPb49Mf-7Al1F_OnzfZ0KCSdzlkMqs8VYN2_5QdcAE0p0m7Fbgx2WW8uBd3hipOK6ky61DhCaql7RWFL_8bssjDKl1G7BoeHwO_8QYLJo_A-Mwbg3zglaqqSFy26JBV6U8YHVWoAOO5LbrzWo1eNjTD0bSXccEA3DgHQ_Bnn0SYC5IKfuvYS1xc6OYDCaq3aiLn_kZZQvU1DL9cus7Bmag='
GROUP_USERNAME = -5274822277
MASTER_KEY = "DEV-786"
BRAND = "🦋⃟‌⃟ ͥ ͣ ͫ 𝕯єν 🖤࿐"
START_TIME = time.time()

# ========== PostgreSQL Database Connection ==========
DATABASE_URL = "postgresql://neondb_owner:npg_ZjnWpV8rzCx6@ep-snowy-dust-aiga7qnv-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        dsn=DATABASE_URL,
        cursor_factory=RealDictCursor
    )
    print("✅ Database connected successfully!")
    
    # Initialize database tables
    init_database()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    db_pool = None

def get_db_connection():
    """Get connection from pool"""
    if db_pool:
        return db_pool.getconn()
    return None

def release_db_connection(conn):
    """Release connection back to pool"""
    if db_pool and conn:
        db_pool.putconn(conn)

def init_database():
    """Create tables if they don't exist"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # API Keys table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key_value VARCHAR(50) UNIQUE NOT NULL,
                owner_name VARCHAR(100),
                owner_contact VARCHAR(50),
                is_active BOOLEAN DEFAULT true,
                created_at BIGINT NOT NULL,
                expiry_time BIGINT,
                usage_count INTEGER DEFAULT 0,
                last_used BIGINT,
                max_usage INTEGER DEFAULT -1,
                allowed_apis TEXT[] DEFAULT '{}',
                created_by VARCHAR(50),
                notes TEXT
            )
        """)
        
        # API usage logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_usage_logs (
                id SERIAL PRIMARY KEY,
                key_value VARCHAR(50),
                api_endpoint VARCHAR(50),
                ip_address VARCHAR(50),
                requested_at BIGINT NOT NULL,
                response_time FLOAT,
                success BOOLEAN
            )
        """)
        
        # Commands/APIs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS available_apis (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                endpoint VARCHAR(100),
                description TEXT,
                is_active BOOLEAN DEFAULT true
            )
        """)
        
        # Insert default APIs if not exists
        default_apis = [
            ('numinfo', '/api/numinfo', 'Phone Number Information'),
            ('aadhar', '/api/aadhar', 'Aadhar Card Details'),
            ('family', '/api/family', 'Family Details'),
            ('insta', '/api/insta', 'Instagram Profile Info'),
            ('ffuid', '/api/ffuid', 'Free Fire UID Info'),
            ('rto', '/api/rto', 'RTO Vehicle Info'),
            ('vehicle', '/api/vehicle', 'Vehicle Details')
        ]
        
        for name, endpoint, desc in default_apis:
            cur.execute("""
                INSERT INTO available_apis (name, endpoint, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (name, endpoint, desc))
        
        conn.commit()
        cur.close()
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    finally:
        release_db_connection(conn)

def generate_api_key(prefix="DEV"):
    """Generate unique API key"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    timestamp = hex(int(time.time()))[2:].upper()
    return f"{prefix}-{timestamp}-{random_part}"

def check_api_key(key, endpoint=None):
    """Check if API key is valid and has permission"""
    if key == MASTER_KEY:
        return True, "master", None
    
    conn = get_db_connection()
    if not conn:
        return False, None, "Database connection error"
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT key_value, owner_name, is_active, expiry_time, usage_count, max_usage, allowed_apis 
            FROM api_keys WHERE key_value = %s
        """, (key,))
        
        key_data = cur.fetchone()
        cur.close()
        
        if not key_data:
            return False, None, "Invalid API key"
        
        # Check if active
        if not key_data['is_active']:
            return False, None, "API key is deactivated"
        
        # Check expiry
        if key_data['expiry_time'] and key_data['expiry_time'] < time.time():
            return False, None, "API key has expired"
        
        # Check usage limit
        if key_data['max_usage'] > 0 and key_data['usage_count'] >= key_data['max_usage']:
            return False, None, "API key usage limit exceeded"
        
        # Check API permission if endpoint specified
        if endpoint and key_data['allowed_apis'] and len(key_data['allowed_apis']) > 0:
            if endpoint not in key_data['allowed_apis']:
                return False, None, f"API key not authorized for {endpoint}"
        
        return True, key_data['owner_name'], None
        
    except Exception as e:
        return False, None, str(e)
    finally:
        release_db_connection(conn)

def log_api_usage(key, endpoint, ip, response_time, success):
    """Log API usage to database"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_usage_logs (key_value, api_endpoint, ip_address, requested_at, response_time, success)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (key, endpoint, ip, int(time.time()), response_time, success))
        
        # Update usage count
        cur.execute("""
            UPDATE api_keys SET usage_count = usage_count + 1, last_used = %s
            WHERE key_value = %s
        """, (int(time.time()), key))
        
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging usage: {e}")
    finally:
        release_db_connection(conn)

# ========== Telegram Bot Functions ==========
async def get_bot_response(command, value):
    client = None
    try:
        client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            return False, "Session expired", None
        
        group = await client.get_entity(GROUP_USERNAME)
        
        msgs_before = await client.get_messages(group, limit=1)
        before_id = msgs_before[0].id if msgs_before else 0
        
        await client.send_message(group, f"{command} {value}")
        
        response_text = None
        timeout = 20
        max_attempts = timeout * 10
        
        for _ in range(max_attempts):
            await asyncio.sleep(0.1)
            msgs_after = await client.get_messages(group, limit=10)
            for msg in msgs_after:
                if msg and msg.id > before_id and msg.text:
                    if value.lower() in msg.text.lower() and 'SCANNING' not in msg.text.upper():
                        if not msg.text.startswith(('/num', '/aadhar', '/family', '/insta', '/ffuid', '/rto', '/vehicle')):
                            response_text = msg.text
                            break
            if response_text:
                break
        
        await client.disconnect()
        
        if response_text:
            return True, "Success", response_text
        else:
            return False, "No response from bot", None
            
    except Exception as e:
        if client:
            try:
                await client.disconnect()
            except:
                pass
        return False, str(e), None

def clean_bot_response(text):
    try:
        if not text:
            return [{"error": "No data"}]
        
        lines = text.split('\n')
        json_lines = []
        
        for line in lines:
            if any(x in line.upper() for x in ['ENCOREX', 'OSINT', 'PIRATEXSOUL']):
                continue
            if '⚡' in line or '⏳' in line:
                continue
            if line.strip().startswith(('╔', '╚', '║')):
                continue
            if '{' in line or '}' in line or ':' in line:
                json_lines.append(line.strip())
        
        cleaned = '\n'.join(json_lines)
        
        array_match = re.search(r'\[\s*\{.*?\}\s*\]', cleaned, re.DOTALL)
        if array_match:
            json_str = array_match.group()
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',\s*}', '}', json_str)
            try:
                return json.loads(json_str)
            except:
                pass
        
        obj_match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
        if obj_match:
            json_str = obj_match.group()
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',\s*}', '}', json_str)
            try:
                return [json.loads(json_str)]
            except:
                pass
        
        return [{"raw": text[:1000]}]
        
    except Exception as e:
        return [{"raw": text[:500]}]

def sync_get(command, value):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, msg, response = loop.run_until_complete(
            get_bot_response(command, value)
        )
        loop.close()
        return success, msg, response
    except Exception as e:
        return False, str(e), None

def create_response(success, data=None, error=None, elapsed=0):
    return {
        "success": success,
        "time": f"{elapsed:.2f}s",
        "brand": BRAND,
        **({"data": data} if data else {}),
        **({"error": error} if error else {})
    }

# ========== API ENDPOINTS ==========
@app.route('/')
def home():
    return jsonify({
        "name": BRAND,
        "status": "LIVE",
        "uptime": f"{time.time() - START_TIME:.2f}s",
        "version": "2.0 - Admin Panel Added",
        "endpoints": {
            "public": [
                "/api/numinfo",
                "/api/aadhar", 
                "/api/family",
                "/api/insta",
                "/api/ffuid",
                "/api/rto",
                "/api/vehicle"
            ],
            "admin": [
                "/admin/create-key",
                "/admin/list-keys",
                "/admin/deactivate-key",
                "/admin/activate-key",
                "/admin/delete-key",
                "/admin/usage-logs",
                "/admin/available-apis"
            ]
        }
    })

# Admin Panel HTML Template
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ brand }} - Admin Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .content { padding: 30px; }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1.1em;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        .tab:hover { color: #667eea; }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-small {
            padding: 8px 20px;
            font-size: 0.9em;
        }
        .key-display {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: monospace;
            word-break: break-all;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th { background: #f8f9fa; font-weight: 600; }
        tr:hover { background: #f5f5f5; }
        .badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .expired { background: #f8d7da; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-number { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .stat-label { font-size: 1em; opacity: 0.9; }
        .message {
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .message-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .loading { display: none; text-align: center; padding: 40px; }
        .loading.show { display: block; }
        @media (max-width: 768px) {
            .tabs { flex-direction: column; }
            .tab { width: 100%; text-align: center; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ brand }}</h1>
            <p>🔑 Admin Panel - API Key Management System</p>
        </div>
        <div class="content">
            <!-- Master Key Login -->
            <div id="login-section" style="text-align: center; padding: 40px;">
                <h2>🔐 Admin Login Required</h2>
                <p style="margin: 20px 0;">Enter Master Key to access admin panel</p>
                <div style="max-width: 400px; margin: 0 auto;">
                    <input type="password" id="master-key" placeholder="Enter Master Key" style="margin-bottom: 20px;">
                    <button onclick="login()" class="btn">Login</button>
                </div>
            </div>
            
            <!-- Admin Panel (Hidden by default) -->
            <div id="admin-panel" style="display: none;">
                <!-- Tabs -->
                <div class="tabs">
                    <button class="tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
                    <button class="tab" onclick="showTab('create')">🔑 Create Key</button>
                    <button class="tab" onclick="showTab('list')">📋 List Keys</button>
                    <button class="tab" onclick="showTab('logs')">📈 Usage Logs</button>
                    <button class="tab" onclick="showTab('apis')">🔧 Available APIs</button>
                </div>
                
                <!-- Loading indicator -->
                <div id="loading" class="loading">
                    <h3>Loading...</h3>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard-tab" class="tab-pane active">
                    <div class="stats-grid" id="dashboard-stats">
                        <!-- Stats will be loaded here -->
                    </div>
                </div>
                
                <!-- Create Key Tab -->
                <div id="create-tab" class="tab-pane">
                    <h2>🔑 Create New API Key</h2>
                    <div class="form-group">
                        <label>Owner Name</label>
                        <input type="text" id="owner-name" placeholder="Enter owner name">
                    </div>
                    <div class="form-group">
                        <label>Contact Info</label>
                        <input type="text" id="owner-contact" placeholder="Phone/Email/Telegram">
                    </div>
                    <div class="form-group">
                        <label>Expiry Date</label>
                        <input type="datetime-local" id="expiry-date">
                    </div>
                    <div class="form-group">
                        <label>Max Usage Limit (-1 for unlimited)</label>
                        <input type="number" id="max-usage" value="-1">
                    </div>
                    <div class="form-group">
                        <label>Allowed APIs (Select multiple)</label>
                        <select id="allowed-apis" multiple size="5">
                            <!-- APIs will be loaded here -->
                        </select>
                        <small>Hold Ctrl/Cmd to select multiple</small>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="notes" rows="3" placeholder="Additional notes"></textarea>
                    </div>
                    <button onclick="createKey()" class="btn">Generate API Key</button>
                    
                    <div id="key-result" style="display: none;">
                        <h3>✅ New API Key Generated</h3>
                        <div class="key-display" id="generated-key"></div>
                        <button onclick="copyKey()" class="btn-small">Copy Key</button>
                    </div>
                </div>
                
                <!-- List Keys Tab -->
                <div id="list-tab" class="tab-pane">
                    <h2>📋 API Keys Management</h2>
                    <div style="margin-bottom: 20px;">
                        <input type="text" id="search-keys" placeholder="Search keys..." style="width: 300px;">
                    </div>
                    <div style="overflow-x: auto;">
                        <table id="keys-table">
                            <thead>
                                <tr>
                                    <th>API Key</th>
                                    <th>Owner</th>
                                    <th>Created</th>
                                    <th>Expiry</th>
                                    <th>Usage</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Logs Tab -->
                <div id="logs-tab" class="tab-pane">
                    <h2>📈 Usage Logs</h2>
                    <div style="margin-bottom: 20px;">
                        <input type="text" id="search-logs" placeholder="Search by key or IP..." style="width: 300px;">
                    </div>
                    <div style="overflow-x: auto;">
                        <table id="logs-table">
                            <thead>
                                <tr>
                                    <th>API Key</th>
                                    <th>Endpoint</th>
                                    <th>IP Address</th>
                                    <th>Time</th>
                                    <th>Response Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Available APIs Tab -->
                <div id="apis-tab" class="tab-pane">
                    <h2>🔧 Available APIs</h2>
                    <div style="overflow-x: auto;">
                        <table id="apis-table">
                            <thead>
                                <tr>
                                    <th>API Name</th>
                                    <th>Endpoint</th>
                                    <th>Description</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let masterKey = '';
        
        function login() {
            masterKey = document.getElementById('master-key').value;
            if (masterKey === 'DEV-786') {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('admin-panel').style.display = 'block';
                loadDashboard();
                loadAPIs();
                loadKeys();
            } else {
                alert('Invalid Master Key!');
            }
        }
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'list') loadKeys();
            if (tabName === 'logs') loadLogs();
            if (tabName === 'apis') loadAPIs();
        }
        
        function showLoading(show) {
            document.getElementById('loading').classList.toggle('show', show);
        }
        
        async function loadDashboard() {
            showLoading(true);
            try {
                const response = await fetch('/admin/stats?key=' + masterKey);
                const data = await response.json();
                
                if (data.success) {
                    let html = '';
                    for (const [key, value] of Object.entries(data.data)) {
                        html += `
                            <div class="stat-card">
                                <div class="stat-number">${value}</div>
                                <div class="stat-label">${key.replace(/_/g, ' ').toUpperCase()}</div>
                            </div>
                        `;
                    }
                    document.getElementById('dashboard-stats').innerHTML = html;
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
            showLoading(false);
        }
        
        async function loadAPIs() {
            try {
                const response = await fetch('/admin/available-apis?key=' + masterKey);
                const data = await response.json();
                
                if (data.success) {
                    // Populate APIs table
                    let tableHtml = '';
                    let selectHtml = '';
                    
                    data.data.forEach(api => {
                        tableHtml += `
                            <tr>
                                <td>${api.name}</td>
                                <td>${api.endpoint}</td>
                                <td>${api.description}</td>
                                <td><span class="badge badge-success">Active</span></td>
                            </tr>
                        `;
                        
                        selectHtml += `<option value="${api.name}">${api.name} - ${api.description}</option>`;
                    });
                    
                    document.querySelector('#apis-table tbody').innerHTML = tableHtml;
                    document.getElementById('allowed-apis').innerHTML = selectHtml;
                }
            } catch (error) {
                console.error('Error loading APIs:', error);
            }
        }
        
        async function createKey() {
            showLoading(true);
            
            const expiryDate = document.getElementById('expiry-date').value;
            const expiryTimestamp = expiryDate ? new Date(expiryDate).getTime() / 1000 : null;
            
            const selectedAPIs = Array.from(document.getElementById('allowed-apis').selectedOptions)
                .map(opt => opt.value);
            
            const data = {
                key: masterKey,
                owner_name: document.getElementById('owner-name').value,
                owner_contact: document.getElementById('owner-contact').value,
                expiry_time: expiryTimestamp,
                max_usage: parseInt(document.getElementById('max-usage').value),
                allowed_apis: selectedAPIs,
                notes: document.getElementById('notes').value
            };
            
            try {
                const response = await fetch('/admin/create-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('generated-key').textContent = result.data.key;
                    document.getElementById('key-result').style.display = 'block';
                    loadKeys(); // Refresh keys list
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error creating key: ' + error);
            }
            
            showLoading(false);
        }
        
        async function loadKeys() {
            showLoading(true);
            try {
                const response = await fetch('/admin/list-keys?key=' + masterKey);
                const data = await response.json();
                
                if (data.success) {
                    let html = '';
                    data.data.forEach(key => {
                        const created = new Date(key.created_at * 1000).toLocaleString();
                        const expiry = key.expiry_time ? new Date(key.expiry_time * 1000).toLocaleString() : 'Never';
                        const status = key.is_active ? 
                            '<span class="badge badge-success">Active</span>' : 
                            '<span class="badge badge-danger">Inactive</span>';
                        
                        const expiredClass = key.expiry_time && key.expiry_time < Date.now()/1000 ? 'expired' : '';
                        
                        html += `
                            <tr class="${expiredClass}">
                                <td><code>${key.key_value}</code></td>
                                <td>${key.owner_name || 'N/A'}</td>
                                <td>${created}</td>
                                <td>${expiry}</td>
                                <td>${key.usage_count} / ${key.max_usage > 0 ? key.max_usage : '∞'}</td>
                                <td>${status}</td>
                                <td>
                                    ${key.is_active ? 
                                        `<button onclick="deactivateKey('${key.key_value}')" class="btn-small">Deactivate</button>` : 
                                        `<button onclick="activateKey('${key.key_value}')" class="btn-small">Activate</button>`
                                    }
                                    <button onclick="deleteKey('${key.key_value}')" class="btn-small" style="background: #dc3545;">Delete</button>
                                </td>
                            </tr>
                        `;
                    });
                    
                    document.querySelector('#keys-table tbody').innerHTML = html;
                }
            } catch (error) {
                console.error('Error loading keys:', error);
            }
            showLoading(false);
        }
        
        async function loadLogs() {
            showLoading(true);
            try {
                const response = await fetch('/admin/usage-logs?key=' + masterKey);
                const data = await response.json();
                
                if (data.success) {
                    let html = '';
                    data.data.forEach(log => {
                        const time = new Date(log.requested_at * 1000).toLocaleString();
                        const status = log.success ? 
                            '<span class="badge badge-success">Success</span>' : 
                            '<span class="badge badge-danger">Failed</span>';
                        
                        html += `
                            <tr>
                                <td><code>${log.key_value}</code></td>
                                <td>${log.api_endpoint}</td>
                                <td>${log.ip_address}</td>
                                <td>${time}</td>
                                <td>${log.response_time}s</td>
                                <td>${status}</td>
                            </tr>
                        `;
                    });
                    
                    document.querySelector('#logs-table tbody').innerHTML = html;
                }
            } catch (error) {
                console.error('Error loading logs:', error);
            }
            showLoading(false);
        }
        
        async function deactivateKey(key) {
            if (!confirm('Deactivate this key?')) return;
            
            try {
                const response = await fetch('/admin/deactivate-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: masterKey, target_key: key })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadKeys();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        async function activateKey(key) {
            try {
                const response = await fetch('/admin/activate-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: masterKey, target_key: key })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadKeys();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        async function deleteKey(key) {
            if (!confirm('Are you sure? This cannot be undone!')) return;
            
            try {
                const response = await fetch('/admin/delete-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: masterKey, target_key: key })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadKeys();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        function copyKey() {
            const key = document.getElementById('generated-key').textContent;
            navigator.clipboard.writeText(key);
            alert('API Key copied to clipboard!');
        }
        
        // Search functionality
        document.getElementById('search-keys').addEventListener('input', function(e) {
            const search = e.target.value.toLowerCase();
            document.querySelectorAll('#keys-table tbody tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(search) ? '' : 'none';
            });
        });
        
        document.getElementById('search-logs').addEventListener('input', function(e) {
            const search = e.target.value.toLowerCase();
            document.querySelectorAll('#logs-table tbody tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(search) ? '' : 'none';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_panel():
    return render_template_string(ADMIN_HTML, brand=BRAND)

# ========== ADMIN API ENDPOINTS ==========
@app.route('/admin/stats')
def admin_stats():
    key = request.args.get('key')
    if key != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        
        # Get total keys
        cur.execute("SELECT COUNT(*) as count FROM api_keys")
        total_keys = cur.fetchone()['count']
        
        # Get active keys
        cur.execute("SELECT COUNT(*) as count FROM api_keys WHERE is_active = true")
        active_keys = cur.fetchone()['count']
        
        # Get expired keys
        cur.execute("SELECT COUNT(*) as count FROM api_keys WHERE expiry_time < %s", (int(time.time()),))
        expired_keys = cur.fetchone()['count']
        
        # Get total usage
        cur.execute("SELECT SUM(usage_count) as total FROM api_keys")
        total_usage = cur.fetchone()['total'] or 0
        
        # Get today's usage
        today_start = int(time.time()) - 86400
        cur.execute("SELECT COUNT(*) as count FROM api_usage_logs WHERE requested_at > %s", (today_start,))
        today_usage = cur.fetchone()['count']
        
        cur.close()
        
        return jsonify({
            "success": True,
            "data": {
                "total_keys": total_keys,
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "total_usage": total_usage,
                "today_usage": today_usage,
                "uptime": f"{time.time() - START_TIME:.2f}s"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/create-key', methods=['POST'])
def admin_create_key():
    data = request.json
    master_key = data.get('key')
    
    if master_key != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        new_key = generate_api_key()
        
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_keys 
            (key_value, owner_name, owner_contact, created_at, expiry_time, max_usage, allowed_apis, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING key_value
        """, (
            new_key,
            data.get('owner_name'),
            data.get('owner_contact'),
            int(time.time()),
            data.get('expiry_time'),
            data.get('max_usage', -1),
            data.get('allowed_apis', []),
            data.get('notes'),
            'master'
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        
        return jsonify({
            "success": True,
            "data": {
                "key": result['key_value'],
                "message": "API Key created successfully"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/list-keys')
def admin_list_keys():
    key = request.args.get('key')
    if key != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM api_keys 
            ORDER BY created_at DESC
        """)
        keys = cur.fetchall()
        cur.close()
        
        return jsonify({"success": True, "data": keys})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/deactivate-key', methods=['POST'])
def admin_deactivate_key():
    data = request.json
    if data.get('key') != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE api_keys SET is_active = false 
            WHERE key_value = %s
            RETURNING key_value
        """, (data.get('target_key'),))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        
        if result:
            return jsonify({"success": True, "message": "Key deactivated"})
        return jsonify({"success": False, "error": "Key not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/activate-key', methods=['POST'])
def admin_activate_key():
    data = request.json
    if data.get('key') != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE api_keys SET is_active = true 
            WHERE key_value = %s
            RETURNING key_value
        """, (data.get('target_key'),))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        
        if result:
            return jsonify({"success": True, "message": "Key activated"})
        return jsonify({"success": False, "error": "Key not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/delete-key', methods=['POST'])
def admin_delete_key():
    data = request.json
    if data.get('key') != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM api_keys WHERE key_value = %s", (data.get('target_key'),))
        conn.commit()
        cur.close()
        
        return jsonify({"success": True, "message": "Key deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/usage-logs')
def admin_usage_logs():
    key = request.args.get('key')
    if key != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM api_usage_logs 
            ORDER BY requested_at DESC 
            LIMIT 500
        """)
        logs = cur.fetchall()
        cur.close()
        
        return jsonify({"success": True, "data": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/admin/available-apis')
def admin_available_apis():
    key = request.args.get('key')
    if key != MASTER_KEY:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM available_apis WHERE is_active = true")
        apis = cur.fetchall()
        cur.close()
        
        return jsonify({"success": True, "data": apis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        release_db_connection(conn)

# ========== PUBLIC API ENDPOINTS (Updated with DB validation) ==========
@app.route('/api/numinfo')
def api_numinfo():
    start = time.time()
    key = request.args.get('key')
    num = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'numinfo')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'numinfo', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not num:
        elapsed = time.time() - start
        log_api_usage(key, 'numinfo', ip, elapsed, False)
        return jsonify(create_response(False, error="Number required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/num", num)
    elapsed = time.time() - start
    
    log_api_usage(key, 'numinfo', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/aadhar')
def api_aadhar():
    start = time.time()
    key = request.args.get('key')
    num = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'aadhar')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'aadhar', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not num:
        elapsed = time.time() - start
        log_api_usage(key, 'aadhar', ip, elapsed, False)
        return jsonify(create_response(False, error="Aadhar required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/aadhar", num)
    elapsed = time.time() - start
    
    log_api_usage(key, 'aadhar', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/family')
def api_family():
    start = time.time()
    key = request.args.get('key')
    num = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'family')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'family', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not num:
        elapsed = time.time() - start
        log_api_usage(key, 'family', ip, elapsed, False)
        return jsonify(create_response(False, error="Aadhar required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/family", num)
    elapsed = time.time() - start
    
    log_api_usage(key, 'family', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/insta')
def api_insta():
    start = time.time()
    key = request.args.get('key')
    username = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'insta')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'insta', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not username:
        elapsed = time.time() - start
        log_api_usage(key, 'insta', ip, elapsed, False)
        return jsonify(create_response(False, error="Username required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/insta", username)
    elapsed = time.time() - start
    
    log_api_usage(key, 'insta', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/ffuid')
def api_ffuid():
    start = time.time()
    key = request.args.get('key')
    uid = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'ffuid')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'ffuid', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not uid:
        elapsed = time.time() - start
        log_api_usage(key, 'ffuid', ip, elapsed, False)
        return jsonify(create_response(False, error="FF UID required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/ffuid", uid)
    elapsed = time.time() - start
    
    log_api_usage(key, 'ffuid', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/rto')
def api_rto():
    start = time.time()
    key = request.args.get('key')
    vehicle = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'rto')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'rto', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not vehicle:
        elapsed = time.time() - start
        log_api_usage(key, 'rto', ip, elapsed, False)
        return jsonify(create_response(False, error="Vehicle required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/rto", vehicle)
    elapsed = time.time() - start
    
    log_api_usage(key, 'rto', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

@app.route('/api/vehicle')
def api_vehicle():
    start = time.time()
    key = request.args.get('key')
    vehicle = request.args.get('num')
    ip = request.remote_addr
    
    valid, owner, msg = check_api_key(key, 'vehicle')
    if not valid:
        elapsed = time.time() - start
        log_api_usage(key or 'invalid', 'vehicle', ip, elapsed, False)
        return jsonify(create_response(False, error=msg, elapsed=elapsed)), 403
    
    if not vehicle:
        elapsed = time.time() - start
        log_api_usage(key, 'vehicle', ip, elapsed, False)
        return jsonify(create_response(False, error="Vehicle required", elapsed=elapsed)), 400
    
    success, msg, response = sync_get("/vehicle", vehicle)
    elapsed = time.time() - start
    
    log_api_usage(key, 'vehicle', ip, elapsed, success)
    
    if success and response:
        cleaned = clean_bot_response(response)
        return jsonify(create_response(True, data=cleaned, elapsed=elapsed))
    return jsonify(create_response(False, error=msg, elapsed=elapsed)), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print("\n" + "🔥"*50)
    print(BRAND)
    print("🔥"*50)
    print("✅ Database: PostgreSQL Connected")
    print("✅ Admin Panel: /admin")
    print(f"✅ Master Key: {MASTER_KEY}")
    print("✅ APIs: All working with key validation")
    print(f"✅ Port: {port}")
    print("🔥"*50 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)

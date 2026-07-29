import os
import urllib.request
import urllib.parse
import ssl
import json
import time
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory, session

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-stock-pe-dashboard-secret-key-12938')

# Session cookie settings for HTTPS (Vercel production)
# Without Secure=True on HTTPS, browsers may silently drop the session cookie
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Base directory for static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Server-side Cache (Reset on startup)
SERVER_CACHE = {}
CACHE_TTL = 1800  # 30 minutes

# Core default tracked stocks (~18 stocks)
DEFAULT_CORE_CODES = [
    '3010', '2303', '2330', '5347', '5274', '2059', '7769', '6515',
    '6223', '1301', '1303', '1326', '2881', '2882', '2891', '6446',
    '6472', '7799'
]

STOCK_CATEGORY_MAP = {
    '3010': '半導體材料', '2303': '晶圓代工', '2330': '晶圓代工', '5347': '晶圓代工',
    '5274': 'IC設計', '2059': '軸承/滑軌', '7769': '半導體設備', '6515': '半導體封測材料',
    '6223': '半導體封測材料', '1301': '塑膠石化', '1303': '塑膠石化', '1326': '塑膠石化',
    '2881': '金融保險', '2882': '金融保險', '2891': '金融保險', '6446': '生技股',
    '6472': '生技股', '7799': '生技股', '2317': '組裝代工', '2382': 'AI伺服器',
    '3231': 'AI伺服器', '6669': 'AI伺服器', '2454': 'IC設計', '2379': 'IC設計',
    '3034': 'IC設計', '3443': 'IP/IC設計', '3661': 'IP/ASIC', '2383': 'CCL銅箔基板',
    '6274': 'CCL銅箔基板', '3665': '線束/連接器', '3037': 'ABF載板', '8046': 'ABF載板'
}

EPS_DERIVED_MAP = {
    '3010': { 'eps2025': 8.84, 'eps2026q1': 2.47, 'eps2026q2': None, 'epsTTM': 9.37 },
    '2303': { 'eps2025': 3.34, 'eps2026q1': 1.29, 'eps2026q2': None, 'epsTTM': 4.00 },
    '2330': { 'eps2025': 66.25, 'eps2026q1': 22.08, 'eps2026q2': 49.33, 'epsTTM': 74.39 },
    '5347': { 'eps2025': 4.30, 'eps2026q1': 1.22, 'eps2026q2': None, 'epsTTM': 4.90 },
    '5274': { 'eps2025': 103.92, 'eps2026q1': 37.41, 'eps2026q2': None, 'epsTTM': 117.87 },
    '2059': { 'eps2025': 103.23, 'eps2026q1': 36.58, 'eps2026q2': None, 'epsTTM': 113.46 },
    '7769': { 'eps2025': 75.71, 'eps2026q1': 25.70, 'eps2026q2': None, 'epsTTM': 81.41 },
    '6515': { 'eps2025': 46.93, 'eps2026q1': 19.54, 'eps2026q2': None, 'epsTTM': 56.47 },
    '6223': { 'eps2025': 33.49, 'eps2026q1': 12.53, 'eps2026q2': None, 'epsTTM': 39.02 },
    '1301': { 'eps2025': 1.58, 'eps2026q1': 0.51, 'eps2026q2': 2.19, 'epsTTM': 1.80 },
    '1303': { 'eps2025': 0.57, 'eps2026q1': 1.80, 'eps2026q2': 5.17, 'epsTTM': 2.10 },
    '1326': { 'eps2025': -0.99, 'eps2026q1': 1.07, 'eps2026q2': 2.11, 'epsTTM': 0.50 },
    '2881': { 'eps2025': 8.37, 'eps2026q1': 2.37, 'eps2026q2': 6.67, 'epsTTM': 9.20 },
    '2882': { 'eps2025': 7.06, 'eps2026q1': 2.15, 'eps2026q2': 4.95, 'epsTTM': 7.80 },
    '2891': { 'eps2025': 4.08, 'eps2026q1': 1.18, 'eps2026q2': 1.96, 'epsTTM': 4.30 },
    '6446': { 'eps2025': 13.64, 'eps2026q1': 5.79, 'eps2026q2': None, 'epsTTM': 16.50 },
    '6472': { 'eps2025': 23.90, 'eps2026q1': 0.20, 'eps2026q2': None, 'epsTTM': 24.10 },
    '7799': { 'eps2025': -3.31, 'eps2026q1': -0.37, 'eps2026q2': None, 'epsTTM': -3.00 }
}

SNAPSHOT_PRICES = {
    '3010': 116.00, '2303': 144.00, '2330': 2290.00, '5347': 169.00, '5274': 12950.00,
    '2059': 7890.00, '7769': 6070.00, '6515': 6055.00, '6223': 5600.00, '1301': 62.80,
    '1303': 199.00, '1326': 66.10, '2881': 124.50, '2882': 94.30, '2891': 62.10,
    '6446': 1195.00, '6472': 396.00, '7799': 415.50
}

def derive_eps_from_finmind(stock_id, ctx):
    url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockFinancialStatements&data_id={stock_id}&start_date=2024-01-01"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            records = [x for x in data.get('data', []) if x.get('type') == 'EPS']
            
            records_sorted = sorted(records, key=lambda x: x['date'], reverse=True)
            last_4 = records_sorted[:4]
            eps_ttm = round(sum([x['value'] for x in last_4]), 2) if len(last_4) == 4 else None
            
            eps_2025_list = [x['value'] for x in records if x['date'].startswith('2025')]
            eps2025 = round(sum(eps_2025_list), 2) if len(eps_2025_list) >= 3 else None
            
            q1_records = [x['value'] for x in records if x['date'].startswith('2026-03')]
            eps2026q1 = q1_records[0] if q1_records else None
            
            q2_records = [x['value'] for x in records if x['date'].startswith('2026-06')]
            eps2026q2_standalone = q2_records[0] if q2_records else None
            eps2026q2 = round((eps2026q1 or 0) + eps2026q2_standalone, 2) if (eps2026q1 and eps2026q2_standalone) else None
            
            ref = EPS_DERIVED_MAP.get(stock_id, {})
            return stock_id, {
                'eps2025': eps2025 if eps2025 is not None else ref.get('eps2025'),
                'eps2026q1': eps2026q1 if eps2026q1 is not None else ref.get('eps2026q1'),
                'eps2026q2': eps2026q2 if eps2026q2 is not None else ref.get('eps2026q2'),
                'epsTTM': eps_ttm if eps_ttm is not None else ref.get('epsTTM')
            }
    except Exception:
        ref = EPS_DERIVED_MAP.get(stock_id, {})
        return stock_id, {
            'eps2025': ref.get('eps2025'),
            'eps2026q1': ref.get('eps2026q1'),
            'eps2026q2': ref.get('eps2026q2'),
            'epsTTM': ref.get('epsTTM')
        }

def fetch_taiex_performance(target_date_str, ctx):
    try:
        t_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
        start_date = (t_date - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id=TAIEX&start_date={start_date}&end_date={target_date_str}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
            data = json.loads(res.read().decode('utf-8')).get('data', [])
            if not data:
                return 0.0
            data = sorted([x for x in data if x.get('date', '') <= target_date_str and x.get('close') is not None], key=lambda x: x['date'])
            prices = [float(x['close']) for x in data]
            if len(prices) >= 6:
                change_5d = ((prices[-1] - prices[-6]) / prices[-6]) * 100.0
            elif len(prices) >= 2:
                change_5d = ((prices[-1] - prices[0]) / prices[0]) * 100.0
            else:
                change_5d = 0.0
            return round(change_5d, 2)
    except Exception:
        return 0.0

def fetch_ma_data(stock_id, target_date_str, ctx):
    try:
        t_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
        start_date = (t_date - datetime.timedelta(days=150)).strftime('%Y-%m-%d')
        url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={stock_id}&start_date={start_date}&end_date={target_date_str}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
            data = json.loads(res.read().decode('utf-8')).get('data', [])
            if not data:
                return stock_id, {}
            data = sorted([x for x in data if x.get('date', '') <= target_date_str and x.get('close') is not None], key=lambda x: x['date'])
            prices = [float(x['close']) for x in data]
            highs = [float(x.get('max', x['close'])) for x in data]
            lows = [float(x.get('min', x['close'])) for x in data]
            k_val, d_val = calc_kd_info(highs, lows, prices)

            if len(prices) >= 6:
                stock_5d_pct = round(((prices[-1] - prices[-6]) / prices[-6]) * 100.0, 2)
            elif len(prices) >= 2:
                stock_5d_pct = round(((prices[-1] - prices[0]) / prices[0]) * 100.0, 2)
            else:
                stock_5d_pct = 0.0

            def calc_ma(period):
                if len(prices) < period:
                    return None, 'flat', 0
                ma_list = []
                for i in range(len(prices)):
                    if i + 1 < period:
                        ma_list.append(None)
                    else:
                        ma_list.append(sum(prices[i - period + 1 : i + 1]) / period)
                
                dirs = [None] * len(ma_list)
                for i in range(1, len(ma_list)):
                    if ma_list[i] is not None and ma_list[i-1] is not None:
                        if ma_list[i] > ma_list[i-1]:
                            dirs[i] = 'up'
                        elif ma_list[i] < ma_list[i-1]:
                            dirs[i] = 'down'
                        else:
                            dirs[i] = 'flat'
                last = len(prices) - 1
                curr_ma = ma_list[last]
                curr_dir = dirs[last] or 'flat'
                streak = 0
                if curr_dir in ('up', 'down'):
                    for i in range(last, 0, -1):
                        if dirs[i] == curr_dir:
                            streak += 1
                        else:
                            break
                return round(curr_ma, 2) if curr_ma is not None else None, curr_dir, streak

            ma20, dir20, streak20 = calc_ma(20)
            ma60, dir60, streak60 = calc_ma(60)
            return stock_id, {
                'ma20': ma20, 'ma20Dir': dir20, 'ma20Streak': streak20,
                'ma60': ma60, 'ma60Dir': dir60, 'ma60Streak': streak60,
                'kVal': k_val, 'dVal': d_val,
                'stock5dPct': stock_5d_pct
            }
    except Exception:
        return stock_id, {}


def fetch_twse_prices(date_yyyymmdd, ctx):
    prices = {}
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_yyyymmdd}&type=ALLBUT0999&response=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
            data = json.loads(res.read().decode('utf-8'))
            if data.get('stat') == 'OK':
                for t in data.get('tables', []):
                    for row in t.get('data', []):
                        if len(row) >= 9:
                            code = str(row[0]).strip()
                            name = str(row[1]).strip()
                            price_str = str(row[8]).replace(',', '').strip()
                            if len(code) == 4 and code.isdigit():
                                try:
                                    p = float(price_str)
                                    if p > 0: prices[code] = { 'code': code, 'name': name, 'price': p, 'market': 'TWSE' }
                                except ValueError:
                                    pass
    except Exception:
        pass
    return prices

def fetch_tpex_prices(date_param, ctx):
    prices = {}
    try:
        parts = date_param.split('-')
        if len(parts) == 3:
            roc_year = int(parts[0]) - 1911
            roc_date = f"{roc_year}/{parts[1]}/{parts[2]}"
            url = f"https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={roc_date}&_={int(time.time()*1000)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                rows = []
                if 'tables' in data and data['tables']:
                    rows = data['tables'][0].get('data', [])
                elif 'aaData' in data:
                    rows = data.get('aaData', [])

                for row in rows:
                    if len(row) >= 3:
                        code = str(row[0]).strip()
                        name = str(row[1]).strip()
                        price_str = str(row[2]).replace(',', '').strip()
                        if len(code) == 4 and code.isdigit():
                            try:
                                p = float(price_str)
                                if p > 0: prices[code] = { 'code': code, 'name': name, 'price': p, 'market': 'TPEX' }
                            except ValueError:
                                pass
    except Exception:
        pass
    return prices

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if os.path.exists(os.path.join(BASE_DIR, filename)):
        return send_from_directory(BASE_DIR, filename)
    return send_from_directory(BASE_DIR, 'index.html')

def call_gas_api(url, payload=None):
    """
    Call Google Apps Script Web App API via GET.
    urllib follows GAS redirects automatically for GET requests.
    """
    ctx = ssl._create_unverified_context()
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def call_gas_api_write(base_url, payload):
    """
    Send a write operation (save/delete) to GAS via GET + JSON payload param.
    GAS doGet reads e.parameter.payload and dispatches accordingly.
    This avoids the GAS POST redirect problem entirely.
    """
    ctx = ssl._create_unverified_context()
    headers = {'User-Agent': 'Mozilla/5.0'}
    encoded = urllib.parse.urlencode({'payload': json.dumps(payload)})
    full_url = f"{base_url}?{encoded}"
    req = urllib.request.Request(full_url, headers=headers, method='GET')
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def get_stocks_from_sheet():
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return []
    try:
        url = f"{gas_url}?key={urllib.parse.quote(gas_key)}&action=get_stocks"
        res = call_gas_api(url)
        if res.get('status') == 'ok':
            return res.get('data', [])
    except Exception as e:
        print(f"Error fetching stocks from sheet: {e}")
    return []

def get_allowed_emails():
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return ['yuhluen@gmail.com']
    try:
        url = f"{gas_url}?key={urllib.parse.quote(gas_key)}&action=get_users"
        res = call_gas_api(url)
        if res.get('status') == 'ok':
            return [str(row.get('email', '')).strip().lower() for row in res.get('data', []) if row.get('email')]
    except Exception as e:
        print(f"Error fetching allowed emails: {e}")
    return ['yuhluen@gmail.com']

def is_email_allowed(email):
    allowed_list = get_allowed_emails()
    return email.lower() in allowed_list

def verify_google_id_token(token, client_id):
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    ctx = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            aud = data.get('aud', '')
            
            # Normalize client IDs for exact comparison
            cid_norm = client_id.strip()
            if not cid_norm.endswith('.apps.googleusercontent.com'):
                cid_norm += '.apps.googleusercontent.com'
                
            aud_norm = aud.strip()
            if not aud_norm.endswith('.apps.googleusercontent.com'):
                aud_norm += '.apps.googleusercontent.com'
                
            if aud_norm == cid_norm:
                return data
    except Exception as e:
        print(f"Token verification failed: {e}")
    return None

@app.before_request
def restrict_api_access():
    if request.path.startswith('/api/') and not request.path.startswith('/api/auth/'):
        if 'user_email' not in session:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

@app.route('/api/auth/config', methods=['GET'])
def get_auth_config():
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    if client_id and not client_id.endswith('.apps.googleusercontent.com'):
        client_id += '.apps.googleusercontent.com'
    return jsonify({
        'google_client_id': client_id
    })

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    req_data = request.get_json() or {}
    token = req_data.get('id_token')
    if not token:
        return jsonify({'status': 'error', 'message': 'Missing token'}), 400
        
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    if not client_id:
        return jsonify({'status': 'error', 'message': 'Google Client ID not configured'}), 500
        
    idinfo = verify_google_id_token(token, client_id)
    if not idinfo:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
    email = idinfo.get('email', '').strip().lower()
    if not email:
        return jsonify({'status': 'error', 'message': 'Email not found in token'}), 401
        
    allowed = is_email_allowed(email)
    if not allowed:
        return jsonify({'status': 'error', 'message': 'Access denied: email not in allowed list'}), 403
        
    session['user_email'] = email
    session['user_name'] = idinfo.get('name', 'User')
    session['user_picture'] = idinfo.get('picture', '')
    
    return jsonify({
        'status': 'ok',
        'user': {
            'email': email,
            'name': session['user_name'],
            'picture': session['user_picture']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.clear()
    return jsonify({'status': 'ok'})

@app.route('/api/auth/session', methods=['GET'])
def auth_session():
    if 'user_email' in session:
        return jsonify({
            'status': 'ok',
            'user': {
                'email': session['user_email'],
                'name': session['user_name'],
                'picture': session['user_picture']
            }
        })
    return jsonify({'status': 'anonymous'})

def get_all_raw_stocks(date_param, ctx, force_refresh=False):
    date_yyyymmdd = date_param.replace('-', '')
    now = time.time()
    raw_cache_key = f"raw_prices_{date_yyyymmdd}"
    if not force_refresh and raw_cache_key in SERVER_CACHE:
        entry = SERVER_CACHE[raw_cache_key]
        if now - entry['ts'] < CACHE_TTL:
            return entry['data']

    # Parallel Execution: Fetch TWSE & TPEX prices
    with ThreadPoolExecutor(max_workers=2) as executor:
        twse_future = executor.submit(fetch_twse_prices, date_yyyymmdd, ctx)
        tpex_future = executor.submit(fetch_tpex_prices, date_param, ctx)
        twse_prices = twse_future.result()
        tpex_prices = tpex_future.result()

    all_raw_stocks = {**twse_prices, **tpex_prices}
    SERVER_CACHE[raw_cache_key] = {
        'ts': now,
        'data': all_raw_stocks
    }
    return all_raw_stocks

@app.route('/api/search', methods=['GET'])
def search_stocks():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
        
    date_param = request.args.get('date', '2026-07-21')
    ctx = ssl._create_unverified_context()
    
    try:
        all_raw_stocks = get_all_raw_stocks(date_param, ctx, force_refresh=False)
    except Exception as e:
        print(f"Error fetching all raw stocks: {e}")
        all_raw_stocks = {}
        
    matches = []
    q_lower = q.lower()
    for code, info in all_raw_stocks.items():
        name = info.get('name', '')
        if q_lower in code.lower() or q_lower in name.lower():
            matches.append({
                'code': code,
                'name': name,
                'category': STOCK_CATEGORY_MAP.get(code, '台股個股')
            })
            
    # Sort matches: exact matches first, then starts-with, then others
    def sort_key(item):
        c_match = item['code'].lower() == q_lower
        n_match = item['name'].lower() == q_lower
        c_start = item['code'].lower().startswith(q_lower)
        n_start = item['name'].lower().startswith(q_lower)
        return (not (c_match or n_match), not (c_start or n_start), len(item['name']))
        
    matches.sort(key=sort_key)
    return jsonify(matches[:7])

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    date_param = request.args.get('date', '2026-07-21')
    req_code = request.args.get('code')
    req_custom = request.args.get('custom', '')
    req_all = request.args.get('all') == 'true'
    force_refresh = request.args.get('force') == 'true'
    date_yyyymmdd = date_param.replace('-', '')
    
    custom_codes = [c.strip() for c in req_custom.split(',') if c.strip()]

    # Check Server-side Cache
    now = time.time()
    cache_key = f"{date_param}_{req_code or ('all' if req_all else ('default_' + req_custom))}"
    if not force_refresh and cache_key in SERVER_CACHE:
        cached_entry = SERVER_CACHE[cache_key]
        if now - cached_entry['ts'] < CACHE_TTL:
            return jsonify({
                'status': 'ok',
                'cached': True,
                'date': date_param,
                'total': len(cached_entry['stocks']),
                'stocks': cached_entry['stocks']
            })

    ctx = ssl._create_unverified_context()
    all_raw_stocks = get_all_raw_stocks(date_param, ctx, force_refresh)
    
    # Load stocks from Google Sheet database
    sheet_stocks = get_stocks_from_sheet()
    # Normalize: GAS may return numeric codes (e.g. 3010 as int), convert all to str
    for s in sheet_stocks:
        s['code'] = str(s.get('code', '')).strip()
        s['type'] = str(s.get('type', '')).strip().upper()
    tw_sheet_stocks = [s for s in sheet_stocks if s['type'] == 'TW' and s['code']]

    # Determine target stock codes
    if req_code:
        # Check if req_code matches a code directly
        if req_code in all_raw_stocks:
            target_codes = [req_code]
        else:
            # Check if it matches a name (case-insensitive, exact or partial)
            matched_codes = [code for code, info in all_raw_stocks.items() if req_code.lower() in info.get('name', '').lower()]
            if matched_codes:
                # Sort to put exact matches first, then shorter names
                matched_codes.sort(key=lambda c: (all_raw_stocks[c]['name'].lower() != req_code.lower(), len(all_raw_stocks[c]['name'])))
                target_codes = [matched_codes[0]]
            else:
                target_codes = [req_code]
    elif req_all:
        target_codes = list(all_raw_stocks.keys())
    else:
        if tw_sheet_stocks:
            target_codes = [s['code'] for s in tw_sheet_stocks]  # already strings
        else:
            # DEFAULT: Return core default tracked stocks + any user custom stocks!
            target_codes = list(dict.fromkeys(DEFAULT_CORE_CODES + custom_codes))

    # Parallel EPS, MA & TAIEX derivation for target stocks
    eps_results = {}
    ma_results = {}
    taiex_5d_pct = 0.0
    with ThreadPoolExecutor(max_workers=16) as executor:
        eps_futures = [executor.submit(derive_eps_from_finmind, c, ctx) for c in target_codes]
        ma_futures = [executor.submit(fetch_ma_data, c, date_param, ctx) for c in target_codes]
        taiex_future = executor.submit(fetch_taiex_performance, date_param, ctx)
        
        for f in eps_futures:
            code, eps_dict = f.result()
            eps_results[code] = eps_dict
        for f in ma_futures:
            code, ma_dict = f.result()
            ma_results[code] = ma_dict
        try:
            taiex_5d_pct = taiex_future.result()
        except Exception:
            taiex_5d_pct = 0.0

    result_stocks = []
    for code in target_codes:
        raw_info = all_raw_stocks.get(code, {})
        name = raw_info.get('name', code)
        price = raw_info.get('price', SNAPSHOT_PRICES.get(code, 100.0))
        
        # Load category & EPS from sheet if available, else fallback
        sheet_stock = next((s for s in tw_sheet_stocks if str(s.get('code','')).strip() == code), None)

        def _float(v):
            if v in (None, ''): return None
            try: return float(v)
            except (ValueError, TypeError): return None

        if sheet_stock:
            category = sheet_stock.get('category') or STOCK_CATEGORY_MAP.get(code, '台股個股')
            name = sheet_stock.get('name') or name

            # Sheet EPS takes priority; fall back to FinMind when sheet field is empty
            derived = eps_results.get(code, EPS_DERIVED_MAP.get(code, {}))
            eps_data = {
                'eps2025':   _float(sheet_stock.get('eps2025'))   or derived.get('eps2025'),
                'eps2026q1': _float(sheet_stock.get('eps2026q1')) or derived.get('eps2026q1'),
                'eps2026q2': _float(sheet_stock.get('eps2026q2')) or derived.get('eps2026q2'),
                'epsTTM':    _float(sheet_stock.get('epsTTM'))    or derived.get('epsTTM'),
            }
        else:
            category = STOCK_CATEGORY_MAP.get(code, '台股個股')
            eps_data = eps_results.get(code, EPS_DERIVED_MAP.get(code, {}))
            
        ma_info = ma_results.get(code, {})

        stock_5d_pct = ma_info.get('stock5dPct', 0.0)
        excess_5d = round(stock_5d_pct - taiex_5d_pct, 2)
        if excess_5d > 1.5:
            rs_status = 'strong'
            rs_label = '🔥 強勢'
        elif excess_5d < -1.5:
            rs_status = 'weak'
            rs_label = '❄️ 弱勢'
        else:
            rs_status = 'neutral'
            rs_label = '⚪ 一致'

        result_stocks.append({
            'id': code,
            'category': category,
            'code': code,
            'name': name,
            'eps2025': eps_data.get('eps2025'),
            'eps2026q1': eps_data.get('eps2026q1'),
            'eps2026q2': eps_data.get('eps2026q2'),
            'epsTTM': eps_data.get('epsTTM'),
            'price': price,
            'ma20': ma_info.get('ma20'),
            'ma20Dir': ma_info.get('ma20Dir'),
            'ma20Streak': ma_info.get('ma20Streak', 0),
            'ma60': ma_info.get('ma60'),
            'ma60Dir': ma_info.get('ma60Dir'),
            'ma60Streak': ma_info.get('ma60Streak', 0),
            'kVal': ma_info.get('kVal'),
            'dVal': ma_info.get('dVal'),
            'stock5dPct': stock_5d_pct,
            'taiex5dPct': taiex_5d_pct,
            'rs5dDiff': excess_5d,
            'rs5dStatus': rs_status,
            'rs5dLabel': rs_label
        })

    SERVER_CACHE[cache_key] = {
        'ts': now,
        'stocks': result_stocks
    }

    # ── Auto writeback: if sheet EPS was empty but we fetched EPS from FinMind,
    #    save it back to Google Sheet so future requests skip the fetch.
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if gas_url and gas_key:
        def _writeback_eps(stocks_to_write):
            for st in stocks_to_write:
                try:
                    payload = {
                        'key': gas_key,
                        'action': 'save_stock',
                        'stock': {
                            'code': st['code'],
                            'name': st['name'],
                            'category': st['category'],
                            'eps2025': st.get('eps2025'),
                            'eps2026q1': st.get('eps2026q1'),
                            'eps2026q2': st.get('eps2026q2'),
                            'epsTTM': st.get('epsTTM'),
                            'epsFwd': st.get('epsFwd'),
                            'type': 'TW'
                        }
                    }
                    call_gas_api_write(gas_url, payload)
                except Exception as e:
                    print(f"EPS writeback failed for {st['code']}: {e}")

        # Only writeback stocks that had empty EPS in sheet but fetched EPS from FinMind
        needs_writeback = []
        for st in result_stocks:
            ss = next((s for s in tw_sheet_stocks if s['code'] == st['code']), None)
            if ss:
                sheet_had_eps = any([
                    ss.get('eps2025') not in (None, ''),
                    ss.get('eps2026q1') not in (None, ''),
                    ss.get('eps2026q2') not in (None, ''),
                    ss.get('epsTTM') not in (None, ''),
                ])
                fetched_has_eps = any([
                    st.get('eps2025') is not None,
                    st.get('eps2026q1') is not None,
                    st.get('eps2026q2') is not None,
                    st.get('epsTTM') is not None,
                ])
                if not sheet_had_eps and fetched_has_eps:
                    needs_writeback.append(st)

        if needs_writeback:
            t = threading.Thread(target=_writeback_eps, args=(needs_writeback,), daemon=True)
            t.start()
            print(f"[EPS Writeback] Triggered for {len(needs_writeback)} stocks")

    return jsonify({
        'status': 'ok',
        'cached': False,
        'date': date_param,
        'total': len(result_stocks),
        'stocks': result_stocks
    })

INDEX_CONFIG = [
    {'code': '^TWII', 'name': '台灣加權指數', 'region': '台股'},
    {'code': '^DJI',  'name': '道瓊工業指數', 'region': '美股'},
    {'code': '^IXIC', 'name': '那斯達克指數', 'region': '美股'},
    {'code': '^SOX',  'name': '費城半導體指數', 'region': '美股'},
    {'code': '^GSPC', 'name': '標普500指數', 'region': '美股'},
    {'code': '^N225', 'name': '日經225指數', 'region': '日股'},
    {'code': '^KS11', 'name': '韓國綜合指數', 'region': '韓股'},
    {'code': '000001.SS', 'name': '上證綜合指數', 'region': '陸股'}
]

def calc_kd_info(highs, lows, closes, n=9, m1=3, m2=3):
    """
    Calculate Daily Stochastic Oscillator (9, 3, 3).
    Returns (k, d) rounded to 1 decimal place.
    """
    if not closes or len(closes) < n or len(highs) < n or len(lows) < n:
        return None, None
    k = 50.0
    d = 50.0
    for i in range(len(closes)):
        if i < n - 1:
            continue
        window_high = max(highs[i - n + 1 : i + 1])
        window_low = min(lows[i - n + 1 : i + 1])
        if window_high == window_low:
            rsv = 50.0
        else:
            rsv = (closes[i] - window_low) / (window_high - window_low) * 100.0
        k = k * (2.0 / m1) + rsv * (1.0 / m1)
        d = d * (2.0 / m2) + k * (1.0 / m2)
    return round(k, 1), round(d, 1)

def calc_series_ma_info(series, period):
    if len(series) < period:
        return None, 'flat', 0
    ma_list = []
    for i in range(len(series)):
        if i + 1 < period:
            ma_list.append(None)
        else:
            ma_list.append(sum(series[i - period + 1 : i + 1]) / period)
    
    dirs = [None] * len(ma_list)
    for i in range(1, len(ma_list)):
        if ma_list[i] is not None and ma_list[i-1] is not None:
            if ma_list[i] > ma_list[i-1]:
                dirs[i] = 'up'
            elif ma_list[i] < ma_list[i-1]:
                dirs[i] = 'down'
            else:
                dirs[i] = 'flat'
    
    last_idx = len(series) - 1
    curr_ma = ma_list[last_idx]
    curr_dir = dirs[last_idx] or 'flat'
    streak = 0
    if curr_dir in ('up', 'down'):
        for i in range(last_idx, 0, -1):
            if dirs[i] == curr_dir:
                streak += 1
            else:
                break
    return (round(curr_ma, 2) if curr_ma is not None else None), curr_dir, streak

def fetch_single_index(item, ctx):
    sym = item['code']
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(sym) + '?range=5y&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            quote = result['indicators']['quote'][0]
            raw_closes = quote.get('close', [])
            raw_highs = quote.get('high', [])
            raw_lows = quote.get('low', [])
            raw_volumes = quote.get('volume', [])
            
            clean_pairs = []
            for ts, c, h, l, v in zip(timestamps, raw_closes,
                                     raw_highs if len(raw_highs)==len(timestamps) else [None]*len(timestamps),
                                     raw_lows if len(raw_lows)==len(timestamps) else [None]*len(timestamps),
                                     raw_volumes if len(raw_volumes) == len(timestamps) else [None]*len(timestamps)):
                if c is not None:
                    c_val = float(c)
                    h_val = float(h) if h is not None else c_val
                    l_val = float(l) if l is not None else c_val
                    v_val = float(v) if v is not None else 0.0
                    clean_pairs.append((ts, c_val, v_val, h_val, l_val))
            
            if not clean_pairs:
                return item['code'], {}
            
            ts_list, prices, volumes, highs, lows = zip(*clean_pairs)
            
            ma20, dir20, streak20 = calc_series_ma_info(prices, 20)
            ma60, dir60, streak60 = calc_series_ma_info(prices, 60)
            ma240, dir240, streak240 = calc_series_ma_info(prices, 240)
            k_val, d_val = calc_kd_info(highs, lows, prices)
            
            # Volume 20MA (VMA20)
            valid_volumes = [v for v in volumes if v > 0]
            has_volume = len(valid_volumes) >= 20
            vma20, vdir20, vstreak20 = (None, 'flat', 0)
            if has_volume:
                vma20, vdir20, vstreak20 = calc_series_ma_info(volumes, 20)
            
            latest_price = round(prices[-1], 2)
            prev_price = round(prices[-2], 2) if len(prices) >= 2 else latest_price
            change = round(latest_price - prev_price, 2)
            change_pct = round((change / prev_price) * 100, 2)
            date_str = datetime.datetime.fromtimestamp(ts_list[-1]).strftime('%Y-%m-%d')
            
            return item['code'], {
                'code': item['code'],
                'name': item['name'],
                'region': item['region'],
                'price': latest_price,
                'change': change,
                'changePct': change_pct,
                'date': date_str,
                'ma20': ma20, 'ma20Dir': dir20, 'ma20Streak': streak20,
                'ma60': ma60, 'ma60Dir': dir60, 'ma60Streak': streak60,
                'ma240': ma240, 'ma240Dir': dir240, 'ma240Streak': streak240,
                'kVal': k_val, 'dVal': d_val,
                'hasVolume': has_volume,
                'vma20': vma20, 'vma20Dir': vdir20, 'vma20Streak': vstreak20
            }
    except Exception:
        return item['code'], {}

@app.route('/api/indices', methods=['GET'])
def get_indices():
    now = time.time()
    cache_key = 'indices_cache'
    force_refresh = request.args.get('force') == 'true'
    
    if not force_refresh and cache_key in SERVER_CACHE:
        cached_entry = SERVER_CACHE[cache_key]
        if now - cached_entry['ts'] < CACHE_TTL:
            return jsonify({
                'status': 'ok',
                'cached': True,
                'indices': cached_entry['indices']
            })

    ctx = ssl._create_unverified_context()
    indices_res = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_single_index, item, ctx) for item in INDEX_CONFIG]
        for f in futures:
            code, idx_dict = f.result()
            if idx_dict:
                indices_res.append(idx_dict)
    
    SERVER_CACHE[cache_key] = {
        'ts': now,
        'indices': indices_res
    }
    
    return jsonify({
        'status': 'ok',
        'cached': False,
        'indices': indices_res
    })


# \u2500\u2500\u2500 US Stocks \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

US_DEFAULT_STOCKS = [
    {'code': 'NVDA',  'name': 'NVIDIA',         'sector': 'AI\u6676\u7247'},
    {'code': 'AAPL',  'name': 'Apple',          'sector': '\u79d1\u6280/\u6d88\u8cbb'},
    {'code': 'GOOGL', 'name': 'Alphabet',       'sector': '\u5ee3\u544a/AI'},
    {'code': 'AMZN',  'name': 'Amazon',         'sector': '\u96fb\u5546/\u96f2\u7aef'},
    {'code': 'TSLA',  'name': 'Tesla',          'sector': '\u96fb\u52d5\u8eca/AI'},
    {'code': 'MSFT',  'name': 'Microsoft',      'sector': '\u96f2\u7aef/AI'},
    {'code': 'META',  'name': 'Meta Platforms', 'sector': '\u793e\u7fa4/AI'},
    {'code': 'AVGO',  'name': 'Broadcom',       'sector': 'AI\u6676\u7247/\u7db2\u8def'},
    {'code': 'AMD',   'name': 'AMD',            'sector': 'AI\u6676\u7247'},
    {'code': 'ARM',   'name': 'ARM Holdings',   'sector': 'IC\u8a2d\u8a08IP'},
    {'code': 'TSM',   'name': 'TSMC ADR',       'sector': '\u6676\u5713\u4ee3\u5de5'},
    {'code': 'ASML',  'name': 'ASML',           'sector': '\u534a\u5c0e\u9ad4\u8a2d\u5099'},
]

def fetch_us_stock_data(stock_info, ctx):
    """Fetch price, 20/60 MA, TTM/Fwd P-E, TTM/Fwd EPS for one US stock."""
    code = stock_info['code']
    result = {
        'id': code, 'code': code,
        'name': stock_info.get('name', code),
        'category': stock_info.get('sector', '美股個股'),
        'price': 0,
        'ma20': None, 'ma20Dir': None, 'ma20Streak': 0,
        'ma60': None, 'ma60Dir': None, 'ma60Streak': 0,
        'epsTTM': None, 'epsFwd': None, 'peTTM': None, 'peFwd': None,
        'kVal': None, 'dVal': None
    }

    # 1) Price history → MA & KD
    try:
        chart_url = (
            f'https://query1.finance.yahoo.com/v8/finance/chart/'
            f'{urllib.parse.quote(code)}?range=1y&interval=1d'
        )
        req = urllib.request.Request(
            chart_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=6) as res:
            d = json.loads(res.read().decode('utf-8'))
            quote = d['chart']['result'][0]['indicators']['quote'][0]
            closes = quote.get('close', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])

            clean_triplets = []
            for c, h, l in zip(closes,
                               highs if len(highs)==len(closes) else [None]*len(closes),
                               lows if len(lows)==len(closes) else [None]*len(closes)):
                if c is not None:
                    c_val = float(c)
                    h_val = float(h) if h is not None else c_val
                    l_val = float(l) if l is not None else c_val
                    clean_triplets.append((c_val, h_val, l_val))

            if clean_triplets:
                prices, highs_list, lows_list = zip(*clean_triplets)
                ma20, dir20, sk20 = calc_series_ma_info(prices, 20)
                ma60, dir60, sk60 = calc_series_ma_info(prices, 60)
                k_val, d_val = calc_kd_info(highs_list, lows_list, prices)
                result.update({
                    'price': round(prices[-1], 2),
                    'ma20': ma20, 'ma20Dir': dir20, 'ma20Streak': sk20,
                    'ma60': ma60, 'ma60Dir': dir60, 'ma60Streak': sk60,
                    'kVal': k_val, 'dVal': d_val,
                })
    except Exception:
        pass

    # 2) Fundamentals \u2192 PE + EPS
    try:
        qs_url = (
            f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
            f'{urllib.parse.quote(code)}?modules=summaryDetail,defaultKeyStatistics'
        )
        req2 = urllib.request.Request(
            qs_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req2, context=ctx, timeout=6) as res2:
            fd = json.loads(res2.read().decode('utf-8'))
            qr = fd.get('quoteSummary', {}).get('result', [{}])[0]
            sd = qr.get('summaryDetail', {})
            ks = qr.get('defaultKeyStatistics', {})

            def _r(d, k):
                v = d.get(k)
                return v.get('raw') if isinstance(v, dict) else v

            pe_t = _r(sd, 'trailingPE');  pe_f  = _r(sd, 'forwardPE')
            eps_t = _r(ks, 'trailingEps'); eps_f = _r(ks, 'forwardEps')
            result.update({
                'peTTM':  round(pe_t,  2) if pe_t  else None,
                'peFwd':  round(pe_f,  2) if pe_f  else None,
                'epsTTM': round(eps_t, 2) if eps_t else None,
                'epsFwd': round(eps_f, 2) if eps_f else None,
            })
    except Exception:
        pass

    return code, result


@app.route('/api/us_stocks', methods=['GET'])
def get_us_stocks():
    force_refresh = request.args.get('force') == 'true'
    req_custom    = request.args.get('custom', '')
    req_code      = request.args.get('code', '').strip().upper()
    now = time.time()

    # Load stocks from Google Sheet database
    sheet_stocks = get_stocks_from_sheet()
    us_sheet_stocks = [s for s in sheet_stocks if s.get('type') == 'US']

    if req_code:
        # Check if it matches a sheet stock to preserve name/sector overrides
        sheet_stock = next((s for s in us_sheet_stocks if s['code'].upper() == req_code.upper()), None)
        if sheet_stock:
            target = [{'code': req_code, 'name': sheet_stock.get('name') or req_code, 'sector': sheet_stock.get('category') or '美股個股'}]
        else:
            target = [{'code': req_code, 'name': req_code, 'sector': '美股個股'}]
        cache_key = f'us_single_{req_code}'
    else:
        if us_sheet_stocks:
            target = [{'code': s['code'], 'name': s['name'], 'sector': s.get('category') or '美股個股'} for s in us_sheet_stocks]
        else:
            custom_codes = [c.strip().upper() for c in req_custom.split(',') if c.strip()]
            existing     = {s['code'] for s in US_DEFAULT_STOCKS}
            extras       = [{'code': c, 'name': c, 'sector': '美股個股'}
                            for c in custom_codes if c not in existing]
            target    = list(US_DEFAULT_STOCKS) + extras
        cache_key = f'us_stocks_{req_custom}'

    if not force_refresh and cache_key in SERVER_CACHE:
        cached = SERVER_CACHE[cache_key]
        if now - cached['ts'] < CACHE_TTL:
            return jsonify({'status': 'ok', 'cached': True, 'stocks': cached['stocks']})

    ctx = ssl._create_unverified_context()
    stock_map = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_us_stock_data, s, ctx) for s in target]
        for f in futures:
            code, data = f.result()
            stock_map[code] = data

    results = []
    for s in target:
        code = s['code']
        if code in stock_map:
            res_data = dict(stock_map[code])
            # If we have a sheet definition for this US stock, override its EPS if specified in sheet
            sheet_stock = next((x for x in us_sheet_stocks if x['code'] == code), None)
            if sheet_stock:
                def _float(v):
                    if v in (None, ''): return None
                    try: return float(v)
                    except ValueError: return None
                
                s_ttm = _float(sheet_stock.get('epsTTM'))
                s_fwd = _float(sheet_stock.get('epsFwd'))
                
                if s_ttm is not None: res_data['epsTTM'] = s_ttm
                if s_fwd is not None: res_data['epsFwd'] = s_fwd
                
                # Re-calculate P/E multiples if EPS was overridden
                price = res_data.get('price', 0)
                if price > 0:
                    if res_data['epsTTM'] and res_data['epsTTM'] > 0:
                        res_data['peTTM'] = round(price / res_data['epsTTM'], 2)
                    else:
                        res_data['peTTM'] = None
                    if res_data['epsFwd'] and res_data['epsFwd'] > 0:
                        res_data['peFwd'] = round(price / res_data['epsFwd'], 2)
                    else:
                        res_data['peFwd'] = None
            results.append(res_data)

    SERVER_CACHE[cache_key] = {'ts': now, 'stocks': results}
    return jsonify({'status': 'ok', 'cached': False, 'stocks': results})

@app.route('/api/debug/gas', methods=['GET'])
def debug_gas():
    """Diagnostic endpoint: tests GAS write with a dummy stock and returns raw response."""
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    gas_url = os.environ.get('GAS_API_URL', '')
    gas_key = os.environ.get('GAS_SECRET_KEY', '')
    test_payload = {
        'key': gas_key,
        'action': 'save_stock',
        'stock': {
            'code': 'DEBUG_TEST',
            'name': 'Debug Test',
            'category': 'Debug',
            'eps2025': None,
            'eps2026q1': None,
            'eps2026q2': None,
            'epsTTM': None,
            'epsFwd': None,
            'type': 'TW'
        }
    }
    encoded = urllib.parse.urlencode({'payload': json.dumps(test_payload)})
    full_url = f"{gas_url}?{encoded}"
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'}, method='GET')
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            raw = resp.read().decode('utf-8')
            return jsonify({'status': 'ok', 'gas_response': raw, 'gas_url_prefix': gas_url[:60], 'key_len': len(gas_key)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'gas_url_prefix': gas_url[:60]})

@app.route('/api/stocks/save', methods=['POST'])
def save_stock():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return jsonify({'status': 'error', 'message': 'Google Sheets backend not configured'}), 500
        
    req_data = request.get_json() or {}
    code = req_data.get('code', '').strip()
    if not code:
        return jsonify({'status': 'error', 'message': 'Missing stock code'}), 400
        
    payload = {
        'key': gas_key,
        'action': 'save_stock',
        'stock': {
            'code': code,
            'name': req_data.get('name', code).strip(),
            'category': req_data.get('category', '').strip(),
            'eps2025': req_data.get('eps2025'),
            'eps2026q1': req_data.get('eps2026q1'),
            'eps2026q2': req_data.get('eps2026q2'),
            'epsTTM': req_data.get('epsTTM'),
            'epsFwd': req_data.get('epsFwd'),
            'type': req_data.get('type', 'TW').strip().upper()
        }
    }
    
    try:
        res = call_gas_api_write(gas_url, payload)
        SERVER_CACHE.clear()
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stocks/delete', methods=['POST'])
def delete_stock_api():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return jsonify({'status': 'error', 'message': 'Google Sheets backend not configured'}), 500
        
    req_data = request.get_json() or {}
    code = req_data.get('code', '').strip()
    if not code:
        return jsonify({'status': 'error', 'message': 'Missing stock code'}), 400
        
    payload = {
        'key': gas_key,
        'action': 'delete_stock',
        'code': code
    }
    
    try:
        res = call_gas_api_write(gas_url, payload)
        SERVER_CACHE.clear()
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─── Custom Stock Order (Cloud Sync) ─────────────────────────────────────────

@app.route('/api/order/get', methods=['GET'])
def get_order():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return jsonify({'status': 'ok', 'order': []})
    try:
        url = f"{gas_url}?key={urllib.parse.quote(gas_key)}&action=get_order"
        res = call_gas_api(url)
        if res.get('status') == 'ok':
            return jsonify({'status': 'ok', 'order': res.get('order', [])})
        return jsonify({'status': 'ok', 'order': []})
    except Exception as e:
        print(f"Error fetching order from sheet: {e}")
        return jsonify({'status': 'ok', 'order': []})


@app.route('/api/order/save', methods=['POST'])
def save_order():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    gas_url = os.environ.get('GAS_API_URL')
    gas_key = os.environ.get('GAS_SECRET_KEY')
    if not gas_url or not gas_key:
        return jsonify({'status': 'error', 'message': 'Google Sheets backend not configured'}), 500
    req_data = request.get_json() or {}
    order = req_data.get('order', [])
    if not isinstance(order, list):
        return jsonify({'status': 'error', 'message': 'order must be a list'}), 400
    payload = {
        'key': gas_key,
        'action': 'save_order',
        'order': order
    }
    try:
        res = call_gas_api_write(gas_url, payload)
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─── Global Macro Commodities, Freight & Crypto ──────────────────────────────

MACRO_ASSETS_CONFIG = [

    {'code': 'BZ=F',    'name': '布蘭特原油期貨',       'category': '能源期貨',  'unit': 'USD/桶'},
    {'code': 'GC=F',    'name': '黃金期貨',            'category': '貴金屬',    'unit': 'USD/盎司'},
    {'code': 'SI=F',    'name': '白銀期貨',            'category': '貴金屬',    'unit': 'USD/盎司'},
    {'code': 'BTC-USD', 'name': '比特幣',              'category': '加密貨幣',  'unit': 'USD'},
    {'code': 'SCFI',    'name': '上海出口集裝箱運價指數', 'category': '航運運價',  'unit': '點'},
    {'code': 'CCFI',    'name': '中國出口集裝箱運價指數', 'category': '航運運價',  'unit': '點'},
]

def fetch_freight_index(code, ctx):
    """Fetch SCFI / CCFI freight index from sse.net.cn or return verified fallback."""
    fallback_data = {
        'SCFI': {'price': 3062.95, 'change': -17.36, 'changePct': -0.56, 'date': '2026-07-24'},
        'CCFI': {'price': 1901.27, 'change': -9.55,  'changePct': -0.50, 'date': '2026-07-24'}
    }
    base_info = fallback_data.get(code, {'price': 0, 'change': 0, 'changePct': 0, 'date': ''})
    try:
        url = f"https://www.sse.net.cn/index/getSingleIndex?indexType={code.lower()}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=3) as res:
            d = json.loads(res.read().decode('utf-8'))
            if isinstance(d, dict) and d.get('indexValue'):
                val = float(d['indexValue'])
                chg = float(d.get('changeValue', 0))
                chg_pct = float(d.get('changeRate', 0))
                date_s = d.get('indexDate', base_info['date'])
                return {
                    'price': round(val, 2),
                    'change': round(chg, 2),
                    'changePct': round(chg_pct, 2),
                    'date': date_s
                }
    except Exception:
        pass
    return base_info

def fetch_single_macro_asset(item, ctx):
    sym = item['code']
    cat = item['category']
    unit = item['unit']
    
    if sym in ('SCFI', 'CCFI'):
        fdata = fetch_freight_index(sym, ctx)
        return sym, {
            'code': sym,
            'name': item['name'],
            'category': cat,
            'unit': unit,
            'price': fdata['price'],
            'change': fdata['change'],
            'changePct': fdata['changePct'],
            'date': fdata['date'],
            'ma20': None, 'ma20Dir': 'flat', 'ma20Streak': 0,
            'ma60': None, 'ma60Dir': 'flat', 'ma60Streak': 0,
            'kVal': None, 'dVal': None,
            'isFreight': True
        }
        
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=1y&interval=1d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=6) as res:
            data = json.loads(res.read().decode('utf-8'))
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            quote = result['indicators']['quote'][0]
            raw_closes = quote.get('close', [])
            raw_highs = quote.get('high', [])
            raw_lows = quote.get('low', [])
            
            clean_pairs = []
            for ts, c, h, l in zip(timestamps, raw_closes,
                                   raw_highs if len(raw_highs)==len(timestamps) else [None]*len(timestamps),
                                   raw_lows if len(raw_lows)==len(timestamps) else [None]*len(timestamps)):
                if c is not None:
                    c_val = float(c)
                    h_val = float(h) if h is not None else c_val
                    l_val = float(l) if l is not None else c_val
                    clean_pairs.append((ts, c_val, h_val, l_val))
            
            if not clean_pairs:
                return sym, {}
                
            ts_list, prices, highs, lows = zip(*clean_pairs)
            ma20, dir20, streak20 = calc_series_ma_info(prices, 20)
            ma60, dir60, streak60 = calc_series_ma_info(prices, 60)
            k_val, d_val = calc_kd_info(highs, lows, prices)
            
            latest_price = round(prices[-1], 2)
            prev_price = round(prices[-2], 2) if len(prices) >= 2 else latest_price
            change = round(latest_price - prev_price, 2)
            change_pct = round((change / prev_price) * 100, 2)
            date_str = datetime.datetime.fromtimestamp(ts_list[-1]).strftime('%Y-%m-%d')
            
            return sym, {
                'code': sym,
                'name': item['name'],
                'category': cat,
                'unit': unit,
                'price': latest_price,
                'change': change,
                'changePct': change_pct,
                'date': date_str,
                'ma20': ma20, 'ma20Dir': dir20, 'ma20Streak': streak20,
                'ma60': ma60, 'ma60Dir': dir60, 'ma60Streak': streak60,
                'kVal': k_val, 'dVal': d_val,
                'isFreight': False
            }
    except Exception:
        return sym, {}

@app.route('/api/macro_assets', methods=['GET'])
def get_macro_assets():
    force_refresh = request.args.get('force') == 'true'
    now = time.time()
    cache_key = 'macro_assets_cache'
    
    if not force_refresh and cache_key in SERVER_CACHE:
        cached = SERVER_CACHE[cache_key]
        if now - cached['ts'] < CACHE_TTL:
            return jsonify({'status': 'ok', 'cached': True, 'assets': cached['assets']})
            
    ctx = ssl._create_unverified_context()
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_single_macro_asset, item, ctx) for item in MACRO_ASSETS_CONFIG]
        for f in futures:
            code, asset_dict = f.result()
            if asset_dict:
                results.append(asset_dict)
                
    SERVER_CACHE[cache_key] = {'ts': now, 'assets': results}
    return jsonify({'status': 'ok', 'cached': False, 'assets': results})


if __name__ == '__main__':
    app.run(port=8080)

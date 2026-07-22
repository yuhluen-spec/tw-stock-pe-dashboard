import os
import urllib.request
import urllib.parse
import ssl
import json
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Base directory for static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Server-side Cache
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

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    date_param = request.args.get('date', '2026-07-21')
    req_code = request.args.get('code')
    req_all = request.args.get('all') == 'true'
    force_refresh = request.args.get('force') == 'true'
    date_yyyymmdd = date_param.replace('-', '')
    
    # Check Server-side Cache
    now = time.time()
    cache_key = f"{date_param}_{req_code or ('all' if req_all else 'default')}"
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

    # Parallel Execution: Fetch TWSE & TPEX prices
    with ThreadPoolExecutor(max_workers=5) as executor:
        twse_future = executor.submit(fetch_twse_prices, date_yyyymmdd, ctx)
        tpex_future = executor.submit(fetch_tpex_prices, date_param, ctx)

        twse_prices = twse_future.result()
        tpex_prices = tpex_future.result()

    all_raw_stocks = {**twse_prices, **tpex_prices}

    # Determine target stock codes
    if req_code:
        target_codes = [req_code]
    elif req_all:
        target_codes = list(all_raw_stocks.keys())
    else:
        # DEFAULT: Return ONLY core default tracked stocks (~18 stocks)!
        target_codes = DEFAULT_CORE_CODES

    # Parallel EPS derivation for target stocks
    eps_results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        eps_futures = [executor.submit(derive_eps_from_finmind, c, ctx) for c in target_codes]
        for f in eps_futures:
            code, eps_dict = f.result()
            eps_results[code] = eps_dict

    result_stocks = []
    for code in target_codes:
        raw_info = all_raw_stocks.get(code, {})
        name = raw_info.get('name', code)
        price = raw_info.get('price', SNAPSHOT_PRICES.get(code, 100.0))
        category = STOCK_CATEGORY_MAP.get(code, '台股個股')
        eps_data = eps_results.get(code, EPS_DERIVED_MAP.get(code, {}))

        result_stocks.append({
            'id': code,
            'category': category,
            'code': code,
            'name': name,
            'eps2025': eps_data.get('eps2025'),
            'eps2026q1': eps_data.get('eps2026q1'),
            'eps2026q2': eps_data.get('eps2026q2'),
            'epsTTM': eps_data.get('epsTTM'),
            'price': price
        })

    SERVER_CACHE[cache_key] = {
        'ts': now,
        'stocks': result_stocks
    }

    return jsonify({
        'status': 'ok',
        'cached': False,
        'date': date_param,
        'total': len(result_stocks),
        'stocks': result_stocks
    })

if __name__ == '__main__':
    app.run(port=8080)

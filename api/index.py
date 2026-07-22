import os
import urllib.request
import urllib.parse
import ssl
import json
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Base directory for static files (parent of api folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Server-side Cache
SERVER_CACHE = {}
CACHE_TTL = 1800  # 30 minutes

STOCK_METADATA = [
    { 'code': '3010', 'name': '華立', 'category': '半導體材料', 'market': 'TWSE' },
    { 'code': '2303', 'name': '聯電', 'category': '晶圓代工', 'market': 'TWSE' },
    { 'code': '2330', 'name': '台積電', 'category': '晶圓代工', 'market': 'TWSE' },
    { 'code': '5347', 'name': '世界先進', 'category': '晶圓代工', 'market': 'TPEX' },
    { 'code': '5274', 'name': '信驊', 'category': 'IC設計', 'market': 'TPEX' },
    { 'code': '2059', 'name': '川湖', 'category': '軸承/滑軌', 'market': 'TWSE' },
    { 'code': '7769', 'name': '鴻勁', 'category': '半導體設備', 'market': 'TPEX' },
    { 'code': '6515', 'name': '穎崴', 'category': '半導體封測材料', 'market': 'TWSE' },
    { 'code': '6223', 'name': '旺矽', 'category': '半導體封測材料', 'market': 'TWSE' },
    { 'code': '1301', 'name': '台塑', 'category': '塑膠', 'market': 'TWSE' },
    { 'code': '1303', 'name': '南亞', 'category': '塑膠', 'market': 'TWSE' },
    { 'code': '1326', 'name': '台化', 'category': '塑膠', 'market': 'TWSE' },
    { 'code': '2881', 'name': '富邦金', 'category': '金融保險', 'market': 'TWSE' },
    { 'code': '2882', 'name': '國泰金', 'category': '金融保險', 'market': 'TWSE' },
    { 'code': '2891', 'name': '中信金', 'category': '金融保險', 'market': 'TWSE' },
    { 'code': '6446', 'name': '藥華藥', 'category': '生技股', 'market': 'TPEX' },
    { 'code': '6472', 'name': '保瑞', 'category': '生技股', 'market': 'TWSE' },
    { 'code': '7799', 'name': '禾榮科', 'category': '生技股', 'market': 'TPEX' }
]

SNAPSHOT_PRICES_20260717 = {
    '3010': 116.00, '2303': 144.00, '2330': 2290.00, '5347': 169.00, '5274': 12950.00,
    '2059': 7890.00, '7769': 6070.00, '6515': 6055.00, '6223': 5600.00,
    '1301': 62.80, '1303': 199.00, '1326': 66.10, '2881': 124.50,
    '2882': 94.30, '2891': 62.10, '6446': 1195.00, '6472': 396.00, '7799': 415.50
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
        with urllib.request.urlopen(req, context=ctx, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            if data.get('stat') == 'OK':
                for t in data.get('tables', []):
                    for row in t.get('data', []):
                        if len(row) >= 9:
                            code = str(row[0]).strip()
                            name = str(row[1]).strip()
                            price_str = str(row[8]).replace(',', '').strip()
                            try:
                                p = float(price_str)
                                if p > 0: prices[code] = { 'price': p, 'name': name }
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
            with urllib.request.urlopen(req, context=ctx, timeout=3) as res:
                data = json.loads(res.read().decode('utf-8'))
                rows = data.get('aaData', [])
                for row in rows:
                    if len(row) >= 3:
                        code = str(row[0]).strip()
                        name = str(row[1]).strip()
                        price_str = str(row[2]).replace(',', '').strip()
                        try:
                            p = float(price_str)
                            if p > 0: prices[code] = { 'price': p, 'name': name }
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
    date_yyyymmdd = date_param.replace('-', '')
    
    # Check Server-side Cache (only for full list requests)
    now = time.time()
    if not req_code and date_param in SERVER_CACHE:
        cached_entry = SERVER_CACHE[date_param]
        if now - cached_entry['ts'] < CACHE_TTL:
            return jsonify({
                'status': 'ok',
                'cached': True,
                'date': date_param,
                'stocks': cached_entry['stocks']
            })

    ctx = ssl._create_unverified_context()
    
    # Determine target stocks
    target_metadata = STOCK_METADATA
    if req_code:
        existing_meta = next((s for s in STOCK_METADATA if s['code'] == req_code), None)
        if existing_meta:
            target_metadata = [existing_meta]
        else:
            target_metadata = [{ 'code': req_code, 'name': req_code, 'category': '自訂個股', 'market': 'TWSE' }]

    eps_results = {}
    twse_prices = {}
    tpex_prices = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        twse_future = executor.submit(fetch_twse_prices, date_yyyymmdd, ctx)
        tpex_future = executor.submit(fetch_tpex_prices, date_param, ctx)
        eps_futures = [executor.submit(derive_eps_from_finmind, item['code'], ctx) for item in target_metadata]

        twse_prices = twse_future.result()
        tpex_prices = tpex_future.result()

        for f in eps_futures:
            code, eps_dict = f.result()
            eps_results[code] = eps_dict

    live_info = {**twse_prices, **tpex_prices}

    result_stocks = []
    for item in target_metadata:
        code = item['code']
        live_item = live_info.get(code, {})
        price = live_item.get('price', SNAPSHOT_PRICES_20260717.get(code, 100.0))
        official_name = live_item.get('name', item['name'])
        eps_data = eps_results.get(code, EPS_DERIVED_MAP.get(code, {}))

        result_stocks.append({
            'id': code,
            'category': item['category'],
            'code': code,
            'name': official_name,
            'eps2025': eps_data.get('eps2025'),
            'eps2026q1': eps_data.get('eps2026q1'),
            'eps2026q2': eps_data.get('eps2026q2'),
            'epsTTM': eps_data.get('epsTTM'),
            'price': price
        })

    if not req_code:
        SERVER_CACHE[date_param] = {
            'ts': now,
            'stocks': result_stocks
        }

    return jsonify({
        'status': 'ok',
        'cached': False,
        'date': date_param,
        'stocks': result_stocks
    })

if __name__ == '__main__':
    app.run(port=8080)

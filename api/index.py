import os
import urllib.request
import urllib.parse
import ssl
import json
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

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
            data = [x for x in data if x.get('date', '') <= target_date_str]
            prices = [float(x['close']) for x in data if x.get('close') is not None]

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
                'ma60': ma60, 'ma60Dir': dir60, 'ma60Streak': streak60
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
        # DEFAULT: Return core default tracked stocks + any user custom stocks!
        target_codes = list(dict.fromkeys(DEFAULT_CORE_CODES + custom_codes))

    # Parallel EPS & MA derivation for target stocks
    eps_results = {}
    ma_results = {}
    with ThreadPoolExecutor(max_workers=15) as executor:
        eps_futures = [executor.submit(derive_eps_from_finmind, c, ctx) for c in target_codes]
        ma_futures = [executor.submit(fetch_ma_data, c, date_param, ctx) for c in target_codes]
        for f in eps_futures:
            code, eps_dict = f.result()
            eps_results[code] = eps_dict
        for f in ma_futures:
            code, ma_dict = f.result()
            ma_results[code] = ma_dict

    result_stocks = []
    for code in target_codes:
        raw_info = all_raw_stocks.get(code, {})
        name = raw_info.get('name', code)
        price = raw_info.get('price', SNAPSHOT_PRICES.get(code, 100.0))
        category = STOCK_CATEGORY_MAP.get(code, '台股個股')
        eps_data = eps_results.get(code, EPS_DERIVED_MAP.get(code, {}))
        ma_info = ma_results.get(code, {})

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
            'ma60Streak': ma_info.get('ma60Streak', 0)
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

INDEX_CONFIG = [
    {'code': '^TWII', 'name': '台灣加權指數', 'region': '台股'},
    {'code': '^DJI',  'name': '道瓊工業指數', 'region': '美股'},
    {'code': '^IXIC', 'name': '那斯達克指數', 'region': '美股'},
    {'code': '^SOX',  'name': '費城半導體指數', 'region': '美股'},
    {'code': '^GSPC', 'name': '標普500指數', 'region': '美股'}
]

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
            raw_volumes = quote.get('volume', [])
            
            clean_pairs = []
            for ts, c, v in zip(timestamps, raw_closes, raw_volumes if len(raw_volumes) == len(timestamps) else [None]*len(timestamps)):
                if c is not None:
                    clean_pairs.append((ts, float(c), float(v) if v is not None else 0.0))
            
            if not clean_pairs:
                return item['code'], {}
            
            ts_list, prices, volumes = zip(*clean_pairs)
            
            ma20, dir20, streak20 = calc_series_ma_info(prices, 20)
            ma60, dir60, streak60 = calc_series_ma_info(prices, 60)
            ma240, dir240, streak240 = calc_series_ma_info(prices, 240)
            
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

if __name__ == '__main__':
    app.run(port=8080)

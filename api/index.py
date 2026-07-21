import os
from flask import Flask, jsonify, request, send_from_directory
import urllib.request
import urllib.parse
import ssl
import json

app = Flask(__name__)

# Base directory for static files (parent of api folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STOCK_METADATA = [
    { 'code': '2303', 'name': '聯電', 'category': '晶圓代工' },
    { 'code': '2330', 'name': '台積電', 'category': '晶圓代工' },
    { 'code': '5347', 'name': '世界先進', 'category': '晶圓代工' },
    { 'code': '5274', 'name': '信驊', 'category': 'IC設計' },
    { 'code': '2059', 'name': '川湖', 'category': '軸承/滑軌' },
    { 'code': '7769', 'name': '鴻勁', 'category': '半導體設備' },
    { 'code': '6515', 'name': '穎崴', 'category': '半導體封測材料' },
    { 'code': '6223', 'name': '旺矽', 'category': '半導體封測材料' },
    { 'code': '1301', 'name': '台塑', 'category': '塑膠' },
    { 'code': '1303', 'name': '南亞', 'category': '塑膠' },
    { 'code': '1326', 'name': '台化', 'category': '塑膠' },
    { 'code': '2881', 'name': '富邦金', 'category': '金融保險' },
    { 'code': '2882', 'name': '國泰金', 'category': '金融保險' },
    { 'code': '2891', 'name': '中信金', 'category': '金融保險' },
    { 'code': '6446', 'name': '藥華藥', 'category': '生技股' },
    { 'code': '6472', 'name': '保瑞', 'category': '生技股' },
    { 'code': '7799', 'name': '禾榮科', 'category': '生技股' }
]

SNAPSHOT_PRICES_20260717 = {
    '2303': 144.00, '2330': 2290.00, '5347': 169.00, '5274': 12950.00,
    '2059': 7890.00, '7769': 6070.00, '6515': 6055.00, '6223': 5600.00,
    '1301': 62.80, '1303': 199.00, '1326': 66.10, '2881': 124.50,
    '2882': 94.30, '2891': 62.10, '6446': 1195.00, '6472': 396.00, '7799': 415.50
}

EPS_DERIVED_MAP = {
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
            return {
                'eps2025': eps2025 if eps2025 is not None else ref.get('eps2025'),
                'eps2026q1': eps2026q1 if eps2026q1 is not None else ref.get('eps2026q1'),
                'eps2026q2': eps2026q2 if eps2026q2 is not None else ref.get('eps2026q2'),
                'epsTTM': eps_ttm if eps_ttm is not None else ref.get('epsTTM')
            }
    except Exception:
        ref = EPS_DERIVED_MAP.get(stock_id, {})
        return {
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
                            price_str = str(row[8]).replace(',', '').strip()
                            try:
                                p = float(price_str)
                                if p > 0: prices[code] = p
                            except ValueError:
                                pass
    except Exception:
        pass
    return prices

# Route for serving static frontend files
@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if os.path.exists(os.path.join(BASE_DIR, filename)):
        return send_from_directory(BASE_DIR, filename)
    return send_from_directory(BASE_DIR, 'index.html')

# Route for stock API
@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    date_param = request.args.get('date', '2026-07-17')
    date_yyyymmdd = date_param.replace('-', '')
    
    ctx = ssl._create_unverified_context()
    live_prices = fetch_twse_prices(date_yyyymmdd, ctx)
    
    result_stocks = []
    for item in STOCK_METADATA:
        code = item['code']
        price = live_prices.get(code, SNAPSHOT_PRICES_20260717.get(code, 100.0))
        eps_data = derive_eps_from_finmind(code, ctx)
        
        result_stocks.append({
            'id': code,
            'category': item['category'],
            'code': code,
            'name': item['name'],
            'eps2025': eps_data.get('eps2025'),
            'eps2026q1': eps_data.get('eps2026q1'),
            'eps2026q2': eps_data.get('eps2026q2'),
            'epsTTM': eps_data.get('epsTTM'),
            'price': price
        })

    return jsonify({
        'status': 'ok',
        'date': date_param,
        'stocks': result_stocks
    })

if __name__ == '__main__':
    app.run(port=8080)

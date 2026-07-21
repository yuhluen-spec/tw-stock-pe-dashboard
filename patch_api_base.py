"""
Add API_BASE auto-detection to app.js for Firebase Hosting Spark Free Plan
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

api_base_code = """
const API_BASE = (window.location.hostname.includes('web.app') || window.location.hostname.includes('firebaseapp.com'))
  ? 'https://tw-stock-pe-dashboard.vercel.app'
  : '';
"""

if 'const API_BASE' not in content:
    content = content.replace("let stockList = [];", api_base_code + "\nlet stockList = [];")
    content = content.replace("fetch(`/api/stocks?date=${dateStr}`)", "fetch(`${API_BASE}/api/stocks?date=${dateStr}`)")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.js with API_BASE for Firebase Hosting!")

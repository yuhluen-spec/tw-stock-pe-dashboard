"""
Fix renderTabs ReferenceError in app.js, add 3010 華立 and dynamic stock lookup to api/index.py and TW_STOCK_MASTER
"""

# 1. Update app.js
with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

# Fix renderTabs active variable
old_render_tabs = """function renderTabs() {
  const cats = ['全部', ...new Set(stockList.map(s => s.category))];
  document.getElementById('industryTabs').innerHTML = cats.map(cat => {
    const val = cat === '全部' ? 'ALL' : cat;
    return `<button class="tab-pill ${active}" data-cat="${val}">${cat}</button>`;
  }).join('');"""

new_render_tabs = """function renderTabs() {
  const cats = ['全部', ...new Set(stockList.map(s => s.category))];
  document.getElementById('industryTabs').innerHTML = cats.map(cat => {
    const val = cat === '全部' ? 'ALL' : cat;
    const active = activeCategory === val ? 'active' : '';
    return `<button class="tab-pill ${active}" data-cat="${val}">${cat}</button>`;
  }).join('');"""

app_js = app_js.replace(old_render_tabs, new_render_tabs)

# Add 3010 華立 to TW_STOCK_MASTER if missing
if "{ code: '3010', name: '華立', category: '半導體材料' }" not in app_js:
  app_js = app_js.replace(
      "{ code: '2330', name: '台積電', category: '晶圓代工' },",
      "{ code: '3010', name: '華立', category: '半導體材料' },\n  { code: '2330', name: '台積電', category: '晶圓代工' },"
  )

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js!")

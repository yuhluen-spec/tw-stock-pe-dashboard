"""
Patch app.js to add custom user stocks persistence in localStorage
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

# Add custom stock persistence functions before renderTable
custom_stock_code = """
/* ─── Custom User Stocks Persistence ──────────────────────────────── */
const CUSTOM_STOCKS_KEY = 'tw_pe_custom_user_stocks';

function loadCustomStocks() {
  try {
    const raw = localStorage.getItem(CUSTOM_STOCKS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveCustomStocks(customList) {
  try {
    localStorage.setItem(CUSTOM_STOCKS_KEY, JSON.stringify(customList));
  } catch {}
}

function mergeCustomStocks(fetchedList) {
  const customStocks = loadCustomStocks();
  if (!customStocks || customStocks.length === 0) return fetchedList;

  const resultMap = new Map(fetchedList.map(s => [s.id, s]));
  customStocks.forEach(custom => {
    resultMap.set(custom.id, { ...resultMap.get(custom.id), ...custom });
  });

  return Array.from(resultMap.values());
}
"""

if 'CUSTOM_STOCKS_KEY' not in content:
    content = content.replace("/* ─── Render industry tabs", custom_stock_code + "\n/* ─── Render industry tabs")
    content = content.replace("stockList = cached;", "stockList = mergeCustomStocks(cached);")
    content = content.replace("stockList = data.stocks;", "stockList = mergeCustomStocks(data.stocks);")

    # Update form submit to persist custom stocks
    old_submit_end = "closeModal(); renderTabs(); renderTable();"
    new_submit_end = """saveCustomStocks(stockList.filter(s => !SNAPSHOT_PRICES_20260717[s.code] || s.isCustom)); closeModal(); renderTabs(); renderTable();"""
    content = content.replace(old_submit_end, new_submit_end)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.js enhanced with custom stock persistence!")

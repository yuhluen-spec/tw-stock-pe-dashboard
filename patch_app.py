"""
Patch app.js: Replace fetchStockData block with localStorage-cached version
and update DOMContentLoaded to use getLatestTradingDate()
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

lines = content.split('\n')

# ── Find fetchStockData block ──
start_idx = None
end_idx   = None
for i, ln in enumerate(lines):
    if start_idx is None and 'Fetch data' in ln and ln.strip().startswith('/*'):
        start_idx = i
    if start_idx is not None and i > start_idx + 2 and ln.strip() == '}':
        end_idx = i
        break

print(f'fetchStockData block: lines {start_idx+1}–{end_idx+1}')

# ── New block to insert ──
NEW_FETCH = r"""/* ─── LocalStorage Cache helpers ─────────────────────────────────── */
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const CACHE_PREFIX = 'tw_pe_';

function cacheKey(dateStr) { return CACHE_PREFIX + dateStr; }

function loadCache(dateStr) {
  try {
    const raw = localStorage.getItem(cacheKey(dateStr));
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (Date.now() - obj.ts > CACHE_TTL_MS) {
      localStorage.removeItem(cacheKey(dateStr));
      return null;
    }
    return obj.data;
  } catch { return null; }
}

function saveCache(dateStr, data) {
  try {
    localStorage.setItem(cacheKey(dateStr), JSON.stringify({ ts: Date.now(), data }));
    const keys = Object.keys(localStorage).filter(k => k.startsWith(CACHE_PREFIX));
    if (keys.length > 7) {
      keys.sort().slice(0, keys.length - 7).forEach(k => localStorage.removeItem(k));
    }
  } catch {}
}

/* ─── Get latest trading date (Mon–Fri, Taiwan timezone) ─────────── */
function getLatestTradingDate() {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Taipei' }));
  if (d.getHours() < 16) d.setDate(d.getDate() - 1);
  while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
  const yyyy = d.getFullYear();
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const dd   = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

/* ─── Fetch data (with LocalStorage cache) ───────────────────────── */
async function fetchStockData(dateStr, forceRefresh = false) {
  const btn = document.getElementById('btnLoadDateData');
  document.getElementById('datePicker').value = dateStr;

  // Try cache first (Shift+Click query btn to force refresh)
  if (!forceRefresh) {
    const cached = loadCache(dateStr);
    if (cached) {
      stockList = cached;
      const d = dateStr.replace(/-/g, '/');
      document.getElementById('priceHeaderDate').textContent = `${d} 收盤價`;
      document.getElementById('updateTime').textContent = `${d} ─ 快取資料`;
      document.getElementById('sidebarStatusText').textContent = `${d} (快取)`;
      renderTabs();
      renderTable();
      return;
    }
  }

  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
  btn.disabled = true;
  document.getElementById('updateTime').textContent = '資料載入中…';
  document.getElementById('sidebarStatusText').textContent = '載入中…';

  try {
    const res = await fetch(`/api/stocks?date=${dateStr}`);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    if (data.stocks) {
      stockList = data.stocks;
      saveCache(dateStr, stockList); // save to localStorage
      const d = dateStr.replace(/-/g, '/');
      document.getElementById('priceHeaderDate').textContent = `${d} 收盤價`;
      document.getElementById('updateTime').textContent = `${d} 已更新`;
      document.getElementById('sidebarStatusText').textContent = `${d} 已載入`;
      renderTabs();
      renderTable();
    }
  } catch (err) {
    document.getElementById('updateTime').textContent = '載入失敗，請重試';
    document.getElementById('sidebarStatusText').textContent = '載入失敗';
    console.error(err);
  } finally {
    btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
    btn.disabled = false;
  }
}"""

# ── Replace the block ──
new_lines = lines[:start_idx] + NEW_FETCH.split('\n') + lines[end_idx+1:]

# ── Fix DOMContentLoaded: replace initial fetch + click handler ──
result = '\n'.join(new_lines)

OLD_INIT = "  fetchStockData(datePicker.value);\n  initScrollShadow();\n\n  /* Date query */\n  document.getElementById('btnLoadDateData').addEventListener('click', () => fetchStockData(datePicker.value));"

NEW_INIT = """  // Auto-load latest trading date
  const latestDate = getLatestTradingDate();
  fetchStockData(latestDate);
  initScrollShadow();

  // Shift+Click = force refresh (bypass cache)
  document.getElementById('btnLoadDateData').addEventListener('click', (e) => {
    fetchStockData(document.getElementById('datePicker').value, e.shiftKey);
  });"""

if OLD_INIT in result:
    result = result.replace(OLD_INIT, NEW_INIT)
    print('DOMContentLoaded init patched OK')
else:
    print('WARNING: DOMContentLoaded init pattern not found, trying partial match...')
    # Try simpler match
    OLD2 = "  fetchStockData(datePicker.value);\n  initScrollShadow();"
    NEW2 = "  const latestDate = getLatestTradingDate();\n  fetchStockData(latestDate);\n  initScrollShadow();"
    if OLD2 in result:
        result = result.replace(OLD2, NEW2, 1)
        print('Partial DOMContentLoaded init patched OK')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(result)

print('Done! app.js patched successfully.')

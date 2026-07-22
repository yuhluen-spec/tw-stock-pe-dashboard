"""
Update app.js for single Sidebar update button with forceUpdateAllStocks global handler and step logs
"""

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

toast_and_global_fn = """
/* ─── Toast Notice & Global Update Handler ───────────────────────── */
function showToast(message) {
  let toast = document.getElementById('toastNotice');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toastNotice';
    toast.className = 'toast-notice';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${message}`;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

function forceUpdateAllStocks() {
  console.log('🔥 [手動觸發] 點擊【更新全台股資料】按鈕！發起連線刷新...');
  const datePicker = document.getElementById('datePicker');
  const dateStr = datePicker ? datePicker.value : getLatestTradingDate();
  fetchStockData(dateStr, true);
}
window.forceUpdateAllStocks = forceUpdateAllStocks;
"""

if 'function forceUpdateAllStocks' not in app_js:
    app_js = app_js.replace("/* ─── Fetch data (with LocalStorage cache)", toast_and_global_fn + "\n/* ─── Fetch data (with LocalStorage cache)")

old_fetch_body = """async function fetchStockData(dateStr, forceRefresh = false) {
  const btn = document.getElementById('btnLoadDateData');
  const datePicker = document.getElementById('datePicker');
  if (datePicker) datePicker.value = dateStr;

  if (!forceRefresh) {
    const cached = loadCache(dateStr);
    if (cached) {
      stockList = mergeCustomStocks(cached);
      const d = dateStr.replace(/-/g, '/');
      const headEl = document.getElementById('priceHeaderDate');
      if (headEl) headEl.textContent = `${d} 收盤價`;
      const updateEl = document.getElementById('updateTime');
      if (updateEl) updateEl.textContent = `${d} ─ 快取資料`;
      const sideEl = document.getElementById('sidebarStatusText');
      if (sideEl) sideEl.textContent = `${d} (快取)`;
      renderTabs();
      renderTable();
      return;
    }
  }

  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    btn.disabled = true;
  }
  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…' : '資料載入中…';
  const sideEl = document.getElementById('sidebarStatusText');
  if (sideEl) sideEl.textContent = '載入中…';

  try {
    const res = await fetch(`/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : ''));
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    if (data.stocks) {
      stockList = mergeCustomStocks(data.stocks);
      saveCache(dateStr, data.stocks);
      const d = dateStr.replace(/-/g, '/');
      const headEl = document.getElementById('priceHeaderDate');
      if (headEl) headEl.textContent = `${d} 收盤價`;
      if (updateEl) updateEl.textContent = `${d} 已更新`;
      if (sideEl) sideEl.textContent = `${d} 已載入`;
      renderTabs();
      renderTable();
    }
  } catch (err) {
    if (updateEl) updateEl.textContent = '載入失敗，請重試';
    if (sideEl) sideEl.textContent = '載入失敗';
    console.error(err);
  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
      btn.disabled = false;
    }
  }
}"""

new_fetch_body = """async function fetchStockData(dateStr, forceRefresh = false) {
  console.log(`🚀 [台股更新 1/5] 開始股票更新 (日期: ${dateStr}, 強制連線刷新 forceRefresh: ${forceRefresh})`);
  const btn = document.getElementById('btnLoadDateData');
  const sideUpdateBtn = document.getElementById('sidebarBtnUpdateAll');
  const datePicker = document.getElementById('datePicker');
  if (datePicker) datePicker.value = dateStr;

  if (!forceRefresh) {
    const cached = loadCache(dateStr);
    if (cached) {
      console.log(`⚡ [台股快取] 從 LocalStorage 快取中讀取 ${cached.length} 檔股票數據。`);
      stockList = mergeCustomStocks(cached);
      const d = dateStr.replace(/-/g, '/');
      const headEl = document.getElementById('priceHeaderDate');
      if (headEl) headEl.textContent = `${d} 收盤價`;
      const updateEl = document.getElementById('updateTime');
      if (updateEl) updateEl.textContent = `${d} ─ 快取資料`;
      const sideEl = document.getElementById('sidebarStatusText');
      if (sideEl) sideEl.textContent = `${d} (快取)`;
      renderTabs();
      renderTable();
      return;
    }
  }

  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    btn.disabled = true;
  }

  if (sideUpdateBtn) {
    sideUpdateBtn.disabled = true;
    sideUpdateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 更新中…';
  }

  if (forceRefresh) {
    showToast('🔄 正從證交所與櫃買中心連線更新 2000+ 檔台股…');
  }

  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 正從證交所即時更新 2000+ 檔台股…' : '資料載入中…';
  const sideEl = document.getElementById('sidebarStatusText');
  if (sideEl) sideEl.textContent = '載入中…';

  const apiUrl = `/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : '');
  console.log(`🌐 [台股更新 2/5] 發起 HTTP 請求: ${apiUrl}`);

  try {
    const startTime = Date.now();
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API error HTTP ${res.status}`);
    const data = await res.json();
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    const totalCount = data.total || data.stocks?.length || 0;

    console.log(`✅ [台股更新 3/5] API 回應成功 (耗時 ${duration}秒)! 狀態: ${data.status}, 取得 ${totalCount} 檔全台股數據。`);

    if (data.stocks) {
      stockList = mergeCustomStocks(data.stocks);
      saveCache(dateStr, data.stocks);
      console.log(`💾 [台股更新 4/5] 已將 ${data.stocks.length} 檔股票存入 LocalStorage。`);

      const d = dateStr.replace(/-/g, '/');
      const headEl = document.getElementById('priceHeaderDate');
      if (headEl) headEl.textContent = `${d} 收盤價`;
      if (updateEl) updateEl.textContent = `${d} ─ 已載入 ${totalCount} 檔全台股`;
      if (sideEl) sideEl.textContent = `${d} (${totalCount}檔)`;

      console.log(`🎨 [台股更新 5/5] 重新渲染產業 Tabs 與表格完畢！`);
      renderTabs();
      renderTable();

      if (forceRefresh) {
        showToast(`已連線更新 ${totalCount} 檔全台股最新收盤價！`);
      }
    }
  } catch (err) {
    console.error(`❌ [台股更新失敗]`, err);
    if (updateEl) updateEl.textContent = '載入失敗，請重試';
    if (sideEl) sideEl.textContent = '載入失敗';
  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
      btn.disabled = false;
    }
    if (sideUpdateBtn) {
      sideUpdateBtn.disabled = false;
      sideUpdateBtn.innerHTML = '<i class="fa-solid fa-rotate"></i> 更新全台股資料';
    }
  }
}"""

app_js = app_js.replace(old_fetch_body, new_fetch_body)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js with single sidebar update button logic!")

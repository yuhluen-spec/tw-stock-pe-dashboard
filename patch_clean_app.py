"""
Patch clean app.js to add console logs, spinner updates, and toast notifications
"""

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

target_old = """async function fetchStockData(dateStr, forceRefresh = false) {
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

replacement_new = """async function fetchStockData(dateStr, forceRefresh = false) {
  console.log(`🚀 [台股更新 1/5] 開始執行股票更新 (日期: ${dateStr}, 強制連線刷新 forceRefresh: ${forceRefresh})`);
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
    sideUpdateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>更新中…</span>';
  }

  if (forceRefresh) {
    showToast('🔄 正從證交所與櫃買中心連線更新 2000+ 檔台股…');
  }

  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…' : '資料載入中…';
  const sideEl = document.getElementById('sidebarStatusText');
  if (sideEl) sideEl.textContent = '載入中…';

  const apiUrl = `/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : '');
  console.log(`🌐 [台股更新 2/5] 發起 HTTP 請求: ${apiUrl}`);

  try {
    const startTime = Date.now();
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`HTTP 錯誤 ${res.status}`);
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
      console.log(`🎉 [台股更新完成] 成功完成 2000+ 檔全台股更新！`);
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

if target_old in app_js:
    app_js = app_js.replace(target_old, replacement_new)
    print("SUCCESS: Target replaced!")
else:
    print("Target not found, checking exact string match...")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

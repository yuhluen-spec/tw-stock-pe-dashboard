"""
Add step-by-step console.log execution flow tracking to fetchStockData in app.js
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

# Update fetchStockData to log every step to console
old_fetch_fn = """async function fetchStockData(dateStr, forceRefresh = false) {
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

  const updateBtns = [
    document.getElementById('btnLoadDateData'),
    document.getElementById('btnUpdateAllMain'),
    document.getElementById('btnUpdateAllTop'),
    document.getElementById('sidebarBtnUpdateAll')
  ].filter(Boolean);

  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    btn.disabled = true;
  }

  if (forceRefresh) {
    updateBtns.forEach(b => {
      b.disabled = true;
      b.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>更新中…</span>';
    });
    showToast('🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…');
  }

  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 即時更新 2000+ 檔台股中…' : '資料載入中…';
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
      const totalCount = data.total || data.stocks.length;
      if (updateEl) updateEl.textContent = `${d} ─ 已載入 ${totalCount} 檔全台股`;
      if (sideEl) sideEl.textContent = `${d} (${totalCount}檔)`;
      renderTabs();
      renderTable();
      if (forceRefresh) {
        showToast(`已連線更新 ${totalCount} 檔全台股最新收盤價！`);
      }
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
    updateBtns.forEach(b => {
      b.disabled = false;
      if (b.id === 'sidebarBtnUpdateAll') {
        b.innerHTML = '<i class="fa-solid fa-rotate"></i> 更新全台股資料';
      } else {
        b.innerHTML = '<i class="fa-solid fa-rotate"></i> <span>更新資料</span>';
      }
    });
  }
}"""

new_fetch_fn = """async function fetchStockData(dateStr, forceRefresh = false) {
  console.log(`🚀 [台股更新流程 1/6] 開始執行股票更新 (日期: ${dateStr}, 強制連線刷新: ${forceRefresh})`);
  const btn = document.getElementById('btnLoadDateData');
  const datePicker = document.getElementById('datePicker');
  if (datePicker) datePicker.value = dateStr;

  if (!forceRefresh) {
    const cached = loadCache(dateStr);
    if (cached) {
      console.log(`⚡ [台股更新流程] 從 LocalStorage 快取中瞬間載入 ${cached.length} 檔股票數據。`);
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

  const updateBtns = [
    document.getElementById('btnLoadDateData'),
    document.getElementById('btnUpdateAllMain'),
    document.getElementById('btnUpdateAllTop'),
    document.getElementById('sidebarBtnUpdateAll')
  ].filter(Boolean);

  console.log(`⏳ [台股更新流程 2/6] 已停用 ${updateBtns.length} 個按鈕並切換圖示為「更新中…」轉圈效果。`);

  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    btn.disabled = true;
  }

  if (forceRefresh) {
    updateBtns.forEach(b => {
      b.disabled = true;
      b.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>更新中…</span>';
    });
    showToast('🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…');
  }

  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 即時更新 2000+ 檔台股中…' : '資料載入中…';
  const sideEl = document.getElementById('sidebarStatusText');
  if (sideEl) sideEl.textContent = '載入中…';

  const apiUrl = `/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : '');
  console.log(`🌐 [台股更新流程 3/6] 向後端 API 發起 HTTP GET 請求: ${apiUrl}`);

  try {
    const startTime = Date.now();
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`HTTP 錯誤! 狀態碼: ${res.status}`);
    const data = await res.json();
    const fetchDuration = ((Date.now() - startTime) / 1000).toFixed(2);
    
    console.log(`✅ [台股更新流程 4/6] 收到 API 回應 (耗時 ${fetchDuration}秒)! 狀態: ${data.status}, 總筆數: ${data.total || data.stocks?.length}`);

    if (data.stocks) {
      stockList = mergeCustomStocks(data.stocks);
      saveCache(dateStr, data.stocks);
      console.log(`💾 [台股更新流程 5/6] 成功將 ${data.stocks.length} 檔股票數據寫入 LocalStorage 快取。`);

      const d = dateStr.replace(/-/g, '/');
      const headEl = document.getElementById('priceHeaderDate');
      if (headEl) headEl.textContent = `${d} 收盤價`;
      const totalCount = data.total || data.stocks.length;
      if (updateEl) updateEl.textContent = `${d} ─ 已載入 ${totalCount} 檔全台股`;
      if (sideEl) sideEl.textContent = `${d} (${totalCount}檔)`;

      console.log(`🎨 [台股更新流程 6/6] 重新渲染產業 Tabs 與股票表格完畢！`);
      renderTabs();
      renderTable();

      if (forceRefresh) {
        showToast(`已連線更新 ${totalCount} 檔全台股最新收盤價！`);
      }
      console.log(`🎉 [台股更新流程] 成功完成全台股更新！`);
    }
  } catch (err) {
    console.error(`❌ [台股更新流程錯誤] 請求失敗:`, err);
    if (updateEl) updateEl.textContent = '載入失敗，請重試';
    if (sideEl) sideEl.textContent = '載入失敗';
  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
      btn.disabled = false;
    }
    updateBtns.forEach(b => {
      b.disabled = false;
      if (b.id === 'sidebarBtnUpdateAll') {
        b.innerHTML = '<i class="fa-solid fa-rotate"></i> 更新全台股資料';
      } else {
        b.innerHTML = '<i class="fa-solid fa-rotate"></i> <span>更新資料</span>';
      }
    });
    console.log(`🏁 [台股更新流程] 按鈕狀態復原完畢。`);
  }
}"""

app_js = app_js.replace(old_fetch_fn, new_fetch_fn)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Added detailed console.log tracking to app.js!")

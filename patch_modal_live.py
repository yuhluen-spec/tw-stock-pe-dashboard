"""
Update app.js with fetchLiveStockInModal function and updated default load / update behavior
"""

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

modal_live_code = """
/* ─── Modal Live Stock Fetcher (證交所/櫃買中心即時查詢個股) ──────────────── */
async function fetchLiveStockInModal() {
  const searchInput = document.getElementById('modalStockSearch');
  const codeInput = document.getElementById('inputCode');
  const queryRaw = (searchInput?.value || codeInput?.value || '').trim();
  const codeMatch = queryRaw.match(/\\d{4}/);
  
  if (!codeMatch) {
    showToast('請在搜尋框輸入 4 位數字股票代號（例如：2383、3665、6274、2317）');
    if (searchInput) searchInput.focus();
    return;
  }

  const code = codeMatch[0];
  const spinner = document.getElementById('modalSearchSpinner');
  const btn = document.getElementById('btnSearchLiveStock');
  
  if (spinner) spinner.style.display = 'inline-block';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 正在連線證交所與櫃買中心查詢…';
  }

  try {
    const datePicker = document.getElementById('datePicker');
    const dateStr = datePicker ? datePicker.value : getLatestTradingDate();
    const res = await fetch(`/api/stocks?date=${dateStr}&code=${code}`);
    
    if (res.ok) {
      const data = await res.json();
      const match = data.stocks?.find(s => s.code === code) || data.stocks?.[0];
      
      if (match) {
        const codeEl = document.getElementById('inputCode');
        const nameEl = document.getElementById('inputName');
        const catEl = document.getElementById('inputCategory');
        const eps25 = document.getElementById('inputEps2025');
        const eps26q1 = document.getElementById('inputEps2026Q1');
        const eps26q2 = document.getElementById('inputEps2026Q2');
        const prEl = document.getElementById('inputPrice');

        if (codeEl) codeEl.value = match.code;
        if (nameEl) nameEl.value = match.name;
        if (catEl) catEl.value = match.category || '台股個股';
        if (eps25) eps25.value = match.eps2025 ?? '';
        if (eps26q1) eps26q1.value = match.eps2026q1 ?? '';
        if (eps26q2) eps26q2.value = match.eps2026q2 ?? '';
        if (prEl) prEl.value = match.price ?? '';
        if (searchInput) searchInput.value = `${match.code} ${match.name}`;

        showToast(`✅ 成功取得 [${match.code} ${match.name}] 最新收盤價與數據！`);
      } else {
        showToast(`⚠️ 查無代號 [${code}] 數據，請確認代號是否正確。`);
      }
    }
  } catch (err) {
    console.error('Fetch live stock failed:', err);
    showToast('連線證交所失敗，請檢查網路後重試');
  } finally {
    if (spinner) spinner.style.display = 'none';
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-bolt"></i> <span>線上即時連線抓取股票資料 (證交所/櫃買中心)</span>';
    }
  }
}
window.fetchLiveStockInModal = fetchLiveStockInModal;
"""

if 'function fetchLiveStockInModal' not in app_js:
    app_js = app_js + "\n" + modal_live_code

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js with fetchLiveStockInModal function!")

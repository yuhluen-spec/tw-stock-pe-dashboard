"""
Update app.js with force=true parameter and event handlers for all 3 update buttons
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

# Update fetchStockData to add &force=true to fetch URL when forceRefresh is True
old_fetch_url = "const res = await fetch(`/api/stocks?date=${dateStr}`);"
new_fetch_url = "const res = await fetch(`/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : ''));"

app_js = app_js.replace(old_fetch_url, new_fetch_url)

# Update loading status message when forceRefresh is true
old_loading_msg = "if (updateEl) updateEl.textContent = '資料載入中…';"
new_loading_msg = "if (updateEl) updateEl.textContent = forceRefresh ? '🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…' : '資料載入中…';"

app_js = app_js.replace(old_loading_msg, new_loading_msg)

# Update event listener bindings in DOMContentLoaded
old_listeners = """  const handleUpdateAll = () => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, true);
  };

  document.getElementById('btnUpdateAllMain')?.addEventListener('click', handleUpdateAll);
  document.getElementById('btnUpdateAllTop')?.addEventListener('click', handleUpdateAll);"""

new_listeners = """  const handleUpdateAll = () => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, true);
  };

  document.getElementById('btnUpdateAllMain')?.addEventListener('click', handleUpdateAll);
  document.getElementById('btnUpdateAllTop')?.addEventListener('click', handleUpdateAll);
  document.getElementById('sidebarBtnUpdateAll')?.addEventListener('click', handleUpdateAll);"""

app_js = app_js.replace(old_listeners, new_listeners)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js with force=true parameter and sidebar button listener!")

"""
Update app.js to handle Update All Stocks buttons and update status display with stock count
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

# Update fetchStockData status text to show total stock count if available
old_success_block = """      if (updateEl) updateEl.textContent = `${d} 已更新`;
      if (sideEl) sideEl.textContent = `${d} 已載入`;"""

new_success_block = """      const totalCount = data.total || data.stocks.length;
      if (updateEl) updateEl.textContent = `${d} ─ 已載入 ${totalCount} 檔全台股`;
      if (sideEl) sideEl.textContent = `${d} (${totalCount}檔)`;"""

app_js = app_js.replace(old_success_block, new_success_block)

# Add event listeners for btnUpdateAllMain and btnUpdateAllTop
old_btn_listeners = """  document.getElementById('btnLoadDateData')?.addEventListener('click', (e) => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, e.shiftKey);
  });"""

new_btn_listeners = """  const handleUpdateAll = () => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, true);
  };

  document.getElementById('btnUpdateAllMain')?.addEventListener('click', handleUpdateAll);
  document.getElementById('btnUpdateAllTop')?.addEventListener('click', handleUpdateAll);

  document.getElementById('btnLoadDateData')?.addEventListener('click', (e) => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, e.shiftKey);
  });"""

app_js = app_js.replace(old_btn_listeners, new_btn_listeners)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js with Update All Stocks button handlers!")

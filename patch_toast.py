"""
Add showToast function and toast feedback on fetchStockData completion to app.js
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

toast_code = """
/* ─── Toast Notice Helper ────────────────────────────────────────── */
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
"""

if 'function showToast' not in app_js:
    app_js = app_js.replace("/* ─── Format helpers", toast_code + "\n/* ─── Format helpers")

# Add showToast call when forceRefresh finishes successfully in fetchStockData
old_render = "renderTabs();\n      renderTable();"
new_render = """renderTabs();
      renderTable();
      if (forceRefresh) {
        showToast(`已連線更新 ${totalCount} 檔全台股最新收盤價！`);
      }"""

if "if (forceRefresh) {" not in app_js:
    app_js = app_js.replace(old_render, new_render, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Added showToast helper and visual feedback to app.js!")

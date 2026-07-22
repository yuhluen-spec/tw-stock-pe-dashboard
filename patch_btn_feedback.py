"""
Fix app.js so that Update buttons display '更新中…' spinner feedback when clicked
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

# Update fetchStockData to show spinner & disable all update buttons
old_fetch_start = """  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    btn.disabled = true;
  }
  const updateEl = document.getElementById('updateTime');
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…' : '資料載入中…';"""

new_fetch_start = """  const updateBtns = [
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
  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 即時更新 2000+ 檔台股中…' : '資料載入中…';"""

app_js = app_js.replace(old_fetch_start, new_fetch_start)

# Update fetchStockData finally block to restore all update buttons
old_fetch_finally = """  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
      btn.disabled = false;
    }
  }"""

new_fetch_finally = """  } finally {
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
  }"""

app_js = app_js.replace(old_fetch_finally, new_fetch_finally)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Updated app.js with instant '更新中…' spinner feedback on all update buttons!")

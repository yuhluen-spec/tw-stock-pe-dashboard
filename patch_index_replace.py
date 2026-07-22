"""
Replace fetchStockData cleanly in app.js
"""

with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'async function fetchStockData(' in line:
        start_idx = i
        break

if start_idx is not None:
    for j in range(start_idx, len(lines)):
        if lines[j].strip() == '}':
            end_idx = j
            break

print(f"Found fetchStockData from line {start_idx+1} to {end_idx+1}")

new_fn = [
    "async function fetchStockData(dateStr, forceRefresh = false) {\n",
    "  console.log(`🚀 [台股更新流程 1/6] 開始執行股票更新 (日期: ${dateStr}, 強制連線刷新: ${forceRefresh})`);\n",
    "  const btn = document.getElementById('btnLoadDateData');\n",
    "  const datePicker = document.getElementById('datePicker');\n",
    "  if (datePicker) datePicker.value = dateStr;\n",
    "\n",
    "  if (!forceRefresh) {\n",
    "    const cached = loadCache(dateStr);\n",
    "    if (cached) {\n",
    "      console.log(`⚡ [台股更新流程] 從 LocalStorage 快取中瞬間載入 ${cached.length} 檔股票數據。`);\n",
    "      stockList = mergeCustomStocks(cached);\n",
    "      const d = dateStr.replace(/-/g, '/');\n",
    "      const headEl = document.getElementById('priceHeaderDate');\n",
    "      if (headEl) headEl.textContent = `${d} 收盤價`;\n",
    "      const updateEl = document.getElementById('updateTime');\n",
    "      if (updateEl) updateEl.textContent = `${d} ─ 快取資料`;\n",
    "      const sideEl = document.getElementById('sidebarStatusText');\n",
    "      if (sideEl) sideEl.textContent = `${d} (快取)`;\n",
    "      renderTabs();\n",
    "      renderTable();\n",
    "      return;\n",
    "    }\n",
    "  }\n",
    "\n",
    "  const updateBtns = [\n",
    "    document.getElementById('btnLoadDateData'),\n",
    "    document.getElementById('btnUpdateAllMain'),\n",
    "    document.getElementById('btnUpdateAllTop'),\n",
    "    document.getElementById('sidebarBtnUpdateAll')\n",
    "  ].filter(Boolean);\n",
    "\n",
    "  console.log(`⏳ [台股更新流程 2/6] 已將 ${updateBtns.length} 個按鈕切換圖示為「更新中…」轉圈效果並停用。`);\n",
    "\n",
    "  if (btn) {\n",
    "    btn.innerHTML = '<i class=\"fa-solid fa-spinner fa-spin\"></i>';\n",
    "    btn.disabled = true;\n",
    "  }\n",
    "\n",
    "  if (forceRefresh) {\n",
    "    updateBtns.forEach(b => {\n",
    "      b.disabled = true;\n",
    "      if (b.id === 'sidebarBtnUpdateAll') {\n",
    "        b.innerHTML = '<i class=\"fa-solid fa-spinner fa-spin\"></i> <span>更新中…</span>';\n",
    "      } else {\n",
    "        b.innerHTML = '<i class=\"fa-solid fa-spinner fa-spin\"></i> <span>更新中…</span>';\n",
    "      }\n",
    "    });\n",
    "    showToast('🔄 正從證交所與櫃買中心即時更新 2000+ 檔台股…');\n",
    "  }\n",
    "\n",
    "  const updateEl = document.getElementById('updateTime');\n",
    "  if (updateEl) updateEl.textContent = forceRefresh ? '🔄 即時更新 2000+ 檔台股中…' : '資料載入中…';\n",
    "  const sideEl = document.getElementById('sidebarStatusText');\n",
    "  if (sideEl) sideEl.textContent = '載入中…';\n",
    "\n",
    "  const apiUrl = `/api/stocks?date=${dateStr}` + (forceRefresh ? '&force=true' : '');\n",
    "  console.log(`🌐 [台股更新流程 3/6] 向後端 API 發起 HTTP GET 請求: ${apiUrl}`);\n",
    "\n",
    "  try {\n",
    "    const startTime = Date.now();\n",
    "    const res = await fetch(apiUrl);\n",
    "    if (!res.ok) throw new Error(`HTTP 錯誤! 狀態碼: ${res.status}`);\n",
    "    const data = await res.json();\n",
    "    const fetchDuration = ((Date.now() - startTime) / 1000).toFixed(2);\n",
    "    \n",
    "    console.log(`✅ [台股更新流程 4/6] 收到 API 回應 (耗時 ${fetchDuration}秒)! 狀態: ${data.status}, 總筆數: ${data.total || data.stocks?.length}`);\n",
    "\n",
    "    if (data.stocks) {\n",
    "      stockList = mergeCustomStocks(data.stocks);\n",
    "      saveCache(dateStr, data.stocks);\n",
    "      console.log(`💾 [台股更新流程 5/6] 成功將 ${data.stocks.length} 檔股票數據寫入 LocalStorage 快取。`);\n",
    "\n",
    "      const d = dateStr.replace(/-/g, '/');\n",
    "      const headEl = document.getElementById('priceHeaderDate');\n",
    "      if (headEl) headEl.textContent = `${d} 收盤價`;\n",
    "      const totalCount = data.total || data.stocks.length;\n",
    "      if (updateEl) updateEl.textContent = `${d} ─ 已載入 ${totalCount} 檔全台股`;\n",
    "      if (sideEl) sideEl.textContent = `${d} (${totalCount}檔)`;\n",
    "\n",
    "      console.log(`🎨 [台股更新流程 6/6] 重新渲染產業 Tabs 與股票表格完畢！`);\n",
    "      renderTabs();\n",
    "      renderTable();\n",
    "\n",
    "      if (forceRefresh) {\n",
    "        showToast(`已連線更新 ${totalCount} 檔全台股最新收盤價！`);\n",
    "      }\n",
    "      console.log(`🎉 [台股更新流程] 成功完成全台股更新！`);\n",
    "    }\n",
    "  } catch (err) {\n",
    "    console.error(`❌ [台股更新流程錯誤] 請求失敗:`, err);\n",
    "    if (updateEl) updateEl.textContent = '載入失敗，請重試';\n",
    "    if (sideEl) sideEl.textContent = '載入失敗';\n",
    "  } finally {\n",
    "    if (btn) {\n",
    "      btn.innerHTML = '<i class=\"fa-solid fa-magnifying-glass\"></i><span>查詢</span>';\n",
    "      btn.disabled = false;\n",
    "    }\n",
    "    updateBtns.forEach(b => {\n",
    "      b.disabled = false;\n",
    "      if (b.id === 'sidebarBtnUpdateAll') {\n",
    "        b.innerHTML = '<i class=\"fa-solid fa-rotate\"></i> 更新全台股資料';\n",
    "      } else {\n",
    "        b.innerHTML = '<i class=\"fa-solid fa-rotate\"></i> <span>更新資料</span>';\n",
    "      }\n",
    "    });\n",
    "    console.log(`🏁 [台股更新流程] 按鈕狀態與介面復原完畢。`);\n",
    "  }\n",
    "}\n"
]

new_lines = lines[:start_idx] + new_fn + lines[end_idx+1:]
with open('app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully replaced fetchStockData in app.js!")

# 📈 台股與美股本益比 ‧ 大盤指數動態儀表板 (TW & US Stock PE Dashboard)

本專案為一個極速、現代化的 **台股與美股個股本益比分析** 以及 **全球主要大盤指數走勢追蹤** Dashboard 系統。前端採用 Vanilla HTML/CSS/JavaScript，後端基於 Python Flask Serverless Functions，部署於 **Vercel** 平台。

---

## 🌐 專案資訊與部署連結

- **線上正式環境 (Vercel Live)**: [https://tw-stock-pe-dashboard.vercel.app/](https://tw-stock-pe-dashboard.vercel.app/)
- **GitHub 程式碼儲存庫**: [https://github.com/yuhluen-spec/tw-stock-pe-dashboard](https://github.com/yuhluen-spec/tw-stock-pe-dashboard)
- **Vercel 專案名稱**: `yuhluen-spec/tw-stock-pe-dashboard`
- **主要工作目錄 (Recommended Path)**: `C:\workspace\Project\tw-stock-pe-dashboard-main`

---

## ✨ 核心功能說明 (Features)

### 1. 個股本益比與均線分析 (Stock PE Table)
- **追蹤標的**: 預設涵蓋台股指標股（如 2330 台積電、2454 聯發科）與美股龍頭股（如 NVDA, TSLA, AAPL 等）。
- **財務指標計算**:
  - **已知 P/E**: `收盤價 ÷ 2025全年稅後EPS`
  - **目前 EPS 倍數 (TTM)**: `收盤價 ÷ 近4季累計EPS`
  - **預估 P/E**: `收盤價 ÷ 年化預估EPS`（Q1估算: `Q1×4` / Q2累計估算: `Q2累計×2`）
- **均線走勢 (20MA & 60MA)**:
  - 比較所選交易日與前一交易日均線數值。
  - **月線 (20MA)** & **季線 (60MA)**：標示 **上彎 (紅/📈)** 或 **下彎 (綠/📉)**，並計算 **連續維持第 X 天**。

### 2. 主要大盤指數專區 (Market Indices Section)
- **涵蓋指數**:
  - 🇹🇼 台灣加權指數 (`^TWII`)
  - 🇺🇸 道瓊工業指數 (`^DJI`)
  - 🇺🇸 那斯達克指數 (`^IXIC`)
  - 🇺🇸 費城半導體指數 (`^SOX`)
  - 🇺🇸 標普500指數 (`^GSPC`)
- **多重均線與成交量走勢**:
  - **月線 (20MA)**、**季線 (60MA)**、**年線 (240MA)** 之上彎/下彎與連續天數。
  - **成交量 20日均量 (20VMA)**：顯示成交量均線走勢與天數。針對無成交量數據之指數（如費城半導體 `^SOX`），自動呈顯 **`— 無成交量`**。

### 3. 互動工具與數據匯出
- **日期切換與數據補抓**: 可自由切換指定歷史交易日、一鍵切換當日/前一日。
- **自訂個股管理**: 支援手動新增/編輯股票，資料自動備份於瀏覽器 `LocalStorage`。
- **CSV 報表匯出**: 一鍵導出完整表單資料（含 20MA/60MA 走勢天數與本益比估算值）。

---

## 📁 專案架構 (Project Architecture)

```text
C:\workspace\Project\tw-stock-pe-dashboard-main\
├── api/
│   └── index.py            # Python Flask Serverless 後端 (含 API 路由、Yahoo Finance 資料抓取與 20/60/240MA/20VMA 計算)
├── index.html              # 主介面結構 (Sidebar 選單、個股表格、大盤指數表格、計算說明)
├── app.js                 # 前端邏輯 (DOM 渲染、數據 Fetch、排序篩選、彈窗管理、CSV 匯出)
├── styles.css              # 現代深色主題 CSS (Glassmorphism 視覺風格、均線狀態 Badge 標籤)
├── vercel.json             # Vercel 路由重寫 (將 /api/stocks 與 /api/indices 轉向 /api/index.py)
└── README.md               # 專案說明文件 (給開發者與 AI 讀取)
```

---

## 🛠️ 開發與部署指南 (For New AI & Developers)

### 1. 後端 API 結構 (`api/index.py`)
- `/api/stocks`: 抓取個股報價、計算 20MA/60MA 走勢方向與連續天數。
- `/api/indices`: 併發抓取 5 大指數，計算 20MA、60MA、240MA 與 20VMA 走勢與天數。
- **快取機制**: `SERVER_CACHE` (內存 TTL 快取) 減少 Yahoo Finance API 請求頻率。

### 2. 注意事項 (Important Gotchas)
1. **工作目錄**:
   - 請固定於 `C:\workspace\Project\tw-stock-pe-dashboard-main` 進行程式碼修改與部署。
   - *(原 `D:` 磁碟區為 SD 卡且有防寫保護，請避免在 `D:` 上直接寫入)*。
2. **PowerShell 語法**:
   - 在 Windows PowerShell 中執行多個串接命令時，請使用 `;`（例如 `git add . ; git commit -m "..."`），請勿使用 `&`。
3. **檔案鎖定處理**:
   - 若後端 Python 測試進程在背景佔用檔案，可執行以下指令解除鎖定：
     ```powershell
     cmd /c "taskkill /F /IM python.exe"
     ```

### 3. Git 推送與 Vercel 部署流程
修改程式碼後，請按以下步驟推送到 GitHub 並發布至 Vercel：

```powershell
# 1. 提交程式碼至 GitHub main 分支
git add .
git commit -m "更新描述"
git push origin main

# 2. 發布至 Vercel 生產環境
npx vercel --prod --yes
```

---

## 💡 AI 助理接手提醒 (Notes for Next AI)
- 本專案所有主要 API 與前端元件皆已實裝完成並經過 Production 驗證。
- 若需要調整股票清單或新增指數，可直接於 `api/index.py` 中的 `STOCK_METADATA` 或 `INDEX_CONFIG` 陣列進行擴充。
- 請維持現有的顏色彩色標準（上彎/漲為紅色 `#f87171` 📈、下彎/跌為綠色 `#4ade80` 📉）。

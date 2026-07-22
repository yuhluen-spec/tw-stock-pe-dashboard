/* ─── Category helper ───────────────────────────────────────────── */
const CAT_META = {
  '晶圓代工':     { cls: 'row-wafer',   color: '#eab308', bg: 'rgba(234,179,8,0.18)',   label: '晶圓' },
  'IC設計':       { cls: 'row-ic',      color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: 'IC設計' },
  '半導體設備':   { cls: 'row-ic',      color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: '半導體' },
  '半導體封測材料':{ cls: 'row-ic',     color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: '封測' },
  '半導體材料':   { cls: 'row-ic',      color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: '材料' },
  '軸承/滑軌':    { cls: 'row-mech',    color: '#f97316', bg: 'rgba(249,115,22,0.18)',  label: '機械' },
  '塑膠':         { cls: 'row-plastic', color: '#f43f5e', bg: 'rgba(244,63,94,0.18)',   label: '塑膠' },
  '金融保險':     { cls: 'row-finance', color: '#38bdf8', bg: 'rgba(56,189,248,0.18)',  label: '金融' },
  '生技股':       { cls: 'row-biotech', color: '#a855f7', bg: 'rgba(168,85,247,0.18)',  label: '生技' },
};

function getCatMeta(cat) {
  return CAT_META[cat] || { cls: '', color: '#64748b', bg: 'rgba(100,116,139,0.18)', label: cat };
}

/* ─── Taiwan Stock Master Database for Smart Autocomplete ────────── */
const TW_STOCK_MASTER = [
  // ── 半導體 & 晶圓代工 & 封測/材料 ──
  { code: '2330', name: '台積電', category: '晶圓代工' },
  { code: '2303', name: '聯電', category: '晶圓代工' },
  { code: '5347', name: '世界先進', category: '晶圓代工' },
  { code: '3010', name: '華立', category: '半導體材料' },
  { code: '3711', name: '日月光投控', category: '半導體封測' },
  { code: '6515', name: '穎崴', category: '半導體封測材料' },
  { code: '6223', name: '旺矽', category: '半導體封測材料' },
  { code: '7769', name: '鴻勁', category: '半導體設備' },
  { code: '3583', name: '辛耘', category: '半導體設備' },
  { code: '3131', name: '弘塑', category: '半導體設備' },
  { code: '6187', name: '萬潤', category: '半導體設備' },
  { code: '2404', name: '漢唐', category: '無塵室工程' },
  { code: '5483', name: '中美晶', category: '矽晶圓' },
  { code: '6488', name: '環球晶', category: '矽晶圓' },

  // ── IC 設計 & IP ──
  { code: '2454', name: '聯發科', category: 'IC設計' },
  { code: '5274', name: '信驊', category: 'IC設計' },
  { code: '2379', name: '瑞昱', category: 'IC設計' },
  { code: '3034', name: '聯詠', category: 'IC設計' },
  { code: '3035', name: '智原', category: 'IP/IC設計' },
  { code: '3443', name: '創意', category: 'IP/IC設計' },
  { code: '3661', name: '世芯-KY', category: 'IP/ASIC' },
  { code: '6533', name: '晶心科', category: 'RISC-V IP' },
  { code: '6415', name: '矽力*-KY', category: '電源管理IC' },
  { code: '4966', name: '譜瑞-KY', category: '高速傳輸IC' },
  { code: '3529', name: '力旺', category: 'IP授權' },
  { code: '8054', name: '安國', category: 'ASIC/IC設計' },

  // ── AI伺服器 & 電腦 & 零組件 ──
  { code: '2317', name: '鴻海', category: '組裝代工' },
  { code: '2382', name: '廣達', category: 'AI伺服器' },
  { code: '3231', name: '緯創', category: 'AI伺服器' },
  { code: '6669', name: '緯穎', category: 'AI伺服器' },
  { code: '2356', name: '英業達', category: '電腦組裝' },
  { code: '2324', name: '仁寶', category: '電腦組裝' },
  { code: '2376', name: '技嘉', category: '主機板/顯卡' },
  { code: '2377', name: '微星', category: '主機板/顯卡' },
  { code: '2357', name: '華碩', category: '品牌電腦' },
  { code: '2395', name: '研華', category: '工業電腦' },
  { code: '2308', name: '台達電', category: '電源/綠能' },
  { code: '2059', name: '川湖', category: '軸承/滑軌' },
  { code: '3533', name: '嘉澤', category: '連接器/Socket' },
  { code: '3665', name: '貿聯-KY', category: '線束/連接器' },
  { code: '2383', name: '台光電', category: 'CCL銅箔基板' },
  { code: '6274', name: '台燿', category: 'CCL銅箔基板' },
  { code: '6213', name: '聯茂', category: 'CCL銅箔基板' },
  { code: '3037', name: '欣興', category: 'ABF載板' },
  { code: '8046', name: '南電', category: 'ABF載板' },
  { code: '3189', name: '景碩', category: 'ABF載板' },
  { code: '2368', name: '金像電', category: 'AI伺服器PCB' },
  { code: '3017', name: '奇鋐', category: '散熱' },
  { code: '3324', name: '雙鴻', category: '散熱' },
  { code: '3008', name: '大立光', category: '光學鏡頭' },
  { code: '3406', name: '玉晶光', category: '光學鏡頭' },

  // ── 被動元件 & 面板 & 被動 ──
  { code: '2327', name: '國巨', category: '被動元件' },
  { code: '2492', name: '華新科', category: '被動元件' },
  { code: '2409', name: '友達', category: '面板' },
  { code: '3481', name: '群創', category: '面板' },

  // ── 金融保險 ──
  { code: '2881', name: '富邦金', category: '金融保險' },
  { code: '2882', name: '國泰金', category: '金融保險' },
  { code: '2891', name: '中信金', category: '金融保險' },
  { code: '2886', name: '兆豐金', category: '金融保險' },
  { code: '2884', name: '玉山金', category: '金融保險' },
  { code: '2885', name: '元大金', category: '金融保險' },
  { code: '2892', name: '第一金', category: '金融保險' },
  { code: '2880', name: '華南金', category: '金融保險' },
  { code: '2883', name: '開發金', category: '金融保險' },
  { code: '2887', name: '台新金', category: '金融保險' },
  { code: '2890', name: '永豐金', category: '金融保險' },
  { code: '2801', name: '彰銀', category: '金融保險' },
  { code: '5880', name: '合庫金', category: '金融保險' },
  { code: '5876', name: '上海商銀', category: '金融保險' },

  // ── 塑膠 & 石化 & 傳統製造 ──
  { code: '1301', name: '台塑', category: '塑膠石化' },
  { code: '1303', name: '南亞', category: '塑膠石化' },
  { code: '1326', name: '台化', category: '塑膠石化' },
  { code: '6505', name: '台塑化', category: '石化煉油' },
  { code: '1305', name: '華夏', category: '塑膠石化' },
  { code: '2002', name: '中鋼', category: '鋼鐵' },
  { code: '1101', name: '台泥', category: '水泥/綠能' },
  { code: '1102', name: '亞泥', category: '水泥' },
  { code: '1216', name: '統一', category: '食品飲料' },
  { code: '2912', name: '統一超', category: '百貨零售' },
  { code: '9910', name: '豐泰', category: '製鞋/傳統' },
  { code: '9904', name: '寶成', category: '製鞋/傳統' },

  // ── 航運 & 交通 & 綠能 ──
  { code: '2603', name: '長榮', category: '航運' },
  { code: '2609', name: '陽明', category: '航運' },
  { code: '2615', name: '萬海', category: '航運' },
  { code: '2618', name: '長榮航', category: '航空' },
  { code: '2610', name: '華航', category: '航空' },
  { code: '2201', name: '裕隆', category: '汽車' },
  { code: '2207', name: '和泰車', category: '汽車' },

  // ── 生技醫療 ──
  { code: '6446', name: '藥華藥', category: '生技股' },
  { code: '6472', name: '保瑞', category: '生技股' },
  { code: '7799', name: '禾榮科', category: '生技股' },
  { code: '1795', name: '美時', category: '生技股' },
  { code: '4147', name: '中裕', category: '生技股' },

  // ── 電信 & ETF ──
  { code: '2412', name: '中華電', category: '電信' },
  { code: '3045', name: '台灣大', category: '電信' },
  { code: '4904', name: '遠傳', category: '電信' },
  { code: '0050', name: '元大台灣50', category: 'ETF' },
  { code: '0056', name: '元大高股息', category: 'ETF' },
  { code: '00878', name: '國泰永續高股息', category: 'ETF' },
  { code: '00919', name: '群益台灣精選高息', category: 'ETF' },
  { code: '00940', name: '元大台灣價值高息', category: 'ETF' }
];

/* ─── State ─────────────────────────────────────────────────────── */
let stockList = [];
let activeCategory = 'ALL';
let deferredPwaPrompt = null;

/* ─── Custom User Stocks Persistence ──────────────────────────────── */
const CUSTOM_STOCKS_KEY = 'tw_pe_custom_user_stocks';

function loadCustomStocks() {
  try {
    const raw = localStorage.getItem(CUSTOM_STOCKS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveCustomStocks(customList) {
  try {
    localStorage.setItem(CUSTOM_STOCKS_KEY, JSON.stringify(customList));
  } catch {}
}

function mergeCustomStocks(fetchedList) {
  const customStocks = loadCustomStocks();
  if (!customStocks || customStocks.length === 0) return fetchedList;

  const resultMap = new Map(fetchedList.map(s => [s.id, s]));
  customStocks.forEach(custom => {
    resultMap.set(custom.id, { ...resultMap.get(custom.id), ...custom });
  });

  return Array.from(resultMap.values());
}

/* ─── PWA Service Worker ─────────────────────────────────────────── */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(console.error);
  });
}
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPwaPrompt = e;
  document.getElementById('pwaInstallBanner')?.classList.add('show');
});

/* ─── Math helpers ───────────────────────────────────────────────── */
function calcKnownPE(price, eps2025) {
  if (!eps2025 || eps2025 <= 0) return null;
  return +(price / eps2025).toFixed(2);
}

function calcCurrentMultiple(price, epsTTM) {
  if (!epsTTM || epsTTM <= 0) return null;
  return +(price / epsTTM).toFixed(2);
}

function calcEstPE(price, q1, q2) {
  let estEps = null;
  if (q2 != null) estEps = q2 * 2;
  else if (q1 != null) estEps = q1 * 4;
  if (!estEps || estEps <= 0) return null;
  return +(price / estEps).toFixed(2);
}


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

/* ─── Format helpers ─────────────────────────────────────────────── */
function fmtNum(v, decimals = 2) {
  if (v == null || isNaN(v)) return '—';
  return Number(v).toFixed(decimals);
}

function epsHtml(v) {
  if (v == null || v === '') return '<span style="color:var(--text-dim)">—</span>';
  const n = +v;
  if (isNaN(n)) return '<span style="color:var(--text-dim)">—</span>';
  const cls = n < 0 ? ' val-negative' : '';
  return `<span class="val-num${cls}">${n.toFixed(2)}</span>`;
}

function pePeHtml(pe, variant = '') {
  if (pe == null) return '<span class="pe-tag na">NA</span>';
  let cls = 'mid';
  if (pe < 15) cls = 'low';
  else if (pe > 30) cls = 'high';
  if (variant) cls = variant;
  return `<span class="pe-tag ${cls}">${pe.toFixed(1)}x</span>`;
}

/* ─── Render industry tabs ───────────────────────────────────────── */
function renderTabs() {
  const cats = ['全部', ...new Set(stockList.map(s => s.category))];
  const container = document.getElementById('industryTabs');
  if (!container) return;

  container.innerHTML = cats.map(cat => {
    const val = cat === '全部' ? 'ALL' : cat;
    const active = activeCategory === val ? 'active' : '';
    return `<button class="tab-pill ${active}" data-cat="${val}">${cat}</button>`;
  }).join('');

  container.querySelectorAll('.tab-pill').forEach(b => {
    b.addEventListener('click', () => {
      activeCategory = b.dataset.cat;
      renderTabs();
      renderTable();
    });
  });
}

/* ─── Get filtered + sorted list ────────────────────────────────── */
function getFiltered() {
  const qInput = document.getElementById('searchInput');
  const q = qInput ? qInput.value.trim().toLowerCase() : '';
  const sortSelect = document.getElementById('sortBySelect');
  const sort = sortSelect ? sortSelect.value : 'default';

  let list = stockList.filter(s => {
    const catOk = activeCategory === 'ALL' || s.category === activeCategory;
    const qOk = !q || s.code.toLowerCase().includes(q) || s.name.toLowerCase().includes(q) || s.category.toLowerCase().includes(q);
    return catOk && qOk;
  });

  list.sort((a, b) => {
    const estA = calcEstPE(a.price, a.eps2026q1, a.eps2026q2);
    const estB = calcEstPE(b.price, b.eps2026q1, b.eps2026q2);
    const knA  = calcKnownPE(a.price, a.eps2025);
    const knB  = calcKnownPE(b.price, b.eps2025);
    const cmA  = calcCurrentMultiple(a.price, a.epsTTM);
    const cmB  = calcCurrentMultiple(b.price, b.epsTTM);
    const nn   = (v) => v == null ? Infinity : v;

    switch (sort) {
      case 'estPeAsc':          return nn(estA) - nn(estB);
      case 'estPeDesc':         return nn(estB) - nn(estA);
      case 'currentMultipleAsc':return nn(cmA)  - nn(cmB);
      case 'knownPeAsc':        return nn(knA)  - nn(knB);
      case 'priceDesc':         return b.price - a.price;
      case 'codeAsc':           return a.code.localeCompare(b.code);
      default:                  return 0;
    }
  });

  return list;
}

/* ─── Render table ───────────────────────────────────────────────── */
function renderTable() {
  const list = getFiltered();
  const tbody = document.getElementById('stockTableBody');
  const empty = document.getElementById('tableEmpty');
  if (!tbody || !empty) return;

  if (list.length === 0) {
    tbody.innerHTML = '';
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  tbody.innerHTML = list.map((s, idx) => {
    const meta    = getCatMeta(s.category);
    const knownPE = calcKnownPE(s.price, s.eps2025);
    const curMult = calcCurrentMultiple(s.price, s.epsTTM);
    const estPE   = calcEstPE(s.price, s.eps2026q1, s.eps2026q2);
    const catBadge = `<span class="cat-badge" style="background:${meta.bg};color:${meta.color}">${meta.label}</span>`;

    return `
      <tr class="${meta.cls}">
        <td class="sticky-col col-idx"><span class="row-num">${idx + 1}</span></td>
        <td class="sticky-col col-stock">
          <div class="stock-cell">
            <span class="stock-name">${s.name}</span>
            <span class="stock-code">${s.code}</span>
          </div>
        </td>
        <td>${catBadge}</td>
        <td>${epsHtml(s.eps2025)}</td>
        <td>${epsHtml(s.eps2026q1)}</td>
        <td>${epsHtml(s.eps2026q2)}</td>
        <td class="highlighted-td"><span class="val-num val-ttm">${fmtNum(s.epsTTM)}</span></td>
        <td><span class="val-num">${fmtNum(s.price)}</span></td>
        <td>${pePeHtml(knownPE)}</td>
        <td class="highlighted-td">${pePeHtml(curMult, 'cyan')}</td>
        <td>${pePeHtml(estPE)}</td>
        <td>
          <div class="act-wrap">
            <button class="act-btn" onclick="editStock('${s.id}')" title="編輯"><i class="fa-solid fa-pen"></i></button>
            <button class="act-btn del" onclick="deleteStock('${s.id}')" title="刪除"><i class="fa-solid fa-trash"></i></button>
          </div>
        </td>
      </tr>`;
  }).join('');

  updateKPIs(list);
}

/* ─── KPI update ─────────────────────────────────────────────────── */
function updateKPIs(list) {
  const countEl = document.getElementById('statTotalCount');
  if (countEl) countEl.textContent = list.length;

  const knPes = list.map(s => calcKnownPE(s.price, s.eps2025)).filter(v => v != null);
  const estPes = list.map(s => calcEstPE(s.price, s.eps2026q1, s.eps2026q2)).filter(v => v != null);

  const avgKnEl = document.getElementById('statAvgKnownPe');
  if (avgKnEl) {
    avgKnEl.textContent = knPes.length ? (knPes.reduce((a,b)=>a+b,0)/knPes.length).toFixed(1)+'x' : '--';
  }

  const avgEstEl = document.getElementById('statAvgEstPe');
  const lowestEl = document.getElementById('statLowestEstPe');

  if (estPes.length) {
    const avg = (estPes.reduce((a,b)=>a+b,0)/estPes.length).toFixed(1);
    if (avgEstEl) avgEstEl.textContent = avg + 'x';

    let minPe = Infinity, minStock = null;
    list.forEach(s => {
      const e = calcEstPE(s.price, s.eps2026q1, s.eps2026q2);
      if (e != null && e < minPe) { minPe = e; minStock = s; }
    });
    if (lowestEl) {
      lowestEl.textContent = minStock ? `${minStock.name} ${minPe.toFixed(1)}x` : '--';
    }
  } else {
    if (avgEstEl) avgEstEl.textContent = '--';
    if (lowestEl) lowestEl.textContent = '--';
  }
}

/* ─── LocalStorage Cache helpers ─────────────────────────────────── */
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const CACHE_PREFIX = 'tw_pe_';

function cacheKey(dateStr) { return CACHE_PREFIX + dateStr; }

function loadCache(dateStr) {
  try {
    const raw = localStorage.getItem(cacheKey(dateStr));
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (Date.now() - obj.ts > CACHE_TTL_MS) {
      localStorage.removeItem(cacheKey(dateStr));
      return null;
    }
    return obj.data;
  } catch { return null; }
}

function saveCache(dateStr, data) {
  try {
    localStorage.setItem(cacheKey(dateStr), JSON.stringify({ ts: Date.now(), data }));
    const keys = Object.keys(localStorage).filter(k => k.startsWith(CACHE_PREFIX));
    if (keys.length > 7) {
      keys.sort().slice(0, keys.length - 7).forEach(k => localStorage.removeItem(k));
    }
  } catch {}
}

/* ─── Get latest trading date (Mon–Fri, Taiwan timezone) ─────────── */
function getLatestTradingDate() {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Taipei' }));
  if (d.getHours() < 14) d.setDate(d.getDate() - 1);
  while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
  const yyyy = d.getFullYear();
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const dd   = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

/* ─── Fetch data (with LocalStorage cache) ───────────────────────── */
async function fetchStockData(dateStr, forceRefresh = false) {
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
}

/* ─── Modal Autocomplete ─────────────────────────────────────────── */
function setupModalStockAutocomplete() {
  const searchInput = document.getElementById('modalStockSearch');
  const box = document.getElementById('suggestionsBox');
  const list = document.getElementById('suggestionsList');
  if (!searchInput || !box || !list) return;

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) {
      box.style.display = 'none';
      return;
    }

    const matches = TW_STOCK_MASTER.filter(s => 
      s.code.toLowerCase().includes(q) || 
      s.name.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q)
    ).slice(0, 7);

    if (matches.length === 0) {
      box.style.display = 'none';
      return;
    }

    list.innerHTML = matches.map(s => `
      <div class="suggestion-item" data-code="${s.code}" data-name="${s.name}" data-cat="${s.category}">
        <div class="sug-stock">
          <span class="sug-code">${s.code}</span>
          <span class="sug-name">${s.name}</span>
        </div>
        <span class="sug-cat">${s.category}</span>
      </div>
    `).join('');

    box.style.display = 'block';

    list.querySelectorAll('.suggestion-item').forEach(item => {
      item.addEventListener('click', () => {
        const code = item.getAttribute('data-code');
        const name = item.getAttribute('data-name');
        const category = item.getAttribute('data-cat');
        selectStockSuggestion(code, name, category);
      });
    });
  });
}

function selectStockSuggestion(code, name, category) {
  const codeEl = document.getElementById('inputCode');
  const nameEl = document.getElementById('inputName');
  const catEl = document.getElementById('inputCategory');
  const searchEl = document.getElementById('modalStockSearch');
  const box = document.getElementById('suggestionsBox');

  if (codeEl) codeEl.value = code;
  if (nameEl) nameEl.value = name;
  if (catEl) catEl.value = category;
  if (searchEl) searchEl.value = `${code} ${name}`;
  if (box) box.style.display = 'none';

  const existing = stockList.find(s => s.code === code);
  if (existing) {
    const eps25 = document.getElementById('inputEps2025');
    if (eps25) eps25.value = existing.eps2025 ?? '';
    const eps26q1 = document.getElementById('inputEps2026Q1');
    if (eps26q1) eps26q1.value = existing.eps2026q1 ?? '';
    const eps26q2 = document.getElementById('inputEps2026Q2');
    if (eps26q2) eps26q2.value = existing.eps2026q2 ?? '';
    const prEl = document.getElementById('inputPrice');
    if (prEl) prEl.value = existing.price ?? '';
  } else {
    fetchStockPriceAndEps(code);
  }
}

async function fetchStockPriceAndEps(code) {
  const spinner = document.getElementById('modalSearchSpinner');
  if (spinner) spinner.style.display = 'inline-block';
  try {
    const datePicker = document.getElementById('datePicker');
    const dateStr = datePicker ? datePicker.value : getLatestTradingDate();
    const res = await fetch(`/api/stocks?date=${dateStr}&code=${code}`);
    if (res.ok) {
      const data = await res.json();
      const match = data.stocks?.find(s => s.code === code);
      if (match) {
        const eps25 = document.getElementById('inputEps2025');
        if (eps25) eps25.value = match.eps2025 ?? '';
        const eps26q1 = document.getElementById('inputEps2026Q1');
        if (eps26q1) eps26q1.value = match.eps2026q1 ?? '';
        const eps26q2 = document.getElementById('inputEps2026Q2');
        if (eps26q2) eps26q2.value = match.eps2026q2 ?? '';
        const prEl = document.getElementById('inputPrice');
        if (prEl) prEl.value = match.price ?? '';
      }
    }
  } catch (err) {
    console.error('Fetch stock detail failed:', err);
  } finally {
    if (spinner) spinner.style.display = 'none';
  }
}

/* ─── Modal ──────────────────────────────────────────────────────── */
function openModal(stock = null) {
  const form = document.getElementById('stockForm');
  if (form) form.reset();

  const searchIn = document.getElementById('modalStockSearch');
  if (searchIn) searchIn.value = '';
  const sugBox = document.getElementById('suggestionsBox');
  if (sugBox) sugBox.style.display = 'none';

  const titleEl = document.getElementById('modalTitle');
  const editId = document.getElementById('editStockId');

  if (stock) {
    if (titleEl) titleEl.textContent = '編輯股票資料';
    if (editId) editId.value = stock.id;
    const catEl = document.getElementById('inputCategory');
    if (catEl) catEl.value = stock.category || '';
    const codeEl = document.getElementById('inputCode');
    if (codeEl) codeEl.value = stock.code || '';
    const nameEl = document.getElementById('inputName');
    if (nameEl) nameEl.value = stock.name || '';
    const eps25 = document.getElementById('inputEps2025');
    if (eps25) eps25.value = stock.eps2025 ?? '';
    const eps26q1 = document.getElementById('inputEps2026Q1');
    if (eps26q1) eps26q1.value = stock.eps2026q1 ?? '';
    const eps26q2 = document.getElementById('inputEps2026Q2');
    if (eps26q2) eps26q2.value = stock.eps2026q2 ?? '';
    const prEl = document.getElementById('inputPrice');
    if (prEl) prEl.value = stock.price ?? '';
  } else {
    if (titleEl) titleEl.textContent = '搜尋並新增股票';
    if (editId) editId.value = '';
  }
  document.getElementById('stockModal')?.classList.add('show');
}

function closeModal() {
  document.getElementById('stockModal')?.classList.remove('show');
}

window.editStock = (id) => { const s = stockList.find(x => x.id === id); if (s) openModal(s); };
window.deleteStock = (id) => {
  const s = stockList.find(x => x.id === id);
  if (s && confirm(`確定要刪除 ${s.code} ${s.name}？`)) {
    stockList = stockList.filter(x => x.id !== id);
    saveCustomStocks(stockList);
    renderTabs();
    renderTable();
  }
};

/* ─── Export CSV ─────────────────────────────────────────────────── */
function exportCsv() {
  const datePicker = document.getElementById('datePicker');
  const dateStr = datePicker ? datePicker.value : getLatestTradingDate();
  let csv = '\uFEFF產業,代號,名稱,2025全年EPS,2026Q1,2026Q2累計,TTM EPS,收盤價,已知P/E,目前EPS倍數,預估P/E\n';
  stockList.forEach(s => {
    const kn = calcKnownPE(s.price, s.eps2025) ?? 'NA';
    const cm = calcCurrentMultiple(s.price, s.epsTTM) ?? 'NA';
    const es = calcEstPE(s.price, s.eps2026q1, s.eps2026q2) ?? 'NA';
    csv += `"${s.category}","${s.code}","${s.name}",${s.eps2025??''},${s.eps2026q1??''},${s.eps2026q2??''},${s.epsTTM??''},${s.price},${kn},${cm},${es}\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob),
    download: `台股本益比_${dateStr}.csv`
  });
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
}

/* ─── Date shortcuts ─────────────────────────────────────────────── */
function setChip(activeId) {
  ['btnDateToday','btnDatePrevDay'].forEach(id => {
    document.getElementById(id)?.classList.toggle('active', id === activeId);
  });
}

/* ─── Sidebar drawer toggle ──────────────────────────────────────── */
function openSidebar() {
  document.getElementById('sidebar')?.classList.add('open');
  document.getElementById('sidebarOverlay')?.classList.add('show');
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('show');
}

/* ─── Table scroll shadow ────────────────────────────────────────── */
function initScrollShadow() {
  const container = document.querySelector('.table-container');
  if (!container) return;
  container.addEventListener('scroll', () => {
    container.classList.toggle('scrolled', container.scrollLeft > 4);
  }, { passive: true });
}

/* ─── DOMContentLoaded ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const datePicker = document.getElementById('datePicker');

  const latestDate = getLatestTradingDate();
  if (datePicker) datePicker.value = latestDate;
  fetchStockData(latestDate);
  initScrollShadow();
  setupModalStockAutocomplete();

  document.getElementById('btnLoadDateData')?.addEventListener('click', (e) => {
    const val = datePicker ? datePicker.value : latestDate;
    fetchStockData(val, e.shiftKey);
  });

  document.getElementById('btnDateToday')?.addEventListener('click', () => {
    const s = getLatestTradingDate();
    if (datePicker) datePicker.value = s;
    setChip('btnDateToday');
    fetchStockData(s);
  });

  document.getElementById('btnDatePrevDay')?.addEventListener('click', () => {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
    const s = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    if (datePicker) datePicker.value = s;
    setChip('btnDatePrevDay');
    fetchStockData(s);
  });

  document.getElementById('searchInput')?.addEventListener('input', renderTable);
  document.getElementById('sortBySelect')?.addEventListener('change', renderTable);

  const openAdd = () => openModal();
  document.getElementById('btnAddStockTop')?.addEventListener('click', openAdd);
  document.getElementById('btnExportTop')?.addEventListener('click', exportCsv);
  document.getElementById('sidebarBtnAdd')?.addEventListener('click', openAdd);
  document.getElementById('sidebarBtnExport')?.addEventListener('click', exportCsv);

  document.getElementById('btnCloseModal')?.addEventListener('click', closeModal);
  document.getElementById('btnCancelModal')?.addEventListener('click', closeModal);
  document.getElementById('stockModal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });

  document.getElementById('stockForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const id = document.getElementById('editStockId')?.value;
    const catEl = document.getElementById('inputCategory');
    const codeEl = document.getElementById('inputCode');
    const nameEl = document.getElementById('inputName');
    const eps25El = document.getElementById('inputEps2025');
    const eps26q1El = document.getElementById('inputEps2026Q1');
    const eps26q2El = document.getElementById('inputEps2026Q2');
    const prEl = document.getElementById('inputPrice');

    const parsed = {
      category: catEl ? catEl.value.trim() : '',
      code:     codeEl ? codeEl.value.trim() : '',
      name:     nameEl ? nameEl.value.trim() : '',
      eps2025:  (eps25El && eps25El.value !== '') ? +eps25El.value : null,
      eps2026q1:(eps26q1El && eps26q1El.value !== '') ? +eps26q1El.value : null,
      eps2026q2:(eps26q2El && eps26q2El.value !== '') ? +eps26q2El.value : null,
      price:    prEl ? +prEl.value : 0,
      isCustom: true
    };

    if (id) {
      const s = stockList.find(x => x.id === id);
      if (s) Object.assign(s, parsed);
    } else {
      stockList.push({ id: parsed.code || String(Date.now()), ...parsed });
    }

    saveCustomStocks(stockList);
    closeModal();
    renderTabs();
    renderTable();
  });

  document.getElementById('hamburgerBtn')?.addEventListener('click', openSidebar);
  document.getElementById('sidebarOverlay')?.addEventListener('click', closeSidebar);

  document.getElementById('navHome')?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('navDate')?.addEventListener('click', () => {
    if (datePicker) {
      datePicker.scrollIntoView({ behavior: 'smooth', block: 'center' });
      datePicker.focus();
    }
  });
  document.getElementById('navAdd')?.addEventListener('click', openAdd);
  document.getElementById('navExportMobile')?.addEventListener('click', exportCsv);
  document.getElementById('navInfo')?.addEventListener('click', () => {
    document.getElementById('formula')?.scrollIntoView({ behavior: 'smooth' });
  });

  document.getElementById('btnInstallPwa')?.addEventListener('click', async () => {
    if (deferredPwaPrompt) {
      deferredPwaPrompt.prompt();
      await deferredPwaPrompt.userChoice;
      deferredPwaPrompt = null;
      document.getElementById('pwaInstallBanner')?.classList.remove('show');
    }
  });
  document.getElementById('btnDismissPwa')?.addEventListener('click', () => {
    document.getElementById('pwaInstallBanner')?.classList.remove('show');
  });
});

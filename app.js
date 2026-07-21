/* ─── Category helper ───────────────────────────────────────────── */
const CAT_META = {
  '晶圓代工':     { cls: 'row-wafer',   color: '#eab308', bg: 'rgba(234,179,8,0.18)',   label: '晶圓' },
  'IC設計':       { cls: 'row-ic',      color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: 'IC設計' },
  '半導體設備':   { cls: 'row-ic',      color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: '半導體' },
  '半導體封測材料':{ cls: 'row-ic',     color: '#22c55e', bg: 'rgba(34,197,94,0.18)',   label: '封測' },
  '軸承/滑軌':    { cls: 'row-mech',    color: '#f97316', bg: 'rgba(249,115,22,0.18)',  label: '機械' },
  '塑膠':         { cls: 'row-plastic', color: '#f43f5e', bg: 'rgba(244,63,94,0.18)',   label: '塑膠' },
  '金融保險':     { cls: 'row-finance', color: '#38bdf8', bg: 'rgba(56,189,248,0.18)',  label: '金融' },
  '生技股':       { cls: 'row-biotech', color: '#a855f7', bg: 'rgba(168,85,247,0.18)',  label: '生技' },
};

function getCatMeta(cat) {
  return CAT_META[cat] || { cls: '', color: '#64748b', bg: 'rgba(100,116,139,0.18)', label: cat };
}

/* ─── State ─────────────────────────────────────────────────────── */

const API_BASE = (window.location.hostname.includes('web.app') || window.location.hostname.includes('firebaseapp.com'))
  ? 'https://tw-stock-pe-dashboard.vercel.app'
  : '';

let stockList = [];
let activeCategory = 'ALL';
let deferredPwaPrompt = null;

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

/* ─── Render industry tabs ───────────────────────────────────────── */
function renderTabs() {
  const cats = ['全部', ...new Set(stockList.map(s => s.category))];
  document.getElementById('industryTabs').innerHTML = cats.map(cat => {
    const val = cat === '全部' ? 'ALL' : cat;
    const active = activeCategory === val ? 'active' : '';
    return `<button class="tab-pill ${active}" data-cat="${val}">${cat}</button>`;
  }).join('');
  document.querySelectorAll('.tab-pill').forEach(b => {
    b.addEventListener('click', () => {
      activeCategory = b.dataset.cat;
      renderTabs();
      renderTable();
    });
  });
}

/* ─── Get filtered + sorted list ────────────────────────────────── */
function getFiltered() {
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const sort = document.getElementById('sortBySelect').value;

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
  document.getElementById('statTotalCount').textContent = list.length;

  const knPes = list.map(s => calcKnownPE(s.price, s.eps2025)).filter(v => v != null);
  const estPes = list.map(s => calcEstPE(s.price, s.eps2026q1, s.eps2026q2)).filter(v => v != null);

  document.getElementById('statAvgKnownPe').textContent =
    knPes.length ? (knPes.reduce((a,b)=>a+b,0)/knPes.length).toFixed(1)+'x' : '--';

  if (estPes.length) {
    const avg = (estPes.reduce((a,b)=>a+b,0)/estPes.length).toFixed(1);
    document.getElementById('statAvgEstPe').textContent = avg + 'x';

    // Find lowest
    let minPe = Infinity, minStock = null;
    list.forEach(s => {
      const e = calcEstPE(s.price, s.eps2026q1, s.eps2026q2);
      if (e != null && e < minPe) { minPe = e; minStock = s; }
    });
    document.getElementById('statLowestEstPe').textContent =
      minStock ? `${minStock.name} ${minPe.toFixed(1)}x` : '--';
  } else {
    document.getElementById('statAvgEstPe').textContent = '--';
    document.getElementById('statLowestEstPe').textContent = '--';
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
  document.getElementById('datePicker').value = dateStr;

  // Try cache first (Shift+Click query btn to force refresh)
  if (!forceRefresh) {
    const cached = loadCache(dateStr);
    if (cached) {
      stockList = mergeCustomStocks(cached);
      const d = dateStr.replace(/-/g, '/');
      document.getElementById('priceHeaderDate').textContent = `${d} 收盤價`;
      document.getElementById('updateTime').textContent = `${d} ─ 快取資料`;
      document.getElementById('sidebarStatusText').textContent = `${d} (快取)`;
      renderTabs();
      renderTable();
      return;
    }
  }

  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
  btn.disabled = true;
  document.getElementById('updateTime').textContent = '資料載入中…';
  document.getElementById('sidebarStatusText').textContent = '載入中…';

  try {
    const res = await fetch(`${API_BASE}/api/stocks?date=${dateStr}`);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    if (data.stocks) {
      stockList = mergeCustomStocks(data.stocks);
      saveCache(dateStr, stockList); // save to localStorage
      const d = dateStr.replace(/-/g, '/');
      document.getElementById('priceHeaderDate').textContent = `${d} 收盤價`;
      document.getElementById('updateTime').textContent = `${d} 已更新`;
      document.getElementById('sidebarStatusText').textContent = `${d} 已載入`;
      renderTabs();
      renderTable();
    }
  } catch (err) {
    document.getElementById('updateTime').textContent = '載入失敗，請重試';
    document.getElementById('sidebarStatusText').textContent = '載入失敗';
    console.error(err);
  } finally {
    btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i><span>查詢</span>';
    btn.disabled = false;
  }
}

/* ─── Modal ──────────────────────────────────────────────────────── */
function openModal(stock = null) {
  document.getElementById('stockForm').reset();
  if (stock) {
    document.getElementById('modalTitle').textContent = '編輯股票資料';
    document.getElementById('editStockId').value = stock.id;
    document.getElementById('inputCategory').value = stock.category || '';
    document.getElementById('inputCode').value = stock.code || '';
    document.getElementById('inputName').value = stock.name || '';
    document.getElementById('inputEps2025').value = stock.eps2025 ?? '';
    document.getElementById('inputEps2026Q1').value = stock.eps2026q1 ?? '';
    document.getElementById('inputEps2026Q2').value = stock.eps2026q2 ?? '';
    document.getElementById('inputPrice').value = stock.price ?? '';
  } else {
    document.getElementById('modalTitle').textContent = '新增股票資料';
    document.getElementById('editStockId').value = '';
  }
  document.getElementById('stockModal').classList.add('show');
}
function closeModal() { document.getElementById('stockModal').classList.remove('show'); }

window.editStock = (id) => { const s = stockList.find(x => x.id === id); if (s) openModal(s); };
window.deleteStock = (id) => {
  const s = stockList.find(x => x.id === id);
  if (s && confirm(`確定要刪除 ${s.code} ${s.name}？`)) {
    stockList = stockList.filter(x => x.id !== id);
    renderTabs();
    renderTable();
  }
};

/* ─── Export CSV ─────────────────────────────────────────────────── */
function exportCsv() {
  const dateStr = document.getElementById('datePicker').value;
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
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebarOverlay').classList.add('show');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('show');
}

/* ─── Table scroll shadow ────────────────────────────────────────── */
function initScrollShadow() {
  const container = document.querySelector('.table-container');
  if (!container) return;
  container.addEventListener('scroll', () => {
    container.classList.toggle('scrolled', container.scrollLeft > 4);
  }, { passive: true });
}

/* ─── DOMContentLoaded ───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const datePicker = document.getElementById('datePicker');

  // Auto-load latest trading date
  const latestDate = getLatestTradingDate();
  fetchStockData(latestDate);
  initScrollShadow();

  // Shift+Click = force refresh (bypass cache)
  document.getElementById('btnLoadDateData')?.addEventListener('click', (e) => {
    fetchStockData(document.getElementById('datePicker').value, e.shiftKey);
  });

  document.getElementById('btnDateToday')?.addEventListener('click', () => {
    const d = new Date();
    const s = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    datePicker.value = s; setChip('btnDateToday'); fetchStockData(s);
  });
  document.getElementById('btnDatePrevDay')?.addEventListener('click', () => {
    const d = new Date(); d.setDate(d.getDate()-1);
    const s = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    datePicker.value = s; setChip('btnDatePrevDay'); fetchStockData(s);
  });

  /* Search & sort */
  document.getElementById('searchInput')?.addEventListener('input', renderTable);
  document.getElementById('sortBySelect')?.addEventListener('change', renderTable);

  /* Add / Edit buttons */
  const openAdd = () => openModal();
  document.getElementById('btnAddStockTop')?.addEventListener('click', openAdd);
  document.getElementById('btnExportTop')?.addEventListener('click', exportCsv);
  document.getElementById('sidebarBtnAdd')?.addEventListener('click', openAdd);
  document.getElementById('sidebarBtnExport')?.addEventListener('click', exportCsv);

  /* Modal */
  document.getElementById('btnCloseModal')?.addEventListener('click', closeModal);
  document.getElementById('btnCancelModal')?.addEventListener('click', closeModal);
  document.getElementById('stockModal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });

  document.getElementById('stockForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const id = document.getElementById('editStockId').value;
    const parsed = {
      category: document.getElementById('inputCategory').value.trim(),
      code:     document.getElementById('inputCode').value.trim(),
      name:     document.getElementById('inputName').value.trim(),
      eps2025:  document.getElementById('inputEps2025').value !== '' ? +document.getElementById('inputEps2025').value : null,
      eps2026q1:document.getElementById('inputEps2026Q1').value !== '' ? +document.getElementById('inputEps2026Q1').value : null,
      eps2026q2:document.getElementById('inputEps2026Q2').value !== '' ? +document.getElementById('inputEps2026Q2').value : null,
      price:    +document.getElementById('inputPrice').value,
    };
    if (id) {
      const s = stockList.find(x => x.id === id);
      if (s) Object.assign(s, parsed);
    } else {
      stockList.push({ id: parsed.code || String(Date.now()), ...parsed });
    }
    saveCustomStocks(stockList.filter(s => !SNAPSHOT_PRICES_20260717[s.code] || s.isCustom)); closeModal(); renderTabs(); renderTable();
  });

  /* Hamburger & sidebar overlay */
  document.getElementById('hamburgerBtn')?.addEventListener('click', openSidebar);
  document.getElementById('sidebarOverlay')?.addEventListener('click', closeSidebar);

  /* Mobile bottom nav */
  document.getElementById('navHome')?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('navDate')?.addEventListener('click', () => {
    datePicker.scrollIntoView({ behavior: 'smooth', block: 'center' });
    datePicker.focus();
  });
  document.getElementById('navAdd')?.addEventListener('click', openAdd);
  document.getElementById('navExportMobile')?.addEventListener('click', exportCsv);
  document.getElementById('navInfo')?.addEventListener('click', () => {
    document.getElementById('formula').scrollIntoView({ behavior: 'smooth' });
  });

  /* PWA */
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

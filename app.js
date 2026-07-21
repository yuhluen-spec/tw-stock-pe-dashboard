// Dynamic Stock Dataset loaded from Live Financial EPS Derivation Engine
let stockList = [];
let activeCategory = 'ALL';
let currentViewMode = 'auto'; // 'auto', 'table', 'card'
let deferredPwaPrompt = null;

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then((reg) => {
      console.log('PWA ServiceWorker registered with scope:', reg.scope);
    }).catch((err) => {
      console.error('ServiceWorker registration failed:', err);
    });
  });
}

// PWA Install Prompt Handler
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPwaPrompt = e;
  const banner = document.getElementById('pwaInstallBanner');
  if (banner) banner.classList.add('show');
});

// Calculation helper functions
function calculateKnownPE(price, eps2025) {
  if (eps2025 === null || eps2025 === undefined || eps2025 <= 0) return null;
  return Number((price / eps2025).toFixed(2));
}

function calculateCurrentMultiple(price, epsTTM, eps2026q1, eps2026q2) {
  if (epsTTM && epsTTM > 0) {
    return Number((price / epsTTM).toFixed(2));
  }
  const curEps = eps2026q2 || eps2026q1;
  if (curEps && curEps > 0) {
    return Number((price / curEps).toFixed(2));
  }
  return null;
}

function calculateEstPE(price, q1, q2, q3) {
  let estEps = null;
  if (q3 !== null && q3 !== undefined) {
    estEps = (q3 / 3) * 4;
  } else if (q2 !== null && q2 !== undefined) {
    estEps = q2 * 2;
  } else if (q1 !== null && q1 !== undefined) {
    estEps = q1 * 4;
  }

  if (estEps === null || estEps <= 0) return null;
  return Number((price / estEps).toFixed(2));
}

function formatNum(val) {
  if (val === null || val === undefined || isNaN(val)) return '-';
  return val.toLocaleString('zh-TW', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatEps(val) {
  if (val === null || val === undefined || val === '') return '-';
  const num = Number(val);
  if (isNaN(num)) return '-';
  const str = num.toFixed(2);
  if (num < 0) {
    return `<span class="negative-eps">${str}</span>`;
  }
  return str;
}

function getPeBadgeHtml(peVal, customClass = '') {
  if (peVal === null || peVal === undefined || isNaN(peVal)) {
    return `<span class="pe-badge na">NA</span>`;
  }
  let className = customClass || 'mid';
  if (!customClass) {
    if (peVal < 15) className = 'low';
    else if (peVal > 30) className = 'high';
  }

  return `<span class="pe-badge ${className}">${peVal.toFixed(2)} 倍</span>`;
}

// Render Category Tabs
function renderIndustryTabs() {
  const categories = ['全部', ...new Set(stockList.map(s => s.category))];
  const container = document.getElementById('industryTabs');
  container.innerHTML = categories.map(cat => {
    const isAll = cat === '全部';
    const isActive = (isAll && activeCategory === 'ALL') || activeCategory === cat;
    const catCode = isAll ? 'ALL' : cat;
    return `<button class="tab-btn ${isActive ? 'active' : ''}" data-cat="${catCode}">${cat}</button>`;
  }).join('');

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      activeCategory = e.target.getAttribute('data-cat');
      renderIndustryTabs();
      renderAllViews();
    });
  });
}

function getFilteredAndSortedStocks() {
  const searchKey = document.getElementById('searchInput').value.trim().toLowerCase();
  const sortBy = document.getElementById('sortBySelect').value;

  let filtered = stockList.filter(item => {
    const matchCat = (activeCategory === 'ALL') || (item.category === activeCategory);
    const matchSearch = !searchKey || 
                        item.code.toLowerCase().includes(searchKey) || 
                        item.name.toLowerCase().includes(searchKey) ||
                        item.category.toLowerCase().includes(searchKey);
    return matchCat && matchSearch;
  });

  filtered.sort((a, b) => {
    const knownPeA = calculateKnownPE(a.price, a.eps2025);
    const knownPeB = calculateKnownPE(b.price, b.eps2025);
    const estPeA = calculateEstPE(a.price, a.eps2026q1, a.eps2026q2, a.eps2026q3);
    const estPeB = calculateEstPE(b.price, b.eps2026q1, b.eps2026q2, b.eps2026q3);
    const multA = calculateCurrentMultiple(a.price, a.epsTTM, a.eps2026q1, a.eps2026q2);
    const multB = calculateCurrentMultiple(b.price, b.epsTTM, b.eps2026q1, b.eps2026q2);

    if (sortBy === 'estPeAsc') {
      if (estPeA === null) return 1;
      if (estPeB === null) return -1;
      return estPeA - estPeB;
    }
    if (sortBy === 'estPeDesc') {
      if (estPeA === null) return 1;
      if (estPeB === null) return -1;
      return estPeB - estPeA;
    }
    if (sortBy === 'currentMultipleAsc') {
      if (multA === null) return 1;
      if (multB === null) return -1;
      return multA - multB;
    }
    if (sortBy === 'knownPeAsc') {
      if (knownPeA === null) return 1;
      if (knownPeB === null) return -1;
      return knownPeA - knownPeB;
    }
    if (sortBy === 'priceDesc') {
      return b.price - a.price;
    }
    if (sortBy === 'codeAsc') {
      return a.code.localeCompare(b.code);
    }
    return 0;
  });

  return filtered;
}

function renderAllViews() {
  const filtered = getFilteredAndSortedStocks();
  renderTable(filtered);
  renderMobileCards(filtered);
  updateStats(filtered);
  updateActiveView();
}

function renderTable(filtered) {
  const tbody = document.getElementById('stockTableBody');
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" class="text-center" style="padding: 2rem; color: var(--text-muted);">無符合條件的股票資料</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const knownPe = calculateKnownPE(item.price, item.eps2025);
    const estPe = calculateEstPE(item.price, item.eps2026q1, item.eps2026q2, item.eps2026q3);
    const currentMultiple = calculateCurrentMultiple(item.price, item.epsTTM, item.eps2026q1, item.eps2026q2);
    const catClass = 'cat-' + item.category.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '');

    return `
      <tr class="${catClass}">
        <td class="col-industry">${item.category}</td>
        <td class="col-stock">
          <div class="stock-badge">
            <span>${item.name}</span>
            <span class="stock-code">${item.code}</span>
          </div>
        </td>
        <td class="text-right">${formatEps(item.eps2025)}</td>
        <td class="text-right">${formatEps(item.eps2026q1)}</td>
        <td class="text-right">${formatEps(item.eps2026q2)}</td>
        <td class="text-right" style="font-weight: 700; color: #38bdf8;">${formatEps(item.epsTTM)}</td>
        <td class="text-right" style="font-family: Outfit, monospace; font-weight: 600;">${formatNum(item.price)}</td>
        <td class="text-right">${getPeBadgeHtml(knownPe)}</td>
        <td class="text-right">${getPeBadgeHtml(currentMultiple, 'cyan')}</td>
        <td class="text-right">${getPeBadgeHtml(estPe)}</td>
        <td class="text-center">
          <button class="btn-icon" onclick="editStock('${item.id}')" title="編輯"><i class="fa-solid fa-pen"></i></button>
          <button class="btn-icon delete" onclick="deleteStock('${item.id}')" title="刪除"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `;
  }).join('');
}

// Render Mobile Stock App Cards
function renderMobileCards(filtered) {
  const container = document.getElementById('mobileCardsGrid');
  if (filtered.length === 0) {
    container.innerHTML = `<div style="text-align: center; padding: 3rem; color: var(--text-muted); grid-column: 1/-1;">無符合條件的股票資料</div>`;
    return;
  }

  container.innerHTML = filtered.map(item => {
    const knownPe = calculateKnownPE(item.price, item.eps2025);
    const estPe = calculateEstPE(item.price, item.eps2026q1, item.eps2026q2, item.eps2026q3);
    const currentMultiple = calculateCurrentMultiple(item.price, item.epsTTM, item.eps2026q1, item.eps2026q2);

    // Get background tint for cat tag
    let catStyle = 'background: rgba(59, 130, 246, 0.2); color: #60a5fa;';
    if (item.category.includes('晶圓')) catStyle = 'background: rgba(234, 179, 8, 0.2); color: #fef08a;';
    else if (item.category.includes('塑膠')) catStyle = 'background: rgba(244, 63, 94, 0.2); color: #fecdd3;';
    else if (item.category.includes('金融')) catStyle = 'background: rgba(14, 165, 233, 0.2); color: #bae6fd;';
    else if (item.category.includes('生技')) catStyle = 'background: rgba(168, 85, 247, 0.2); color: #e9d5ff;';
    else if (item.category.includes('半導體') || item.category.includes('IC')) catStyle = 'background: rgba(34, 197, 94, 0.2); color: #bbf7d0;';

    return `
      <div class="mobile-stock-card">
        <div class="m-card-top">
          <div class="m-stock-info">
            <div class="m-stock-title">
              <span class="m-stock-name">${item.name}</span>
              <span class="m-stock-code">${item.code}</span>
            </div>
            <span class="m-cat-tag" style="${catStyle}">${item.category}</span>
          </div>
          <div class="m-price-box">
            <span class="m-price-num">${formatNum(item.price)}</span>
            <span class="m-price-unit">元</span>
          </div>
        </div>

        <div class="m-metrics-grid">
          <div class="m-metric-item">
            <span class="m-metric-label">2025 全年</span>
            <span class="m-metric-val">${formatEps(item.eps2025)}</span>
          </div>
          <div class="m-metric-item">
            <span class="m-metric-label">2026 Q1</span>
            <span class="m-metric-val">${formatEps(item.eps2026q1)}</span>
          </div>
          <div class="m-metric-item">
            <span class="m-metric-label">TTM 近4季</span>
            <span class="m-metric-val" style="color: #38bdf8; font-weight:700;">${formatEps(item.epsTTM)}</span>
          </div>
        </div>

        <div class="m-pe-section">
          <div class="m-pe-box">
            <span class="m-pe-title">已知 P/E</span>
            ${getPeBadgeHtml(knownPe)}
          </div>
          <div class="m-pe-box">
            <span class="m-pe-title">目前 EPS 倍數</span>
            ${getPeBadgeHtml(currentMultiple, 'cyan')}
          </div>
          <div class="m-pe-box">
            <span class="m-pe-title">預估 P/E</span>
            ${getPeBadgeHtml(estPe)}
          </div>
        </div>

        <div class="m-card-actions">
          <button class="btn-icon" onclick="editStock('${item.id}')"><i class="fa-solid fa-pen"></i> 編輯</button>
          <button class="btn-icon delete" onclick="deleteStock('${item.id}')"><i class="fa-solid fa-trash"></i> 刪除</button>
        </div>
      </div>
    `;
  }).join('');
}

function updateStats(items) {
  document.getElementById('statTotalCount').textContent = items.length;

  const knownPes = items.map(s => calculateKnownPE(s.price, s.eps2025)).filter(v => v !== null);
  const estPes = items.map(s => calculateEstPE(s.price, s.eps2026q1, s.eps2026q2, s.eps2026q3)).filter(v => v !== null);

  if (knownPes.length > 0) {
    const avgKnown = (knownPes.reduce((a, b) => a + b, 0) / knownPes.length).toFixed(2);
    document.getElementById('statAvgKnownPe').textContent = `${avgKnown} 倍`;
  } else {
    document.getElementById('statAvgKnownPe').textContent = '--';
  }

  if (estPes.length > 0) {
    const avgEst = (estPes.reduce((a, b) => a + b, 0) / estPes.length).toFixed(2);
    document.getElementById('statAvgEstPe').textContent = `${avgEst} 倍`;

    let minEstPe = Infinity;
    let minStockName = '--';
    items.forEach(s => {
      const est = calculateEstPE(s.price, s.eps2026q1, s.eps2026q2, s.eps2026q3);
      if (est !== null && est < minEstPe) {
        minEstPe = est;
        minStockName = `${s.name} (${est.toFixed(2)} 倍)`;
      }
    });
    document.getElementById('statLowestEstPe').textContent = minStockName;
  } else {
    document.getElementById('statAvgEstPe').textContent = '--';
    document.getElementById('statLowestEstPe').textContent = '--';
  }
}

function updateActiveView() {
  const isMobile = window.innerWidth <= 768;
  const tableView = document.getElementById('tableViewSection');
  const cardsView = document.getElementById('cardsViewSection');
  const btnText = document.querySelector('.btn-view-toggle .view-text');

  if (currentViewMode === 'card' || (currentViewMode === 'auto' && isMobile)) {
    tableView.classList.remove('active');
    cardsView.classList.add('active');
    if (btnText) btnText.textContent = '表格模式';
  } else {
    cardsView.classList.remove('active');
    tableView.classList.add('active');
    if (btnText) btnText.textContent = '卡片模式';
  }
}

// Fetch dynamic stock data
async function fetchStockData(dateStr) {
  const btn = document.getElementById('btnLoadDateData');
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 載入中...`;
  btn.disabled = true;

  try {
    const response = await fetch(`/api/stocks?date=${dateStr}`);
    if (!response.ok) throw new Error('API 無法取得資料');
    const resData = await response.json();

    if (resData.stocks) {
      stockList = resData.stocks;
      const dateFormatted = dateStr.replace(/-/g, '/');
      document.getElementById('priceHeaderDate').textContent = `${dateFormatted}收盤價`;
      document.getElementById('updateTime').textContent = `已即時更新 ${dateFormatted} 歷史股價與財報指標`;
      
      renderIndustryTabs();
      renderAllViews();
    }
  } catch (err) {
    console.error('Fetch stock data failed:', err);
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
  }
}

// Modal handling
function openModal(stock = null) {
  const modal = document.getElementById('stockModal');
  const title = document.getElementById('modalTitle');
  const form = document.getElementById('stockForm');

  form.reset();
  if (stock) {
    title.textContent = '編輯股票資料';
    document.getElementById('editStockId').value = stock.id;
    document.getElementById('inputCategory').value = stock.category;
    document.getElementById('inputCode').value = stock.code;
    document.getElementById('inputName').value = stock.name;
    document.getElementById('inputEps2025').value = stock.eps2025 ?? '';
    document.getElementById('inputEps2026Q1').value = stock.eps2026q1 ?? '';
    document.getElementById('inputEps2026Q2').value = stock.eps2026q2 ?? '';
    document.getElementById('inputPrice').value = stock.price ?? '';
  } else {
    title.textContent = '新增股票資料';
    document.getElementById('editStockId').value = '';
  }
  modal.classList.add('show');
}

function closeModal() {
  document.getElementById('stockModal').classList.remove('show');
}

window.editStock = function(id) {
  const stock = stockList.find(s => s.id === id);
  if (stock) openModal(stock);
};

window.deleteStock = function(id) {
  const stock = stockList.find(s => s.id === id);
  if (stock && confirm(`確定要刪除 ${stock.code} ${stock.name} 嗎？`)) {
    stockList = stockList.filter(s => s.id !== id);
    renderIndustryTabs();
    renderAllViews();
  }
};

// Export to CSV
function exportCsv() {
  const dateStr = document.getElementById('datePicker').value;
  let csvContent = '\uFEFF';
  csvContent += `產業,熱門股代號,熱門股名稱,2025年全年稅後EPS,2026年第一季稅後EPS,2026年第二季稅後EPS,近4季累計EPS(TTM),${dateStr}收盤價,已知本益比(2025),目前EPS倍數(TTM),預估本益比\n`;

  stockList.forEach(item => {
    const knownPe = calculateKnownPE(item.price, item.eps2025) ?? 'NA';
    const estPe = calculateEstPE(item.price, item.eps2026q1, item.eps2026q2, item.eps2026q3) ?? 'NA';
    const currentMult = calculateCurrentMultiple(item.price, item.epsTTM, item.eps2026q1, item.eps2026q2) ?? 'NA';
    csvContent += `"${item.category}","${item.code}","${item.name}",${item.eps2025 ?? ''},${item.eps2026q1 ?? ''},${item.eps2026q2 ?? ''},${item.epsTTM ?? ''},${item.price},${knownPe},${currentMult},${estPe}\n`;
  });

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `台股本益比試算表_${dateStr}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function setActiveShortcut(activeId) {
  ['btnDateSnapshot', 'btnDateToday', 'btnDatePrevDay'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      if (id === activeId) btn.classList.add('active');
      else btn.classList.remove('active');
    }
  });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  const datePicker = document.getElementById('datePicker');
  fetchStockData(datePicker.value);

  // View Toggle Button
  document.getElementById('btnToggleView').addEventListener('click', () => {
    if (currentViewMode === 'card') currentViewMode = 'table';
    else currentViewMode = 'card';
    updateActiveView();
  });

  // PWA Install Button
  document.getElementById('btnInstallPwa')?.addEventListener('click', async () => {
    if (deferredPwaPrompt) {
      deferredPwaPrompt.prompt();
      const { outcome } = await deferredPwaPrompt.userChoice;
      console.log(`User PWA prompt outcome: ${outcome}`);
      deferredPwaPrompt = null;
      document.getElementById('pwaInstallBanner')?.classList.remove('show');
    }
  });

  document.getElementById('btnDismissPwa')?.addEventListener('click', () => {
    document.getElementById('pwaInstallBanner')?.classList.remove('show');
  });

  // Mobile Bottom Nav
  document.getElementById('navHome')?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('navDate')?.addEventListener('click', () => {
    datePicker.focus();
    datePicker.scrollIntoView({ behavior: 'smooth' });
  });
  document.getElementById('navAdd')?.addEventListener('click', () => openModal());
  document.getElementById('navExport')?.addEventListener('click', exportCsv);

  // Load Date Button
  document.getElementById('btnLoadDateData').addEventListener('click', () => {
    fetchStockData(datePicker.value);
  });

  // Date Shortcuts
  document.getElementById('btnDateSnapshot').addEventListener('click', () => {
    datePicker.value = '2026-07-17';
    setActiveShortcut('btnDateSnapshot');
    fetchStockData('2026-07-17');
  });

  document.getElementById('btnDateToday').addEventListener('click', () => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    const todayStr = `${yyyy}-${mm}-${dd}`;
    datePicker.value = todayStr;
    setActiveShortcut('btnDateToday');
    fetchStockData(todayStr);
  });

  document.getElementById('btnDatePrevDay').addEventListener('click', () => {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const prevStr = `${yyyy}-${mm}-${dd}`;
    datePicker.value = prevStr;
    setActiveShortcut('btnDatePrevDay');
    fetchStockData(prevStr);
  });

  document.getElementById('searchInput').addEventListener('input', renderAllViews);
  document.getElementById('sortBySelect').addEventListener('change', renderAllViews);
  
  document.getElementById('btnAddStock').addEventListener('click', () => openModal());
  document.getElementById('btnCloseModal').addEventListener('click', closeModal);
  document.getElementById('btnCancelModal').addEventListener('click', closeModal);
  document.getElementById('btnExportCsv').addEventListener('click', exportCsv);

  document.getElementById('stockForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const id = document.getElementById('editStockId').value;
    const category = document.getElementById('inputCategory').value.trim();
    const code = document.getElementById('inputCode').value.trim();
    const name = document.getElementById('inputName').value.trim();
    const eps2025 = document.getElementById('inputEps2025').value !== '' ? parseFloat(document.getElementById('inputEps2025').value) : null;
    const eps2026q1 = document.getElementById('inputEps2026Q1').value !== '' ? parseFloat(document.getElementById('inputEps2026Q1').value) : null;
    const eps2026q2 = document.getElementById('inputEps2026Q2').value !== '' ? parseFloat(document.getElementById('inputEps2026Q2').value) : null;
    const price = parseFloat(document.getElementById('inputPrice').value);

    if (id) {
      const stock = stockList.find(s => s.id === id);
      if (stock) {
        Object.assign(stock, { category, code, name, eps2025, eps2026q1, eps2026q2, price });
      }
    } else {
      stockList.push({
        id: code || String(Date.now()),
        category,
        code,
        name,
        eps2025,
        eps2026q1,
        eps2026q2,
        price
      });
    }

    closeModal();
    renderIndustryTabs();
    renderAllViews();
  });

  window.addEventListener('resize', updateActiveView);
});

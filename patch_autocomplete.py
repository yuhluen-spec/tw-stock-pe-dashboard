"""
Patch app.js to add TW_STOCK_MASTER database and smart autocomplete suggestions for Add Stock Modal
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

tw_stock_master_code = """
/* ─── Taiwan Stock Master Database for Smart Autocomplete ────────── */
const TW_STOCK_MASTER = [
  { code: '2330', name: '台積電', category: '晶圓代工' },
  { code: '2303', name: '聯電', category: '晶圓代工' },
  { code: '5347', name: '世界先進', category: '晶圓代工' },
  { code: '2317', name: '鴻海', category: '組裝代工' },
  { code: '2454', name: '聯發科', category: 'IC設計' },
  { code: '2308', name: '台達電', category: '電源/綠能' },
  { code: '2382', name: '廣達', category: 'AI伺服器' },
  { code: '3231', name: '緯創', category: 'AI伺服器' },
  { code: '6669', name: '緯穎', category: 'AI伺服器' },
  { code: '2356', name: '英業達', category: '電腦組裝' },
  { code: '2324', name: '仁寶', category: '電腦組裝' },
  { code: '2376', name: '技嘉', category: '主機板/顯卡' },
  { code: '2357', name: '華碩', category: '品牌電腦' },
  { code: '2395', name: '研華', category: '工業電腦' },
  { code: '5274', name: '信驊', category: 'IC設計' },
  { code: '3034', name: '聯詠', category: 'IC設計' },
  { code: '3035', name: '智原', category: 'IP/IC設計' },
  { code: '3443', name: '創意', category: 'IP/IC設計' },
  { code: '3661', name: '世芯-KY', category: 'IP/ASIC' },
  { code: '2059', name: '川湖', category: '軸承/滑軌' },
  { code: '7769', name: '鴻勁', category: '半導體設備' },
  { code: '6515', name: '穎崴', category: '半導體封測材料' },
  { code: '6223', name: '旺矽', category: '半導體封測材料' },
  { code: '3583', name: '辛耘', category: '半導體設備' },
  { code: '3131', name: '弘塑', category: '半導體設備' },
  { code: '1301', name: '台塑', category: '塑膠' },
  { code: '1303', name: '南亞', category: '塑膠' },
  { code: '1326', name: '台化', category: '塑膠' },
  { code: '1305', name: '華夏', category: '塑膠' },
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
  { code: '6446', name: '藥華藥', category: '生技股' },
  { code: '6472', name: '保瑞', category: '生技股' },
  { code: '7799', name: '禾榮科', category: '生技股' },
  { code: '1795', name: '美時', category: '生技股' },
  { code: '4147', name: '中裕', category: '生技股' },
  { code: '2603', name: '長榮', category: '航運股' },
  { code: '2609', name: '陽明', category: '航運股' },
  { code: '2615', name: '萬海', category: '航運股' },
  { code: '2618', name: '長榮航', category: '航空股' },
  { code: '2610', name: '華航', category: '航空股' },
  { code: '2002', name: '中鋼', category: '鋼鐵股' },
  { code: '2412', name: '中華電', category: '電信股' },
  { code: '3045', name: '台灣大', category: '電信股' },
  { code: '4904', name: '遠傳', category: '電信股' },
  { code: '2201', name: '裕隆', category: '汽車股' },
  { code: '2207', name: '和泰車', category: '汽車股' },
  { code: '9910', name: '豐泰', category: '製鞋/傳統' },
  { code: '9904', name: '寶成', category: '製鞋/傳統' },
  { code: '2912', name: '統一超', category: '百貨零售' },
  { code: '1216', name: '統一', category: '食品飲料' }
];

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

    // Filter matching stocks and take top 7
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
  document.getElementById('inputCode').value = code;
  document.getElementById('inputName').value = name;
  document.getElementById('inputCategory').value = category;
  document.getElementById('modalStockSearch').value = `${code} ${name}`;
  document.getElementById('suggestionsBox').style.display = 'none';

  // Check if stock already exists in current dataset to auto-fill price & EPS
  const existing = stockList.find(s => s.code === code);
  if (existing) {
    document.getElementById('inputEps2025').value = existing.eps2025 ?? '';
    document.getElementById('inputEps2026Q1').value = existing.eps2026q1 ?? '';
    document.getElementById('inputEps2026Q2').value = existing.eps2026q2 ?? '';
    document.getElementById('inputPrice').value = existing.price ?? '';
  } else {
    // If not in stockList, attempt to fetch live stock price
    fetchStockPriceAndEps(code);
  }
}

async function fetchStockPriceAndEps(code) {
  const spinner = document.getElementById('modalSearchSpinner');
  if (spinner) spinner.style.display = 'inline-block';
  try {
    const dateStr = document.getElementById('datePicker').value;
    const res = await fetch(`${API_BASE}/api/stocks?date=${dateStr}`);
    if (res.ok) {
      const data = await res.json();
      const match = data.stocks?.find(s => s.code === code);
      if (match) {
        document.getElementById('inputEps2025').value = match.eps2025 ?? '';
        document.getElementById('inputEps2026Q1').value = match.eps2026q1 ?? '';
        document.getElementById('inputEps2026Q2').value = match.eps2026q2 ?? '';
        document.getElementById('inputPrice').value = match.price ?? '';
      }
    }
  } catch (err) {
    console.error('Fetch stock detail failed:', err);
  } finally {
    if (spinner) spinner.style.display = 'none';
  }
}
"""

if 'TW_STOCK_MASTER' not in content:
    content = content.replace("/* ─── State ───", tw_stock_master_code + "\n/* ─── State ───")
    content = content.replace("document.getElementById('stockModal')?.classList.add('show');", 
                              "const searchIn = document.getElementById('modalStockSearch'); if(searchIn) searchIn.value=''; const sugBox = document.getElementById('suggestionsBox'); if(sugBox) sugBox.style.display='none'; document.getElementById('stockModal')?.classList.add('show');")

    content = content.replace("initScrollShadow();", "initScrollShadow();\n  setupModalStockAutocomplete();")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added TW_STOCK_MASTER and autocomplete to app.js!")

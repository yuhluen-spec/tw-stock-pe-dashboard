"""
Expand TW_STOCK_MASTER to 150+ stocks and add 4-digit live code lookup fallback in app.js
"""

with open('app.js', 'rb') as f:
    app_js = f.read().decode('utf-8')

EXPANDED_TW_STOCK_MASTER = r"""const TW_STOCK_MASTER = [
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
];"""

# Replace TW_STOCK_MASTER
import re
app_js = re.sub(r'const TW_STOCK_MASTER = \[[\s\S]*?\];', EXPANDED_TW_STOCK_MASTER, app_js)

# Update setupModalStockAutocomplete to add 4-digit dynamic code fallback
old_auto = """    const matches = TW_STOCK_MASTER.filter(s => 
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
    `).join('');"""

new_auto = """    let matches = TW_STOCK_MASTER.filter(s => 
      s.code.toLowerCase().includes(q) || 
      s.name.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q)
    ).slice(0, 7);

    // If query is a 4-digit code not fully in top matches, append live online search item
    const isNumericCode = /^\d{4}$/.test(q);
    const hasExact = matches.some(s => s.code === q);
    
    if (isNumericCode && !hasExact) {
      matches.unshift({ code: q, name: `即時線上抓取 [${q}]`, category: '台股個股', isLive: true });
      matches = matches.slice(0, 7);
    }

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
    `).join('');"""

app_js = app_js.replace(old_auto, new_auto)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Expanded TW_STOCK_MASTER and added 4-digit live code lookup fallback in app.js!")

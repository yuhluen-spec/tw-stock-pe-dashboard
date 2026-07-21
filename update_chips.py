"""
Remove btnDateSnapshot chip handling from app.js and default to latest trading date
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

# Remove btnDateSnapshot from setChip
content = content.replace("['btnDateSnapshot','btnDateToday','btnDatePrevDay']", "['btnDateToday','btnDatePrevDay']")

# Remove btnDateSnapshot event listener
old_listeners = """  document.getElementById('btnDateSnapshot').addEventListener('click', () => {
    datePicker.value = '2026-07-17'; setChip('btnDateSnapshot'); fetchStockData('2026-07-17');
  });
  document.getElementById('btnDateToday').addEventListener('click', () => {
    const d = new Date();
    const s = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    datePicker.value = s; setChip('btnDateToday'); fetchStockData(s);
  });"""

new_listeners = """  document.getElementById('btnDateToday').addEventListener('click', () => {
    const s = getLatestTradingDate();
    datePicker.value = s; setChip('btnDateToday'); fetchStockData(s);
  });"""

content = content.replace(old_listeners, new_listeners)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.js date handlers!")

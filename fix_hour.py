"""
Fix getLatestTradingDate cut-off hour from 16:00 to 14:00 (TWSE data publishes at 14:00)
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

content = content.replace("if (d.getHours() < 16) d.setDate(d.getDate() - 1);", "if (d.getHours() < 14) d.setDate(d.getDate() - 1);")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated getLatestTradingDate cut-off hour to 14:00!")

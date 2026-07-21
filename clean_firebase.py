"""
Clean up Firebase files and restore app.js to pure Vercel relative endpoint /api/stocks
"""

import os
import shutil

# 1. Update app.js
with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

# Remove API_BASE logic
lines = content.split('\n')
clean_lines = []
for line in lines:
    if 'const API_BASE =' in line or 'firebaseapp.com' in line:
        continue
    clean_lines.append(line)

content = '\n'.join(clean_lines)
content = content.replace('${API_BASE}/api/stocks', '/api/stocks')
content = content.replace('API_BASE + \'/api/stocks\'', '\'/api/stocks\'')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Remove Firebase directories and files if present
for path in ['firebase.json', '.firebaserc']:
    if os.path.exists(path):
        os.remove(path)

if os.path.exists('functions'):
    shutil.rmtree('functions')

print("Cleaned up Firebase files and restored app.js for pure Vercel deployment!")

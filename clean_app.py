"""
Clean up app.js lines 384 and 387
"""

with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    if 'vercel.app' in line or ": '';" in line:
        continue
    clean_lines.append(line)

with open('app.js', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print("app.js cleaned up!")

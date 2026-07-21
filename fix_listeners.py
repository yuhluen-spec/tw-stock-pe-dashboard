"""
Safely fix all event listener bindings in app.js using optional chaining ?.addEventListener
and completely remove btnDateSnapshot references
"""

with open('app.js', 'rb') as f:
    content = f.read().decode('utf-8')

# Remove any remaining btnDateSnapshot listener
lines = content.split('\n')
clean_lines = []
for line in lines:
    if 'btnDateSnapshot' in line:
        continue
    clean_lines.append(line)

content = '\n'.join(clean_lines)

# Replace document.getElementById('XYZ').addEventListener with document.getElementById('XYZ')?.addEventListener
import re
content = re.sub(
    r"document\.getElementById\((['\"].*?['\"])\)\.addEventListener",
    r"document.getElementById(\1)?.addEventListener",
    content
)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Safely updated all event listeners in app.js!")

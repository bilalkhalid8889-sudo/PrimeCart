import os
import json

formats = {}
for f in os.listdir('images'):
    parts = f.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
        if '-' in name:
            pieces = name.split('-')
            pid = pieces[0]
            num = pieces[1]
            if num == '1':
                formats[pid] = ext

# Show first 20 files to debug
print("First 20 files in images folder:")
files = os.listdir('images')[:20]
for f in files:
    print(f)

print("\nFormat map found:", len(formats), "products")
print(json.dumps(formats, indent=2))
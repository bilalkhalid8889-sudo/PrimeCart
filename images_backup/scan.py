import os
import json

formats = {}
for f in os.listdir('images'):
    parts = f.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
        if '-' in name:
            pid, num = name.split('-')[0], name.split('-')[1]
            if num == '1':
                formats[pid] = ext

print(json.dumps(formats, indent=2))
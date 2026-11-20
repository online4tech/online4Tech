#!/usr/bin/env python3
import json, sys
from pathlib import Path

local_path = Path(sys.argv[1])
remote_path = Path(sys.argv[2])
local = json.loads(local_path.read_text(encoding='utf-8'))
remote = json.loads(remote_path.read_text(encoding='utf-8'))
local_items = local.get('items', [])
remote_items = remote.setdefault('items', [])

def identity(item):
    repo = item.get('sourceRepo') or ''
    asset = item.get('sourceAssetName') or ''
    if repo and asset:
        return ('source-asset', repo.lower(), asset.lower())
    source = item.get('originalSourceUrl') or item.get('sourceUrl') or ''
    if source and ('/releases/download/' in source or source.lower().endswith(('.ipk','.sh','.zip','.tar','.tar.gz','.tar.xz','.tgz','.deb','.nfi','.img','.bin'))):
        return ('source-url', source)
    package = item.get('packageName') or ''
    if package:
        return ('package', repo.lower(), package.lower(), str(item.get('architecture') or '').lower(), str(item.get('version') or ''))
    return ('id', str(item.get('id', '')))

index = {identity(item): i for i, item in enumerate(remote_items)}
used_ids = {str(item.get('id')) for item in remote_items if item.get('id') is not None}
next_id = max([int(x) for x in used_ids if x.isdigit()] or [0]) + 1
for item in local_items:
    key = identity(item)
    if key in index:
        # Local item is the newest validated representation of the same source asset.
        item['id'] = remote_items[index[key]].get('id', item.get('id'))
        remote_items[index[key]] = item
        continue
    if item.get('id') is not None and str(item.get('id')) in used_ids:
        item['id'] = next_id
        next_id += 1
    used_ids.add(str(item.get('id')))
    index[key] = len(remote_items)
    remote_items.append(item)

for category in remote.get('categories', []):
    cid = category.get('id')
    category['count'] = sum(1 for item in remote_items if item.get('category') == cid)
    for sub in category.get('subcategories', []):
        sub['count'] = sum(1 for item in remote_items if item.get('category') == cid and item.get('subcategory') == sub.get('id'))

remote_path.write_text(json.dumps(remote, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'merged_local_items': len(local_items), 'final_items': len(remote_items)}, ensure_ascii=False))

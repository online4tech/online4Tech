#!/usr/bin/env python3
import json, sys
from pathlib import Path

local_path=Path(sys.argv[1]); remote_path=Path(sys.argv[2])
local=json.loads(local_path.read_text(encoding='utf-8'))
remote=json.loads(remote_path.read_text(encoding='utf-8'))
remote_items=remote.setdefault('items',[])

def keys(item):
    out=[]
    if item.get('id') is not None: out.append(('id',str(item.get('id'))))
    repo=item.get('sourceRepo') or ''; asset=item.get('sourceAssetName') or ''
    if repo and asset: out.append(('source-asset',repo.lower(),asset.lower()))
    package=item.get('packageName') or ''
    if package: out.append(('package',repo.lower(),package.lower(),str(item.get('architecture') or '').lower(),str(item.get('version') or '')))
    return out

index={}
for i,item in enumerate(remote_items):
    for key in keys(item): index[key]=i
used_ids={str(x.get('id')) for x in remote_items if x.get('id') is not None}
next_id=max([int(x) for x in used_ids if x.isdigit()] or [0])+1
for item in local.get('items',[]):
    item_keys=keys(item)
    match=next((index[k] for k in item_keys if k in index),None)
    if match is not None:
        # Prefer the same numeric ID for existing catalog rows; source identity also deduplicates imports.
        existing=remote_items[match]
        if item.get('id') is not None and str(item.get('id'))==str(existing.get('id')):
            item['id']=existing.get('id')
        else:
            item['id']=existing.get('id',item.get('id'))
        remote_items[match]=item
        for key in keys(item): index[key]=match
        continue
    if item.get('id') is not None and str(item.get('id')) in used_ids:
        item['id']=next_id; next_id+=1
    used_ids.add(str(item.get('id')))
    pos=len(remote_items); remote_items.append(item)
    for key in keys(item): index[key]=pos

for category in remote.get('categories',[]):
    cid=category.get('id')
    category['count']=sum(1 for item in remote_items if item.get('category')==cid)
    for sub in category.get('subcategories',[]):
        sub['count']=sum(1 for item in remote_items if item.get('category')==cid and item.get('subcategory')==sub.get('id'))

remote_path.write_text(json.dumps(remote,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'merged_local_items':len(local.get('items',[])),'final_items':len(remote_items)},ensure_ascii=False))

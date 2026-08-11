import os, uuid
from .. import wrapper, data
from . import state
from .gateway import safe_write

def read_cats(lib_path):
    if not lib_path: return {}
    dir_path = os.path.dirname(wrapper.abspath(lib_path))
    fpath = os.path.join(dir_path, data.CATALOG_FILE) if dir_path else ""
    if not os.path.exists(fpath): return {}
    
    cats = {}
    with open(fpath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip() or line.startswith('VERSION'): continue
            parts = line.split(':', 2)
            if len(parts) == 3: cats[parts[2].strip()] = parts[0].strip()
    return cats

def get_cat_name(obj):
    cid = state.get_cat(obj)
    if not cid: return None
    cats = read_cats(state.get_lib(obj))
    return next((name for name, u in cats.items() if u == cid), None)

def add_cat(lib_path, name):
    cid = str(uuid.uuid5(data.NAMESPACE, name))
    
    existing_cats = read_cats(lib_path)
    if name in existing_cats: return existing_cats[name]
    
    dir_path = os.path.dirname(wrapper.abspath(lib_path)) or "."
    fpath = os.path.join(dir_path, data.CATALOG_FILE)
    
    lines = [data.CATALOG_HEADER]
    if os.path.exists(fpath):
        with open(fpath, 'r') as f: lines = f.readlines()
            
    lines.append(f"{cid}:{name}:{name}\n")
    safe_write(fpath, lines, data.MODE_REPLACE)
    return cid

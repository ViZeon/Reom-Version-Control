import os, uuid
from .. import wrapper, data
from .state import get_cat, get_lib
from .gateway import safe_write

def read_cats(lib_path):
    if not lib_path: return {}
    dir_path = os.path.dirname(wrapper.abspath(lib_path))
    if not dir_path: return {}
    fpath = os.path.join(dir_path, data.CATALOG_FILE)
    if not os.path.exists(fpath): return {}
    cats = {}
    with open(fpath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip() or line.startswith('VERSION'): continue
            parts = line.split(':', 2)
            if len(parts) == 3:
                cats[parts[2].strip()] = parts[0].strip()
    return cats

def get_cat_name(obj):
    cid = get_cat(obj)
    if not cid: return None
    cats = read_cats(get_lib(obj))
    for name, u in cats.items():
        if u == cid: return name
    return None

def add_cat(lib_path, name):
    cid = str(uuid.uuid5(data.NAMESPACE, name))
    dir_path = os.path.dirname(wrapper.abspath(lib_path))
    if not dir_path: dir_path = "."
    fpath = os.path.join(dir_path, data.CATALOG_FILE)
    
    lines = [data.CATALOG_HEADER]
    if os.path.exists(fpath):
        with open(fpath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('VERSION') or line.startswith('#'): continue
                parts = line.split(':', 2)
                if len(parts) == 3:
                    lines.append(f"{parts[0]}:{parts[1]}:{parts[2]}\n")
                    
    if not any(line.startswith(f"{cid}:") for line in lines):
        lines.append(f"{cid}:{name}:{name}\n")
        
    safe_write(fpath, lines, data.MODE_REPLACE)
    return cid
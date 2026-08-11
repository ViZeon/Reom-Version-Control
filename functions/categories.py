import os, uuid
from .. import wrapper, data
from . import state

def _get_cat_file_path(lib_path):
    """Finds the correct root directory for the catalog file."""
    root = wrapper.get_asset_library_root(lib_path)
    if not root:
        root = os.path.dirname(wrapper.abspath(lib_path))
    return os.path.join(root, data.CATALOG_FILE) if root else ""

def read_cats(lib_path):
    if not lib_path: return {}
    fpath = _get_cat_file_path(lib_path)
    if not fpath or not os.path.exists(fpath): return {}
    
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
    cid = str(uuid.uuid4())
    
    existing_cats = read_cats(lib_path)
    if name in existing_cats: return existing_cats[name]
    
    fpath = _get_cat_file_path(lib_path)
    if not fpath: return cid
    
    # FAILSAFE: If the file doesn't exist, create it safely.
    if not os.path.exists(fpath):
        with open(fpath, 'w') as f:
            f.write(f"VERSION 1\n\n{cid}:{name}:{name}\n")
        return cid
        
    # FAILSAFE: If it exists, strictly APPEND to it to protect user data.
    needs_newline = False
    with open(fpath, 'r') as f:
        lines = f.readlines()
        if lines and not lines[-1].endswith('\n'):
            needs_newline = True
            
    with open(fpath, 'a') as f:
        if needs_newline:
            f.write('\n')
        f.write(f"{cid}:{name}:{name}\n")
        
    return cid

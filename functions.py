"""Pure functions and business logic. No bpy."""
import os, sys, uuid
from . import wrapper, data

def addon_register(classes):
    wrapper.register(classes)
    mod = sys.modules.get(__package__)
    if mod and getattr(mod, data.AUTO_ENABLED, False):
        setattr(mod, data.AUTO_ENABLED, False)
    else:
        def _startup():
            win, area = wrapper.get_view3d()
            if win and area:
                with wrapper.override(win, area): wrapper.invoke(data.OP_STARTUP)
        wrapper.timer(_startup, data.STARTUP_DELAY)

def addon_unregister(classes): wrapper.unregister(classes)

# === STATE ===
def get_name(obj): return wrapper.get_prop(obj, data.P_NAME) or obj.name
def get_ver(obj):
    v = wrapper.get_prop(obj, data.P_VER)
    return tuple(map(int, v.split(data.VER_SEP))) if v else None
def get_lib(obj): return wrapper.get_prop(obj, data.P_LIB)
def get_cat(obj): return wrapper.get_prop(obj, data.P_CAT)

def set_ver(obj, v): wrapper.set_prop(obj, data.P_VER, data.VER_SEP.join(map(str, v)))
def set_lib(obj, p): wrapper.set_prop(obj, data.P_LIB, p)
def set_cat(obj, cid): wrapper.set_prop(obj, data.P_CAT, cid)

# === MATH & PARSING ===
def bump_ver(v): return (v[0], v[1], v[2] + 1)
def str_ver(v): return data.VER_SEP.join(map(str, v))

# === FILE PATHS ===
def find_root(path):
    if not path: return None
    p = os.path.expanduser(path)
    if os.path.exists(os.path.join(p, data.V_DIR)): return p
    try:
        for n in os.listdir(p):
            sub = os.path.join(p, n)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, data.V_DIR)): return sub
    except: pass
    return None

def scan_versions(name, path):
    root = find_root(path)
    if not root: return []
    vdir = os.path.join(root, data.V_DIR, name)
    if not os.path.exists(vdir): return []
    
    pref, suff = f"{name}{data.VER_SEP}", data.BLEND_EXT
    vers = []
    for f in os.listdir(vdir):
        if f.startswith(pref) and f.endswith(suff):
            try: vers.append(tuple(map(int, f[len(pref):-len(suff)].split(data.VER_SEP))))
            except: pass
    vers.sort()
    return vers

def get_version_path(name, v_str, root):
    vdir = os.path.join(root, data.V_DIR, name)
    os.makedirs(vdir, exist_ok=True)
    return os.path.join(vdir, f"{name}{data.VER_SEP}{v_str}{data.BLEND_EXT}")

def prepare_path(path):
    if not path.endswith(data.BLEND_EXT): path += data.BLEND_EXT
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# === CATEGORIES (Asset Browser Catalogs) ===
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
        
    with open(fpath, 'w') as f:
        f.writelines(lines)
        
    return cid

# === LIBRARY VALIDATION & SYNC ===
def validate_lib_file(lib_path, obj_name):
    if not lib_path or not os.path.exists(lib_path): return
    
    needs_backup = False
    try:
        with wrapper.load_lib(lib_path) as (df, dt):
            obj_count = len(df.objects)
            # If there's more than 1 object, or 1 object but wrong name, backup.
            if obj_count > 1 or (obj_count == 1 and obj_name not in df.objects):
                needs_backup = True
    except:
        needs_backup = True
        
    if needs_backup:
        bak_path = lib_path + data.SIG_BAK_EXT
        if os.path.exists(bak_path): os.remove(bak_path)
        os.rename(lib_path, bak_path)
        print(data.WARN_BACKUP.format(bak_path))

def write_obj(obj, path, cat=None):
    if cat:
        wrapper.mark_asset(obj)
        wrapper.set_catalog(obj, cat)
        
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mats(obj))
    wrapper.write_lib(path, blocks)
    
    if cat:
        wrapper.clear_asset(obj)

def sync_file_to_lib(ver_path, lib_path, tag=None):
    existing = set(wrapper.get_all_objs().keys())
    with wrapper.load_lib(ver_path) as (df, dt): dt.objects = df.objects
    for ob in wrapper.get_all_objs():
        if ob.name not in existing:
            write_obj(ob, lib_path, tag)
            wrapper.remove_obj(ob)

# === ACTIONS (Called by UI) ===
def setup_lib(obj, filepath):
    path = prepare_path(wrapper.abspath(filepath))
    if not os.path.exists(path): wrapper.save_main(path)
    set_lib(obj, path)
    return data.INFO_LIB_SET.format(path)

def save_version(obj):
    lib = get_lib(obj)
    name = get_name(obj)
    root = wrapper.get_prefs().lib_path
    cat = get_cat(obj)
    new_ver = bump_ver(get_ver(obj)) if get_ver(obj) else data.INITIAL_VERSION
    v_str = str_ver(new_ver)
    
    write_obj(obj, get_version_path(name, v_str, root)) # Plain save to versions dir
    
    validate_lib_file(lib, name)
    write_obj(obj, lib, cat) # Marked save to library
    
    set_ver(obj, new_ver)
    wrapper.refresh_assets()
    return data.INFO_SAVED.format(name, v_str)

def highlight_version(obj, v_str):
    lib = get_lib(obj)
    name = get_name(obj)
    ver_path = get_version_path(name, v_str, wrapper.get_prefs().lib_path)
    
    validate_lib_file(lib, name)
    sync_file_to_lib(ver_path, lib, get_cat(obj))
    wrapper.refresh_assets()
    return data.INFO_HIGHLIGHTED.format(name, v_str)

def assign_cat(obj, cid):
    set_cat(obj, cid)
    return data.INFO_CAT_SET.format(cid)

def scan_info(obj):
    name = get_name(obj)
    vers = scan_versions(name, wrapper.get_prefs().lib_path)
    if vers: return data.INFO_VER_LIST.format(name, data.LIST_JOIN.join(str_ver(v) for v in vers))
    return data.INFO_NO_VER.format(name)
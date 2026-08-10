"""Pure functions and business logic. No bpy."""
import os, sys, uuid
from . import wrapper, data

def addon_register(classes):
    wrapper.register(classes)
    
    wrapper.register_keymap(data.OP_VERSION, data.KEY_SAVE, [data.MOD_SHIFT, data.MOD_ALT], data.PROP_ACTION, data.ACT_SAVE)
    
    mod = sys.modules.get(__package__)
    if mod and getattr(mod, data.AUTO_ENABLED, False):
        setattr(mod, data.AUTO_ENABLED, False)
    else:
        def _startup():
            win, area = wrapper.get_view3d()
            if win and area:
                with wrapper.override(win, area): wrapper.invoke(data.OP_STARTUP)
        wrapper.timer(_startup, data.STARTUP_DELAY)

def addon_unregister(classes): 
    wrapper.unregister_keymaps()
    wrapper.unregister(classes)

# === STATE ===
def get_name(obj):
    name = wrapper.get_prop(obj, data.P_NAME)
    if name: return name
    lib = get_lib(obj)
    if lib: return os.path.splitext(os.path.basename(lib))[0]
    return obj.name

def get_uuid(obj): return wrapper.get_prop(obj, data.P_UUID)
def get_ver(obj):
    v = wrapper.get_prop(obj, data.P_VER)
    return tuple(map(int, v.split(data.VER_SEP))) if v else None
def get_lib(obj): return wrapper.get_prop(obj, data.P_LIB)
def get_cat(obj): return wrapper.get_prop(obj, data.P_CAT)
def is_linked(obj): return wrapper.is_linked(obj)

def set_ver(obj, v): wrapper.set_prop(obj, data.P_VER, data.VER_SEP.join(map(str, v)))
def set_lib(obj, p): wrapper.set_prop(obj, data.P_LIB, p)
def set_cat(obj, cid): wrapper.set_prop(obj, data.P_CAT, cid)
def set_name(obj, name): wrapper.set_prop(obj, data.P_NAME, name)
def set_uuid(obj, uid): wrapper.set_prop(obj, data.P_UUID, uid)

# === MATH & PARSING ===
def bump_ver(v): return (v[0], v[1], v[2] + 1)
def bump_step(v): return (v[0], v[1] + 1, 0)
def bump_release(v): return (v[0] + 1, 0, 0)
def str_ver(v): return data.VER_SEP.join(map(str, v))
def format_ver_ui(v): return data.UI_VER_PREFIX + data.UI_VER_SEP.join(map(str, v))

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

def get_default_lib_path(obj):
    root = wrapper.get_prefs().lib_path
    if not root: return ""
    return os.path.join(os.path.expanduser(root), f"{get_name(obj)}{data.BLEND_EXT}")

def prepare_path(path):
    if not path.endswith(data.BLEND_EXT): path += data.BLEND_EXT
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# === SAFE WRITE GATEWAY ===
def _get_unique_path(path):
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def _resolve_safety(path, mode, *args):
    if not os.path.exists(path): return path
    
    match mode:
        case data.MODE_SAFE:
            return _get_unique_path(path)
        case data.MODE_REPLACE:
            os.remove(path)
            return path
        case data.MODE_BACKUP:
            bak_path = _get_unique_path(path + data.BAK_EXT)
            os.rename(path, bak_path)
            print(data.WARN_BACKUP.format(bak_path))
            return path
        case data.MODE_CUSTOM:
            if args and callable(args[0]): return args[0](path)
            return path
        case _:
            raise ValueError(f"Unknown safety mode: {mode}")

def _write_text(path, lines):
    with open(path, 'w') as f: f.writelines(lines)

def safe_write(path, file_data, mode, *args):
    safety_mode = mode
    file_func = None
    
    if mode == data.MODE_CUSTOM:
        safety_mode = args[0] if len(args) > 0 else data.MODE_SAFE
        file_func = args[1] if len(args) > 1 else None

    safe_path = _resolve_safety(path, safety_mode)
    
    if file_func:
        file_func(safe_path, file_data)
        return
        
    ext = os.path.splitext(safe_path)[1].lower()
    match ext:
        case data.BLEND_EXT: wrapper.write_lib(safe_path, file_data)
        case data.TXT_EXT: _write_text(safe_path, file_data)
        case _: raise ValueError(f"Unsupported file type for write: {ext}")

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
        
    safe_write(fpath, lines, data.MODE_REPLACE)
    return cid

# === LIBRARY VALIDATION & SYNC ===
def validate_lib_file(lib_path, obj_name):
    if not lib_path or not os.path.exists(lib_path): return
    
    needs_backup = False
    try:
        with wrapper.load_lib(lib_path) as (df, dt):
            obj_count = len(df.objects)
            if obj_count > 1 or (obj_count == 1 and obj_name not in df.objects):
                needs_backup = True
    except:
        needs_backup = True
        
    if needs_backup:
        _resolve_safety(lib_path, data.MODE_BACKUP)

def write_obj(obj, path, name=None, cat=None, mode=data.MODE_REPLACE):
    """
    Writes an object to a .blend file, ensuring it is saved with the correct name.
    Temporarily renames objects/meshes if there are collisions in the scene.
    """
    orig_name = obj.name
    orig_data_name = obj.data.name if obj.data else None
    temp_name = name + data.TEMP_SUFFIX if name else None
    
    if name:
        # Temporarily move colliding objects/meshes out of the way
        if temp_name and name in wrapper.get_all_objs() and wrapper.get_all_objs()[name] != obj:
            wrapper.get_all_objs()[name].name = temp_name
        if temp_name and obj.data and name in wrapper.get_meshes() and wrapper.get_meshes()[name] != obj.data:
            wrapper.get_meshes()[name].name = temp_name
            
        obj.name = name
        if obj.data: obj.data.name = name

    if cat:
        wrapper.mark_asset(obj)
        wrapper.set_catalog(obj, cat)
        
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mats(obj))
    safe_write(path, blocks, mode)
    
    if cat:
        wrapper.clear_asset(obj)
        
    # Restore original names
    if name:
        obj.name = orig_name
        if obj.data and orig_data_name:
            obj.data.name = orig_data_name
            
        if temp_name and temp_name in wrapper.get_all_objs():
            wrapper.get_all_objs()[temp_name].name = name
        if temp_name and temp_name in wrapper.get_meshes():
            wrapper.get_meshes()[temp_name].name = name

def sync_file_to_lib(ver_path, lib_path, name, tag=None):
    existing = set(wrapper.get_all_objs().keys())
    
    with wrapper.load_lib(ver_path) as (df, dt): dt.objects = df.objects
    
    for ob in wrapper.get_all_objs():
        if ob.name not in existing:
            # write_obj handles renaming to `name` safely
            write_obj(ob, lib_path, name, tag, data.MODE_REPLACE)
            wrapper.remove_obj(ob)

# === ACTIONS (Called by UI) ===
def setup_lib(obj, name, filepath):
    path = prepare_path(wrapper.abspath(filepath))
    if not os.path.exists(path): wrapper.save_main(path)
    
    set_name(obj, name)
    set_uuid(obj, str(uuid.uuid4()))
    set_lib(obj, path)
    return data.INFO_LIB_SET.format(path)

def save_version(obj, action=data.ACT_SAVE):
    lib = get_lib(obj)
    name = get_name(obj)
    root = wrapper.get_prefs().lib_path
    cat = get_cat(obj)
    cur_ver = get_ver(obj)
    
    if not cur_ver:
        new_ver = data.INITIAL_VERSION
    else:
        match action:
            case data.ACT_SAVE: new_ver = bump_ver(cur_ver)
            case data.ACT_STEP: new_ver = bump_step(cur_ver)
            case data.ACT_RELEASE: new_ver = bump_release(cur_ver)
            case _: new_ver = bump_ver(cur_ver)
            
    v_str = str_ver(new_ver)
    
    write_obj(obj, get_version_path(name, v_str, root), name, mode=data.MODE_SAFE)
    
    validate_lib_file(lib, name)
    write_obj(obj, lib, name, cat, data.MODE_REPLACE)
    
    set_ver(obj, new_ver)
    wrapper.refresh_assets()
    return data.INFO_SAVED.format(name, v_str)

def set_main_version(obj, v_str):
    lib = get_lib(obj)
    name = get_name(obj)
    ver_path = get_version_path(name, v_str, wrapper.get_prefs().lib_path)
    
    validate_lib_file(lib, name)
    sync_file_to_lib(ver_path, lib, name, get_cat(obj))
    wrapper.refresh_assets()
    return data.INFO_SET_MAIN.format(name, v_str)

def enter_edit(obj):
    wrapper.make_local(obj)
    return data.INFO_ENTER_EDIT.format(get_name(obj))

def end_edit(obj):
    name = get_name(obj)
    lib = get_lib(obj)
    save_version(obj, data.ACT_SAVE)
    wrapper.remove_obj(obj)
    wrapper.link_obj_from_lib(lib, name)
    return data.INFO_END_EDIT.format(name)

def assign_cat(obj, cid):
    set_cat(obj, cid)
    return data.INFO_CAT_SET.format(cid)

def scan_info(obj):
    name = get_name(obj)
    vers = scan_versions(name, wrapper.get_prefs().lib_path)
    if vers: return data.INFO_VER_LIST.format(name, data.LIST_JOIN.join(str_ver(v) for v in vers))
    return data.INFO_NO_VER.format(name)
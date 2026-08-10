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
def get_tag(obj): return wrapper.get_prop(obj, data.P_TAG)
def get_lib(obj): return wrapper.get_prop(obj, data.P_LIB)

def set_ver(obj, v): wrapper.set_prop(obj, data.P_VER, data.VER_SEP.join(map(str, v)))
def set_tag(obj, t): wrapper.set_prop(obj, data.P_TAG, t)
def set_lib(obj, p): wrapper.set_prop(obj, data.P_LIB, p)

# === MATH & PARSING ===
def parse_tags(s): return [t.strip() for t in s.split(data.TAG_SEP)] if s else []
def tag_to_catalog(t): return str(uuid.uuid5(data.NAMESPACE, t))
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

# === LIBRARY SYNC ===
def write_obj(obj, path):
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mats(obj))
    wrapper.write_lib(path, blocks)

def sync_to_lib(obj, lib_path, tag=None):
    if not wrapper.has_asset(obj): wrapper.mark_asset(obj)
    if tag and wrapper.has_asset(obj): wrapper.set_catalog(obj, tag_to_catalog(tag))
    write_obj(obj, lib_path)

def sync_file_to_lib(ver_path, lib_path, tag=None):
    existing = set(wrapper.get_all_objs().keys())
    with wrapper.load_lib(ver_path) as (df, dt): dt.objects = df.objects
    for ob in wrapper.get_all_objs():
        if ob.name not in existing:
            sync_to_lib(ob, lib_path, tag)
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
    new_ver = bump_ver(get_ver(obj)) if get_ver(obj) else data.INITIAL_VERSION
    v_str = str_ver(new_ver)
    
    write_obj(obj, get_version_path(name, v_str, root))
    sync_to_lib(obj, lib, get_tag(obj))
    set_ver(obj, new_ver)
    return data.INFO_SAVED.format(name, v_str)

def highlight_version(obj, v_str):
    lib = get_lib(obj)
    name = get_name(obj)
    ver_path = get_version_path(name, v_str, wrapper.get_prefs().lib_path)
    sync_file_to_lib(ver_path, lib, get_tag(obj))
    return data.INFO_HIGHLIGHTED.format(name, v_str)

def assign_tag(obj, tag):
    set_tag(obj, tag)
    return data.INFO_TAG_SET.format(tag)

def scan_info(obj):
    name = get_name(obj)
    vers = scan_versions(name, wrapper.get_prefs().lib_path)
    if vers: return data.INFO_VER_LIST.format(name, data.TAG_JOIN.join(str_ver(v) for v in vers))
    return data.INFO_NO_VER.format(name)
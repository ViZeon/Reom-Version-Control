"""Pure functions. No bpy."""
import os, sys, uuid
from . import wrapper, data

# === LIFECYCLE ===
def addon_register(classes):
    wrapper.register(classes)
    mod = sys.modules.get(__package__)
    if mod and getattr(mod, "_AUTO_ENABLED", False):
        setattr(mod, "_AUTO_ENABLED", False)
    else:
        def _startup():
            win, area = wrapper.get_view3d()
            if win and area:
                with wrapper.override(win, area): wrapper.invoke(data.OP_STARTUP)
        wrapper.timer(_startup, 0.1)

def addon_unregister(classes): wrapper.unregister(classes)

# === MESH STATE ===
def mesh_get_name(obj): return wrapper.get_prop(obj, data.PROP_NAME) or obj.name

def mesh_get_ver(obj):
    v = wrapper.get_prop(obj, data.PROP_VER)
    return tuple(int(p) for p in v.split('_')) if v else None

def mesh_set_ver(obj, v): wrapper.set_prop(obj, data.PROP_VER, '_'.join(map(str, v)))
def mesh_get_lib(obj): return wrapper.get_prop(obj, data.PROP_LIB)
def mesh_set_lib(obj, p): wrapper.set_prop(obj, data.PROP_LIB, p)
def mesh_get_tag(obj): return wrapper.get_prop(obj, data.PROP_TAG)
def mesh_set_tag(obj, t): wrapper.set_prop(obj, data.PROP_TAG, t)

# === TAGS & VERSIONS ===
def tag_parse(s): return [t.strip() for t in s.split(',')] if s else []
def tag_to_catalog(t): return str(uuid.uuid5(uuid.NAMESPACE_DNS, t))
def ver_bump(v): return (v[0], v[1], v[2] + 1)
def ver_str(v): return '_'.join(map(str, v))

# === FILE PATHS ===
def file_find_root(lib_path):
    if not lib_path: return None
    p = os.path.expanduser(lib_path)
    if os.path.exists(os.path.join(p, data.VERSIONS_DIR)): return p
    try:
        for n in os.listdir(p):
            sub = os.path.join(p, n)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, data.VERSIONS_DIR)): return sub
    except: pass
    return None

def file_scan_versions(mesh_name, lib_path):
    root = file_find_root(lib_path)
    if not root: return []
    vdir = os.path.join(root, data.VERSIONS_DIR, mesh_name)
    if not os.path.exists(vdir): return []
    
    pref, suff = f"{mesh_name}_", ".blend"
    vers = []
    for f in os.listdir(vdir):
        if f.startswith(pref) and f.endswith(suff):
            try: vers.append(tuple(int(p) for p in f[len(pref):-len(suff)].split('_')))
            except: pass
    vers.sort()
    return vers

def file_get_version_path(mesh_name, ver_str, root):
    vdir = os.path.join(root, data.VERSIONS_DIR, mesh_name)
    os.makedirs(vdir, exist_ok=True)
    return os.path.join(vdir, f"{mesh_name}_{ver_str}.blend")

def file_get_lib_path(mesh_name, root):
    return os.path.join(os.path.expanduser(root), f"{mesh_name}.blend") if root else ""

def file_prepare_path(path):
    if not path.endswith('.blend'): path += '.blend'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# === LIBRARY OPS ===
def lib_write(obj, filepath):
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mats(obj))
    wrapper.write_lib(filepath, blocks)

def lib_update(obj, filepath, tag):
    if not wrapper.has_asset(obj): wrapper.mark_asset(obj)
    if tag and wrapper.has_asset(obj): wrapper.set_catalog(obj, tag_to_catalog(tag))
    lib_write(obj, filepath)

def lib_promote_from_file(src_path, lib_path, tag):
    existing = set(wrapper.get_all_objs().keys())
    with wrapper.load_lib(src_path) as (df, dt): dt.objects = df.objects
    for ob in wrapper.get_all_objs():
        if ob.name not in existing:
            lib_update(ob, lib_path, tag)
            wrapper.remove_obj(ob)
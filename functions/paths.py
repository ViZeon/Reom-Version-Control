import os
from .. import wrapper, data
from ..utils.logger import get_logger
from .state import get_name, get_storage_mode

log = get_logger()

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

def get_version_path(name, v_tuple, root, mode):
    vdir = os.path.join(root, data.V_DIR, name)
    os.makedirs(vdir, exist_ok=True)
    
    if mode == data.MODE_VER:
        v_str = data.VER_SEP.join(map(str, v_tuple))
        return os.path.join(vdir, f"{name}{data.VER_SEP}{v_str}{data.BLEND_EXT}")
    elif mode == data.MODE_SUB:
        v_str = data.VER_SEP.join(map(str, v_tuple[:2]))
        return os.path.join(vdir, f"{name}{data.VER_SEP}{v_str}{data.PACKED_SUFFIX}{data.BLEND_EXT}")
    elif mode == data.MODE_RELEASE:
        v_str = str(v_tuple[0])
        return os.path.join(vdir, f"{name}{data.VER_SEP}{v_str}{data.PACKED_SUFFIX}{data.BLEND_EXT}")

def scan_versions(name, path):
    root = find_root(path)
    if not root: return []
    vdir = os.path.join(root, data.V_DIR, name)
    if not os.path.exists(vdir): return []
    
    mode = get_storage_mode()
    vers = []
    
    if mode == data.MODE_VER:
        pref, suff = f"{name}{data.VER_SEP}", data.BLEND_EXT
        for f in os.listdir(vdir):
            if f.startswith(pref) and f.endswith(suff) and not f.endswith(data.PACKED_SUFFIX + data.BLEND_EXT):
                try: vers.append(tuple(map(int, f[len(pref):-len(suff)].split(data.VER_SEP))))
                except: pass
    else:
        pref, suff = f"{name}{data.VER_SEP}", f"{data.PACKED_SUFFIX}{data.BLEND_EXT}"
        for f in os.listdir(vdir):
            if f.startswith(pref) and f.endswith(suff):
                fpath = os.path.join(vdir, f)
                try:
                    with wrapper.load_lib(fpath) as (df, dt):
                        for obj_name in df.objects:
                            if obj_name.startswith(name + data.VER_SEP):
                                try: vers.append(tuple(map(int, obj_name[len(name)+1:].split(data.VER_SEP))))
                                except: pass
                except Exception as e: log.error(f"Failed to scan packed file {fpath}: {e}")
                
    vers.sort()
    return vers

def get_default_lib_path(obj):
    root = wrapper.get_prefs().lib_path
    if not root: return ""
    return os.path.join(os.path.expanduser(root), f"{get_name(obj)}{data.BLEND_EXT}")

def prepare_path(path):
    if not path.endswith(data.BLEND_EXT): path += data.BLEND_EXT
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# === MIGRATION ===
def migrate_all_versions(root, new_mode):
    """Unpacks everything to individual files, then repacks according to new_mode."""
    if not root: return
    vdir = os.path.join(root, data.V_DIR)
    if not os.path.exists(vdir): return
    log.info(f"Starting migration to {new_mode}...")
    
    for asset_name in os.listdir(vdir):
        asset_dir = os.path.join(vdir, asset_name)
        if not os.path.isdir(asset_dir): continue
        
        # 1. Unpack any existing packed files to individual files
        for f in list(os.listdir(asset_dir)):
            if not f.endswith(data.PACKED_SUFFIX + data.BLEND_EXT): continue
            fpath = os.path.join(asset_dir, f)
            
            existing = set(wrapper.get_all_objs().keys())
            with wrapper.load_lib(fpath) as (df, dt):
                obj_names = [n for n in df.objects if n.startswith(asset_name + data.VER_SEP)]
                dt.objects = obj_names
                
            for ob in list(wrapper.get_all_objs()):
                if ob.name not in existing:
                    wrapper.make_local(ob)
                    ind_path = os.path.join(asset_dir, f"{ob.name}{data.BLEND_EXT}")
                    blocks = {ob, ob.data} if ob.data else {ob}
                    blocks.update(wrapper.get_mats(ob))
                    wrapper.write_lib(ind_path, blocks)
                    wrapper.remove_obj(ob)
                    existing.add(ob.name)
                    
            os.remove(fpath)
            
        if new_mode == data.MODE_VER: continue
        
        # 2. Group individual files and repack them
        groups = {} # group_key -> [list of (filepath, v_tuple)]
        for f in os.listdir(asset_dir):
            if not f.endswith(data.BLEND_EXT): continue
            v_str = f[len(asset_name)+1:-len(data.BLEND_EXT)]
            try:
                v_tuple = tuple(map(int, v_str.split(data.VER_SEP)))
            except: continue
            
            if new_mode == data.MODE_SUB:
                group_key = v_tuple[:2]
            elif new_mode == data.MODE_RELEASE:
                group_key = (v_tuple[0],)
            else: continue
                
            if group_key not in groups: groups[group_key] = []
            groups[group_key].append((os.path.join(asset_dir, f), v_tuple))
            
        for group_key, files in groups.items():
            if new_mode == data.MODE_SUB:
                packed_name = f"{asset_name}{data.VER_SEP}{data.VER_SEP.join(map(str, group_key))}{data.PACKED_SUFFIX}{data.BLEND_EXT}"
            elif new_mode == data.MODE_RELEASE:
                packed_name = f"{asset_name}{data.VER_SEP}{group_key[0]}{data.PACKED_SUFFIX}{data.BLEND_EXT}"
                
            packed_path = os.path.join(asset_dir, packed_name)
            
            loaded_objs = []
            existing = set(wrapper.get_all_objs().keys())
            
            for fpath, v_tuple in files:
                with wrapper.load_lib(fpath) as (df, dt):
                    dt.objects = [n for n in df.objects if n.startswith(asset_name)]
                    
                for ob in list(wrapper.get_all_objs()):
                    if ob.name not in existing:
                        wrapper.make_local(ob)
                        v_str = data.VER_SEP.join(map(str, v_tuple))
                        ob.name = f"{asset_name}{data.VER_SEP}{v_str}"
                        if ob.data: ob.data.name = ob.name
                        loaded_objs.append(ob)
                        existing.add(ob.name)
                        
            blocks = set()
            for ob in loaded_objs:
                blocks.add(ob)
                if ob.data: blocks.add(ob.data)
                blocks.update(wrapper.get_mats(ob))
                
            wrapper.write_lib(packed_path, blocks)
            log.info(f"Packed {len(loaded_objs)} versions into {packed_path}")
            
            for ob in loaded_objs: wrapper.remove_obj(ob)
            for fpath, _ in files:
                if os.path.exists(packed_path): os.remove(fpath)
                
    log.info("Migration complete.")
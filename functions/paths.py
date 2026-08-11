import os
import shutil
from .. import wrapper, data
from ..utils.logger import get_logger
from . import state
from .gateway import safe_write

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
    
    mode = state.get_storage_mode()
    vers = []
    
    if mode == data.MODE_VER:
        pref, suff = f"{name}{data.VER_SEP}", data.BLEND_EXT
        for f in os.listdir(vdir):
            if f.startswith(data.BACKUP_PREFIX) or f.endswith(data.PACKED_SUFFIX + data.BLEND_EXT): continue
            if f.startswith(pref) and f.endswith(suff):
                try: vers.append(tuple(map(int, f[len(pref):-len(suff)].split(data.VER_SEP))))
                except: pass
    else:
        pref, suff = f"{name}{data.VER_SEP}", f"{data.PACKED_SUFFIX}{data.BLEND_EXT}"
        for f in os.listdir(vdir):
            if f.startswith(data.BACKUP_PREFIX): continue
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
    return os.path.join(os.path.expanduser(root), f"{state.get_name(obj)}{data.BLEND_EXT}") if root else ""

def prepare_path(path):
    if not path.endswith(data.BLEND_EXT): path += data.BLEND_EXT
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def migrate_all_versions(root, new_mode):
    if not root: return
    vdir = os.path.join(root, data.V_DIR)
    if not os.path.exists(vdir): return
    log.info(f"Starting migration to {new_mode}...")
    
    for asset_name in os.listdir(vdir):
        asset_dir = os.path.join(vdir, asset_name)
        if not os.path.isdir(asset_dir): continue
        
        active_files = [f for f in os.listdir(asset_dir) if not f.startswith(data.BACKUP_PREFIX) and f.endswith(data.BLEND_EXT)]
        if active_files:
            backup_dir = os.path.join(asset_dir, f"{data.BACKUP_PREFIX}migration")
            os.makedirs(backup_dir, exist_ok=True)
            for f in active_files: shutil.copy2(os.path.join(asset_dir, f), os.path.join(backup_dir, f))
        
        for f in list(os.listdir(asset_dir)):
            if f.startswith(data.BACKUP_PREFIX) or not f.endswith(data.PACKED_SUFFIX + data.BLEND_EXT): continue
            fpath = os.path.join(asset_dir, f)
            
            existing = set(wrapper.get_all_objs())
            with wrapper.load_lib(fpath) as (df, dt):
                dt.objects = [n for n in df.objects if n.startswith(asset_name + data.VER_SEP)]
                
            loaded_objs = [ob for ob in wrapper.get_all_objs() if ob not in existing]
            for ob in loaded_objs:
                wrapper.make_local(ob)
                ind_path = os.path.join(asset_dir, f"{ob.name}{data.BLEND_EXT}")
                safe_write(ind_path, wrapper.get_blocks(ob), data.MODE_REPLACE)
                wrapper.remove_obj(ob)
                    
            os.remove(fpath)
            
        if new_mode == data.MODE_VER: continue
        
        groups = {}
        for f in os.listdir(asset_dir):
            if f.startswith(data.BACKUP_PREFIX) or not f.endswith(data.BLEND_EXT): continue
            v_str = f[len(asset_name)+1:-len(data.BLEND_EXT)]
            try: v_tuple = tuple(map(int, v_str.split(data.VER_SEP)))
            except: continue
            
            group_key = v_tuple[:2] if new_mode == data.MODE_SUB else (v_tuple[0],) if new_mode == data.MODE_RELEASE else None
            if not group_key: continue
                
            groups.setdefault(group_key, []).append((os.path.join(asset_dir, f), v_tuple))
            
        for group_key, files in groups.items():
            packed_name = f"{asset_name}{data.VER_SEP}{data.VER_SEP.join(map(str, group_key))}{data.PACKED_SUFFIX}{data.BLEND_EXT}" if new_mode == data.MODE_SUB else f"{asset_name}{data.VER_SEP}{group_key[0]}{data.PACKED_SUFFIX}{data.BLEND_EXT}"
            packed_path = os.path.join(asset_dir, packed_name)
            
            existing = set(wrapper.get_all_objs())
            loaded_objs = []
            
            for fpath, v_tuple in files:
                with wrapper.load_lib(fpath) as (df, dt): dt.objects = df.objects
                new_objs = [ob for ob in wrapper.get_all_objs() if ob not in existing]
                for ob in new_objs:
                    wrapper.make_local(ob)
                    ob.name = f"{asset_name}{data.VER_SEP}{data.VER_SEP.join(map(str, v_tuple))}"
                    if ob.data: ob.data.name = ob.name
                    loaded_objs.append(ob)
                    existing.add(ob)
                        
            if not loaded_objs: continue
                        
            safe_write(packed_path, wrapper.get_blocks(loaded_objs), data.MODE_REPLACE)
            
            for ob in loaded_objs: wrapper.remove_obj(ob)
            for fpath, _ in files:
                if os.path.exists(packed_path): os.remove(fpath)

import os
from .. import wrapper, data
from ..utils.logger import get_logger
from .gateway import safe_write

log = get_logger()

def backup_file(path, backup_dir_name):
    if not os.path.exists(path): return None
    backup_dir = os.path.join(os.path.dirname(path), backup_dir_name)
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = os.path.join(backup_dir, os.path.basename(path))
    if os.path.exists(backup_path): os.remove(backup_path)
    os.rename(path, backup_path)
    return backup_path

def validate_lib_file(lib_path, obj_name):
    if not lib_path or not os.path.exists(lib_path): return
    try:
        with wrapper.load_lib(lib_path) as (df, dt):
            if len(df.objects) > 1 or (len(df.objects) == 1 and obj_name not in df.objects):
                backup_file(lib_path, f"{data.BACKUP_PREFIX}foreign")
    except:
        backup_file(lib_path, f"{data.BACKUP_PREFIX}foreign")

def write_obj(obj, path, name=None, cat=None, mode=data.MODE_REPLACE):
    orig_name, orig_data_name = obj.name, (obj.data.name if obj.data else None)
    
    if name:
        obj.name = name
        if obj.data: obj.data.name = name
    if cat:
        wrapper.mark_asset(obj)
        wrapper.set_catalog(obj, cat)
        
    safe_write(path, wrapper.get_blocks(obj), mode)
    
    if cat: wrapper.clear_asset(obj)
    if name:
        obj.name = orig_name
        if obj.data and orig_data_name: obj.data.name = orig_data_name

def pack_version(obj, name, v_tuple, path, mode):
    backup_path = backup_file(path, f"{data.BACKUP_PREFIX}{mode}")
    loaded_objs = []
    target_name = f"{name}{data.VER_SEP}{data.VER_SEP.join(map(str, v_tuple))}"
    
    if backup_path and os.path.exists(backup_path):
        existing = set(wrapper.get_all_objs())
        with wrapper.load_lib(backup_path) as (df, dt):
            dt.objects = [n for n in df.objects if n.startswith(name) and n != target_name]
        loaded_objs = [ob for ob in wrapper.get_all_objs() if ob not in existing]
        for ob in loaded_objs: wrapper.make_local(ob)
                
    orig_name = obj.name
    obj.name = target_name
        
    safe_write(path, wrapper.get_blocks([obj] + loaded_objs), data.MODE_REPLACE)
    
    obj.name = orig_name
    for ob in loaded_objs: wrapper.remove_obj(ob)

def sync_to_lib(ver_path, lib_path, name, v_str, tag=None, is_packed=False):
    live_obj = wrapper.get_active_obj()
    if live_obj and live_obj.name == name:
        wrapper.remove_obj(live_obj)
        
    existing = set(wrapper.get_all_objs())
    target_name = f"{name}{data.VER_SEP}{v_str}"
    
    with wrapper.load_lib(ver_path) as (df, dt):
        dt.objects = [target_name] if is_packed and target_name in df.objects else df.objects
        
    for ob in list(wrapper.get_all_objs()):
        if ob not in existing:
            wrapper.make_local(ob)
            write_obj(ob, lib_path, name, tag, data.MODE_REPLACE)
            wrapper.remove_obj(ob)
            
    wrapper.link_obj_from_lib(lib_path, name)

import os
from .. import wrapper, data
from ..utils.logger import get_logger
from .gateway import safe_write

log = get_logger()

def backup_file(path, backup_dir_name):
    """Moves a file to a specified backup folder. Replaces if exists."""
    if not os.path.exists(path): return None
    
    vdir = os.path.dirname(path)
    backup_dir = os.path.join(vdir, backup_dir_name)
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = os.path.join(backup_dir, os.path.basename(path))
    if os.path.exists(backup_path): os.remove(backup_path)
    
    os.rename(path, backup_path)
    log.info(f"Backed up file to: {backup_path}")
    return backup_path

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
        backup_file(lib_path, f"{data.BACKUP_PREFIX}foreign")

def write_obj(obj, path, name=None, cat=None, mode=data.MODE_REPLACE):
    """Writes an object to a .blend file, safely handling name collisions."""
    orig_name = obj.name
    orig_data_name = obj.data.name if obj.data else None
    temp_name = name + data.TEMP_SUFFIX if name else None
    
    if name:
        # Temporarily move colliding objects/meshes out of the way
        if temp_name and name in wrapper.get_all_objs() and wrapper.get_all_objs()[name] != obj:
            colliding_obj = wrapper.get_all_objs()[name]
            if not colliding_obj.library: colliding_obj.name = temp_name
                
        if temp_name and obj.data and name in wrapper.get_meshes() and wrapper.get_meshes()[name] != obj.data:
            colliding_mesh = wrapper.get_meshes()[name]
            if not colliding_mesh.library: colliding_mesh.name = temp_name
            
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
        
    # Restore names
    if name:
        obj.name = orig_name
        if obj.data and orig_data_name: obj.data.name = orig_data_name
            
        if temp_name and temp_name in wrapper.get_all_objs():
            wrapper.get_all_objs()[temp_name].name = name
        if temp_name and temp_name in wrapper.get_meshes():
            wrapper.get_meshes()[temp_name].name = name

def pack_version(obj, name, v_tuple, path, mode):
    """Packs an object into a single .blend file containing multiple versions."""
    backup_path = backup_file(path, f"{data.BACKUP_PREFIX}{mode}")
    
    loaded_objs = []
    v_str = data.VER_SEP.join(map(str, v_tuple))
    target_name = f"{name}{data.VER_SEP}{v_str}"
    
    if backup_path and os.path.exists(backup_path):
        existing = set(wrapper.get_all_objs().keys())
        with wrapper.load_lib(backup_path) as (df, dt):
            # Load all versions EXCEPT the one we are currently saving (to prevent collisions)
            dt.objects = [n for n in df.objects if n.startswith(name) and n != target_name]
            
        for ob in list(wrapper.get_all_objs()):
            if ob.name not in existing:
                wrapper.make_local(ob)
                loaded_objs.append(ob)
                
    orig_name = obj.name
    obj.name = target_name
        
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mats(obj))
    for ob in loaded_objs:
        blocks.add(ob)
        if ob.data: blocks.add(ob.data)
        blocks.update(wrapper.get_mats(ob))
        
    safe_write(path, blocks, data.MODE_REPLACE)
    log.info(f"Packed version {v_str} into {path}")
    
    obj.name = orig_name
    for ob in loaded_objs: wrapper.remove_obj(ob)

def sync_to_lib(ver_path, lib_path, name, v_str, tag=None, is_packed=False):
    """Extracts a version and writes it to the library file. Unifies file and packed sync."""
    live_obj = wrapper.get_active_obj()
    if live_obj and live_obj.name == name:
        wrapper.remove_obj(live_obj)
        
    existing = set(wrapper.get_all_objs().keys())
    target_name = f"{name}{data.VER_SEP}{v_str}"
    
    with wrapper.load_lib(ver_path) as (df, dt):
        if is_packed:
            dt.objects = [target_name] if target_name in df.objects else []
        else:
            dt.objects = df.objects
        
    for ob in list(wrapper.get_all_objs()):
        if ob.name not in existing:
            wrapper.make_local(ob)
            write_obj(ob, lib_path, name, tag, data.MODE_REPLACE)
            wrapper.remove_obj(ob)
            
    wrapper.link_obj_from_lib(lib_path, name)
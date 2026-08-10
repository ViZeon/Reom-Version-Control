import os, uuid
from .. import wrapper, data
from ..utils.logger import get_logger
from . import state
from .paths import get_default_lib_path, get_version_path, prepare_path, scan_versions
from .gateway import safe_write
from .sync import validate_lib_file, write_obj, pack_version, sync_file_to_lib, sync_packed_to_lib
from .math import str_ver, bump_ver, bump_step, bump_release

log = get_logger()

def setup_lib(obj, name, filepath):
    path = prepare_path(wrapper.abspath(filepath))
    if not os.path.exists(path):
        blocks = {obj, obj.data} if obj.data else {obj}
        blocks.update(wrapper.get_mats(obj))
        wrapper.write_lib(path, blocks)
    
    state.set_name(obj, name)
    state.set_uuid(obj, str(uuid.uuid4()))
    state.set_lib(obj, path)
    log.info(f"Setup library for {name} at {path}")
    return data.INFO_LIB_SET.format(path)

def save_version(obj, action=data.ACT_SAVE, root=None):
    lib = state.get_lib(obj)
    name = state.get_name(obj)
    if root is None: root = wrapper.get_prefs().lib_path
    cat = state.get_cat(obj)
    cur_ver = state.get_ver(obj)
    mode = state.get_storage_mode()
    
    if not cur_ver:
        new_ver = data.INITIAL_VERSION
    else:
        match action:
            case data.ACT_SAVE: new_ver = bump_ver(cur_ver)
            case data.ACT_STEP: new_ver = bump_step(cur_ver)
            case data.ACT_RELEASE: new_ver = bump_release(cur_ver)
            case _: new_ver = bump_ver(cur_ver)
            
    v_str = str_ver(new_ver)
    ver_path = get_version_path(name, new_ver, root, mode)
    
    if mode == data.MODE_VER:
        write_obj(obj, ver_path, name, mode=data.MODE_SAFE)
    else:
        pack_version(obj, name, new_ver, ver_path, mode)
    
    validate_lib_file(lib, name)
    write_obj(obj, lib, name, cat, data.MODE_REPLACE)
    
    state.set_ver(obj, new_ver)
    wrapper.refresh_assets()
    log.info(f"Saved {name} {v_str} (Mode: {mode})")
    return data.INFO_SAVED.format(name, v_str)

def set_main_version(obj, v_str, root=None):
    lib = state.get_lib(obj)
    name = state.get_name(obj)
    v_tuple = tuple(map(int, v_str.split(data.VER_SEP)))
    mode = state.get_storage_mode()
    if root is None: root = wrapper.get_prefs().lib_path
    ver_path = get_version_path(name, v_tuple, root, mode)
    
    validate_lib_file(lib, name)
    
    if mode == data.MODE_VER:
        sync_file_to_lib(ver_path, lib, name, state.get_cat(obj))
    else:
        sync_packed_to_lib(ver_path, lib, name, v_str, state.get_cat(obj))
        
    wrapper.refresh_assets()
    log.info(f"Set main version for {name} to {v_str}")
    return data.INFO_SET_MAIN.format(name, v_str)

def enter_edit(obj):
    wrapper.make_local(obj)
    return data.INFO_ENTER_EDIT.format(state.get_name(obj))

def end_edit(obj):
    name = state.get_name(obj)
    lib = state.get_lib(obj)
    save_version(obj, data.ACT_SAVE)
    wrapper.remove_obj(obj)
    wrapper.link_obj_from_lib(lib, name)
    return data.INFO_END_EDIT.format(name)

def assign_cat(obj, cid):
    state.set_cat(obj, cid)
    return data.INFO_CAT_SET.format(cid)

def scan_info(obj):
    name = state.get_name(obj)
    vers = scan_versions(name, wrapper.get_prefs().lib_path)
    if vers: return data.INFO_VER_LIST.format(name, data.LIST_JOIN.join(str_ver(v) for v in vers))
    return data.INFO_NO_VER.format(name)
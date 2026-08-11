import os
from .. import wrapper, data
from ..utils.logger import get_logger

log = get_logger()

def _resolve_safety(path, mode):
    if not os.path.exists(path): return path
    
    if mode == data.MODE_SAFE:
        base, ext = os.path.splitext(path)
        i = 1
        while os.path.exists(f"{base}_{i}{ext}"): i += 1
        return f"{base}_{i}{ext}"
        
    if mode == data.MODE_REPLACE:
        os.remove(path)
        return path
        
    if mode == data.MODE_BACKUP:
        i = 1
        while os.path.exists(f"{path}{data.BAK_EXT}{i}"): i += 1
        bak_path = f"{path}{data.BAK_EXT}{i}"
        os.rename(path, bak_path)
        log.info(f"Backed up file to: {bak_path}")
        return path
        
    raise ValueError(f"Unknown safety mode: {mode}")

def safe_write(path, file_data, mode):
    safe_path = _resolve_safety(path, mode)
    ext = os.path.splitext(safe_path)[1].lower()
    
    if ext == data.BLEND_EXT: 
        wrapper.write_lib(safe_path, file_data)
    elif ext == data.TXT_EXT: 
        with open(safe_path, 'w') as f: f.writelines(file_data)
    else: 
        raise ValueError(f"Unsupported file type: {ext}")

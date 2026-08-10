import os
from .. import wrapper, data
from ..utils.logger import get_logger

log = get_logger()

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
            bak_base = path + data.BAK_EXT
            i = 1
            while os.path.exists(f"{bak_base}{i}"):
                i += 1
            bak_path = f"{bak_base}{i}"
            os.rename(path, bak_path)
            log.info(f"Backed up file to: {bak_path}")
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
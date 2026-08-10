import os
from .. import wrapper, data

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
def get_storage_mode(): return wrapper.get_prefs().storage_mode

def set_ver(obj, v): wrapper.set_prop(obj, data.P_VER, data.VER_SEP.join(map(str, v)))
def set_lib(obj, p): wrapper.set_prop(obj, data.P_LIB, p)
def set_cat(obj, cid): wrapper.set_prop(obj, data.P_CAT, cid)
def set_name(obj, name): wrapper.set_prop(obj, data.P_NAME, name)
def set_uuid(obj, uid): wrapper.set_prop(obj, data.P_UUID, uid)
from .. import data

def bump_ver(v): return (v[0], v[1], v[2] + 1)
def bump_step(v): return (v[0], v[1] + 1, 0)
def bump_release(v): return (v[0] + 1, 0, 0)
def str_ver(v): return data.VER_SEP.join(map(str, v))

def format_ver_ui(v):
    """Formats version tuple for UI, padding to 3 digits."""
    if not v: return ""
    padded = (list(v) + [0, 0, 0])[:3]
    return data.UI_VER_PREFIX + data.UI_VER_SEP.join(map(str, padded))

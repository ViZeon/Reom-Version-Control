# Re-exports everything so UI calls don't change.
from .lifecycle import addon_register, addon_unregister
from .state import get_name, get_uuid, get_ver, get_lib, get_cat, is_linked, get_storage_mode, set_ver, set_lib, set_cat, set_name, set_uuid
from .math import bump_ver, bump_step, bump_release, str_ver, format_ver_ui
from .paths import find_root, get_version_path, scan_versions, get_default_lib_path, prepare_path, migrate_all_versions
from .gateway import safe_write, _resolve_safety
from .categories import read_cats, get_cat_name, add_cat
from .sync import validate_lib_file, write_obj, backup_packed_file, pack_version, sync_file_to_lib, sync_packed_to_lib
from .actions import setup_lib, save_version, set_main_version, enter_edit, end_edit, assign_cat, scan_info
import uuid

# === BLENDER ENUMS ===
AREA_VIEW3D = 'VIEW_3D'
REGION_UI = 'UI'
SUBTYPE_FILE = 'FILE_PATH'
SUBTYPE_DIR = 'DIR_PATH'
OP_INVOKE = 'INVOKE_DEFAULT'
REPORT_ERROR = 'ERROR'
REPORT_INFO = 'INFO'
OP_CANCEL = 'CANCELLED'
OP_FINISH = 'FINISHED'

# === API BOOLEANS ===
FAKE_USER = True
DO_UNLINK = True
COPY_MAIN = True

# === CONFIG ===
STARTUP_DELAY = 0.1
REFRESH_DELAY = 0.2
AUTO_ENABLED = "_AUTO_ENABLED"
INITIAL_VERSION = (1, 0, 0)
NAMESPACE = uuid.NAMESPACE_DNS
LIST_JOIN = ", "
TEMP_SUFFIX = "_reom_temp"

# === FILE SYSTEM ===
V_DIR = "_versions"
VER_SEP = "_"
BLEND_EXT = ".blend"
TXT_EXT = ".txt"
BAK_EXT = ".bak"
CATALOG_FILE = "blender_assets.cats.txt"
CATALOG_HEADER = "VERSION 1\n"
PACKED_SUFFIX = ".versions"
MAX_BACKUPS = 3

# === STORAGE MODES ===
MODE_VER = "per_current"
MODE_SUB = "per_sub"
MODE_RELEASE = "per_release"

ITEM_STORAGE_MODES = [
    (MODE_VER, "Per-Current", "Save a new file for every save (e.g., 1_0_0.blend)"),
    (MODE_SUB, "Per-Sub", "Pack all saves of a sub-version into one file (e.g., 1_0.versions.blend)"),
    (MODE_RELEASE, "Per-Release", "Pack all saves of a release into one file (e.g., 1.versions.blend)")
]

# === WRITE MODES ===
MODE_SAFE = "safe"
MODE_REPLACE = "replace"
MODE_BACKUP = "backup"
MODE_CUSTOM = "custom"

# === VERSION ACTIONS ===
ACT_SAVE = "save"
ACT_STEP = "step"
ACT_RELEASE = "release"

# === ENUM ITEMS ===
ITEM_ACTIONS = [
    (ACT_SAVE, "Save", "Save Version"),
    (ACT_STEP, "Step", "Step Sub-Version"),
    (ACT_RELEASE, "Release", "Release Major Version")
]

# === UI METADATA ===
PANEL_LABEL = "Reom VC"
PANEL_CATEGORY = "Reom"
OP_SETUP_LABEL = "Setup Lib File"
OP_VERSION_LABEL = "Version Actions"
OP_SETUP_CAT_LABEL = "Set Category"
OP_TEST_LABEL = "Test Scan"
OP_ENTER_EDIT_LABEL = "Enter Edit"
OP_END_EDIT_LABEL = "End Edit"
PREF_LIB = "lib_path"
PREF_STORAGE = "storage_mode"
WIDTH_SMALL = 300
WIDTH_LARGE = 400

# === UI FORMATS ===
UI_VER_PREFIX = "v"
UI_VER_SEP = "."

# === PROPERTIES ===
P_NAME = "reom_vc_name"
P_UUID = "reom_vc_uuid"
P_VER = "reom_vc_ver"
P_LIB = "reom_vc_lib"
P_CAT = "reom_vc_cat"
PROP_FILEPATH = "filepath"
PROP_EXISTING = "existing"
PROP_NEW_CAT = "new_cat"
PROP_ACTION = "action"
PROP_ASSET_NAME = "asset_name"

# === UI IDS ===
OP_STARTUP = "reom_vc.startup"
OP_SETUP = "reom_vc.setup_lib_file"
OP_VERSION = "reom_vc.version"
OP_SET_MAIN = "reom_vc.set_main"
OP_SETUP_CAT = "reom_vc.setup_cat"
OP_TEST = "reom_vc.test_scan"
OP_ENTER_EDIT = "reom_vc.enter_edit"
OP_END_EDIT = "reom_vc.end_edit"
PANEL_ID = "VIEW3D_PT_reom_vc"

# === KEYMAP ===
KEYMAP_NAME = "Reom VC"
KEY_SAVE = 'W'
MOD_SHIFT = 'SHIFT'
MOD_ALT = 'ALT'
MOD_CTRL = 'CTRL'

# === UI STRINGS ===
TEXT_READY = "VC is ready."
TEXT_SELECT_LIB = "Select library file"
TEXT_FILEPATH_LABEL = "Library File"
TEXT_FILEPATH_DESC = "Creates a .blend file to hold the asset and its versions."
TEXT_ASSET_NAME = "Asset Name"
TEXT_PICK_VER = "Pick version:"
TEXT_SET_MAIN = "Set Main"
TEXT_MESH = "Mesh: "
TEXT_VERSION = "Version: "
TEXT_CAT = "Category: "
TEXT_VERSIONS = "Versions:"
TEXT_NO_VER = "No versions found"
TEXT_SETUP_PROMPT = "No library file set for this object."
TEXT_SETUP_HINT = "Click 'Setup Lib File' to begin tracking versions."
TEXT_SELECT_CAT = "Select Category"
TEXT_EXISTING = "Existing:"
TEXT_NEW_CAT = "New Category:"
TEXT_STATE_LINKED = "Linked (Read-Only)"
TEXT_STATE_ACTIVE = "Active (Editing)"
TEXT_PREF_LIB = "Library Path"
TEXT_PREF_STORAGE = "Storage Mode"

# === BUTTON LABELS ===
TEXT_SAVE = "Save"
TEXT_STEP = "Step"
TEXT_RELEASE = "Release"

# === REPORT TEMPLATES ===
INFO_LIB_SET = "Lib set: {}"
INFO_SAVED = "Saved {} {}"
INFO_SET_MAIN = "Set main {} {}"
INFO_CAT_SET = "Category set: {}"
INFO_VER_LIST = "Mesh '{}' versions: {}"
INFO_NO_VER = "Mesh '{}' has no versions"
INFO_ENTER_EDIT = "Entered edit mode for {}"
INFO_END_EDIT = "Saved and re-linked {}"

# === WARNINGS ===
WARN_BACKUP = "Backed up user file to: {}"

# === ERROR MESSAGES ===
ERR_NO_OBJ = "No object selected"
ERR_NO_LIB = "No library file set"
ERR_NO_CAT = "No category selected"
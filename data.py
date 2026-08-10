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
AUTO_ENABLED = "_AUTO_ENABLED"
INITIAL_VERSION = (1, 0, 0)
NAMESPACE = uuid.NAMESPACE_DNS

# === FILE SYSTEM ===
V_DIR = "_versions"
VER_SEP = "_"
BLEND_EXT = ".blend"
DEFAULT_TAGS = "Character, Prop, Weapon"
TAG_SEP = ","
TAG_JOIN = ", "

# === PROPERTIES ===
P_NAME = "reom_vc_name"
P_VER = "reom_vc_ver"
P_LIB = "reom_vc_lib"
P_TAG = "reom_vc_tag"
PROP_FILEPATH = "filepath"
PROP_TAG_UI = "tag"

# === UI IDS ===
OP_STARTUP = "reom_vc.startup"
OP_SETUP = "reom_vc.setup_lib_file"
OP_SAVE = "reom_vc.save"
OP_HIGHLIGHT = "reom_vc.highlight"
OP_TAG = "reom_vc.set_tag"
OP_TEST = "reom_vc.test_scan"
PANEL_ID = "VIEW3D_PT_reom_vc"

# === UI METADATA ===
PANEL_LABEL = "Reom VC"
PANEL_CATEGORY = "Reom"
OP_SETUP_LABEL = "Setup Lib File"
OP_SAVE_LABEL = "Save Version"
OP_TAG_LABEL = "Set Tag"
OP_TEST_LABEL = "Test Scan"
PREF_LIB = "lib_path"
PREF_TAGS = "tags"
PREF_LIB_LABEL = "Library Path"
PREF_TAGS_LABEL = "Tags"
WIDTH_SMALL = 300
WIDTH_LARGE = 400

# === UI STRINGS ===
TEXT_READY = "VC is ready."
TEXT_SELECT_LIB = "Select library file"
TEXT_PICK_VER = "Pick version:"
TEXT_EXISTING = "Existing:"
TEXT_HIGHLIGHT = "Highlight"
TEXT_MESH = "Mesh: "
TEXT_VERSION = "Version: "
TEXT_TAG = "Tag: "
TEXT_VERSIONS = "Versions:"
TEXT_NO_VER = "No versions found"

# === REPORT TEMPLATES ===
INFO_LIB_SET = "Lib set: {}"
INFO_SAVED = "Saved {} {}"
INFO_HIGHLIGHTED = "Highlighted {} {}"
INFO_TAG_SET = "Tag set: {}"
INFO_VER_LIST = "Mesh '{}' versions: {}"
INFO_NO_VER = "Mesh '{}' has no versions"

# === ERROR MESSAGES ===
ERR_NO_OBJ = "No object selected"
ERR_NO_LIB = "No library file set"
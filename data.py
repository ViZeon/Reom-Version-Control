# === ADDON ===
ADDON_NAME = "Reom Version Control"
FIRST_RUN_DELAY = 0.1
AUTO_ENABLE_FLAG = "_AUTO_ENABLED_BY_REOM_EXT"

# === FILE PATHS ===
VERSIONS_FOLDER_NAME = "_versions"
DEFAULT_TAGS = "Character, Prop, Weapon"

# === MESH PROPERTIES ===
PROP_MESH_NAME = "reom_vc_mesh_name"
PROP_MESH_VERSION = "reom_vc_version"
PROP_MESH_LIB_FILE = "reom_vc_lib_file"
PROP_MESH_TAG = "reom_vc_tag"

# === UI: PANELS ===
PANEL_CATEGORY = "Reom"
PANEL_LABEL = "Reom Version Control"
PANEL_ID = "VIEW3D_PT_reom_vc_main"
PANEL_TEXT = "Reom Version Control"

# === UI: PREFERENCES ===
PREF_PROP_LIB_PATH = "lib_path"
PREF_PROP_TAGS = "tags"
PREF_LABEL_LIB_PATH = "Library Path"
PREF_LABEL_TAGS = "Tags (comma-separated)"

# === UI: OPERATORS ===
OP_STARTUP_ID = "reom_vc.startup"
OP_STARTUP_LABEL = "Reom Version Control"
OP_STARTUP_TEXT = "Version Control is ready."

OP_TEST_SCAN_ID = "reom_vc.test_scan"
OP_TEST_SCAN_LABEL = "Test Version Scan"

OP_SAVE_ID = "reom_vc.save"
OP_SAVE_LABEL = "Save Version"

OP_SETUP_LIB_FILE_ID = "reom_vc.setup_lib_file"
OP_SETUP_LIB_FILE_LABEL = "Setup Library File"
OP_SETUP_LIB_FILE_TEXT = "Select library file for this mesh"

OP_HIGHLIGHT_ID = "reom_vc.highlight"
OP_HIGHLIGHT_LABEL = "Highlight Version"

OP_SET_TAG_ID = "reom_vc.set_tag"
OP_SET_TAG_LABEL = "Set Tag"

# === UI: TEXTS ===
ERROR_NO_OBJECT = "No object selected"
ERROR_NO_LIB_FILE = "No library file set"
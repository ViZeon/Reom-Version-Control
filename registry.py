from .operators import (
    REOM_VC_OT_startup,
    REOM_VC_OT_setup_lib_file,
    REOM_VC_OT_save,
    REOM_VC_OT_highlight,
    REOM_VC_OT_set_tag,
)
from .testing import REOM_VC_OT_test_scan
from .panels import ReomVCPreferences, REOM_VC_PT_main

classes = (
    ReomVCPreferences,
    REOM_VC_OT_startup,
    REOM_VC_OT_setup_lib_file,
    REOM_VC_OT_save,
    REOM_VC_OT_highlight,
    REOM_VC_OT_set_tag,
    REOM_VC_OT_test_scan,
    REOM_VC_PT_main,
)
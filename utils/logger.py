"""Professional logging setup. Writes to Blender's temp directory."""
import logging
import os
import bpy

def get_logger():
    logger = logging.getLogger("ReomVC")
    if not logger.handlers:
        log_path = os.path.join(bpy.app.tempdir, "reom_vc.log")
        handler = logging.FileHandler(log_path, mode='w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
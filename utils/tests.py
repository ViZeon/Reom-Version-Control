"""Automated unit tests for pure logic. Run via the 'Run Reom VC Tests' operator."""
import unittest
import os
import tempfile
import shutil
import sys
import bpy
from .. import functions, wrapper, data
from ..functions import state

class TestVersionMath(unittest.TestCase):
    def test_bump_ver(self):
        self.assertEqual(functions.bump_ver((1, 0, 0)), (1, 0, 1))
        self.assertEqual(functions.bump_ver((2, 5, 9)), (2, 5, 10))

    def test_bump_step(self):
        self.assertEqual(functions.bump_step((1, 0, 5)), (1, 1, 0))
        
    def test_bump_release(self):
        self.assertEqual(functions.bump_release((1, 9, 9)), (2, 0, 0))

    def test_format_ver_ui(self):
        self.assertEqual(functions.format_ver_ui((1, 0, 0)), "v1.0.0")
        self.assertEqual(functions.format_ver_ui((2, 1)), "v2.1.0")

class TestFilePaths(unittest.TestCase):
    def test_get_version_path_per_current(self):
        path = functions.get_version_path("Cube", (1, 0, 0), "/tmp", data.MODE_VER)
        self.assertTrue(path.endswith("Cube_1_0_0.blend"))
        
    def test_get_version_path_per_sub(self):
        path = functions.get_version_path("Cube", (1, 0, 5), "/tmp", data.MODE_SUB)
        self.assertTrue(path.endswith("Cube_1_0.versions.blend"))
        
    def test_get_version_path_per_release(self):
        path = functions.get_version_path("Cube", (2, 1, 3), "/tmp", data.MODE_RELEASE)
        self.assertTrue(path.endswith("Cube_2.versions.blend"))

class TestSafetyGateway(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.tmpdir, "test.blend")
        with open(self.test_file, 'w') as f: f.write("dummy")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_mode_safe(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_SAFE)
        self.assertEqual(safe_path, os.path.join(self.tmpdir, "test_1.blend"))

    def test_mode_replace(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_REPLACE)
        self.assertEqual(safe_path, self.test_file)
        self.assertFalse(os.path.exists(self.test_file))

    def test_mode_backup(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_BACKUP)
        self.assertEqual(safe_path, self.test_file)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "test.blend.bak1")))

class TestStorageAndPacking(unittest.TestCase):
    """Integration tests that actually use Blender's file I/O."""
    
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.obj = bpy.data.objects.new("TestCube", bpy.data.meshes.new("TestCubeMesh"))
        bpy.context.collection.objects.link(self.obj)
        functions.set_name(self.obj, "TestCube")
        functions.set_lib(self.obj, os.path.join(self.tmpdir, "TestCube.blend"))
        
    def tearDown(self):
        if self.obj.name in bpy.data.objects:
            bpy.data.objects.remove(self.obj, do_unlink=True)
        if "TestCubeMesh" in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes["TestCubeMesh"])
            
        for ob in list(bpy.data.objects):
            if ob.name.startswith("TestCube_"):
                bpy.data.objects.remove(ob, do_unlink=True)
                
        shutil.rmtree(self.tmpdir)

    def test_per_current_mode(self):
        # Mock the storage mode dynamically in the state module
        orig_mode = state.get_storage_mode
        state.get_storage_mode = lambda: data.MODE_VER
        try:
            functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
            functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
            
            vers = functions.scan_versions("TestCube", self.tmpdir)
            self.assertEqual(len(vers), 2)
            self.assertTrue(os.path.exists(os.path.join(self.tmpdir, data.V_DIR, "TestCube", "TestCube_1_0_0.blend")))
            self.assertTrue(os.path.exists(os.path.join(self.tmpdir, data.V_DIR, "TestCube", "TestCube_1_0_1.blend")))
        finally:
            state.get_storage_mode = orig_mode

    def test_per_sub_mode(self):
        # Mock the storage mode dynamically in the state module
        orig_mode = state.get_storage_mode
        state.get_storage_mode = lambda: data.MODE_SUB
        try:
            functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
            functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
            
            vers = functions.scan_versions("TestCube", self.tmpdir)
            self.assertEqual(len(vers), 2)
            
            packed_path = os.path.join(self.tmpdir, data.V_DIR, "TestCube", "TestCube_1_0.versions.blend")
            self.assertTrue(os.path.exists(packed_path))
            
            with wrapper.load_lib(packed_path) as (df, dt):
                self.assertIn("TestCube_1_0_0", df.objects)
                self.assertIn("TestCube_1_0_1", df.objects)
        finally:
            state.get_storage_mode = orig_mode

def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)
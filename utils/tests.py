"""Comprehensive automated integration and unit tests for Reom VC."""
import unittest
import os
import tempfile
import shutil
import sys
import bpy
from .. import functions, wrapper, data
from ..functions import state

class BaseBlenderTest(unittest.TestCase):
    """Base class that handles safe creation and cleanup of Blender objects and temp dirs."""
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.obj = bpy.data.objects.new("TestCube", bpy.data.meshes.new("TestCubeMesh"))
        bpy.context.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        
        # Mock preferences for testing
        self.orig_mode = state.get_storage_mode
        state.get_storage_mode = lambda: data.MODE_VER
        
    def tearDown(self):
        state.get_storage_mode = self.orig_mode
        
        # Clean up all test objects
        for ob in list(bpy.data.objects):
            if "TestCube" in ob.name:
                wrapper.remove_obj(ob)
                
        # Clean up orphan meshes
        for mesh in list(bpy.data.meshes):
            if "TestCube" in mesh.name and mesh.users == 0:
                bpy.data.meshes.remove(mesh, do_unlink=True)
                
        shutil.rmtree(self.tmpdir, ignore_errors=True)

class TestVersionMath(unittest.TestCase):
    def test_bump_ver(self):
        self.assertEqual(functions.bump_ver((1, 0, 0)), (1, 0, 1))
    def test_bump_step(self):
        self.assertEqual(functions.bump_step((1, 0, 5)), (1, 1, 0))
    def test_bump_release(self):
        self.assertEqual(functions.bump_release((1, 9, 9)), (2, 0, 0))
    def test_format_ver_ui(self):
        self.assertEqual(functions.format_ver_ui((1, 0, 0)), "v1.0.0")
        self.assertEqual(functions.format_ver_ui((2, 1)), "v2.1.0")

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

class TestCategories(BaseBlenderTest):
    def test_category_creation_and_reading(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        
        # Test adding a new category
        cid1 = functions.add_cat(lib_path, "Props")
        self.assertTrue(cid1)
        
        # Verify file formatting
        cat_file = os.path.join(self.tmpdir, data.CATALOG_FILE)
        self.assertTrue(os.path.exists(cat_file))
        with open(cat_file, 'r') as f:
            content = f.read()
            self.assertIn("VERSION 1\n\n", content)
            self.assertIn(f"{cid1}:Props:Props", content)
            
        # Test reading categories
        cats = functions.read_cats(lib_path)
        self.assertIn("Props", cats)
        self.assertEqual(cats["Props"], cid1)
        
        # Test duplicate prevention
        cid2 = functions.add_cat(lib_path, "Props")
        self.assertEqual(cid1, cid2)

class TestCoreActions(BaseBlenderTest):
    def test_setup_lib(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        functions.setup_lib(self.obj, "TestCube", lib_path)
        
        self.assertEqual(state.get_name(self.obj), "TestCube")
        self.assertTrue(state.get_uuid(self.obj))
        self.assertEqual(state.get_lib(self.obj), lib_path)
        self.assertTrue(os.path.exists(lib_path))

    def test_save_and_step_versions(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        functions.setup_lib(self.obj, "TestCube", lib_path)
        
        # Save v0.0.0
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
        self.assertEqual(state.get_ver(self.obj), (0, 0, 0))
        
        # Save v0.0.1
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
        self.assertEqual(state.get_ver(self.obj), (0, 0, 1))
        
        # Step to v0.1.0
        functions.save_version(self.obj, data.ACT_STEP, root=self.tmpdir)
        self.assertEqual(state.get_ver(self.obj), (0, 1, 0))
        
        # Release to v1.0.0
        functions.save_version(self.obj, data.ACT_RELEASE, root=self.tmpdir)
        self.assertEqual(state.get_ver(self.obj), (1, 0, 0))
        
        vers = functions.scan_versions("TestCube", self.tmpdir)
        self.assertEqual(len(vers), 4)
        self.assertIn((0, 1, 0), vers)

    def test_set_main_version(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        functions.setup_lib(self.obj, "TestCube", lib_path)
        
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir) # 0_0_0
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir) # 0_0_1
        
        # Rollback to 0_0_0
        functions.set_main_version(self.obj, "0_0_0", root=self.tmpdir)
        
        # Verify the library file contains the 0_0_0 version
        with wrapper.load_lib(lib_path) as (df, dt):
            self.assertIn("TestCube", df.objects)

class TestEditFlow(BaseBlenderTest):
    def test_enter_and_end_edit(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        functions.setup_lib(self.obj, "TestCube", lib_path)
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir)
        
        # Simulate linking the object
        wrapper.remove_obj(self.obj)
        wrapper.link_obj_from_lib(lib_path, "TestCube")
        linked_obj = bpy.data.objects["TestCube"]
        
        self.assertTrue(wrapper.is_linked(linked_obj))
        
        # Enter Edit
        functions.enter_edit(linked_obj)
        self.assertFalse(wrapper.is_linked(linked_obj))
        
        # End Edit
        functions.end_edit(linked_obj)
        final_obj = bpy.data.objects["TestCube"]
        self.assertTrue(wrapper.is_linked(final_obj))

class TestMigration(BaseBlenderTest):
    def test_migration_ver_to_sub(self):
        lib_path = os.path.join(self.tmpdir, "TestCube.blend")
        functions.setup_lib(self.obj, "TestCube", lib_path)
        
        # Create 3 versions in MODE_VER
        state.get_storage_mode = lambda: data.MODE_VER
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir) # 0_0_0
        functions.save_version(self.obj, data.ACT_SAVE, root=self.tmpdir) # 0_0_1
        functions.save_version(self.obj, data.ACT_STEP, root=self.tmpdir) # 0_1_0
        
        # Migrate to MODE_SUB
        functions.migrate_all_versions(self.tmpdir, data.MODE_SUB)
        
        vdir = os.path.join(self.tmpdir, data.V_DIR, "TestCube")
        
        # Check that individual files are gone (except backups)
        self.assertFalse(os.path.exists(os.path.join(vdir, "TestCube_0_0_0.blend")))
        
        # Check that packed files exist
        packed_0_0 = os.path.join(vdir, "TestCube_0_0.versions.blend")
        packed_0_1 = os.path.join(vdir, "TestCube_0_1.versions.blend")
        self.assertTrue(os.path.exists(packed_0_0))
        self.assertTrue(os.path.exists(packed_0_1))
        
        # Verify contents of packed file
        with wrapper.load_lib(packed_0_0) as (df, dt):
            self.assertIn("TestCube_0_0_0", df.objects)
            self.assertIn("TestCube_0_0_1", df.objects)

def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

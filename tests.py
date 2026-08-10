"""Automated unit tests for pure logic. Run via the 'Run Reom VC Tests' operator."""
import unittest
import os
import tempfile
from . import functions, data

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
        self.assertEqual(functions.format_ver_ui((2, 1)), "v2.1.0") # Tests padding fix

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

    def test_mode_safe(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_SAFE)
        self.assertEqual(safe_path, os.path.join(self.tmpdir, "test_1.blend"))

    def test_mode_replace(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_REPLACE)
        self.assertEqual(safe_path, self.test_file)
        self.assertFalse(os.path.exists(self.test_file)) # Should be deleted

    def test_mode_backup(self):
        safe_path = functions._resolve_safety(self.test_file, data.MODE_BACKUP)
        self.assertEqual(safe_path, self.test_file)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "test.blend.bak1")))

def run_tests():
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)
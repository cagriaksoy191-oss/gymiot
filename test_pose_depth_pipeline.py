"""Tests for pose_depth_pipeline module.

Verifies that:
- The module can be imported safely without loading heavy models.
- `init_models` function exists and is callable.
- Module-level globals are None before init_models() is called.
- `percentile_range` and `within` utility functions work correctly.

Heavy external packages (cv2, mediapipe, torch, numpy) are mocked so
the tests run in any environment without those libraries installed.
"""
import math
import sys
import types
import unittest
from unittest.mock import MagicMock


def _build_mock_modules():
    """Create stub modules for all heavy dependencies."""
    # numpy stub
    np_mod = MagicMock(name="numpy")
    np_mod.array = lambda vals, dtype=None: list(vals)
    np_mod.percentile = lambda arr, q: sorted(arr)[min(int(len(arr) * q / 100), len(arr) - 1)]
    sys.modules.setdefault("numpy", np_mod)

    # cv2 stub
    sys.modules.setdefault("cv2", MagicMock(name="cv2"))

    # mediapipe stub
    mp_mod = MagicMock(name="mediapipe")
    sys.modules.setdefault("mediapipe", mp_mod)

    # torch stub
    torch_mod = MagicMock(name="torch")
    torch_mod.cuda.is_available.return_value = False
    sys.modules.setdefault("torch", torch_mod)


_build_mock_modules()


def _fresh_import():
    """Remove any cached module and re-import pose_depth_pipeline."""
    sys.modules.pop("pose_depth_pipeline", None)
    import importlib
    return importlib.import_module("pose_depth_pipeline")


class TestSafeImport(unittest.TestCase):
    """Module must be importable without triggering model loading."""

    def setUp(self):
        sys.modules.pop("pose_depth_pipeline", None)

    def test_import_does_not_raise(self):
        """Importing the module must not raise any exception."""
        mod = _fresh_import()
        self.assertIsNotNone(mod)

    def test_init_models_exists(self):
        """init_models must be a callable defined in the module."""
        mod = _fresh_import()
        self.assertTrue(callable(mod.init_models))

    def test_globals_are_none_before_init(self):
        """Heavy-model globals must be None until init_models() is called."""
        mod = _fresh_import()
        for name in ("device", "midas", "transforms", "mp_pose", "pose", "drawer", "style"):
            self.assertIsNone(
                getattr(mod, name),
                f"Expected '{name}' to be None before init_models(), "
                f"got {getattr(mod, name)!r}",
            )

    def test_args_is_none_on_import(self):
        """ARGS must be None when module is imported (not run as __main__)."""
        mod = _fresh_import()
        self.assertIsNone(mod.ARGS)


class TestUtilityFunctions(unittest.TestCase):
    """Pure utility functions should work without model initialization."""

    @classmethod
    def setUpClass(cls):
        sys.modules.pop("pose_depth_pipeline", None)
        cls.mod = _fresh_import()

    def test_percentile_range_empty(self):
        result = self.mod.percentile_range([])
        self.assertEqual(result, (None, None))

    def test_percentile_range_single(self):
        lo, hi = self.mod.percentile_range([42], lo=10, hi=90)
        self.assertIsNotNone(lo)
        self.assertIsNotNone(hi)

    def test_within_in_range(self):
        self.assertTrue(self.mod.within(5, 1, 10))

    def test_within_below_range(self):
        self.assertFalse(self.mod.within(0, 1, 10))

    def test_within_above_range(self):
        self.assertFalse(self.mod.within(11, 1, 10))

    def test_within_none_bounds(self):
        self.assertTrue(self.mod.within(999, None, None))

    def test_angle_3pts_straight(self):
        a, b, c = (0, 0), (1, 0), (2, 0)
        angle = self.mod.angle_3pts(a, b, c)
        self.assertAlmostEqual(angle, 180.0, delta=0.1)

    def test_angle_3pts_right_angle(self):
        a, b, c = (0, 1), (0, 0), (1, 0)
        angle = self.mod.angle_3pts(a, b, c)
        self.assertAlmostEqual(angle, 90.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()


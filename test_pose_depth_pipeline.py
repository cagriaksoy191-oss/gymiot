import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module under test
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['PIL'] = MagicMock()

# Improved numpy mock that implements basic logic for testing
class MockNumpy:
    def array(self, vals, dtype=None):
        return list(vals) # Return a list to simulate an array for simplicity in our mock logic

    def percentile(self, arr, q):
        # Very simplified percentile calculation for testing purposes
        if not arr:
            return None
        arr_sorted = sorted(arr)
        if isinstance(q, (list, tuple)):
            results = []
            for qi in q:
                index = (qi / 100.0) * (len(arr_sorted) - 1)
                results.append(arr_sorted[int(index)])
            return results
        else:
            index = (q / 100.0) * (len(arr_sorted) - 1)
            return arr_sorted[int(index)]

mock_np = MockNumpy()
sys.modules['numpy'] = mock_np

from pose_depth_pipeline import percentile_range, within, apply_offset

def test_percentile_range_empty():
    assert percentile_range([]) == (None, None)

def test_percentile_range_values():
    # Test with a simple sequence
    # percentile_range(vals, lo=10, hi=90)
    # For [0, 1, 2, ..., 10], 10th percentile is ~1, 90th is ~9
    vals = list(range(11))
    res_lo, res_hi = percentile_range(vals, lo=10, hi=90)

    assert res_lo == 1.0
    assert res_hi == 9.0
    assert isinstance(res_lo, float)
    assert isinstance(res_hi, float)

def test_within():
    assert within(5, 1, 10) is True
    assert within(0, 1, 10) is False
    assert within(11, 1, 10) is False
    assert within(1, 1, 10) is True
    assert within(10, 1, 10) is True

def test_within_none_boundaries():
    assert within(5, None, 10) is True
    assert within(15, None, 10) is False
    assert within(5, 1, None) is True
    assert within(0, 1, None) is False
    assert within(5, None, None) is True

def test_apply_offset_shoulders():
    with patch.dict('pose_depth_pipeline.CALIB', {"shoulder_offset_xy": [10, 20], "elbow_offset_xy": [0, 0]}):
        # 11: L-shoulder, 12: R-shoulder
        assert apply_offset(11, 100, 100) == (110, 120)
        assert apply_offset(12, 50, 50) == (60, 70)

def test_apply_offset_elbows():
    with patch.dict('pose_depth_pipeline.CALIB', {"shoulder_offset_xy": [0, 0], "elbow_offset_xy": [5, -5]}):
        # 13: L-elbow, 14: R-elbow
        assert apply_offset(13, 100, 100) == (105, 95)
        assert apply_offset(14, 50, 50) == (55, 45)

def test_apply_offset_none():
    with patch.dict('pose_depth_pipeline.CALIB', {"shoulder_offset_xy": [10, 20], "elbow_offset_xy": [5, 5]}):
        # Other indices should not have offset
        assert apply_offset(0, 100, 100) == (100, 100)
        assert apply_offset(23, 100, 100) == (100, 100)

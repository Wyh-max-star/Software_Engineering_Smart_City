"""Unit tests for the pure helpers in ``ecology_common``.

Test design follows the lecture material: equivalence partitioning and boundary
value analysis for the value-clamping helpers, plus white-box path coverage for
the geometric helpers (degenerate segments, wrap-around path sampling, etc.).
"""

import math
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402


ecology_common = load_module("ecology_common", "iCity/smart_city/ecology_common.py")


class ClampBoundaryTests(unittest.TestCase):
    """Boundary value analysis for ``clamp`` (range [0, 10])."""

    def test_inside_range_is_unchanged(self):
        self.assertEqual(ecology_common.clamp(5.0, 0.0, 10.0), 5.0)

    def test_on_lower_boundary(self):
        self.assertEqual(ecology_common.clamp(0.0, 0.0, 10.0), 0.0)

    def test_on_upper_boundary(self):
        self.assertEqual(ecology_common.clamp(10.0, 0.0, 10.0), 10.0)

    def test_just_below_lower_boundary(self):
        self.assertEqual(ecology_common.clamp(-0.01, 0.0, 10.0), 0.0)

    def test_just_above_upper_boundary(self):
        self.assertEqual(ecology_common.clamp(10.01, 0.0, 10.0), 10.0)


class SmoothstepTests(unittest.TestCase):
    def test_equal_edges_returns_zero(self):
        self.assertEqual(ecology_common.smoothstep(3.0, 3.0, 5.0), 0.0)

    def test_below_low_edge_clamped_to_zero(self):
        self.assertEqual(ecology_common.smoothstep(0.0, 10.0, -2.0), 0.0)

    def test_above_high_edge_clamped_to_one(self):
        self.assertEqual(ecology_common.smoothstep(0.0, 10.0, 12.0), 1.0)

    def test_midpoint_is_half(self):
        self.assertAlmostEqual(ecology_common.smoothstep(0.0, 10.0, 5.0), 0.5)


class RotationTests(unittest.TestCase):
    def test_rotate_quarter_turn(self):
        rotated = ecology_common.rotate_2d(Vector((1.0, 0.0)), math.pi / 2)
        self.assertAlmostEqual(rotated.x, 0.0)
        self.assertAlmostEqual(rotated.y, 1.0)

    def test_inverse_round_trips(self):
        original = Vector((2.0, -3.0))
        rotated = ecology_common.rotate_2d(original, 0.9)
        restored = ecology_common.rotate_2d_inverse(rotated, 0.9)
        self.assertAlmostEqual(restored.x, original.x)
        self.assertAlmostEqual(restored.y, original.y)


class DistanceTests(unittest.TestCase):
    def test_point_above_segment_midpoint(self):
        distance = ecology_common.distance_to_segment_2d(
            Vector((0.0, 1.0)), Vector((-1.0, 0.0)), Vector((1.0, 0.0))
        )
        self.assertAlmostEqual(distance, 1.0)

    def test_degenerate_segment_falls_back_to_point_distance(self):
        distance = ecology_common.distance_to_segment_2d(
            Vector((3.0, 4.0)), Vector((0.0, 0.0)), Vector((0.0, 0.0))
        )
        self.assertAlmostEqual(distance, 5.0)

    def test_polyline_returns_minimum_segment_distance(self):
        polyline = [Vector((-1.0, 0.0)), Vector((1.0, 0.0)), Vector((1.0, 2.0))]
        distance = ecology_common.distance_to_polyline(Vector((0.0, 1.0)), polyline)
        self.assertAlmostEqual(distance, 1.0)


class EllipsePointsTests(unittest.TestCase):
    def test_point_count_and_height(self):
        points = ecology_common.ellipse_points(Vector((0.0, 0.0)), 2.0, 1.0, 0.0, 4, 5.0)
        self.assertEqual(len(points), 4)
        self.assertTrue(all(math.isclose(point.z, 5.0) for point in points))

    def test_first_point_lies_on_major_axis(self):
        points = ecology_common.ellipse_points(Vector((0.0, 0.0)), 2.0, 1.0, 0.0, 4, 0.0)
        self.assertAlmostEqual(points[0].x, 2.0)
        self.assertAlmostEqual(points[0].y, 0.0)


class SamplePathPointTests(unittest.TestCase):
    def test_empty_path_returns_origin(self):
        point = ecology_common._sample_path_point([], 0.3)
        self.assertEqual((point.x, point.y, point.z), (0.0, 0.0, 0.0))

    def test_offset_zero_returns_first_point(self):
        path = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]
        point = ecology_common._sample_path_point(path, 0.0)
        self.assertAlmostEqual(point.x, 0.0)

    def test_offset_interpolates_between_points(self):
        path = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]
        point = ecology_common._sample_path_point(path, 0.25)
        self.assertAlmostEqual(point.x, 5.0)

    def test_offset_wraps_around(self):
        path = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]
        wrapped = ecology_common._sample_path_point(path, 1.0)
        self.assertAlmostEqual(wrapped.x, 0.0)


def _layout_settings(seed):
    return types.SimpleNamespace(
        seed=seed,
        terrain_margin=55.0,
        lake_radius=16.0,
        lake_depth=7.5,
        river_width=7.0,
        traffic_loop_radius_x=14.0,
        traffic_loop_radius_y=8.5,
        road_width=3.8,
    )


class ComputeLayoutInvariantTests(unittest.TestCase):
    """Across many seeds the water/traffic features must stay clear of the city.

    This mirrors the orthogonal-array idea from the lecture: sample several
    discrete seeds (which drive the layout rotation) rather than exhaustively.
    """

    def test_lake_and_traffic_stay_outside_city_for_many_seeds(self):
        for seed in (0, 1, 7, 12, 99, 180, 359, 360, 999999):
            with self.subTest(seed=seed):
                settings = _layout_settings(seed)
                layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)

                lake_clearance = layout["lake_center"].length - max(
                    layout["lake_radius_x"], layout["lake_radius_y"]
                )
                self.assertGreaterEqual(lake_clearance, 30.0)

                traffic_clearance = (
                    layout["traffic_center"].length
                    - max(settings.traffic_loop_radius_x, settings.traffic_loop_radius_y)
                    - settings.road_width * 0.5
                )
                self.assertGreaterEqual(traffic_clearance, 30.0)

    def test_terrain_radius_extends_city_by_margin(self):
        settings = _layout_settings(12)
        layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)
        self.assertAlmostEqual(layout["terrain_radius"], 30.0 + settings.terrain_margin)


if __name__ == "__main__":
    unittest.main()

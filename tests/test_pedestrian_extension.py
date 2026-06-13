"""Unit tests for sidewalk planning helpers in ``pedestrian_extension``."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402


pedestrian_extension = load_module(
    "pedestrian_extension", "iCity/smart_city/pedestrian_extension.py"
)
SIDEWALK_LANES = pedestrian_extension.SIDEWALK_LANES


class NormalizeBandTests(unittest.TestCase):
    def test_swaps_when_far_is_smaller(self):
        near, far = pedestrian_extension.normalize_band(8.0, 4.0)
        self.assertEqual(near, 4.0)
        self.assertEqual(far, 8.0)

    def test_negative_inputs_become_zero(self):
        near, far = pedestrian_extension.normalize_band(-2.0, -1.0)
        self.assertEqual((near, far), (0.0, 0.0))


class BandDistancesTests(unittest.TestCase):
    def test_single_lane_returns_midpoint(self):
        distances = pedestrian_extension.band_distances(4.0, 8.0, lanes=1)
        self.assertEqual(distances, [6.0])

    def test_multiple_lanes_span_the_band(self):
        distances = pedestrian_extension.band_distances(2.0, 8.0, lanes=3)
        self.assertEqual(len(distances), 3)
        self.assertAlmostEqual(distances[0], 2.0)
        self.assertAlmostEqual(distances[-1], 8.0)


class CornerVertexFlagsTests(unittest.TestCase):
    def test_straight_chain_has_no_corners(self):
        chain = [Vector((index * 5.0, 0.0, 0.0)) for index in range(6)]
        flags = pedestrian_extension.corner_vertex_flags(chain)
        self.assertFalse(any(flags))

    def test_sharp_turn_is_flagged(self):
        chain = [
            Vector((0.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
            Vector((20.0, 10.0, 0.0)),
        ]
        flags = pedestrian_extension.corner_vertex_flags(chain)
        self.assertTrue(flags[2])

    def test_endpoints_are_never_flagged(self):
        chain = [
            Vector((0.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
        ]
        flags = pedestrian_extension.corner_vertex_flags(chain)
        self.assertFalse(flags[0])
        self.assertFalse(flags[-1])


class PlanSidewalkRoutesTests(unittest.TestCase):
    def test_builds_routes_for_both_sides_and_lanes(self):
        chain = [Vector((index * 4.0, 0.0, 0.0)) for index in range(8)]
        routes = pedestrian_extension.plan_sidewalk_routes([chain], 3.0, 6.0, z_lift=0.05)
        expected = 2 * SIDEWALK_LANES
        self.assertEqual(len(routes), expected)

    def test_negative_side_reverses_motion(self):
        chain = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0)), Vector((20.0, 0.0, 0.0))]
        routes = pedestrian_extension.plan_sidewalk_routes([chain], 2.0, 4.0, z_lift=0.0)
        positive = next(route for route in routes if route["side"] > 0.0)
        negative = next(route for route in routes if route["side"] < 0.0)
        self.assertNotEqual(
            [point.x for point in positive["points"][:3]],
            [point.x for point in negative["points"][:3]],
        )

    def test_short_chain_is_skipped(self):
        routes = pedestrian_extension.plan_sidewalk_routes([[Vector((0.0, 0.0, 0.0))]], 2.0, 4.0, 0.0)
        self.assertEqual(routes, [])


class PlanIdleSpotsTests(unittest.TestCase):
    def test_respects_idle_count_cap(self):
        chain = [Vector((index * 5.0, 0.0, 0.0)) for index in range(10)]
        spots = pedestrian_extension.plan_idle_spots([chain], 2.0, 6.0, idle_count=3, seed=7, z_lift=0.05)
        self.assertLessEqual(len(spots), 3)

    def test_zero_idle_count_returns_empty(self):
        chain = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]
        self.assertEqual(
            pedestrian_extension.plan_idle_spots([chain], 2.0, 6.0, idle_count=0, seed=1, z_lift=0.0),
            [],
        )

    def test_seed_is_deterministic(self):
        chain = [Vector((index * 4.0, 0.0, 0.0)) for index in range(12)]
        first = pedestrian_extension.plan_idle_spots([chain], 2.0, 6.0, idle_count=4, seed=42, z_lift=0.0)
        second = pedestrian_extension.plan_idle_spots([chain], 2.0, 6.0, idle_count=4, seed=42, z_lift=0.0)
        self.assertEqual(
            [(spot[0].x, spot[0].y) for spot in first],
            [(spot[0].x, spot[0].y) for spot in second],
        )


class FallbackPlannerTests(unittest.TestCase):
    def test_fallback_loop_routes_cover_both_sides(self):
        routes = pedestrian_extension.plan_fallback_loop_routes(
            Vector((0.0, 0.0, 0.0)), 30.0, 0.0, 4.0, 8.0, z_lift=0.05
        )
        self.assertEqual(len(routes), 2)
        sides = {route["side"] for route in routes}
        self.assertEqual(sides, {1.0, -1.0})

    def test_fallback_idle_spots_face_inward(self):
        spots = pedestrian_extension.plan_fallback_idle_spots(
            Vector((0.0, 0.0, 0.0)), 30.0, 0.0, 4.0, 8.0, idle_count=4, z_lift=0.0
        )
        self.assertEqual(len(spots), 4)
        for position, _facing in spots:
            self.assertGreaterEqual(position.length, 29.0)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for pure helpers in ``traffic_extension``.

Covers road-chain extraction, motion-point conversion, layout bands, and the
vehicle type sequence. These run without Blender via ``blender_test_utils``.
"""

import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402
from test_markers import white_box  # noqa: E402


traffic_extension = load_module(
    "traffic_extension", "iCity/smart_city/traffic_extension.py"
)


def _traffic_settings(**overrides):
    defaults = dict(
        animation_start=1,
        animation_end=100,
        car_count=6,
        taxi_count=2,
        bus_count=1,
        traffic_outer_offset=10.0,
        traffic_lane_gap=2.4,
        pedestrian_outer_gap=3.2,
        pedestrian_lane_gap=1.6,
        road_width=3.8,
        walkway_width=2.4,
    )
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


class ClampTests(unittest.TestCase):
    def test_clamp_boundaries(self):
        self.assertEqual(traffic_extension._clamp(-1.0, 0.0, 5.0), 0.0)
        self.assertEqual(traffic_extension._clamp(3.0, 0.0, 5.0), 3.0)
        self.assertEqual(traffic_extension._clamp(9.0, 0.0, 5.0), 5.0)


class ExtractRoadEdgeChainsTests(unittest.TestCase):
    def test_empty_when_all_edges_deleted(self):
        vertices = [Vector((0, 0, 0)), Vector((10, 0, 0))]
        edges = [(0, 1)]
        chains = traffic_extension.extract_road_edge_chains(vertices, edges, [True])
        self.assertEqual(chains, [])

    def test_single_open_chain(self):
        vertices = [
            Vector((0, 0, 0)),
            Vector((10, 0, 0)),
            Vector((10, 10, 0)),
        ]
        edges = [(0, 1), (1, 2)]
        chains = traffic_extension.extract_road_edge_chains(vertices, edges, [False, False])
        self.assertEqual(len(chains), 1)
        self.assertEqual(len(chains[0]), 3)

    def test_closed_loop_chain(self):
        vertices = [
            Vector((0, 0, 0)),
            Vector((10, 0, 0)),
            Vector((10, 10, 0)),
            Vector((0, 10, 0)),
        ]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        chains = traffic_extension.extract_road_edge_chains(
            vertices, edges, [False, False, False, False]
        )
        self.assertGreaterEqual(len(chains), 1)
        self.assertGreaterEqual(len(chains[0]), 4)


class VehicleMotionPointsTests(unittest.TestCase):
    def test_open_chain_doubles_back(self):
        chain = [Vector((0, 0, 0)), Vector((5, 0, 0)), Vector((10, 0, 0))]
        points = traffic_extension.vehicle_motion_points_from_chain(chain)
        self.assertGreater(len(points), len(chain))

    def test_closed_loop_drops_duplicate_end(self):
        chain = [
            Vector((0, 0, 0)),
            Vector((5, 0, 0)),
            Vector((0, 0, 0)),
        ]
        points = traffic_extension.vehicle_motion_points_from_chain(chain)
        self.assertEqual(len(points), 2)


class VehicleTypeSequenceTests(unittest.TestCase):
    def test_respects_counts(self):
        settings = _traffic_settings(car_count=3, taxi_count=2, bus_count=1)
        sequence = traffic_extension.vehicle_type_sequence(settings)
        self.assertEqual(sequence.count("BUS"), 1)
        self.assertEqual(sequence.count("TAXI"), 2)
        self.assertEqual(sequence.count("CAR"), 3)

    def test_empty_when_all_zero(self):
        settings = _traffic_settings(car_count=0, taxi_count=0, bus_count=0)
        self.assertEqual(traffic_extension.vehicle_type_sequence(settings), [])


class ComputeTrafficLayoutTests(unittest.TestCase):
    def test_lanes_expand_outward_from_city(self):
        settings = _traffic_settings()
        layout = traffic_extension.compute_traffic_layout(
            Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings
        )
        self.assertGreater(
            layout["vehicle_lane_outer_x"], layout["vehicle_lane_inner_x"]
        )
        self.assertGreater(
            layout["pedestrian_lane_outer_x"], layout["pedestrian_lane_inner_x"]
        )
        self.assertGreater(
            layout["pedestrian_lane_inner_x"], layout["vehicle_lane_outer_x"]
        )

    def test_uses_minimum_offsets_when_settings_are_small(self):
        settings = _traffic_settings(
            traffic_outer_offset=1.0,
            traffic_lane_gap=0.5,
            pedestrian_outer_gap=0.5,
            pedestrian_lane_gap=0.5,
        )
        layout = traffic_extension.compute_traffic_layout(
            Vector((0.0, 0.0, 0.0)), 20.0, 1.0, settings
        )
        self.assertAlmostEqual(layout["center"].z, 1.0)
        self.assertGreaterEqual(layout["vehicle_lane_inner_x"], 24.0)


class PrepareVehiclePathTests(unittest.TestCase):
    def test_lane_offset_shifts_path_sideways(self):
        chain = [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0)), Vector((20.0, 0.0, 0.0))]
        centred = traffic_extension.prepare_vehicle_path(
            chain,
            lane_offset=0.0,
            sample_spacing=2.0,
            smoothing_iterations=0,
            corner_rounding_radius=0.0,
            corner_rounding_segments=2,
            corner_max_angle_deg=30.0,
        )
        offset = traffic_extension.prepare_vehicle_path(
            chain,
            lane_offset=2.0,
            sample_spacing=2.0,
            smoothing_iterations=0,
            corner_rounding_radius=0.0,
            corner_rounding_segments=2,
            corner_max_angle_deg=30.0,
        )
        self.assertNotAlmostEqual(centred[1].y, offset[1].y)

    def test_resampling_increases_point_count(self):
        chain = [Vector((0.0, 0.0, 0.0)), Vector((40.0, 0.0, 0.0)), Vector((40.0, 20.0, 0.0))]
        prepared = traffic_extension.prepare_vehicle_path(
            chain,
            lane_offset=0.0,
            sample_spacing=2.0,
            smoothing_iterations=0,
            corner_rounding_radius=0.0,
            corner_rounding_segments=2,
            corner_max_angle_deg=30.0,
        )
        self.assertGreaterEqual(len(prepared), 5)


class BundledVehicleProfileTests(unittest.TestCase):
    def test_each_vehicle_type_has_asset_id(self):
        for vehicle_type in ("CAR", "TAXI", "BUS"):
            asset_id = traffic_extension.bundled_vehicle_asset_id(vehicle_type)
            self.assertIsNotNone(asset_id)

    def test_profile_contains_path_tuning_keys(self):
        profile = traffic_extension.bundled_vehicle_profile("CAR")
        for key in ("lane_offset", "sample_spacing", "smoothing_iterations"):
            self.assertIn(key, profile)
            self.assertIsInstance(profile[key], (int, float))


class VehicleMeshTests(unittest.TestCase):
    def test_each_vehicle_type_produces_valid_mesh(self):
        for vehicle_type in ("CAR", "TAXI", "BUS"):
            vertices, faces = traffic_extension._vehicle_mesh(vehicle_type, 1.0)
            self.assertGreater(len(vertices), 0)
            for face in faces:
                for index in face:
                    self.assertTrue(0 <= index < len(vertices))


def _plan(sequence, **kwargs):
    defaults = dict(
        passenger_route_count=2,
        bus_route_count=1,
        seed=12,
        randomness=0.35,
        min_phase_gap=0.08,
        scale_jitter=0.06,
    )
    defaults.update(kwargs)
    return traffic_extension.plan_vehicle_assignments(sequence, **defaults)


@white_box
class VehicleRandomizationTests(unittest.TestCase):
    def test_route_cycle_unshuffled_when_randomness_zero(self):
        import random

        rng = random.Random(7)
        cycle = traffic_extension._randomized_route_cycle(4, rng, randomness=0.0)
        self.assertEqual(cycle, [0, 1, 2, 3])

    def test_route_cycle_shuffled_when_randomness_positive(self):
        import random

        rng = random.Random(7)
        cycle = traffic_extension._randomized_route_cycle(4, rng, randomness=1.0)
        self.assertEqual(sorted(cycle), [0, 1, 2, 3])
        self.assertNotEqual(cycle, [0, 1, 2, 3])

    def test_same_seed_produces_identical_assignments(self):
        sequence = ["BUS", "CAR", "TAXI", "CAR", "CAR"]
        first = _plan(sequence, seed=42, randomness=0.6)
        second = _plan(sequence, seed=42, randomness=0.6)
        self.assertEqual(first, second)

    def test_different_seed_changes_distribution(self):
        sequence = ["CAR", "CAR", "CAR", "TAXI", "TAXI"]
        low = _plan(sequence, seed=1, randomness=0.9)
        high = _plan(sequence, seed=999, randomness=0.9)
        fingerprint = lambda rows: [
            (row["route_kind"], row["route_index"], row["phase_start"], row["scale_factor"])
            for row in rows
        ]
        self.assertNotEqual(fingerprint(low), fingerprint(high))

    def test_zero_randomness_keeps_unit_scale_and_ordered_routes(self):
        sequence = ["CAR", "CAR", "TAXI"]
        assignments = _plan(sequence, seed=5, randomness=0.0)
        self.assertEqual(len(assignments), 3)
        for row in assignments:
            self.assertEqual(row["scale_factor"], 1.0)
            self.assertIn(row["route_kind"], ("passenger", "bus"))
            self.assertGreaterEqual(row["route_index"], 0)

    def test_assignments_cover_every_vehicle_in_sequence(self):
        sequence = traffic_extension.vehicle_type_sequence(
            _traffic_settings(car_count=4, taxi_count=2, bus_count=1)
        )
        assignments = _plan(sequence, seed=12, randomness=0.35)
        self.assertEqual(len(assignments), len(sequence))
        self.assertEqual(
            [row["vehicle_type"] for row in assignments],
            sequence,
        )

    def test_multiple_vehicles_on_same_route_get_distinct_phases(self):
        sequence = ["CAR", "CAR", "CAR"]
        assignments = _plan(
            sequence,
            passenger_route_count=1,
            bus_route_count=0,
            seed=3,
            randomness=0.5,
        )
        phases = [row["phase_start"] for row in assignments]
        self.assertEqual(len(phases), 3)
        self.assertEqual(len(set(phases)), 3)

    def test_generate_traffic_reads_random_settings_from_context(self):
        source = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "traffic_extension.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("traffic_random_seed", text)
        self.assertIn("traffic_randomness", text)
        self.assertIn("plan_vehicle_assignments(", text)


if __name__ == "__main__":
    unittest.main()

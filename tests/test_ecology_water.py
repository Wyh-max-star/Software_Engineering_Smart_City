"""Unit tests for plot-based terrain and water helpers in ``ecology_water``.

``mathutils.noise`` is stubbed to zero in ``blender_test_utils``, so height-field
tests assert domain invariants (lake carve, river channel, edge falloff) rather
than exact noise amplitudes.
"""

import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402


ecology_common = load_module("ecology_common", "iCity/smart_city/ecology_common.py")
ecology_water = load_module("ecology_water", "iCity/smart_city/ecology_water.py")


def make_plot_settings(**overrides):
    defaults = dict(
        seed=3,
        ecology_plot_mode="LAKE_RING",
        plot_shape="RECTANGLE",
        plot_width=80.0,
        plot_depth=60.0,
        plot_offset=12.0,
        lake_radius=16.0,
        lake_depth=7.5,
        river_source_width=6.0,
        river_mouth_width=14.0,
        river_depth=3.0,
        river_meander=0.45,
        river_bend_count=3,
        mountain_height=10.0,
        noise_strength=2.0,
        mountain_peak_count=4,
    )
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def build_layout(settings, plot_index=1, **overrides):
    base = Vector((0.0, 0.0, 0.0))
    layout = ecology_water.build_plot_layout(plot_index, base, settings)
    layout.update(overrides)
    return layout


class PlotLayoutTests(unittest.TestCase):
    def test_lake_ring_enables_lake_not_river(self):
        layout = build_layout(make_plot_settings(ecology_plot_mode="LAKE_RING"))
        self.assertTrue(layout["has_lake"])
        self.assertFalse(layout["has_river"])

    def test_river_valley_enables_river_not_lake(self):
        layout = build_layout(make_plot_settings(ecology_plot_mode="RIVER_VALLEY"))
        self.assertFalse(layout["has_lake"])
        self.assertTrue(layout["has_river"])

    def test_meander_amplitude_is_clamped_inside_plot(self):
        settings = make_plot_settings(
            ecology_plot_mode="RIVER_VALLEY",
            plot_depth=40.0,
            river_source_width=8.0,
            river_mouth_width=18.0,
            river_meander=2.0,
        )
        layout = build_layout(settings)
        widest_half = max(layout["river_source_half"], layout["river_mouth_half"])
        self.assertLessEqual(layout["river_meander_amp"], layout["half_y"] - widest_half)

    def test_peak_specs_generated_for_each_mode(self):
        for mode in ("LAKE_RING", "RIVER_VALLEY", "MOUNTAIN_ONLY"):
            layout = build_layout(make_plot_settings(ecology_plot_mode=mode))
            self.assertGreaterEqual(len(layout["peak_specs"]), 2)


class PlotShapeTests(unittest.TestCase):
    def setUp(self):
        self.layout = build_layout(make_plot_settings(plot_shape="RECTANGLE"))

    def test_center_is_inside_rectangle(self):
        self.assertTrue(ecology_water.point_inside_plot_shape(Vector((0.0, 0.0)), self.layout))

    def test_outside_corner_is_outside_rectangle(self):
        half_x = self.layout["half_x"]
        half_y = self.layout["half_y"]
        outside = Vector((half_x + 1.0, half_y + 1.0))
        self.assertFalse(ecology_water.point_inside_plot_shape(outside, self.layout))

    def test_edge_falloff_is_one_at_center(self):
        self.assertAlmostEqual(ecology_water.edge_falloff(Vector((0.0, 0.0)), self.layout), 1.0)

    def test_edge_falloff_tapers_near_boundary(self):
        edge_point = Vector((self.layout["half_x"] * 0.98, 0.0))
        self.assertLess(ecology_water.edge_falloff(edge_point, self.layout), 0.5)

    def test_ellipse_shape_uses_normalized_distance(self):
        layout = build_layout(make_plot_settings(plot_shape="ELLIPSE"))
        on_boundary = Vector((layout["half_x"], 0.0))
        self.assertTrue(ecology_water.point_inside_plot_shape(on_boundary, layout))
        outside = Vector((layout["half_x"] * 1.05, 0.0))
        self.assertFalse(ecology_water.point_inside_plot_shape(outside, layout))


class RiverGeometryTests(unittest.TestCase):
    def setUp(self):
        self.layout = build_layout(make_plot_settings(ecology_plot_mode="RIVER_VALLEY"))

    def test_progress_runs_source_to_mouth(self):
        half_x = self.layout["half_x"]
        self.assertAlmostEqual(ecology_water.river_progress(-half_x, self.layout), 0.0)
        self.assertAlmostEqual(ecology_water.river_progress(half_x, self.layout), 1.0)

    def test_half_width_widens_toward_mouth(self):
        half_x = self.layout["half_x"]
        source_half = ecology_water.river_half_width(-half_x, self.layout)
        mouth_half = ecology_water.river_half_width(half_x, self.layout)
        self.assertLessEqual(source_half, mouth_half)


class TerrainHeightTests(unittest.TestCase):
    def test_lake_centre_is_below_water_level(self):
        settings = make_plot_settings(ecology_plot_mode="LAKE_RING")
        layout = build_layout(settings)
        height = ecology_water.terrain_height(layout["lake_center"], layout, settings)
        self.assertLessEqual(height, layout["water_level"])

    def test_river_channel_is_carved_below_water_level(self):
        settings = make_plot_settings(ecology_plot_mode="RIVER_VALLEY")
        layout = build_layout(settings)
        channel_point = Vector((0.0, ecology_water.river_center_offset(0.0, layout)))
        height = ecology_water.terrain_height(channel_point, layout, settings)
        self.assertLess(height, layout["water_level"])

    def test_mountain_only_has_positive_relief_at_centre(self):
        settings = make_plot_settings(ecology_plot_mode="MOUNTAIN_ONLY")
        layout = build_layout(settings)
        height = ecology_water.terrain_height(Vector((0.0, 0.0)), layout, settings)
        self.assertGreater(height, 0.0)

    def test_edge_points_fall_off_toward_zero(self):
        settings = make_plot_settings(ecology_plot_mode="MOUNTAIN_ONLY")
        layout = build_layout(settings)
        edge = Vector((layout["half_x"] * 0.99, layout["half_y"] * 0.99))
        centre = Vector((0.0, 0.0))
        self.assertLess(
            ecology_water.terrain_height(edge, layout, settings),
            ecology_water.terrain_height(centre, layout, settings),
        )


class PlotPlacementTests(unittest.TestCase):
    def test_plot_location_sits_outside_city_radius(self):
        settings = make_plot_settings(plot_offset=10.0, plot_width=70.0, plot_depth=50.0)
        location = ecology_water.compute_plot_location(Vector((0.0, 0.0, 0.0)), 30.0, settings, 1)
        self.assertGreater(location.length, 30.0 + settings.plot_offset)


class EllipticalDistanceTests(unittest.TestCase):
    def setUp(self):
        self.layout = build_layout(make_plot_settings())

    def test_distance_is_zero_at_lake_centre(self):
        distance = ecology_water.elliptical_distance(self.layout["lake_center"], self.layout)
        self.assertAlmostEqual(distance, 0.0)

    def test_distance_is_one_on_lake_boundary(self):
        layout = self.layout
        offset = ecology_common.rotate_2d(
            Vector((layout["lake_radius_x"], 0.0)), layout["lake_rotation"]
        )
        boundary = layout["lake_center"] + offset
        distance = ecology_water.elliptical_distance(boundary, layout)
        self.assertAlmostEqual(distance, 1.0, places=2)


class BoatMeshTests(unittest.TestCase):
    def test_mesh_has_expected_vertex_and_face_counts(self):
        vertices, faces = ecology_water.build_boat_mesh(1.0)
        self.assertEqual(len(vertices), 10)
        self.assertEqual(len(faces), 9)

    def test_scale_is_applied_uniformly(self):
        base_vertices, _ = ecology_water.build_boat_mesh(1.0)
        scaled_vertices, _ = ecology_water.build_boat_mesh(2.0)
        for base, scaled in zip(base_vertices, scaled_vertices):
            for base_axis, scaled_axis in zip(base, scaled):
                self.assertAlmostEqual(scaled_axis, base_axis * 2.0)


if __name__ == "__main__":
    unittest.main()

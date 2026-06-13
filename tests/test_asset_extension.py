"""Unit tests for pure helpers in ``asset_extension`` (all external deps mocked)."""

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402
from test_markers import white_box  # noqa: E402


asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")


def make_streetlight_settings(count):
    return types.SimpleNamespace(
        streetlight_count=count,
        streetlight_offset=7.5,
        streetlight_base_z_offset=0.0,
    )


@white_box
class ClampTests(unittest.TestCase):
    def test_inside_range(self):
        self.assertEqual(asset_extension.clamp(1.0, 0.0, 2.0), 1.0)

    def test_boundaries(self):
        self.assertEqual(asset_extension.clamp(0.0, 0.0, 2.0), 0.0)
        self.assertEqual(asset_extension.clamp(2.0, 0.0, 2.0), 2.0)

    def test_outside_range(self):
        self.assertEqual(asset_extension.clamp(-1.0, 0.0, 2.0), 0.0)
        self.assertEqual(asset_extension.clamp(9.0, 0.0, 2.0), 2.0)


@white_box
class PerimeterPositionsTests(unittest.TestCase):
    def setUp(self):
        self.center = Vector((0.0, 0.0, 0.0))
        self.radius = 30.0

    def test_returns_requested_count(self):
        positions = asset_extension.perimeter_positions(
            self.center, self.radius, make_streetlight_settings(20)
        )
        self.assertEqual(len(positions), 20)

    def test_minimum_valid_count(self):
        positions = asset_extension.perimeter_positions(
            self.center, self.radius, make_streetlight_settings(4)
        )
        self.assertEqual(len(positions), 4)

    def test_zero_count_is_clamped_to_one(self):
        positions = asset_extension.perimeter_positions(
            self.center, self.radius, make_streetlight_settings(0)
        )
        self.assertEqual(len(positions), 1)

    def test_large_count(self):
        positions = asset_extension.perimeter_positions(
            self.center, self.radius, make_streetlight_settings(200)
        )
        self.assertEqual(len(positions), 200)

    def test_positions_lie_on_the_outer_rectangle(self):
        settings = make_streetlight_settings(40)
        lateral_offset = max(settings.streetlight_offset * 0.55, self.radius * 0.10)
        half_x = self.radius + max(settings.streetlight_offset, self.radius * 0.12)
        half_y = max(self.radius * 0.72 + settings.streetlight_offset, self.radius + lateral_offset)
        tolerance = 0.05
        positions = asset_extension.perimeter_positions(self.center, self.radius, settings)
        for location, _rotation in positions:
            on_x_edge = abs(abs(location.x) - half_x) <= tolerance
            on_y_edge = abs(abs(location.y) - half_y) <= tolerance
            within_x = abs(location.x) <= half_x + tolerance
            within_y = abs(location.y) <= half_y + tolerance
            self.assertTrue(
                (on_x_edge and within_y) or (on_y_edge and within_x),
                f"position {location} outside rectangle ({half_x}, {half_y})",
            )

    def test_base_z_offset_is_applied(self):
        settings = make_streetlight_settings(8)
        settings.streetlight_base_z_offset = 1.25
        positions = asset_extension.perimeter_positions(self.center, self.radius, settings)
        for location, _rotation in positions:
            self.assertAlmostEqual(location.z, 1.25)


@white_box
class AppendBoxTests(unittest.TestCase):
    def test_adds_eight_vertices_and_six_faces(self):
        vertices = []
        face_data = []
        asset_extension.append_box(vertices, face_data, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 3)
        self.assertEqual(len(vertices), 8)
        self.assertEqual(len(face_data), 6)

    def test_propagates_material_index_and_offsets_indices(self):
        vertices = [(0.0, 0.0, 0.0)]
        face_data = []
        asset_extension.append_box(vertices, face_data, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 7)
        for face_indices, material_index in face_data:
            self.assertEqual(material_index, 7)
            self.assertTrue(all(index >= 1 for index in face_indices))


@white_box
class PointInCityCoreTests(unittest.TestCase):
    def test_city_centre_is_inside_core(self):
        self.assertTrue(
            asset_extension.point_in_city_core(Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0)), 30.0)
        )

    def test_far_perimeter_point_is_outside_core(self):
        outside = Vector((30.0, 30.0, 0.0))
        self.assertFalse(
            asset_extension.point_in_city_core(outside, Vector((0.0, 0.0, 0.0)), 30.0)
        )


@white_box
class FilteredPerimeterTests(unittest.TestCase):
    def test_filters_positions_away_from_city_interior(self):
        settings = make_streetlight_settings(12)
        filtered = asset_extension.filtered_perimeter_positions(
            Vector((0.0, 0.0, 0.0)), 30.0, settings
        )
        self.assertEqual(len(filtered), 12)
        for location, _rotation in filtered:
            self.assertFalse(
                asset_extension.point_in_city_core(location, Vector((0.0, 0.0, 0.0)), 30.0)
            )


@white_box
class RoadAssetSpecTests(unittest.TestCase):
    def test_known_styles_return_node_specs(self):
        for style in ("STREETLIGHT", "BENCH", "BOLLARD"):
            spec = asset_extension.road_asset_spec_for_style(style)
            self.assertIsNotNone(spec)
            self.assertIn("node_name", spec)

    def test_unknown_style_returns_none(self):
        self.assertIsNone(asset_extension.road_asset_spec_for_style("UNKNOWN_STYLE"))


@white_box
class GetTexturePathTests(unittest.TestCase):
    def test_empty_filename_returns_none(self):
        self.assertIsNone(asset_extension.get_texture_path(""))

    @patch.object(asset_extension, "texture_directories")
    def test_exact_match_is_returned(self, mock_dirs: MagicMock):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "road.jpg").write_text("x", encoding="utf-8")
            mock_dirs.return_value = (directory,)
            path = asset_extension.get_texture_path("road.jpg")
            self.assertIsNotNone(path)
            self.assertEqual(path.name, "road.jpg")
            mock_dirs.assert_called()

    @patch.object(asset_extension, "texture_directories")
    def test_numbered_duplicate_is_matched_via_glob(self, mock_dirs: MagicMock):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "road_2.jpg").write_text("x", encoding="utf-8")
            mock_dirs.return_value = (directory,)
            path = asset_extension.get_texture_path("road.jpg")
            self.assertIsNotNone(path)
            self.assertTrue(path.name.startswith("road"))

    @patch.object(asset_extension, "texture_directories")
    def test_missing_file_returns_none(self, mock_dirs: MagicMock):
        with tempfile.TemporaryDirectory() as tmp:
            mock_dirs.return_value = (Path(tmp),)
            self.assertIsNone(asset_extension.get_texture_path("does_not_exist.jpg"))


if __name__ == "__main__":
    unittest.main()

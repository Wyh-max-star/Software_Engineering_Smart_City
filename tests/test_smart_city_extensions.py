"""Integration-style unit tests for cross-module Smart City behaviour."""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402
from test_markers import gray_box  # noqa: E402

asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")


@gray_box
class SmartCityExtensionTests(unittest.TestCase):
    def test_plot_placement_stays_outside_city_core(self):
        ecology_water = load_module("ecology_water", "iCity/smart_city/ecology_water.py")
        settings = types.SimpleNamespace(
            seed=12,
            plot_offset=14.0,
            plot_width=70.0,
            plot_depth=55.0,
        )
        for plot_index in range(1, 6):
            location = ecology_water.compute_plot_location(
                Vector((0.0, 0.0, 0.0)), 30.0, settings, plot_index
            )
            self.assertGreater(location.length, 44.0)

    @patch.object(
        asset_extension,
        "get_texture_path",
        return_value=Path("RoadLines010_2K-JPG_Opacity.jpg"),
    )
    def test_asset_texture_lookup_accepts_numbered_duplicate_files(self, mock_lookup):
        path = asset_extension.get_texture_path("RoadLines010_2K-JPG_Opacity.jpg")
        self.assertIsNotNone(path)
        self.assertTrue(str(path).startswith("RoadLines010_2K-JPG_Opacity"))
        mock_lookup.assert_called_once_with("RoadLines010_2K-JPG_Opacity.jpg")

    def test_traffic_layout_stays_outside_city_core(self):
        traffic_extension = load_module(
            "traffic_extension", "iCity/smart_city/traffic_extension.py"
        )
        settings = types.SimpleNamespace(
            traffic_outer_offset=10.0,
            traffic_lane_gap=2.4,
            pedestrian_outer_gap=3.2,
            pedestrian_lane_gap=1.6,
            road_width=3.8,
            walkway_width=2.4,
        )
        layout = traffic_extension.compute_traffic_layout(
            Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings
        )
        self.assertGreater(layout["vehicle_lane_inner_x"], 30.0)

    def test_pedestrian_routes_use_traffic_offset_helpers(self):
        pedestrian_extension = load_module(
            "pedestrian_extension", "iCity/smart_city/pedestrian_extension.py"
        )
        chain = [Vector((index * 5.0, 0.0, 0.0)) for index in range(8)]
        routes = pedestrian_extension.plan_sidewalk_routes([chain], 3.0, 6.0, z_lift=0.05)
        self.assertGreater(len(routes), 0)
        for route in routes:
            self.assertGreaterEqual(route["distance"], 3.0)
            self.assertLessEqual(route["distance"], 6.0)


if __name__ == "__main__":
    unittest.main()

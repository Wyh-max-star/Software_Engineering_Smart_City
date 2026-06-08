import types
import unittest

from tests.test_smart_city_extensions import Vector, load_module


class SmartCityLayoutSamplingTests(unittest.TestCase):
    def test_multiple_seeds_keep_ecology_and_traffic_outside_city_band(self):
        ecology_common = load_module("ecology_common_sampling", "iCity/smart_city/ecology_common.py")

        for seed in (1, 7, 12, 25, 48, 77):
            settings = types.SimpleNamespace(
                seed=seed,
                terrain_margin=55.0,
                lake_radius=16.0,
                lake_depth=7.5,
                river_width=7.0,
                traffic_loop_radius_x=14.0,
                traffic_loop_radius_y=8.5,
                road_width=3.8,
            )
            layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)

            lake_clearance = layout["lake_center"].length - max(layout["lake_radius_x"], layout["lake_radius_y"])
            traffic_clearance = (
                layout["traffic_center"].length
                - max(settings.traffic_loop_radius_x, settings.traffic_loop_radius_y)
                - settings.road_width * 0.5
            )

            self.assertGreaterEqual(lake_clearance, 36.0)
            self.assertGreaterEqual(traffic_clearance, 34.0)

    def test_layout_helpers_share_same_city_radius_assumptions(self):
        asset_extension = load_module("asset_extension_bounds", "iCity/smart_city/asset_extension.py")
        ecology_common = load_module("ecology_common_bounds", "iCity/smart_city/ecology_common.py")

        self.assertEqual(asset_extension.ICITY_BASE_OBJECT, ecology_common.ICITY_BASE_OBJECT)
        self.assertEqual(asset_extension.ICITY_ROOT_COLLECTION, ecology_common.ICITY_ROOT_COLLECTION)

    def test_traffic_and_lake_do_not_share_same_center(self):
        ecology_common = load_module("ecology_common_demo_side", "iCity/smart_city/ecology_common.py")
        settings = types.SimpleNamespace(
            seed=12,
            terrain_margin=55.0,
            lake_radius=16.0,
            lake_depth=7.5,
            river_width=7.0,
            traffic_loop_radius_x=14.0,
            traffic_loop_radius_y=8.5,
            road_width=3.8,
        )

        layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)
        separation = (layout["lake_center"] - layout["traffic_center"]).length

        self.assertGreaterEqual(separation, 35.0)

    def test_ecology_asset_anchors_stay_outside_city_core_across_seeds(self):
        ecology_common = load_module("ecology_common_asset_sampling", "iCity/smart_city/ecology_common.py")

        for seed in (1, 7, 12, 25, 48, 77):
            settings = types.SimpleNamespace(
                seed=seed,
                terrain_margin=55.0,
                lake_radius=16.0,
                lake_depth=7.5,
                river_width=7.0,
                traffic_loop_radius_x=14.0,
                traffic_loop_radius_y=8.5,
                road_width=3.8,
            )
            layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)
            anchors = ecology_common.compute_ecology_asset_anchors(layout, settings)

            self.assertLess((anchors["dock_center"] - layout["lake_center"]).dot(layout["direction"]), 0.0)
            for point in anchors["tree_points"] + anchors["shrub_points"]:
                self.assertGreaterEqual(point.length, layout["city_safe_radius"] + 1.0)


if __name__ == "__main__":
    unittest.main()

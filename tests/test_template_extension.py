"""Gray-box tests for template application logic (mocked ``bpy.ops``)."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from mock_helpers import make_settings  # noqa: E402
from test_markers import gray_box  # noqa: E402


template_core = load_module("template_core", "iCity/smart_city/template_core.py")
template_extension = load_module("template_extension", "iCity/smart_city/template_extension.py")


def _bind_traffic_settings():
    traffic_settings = make_settings(
        car_count=0,
        taxi_count=0,
        bus_count=0,
        animation_start=1,
        animation_end=60,
    )
    template_extension.bpy.context.scene.icity_traffic_settings = traffic_settings
    return traffic_settings


@gray_box
class ApplySceneDimensionsTests(unittest.TestCase):
    @patch.object(template_extension, "_call_op")
    @patch.object(template_extension, "_op_exists", return_value=True)
    def test_clear_traffic_invokes_clear_op(self, _mock_exists, mock_call):
        results = template_extension.apply_scene_dimensions({"traffic": {"_clear": True}})
        mock_call.assert_called_once_with("icity.clear_traffic")
        self.assertEqual(results[0], ("交通(清空)", True))

    @patch.object(template_extension, "_call_op")
    @patch.object(template_extension, "_op_exists", return_value=True)
    @patch.object(template_extension, "_settings_present", return_value=True)
    def test_generate_traffic_sets_settings_before_op(self, _mock_present, _mock_exists, mock_call):
        traffic_settings = _bind_traffic_settings()
        scene_cfg = {
            "traffic": {"enable": True, "car_count": 24, "taxi_count": 4, "bus_count": 2},
        }
        results = template_extension.apply_scene_dimensions(scene_cfg)
        self.assertEqual(traffic_settings.car_count, 24)
        self.assertEqual(traffic_settings.taxi_count, 4)
        self.assertEqual(traffic_settings.bus_count, 2)
        mock_call.assert_called_once_with("icity.generate_traffic")
        self.assertEqual(results[0], ("交通", True))

    @patch.object(template_extension, "_call_op")
    @patch.object(template_extension, "_op_exists", return_value=False)
    @patch.object(template_extension, "_settings_present", return_value=True)
    def test_missing_op_is_reported_as_skip(self, _mock_present, _mock_exists, _mock_call):
        traffic_settings = _bind_traffic_settings()
        results = template_extension.apply_scene_dimensions(
            {"traffic": {"enable": True, "car_count": 12}}
        )
        self.assertEqual(results[0], ("交通", None))
        self.assertEqual(traffic_settings.car_count, 0)

    @patch.object(template_extension, "_call_op")
    @patch.object(template_extension, "_op_exists", return_value=True)
    @patch.object(template_extension, "_settings_present", return_value=True)
    def test_ecology_plot_clears_before_add(self, _mock_present, _mock_exists, mock_call):
        ecology_settings = make_settings(enable_ecology_block=False)
        template_extension.bpy.context.scene.icity_ecology_settings = ecology_settings
        scene_cfg = {
            "ecology": {
                "enable": True,
                "ecology_plot_mode": "LAKE_RING",
                "mountain_height": 12.0,
            },
        }
        template_extension.apply_scene_dimensions(scene_cfg)
        self.assertTrue(ecology_settings.enable_ecology_block)
        self.assertEqual(mock_call.call_args_list[0].args[0], "icity.clear_ecology")
        self.assertEqual(mock_call.call_args_list[1].args[0], "icity.add_ecology_plot")

    def test_empty_scene_cfg_returns_no_results(self):
        self.assertEqual(template_extension.apply_scene_dimensions({}), [])
        self.assertEqual(template_extension.apply_scene_dimensions(None), [])


@gray_box
class SmartCityAvailabilityTests(unittest.TestCase):
    @patch.object(template_extension, "_settings_present", return_value=False)
    def test_unavailable_when_no_settings_groups(self, _mock_present):
        self.assertFalse(template_extension.smart_city_available())

    @patch.object(template_extension, "_settings_present", return_value=True)
    def test_available_when_any_settings_group_exists(self, _mock_present):
        self.assertTrue(template_extension.smart_city_available())


@gray_box
class ApplySelectionTests(unittest.TestCase):
    def setUp(self):
        self.base = MagicMock(name="ICity Base")

    @patch.object(template_extension, "apply_street_asset", return_value=True)
    @patch.object(template_extension, "apply_road_material", return_value=True)
    @patch.object(template_extension, "enter_edit_select_all")
    def test_applies_all_non_null_categories(self, mock_enter, mock_road, mock_street):
        sel = {
            "tree": "Tree1_Tree_ICity_Default",
            "bench": "Bench1_Bench_ICity_Default",
            "road_material": "ICity_Road 4 clean_Default",
            "light": None,
        }
        results = template_extension.apply_selection(self.base, sel)
        self.assertEqual(mock_enter.call_count, 3)
        mock_street.assert_any_call("Tree", "Tree1_Tree_ICity_Default")
        mock_street.assert_any_call("Bench", "Bench1_Bench_ICity_Default")
        mock_road.assert_called_once_with("ICity_Road 4 clean_Default", "Road")
        self.assertEqual(len(results), 3)
        self.assertTrue(all(ok for _, ok in results))

    @patch.object(template_extension, "apply_street_asset", return_value=True)
    @patch.object(template_extension, "enter_edit_select_all")
    def test_skips_null_assets(self, mock_enter, mock_street):
        sel = {cat: None for cat in template_extension.ALL_CATS}
        sel["tree"] = "Tree7_Tree_ICity_Default"
        results = template_extension.apply_selection(self.base, sel)
        mock_enter.assert_called_once()
        mock_street.assert_called_once_with("Tree", "Tree7_Tree_ICity_Default")
        self.assertEqual(len(results), 1)


@gray_box
class ApplyStreetAssetTests(unittest.TestCase):
    def _bind_scene(self):
        scene = make_settings(
            sna_street_asset_type=None,
            sna_street_asset_browser=None,
            sna_road_materials_type_=None,
            sna_road_materials_browser=None,
        )
        template_extension.bpy.context.scene = scene
        template_extension.bpy.context.view_layer = MagicMock()
        template_extension.bpy.context.object = MagicMock(mode="OBJECT")
        template_extension.bpy.ops.sna = MagicMock()
        template_extension.bpy.ops.sna.road_apply_5c3ab = MagicMock()
        template_extension.bpy.ops.object = MagicMock()
        template_extension.bpy.ops.object.mode_set = MagicMock()
        template_extension.bpy.ops.object.select_all = MagicMock()
        template_extension.bpy.ops.mesh = MagicMock()
        template_extension.bpy.ops.mesh.select_all = MagicMock()
        return scene

    @patch.object(template_extension, "enter_edit_select_all")
    def test_apply_street_asset_sets_browser_and_calls_road_apply(self, _mock_enter):
        scene = self._bind_scene()
        ok = template_extension.apply_street_asset("Tree", "Tree1_Tree_ICity_Default")
        self.assertTrue(ok)
        self.assertEqual(scene.sna_street_asset_type, "Tree")
        self.assertEqual(scene.sna_street_asset_browser, "Tree1_Tree_ICity_Default")
        template_extension.bpy.ops.sna.road_apply_5c3ab.assert_called_once()

    @patch.object(template_extension, "enter_edit_select_all")
    def test_apply_road_material_sets_material_browser(self, _mock_enter):
        scene = self._bind_scene()
        ok = template_extension.apply_road_material("ICity_Road 8 dirty_Default", "Road")
        self.assertTrue(ok)
        self.assertEqual(scene.sna_street_asset_type, "Texture")
        self.assertEqual(scene.sna_road_materials_type_, "Road")
        self.assertEqual(scene.sna_road_materials_browser, "ICity_Road 8 dirty_Default")
        template_extension.bpy.ops.sna.road_apply_5c3ab.assert_called_once()

    @patch.object(template_extension, "enter_edit_select_all")
    def test_apply_street_asset_returns_false_when_road_apply_fails(self, _mock_enter):
        self._bind_scene()
        template_extension.bpy.ops.sna.road_apply_5c3ab.side_effect = RuntimeError("boom")
        ok = template_extension.apply_street_asset("Bench", "Bench1_Bench_ICity_Default")
        self.assertFalse(ok)


@gray_box
class EnterEditSelectAllTests(unittest.TestCase):
    @patch.object(template_core, "get_icity_module")
    def test_sets_sna_edit_city_when_icity_module_present(self, mock_get_icity):
        icity_mod = make_settings(variables={"sna_edit_city": False})
        mock_get_icity.return_value = icity_mod
        base = MagicMock(name="ICity Base")
        template_extension.bpy.context.object = MagicMock(mode="EDIT")
        template_extension.bpy.context.view_layer = MagicMock()
        template_extension.bpy.ops.object = MagicMock()
        template_extension.bpy.ops.object.mode_set = MagicMock()
        template_extension.bpy.ops.object.select_all = MagicMock()
        template_extension.bpy.ops.mesh = MagicMock()
        template_extension.bpy.ops.mesh.select_all = MagicMock()

        template_extension.enter_edit_select_all(base)

        self.assertTrue(icity_mod.variables["sna_edit_city"])
        self.assertIs(template_extension.bpy.context.view_layer.objects.active, base)
        base.select_set.assert_called_once_with(True)


@gray_box
class IncrementalMergeTests(unittest.TestCase):
    def setUp(self):
        template_extension._last_scene_cfg = {}
        template_extension._last_asset_sel = {}

    def test_new_scene_overrides_old_dimension(self):
        template_extension._last_scene_cfg = {"traffic": {"car_count": 24}}
        merged_scene, _ = template_extension._merge_incremental({"weather": "rainy"}, {})
        self.assertEqual(merged_scene["weather"], "rainy")
        self.assertEqual(merged_scene["traffic"]["car_count"], 24)

    def test_clear_traffic_replaces_prior_traffic(self):
        template_extension._last_scene_cfg = {"traffic": {"car_count": 24}}
        merged_scene, _ = template_extension._merge_incremental({"traffic": {"_clear": True}}, {})
        self.assertEqual(merged_scene["traffic"], {"_clear": True})

    def test_asset_merge_skips_none_values(self):
        template_extension._last_asset_sel = {"tree": "Tree1_Tree_ICity_Default"}
        _, merged_assets = template_extension._merge_incremental({}, {"tree": None, "bench": "Bench1_Bench_ICity_Default"})
        self.assertEqual(merged_assets["tree"], "Tree1_Tree_ICity_Default")
        self.assertEqual(merged_assets["bench"], "Bench1_Bench_ICity_Default")


if __name__ == "__main__":
    unittest.main()

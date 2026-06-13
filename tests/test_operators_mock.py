"""Black-box operator tests using ``unittest.mock`` (no real Blender runtime).

Each case patches the heavy generation pipeline and asserts operator
``execute`` / ``poll`` contracts — equivalent coverage to the former
``tests/blender/test_generate_ops.py`` but fully mock-driven.
"""

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import Vector, load_module  # noqa: E402
from mock_helpers import make_mock_context, make_settings  # noqa: E402
from test_markers import black_box  # noqa: E402


asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")
ecology_extension = load_module("ecology_extension", "iCity/smart_city/ecology_extension.py")
traffic_extension = load_module("traffic_extension", "iCity/smart_city/traffic_extension.py")
pedestrian_extension = load_module("pedestrian_extension", "iCity/smart_city/pedestrian_extension.py")
template_core = load_module("template_core", "iCity/smart_city/template_core.py")
template_extension = load_module("template_extension", "iCity/smart_city/template_extension.py")


def _traffic_context(start=1, end=60):
    return make_mock_context(
        icity_traffic_settings=make_settings(
            animation_start=start,
            animation_end=end,
            car_count=3,
            taxi_count=1,
            bus_count=1,
        )
    )


def _ecology_context(enabled=True, start=1, end=120):
    return make_mock_context(
        icity_ecology_settings=make_settings(
            enable_ecology_block=enabled,
            animation_start=start,
            animation_end=end,
        )
    )


def _pedestrian_context(start=1, end=60):
    return make_mock_context(
        icity_pedestrian_settings=make_settings(
            animation_start=start,
            animation_end=end,
            walker_count=4,
            idle_count=2,
        )
    )


@black_box
class AssetOperatorMockTests(unittest.TestCase):
    @patch.object(asset_extension, "create_streetlight_instance")
    @patch.object(asset_extension, "build_streetlight_mesh")
    @patch.object(asset_extension, "build_streetlight_materials", return_value=(MagicMock(), MagicMock()))
    @patch.object(asset_extension, "filtered_perimeter_positions")
    @patch.object(asset_extension, "get_city_bounds", return_value=(Vector((0, 0, 0)), 30.0, 0.0))
    @patch.object(asset_extension, "clear_streetlights")
    @patch.object(asset_extension, "get_asset_root_collection")
    @patch.object(asset_extension, "get_or_create_child_collection")
    def test_generate_streetlights_returns_finished(
        self,
        mock_child_coll,
        mock_root,
        mock_clear,
        mock_bounds,
        mock_positions,
        mock_materials,
        mock_mesh,
        mock_create,
    ):
        mock_mesh.return_value = MagicMock(materials=MagicMock())
        mock_positions.return_value = [(Vector((1, 0, 0)), 0.0)] * 12
        context = make_mock_context(
            icity_asset_settings=make_settings(streetlight_count=12, streetlight_offset=7.5, streetlight_base_z_offset=0.0)
        )
        op = asset_extension.ICITY_OT_GenerateStreetlights()
        result = op.execute(context)
        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(mock_create.call_count, 12)
        mock_clear.assert_called_once()

    @patch.object(asset_extension, "clear_streetlights")
    @patch.object(asset_extension, "clear_roadside_assets")
    @patch.object(asset_extension, "get_asset_root_collection", return_value=None)
    def test_clear_asset_expansion(self, mock_root, mock_roadside, mock_lights):
        op = asset_extension.ICITY_OT_ClearAssetExpansion()
        result = op.execute(make_mock_context())
        self.assertEqual(result, {"FINISHED"})
        mock_lights.assert_called_once()
        mock_roadside.assert_called_once()


@black_box
class EcologyOperatorMockTests(unittest.TestCase):
    @patch.object(ecology_extension, "add_ecology_plot", return_value=(MagicMock(), 1))
    @patch.object(ecology_extension.bpy.data.collections, "get", return_value=MagicMock())
    def test_add_ecology_plot_finished(self, mock_get, mock_add):
        op = ecology_extension.ICITY_OT_AddEcologyPlot()
        result = op.execute(_ecology_context())
        self.assertEqual(result, {"FINISHED"})
        mock_add.assert_called_once()

    @patch.object(ecology_extension.bpy.data.collections, "get", return_value=None)
    def test_add_ecology_plot_poll_requires_icity(self, mock_get):
        self.assertFalse(ecology_extension.ICITY_OT_AddEcologyPlot.poll(make_mock_context()))

    def test_add_ecology_plot_cancelled_when_block_disabled(self):
        op = ecology_extension.ICITY_OT_AddEcologyPlot()
        with patch.object(ecology_extension.bpy.data.collections, "get", return_value=MagicMock()):
            result = op.execute(_ecology_context(enabled=False))
        self.assertEqual(result, {"CANCELLED"})

    @patch.object(ecology_extension.ecology_common, "clear_existing_ecology")
    def test_clear_ecology(self, mock_clear):
        op = ecology_extension.ICITY_OT_ClearEcology()
        self.assertEqual(op.execute(make_mock_context()), {"FINISHED"})
        mock_clear.assert_called_once()


@black_box
class TrafficOperatorMockTests(unittest.TestCase):
    @patch.object(traffic_extension, "generate_traffic")
    def test_generate_traffic_finished(self, mock_generate):
        op = traffic_extension.ICITY_OT_GenerateTraffic()
        context = _traffic_context()
        self.assertEqual(op.execute(context), {"FINISHED"})
        mock_generate.assert_called_once_with(context)

    def test_generate_traffic_cancelled_on_bad_frames(self):
        op = traffic_extension.ICITY_OT_GenerateTraffic()
        result = op.execute(_traffic_context(start=10, end=10))
        self.assertEqual(result, {"CANCELLED"})

    @patch.object(traffic_extension, "generate_traffic", side_effect=RuntimeError("Please run iCity Start"))
    def test_generate_traffic_cancelled_on_runtime_error(self, mock_generate):
        op = traffic_extension.ICITY_OT_GenerateTraffic()
        self.assertEqual(op.execute(_traffic_context()), {"CANCELLED"})

    @patch.object(traffic_extension, "clear_traffic")
    def test_clear_traffic(self, mock_clear):
        op = traffic_extension.ICITY_OT_ClearTraffic()
        self.assertEqual(op.execute(_traffic_context()), {"FINISHED"})
        mock_clear.assert_called_once()


@black_box
class PedestrianOperatorMockTests(unittest.TestCase):
    @patch.object(
        pedestrian_extension,
        "generate_pedestrians",
        return_value={"walkers": 4, "idlers": 2, "used_road_graph": False, "near": 6.3, "far": 6.8},
    )
    def test_generate_pedestrians_finished(self, mock_generate):
        op = pedestrian_extension.ICITY_OT_GeneratePedestrians()
        context = _pedestrian_context()
        self.assertEqual(op.execute(context), {"FINISHED"})
        mock_generate.assert_called_once_with(context)

    @patch.object(
        pedestrian_extension,
        "generate_pedestrians",
        side_effect=RuntimeError("Please run iCity Start before generating pedestrians."),
    )
    def test_generate_pedestrians_cancelled_without_city(self, mock_generate):
        op = pedestrian_extension.ICITY_OT_GeneratePedestrians()
        self.assertEqual(op.execute(_pedestrian_context()), {"CANCELLED"})

    @patch.object(pedestrian_extension, "clear_pedestrians")
    def test_clear_pedestrians(self, mock_clear):
        op = pedestrian_extension.ICITY_OT_ClearPedestrians()
        self.assertEqual(op.execute(_pedestrian_context()), {"FINISHED"})
        mock_clear.assert_called_once()


def _template_context(template_id="0", nl_command="车水马龙"):
    return make_mock_context(
        icity_template_settings=make_settings(template_id=template_id, nl_command=nl_command)
    )


def _mock_icity_base():
    base = MagicMock(name="ICity Base")
    template_extension.bpy.data.objects.get = MagicMock(return_value=base)
    return base


@black_box
class TemplateOperatorMockTests(unittest.TestCase):
    @patch.object(template_extension, "apply_scene_dimensions", return_value=[("交通", True)])
    @patch.object(template_extension, "apply_selection", return_value=[("树", True)])
    @patch.object(template_core, "load_templates")
    def test_apply_template_finished(self, mock_load, mock_apply_sel, mock_apply_scene):
        mock_load.return_value = [
            {
                "id": "0",
                "name": "公园",
                "plugin": {"tree": "Tree1_Tree_ICity_Default"},
                "scene": {"traffic": {"enable": True, "car_count": 6}},
            }
        ]
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyTemplate()
        result = op.execute(_template_context(template_id="0"))
        self.assertEqual(result, {"FINISHED"})
        mock_apply_sel.assert_called_once()
        mock_apply_scene.assert_called_once()

    @patch.object(template_extension.bpy.data.objects, "get", return_value=None)
    def test_apply_template_cancelled_without_base(self, _mock_get):
        op = template_extension.ICITY_OT_ApplyTemplate()
        self.assertEqual(op.execute(_template_context()), {"CANCELLED"})

    @patch.object(template_core, "load_templates", return_value=[])
    def test_apply_template_cancelled_when_template_missing(self, _mock_load):
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyTemplate()
        self.assertEqual(op.execute(_template_context(template_id="99")), {"CANCELLED"})

    @patch.object(template_extension, "apply_scene_dimensions", return_value=[])
    @patch.object(template_extension, "apply_selection", return_value=[("树", True)])
    @patch.object(
        template_core,
        "parse_command",
        return_value=(
            {"tree": "Tree7_Tree_ICity_Default", "_scene": {"traffic": {"_clear": True}}},
            "DeepSeek",
        ),
    )
    def test_apply_nl_command_finished(self, _mock_parse, mock_apply_sel, _mock_apply_scene):
        template_extension._last_scene_cfg = {}
        template_extension._last_asset_sel = {}
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyNaturalLanguage()
        result = op.execute(_template_context(nl_command="去掉车，金黄的树"))
        self.assertEqual(result, {"FINISHED"})
        mock_apply_sel.assert_called_once()

    def test_apply_nl_command_cancelled_on_empty_text(self):
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyNaturalLanguage()
        ctx = _template_context(nl_command="   ")
        self.assertEqual(op.execute(ctx), {"CANCELLED"})

    @patch.object(template_core, "parse_command", return_value=({c: None for c in template_core.ALL_CATS} | {"_scene": {}}, "规则解析"))
    def test_apply_nl_command_cancelled_when_unparsed(self, _mock_parse):
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyNaturalLanguage()
        self.assertEqual(op.execute(_template_context(nl_command="你好世界")), {"CANCELLED"})

    @patch.object(template_extension, "apply_weather", return_value="雨天")
    @patch.object(template_extension, "apply_scene_dimensions", return_value=[])
    @patch.object(template_extension, "apply_selection", return_value=[])
    @patch.object(
        template_core,
        "parse_command",
        return_value=(
            {c: None for c in template_core.ALL_CATS} | {"_scene": {"weather": "rainy"}},
            "规则解析",
        ),
    )
    def test_apply_nl_command_applies_weather(
        self, _mock_parse, _mock_sel, _mock_scene, mock_weather
    ):
        template_extension._last_scene_cfg = {}
        template_extension._last_asset_sel = {}
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyNaturalLanguage()
        self.assertEqual(op.execute(_template_context(nl_command="下雨天")), {"FINISHED"})
        mock_weather.assert_called_once_with("rainy")

    @patch.object(template_extension, "apply_weather")
    @patch.object(template_extension, "apply_scene_dimensions", return_value=[])
    @patch.object(template_extension, "apply_selection", return_value=[("树", True)])
    @patch.object(
        template_core,
        "parse_command",
        side_effect=[
            (
                {"tree": "Tree14_Tree_ICity_Default", "_scene": {"weather": "rainy"}},
                "规则解析",
            ),
            (
                {"tree": None, "_scene": {"weather": "sunny"}},
                "规则解析",
            ),
        ],
    )
    def test_apply_nl_command_incremental_merge(
        self, _mock_parse, _mock_sel, _mock_scene, _mock_weather
    ):
        template_extension._last_scene_cfg = {}
        template_extension._last_asset_sel = {}
        _mock_icity_base()
        op = template_extension.ICITY_OT_ApplyNaturalLanguage()
        ctx = _template_context(nl_command="下雨天、棕榈树")
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertEqual(template_extension._last_asset_sel.get("tree"), "Tree14_Tree_ICity_Default")
        self.assertEqual(template_extension._last_scene_cfg.get("weather"), "rainy")

        ctx = _template_context(nl_command="晴天")
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertEqual(template_extension._last_scene_cfg.get("weather"), "sunny")
        self.assertEqual(template_extension._last_asset_sel.get("tree"), "Tree14_Tree_ICity_Default")


if __name__ == "__main__":
    unittest.main()

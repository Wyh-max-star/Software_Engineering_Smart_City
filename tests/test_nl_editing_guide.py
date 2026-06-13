# -*- coding: utf-8 -*-
"""NL editing guide tests: assets, scene, weather, incremental merge, rule fallback."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from test_markers import gray_box, white_box  # noqa: E402

def _load_template_core():
    path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "template_core.py"
    spec = importlib.util.spec_from_file_location("template_core_nl", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tc = _load_template_core()

template_extension = load_module("template_extension", "iCity/smart_city/template_extension.py")


def _rule_sel(text: str) -> dict:
    sel = tc.rule_parse(text)
    sel["_scene"] = tc.expand_scene(tc.rule_parse_scene(text))
    return sel


def _assets(sel: dict) -> dict:
    return {k: v for k, v in sel.items() if k != "_scene"}


def _scene(sel: dict) -> dict:
    return dict(sel.get("_scene") or {})


def _reset_incremental() -> None:
    template_extension._last_scene_cfg = {}
    template_extension._last_asset_sel = {}


def _apply_incremental(text: str) -> tuple[dict, dict]:
    sel = _rule_sel(text)
    merged_scene, merged_assets = template_extension._merge_incremental(_scene(sel), _assets(sel))
    template_extension._last_scene_cfg = merged_scene
    template_extension._last_asset_sel = merged_assets
    return merged_scene, merged_assets


WEATHER_CASES = (
    ("晴天", "sunny"),
    ("天色变暗", "cloudy"),
    ("下雨天", "rainy"),
    ("夜晚", "night"),
    ("起雾", "foggy"),
    ("黄昏", "sunset"),
    ("下雪", "snowy"),
)


@white_box
class NlWeatherGuideTests(unittest.TestCase):
    @patch.object(tc, "LLM_ENABLED", False)
    def test_weather_rule_parse_and_expand(self):
        for text, mode in WEATHER_CASES:
            with self.subTest(text=text, mode=mode):
                raw = tc.rule_parse_scene(text)
                self.assertEqual(raw.get("weather"), mode)
                self.assertEqual(tc.expand_scene(raw).get("weather"), mode)

    def test_has_content_true_for_weather_only(self):
        sel = {c: None for c in tc.ALL_CATS}
        sel["_scene"] = {"weather": "rainy"}
        self.assertTrue(tc._has_content(sel))

    def test_system_prompt_documents_weather_modes(self):
        block = tc.build_scene_prompt_block()
        for mode in tc.WEATHER_MODES:
            self.assertIn(mode, block)


@white_box
class NlCombinedCommandTests(unittest.TestCase):
    @patch.object(tc, "LLM_ENABLED", False)
    def test_combined_traffic_ecology_pedestrian_tree(self):
        sel = _rule_sel("车水马龙、有山有湖、很多人，金黄的树")
        self.assertEqual(sel["tree"], "Tree7_Tree_ICity_Default")
        scene = _scene(sel)
        self.assertEqual(scene["traffic"]["car_count"], 24)
        self.assertEqual(scene["pedestrian"]["walker_count"], 40)
        self.assertEqual(scene["ecology"]["ecology_plot_mode"], "LAKE_RING")

    @patch.object(tc, "LLM_ENABLED", False)
    def test_combined_weather_and_traffic(self):
        scene = _scene(_rule_sel("下雨天、车水马龙"))
        self.assertEqual(scene["weather"], "rainy")
        self.assertEqual(scene["traffic"]["car_count"], 24)


@gray_box
class NlIncrementalDialogueTests(unittest.TestCase):
    def setUp(self):
        _reset_incremental()

    @patch.object(tc, "LLM_ENABLED", False)
    def test_multi_turn_preserves_prior_scene(self):
        scene, _ = _apply_incremental("有山有湖，车水马龙")
        self.assertEqual(scene["ecology"]["ecology_plot_mode"], "LAKE_RING")
        self.assertEqual(scene["traffic"]["car_count"], 24)

        scene, _ = _apply_incremental("加上下雨")
        self.assertEqual(scene["weather"], "rainy")
        self.assertEqual(scene["traffic"]["car_count"], 24)

        scene, assets = _apply_incremental("去掉车")
        self.assertEqual(scene["traffic"], {"_clear": True})
        self.assertEqual(scene["weather"], "rainy")

        scene, assets = _apply_incremental("棕榈树")
        self.assertEqual(assets["tree"], "Tree14_Tree_ICity_Default")
        self.assertEqual(scene["weather"], "rainy")

    def test_merge_keeps_unmentioned_keys(self):
        _reset_incremental()
        template_extension._last_scene_cfg = {"traffic": {"enable": True, "car_count": 24}}
        template_extension._last_asset_sel = {"tree": "Tree1_Tree_ICity_Default"}
        merged_scene, merged_assets = template_extension._merge_incremental(
            {"weather": "rainy"},
            {"bench": "Bench1_Bench_ICity_Default"},
        )
        self.assertEqual(merged_scene["traffic"]["car_count"], 24)
        self.assertEqual(merged_scene["weather"], "rainy")
        self.assertEqual(merged_assets["tree"], "Tree1_Tree_ICity_Default")
        self.assertEqual(merged_assets["bench"], "Bench1_Bench_ICity_Default")


@gray_box
class NlWeatherApplyTests(unittest.TestCase):
    def test_apply_weather_rejects_unknown_mode(self):
        self.assertEqual(template_extension.apply_weather("hurricane"), "未知天气模式")

    @patch.object(template_extension, "_ensure_weather_particles")
    @patch.object(template_extension, "_clear_weather_particles")
    @patch.object(template_extension, "_set_eevee_fog")
    def test_apply_weather_rainy_returns_label(self, _mock_fog, _mock_clear, _mock_particles):
        bg = MagicMock()
        bg.type = "BACKGROUND"
        bg.inputs = {
            "Strength": MagicMock(default_value=1.0),
            "Color": MagicMock(default_value=(0, 0, 0, 1)),
        }
        world = MagicMock()
        world.node_tree.nodes = [bg]
        template_extension.bpy.context.scene.world = world
        template_extension.bpy.data.lights.get = MagicMock(return_value=None)

        self.assertEqual(template_extension.apply_weather("rainy"), "雨天")
        _mock_particles.assert_called_once_with("rainy")


if __name__ == "__main__":
    unittest.main()

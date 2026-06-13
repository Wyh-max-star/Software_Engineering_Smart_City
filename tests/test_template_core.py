# -*- coding: utf-8 -*-
"""模板化模块纯逻辑单元测试（不依赖 Blender）。

测 iCity/smart_city/template_core.py 的关键词解析、档位换算、数据加载。
运行：python tests/test_template_core.py  或  python -m unittest discover tests
"""

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from test_markers import white_box  # noqa: E402


def load_template_core():
    module_path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "template_core.py"
    spec = importlib.util.spec_from_file_location("template_core", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tc = load_template_core()


@white_box
class RuleParseTests(unittest.TestCase):
    def test_tree_keywords(self):
        self.assertEqual(tc.rule_parse("把树换成金黄的")["tree"], "Tree7_Tree_ICity_Default")
        self.assertEqual(tc.rule_parse("换成棕榈树")["tree"], "Tree14_Tree_ICity_Default")

    def test_road_and_bench_keywords(self):
        self.assertEqual(tc.rule_parse("脏旧的路")["road_material"], "ICity_Road 8 dirty_Default")
        self.assertEqual(tc.rule_parse("现代金属椅")["bench"], "Bench11_Bench_ICity_Default")

    def test_unrelated_text_yields_none(self):
        sel = tc.rule_parse("你好世界")
        self.assertTrue(all(v is None for v in sel.values()))


@white_box
class RuleParseSceneTests(unittest.TestCase):
    def test_traffic_levels(self):
        self.assertEqual(tc.rule_parse_scene("车水马龙")["traffic"], "high")
        self.assertEqual(tc.rule_parse_scene("步行街没有车")["traffic"], "none")

    def test_ecology_modes_and_clear(self):
        self.assertEqual(tc.rule_parse_scene("去掉山去掉湖")["ecology_mode"], "NONE")
        self.assertEqual(tc.rule_parse_scene("有山有湖")["ecology_mode"], "LAKE_RING")
        self.assertEqual(tc.rule_parse_scene("蜿蜒的河")["ecology_mode"], "RIVER_VALLEY")

    def test_unmentioned_dim_absent(self):
        # 没提到的维度不应出现(避免误清)
        self.assertNotIn("ecology_mode", tc.rule_parse_scene("把树换成棕榈"))


@white_box
class ExpandSceneTests(unittest.TestCase):
    def test_clear_markers(self):
        self.assertEqual(tc.expand_scene({"traffic": "none"})["traffic"], {"_clear": True})
        self.assertEqual(tc.expand_scene({"ecology_mode": "NONE"})["ecology"], {"_clear": True})

    def test_level_to_numbers(self):
        cs = tc.load_catalog_scene()
        expect = cs["traffic"]["levels"]["car_count"]["high"]
        d = tc.expand_scene({"traffic": "high"})["traffic"]
        self.assertTrue(d.get("enable"))
        self.assertEqual(d["car_count"], expect)
        self.assertIsInstance(d["car_count"], int)

    def test_surface_passthrough(self):
        d = tc.expand_scene({"surface": "BOARDWALK_WARM"})["surface"]
        self.assertEqual(d["surface_style"], "BOARDWALK_WARM")

    def test_ecology_intensity(self):
        d = tc.expand_scene({"ecology_mode": "LAKE_RING", "ecology_intensity": "high"})["ecology"]
        self.assertEqual(d["ecology_plot_mode"], "LAKE_RING")
        self.assertIn("mountain_height", d)

    def test_weather_passthrough(self):
        self.assertEqual(tc.expand_scene({"weather": "rainy"})["weather"], "rainy")
        self.assertNotIn("weather", tc.expand_scene({}))


@white_box
class WeatherRuleParseTests(unittest.TestCase):
    def test_weather_keywords(self):
        self.assertEqual(tc.rule_parse_scene("下雨天")["weather"], "rainy")
        self.assertEqual(tc.rule_parse_scene("天色变暗")["weather"], "cloudy")
        self.assertEqual(tc.rule_parse_scene("下雪天")["weather"], "snowy")

    def test_weather_in_build_system_prompt(self):
        prompt = tc.build_system_prompt()
        self.assertIn("weather", prompt)
        for mode in tc.WEATHER_MODES:
            self.assertIn(mode, prompt)


@white_box
class HasContentWeatherTests(unittest.TestCase):
    def test_true_when_only_weather_in_scene(self):
        sel = {c: None for c in tc.ALL_CATS}
        sel["_scene"] = {"weather": "sunny"}
        self.assertTrue(tc._has_content(sel))


@white_box
class DataIntegrityTests(unittest.TestCase):
    def test_templates_loaded(self):
        tpls = tc.load_templates()
        self.assertTrue(tpls, "templates.json 应非空")
        ids = {str(t["id"]) for t in tpls}
        self.assertSetEqual(ids, {"0", "1", "2"})
        for t in tpls:
            self.assertIn("plugin", t)
            self.assertIn("scene", t)

    def test_catalog_scene_dimensions(self):
        cs = tc.load_catalog_scene()
        for dim in ("traffic", "pedestrian", "ecology", "surface"):
            self.assertIn(dim, cs)

    def test_template_scene_enums_valid(self):
        for t in tc.load_templates():
            sc = t.get("scene", {})
            surf = sc.get("surface", {}).get("surface_style")
            if surf:
                self.assertIn(surf, tc.SURFACE_STYLES)
            ec = sc.get("ecology", {})
            if ec.get("enable") and ec.get("ecology_plot_mode"):
                self.assertIn(ec["ecology_plot_mode"], tc.ECO_MODES)

    def test_template_plugin_assets_are_valid(self):
        # 模板 plugin 里的资产名都应在 catalog 里(validate_selection 不丢弃)
        for t in tc.load_templates():
            cleaned = tc.validate_selection(t["plugin"])
            for cat in tc.ALL_CATS:
                if t["plugin"].get(cat):
                    self.assertEqual(cleaned[cat], t["plugin"][cat],
                                     f"模板{t['id']} {cat} 资产不在 catalog: {t['plugin'][cat]}")

    def test_catalog_items_have_desc_for_llm_cats(self):
        for cat in tc.LLM_CATS:
            items = tc.catalog_items(cat)
            self.assertTrue(items, f"catalog.{cat} 应有条目")
            for asset, desc in items:
                self.assertTrue(asset)
                self.assertTrue(desc, f"{cat}/{asset} 缺少 desc（LLM 映射用）")

    def test_catalog_scene_levels_cover_all_levels(self):
        cs = tc.load_catalog_scene()
        for dim in ("traffic", "pedestrian"):
            levels = cs[dim]["levels"]
            for count_key, mapping in levels.items():
                for level in tc.LEVELS:
                    if level == "none":
                        continue
                    self.assertIn(level, mapping, f"{dim}.{count_key} 缺少档位 {level}")


@white_box
class ValidateSelectionTests(unittest.TestCase):
    def test_drops_assets_not_in_catalog(self):
        raw = {"tree": "NOT_A_REAL_TREE", "bench": "Bench1_Bench_ICity_Default"}
        out = tc.validate_selection(raw)
        self.assertIsNone(out["tree"])
        self.assertEqual(out["bench"], "Bench1_Bench_ICity_Default")

    def test_unknown_categories_stay_none(self):
        out = tc.validate_selection({})
        self.assertTrue(all(v is None for v in out.values()))


@white_box
class HasContentTests(unittest.TestCase):
    def test_true_when_asset_present(self):
        sel = {c: None for c in tc.ALL_CATS}
        sel["tree"] = "Tree1_Tree_ICity_Default"
        sel["_scene"] = {}
        self.assertTrue(tc._has_content(sel))

    def test_true_when_scene_present(self):
        sel = {c: None for c in tc.ALL_CATS}
        sel["_scene"] = {"traffic": {"enable": True, "car_count": 3}}
        self.assertTrue(tc._has_content(sel))

    def test_false_when_all_empty(self):
        sel = {c: None for c in tc.ALL_CATS}
        sel["_scene"] = {}
        self.assertFalse(tc._has_content(sel))


@white_box
class GetApiKeyTests(unittest.TestCase):
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-key", "ICITY_LLM_KEY": ""}, clear=False)
    def test_prefers_deepseek_env_var(self):
        self.assertEqual(tc.get_api_key(), "env-key")

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "", "ICITY_LLM_KEY": "icity-key"}, clear=False)
    def test_falls_back_to_icity_env_var(self):
        self.assertEqual(tc.get_api_key(), "icity-key")


@white_box
class BuildPromptTests(unittest.TestCase):
    def test_system_prompt_includes_llm_catalog_assets(self):
        prompt = tc.build_system_prompt()
        self.assertIn("Tree7_Tree_ICity_Default", prompt)
        self.assertIn("Bench1_Bench_ICity_Default", prompt)

    def test_scene_prompt_block_lists_traffic_levels(self):
        block = tc.build_scene_prompt_block()
        self.assertIn("traffic", block)
        self.assertIn("ecology_mode", block)


@white_box
class LlmParseTests(unittest.TestCase):
    @patch.object(tc, "_http_post_json")
    def test_llm_parse_returns_json_content(self, mock_http):
        mock_http.return_value = {
            "choices": [{"message": {"content": '{"tree":"Tree1_Tree_ICity_Default","scene":{"traffic":"high"}}'}}]
        }
        result = tc.llm_parse("车水马龙", "test-key")
        self.assertEqual(result["tree"], "Tree1_Tree_ICity_Default")
        self.assertEqual(result["scene"]["traffic"], "high")
        mock_http.assert_called_once()
        _args, kwargs = mock_http.call_args
        self.assertIn("/chat/completions", _args[0])
        self.assertEqual(kwargs.get("timeout") or _args[3], tc.LLM_TIMEOUT)

    @patch.object(tc, "_http_post_json", side_effect=TimeoutError("timeout"))
    def test_llm_parse_propagates_http_errors(self, mock_http):
        with self.assertRaises(TimeoutError):
            tc.llm_parse("test", "key")


@white_box
class ParseCommandTests(unittest.TestCase):
    @patch.object(tc, "llm_parse")
    @patch.object(tc, "get_api_key", return_value="test-key")
    def test_uses_llm_when_response_is_valid(self, _mock_key, mock_llm):
        cs = tc.load_catalog_scene()
        expect_cars = cs["traffic"]["levels"]["car_count"]["high"]
        mock_llm.return_value = {
            "tree": "Tree7_Tree_ICity_Default",
            "bench": "NOT_IN_CATALOG",
            "scene": {"traffic": "high", "pedestrian": "none"},
        }
        sel, engine = tc.parse_command("金黄的树，去掉人")
        self.assertEqual(engine, "DeepSeek")
        self.assertEqual(sel["tree"], "Tree7_Tree_ICity_Default")
        self.assertIsNone(sel["bench"])
        self.assertEqual(sel["_scene"]["traffic"]["car_count"], expect_cars)
        self.assertEqual(sel["_scene"]["pedestrian"], {"_clear": True})

    @patch.object(tc, "llm_parse", return_value={"tree": None, "scene": {}})
    @patch.object(tc, "get_api_key", return_value="test-key")
    def test_falls_back_to_rules_when_llm_empty(self, _mock_key, _mock_llm):
        sel, engine = tc.parse_command("把树换成金黄的")
        self.assertEqual(engine, "规则解析")
        self.assertEqual(sel["tree"], "Tree7_Tree_ICity_Default")

    @patch.object(tc, "llm_parse", side_effect=RuntimeError("network down"))
    @patch.object(tc, "get_api_key", return_value="test-key")
    def test_falls_back_to_rules_on_llm_error(self, _mock_key, _mock_llm):
        sel, engine = tc.parse_command("车水马龙、有山有湖")
        self.assertEqual(engine, "规则解析")
        self.assertEqual(sel["_scene"]["ecology"]["ecology_plot_mode"], "LAKE_RING")

    @patch.object(tc, "LLM_ENABLED", False)
    def test_rules_only_when_llm_disabled(self):
        sel, engine = tc.parse_command("步行街没有车")
        self.assertEqual(engine, "规则解析")
        self.assertEqual(sel["_scene"]["traffic"], {"_clear": True})


if __name__ == "__main__":
    unittest.main()

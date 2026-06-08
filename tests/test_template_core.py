# -*- coding: utf-8 -*-
"""模板化模块纯逻辑单元测试（不依赖 Blender）。

测 iCity/smart_city/template_core.py 的关键词解析、档位换算、数据加载。
运行：python tests/test_template_core.py  或  python -m unittest discover tests
"""

import importlib.util
import unittest
from pathlib import Path


def load_template_core():
    module_path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "template_core.py"
    spec = importlib.util.spec_from_file_location("template_core", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tc = load_template_core()


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


if __name__ == "__main__":
    unittest.main()

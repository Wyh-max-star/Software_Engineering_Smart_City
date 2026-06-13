"""Cross-check frontend ``templates.ts`` against plugin ``templates.json``."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from frontend_test_utils import (  # noqa: E402
    ECOLOGY_MODE_LABELS,
    FRONTEND_TS,
    PREVIEW_ASSETS_DIR,
    REPO_ROOT,
    ecology_summary_for_backend,
    first_int,
    parse_frontend_roles,
    parse_frontend_templates,
    resolve_template_id,
)
from test_markers import gray_box  # noqa: E402


def load_template_core():
    module_path = REPO_ROOT / "iCity" / "smart_city" / "template_core.py"
    spec = importlib.util.spec_from_file_location("template_core_parity", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tc = load_template_core()


@gray_box
class FrontendTemplateParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ts_text = FRONTEND_TS.read_text(encoding="utf-8")
        cls.frontend = parse_frontend_templates(cls.ts_text)
        cls.backend = {str(t["id"]): t for t in tc.load_templates()}

    def test_template_count_matches_backend(self):
        self.assertEqual(set(self.frontend.keys()), {str(t["id"]) for t in tc.load_templates()})

    def test_template_ids_and_names_match(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            be = self.backend[tid]
            self.assertEqual(fe["name"], be["name"], tid)
            self.assertEqual(fe["sceneType"], be["sceneType"], tid)

    def test_display_integers_match_json(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            display = self.backend[tid]["display"]
            self.assertEqual(fe["tree_type"], display["tree_type"], tid)
            self.assertEqual(fe["road_texture"], display["road_texture"], tid)
            self.assertEqual(fe["bench_type"], display["bench_type"], tid)

    def test_plugin_values_match_json(self):
        mapping = (
            ("plugin_tree", "tree"),
            ("plugin_road", "road_material"),
            ("plugin_bench", "bench"),
        )
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            plugin = self.backend[tid]["plugin"]
            for fe_key, json_key in mapping:
                self.assertEqual(fe[fe_key], plugin[json_key], f"模板{tid} {json_key} 不一致")

    def test_plugin_assets_exist_in_catalog(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            raw = {
                "tree": fe["plugin_tree"],
                "road_material": fe["plugin_road"],
                "bench": fe["plugin_bench"],
            }
            cleaned = tc.validate_selection(raw)
            for cat, value in raw.items():
                self.assertEqual(cleaned[cat], value, f"模板{tid} {cat} 不在 catalog")

    def test_scene_summary_format_and_counts(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            scene = self.backend[tid]["scene"]
            traffic = scene.get("traffic", {})
            pedestrian = scene.get("pedestrian", {})
            if traffic.get("enable", True):
                self.assertRegex(fe["scene_traffic"], r"\d+\s*辆", tid)
                self.assertEqual(first_int(fe["scene_traffic"]), traffic.get("car_count"), tid)
            if pedestrian.get("enable", True):
                self.assertRegex(fe["scene_pedestrian"], r"\d+\s*人", tid)
                self.assertEqual(first_int(fe["scene_pedestrian"]), pedestrian.get("walker_count"), tid)

    def test_scene_ecology_summary_matches_json(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            ecology = self.backend[tid]["scene"]["ecology"]
            expected = ecology_summary_for_backend(ecology)
            self.assertEqual(fe["scene_ecology"], expected, tid)

    def test_preview_image_files_exist(self):
        for tid in ("0", "1", "2"):
            for kind in ("road", "tree", "bench"):
                path = PREVIEW_ASSETS_DIR / f"{kind}-{tid}.png"
                self.assertTrue(path.is_file(), str(path))

    def test_frontend_roles_match_templates_ts(self):
        self.assertEqual(parse_frontend_roles(self.ts_text), ["modeler", "admin", "analyst"])

    def test_frontend_only_fields_nonempty(self):
        for tid in ("0", "1", "2"):
            fe = self.frontend[tid]
            self.assertTrue(fe["description"].strip(), tid)
            self.assertTrue(fe["fit"].strip(), tid)
            self.assertGreaterEqual(len(re.findall(r"'[^']+'", fe["tags"])), 1, tid)

    def test_get_template_fallback_resolves_to_template_zero(self):
        for unknown in (None, "", "9", "missing"):
            resolved = resolve_template_id(self.frontend, unknown)
            self.assertEqual(resolved, "0")
        self.assertEqual(resolve_template_id(self.frontend, "2"), "2")


@gray_box
class FrontendEcologyLabelRegistryTests(unittest.TestCase):
    def test_ecology_labels_cover_backend_modes(self):
        modes = {t["scene"]["ecology"].get("ecology_plot_mode") for t in tc.load_templates()}
        modes.discard(None)
        for mode in modes:
            if mode == "MOUNTAIN_ONLY":
                continue  # template 1 uses enable=false → "无"
            self.assertIn(mode, ECOLOGY_MODE_LABELS, f"缺少生态模式 {mode} 的前端文案")


if __name__ == "__main__":
    unittest.main()

"""Static contract tests for the React frontend prototype (``App.tsx``)."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from frontend_test_utils import (  # noqa: E402
    APP_ROUTES,
    FRONTEND_APP,
    FRONTEND_TS,
    ROLE_IDS,
    STORAGE_KEYS,
    role_permission,
)
from test_markers import gray_box  # noqa: E402


@gray_box
class FrontendRolePermissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_text = FRONTEND_APP.read_text(encoding="utf-8")

    def test_three_roles_imported_from_templates(self):
        for role in ROLE_IDS:
            self.assertIn(f"type RoleId", FRONTEND_TS.read_text(encoding="utf-8"))
            self.assertIn(f"from './templates'", self.app_text)

    def test_modeler_can_apply_and_enter_blender(self):
        self.assertTrue(role_permission(self.app_text, "modeler", "applyTemplate"))
        self.assertTrue(role_permission(self.app_text, "modeler", "enterBlender"))
        self.assertFalse(role_permission(self.app_text, "modeler", "managePermissions"))

    def test_admin_can_manage_and_review_plugins(self):
        self.assertTrue(role_permission(self.app_text, "admin", "managePermissions"))
        self.assertTrue(role_permission(self.app_text, "admin", "reviewPlugin"))
        self.assertFalse(role_permission(self.app_text, "admin", "enterBlender"))
        self.assertFalse(role_permission(self.app_text, "admin", "applyTemplate"))

    def test_analyst_can_record_acceptance_only(self):
        self.assertTrue(role_permission(self.app_text, "analyst", "recordAcceptance"))
        self.assertFalse(role_permission(self.app_text, "analyst", "enterBlender"))
        self.assertFalse(role_permission(self.app_text, "analyst", "managePermissions"))


@gray_box
class FrontendRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_text = FRONTEND_APP.read_text(encoding="utf-8")

    def test_core_routes_declared(self):
        for route in APP_ROUTES:
            self.assertIn(f'path="{route}"', self.app_text, route)

    def test_plugin_entry_guarded_by_blender_permission(self):
        self.assertIn("canEnterBlender(activeRole)", self.app_text)

    def test_admin_routes_guarded_by_manage_permissions(self):
        self.assertIn("canManagePermissions(activeRole)", self.app_text)


@gray_box
class FrontendWorkflowSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_text = FRONTEND_APP.read_text(encoding="utf-8")

    def test_role_workflows_reference_template_usage(self):
        self.assertIn("模板商城", self.app_text)
        self.assertIn("Apply Template", self.app_text)
        self.assertIn("tree_type", self.app_text)

    def test_analyst_workflow_mentions_template_acceptance(self):
        self.assertIn("recordAcceptance", self.app_text)
        self.assertIn("验收模板能力与插件演示链路", self.app_text)
        self.assertIn("模板指标", self.app_text)

    def test_plugin_entry_exposes_template_integers_and_assets(self):
        for snippet in (
            'label="tree_type"',
            'label="road_texture"',
            'label="bench_type"',
            "pluginValues.tree",
            "pluginValues.road",
            "pluginValues.bench",
        ):
            self.assertIn(snippet, self.app_text)

    def test_local_storage_keys_defined(self):
        for key in STORAGE_KEYS:
            self.assertIn(key, self.app_text)


@gray_box
class FrontendTemplateMarketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_text = FRONTEND_APP.read_text(encoding="utf-8")

    def test_template_market_imports_all_templates(self):
        self.assertIn("templates.filter", self.app_text)
        self.assertIn("getTemplate(", self.app_text)

    def test_selected_template_persisted_for_blender_handoff(self):
        self.assertIn("icity-selected-template", self.app_text)
        self.assertIn("selectedTemplateKey", self.app_text)

    def test_template_search_uses_name_and_tags(self):
        self.assertIn("Search", self.app_text)
        self.assertIn("...template.tags", self.app_text)


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""Black-box tests for layout-control Blender operators (Mock context)."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from mock_helpers import make_mock_context  # noqa: E402
from test_markers import black_box  # noqa: E402
from test_layout_control import (  # noqa: E402
    MockDraftCollection,
    RECTANGLE_GRAPH,
    _edge_item,
    _make_draft_scene,
    _node_item,
)

lc = load_module("layout_control", "iCity/smart_city/layout_control.py")


def _layout_context(**scene_fields):
    scene = _make_draft_scene(RECTANGLE_GRAPH)
    for name, value in scene_fields.items():
        setattr(scene, name, value)
    return make_mock_context(**{k: v for k, v in scene.__dict__.items()})


@black_box
class LayoutOperatorTests(unittest.TestCase):
    def test_add_layout_draft_node_finished(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        ctx = make_mock_context(**scene.__dict__)
        op = lc.ICITY_OT_AddLayoutDraftNode()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertEqual(len(ctx.scene.icity_layout_nodes), 5)

    def test_remove_layout_draft_node_finished(self):
        ctx = _layout_context(icity_layout_node_index=0)
        op = lc.ICITY_OT_RemoveLayoutDraftNode()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertEqual(len(ctx.scene.icity_layout_nodes), 3)

    def test_remove_layout_draft_node_cancelled_without_selection(self):
        ctx = _layout_context(icity_layout_node_index=-1)
        op = lc.ICITY_OT_RemoveLayoutDraftNode()
        self.assertEqual(op.execute(ctx), {"CANCELLED"})

    def test_add_layout_draft_edge_finished(self):
        ctx = _layout_context()
        op = lc.ICITY_OT_AddLayoutDraftEdge()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertEqual(len(ctx.scene.icity_layout_edges), 5)

    def test_add_layout_draft_edge_cancelled_with_few_nodes(self):
        scene = types.SimpleNamespace(
            icity_layout_nodes=MockDraftCollection(_node_item),
            icity_layout_edges=MockDraftCollection(_edge_item),
            icity_layout_edge_index=0,
        )
        lc.add_draft_node(scene)
        ctx = make_mock_context(**scene.__dict__)
        op = lc.ICITY_OT_AddLayoutDraftEdge()
        self.assertEqual(op.execute(ctx), {"CANCELLED"})

    def test_validate_layout_draft_reports_no_errors_for_rectangle(self):
        ctx = _layout_context()
        op = lc.ICITY_OT_ValidateLayoutDraft()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertIn("0 errors", ctx.scene.icity_layout_draft_summary)

    def test_validate_layout_draft_reports_missing_node_error(self):
        ctx = _layout_context()
        ctx.scene.icity_layout_edges[0].end_node_id = "missing"
        op = lc.ICITY_OT_ValidateLayoutDraft()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        self.assertIn("ERROR", ctx.scene.icity_layout_validation_details)

    @patch.object(lc, "populate_layout_draft")
    @patch.object(lc, "write_layout_graph_text")
    @patch.object(lc, "write_validation_details")
    def test_normalize_layout_draft_finished(self, _mock_val, _mock_write, mock_populate):
        ctx = _layout_context(
            icity_layout_merge_distance=0.1,
            icity_layout_intersection_tolerance=0.001,
            icity_layout_minimum_edge_length=0.001,
        )
        op = lc.ICITY_OT_NormalizeLayoutDraft()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        mock_populate.assert_called_once()

    @patch.object(lc, "inspect_icity_base_contract")
    @patch.object(lc, "write_contract_report_text")
    def test_inspect_layout_contract_finished(self, mock_write, mock_inspect):
        mock_inspect.return_value = {
            "vertices": 4,
            "edges": 4,
            "polygons": 1,
            "attributes": [],
            "node_rows": [],
            "edge_rows": [],
            "face_rows": [],
        }
        ctx = make_mock_context()
        op = lc.ICITY_OT_InspectLayoutContract()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        mock_write.assert_called_once()
        self.assertIn("4 nodes", ctx.scene.icity_layout_contract_summary)

    def test_import_layout_sketch_cancelled_without_filepath(self):
        lc.bpy.path.abspath = MagicMock(return_value="")
        ctx = make_mock_context(icity_layout_sketch_path="")
        op = lc.ICITY_OT_ImportLayoutSketch()
        self.assertEqual(op.execute(ctx), {"CANCELLED"})

    @patch.object(lc, "refresh_layout_preview", return_value={"objects": 1})
    @patch.object(lc, "write_validation_details")
    @patch.object(lc, "write_layout_graph_text")
    @patch.object(lc, "populate_layout_draft")
    @patch.object(lc, "parse_layout_graph_json_text", return_value=RECTANGLE_GRAPH)
    @patch.object(lc, "validate_layout_graph", return_value={"errors": [], "warnings": []})
    def test_import_layout_json_finished(
        self, _mock_validate, mock_parse, mock_populate, _mock_write, _mock_val, _mock_preview
    ):
        ctx = make_mock_context(
            icity_layout_json_path="//layout.json",
            icity_layout_nodes=MockDraftCollection(_node_item),
            icity_layout_edges=MockDraftCollection(_edge_item),
            icity_layout_node_index=0,
            icity_layout_edge_index=0,
        )
        lc.bpy.path.abspath = MagicMock(return_value="C:/layout.json")
        op = lc.ICITY_OT_ImportLayoutJSON()
        with patch("builtins.open", MagicMock(return_value=MagicMock(read=lambda: "{}"))):
            self.assertEqual(op.execute(ctx), {"FINISHED"})
        mock_parse.assert_called_once()
        mock_populate.assert_called_once()

    @patch.object(lc, "inspect_icity_base_contract")
    @patch.object(lc, "populate_layout_draft")
    @patch.object(lc, "write_validation_details")
    def test_load_layout_draft_from_base_finished(self, _mock_val, mock_populate, mock_inspect):
        mock_inspect.return_value = {
            "vertices": 4,
            "edges": 4,
            "polygons": 1,
            "attributes": [],
            "node_rows": [{"index": 0, "coordinate": [0, 0, 0]}],
            "edge_rows": [{"index": 0, "vertices": [0, 1], "enabled_as_road": True}],
            "face_rows": [],
        }
        ctx = make_mock_context(
            icity_layout_nodes=MockDraftCollection(_node_item),
            icity_layout_edges=MockDraftCollection(_edge_item),
        )
        op = lc.ICITY_OT_LoadLayoutDraftFromBase()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        mock_populate.assert_called_once()

    @patch.object(lc, "clear_layout_preview")
    @patch.object(lc, "write_contract_report_text")
    @patch.object(lc, "inspect_icity_base_contract")
    @patch.object(lc, "populate_layout_draft")
    @patch.object(lc, "write_layout_graph_text")
    @patch.object(lc, "write_validation_details")
    @patch.object(lc, "replace_icity_base_roads_via_edit_mode")
    @patch.object(lc, "normalize_layout_graph")
    @patch.object(lc, "build_layout_graph_from_draft")
    def test_apply_layout_draft_finished(
        self,
        mock_from_draft,
        mock_normalize,
        mock_replace,
        _mock_val,
        _mock_write,
        _mock_populate,
        _mock_inspect,
        _mock_contract,
        _mock_clear,
    ):
        mock_from_draft.return_value = RECTANGLE_GRAPH
        mock_normalize.return_value = (
            RECTANGLE_GRAPH,
            {
                "merged_nodes": 0,
                "intersection_nodes": 0,
                "point_on_edge_splits": 0,
                "split_edges": 0,
                "removed_invalid_edges": 0,
                "removed_short_edges": 0,
                "removed_duplicate_edges": 0,
            },
        )
        mock_replace.return_value = {
            "final_counts": (4, 4, 1),
            "enabled_roads": 4,
            "disabled_roads": 0,
            "procedural_faces": 1,
        }
        ctx = make_mock_context(
            icity_layout_merge_distance=0.1,
            icity_layout_intersection_tolerance=0.001,
            icity_layout_minimum_edge_length=0.001,
            icity_layout_nodes=MockDraftCollection(_node_item),
            icity_layout_edges=MockDraftCollection(_edge_item),
        )
        op = lc.ICITY_OT_ApplyLayoutDraftToBase()
        self.assertEqual(op.execute(ctx), {"FINISHED"})
        mock_replace.assert_called_once()

    @patch.object(lc, "build_layout_graph_from_draft")
    def test_apply_layout_draft_cancelled_on_validation_error(self, mock_from_draft):
        mock_from_draft.return_value = {
            "nodes": [{"id": "n0", "source_index": -1, "x": 0, "y": 0, "z": 0}],
            "edges": [{"id": "e0", "source_index": -1, "start": "n0", "end": "missing", "enabled_as_road": True}],
            "faces": [],
        }
        ctx = make_mock_context(
            icity_layout_merge_distance=0.1,
            icity_layout_intersection_tolerance=0.001,
            icity_layout_minimum_edge_length=0.001,
            icity_layout_nodes=MockDraftCollection(_node_item),
            icity_layout_edges=MockDraftCollection(_edge_item),
        )
        op = lc.ICITY_OT_ApplyLayoutDraftToBase()
        self.assertEqual(op.execute(ctx), {"CANCELLED"})


if __name__ == "__main__":
    unittest.main()

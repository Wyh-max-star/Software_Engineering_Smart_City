# -*- coding: utf-8 -*-
"""Unit tests for layout_control: inspect, CRUD draft, validate, normalize, export."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from test_markers import gray_box, white_box  # noqa: E402

lc = load_module("layout_control", "iCity/smart_city/layout_control.py")

RECTANGLE_JSON = """
{
  "version": 1,
  "nodes": [
    {"id": "n0", "x": 0, "y": 0, "z": 0},
    {"id": "n1", "x": 100, "y": 0, "z": 0},
    {"id": "n2", "x": 100, "y": 100, "z": 0},
    {"id": "n3", "x": 0, "y": 100, "z": 0}
  ],
  "edges": [
    {"id": "e0", "start": "n0", "end": "n1", "enabled_as_road": true},
    {"id": "e1", "start": "n1", "end": "n2", "enabled_as_road": true},
    {"id": "e2", "start": "n2", "end": "n3", "enabled_as_road": true},
    {"id": "e3", "start": "n3", "end": "n0", "enabled_as_road": true}
  ],
  "faces": []
}
"""


def _rectangle_graph(*, first_edge_enabled: bool = True) -> dict:
    return {
        "version": 1,
        "source": "test",
        "nodes": [
            {"id": "n0", "source_index": 0, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": "n1", "source_index": 1, "x": 100.0, "y": 0.0, "z": 0.0},
            {"id": "n2", "source_index": 2, "x": 100.0, "y": 100.0, "z": 0.0},
            {"id": "n3", "source_index": 3, "x": 0.0, "y": 100.0, "z": 0.0},
        ],
        "edges": [
            {"id": "e0", "source_index": 0, "start": "n0", "end": "n1", "enabled_as_road": first_edge_enabled},
            {"id": "e1", "source_index": 1, "start": "n1", "end": "n2", "enabled_as_road": True},
            {"id": "e2", "source_index": 2, "start": "n2", "end": "n3", "enabled_as_road": True},
            {"id": "e3", "source_index": 3, "start": "n3", "end": "n0", "enabled_as_road": True},
        ],
        "faces": [
            {"id": "f0", "source_index": -1, "vertices": ["n0", "n1", "n2", "n3"]},
        ],
    }


RECTANGLE_GRAPH = _rectangle_graph()


class MockDraftCollection:
    def __init__(self, factory):
        self._items: list = []
        self._factory = factory

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def add(self):
        item = self._factory()
        self._items.append(item)
        return item

    def clear(self):
        self._items.clear()

    def remove(self, index):
        del self._items[index]


def _node_item(**fields):
    return types.SimpleNamespace(
        node_id="",
        source_index=-1,
        x=0.0,
        y=0.0,
        z=0.0,
        **fields,
    )


def _edge_item(**fields):
    return types.SimpleNamespace(
        edge_id="",
        source_index=-1,
        start_node_id="",
        end_node_id="",
        enabled_as_road=True,
        **fields,
    )


def _make_draft_scene(graph: dict | None = None) -> types.SimpleNamespace:
    scene = types.SimpleNamespace(
        icity_layout_nodes=MockDraftCollection(_node_item),
        icity_layout_edges=MockDraftCollection(_edge_item),
        icity_layout_node_index=0,
        icity_layout_edge_index=0,
        icity_layout_validation_details="",
        icity_layout_draft_summary="",
    )
    if graph:
        lc.populate_layout_draft(scene, graph)
    return scene


def _mock_mesh(*, vertices=None, edges=None, polygons=None, road_deleted=None):
    vertices = vertices or [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0)]
    edges = edges or [(0, 1), (1, 2)]
    polygons = polygons or [(0, 1, 2)]

    class _Vertex:
        def __init__(self, co):
            self.co = co

    class _Edge:
        def __init__(self, pair):
            self.vertices = pair

    class _Polygon:
        def __init__(self, loop):
            self.vertices = loop

    class _AttrItem:
        def __init__(self, value):
            self.value = value

    class _Attribute:
        def __init__(self, name, domain, data_type, data):
            self.name = name
            self.domain = domain
            self.data_type = data_type
            self.data = data

    mesh = types.SimpleNamespace(
        vertices=[_Vertex(co) for co in vertices],
        edges=[_Edge(pair) for pair in edges],
        polygons=[_Polygon(loop) for loop in polygons],
        attributes=[],
    )
    if road_deleted is not None:
        mesh.attributes.append(
            _Attribute(
                "Road del",
                "EDGE",
                "BOOLEAN",
                [_AttrItem(flag) for flag in road_deleted],
            )
        )
    return mesh


@white_box
class InspectMeshContractTests(unittest.TestCase):
    def test_inspect_mesh_contract_exports_node_coordinates(self):
        mesh = _mock_mesh(
            vertices=[(1.0, 2.0, 0.0), (5.0, 6.0, 0.0)],
            edges=[(0, 1)],
            polygons=[],
        )
        report = lc.inspect_mesh_contract(mesh)
        self.assertEqual(report["vertices"], 2)
        self.assertEqual(report["node_rows"][0]["coordinate"], [1.0, 2.0, 0.0])
        self.assertEqual(report["node_rows"][1]["coordinate"], [5.0, 6.0, 0.0])
        self.assertEqual(report["edge_rows"][0]["vertices"], [0, 1])

    def test_road_del_attribute_inverts_enabled_as_road(self):
        mesh = _mock_mesh(edges=[(0, 1), (1, 2)], road_deleted=[True, False])
        report = lc.inspect_mesh_contract(mesh)
        self.assertFalse(report["edge_rows"][0]["enabled_as_road"])
        self.assertTrue(report["edge_rows"][1]["enabled_as_road"])


@white_box
class LayoutGraphExportTests(unittest.TestCase):
    def test_build_layout_graph_export_maps_nodes_and_edges(self):
        report = {
            "node_rows": [
                {"index": 0, "coordinate": [0.0, 0.0, 0.0]},
                {"index": 1, "coordinate": [20.0, 0.0, 0.0]},
            ],
            "edge_rows": [
                {"index": 0, "vertices": [0, 1], "enabled_as_road": True},
            ],
            "face_rows": [],
        }
        graph = lc.build_layout_graph_export(report)
        self.assertEqual(graph["nodes"][0]["id"], "n0")
        self.assertEqual(graph["nodes"][1]["x"], 20.0)
        self.assertEqual(graph["edges"][0]["start"], "n0")
        self.assertEqual(graph["edges"][0]["end"], "n1")
        self.assertTrue(graph["edges"][0]["enabled_as_road"])


@white_box
class LayoutJsonParseTests(unittest.TestCase):
    def test_parse_rectangle_json(self):
        graph = lc.parse_layout_graph_json_text(RECTANGLE_JSON)
        self.assertEqual(len(graph["nodes"]), 4)
        self.assertEqual(len(graph["edges"]), 4)
        self.assertEqual(graph["nodes"][1]["x"], 100.0)

    def test_parse_rejects_missing_node_reference(self):
        bad = """
        {
          "version": 1,
          "nodes": [{"id": "n0", "x": 0, "y": 0, "z": 0}],
          "edges": [{"id": "e0", "start": "n0", "end": "missing"}],
          "faces": []
        }
        """
        with self.assertRaises(ValueError):
            lc.parse_layout_graph_json_text(bad)

    def test_parse_rejects_non_finite_coordinates(self):
        bad = RECTANGLE_JSON.replace('"x": 0', '"x": NaN', 1)
        with self.assertRaises(ValueError):
            lc.parse_layout_graph_json_text(bad)


@white_box
class LayoutValidationTests(unittest.TestCase):
    def test_valid_rectangle_has_no_errors(self):
        result = lc.validate_layout_graph(RECTANGLE_GRAPH)
        self.assertEqual(result["errors"], [])

    def test_missing_end_node_is_error(self):
        graph = {
            "nodes": [{"id": "n0", "x": 0, "y": 0, "z": 0}],
            "edges": [{"id": "e0", "start": "n0", "end": "missing"}],
            "faces": [],
        }
        result = lc.validate_layout_graph(graph)
        self.assertTrue(any("missing end node" in err for err in result["errors"]))

    def test_duplicate_undirected_edge_is_error(self):
        graph = {
            "nodes": [
                {"id": "n0", "x": 0, "y": 0, "z": 0},
                {"id": "n1", "x": 10, "y": 0, "z": 0},
            ],
            "edges": [
                {"id": "e0", "start": "n0", "end": "n1"},
                {"id": "e1", "start": "n1", "end": "n0"},
            ],
            "faces": [],
        }
        result = lc.validate_layout_graph(graph)
        self.assertTrue(any("Duplicate undirected edge" in err for err in result["errors"]))


@gray_box
class LayoutDraftCrudTests(unittest.TestCase):
    def test_populate_and_read_back_node_coordinates(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        graph = lc.build_layout_graph_from_draft(scene)
        self.assertEqual(len(graph["nodes"]), 4)
        self.assertEqual(graph["nodes"][2]["y"], 100.0)
        self.assertEqual(len(graph["edges"]), 4)

    def test_update_node_coordinates_in_draft(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        scene.icity_layout_nodes[0].x = 25.0
        scene.icity_layout_nodes[0].y = 30.0
        graph = lc.build_layout_graph_from_draft(scene)
        self.assertEqual(graph["nodes"][0]["x"], 25.0)
        self.assertEqual(graph["nodes"][0]["y"], 30.0)

    def test_add_node_assigns_unique_id(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        index = lc.add_draft_node(scene)
        self.assertEqual(index, 4)
        self.assertEqual(scene.icity_layout_nodes[index].node_id, "n4")

    def test_add_edge_connects_first_two_nodes(self):
        scene = _make_draft_scene()
        lc.add_draft_node(scene)
        lc.add_draft_node(scene)
        lc.add_draft_edge(scene)
        edge = scene.icity_layout_edges[0]
        self.assertEqual(edge.start_node_id, "n0")
        self.assertEqual(edge.end_node_id, "n1")

    def test_remove_node_deletes_connected_edges(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        node_id, affected = lc.remove_draft_node(scene, 0)
        self.assertEqual(node_id, "n0")
        self.assertEqual(affected, 2)
        self.assertEqual(len(scene.icity_layout_nodes), 3)
        self.assertEqual(len(scene.icity_layout_edges), 2)
        remaining_starts = {edge.start_node_id for edge in scene.icity_layout_edges}
        remaining_ends = {edge.end_node_id for edge in scene.icity_layout_edges}
        self.assertNotIn("n0", remaining_starts | remaining_ends)

    def test_remove_edge_keeps_nodes(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        edge_id = lc.remove_draft_edge(scene, 0)
        self.assertEqual(edge_id, "e0")
        self.assertEqual(len(scene.icity_layout_nodes), 4)
        self.assertEqual(len(scene.icity_layout_edges), 3)

    def test_toggle_edge_enabled_as_road(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        scene.icity_layout_edges[0].enabled_as_road = False
        graph = lc.build_layout_graph_from_draft(scene)
        self.assertFalse(graph["edges"][0]["enabled_as_road"])


@white_box
class LayoutNormalizeTests(unittest.TestCase):
    def test_crossing_roads_gain_shared_intersection_node(self):
        graph = {
            "version": 1,
            "source": "test",
            "nodes": [
                {"id": "n0", "source_index": -1, "x": 0.0, "y": 10.0, "z": 0.0},
                {"id": "n1", "source_index": -1, "x": 20.0, "y": 10.0, "z": 0.0},
                {"id": "n2", "source_index": -1, "x": 10.0, "y": 0.0, "z": 0.0},
                {"id": "n3", "source_index": -1, "x": 10.0, "y": 20.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "source_index": -1, "start": "n0", "end": "n1", "enabled_as_road": True},
                {"id": "e1", "source_index": -1, "start": "n2", "end": "n3", "enabled_as_road": True},
            ],
            "faces": [],
        }
        normalized, stats = lc.normalize_layout_graph(graph)
        self.assertGreaterEqual(stats["intersection_nodes"], 1)
        self.assertGreater(len(normalized["edges"]), 2)
        validation = lc.validate_layout_graph(normalized)
        self.assertEqual(validation["errors"], [])

    def test_merge_nearby_nodes(self):
        graph = {
            "version": 1,
            "source": "test",
            "nodes": [
                {"id": "n0", "source_index": -1, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "source_index": -1, "x": 0.05, "y": 0.0, "z": 0.0},
                {"id": "n2", "source_index": -1, "x": 10.0, "y": 0.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "source_index": -1, "start": "n0", "end": "n2", "enabled_as_road": True},
                {"id": "e1", "source_index": -1, "start": "n1", "end": "n2", "enabled_as_road": True},
            ],
            "faces": [],
        }
        normalized, stats = lc.normalize_layout_graph(graph, merge_distance=0.1)
        self.assertGreaterEqual(stats["merged_nodes"], 1)
        self.assertEqual(len(normalized["nodes"]), 2)


@white_box
class LayoutFaceInferenceTests(unittest.TestCase):
    def test_rectangle_graph_infers_one_face_loop(self):
        loops = lc.infer_face_loops_from_graph(RECTANGLE_GRAPH)
        self.assertEqual(len(loops), 1)
        self.assertEqual(len(loops[0]), 4)

    def test_build_layout_graph_from_draft_includes_inferred_faces(self):
        scene = _make_draft_scene(RECTANGLE_GRAPH)
        graph = lc.build_layout_graph_from_draft(scene)
        self.assertEqual(len(graph["faces"]), 1)


@white_box
class LayoutMeshPayloadTests(unittest.TestCase):
    def test_build_layout_mesh_payload_maps_vertices_and_edges(self):
        payload = lc.build_layout_mesh_payload(RECTANGLE_GRAPH)
        self.assertEqual(len(payload["vertices"]), 4)
        self.assertEqual(len(payload["edges"]), 4)
        self.assertEqual(payload["vertices"][1], (100.0, 0.0, 0.0))
        self.assertTrue(all(payload["edge_road_enabled"]))


@white_box
class LayoutApplyPayloadTests(unittest.TestCase):
    def test_apply_payload_includes_oriented_faces_for_enabled_road_loop(self):
        payload = lc.build_layout_apply_payload(RECTANGLE_GRAPH)
        self.assertEqual(len(payload["faces"]), 1)
        self.assertEqual(len(payload["faces"][0]), 4)

    def test_disabled_edge_removes_block_face_from_apply_payload(self):
        payload = lc.build_layout_apply_payload(_rectangle_graph(first_edge_enabled=False))
        self.assertEqual(len(payload["faces"]), 0)

    def test_orient_face_loop_up_keeps_positive_signed_area(self):
        vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]
        ccw = lc.orient_face_loop_up(vertices, (0, 1, 2, 3))
        cw = lc.orient_face_loop_up(vertices, (3, 2, 1, 0))
        self.assertEqual(ccw, (0, 1, 2, 3))
        self.assertEqual(cw, (0, 1, 2, 3))


@white_box
class LayoutUtilityTests(unittest.TestCase):
    def test_next_unique_id_skips_existing(self):
        self.assertEqual(lc.next_unique_id({"n0", "n1"}, "n"), "n2")

    def test_group_attributes_by_domain(self):
        report = {
            "attributes": [
                {"name": "Road del", "domain": "EDGE"},
                {"name": "space type", "domain": "FACE"},
            ]
        }
        grouped = lc.group_attributes_by_domain(report)
        self.assertIn("EDGE", grouped)
        self.assertEqual(len(grouped["EDGE"]), 1)

    def test_format_normalization_summary_mentions_merged_nodes(self):
        summary = lc.format_normalization_summary({"merged_nodes": 2, "intersection_nodes": 1, "split_edges": 1,
                                                   "point_on_edge_splits": 0, "removed_invalid_edges": 0,
                                                   "removed_short_edges": 0, "removed_duplicate_edges": 0})
        self.assertIn("Merged 2 nodes", summary)


@white_box
class LayoutPreviewGeometryTests(unittest.TestCase):
    def test_preview_geometry_contains_nodes_and_roads(self):
        geometry = lc.build_layout_preview_geometry(RECTANGLE_GRAPH)
        self.assertGreater(len(geometry["nodes"]["vertices"]), 0)
        self.assertGreater(len(geometry["roads"]["vertices"]), 0)


if __name__ == "__main__":
    unittest.main()

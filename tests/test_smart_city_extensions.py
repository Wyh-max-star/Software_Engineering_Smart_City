import importlib.util
import sys
import types
import unittest
from pathlib import Path


class Vector:
    def __init__(self, values):
        if len(values) == 2:
            self.x, self.y = values
            self.z = 0.0
        else:
            self.x, self.y, self.z = values

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, scalar):
        return Vector((self.x * scalar, self.y * scalar, self.z * scalar))

    __rmul__ = __mul__

    def __neg__(self):
        return Vector((-self.x, -self.y, -self.z))

    @property
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    @property
    def length_squared(self):
        return self.x**2 + self.y**2 + self.z**2

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def normalized(self):
        magnitude = self.length
        if magnitude == 0.0:
            return Vector((0.0, 0.0, 0.0))
        return Vector((self.x / magnitude, self.y / magnitude, self.z / magnitude))

    def copy(self):
        return Vector((self.x, self.y, self.z))


class StrictVector(Vector):
    def __init__(self, values):
        self._dimensions = len(values)
        super().__init__(values)

    def _check_same_dimensions(self, other):
        if getattr(other, "_dimensions", self._dimensions) != self._dimensions:
            raise TypeError("Vector addition: vectors must have the same dimensions for this operation")

    def __add__(self, other):
        self._check_same_dimensions(other)
        return StrictVector(
            (self.x + other.x, self.y + other.y) if self._dimensions == 2 else (self.x + other.x, self.y + other.y, self.z + other.z)
        )

    def __sub__(self, other):
        self._check_same_dimensions(other)
        return StrictVector(
            (self.x - other.x, self.y - other.y) if self._dimensions == 2 else (self.x - other.x, self.y - other.y, self.z - other.z)
        )

    def __mul__(self, scalar):
        return StrictVector((self.x * scalar, self.y * scalar) if self._dimensions == 2 else (self.x * scalar, self.y * scalar, self.z * scalar))

    __rmul__ = __mul__

    def __neg__(self):
        return StrictVector((-self.x, -self.y) if self._dimensions == 2 else (-self.x, -self.y, -self.z))

    def dot(self, other):
        self._check_same_dimensions(other)
        return super().dot(other)

    def normalized(self):
        magnitude = self.length
        if magnitude == 0.0:
            return StrictVector((0.0, 0.0) if self._dimensions == 2 else (0.0, 0.0, 0.0))
        return StrictVector(
            (self.x / magnitude, self.y / magnitude)
            if self._dimensions == 2
            else (self.x / magnitude, self.y / magnitude, self.z / magnitude)
        )

    def copy(self):
        return StrictVector((self.x, self.y) if self._dimensions == 2 else (self.x, self.y, self.z))


def install_blender_stubs(vector_cls=Vector):
    bpy = types.ModuleType("bpy")
    bpy.data = types.SimpleNamespace()
    bpy.context = types.SimpleNamespace()

    props = types.ModuleType("bpy.props")
    for name in ("BoolProperty", "CollectionProperty", "EnumProperty", "FloatProperty", "IntProperty", "PointerProperty", "StringProperty"):
        setattr(props, name, lambda *args, **kwargs: None)

    bpy_types = types.ModuleType("bpy.types")
    for name in ("Operator", "Panel", "PropertyGroup", "UIList", "Collection", "Object", "Material", "Action", "Node"):
        setattr(bpy_types, name, type(name, (), {}))

    mathutils = types.ModuleType("mathutils")
    mathutils.Vector = vector_cls
    mathutils.noise = types.SimpleNamespace(fractal=lambda *args, **kwargs: 0.0, turbulence=lambda *args, **kwargs: 0.0)

    sys.modules["bpy"] = bpy
    sys.modules["bpy.props"] = props
    sys.modules["bpy.types"] = bpy_types
    sys.modules["mathutils"] = mathutils


def load_module(name, relative_path, *, vector_cls=Vector):
    install_blender_stubs(vector_cls)
    module_path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def serialize_positions(positions):
    return [(point.x, point.y, point.z, rotation) for point, rotation in positions]


class SmartCityExtensionTests(unittest.TestCase):
    def test_traffic_layout_stays_outside_city_radius(self):
        traffic_extension = load_module("traffic_extension_layout", "iCity/smart_city/traffic_extension.py")
        settings = types.SimpleNamespace(
            traffic_outer_offset=10.0,
            traffic_lane_gap=2.4,
            pedestrian_outer_gap=3.2,
            pedestrian_lane_gap=1.6,
        )

        layout = traffic_extension.compute_traffic_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)

        self.assertGreaterEqual(layout["vehicle_lane_inner_x"], 40.0)
        self.assertGreaterEqual(layout["vehicle_lane_inner_y"], 35.0)
        self.assertGreater(layout["vehicle_lane_outer_x"], layout["vehicle_lane_inner_x"])
        self.assertGreater(layout["pedestrian_lane_inner_x"], layout["vehicle_lane_outer_x"])

    def test_vehicle_type_sequence_balances_car_taxi_bus(self):
        traffic_extension = load_module("traffic_extension_vehicle_sequence", "iCity/smart_city/traffic_extension.py")
        settings = types.SimpleNamespace(
            car_count=4,
            taxi_count=2,
            bus_count=1,
        )

        sequence = traffic_extension.vehicle_type_sequence(settings)

        self.assertEqual(len(sequence), 7)
        self.assertEqual(sequence.count("CAR"), 4)
        self.assertEqual(sequence.count("TAXI"), 2)
        self.assertEqual(sequence.count("BUS"), 1)
        self.assertEqual(sequence[0], "BUS")

    def test_clear_traffic_module_only_removes_traffic_collections(self):
        traffic_extension = load_module("traffic_extension_clear", "iCity/smart_city/traffic_extension.py")
        calls = []

        traffic_extension.remove_collection_recursive = lambda collection: calls.append(collection.name)
        traffic_extension.bpy.data.collections = {
            traffic_extension.TRAFFIC_ROOT_COLLECTION: types.SimpleNamespace(name=traffic_extension.TRAFFIC_ROOT_COLLECTION),
            "ICity Ecology": types.SimpleNamespace(name="ICity Ecology"),
        }

        traffic_extension.clear_traffic()

        self.assertEqual(calls, [traffic_extension.TRAFFIC_ROOT_COLLECTION])

    def test_generate_traffic_module_rejects_invalid_frame_range(self):
        traffic_extension = load_module("traffic_extension_invalid_frames", "iCity/smart_city/traffic_extension.py")
        settings = types.SimpleNamespace(
            animation_start=20,
            animation_end=20,
        )
        context = types.SimpleNamespace(scene=types.SimpleNamespace(icity_traffic_settings=settings))
        operator = traffic_extension.ICITY_OT_GenerateTraffic()
        reports = []
        operator.report = lambda level, message: reports.append((level, message))

        result = operator.execute(context)

        self.assertEqual(result, {"CANCELLED"})
        self.assertTrue(any("End Frame" in message for _, message in reports))

    def test_traffic_module_registers_panel_and_operators(self):
        traffic_extension = load_module("traffic_extension_classes", "iCity/smart_city/traffic_extension.py")

        class_names = [cls.__name__ for cls in traffic_extension.CLASSES]

        self.assertIn("ICITY_OT_GenerateTraffic", class_names)
        self.assertIn("ICITY_OT_ClearTraffic", class_names)
        self.assertIn("ICITY_PT_TrafficPanel", class_names)

    def test_extract_road_edge_chains_ignores_removed_edges(self):
        traffic_extension = load_module("traffic_extension_road_chains", "iCity/smart_city/traffic_extension.py")

        vertices = [
            Vector((0.0, 0.0, 0.0)),
            Vector((5.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((15.0, 0.0, 0.0)),
        ]
        edge_vertex_indices = [(0, 1), (1, 2), (2, 3)]
        road_deleted_flags = [False, False, True]

        chains = traffic_extension.extract_road_edge_chains(vertices, edge_vertex_indices, road_deleted_flags)

        self.assertEqual(len(chains), 1)
        self.assertEqual([(point.x, point.y, point.z) for point in chains[0]], [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0), (10.0, 0.0, 0.0)])

    def test_layout_contract_inspector_reports_mesh_attributes(self):
        layout_control = load_module("layout_control_contract", "iCity/smart_city/layout_control.py")

        class BlenderPropertyArray:
            def __iter__(self):
                return iter((1.0, 2.0, 3.0))

        class BlenderVector:
            x = 5.0
            y = 0.0
            z = 0.0

        mesh = types.SimpleNamespace(
            vertices=[
                types.SimpleNamespace(co=(0.0, 0.0, 0.0)),
                types.SimpleNamespace(co=BlenderVector()),
                types.SimpleNamespace(co=(5.0, 5.0, 0.0)),
            ],
            edges=[
                types.SimpleNamespace(vertices=(0, 1)),
                types.SimpleNamespace(vertices=(1, 2)),
            ],
            polygons=[types.SimpleNamespace(vertices=(0, 1, 2))],
            attributes=[
                types.SimpleNamespace(
                    name="Road del",
                    domain="EDGE",
                    data_type="BOOLEAN",
                    data=[
                        types.SimpleNamespace(value=False),
                        types.SimpleNamespace(value=True),
                    ],
                ),
                types.SimpleNamespace(
                    name="space type",
                    domain="FACE",
                    data_type="INT",
                    data=[types.SimpleNamespace(value=0)],
                ),
                types.SimpleNamespace(
                    name="position sample",
                    domain="POINT",
                    data_type="FLOAT_VECTOR",
                    data=[types.SimpleNamespace(value=BlenderPropertyArray())],
                ),
            ],
        )

        report = layout_control.inspect_mesh_contract(mesh)

        self.assertEqual(report["vertices"], 3)
        self.assertEqual(report["edges"], 2)
        self.assertEqual(report["polygons"], 1)
        self.assertEqual(report["attributes"][0]["name"], "Road del")
        self.assertEqual(report["attributes"][0]["samples"], [False, True])
        self.assertEqual(report["attributes"][1]["name"], "space type")
        self.assertEqual(report["attributes"][2]["samples"], [[1.0, 2.0, 3.0]])
        self.assertEqual(report["node_rows"][1]["coordinate"], [5.0, 0.0, 0.0])
        self.assertEqual(report["edge_rows"][0]["vertices"], [0, 1])
        self.assertTrue(report["edge_rows"][0]["enabled_as_road"])
        self.assertFalse(report["edge_rows"][1]["enabled_as_road"])
        self.assertEqual(report["face_rows"][0]["vertices"], [0, 1, 2])
        layout_control.format_contract_report(report)

    def test_layout_coordinate_components_tolerates_unexpected_values(self):
        layout_control = load_module("layout_control_coordinates", "iCity/smart_city/layout_control.py")

        self.assertEqual(layout_control._coordinate_components("not-a-coordinate"), (0.0, 0.0, 0.0))
        self.assertEqual(layout_control._coordinate_components(("1.5", 2, None)), (1.5, 2.0, 0.0))

    def test_layout_control_registers_phase_zero_panel_and_operator(self):
        layout_control = load_module("layout_control_classes", "iCity/smart_city/layout_control.py")

        class_names = [cls.__name__ for cls in layout_control.CLASSES]

        self.assertIn("ICITY_OT_InspectLayoutContract", class_names)
        self.assertIn("ICITY_OT_ExportLayoutGraph", class_names)
        self.assertIn("ICITY_OT_LoadLayoutDraftFromBase", class_names)
        self.assertIn("ICITY_OT_ExportLayoutDraft", class_names)
        self.assertIn("ICITY_OT_AddLayoutDraftNode", class_names)
        self.assertIn("ICITY_OT_RemoveLayoutDraftNode", class_names)
        self.assertIn("ICITY_OT_AddLayoutDraftEdge", class_names)
        self.assertIn("ICITY_OT_RemoveLayoutDraftEdge", class_names)
        self.assertIn("ICITY_OT_ValidateLayoutDraft", class_names)
        self.assertIn("ICITY_OT_NormalizeLayoutDraft", class_names)
        self.assertIn("ICITY_OT_RefreshLayoutDraftPreview", class_names)
        self.assertIn("ICITY_OT_ClearLayoutDraftPreview", class_names)
        self.assertNotIn("ICITY_OT_ApplyLayoutDraftToBase", class_names)
        self.assertIn("ICITY_UL_LayoutNodeList", class_names)
        self.assertIn("ICITY_UL_LayoutEdgeList", class_names)
        self.assertIn("ICITY_PT_LayoutControlPanel", class_names)

    def test_layout_contract_summary_groups_domains_and_known_attributes(self):
        layout_control = load_module("layout_control_summary", "iCity/smart_city/layout_control.py")
        report = {
            "attributes": [
                {"name": "Road del", "domain": "EDGE", "data_type": "BOOLEAN", "length": 4},
                {"name": "Road lanes width", "domain": "EDGE", "data_type": "FLOAT", "length": 4},
                {"name": "space type", "domain": "FACE", "data_type": "INT", "length": 1},
                {"name": "custom", "domain": "POINT", "data_type": "FLOAT", "length": 4},
            ]
        }

        grouped = layout_control.group_attributes_by_domain(report)
        known = layout_control.key_attribute_status(report)

        self.assertEqual(len(grouped["EDGE"]), 2)
        self.assertEqual(len(grouped["FACE"]), 1)
        self.assertEqual(len(grouped["POINT"]), 1)
        self.assertEqual(
            [attribute["name"] for attribute in known],
            ["Road del", "Road lanes width", "space type"],
        )

    def test_layout_graph_export_uses_stable_node_and_edge_ids(self):
        layout_control = load_module("layout_control_export", "iCity/smart_city/layout_control.py")
        report = {
            "node_rows": [
                {"index": 0, "coordinate": [0.0, 0.0, 0.0]},
                {"index": 1, "coordinate": [10.0, 0.0, 0.0]},
            ],
            "edge_rows": [
                {"index": 0, "vertices": [0, 1], "enabled_as_road": True},
            ],
            "face_rows": [
                {"index": 0, "vertices": [0, 1]},
            ],
        }

        graph = layout_control.build_layout_graph_export(report)

        self.assertEqual(graph["version"], 1)
        self.assertEqual(graph["source"], layout_control.ICITY_BASE_OBJECT)
        self.assertEqual(graph["nodes"][0]["id"], "n0")
        self.assertEqual(graph["nodes"][1]["x"], 10.0)
        self.assertEqual(graph["edges"][0]["id"], "e0")
        self.assertEqual(graph["edges"][0]["start"], "n0")
        self.assertEqual(graph["edges"][0]["end"], "n1")
        self.assertTrue(graph["edges"][0]["enabled_as_road"])
        self.assertEqual(graph["faces"][0]["vertices"], ["n0", "n1"])
        layout_control.format_layout_graph_export(graph)

    def test_layout_graph_validation_reports_missing_nodes_and_self_loops(self):
        layout_control = load_module("layout_control_validate", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": 0.0, "y": 0.0},
                {"id": "n0", "x": 1.0, "y": 0.0},
            ],
            "edges": [
                {"id": "e0", "start": "n0", "end": "n0"},
                {"id": "e1", "start": "n0", "end": "missing"},
                {"id": "e2", "start": "n0", "end": "missing"},
            ],
            "faces": [],
        }

        validation = layout_control.validate_layout_graph(graph)

        self.assertTrue(any("Duplicate node id" in error for error in validation["errors"]))
        self.assertTrue(any("Self-loop edge" in error for error in validation["errors"]))
        self.assertTrue(any("missing end node" in error for error in validation["errors"]))
        self.assertTrue(any("Duplicate undirected edge" in error for error in validation["errors"]))
        self.assertTrue(validation["warnings"])

    def test_layout_draft_populates_and_exports_scene_collections(self):
        layout_control = load_module("layout_control_draft", "iCity/smart_city/layout_control.py")

        class FakeCollection(list):
            def add(self):
                item = types.SimpleNamespace()
                self.append(item)
                return item

            def remove(self, index):
                del self[index]

        scene = types.SimpleNamespace(
            icity_layout_nodes=FakeCollection(),
            icity_layout_edges=FakeCollection(),
        )
        graph = {
            "nodes": [
                {"id": "n0", "source_index": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "source_index": 1, "x": 10.0, "y": 0.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "source_index": 0, "start": "n0", "end": "n1", "enabled_as_road": True},
            ],
        }

        layout_control.populate_layout_draft(scene, graph)
        exported = layout_control.build_layout_graph_from_draft(scene)

        self.assertEqual(len(scene.icity_layout_nodes), 2)
        self.assertEqual(scene.icity_layout_nodes[1].node_id, "n1")
        self.assertEqual(scene.icity_layout_nodes[1].x, 10.0)
        self.assertEqual(len(scene.icity_layout_edges), 1)
        self.assertEqual(scene.icity_layout_edges[0].start_node_id, "n0")
        self.assertEqual(exported["nodes"][1]["id"], "n1")
        self.assertEqual(exported["edges"][0]["end"], "n1")

    def test_layout_draft_export_infers_closed_face_loops(self):
        layout_control = load_module("layout_control_draft_faces", "iCity/smart_city/layout_control.py")

        class FakeCollection(list):
            def add(self):
                item = types.SimpleNamespace()
                self.append(item)
                return item

            def remove(self, index):
                del self[index]

        scene = types.SimpleNamespace(
            icity_layout_nodes=FakeCollection(),
            icity_layout_edges=FakeCollection(),
        )
        graph = {
            "nodes": [
                {"id": "n0", "source_index": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "source_index": 1, "x": 10.0, "y": 0.0, "z": 0.0},
                {"id": "n2", "source_index": 2, "x": 10.0, "y": 10.0, "z": 0.0},
                {"id": "n3", "source_index": 3, "x": 0.0, "y": 10.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "source_index": 0, "start": "n0", "end": "n1", "enabled_as_road": True},
                {"id": "e1", "source_index": 1, "start": "n1", "end": "n2", "enabled_as_road": True},
                {"id": "e2", "source_index": 2, "start": "n2", "end": "n3", "enabled_as_road": True},
                {"id": "e3", "source_index": 3, "start": "n3", "end": "n0", "enabled_as_road": True},
            ],
        }

        layout_control.populate_layout_draft(scene, graph)
        exported = layout_control.build_layout_graph_from_draft(scene)

        self.assertEqual(len(exported["faces"]), 1)
        self.assertEqual(set(exported["faces"][0]["vertices"]), {"n0", "n1", "n2", "n3"})

    def test_layout_draft_add_remove_helpers_manage_ids_and_connected_edges(self):
        layout_control = load_module("layout_control_draft_helpers", "iCity/smart_city/layout_control.py")

        class FakeCollection(list):
            def add(self):
                item = types.SimpleNamespace()
                self.append(item)
                return item

            def remove(self, index):
                del self[index]

        scene = types.SimpleNamespace(
            icity_layout_nodes=FakeCollection(),
            icity_layout_edges=FakeCollection(),
        )

        first_node_index = layout_control.add_draft_node(scene)
        second_node_index = layout_control.add_draft_node(scene)
        edge_index = layout_control.add_draft_edge(scene)

        self.assertEqual(first_node_index, 0)
        self.assertEqual(second_node_index, 1)
        self.assertEqual(edge_index, 0)
        self.assertEqual([node.node_id for node in scene.icity_layout_nodes], ["n0", "n1"])
        self.assertEqual(scene.icity_layout_edges[0].edge_id, "e0")
        self.assertEqual(scene.icity_layout_edges[0].start_node_id, "n0")
        self.assertEqual(scene.icity_layout_edges[0].end_node_id, "n1")

        removed_node_id, affected_edges = layout_control.remove_draft_node(scene, 0)

        self.assertEqual(removed_node_id, "n0")
        self.assertEqual(affected_edges, 1)
        self.assertEqual(len(scene.icity_layout_nodes), 1)
        self.assertEqual(len(scene.icity_layout_edges), 0)

    def test_layout_draft_remove_edge_and_unique_id_fill_gaps(self):
        layout_control = load_module("layout_control_edge_helpers", "iCity/smart_city/layout_control.py")

        class FakeCollection(list):
            def add(self):
                item = types.SimpleNamespace()
                self.append(item)
                return item

            def remove(self, index):
                del self[index]

        scene = types.SimpleNamespace(
            icity_layout_nodes=FakeCollection(
                [
                    types.SimpleNamespace(node_id="n0"),
                    types.SimpleNamespace(node_id="n1"),
                ]
            ),
            icity_layout_edges=FakeCollection(
                [
                    types.SimpleNamespace(edge_id="e1", start_node_id="n0", end_node_id="n1"),
                ]
            ),
        )

        edge_index = layout_control.add_draft_edge(scene)
        removed_edge_id = layout_control.remove_draft_edge(scene, edge_index)

        self.assertEqual(scene.icity_layout_edges[0].edge_id, "e1")
        self.assertEqual(removed_edge_id, "e0")

    def test_layout_normalization_merges_near_nodes_and_removes_duplicate_edges(self):
        layout_control = load_module("layout_control_normalize_merge", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "x": 0.05, "y": 0.0, "z": 0.0},
                {"id": "n2", "x": 10.0, "y": 0.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "start": "n0", "end": "n2", "enabled_as_road": False},
                {"id": "e1", "start": "n1", "end": "n2", "enabled_as_road": True},
                {"id": "e2", "start": "n0", "end": "n1", "enabled_as_road": True},
            ],
            "faces": [],
        }

        normalized, stats = layout_control.normalize_layout_graph(graph, merge_distance=0.1)

        self.assertEqual([node["id"] for node in normalized["nodes"]], ["n0", "n2"])
        self.assertEqual(len(normalized["edges"]), 1)
        self.assertEqual(normalized["edges"][0]["id"], "e0")
        self.assertFalse(normalized["edges"][0]["enabled_as_road"])
        self.assertEqual(stats["merged_nodes"], 1)
        self.assertEqual(stats["removed_invalid_edges"], 1)
        self.assertEqual(stats["removed_duplicate_edges"], 1)

    def test_layout_normalization_splits_crossing_edges_at_shared_node(self):
        layout_control = load_module("layout_control_normalize_crossing", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": -10.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "x": 10.0, "y": 0.0, "z": 0.0},
                {"id": "n2", "x": 0.0, "y": -10.0, "z": 0.0},
                {"id": "n3", "x": 0.0, "y": 10.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "start": "n0", "end": "n1", "enabled_as_road": True},
                {"id": "e1", "start": "n2", "end": "n3", "enabled_as_road": True},
            ],
            "faces": [],
        }

        normalized, stats = layout_control.normalize_layout_graph(graph)

        intersection_nodes = [
            node for node in normalized["nodes"] if node["x"] == 0.0 and node["y"] == 0.0
        ]
        self.assertEqual(len(intersection_nodes), 1)
        intersection_id = intersection_nodes[0]["id"]
        self.assertEqual(len(normalized["edges"]), 4)
        self.assertEqual(
            sum(intersection_id in (edge["start"], edge["end"]) for edge in normalized["edges"]),
            4,
        )
        self.assertEqual(stats["intersection_nodes"], 1)
        self.assertEqual(stats["split_edges"], 2)

    def test_layout_normalization_removes_missing_and_short_edges(self):
        layout_control = load_module("layout_control_normalize_cleanup", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "x": 0.01, "y": 0.0, "z": 0.0},
            ],
            "edges": [
                {"id": "e0", "start": "n0", "end": "missing", "enabled_as_road": True},
                {"id": "e1", "start": "n0", "end": "n1", "enabled_as_road": True},
            ],
            "faces": [],
        }

        normalized, stats = layout_control.normalize_layout_graph(
            graph,
            merge_distance=0.0,
            minimum_edge_length=0.1,
        )

        self.assertEqual(normalized["edges"], [])
        self.assertEqual(stats["removed_invalid_edges"], 1)
        self.assertEqual(stats["removed_short_edges"], 1)

    def test_layout_face_inference_uses_closed_chordless_cycles(self):
        layout_control = load_module("layout_control_faces", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "x": 10.0, "y": 0.0, "z": 0.0},
                {"id": "n2", "x": 10.0, "y": 10.0, "z": 0.0},
                {"id": "n3", "x": 0.0, "y": 10.0, "z": 0.0},
            ],
            "edges": [
                {"start": "n0", "end": "n1", "enabled_as_road": True},
                {"start": "n1", "end": "n2", "enabled_as_road": True},
                {"start": "n2", "end": "n3", "enabled_as_road": True},
                {"start": "n3", "end": "n0", "enabled_as_road": True},
            ],
            "faces": [],
        }

        faces = layout_control.infer_face_loops_from_graph(graph)

        self.assertEqual(len(faces), 1)
        self.assertEqual(set(faces[0]), {"n0", "n1", "n2", "n3"})

    def test_layout_preview_geometry_builds_visible_nodes_roads_and_blocks(self):
        layout_control = load_module("layout_control_preview_geometry", "iCity/smart_city/layout_control.py")
        graph = {
            "nodes": [
                {"id": "n0", "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": "n1", "x": 10.0, "y": 0.0, "z": 0.0},
                {"id": "n2", "x": 10.0, "y": 10.0, "z": 0.0},
                {"id": "n3", "x": 0.0, "y": 10.0, "z": 0.0},
            ],
            "edges": [
                {"start": "n0", "end": "n1", "enabled_as_road": True},
                {"start": "n1", "end": "n2", "enabled_as_road": True},
                {"start": "n2", "end": "n3", "enabled_as_road": False},
                {"start": "n3", "end": "n0", "enabled_as_road": True},
            ],
            "faces": [{"vertices": ["n0", "n1", "n2", "n3"]}],
        }

        geometry = layout_control.build_layout_preview_geometry(
            graph,
            road_width=2.0,
            node_radius=1.0,
            preview_height=0.5,
        )

        self.assertEqual(len(geometry["nodes"]["vertices"]), 24)
        self.assertEqual(len(geometry["nodes"]["faces"]), 32)
        self.assertEqual(len(geometry["roads"]["faces"]), 3)
        self.assertEqual(len(geometry["disabled_roads"]["faces"]), 1)
        self.assertEqual(len(geometry["blocks"]["faces"]), 1)
        first_road_vertex = geometry["roads"]["vertices"][0]
        self.assertEqual(first_road_vertex, (0.0, 1.0, 0.5))

    def test_vehicle_motion_points_from_open_chain_ping_pong_without_shortcut(self):
        traffic_extension = load_module("traffic_extension_pingpong", "iCity/smart_city/traffic_extension.py")

        chain = [
            Vector((0.0, 0.0, 0.0)),
            Vector((5.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((15.0, 0.0, 0.0)),
        ]

        motion_points = traffic_extension.vehicle_motion_points_from_chain(chain)

        self.assertEqual(
            [(point.x, point.y, point.z) for point in motion_points],
            [
                (0.0, 0.0, 0.0),
                (5.0, 0.0, 0.0),
                (10.0, 0.0, 0.0),
                (15.0, 0.0, 0.0),
                (10.0, 0.0, 0.0),
                (5.0, 0.0, 0.0),
            ],
        )

    def test_generate_traffic_module_prefers_base_road_paths_over_outer_fallback(self):
        traffic_extension = load_module("traffic_extension_prefers_base_roads", "iCity/smart_city/traffic_extension.py")
        settings = types.SimpleNamespace(
            animation_start=1,
            animation_end=60,
        )
        frame_calls = []
        scene = types.SimpleNamespace(
            icity_traffic_settings=settings,
            frame_start=0,
            frame_end=0,
            frame_set=lambda frame: frame_calls.append(frame),
        )
        context = types.SimpleNamespace(scene=scene)
        generated = []

        traffic_extension.clear_traffic = lambda: None
        traffic_extension.bpy.data.collections = {traffic_extension.ICITY_ROOT_COLLECTION: object()}
        traffic_extension.ecology_common.get_or_create_child_collection = lambda parent, name: object()
        traffic_extension.extract_vehicle_road_paths_from_scene = lambda: [[Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0)), Vector((20.0, 0.0, 0.0))]]
        traffic_extension._build_vehicle_and_walkway_surfaces = (
            lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("outer fallback should not be used"))
        )
        traffic_extension._generate_vehicles_on_road_paths = lambda settings, path_collection, vehicle_collection, road_paths: generated.append(("vehicles", len(road_paths)))

        traffic_extension.generate_traffic(context)

        self.assertEqual(generated, [("vehicles", 1)])
        self.assertEqual(frame_calls, [1])

    def test_clear_streetlights_only_removes_generated_collection(self):
        asset_extension = load_module("asset_extension_clear_streetlights", "iCity/smart_city/asset_extension.py")
        calls = []

        asset_extension.clear_scoped_road_asset_assignments = lambda *args, **kwargs: calls.append("scoped")
        asset_extension.clear_collection_contents = lambda collection_name: calls.append(collection_name)

        asset_extension.clear_streetlights()

        self.assertEqual(calls, [asset_extension.ASSET_STREETLIGHT_COLLECTION])

    def test_streetlight_road_asset_spec_maps_to_light_node(self):
        asset_extension = load_module("asset_extension_road_spec_light", "iCity/smart_city/asset_extension.py")

        spec = asset_extension.road_asset_spec_for_style("STREETLIGHT")

        self.assertIsNotNone(spec)
        self.assertEqual(spec["node_name"], "Light")
        self.assertEqual(spec["placement_mode"], "OBJECT")
        self.assertEqual(spec["asset_input_index"], 4)
        self.assertEqual(spec["spacing_input_index"], 10)
        self.assertEqual(spec["lateral_offset_input_index"], 11)
        self.assertEqual(spec["depth_offset_input_index"], 12)

    def test_supported_roadside_asset_specs_map_to_expected_nodes(self):
        asset_extension = load_module("asset_extension_road_spec_props", "iCity/smart_city/asset_extension.py")

        bench_spec = asset_extension.road_asset_spec_for_style("BENCH")
        bollard_spec = asset_extension.road_asset_spec_for_style("BOLLARD")

        self.assertEqual(bench_spec["node_name"], "Bench")
        self.assertEqual(bench_spec["placement_mode"], "OBJECT")
        self.assertEqual(bollard_spec["node_name"], "Bollard")
        self.assertEqual(bollard_spec["placement_mode"], "OBJECT")

    def test_unsupported_roadside_asset_styles_fall_back_to_manual_placement(self):
        asset_extension = load_module("asset_extension_road_spec_fallback", "iCity/smart_city/asset_extension.py")

        self.assertIsNone(asset_extension.road_asset_spec_for_style("PLANTER"))
        self.assertIsNone(asset_extension.road_asset_spec_for_style("BUS_STOP"))

    def test_road_asset_node_availability_checks_node_and_input_capacity(self):
        asset_extension = load_module("asset_extension_road_spec_availability", "iCity/smart_city/asset_extension.py")
        spec = asset_extension.road_asset_spec_for_style("STREETLIGHT")

        valid_group = types.SimpleNamespace(
            nodes={
                "Light": types.SimpleNamespace(inputs=[object() for _ in range(13)]),
            }
        )
        missing_group = types.SimpleNamespace(nodes={})
        short_group = types.SimpleNamespace(
            nodes={
                "Light": types.SimpleNamespace(inputs=[object() for _ in range(5)]),
            }
        )

        self.assertTrue(asset_extension.road_asset_node_available(valid_group, spec))
        self.assertFalse(asset_extension.road_asset_node_available(missing_group, spec))
        self.assertFalse(asset_extension.road_asset_node_available(short_group, spec))

    def test_road_asset_styles_for_scope_keeps_streetlights_isolated(self):
        asset_extension = load_module("asset_extension_scope_streetlight", "iCity/smart_city/asset_extension.py")

        self.assertEqual(asset_extension.road_asset_styles_for_scope("STREETLIGHT"), ("STREETLIGHT",))

    def test_road_asset_styles_for_scope_limits_single_supported_roadside_style(self):
        asset_extension = load_module("asset_extension_scope_roadside", "iCity/smart_city/asset_extension.py")

        self.assertEqual(asset_extension.road_asset_styles_for_scope("ROADSIDE", "BENCH"), ("BENCH",))
        self.assertEqual(asset_extension.road_asset_styles_for_scope("ROADSIDE", "BOLLARD"), ("BOLLARD",))
        self.assertEqual(asset_extension.road_asset_styles_for_scope("ROADSIDE", "PLANTER"), ())
        self.assertEqual(asset_extension.road_asset_styles_for_scope("ROADSIDE", "MIXED"), ("BENCH", "BOLLARD"))

    def test_streetlight_positions_prefer_road_anchors_when_supported(self):
        asset_extension = load_module("asset_extension_anchor_preferred", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=3,
            streetlight_base_z_offset=0.0,
        )
        anchor_candidates = [
            (Vector((40.0, 2.0, 0.0)), 0.1),
            (Vector((45.0, 3.0, 0.0)), 0.2),
            (Vector((50.0, 4.0, 0.0)), 0.3),
            (Vector((55.0, 5.0, 0.0)), 0.4),
        ]

        positions = asset_extension.streetlight_positions_with_fallback(
            Vector((0.0, 0.0, 0.0)),
            30.0,
            settings,
            anchor_candidates=anchor_candidates,
            road_node_supported=True,
        )

        self.assertEqual(
            serialize_positions(positions),
            serialize_positions(asset_extension._downsample_positions(anchor_candidates, 3)),
        )

    def test_streetlight_positions_fall_back_when_anchor_candidates_empty(self):
        asset_extension = load_module("asset_extension_anchor_empty", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=4,
            streetlight_base_z_offset=0.0,
        )

        fallback_positions = asset_extension.filtered_perimeter_positions(Vector((0.0, 0.0, 0.0)), 30.0, settings)
        positions = asset_extension.streetlight_positions_with_fallback(
            Vector((0.0, 0.0, 0.0)),
            30.0,
            settings,
            anchor_candidates=[],
            road_node_supported=True,
        )

        self.assertEqual(serialize_positions(positions), serialize_positions(fallback_positions))

    def test_streetlight_positions_fall_back_when_road_node_unavailable(self):
        asset_extension = load_module("asset_extension_anchor_unsupported", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=4,
            streetlight_base_z_offset=0.0,
        )
        anchor_candidates = [
            (Vector((40.0, 2.0, 0.0)), 0.1),
            (Vector((45.0, 3.0, 0.0)), 0.2),
            (Vector((50.0, 4.0, 0.0)), 0.3),
            (Vector((55.0, 5.0, 0.0)), 0.4),
        ]

        fallback_positions = asset_extension.filtered_perimeter_positions(Vector((0.0, 0.0, 0.0)), 30.0, settings)
        positions = asset_extension.streetlight_positions_with_fallback(
            Vector((0.0, 0.0, 0.0)),
            30.0,
            settings,
            anchor_candidates=anchor_candidates,
            road_node_supported=False,
        )

        self.assertEqual(serialize_positions(positions), serialize_positions(fallback_positions))

    def test_streetlight_band_stays_outside_city_radius(self):
        asset_extension = load_module("asset_extension_streetlight", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=20,
            streetlight_base_z_offset=0.0,
        )

        points = asset_extension.perimeter_positions(Vector((0.0, 0.0, 0.0)), 30.0, settings)
        min_distance = min(Vector((point.x, point.y, 0.0)).length for point, _ in points)

        self.assertGreaterEqual(min_distance, 33.0)

    def test_filtered_streetlight_points_exclude_city_core(self):
        asset_extension = load_module("asset_extension_filtered", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=24,
            streetlight_base_z_offset=0.0,
        )

        points = asset_extension.filtered_perimeter_positions(Vector((0.0, 0.0, 0.0)), 30.0, settings)

        self.assertTrue(all(abs(point.x) >= 18.0 or abs(point.y) >= 18.0 for point, _ in points))

    def test_roadside_positions_stay_in_stronger_outer_band(self):
        asset_extension = load_module("asset_extension_roadside_outer_band", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            roadside_asset_offset=8.0,
            roadside_asset_count=18,
        )

        points = asset_extension.roadside_prop_positions(Vector((0.0, 0.0, 0.0)), 30.0, settings)
        min_distance = min(Vector((point.x, point.y, 0.0)).length for point, _ in points)

        self.assertGreaterEqual(min_distance, 37.0)

    def test_generate_streetlights_skips_brittle_road_system_path(self):
        asset_extension = load_module("asset_extension_generate_streetlights_manual", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            streetlight_offset=7.5,
            streetlight_count=4,
            streetlight_base_z_offset=0.0,
            streetlight_height=5.8,
            streetlight_arm_length=1.35,
            streetlight_light_power=950.0,
            streetlight_emission_strength=7.5,
        )
        context = types.SimpleNamespace(scene=types.SimpleNamespace(icity_asset_settings=settings))
        created = []

        asset_extension.clear_streetlights = lambda: None
        asset_extension.get_asset_root_collection = lambda: object()
        asset_extension.get_or_create_child_collection = lambda parent, name: object()
        asset_extension.get_city_bounds = lambda: (Vector((0.0, 0.0, 0.0)), 30.0, 0.0)
        asset_extension.try_generate_streetlights_on_road_system = (
            lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("road-system path should not be used"))
        )
        asset_extension.build_streetlight_materials = lambda settings: ("metal", "emission")
        asset_extension.build_streetlight_mesh = lambda settings: types.SimpleNamespace(materials=[])
        asset_extension.filtered_perimeter_positions = lambda center, radius, settings: [(Vector((40.0, 0.0, 0.0)), 0.0)]
        asset_extension.create_streetlight_instance = lambda *args, **kwargs: created.append(args)

        operator = asset_extension.ICITY_OT_GenerateStreetlights()
        operator.report = lambda *args, **kwargs: None

        result = operator.execute(context)

        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(len(created), 1)

    def test_generate_roadside_assets_skips_city_internal_road_system_path(self):
        asset_extension = load_module("asset_extension_generate_roadside_manual", "iCity/smart_city/asset_extension.py")
        settings = types.SimpleNamespace(
            roadside_asset_style="BENCH",
            roadside_asset_offset=8.0,
            roadside_asset_count=2,
            roadside_asset_scale=1.0,
        )
        context = types.SimpleNamespace(scene=types.SimpleNamespace(icity_asset_settings=settings))
        created = []

        asset_extension.clear_roadside_assets = lambda style_key=None: None
        asset_extension.get_asset_root_collection = lambda: object()
        asset_extension.get_or_create_child_collection = lambda parent, name: object()
        asset_extension.get_city_bounds = lambda: (Vector((0.0, 0.0, 0.0)), 30.0, 0.0)
        asset_extension.try_generate_roadside_assets_on_road_system = (
            lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("road-system path should not be used"))
        )
        asset_extension.roadside_prop_positions = lambda center, radius, settings: [
            (Vector((40.0, 0.0, 0.0)), 0.0),
            (Vector((0.0, 40.0, 0.0)), 1.57),
        ]
        asset_extension.roadside_style_keys = lambda settings: ["BENCH"]
        asset_extension._build_roadside_prop_mesh = lambda style_key: types.SimpleNamespace(materials=[])
        asset_extension.build_roadside_prop_material = lambda style_key: "material"
        asset_extension.create_roadside_prop_instance = lambda *args, **kwargs: created.append(args)

        operator = asset_extension.ICITY_OT_GenerateRoadsideAssets()
        operator.report = lambda *args, **kwargs: None

        result = operator.execute(context)

        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(len(created), 2)

    def test_ecology_layout_keeps_water_and_traffic_outside_city_buffer(self):
        ecology_common = load_module("ecology_common", "iCity/smart_city/ecology_common.py")
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

        lake_clearance = layout["lake_center"].length - max(layout["lake_radius_x"], layout["lake_radius_y"])
        self.assertGreaterEqual(lake_clearance, 36.0)

        river_clearance = min(point.length for point in layout["river_points"]) - settings.river_width * 0.5
        self.assertGreaterEqual(river_clearance, 36.0)

        traffic_clearance = (
            layout["traffic_center"].length
            - max(settings.traffic_loop_radius_x, settings.traffic_loop_radius_y)
            - settings.road_width * 0.5
        )
        self.assertGreaterEqual(traffic_clearance, 34.0)

    def test_ecology_asset_anchors_stay_in_shore_band(self):
        ecology_common = load_module("ecology_common_asset_band", "iCity/smart_city/ecology_common.py")
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
        anchors = ecology_common.compute_ecology_asset_anchors(layout, settings)

        self.assertEqual(len(anchors["tree_points"]), 4)
        self.assertEqual(len(anchors["shrub_points"]), 5)
        self.assertLess((anchors["dock_center"] - layout["lake_center"]).dot(layout["direction"]), 0.0)

        dock_distance = (anchors["dock_center"] - layout["lake_center"]).length
        self.assertGreaterEqual(dock_distance, min(layout["lake_radius_x"], layout["lake_radius_y"]) * 0.45)
        self.assertLessEqual(dock_distance, max(layout["lake_radius_x"], layout["lake_radius_y"]) * 1.15)

        for point in anchors["tree_points"] + anchors["shrub_points"]:
            self.assertGreaterEqual(point.length, layout["city_safe_radius"] + 1.0)

    def test_ecology_asset_anchors_support_strict_vector_dimensions(self):
        ecology_common = load_module(
            "ecology_common_strict_dimensions",
            "iCity/smart_city/ecology_common.py",
            vector_cls=StrictVector,
        )
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

        layout = ecology_common.compute_layout(StrictVector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)
        anchors = ecology_common.compute_ecology_asset_anchors(layout, settings)

        self.assertEqual(len(anchors["tree_points"]), 4)
        self.assertEqual(len(anchors["shrub_points"]), 5)

    def test_asset_texture_lookup_accepts_numbered_duplicate_files(self):
        asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")

        path = asset_extension.get_texture_path("RoadLines010_2K-JPG_Opacity.jpg")

        self.assertIsNotNone(path)
        self.assertTrue(path.name.startswith("RoadLines010_2K-JPG_Opacity"))

    def test_asset_manifest_contains_phase2_categories(self):
        import json

        manifest_path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "manifests" / "asset_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        categories = {item["category"] for item in manifest.get("objects", [])}
        object_ids = {item["id"] for item in manifest.get("objects", [])}

        self.assertIn("roadside_asset", categories)
        self.assertIn("ecology_asset", categories)
        self.assertIn("dock_pier_proc_01", object_ids)
        self.assertIn("tree_cluster_proc_01", object_ids)
        self.assertIn("shrub_patch_proc_01", object_ids)


if __name__ == "__main__":
    unittest.main()

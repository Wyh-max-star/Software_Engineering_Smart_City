"""Layout-control diagnostics and Blender-facing panel.

Phase 0 intentionally inspects the existing ``ICity Base`` contract without
modifying its mesh or attributes. Later layout-control phases build on the
same standalone module.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable

import bpy
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup, UIList


ICITY_BASE_OBJECT = "ICity Base"
LAYOUT_CONTRACT_TEXT = "ICity Layout Contract Report"
LAYOUT_GRAPH_TEXT = "ICity Layout Graph Export"

# The complete contract report can be large and is only needed while Blender
# is running. Keeping the last read-only report in module memory avoids
# creating dozens of Scene properties solely for diagnostic UI rendering.
_last_contract_report = None

# These attributes are already referenced by the existing iCity Python code
# and are the most important contract signals for later layout-control phases.
KEY_LAYOUT_ATTRIBUTES = {
    "Road del",
    "street type",
    "Road lanes width",
    "side walk offset",
    "offset",
    "crosswalk offset",
    "space type",
    "Procedural index",
    "Floor count",
    "Floor count max",
}


def _attribute_value(data_item):
    """Read one mesh-attribute item across Blender attribute data types.

    Blender exposes different fields for BOOLEAN, INT, FLOAT, vector, and
    color attributes. The inspector deliberately avoids assuming the exact
    ICity attribute schema before Phase 0 has measured it in a real scene.
    """

    for field_name in ("value", "value_bool", "value_int", "value_float"):
        if hasattr(data_item, field_name):
            return _plain_json_value(getattr(data_item, field_name))
    if hasattr(data_item, "vector"):
        return _plain_json_value(data_item.vector)
    if hasattr(data_item, "color"):
        return _plain_json_value(data_item.color)
    return None


def _plain_json_value(value):
    """Convert Blender RNA values into JSON-safe Python primitives.

    Some Blender attribute fields named ``value`` are scalar values, while
    others are ``bpy_prop_array`` instances. Those arrays look list-like in
    Blender's UI but Python's JSON encoder does not recognize them directly.
    """

    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if all(hasattr(value, axis) for axis in ("x", "y", "z")):
        return [
            _plain_json_value(value.x),
            _plain_json_value(value.y),
            _plain_json_value(value.z),
        ]
    if isinstance(value, dict):
        return {str(key): _plain_json_value(item) for key, item in value.items()}
    if isinstance(value, Iterable):
        return [_plain_json_value(item) for item in value]
    return str(value)


def _coordinate_components(value) -> tuple[float, float, float]:
    """Return a safe XYZ tuple for UI display.

    Phase 1 is diagnostic UI, so malformed or unexpected coordinate values
    should not crash Blender's draw loop. If Blender gives us an unexpected
    representation, keep the panel usable and show zeros instead of repeatedly
    raising format errors.
    """

    if all(hasattr(value, axis) for axis in ("x", "y", "z")):
        value = (value.x, value.y, value.z)
    try:
        components = list(value)
    except TypeError:
        components = []
    while len(components) < 3:
        components.append(0.0)
    safe_components = []
    for component in components[:3]:
        try:
            safe_components.append(float(component))
        except (TypeError, ValueError):
            safe_components.append(0.0)
    return tuple(safe_components)


def inspect_mesh_contract(mesh, *, sample_limit: int = 8) -> dict:
    """Return a JSON-serializable summary of an ICity Base-like mesh.

    This function is kept independent of ``bpy.data`` so the contract-report
    shape can be unit-tested outside Blender. Only a small sample is exported
    for each attribute: the report is for understanding the schema, not for
    backing up the complete city layout.
    """

    report = {
        "vertices": len(getattr(mesh, "vertices", [])),
        "edges": len(getattr(mesh, "edges", [])),
        "polygons": len(getattr(mesh, "polygons", [])),
        "node_rows": [],
        "edge_rows": [],
        "face_rows": [],
        "attributes": [],
    }

    # Keep the complete basic point/edge graph in the in-memory report. This
    # is the first read-only layout viewer: users can inspect exact coordinates
    # and connectivity without selecting tiny mesh elements in the viewport.
    for index, vertex in enumerate(getattr(mesh, "vertices", [])):
        coordinate = list(_coordinate_components(getattr(vertex, "co", (0.0, 0.0, 0.0))))
        report["node_rows"].append(
            {
                "index": index,
                "coordinate": coordinate,
            }
        )

    for index, edge in enumerate(getattr(mesh, "edges", [])):
        report["edge_rows"].append(
            {
                "index": index,
                "vertices": _plain_json_value(getattr(edge, "vertices", ())),
                "enabled_as_road": None,
            }
        )

    for index, polygon in enumerate(getattr(mesh, "polygons", [])):
        report["face_rows"].append(
            {
                "index": index,
                "vertices": _plain_json_value(getattr(polygon, "vertices", ())),
            }
        )

    for attribute in getattr(mesh, "attributes", []):
        # Convert Blender-specific attribute items into plain JSON values.
        # This also reveals unsupported attribute types as ``null`` samples,
        # which is more useful during diagnosis than silently omitting them.
        samples = [
            _attribute_value(item)
            for item in list(getattr(attribute, "data", []))[: max(sample_limit, 0)]
        ]
        report["attributes"].append(
            {
                "name": getattr(attribute, "name", ""),
                "domain": getattr(attribute, "domain", "UNKNOWN"),
                "data_type": getattr(attribute, "data_type", "UNKNOWN"),
                "length": len(getattr(attribute, "data", [])),
                "samples": samples,
            }
        )

        # ``Road del`` uses inverted semantics in the original addon:
        # False means the edge generates a road, True means it is disabled.
        if getattr(attribute, "name", "") == "Road del" and getattr(attribute, "domain", "") == "EDGE":
            for index, item in enumerate(getattr(attribute, "data", [])):
                if index >= len(report["edge_rows"]):
                    break
                road_deleted = bool(_attribute_value(item))
                report["edge_rows"][index]["enabled_as_road"] = not road_deleted

    # Stable ordering makes reports and tests easy to compare between runs.
    report["attributes"].sort(key=lambda item: (item["domain"], item["name"]))
    return report


def format_contract_report(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)


def build_layout_graph_export(report: dict) -> dict:
    """Convert the inspected mesh report into the user-facing graph format.

    The contract report is intentionally verbose and includes raw attribute
    samples. The layout graph is narrower: it is the format users will edit,
    import, export, and eventually apply back to ``ICity Base``.
    """

    nodes = []
    for node in report.get("node_rows", []):
        x, y, z = _coordinate_components(node.get("coordinate", (0.0, 0.0, 0.0)))
        nodes.append(
            {
                "id": f"n{node['index']}",
                "source_index": node["index"],
                "x": x,
                "y": y,
                "z": z,
            }
        )

    edges = []
    for edge in report.get("edge_rows", []):
        vertices = list(edge.get("vertices", []))
        if len(vertices) < 2:
            continue
        edges.append(
            {
                "id": f"e{edge['index']}",
                "source_index": edge["index"],
                "start": f"n{vertices[0]}",
                "end": f"n{vertices[1]}",
                "enabled_as_road": edge.get("enabled_as_road"),
            }
        )

    # Faces are not editable yet, but exporting their vertex loops makes the
    # current city-block topology visible and prepares the Phase 3 apply path.
    faces = []
    for face in report.get("face_rows", []):
        faces.append(
            {
                "id": f"f{face['index']}",
                "source_index": face["index"],
                "vertices": [f"n{vertex_index}" for vertex_index in face.get("vertices", [])],
            }
        )

    return {
        "version": 1,
        "source": ICITY_BASE_OBJECT,
        "nodes": nodes,
        "edges": edges,
        "faces": faces,
    }


def format_layout_graph_export(graph: dict) -> str:
    return json.dumps(graph, ensure_ascii=False, indent=2)


def validate_layout_graph(graph: dict) -> dict:
    """Run lightweight draft validation before any topology normalization.

    This is intentionally narrower than the later graph-normalization phase.
    It catches editing mistakes that make the draft impossible to reason about:
    duplicate node IDs, missing edge endpoints, and self-loop roads.
    """

    errors = []
    warnings = []
    node_ids = [node.get("id", "") for node in graph.get("nodes", [])]
    node_id_set = set()
    for node_id in node_ids:
        if not node_id:
            errors.append("Node with empty id")
            continue
        if node_id in node_id_set:
            errors.append(f"Duplicate node id: {node_id}")
        node_id_set.add(node_id)

    edge_ids = set()
    undirected_edges = set()
    for edge in graph.get("edges", []):
        edge_id = edge.get("id", "")
        if not edge_id:
            errors.append("Edge with empty id")
        elif edge_id in edge_ids:
            errors.append(f"Duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)

        start = edge.get("start", "")
        end = edge.get("end", "")
        if start == end:
            errors.append(f"Self-loop edge: {edge_id or '<unnamed>'}")
        if start not in node_id_set:
            errors.append(f"Edge {edge_id or '<unnamed>'} references missing start node: {start}")
        if end not in node_id_set:
            errors.append(f"Edge {edge_id or '<unnamed>'} references missing end node: {end}")
        edge_key = tuple(sorted((start, end)))
        if start and end and start != end:
            if edge_key in undirected_edges:
                errors.append(f"Duplicate undirected edge: {start} <-> {end}")
            undirected_edges.add(edge_key)

    if not graph.get("faces"):
        warnings.append("No face loops exported; buildings may not have city blocks.")

    return {"errors": errors, "warnings": warnings}


def _node_distance(first: dict, second: dict) -> float:
    """Return the 3D distance between two plain layout-graph nodes."""

    return math.sqrt(
        (float(first.get("x", 0.0)) - float(second.get("x", 0.0))) ** 2
        + (float(first.get("y", 0.0)) - float(second.get("y", 0.0))) ** 2
        + (float(first.get("z", 0.0)) - float(second.get("z", 0.0))) ** 2
    )


def _segment_intersection_2d(start_a: dict, end_a: dict, start_b: dict, end_b: dict, tolerance: float):
    """Return parameters and coordinates for one proper XY intersection.

    Endpoint intersections are already represented by graph nodes and are
    deliberately ignored here. Collinear overlaps are also left unchanged:
    deciding how overlapping roads should combine is a separate user-facing
    policy, not a safe automatic cleanup.
    """

    ax = float(end_a.get("x", 0.0)) - float(start_a.get("x", 0.0))
    ay = float(end_a.get("y", 0.0)) - float(start_a.get("y", 0.0))
    bx = float(end_b.get("x", 0.0)) - float(start_b.get("x", 0.0))
    by = float(end_b.get("y", 0.0)) - float(start_b.get("y", 0.0))
    denominator = ax * by - ay * bx
    if abs(denominator) <= tolerance:
        return None

    offset_x = float(start_b.get("x", 0.0)) - float(start_a.get("x", 0.0))
    offset_y = float(start_b.get("y", 0.0)) - float(start_a.get("y", 0.0))
    parameter_a = (offset_x * by - offset_y * bx) / denominator
    parameter_b = (offset_x * ay - offset_y * ax) / denominator
    if not (tolerance < parameter_a < 1.0 - tolerance):
        return None
    if not (tolerance < parameter_b < 1.0 - tolerance):
        return None

    x = float(start_a.get("x", 0.0)) + parameter_a * ax
    y = float(start_a.get("y", 0.0)) + parameter_a * ay
    z_a = float(start_a.get("z", 0.0)) + parameter_a * (
        float(end_a.get("z", 0.0)) - float(start_a.get("z", 0.0))
    )
    z_b = float(start_b.get("z", 0.0)) + parameter_b * (
        float(end_b.get("z", 0.0)) - float(start_b.get("z", 0.0))
    )
    return parameter_a, parameter_b, x, y, (z_a + z_b) / 2.0


def normalize_layout_graph(
    graph: dict,
    *,
    merge_distance: float = 0.1,
    intersection_tolerance: float = 0.001,
    minimum_edge_length: float = 0.001,
) -> tuple[dict, dict]:
    """Normalize an editable road graph without touching ``ICity Base``.

    The operation is deterministic and conservative:
    - nearby nodes merge into the first matching node;
    - proper interior XY crossings become shared nodes;
    - missing, self-loop, duplicate, and too-short edges are removed;
    - the first surviving edge keeps its original road attributes.
    """

    merge_distance = max(float(merge_distance), 0.0)
    intersection_tolerance = max(float(intersection_tolerance), 1e-9)
    minimum_edge_length = max(float(minimum_edge_length), 0.0)
    stats = {
        "merged_nodes": 0,
        "intersection_nodes": 0,
        "removed_invalid_edges": 0,
        "removed_short_edges": 0,
        "removed_duplicate_edges": 0,
        "split_edges": 0,
    }

    nodes = []
    node_aliases = {}
    for source_node in graph.get("nodes", []):
        node = {
            "id": str(source_node.get("id", "")),
            "source_index": int(source_node.get("source_index", -1)),
            "x": float(source_node.get("x", 0.0)),
            "y": float(source_node.get("y", 0.0)),
            "z": float(source_node.get("z", 0.0)),
        }
        if not node["id"] or node["id"] in node_aliases:
            continue
        target = next(
            (candidate for candidate in nodes if _node_distance(node, candidate) <= merge_distance),
            None,
        )
        if target is None:
            nodes.append(node)
            node_aliases[node["id"]] = node["id"]
        else:
            node_aliases[node["id"]] = target["id"]
            stats["merged_nodes"] += 1

    node_by_id = {node["id"]: node for node in nodes}
    edges = []
    seen_edge_keys = set()
    for source_edge in graph.get("edges", []):
        start = node_aliases.get(source_edge.get("start"))
        end = node_aliases.get(source_edge.get("end"))
        if not start or not end or start == end:
            stats["removed_invalid_edges"] += 1
            continue
        if _node_distance(node_by_id[start], node_by_id[end]) < minimum_edge_length:
            stats["removed_short_edges"] += 1
            continue
        key = tuple(sorted((start, end)))
        if key in seen_edge_keys:
            stats["removed_duplicate_edges"] += 1
            continue
        seen_edge_keys.add(key)
        edges.append(
            {
                "id": str(source_edge.get("id", "")),
                "source_index": int(source_edge.get("source_index", -1)),
                "start": start,
                "end": end,
                "enabled_as_road": bool(source_edge.get("enabled_as_road", True)),
            }
        )

    # Collect all split points before rebuilding edges. This prevents a newly
    # split edge from changing the pair iteration while intersections are read.
    split_points = {index: [] for index in range(len(edges))}
    existing_node_ids = {node["id"] for node in nodes}
    for first_index, first_edge in enumerate(edges):
        for second_index in range(first_index + 1, len(edges)):
            second_edge = edges[second_index]
            if {first_edge["start"], first_edge["end"]} & {second_edge["start"], second_edge["end"]}:
                continue
            intersection = _segment_intersection_2d(
                node_by_id[first_edge["start"]],
                node_by_id[first_edge["end"]],
                node_by_id[second_edge["start"]],
                node_by_id[second_edge["end"]],
                intersection_tolerance,
            )
            if intersection is None:
                continue
            parameter_a, parameter_b, x, y, z = intersection
            intersection_node = next(
                (
                    node
                    for node in nodes
                    if _node_distance(node, {"x": x, "y": y, "z": z}) <= intersection_tolerance
                ),
                None,
            )
            if intersection_node is None:
                node_id = next_unique_id(existing_node_ids, "n")
                existing_node_ids.add(node_id)
                intersection_node = {
                    "id": node_id,
                    "source_index": -1,
                    "x": x,
                    "y": y,
                    "z": z,
                }
                nodes.append(intersection_node)
                node_by_id[node_id] = intersection_node
                stats["intersection_nodes"] += 1
            split_points[first_index].append((parameter_a, intersection_node["id"]))
            split_points[second_index].append((parameter_b, intersection_node["id"]))

    normalized_edges = []
    existing_edge_ids = {edge["id"] for edge in edges if edge["id"]}
    for edge_index, edge in enumerate(edges):
        points = [(0.0, edge["start"]), *split_points[edge_index], (1.0, edge["end"])]
        points.sort(key=lambda item: item[0])
        if split_points[edge_index]:
            stats["split_edges"] += 1
        for segment_index, ((_, start), (_, end)) in enumerate(zip(points, points[1:])):
            if start == end:
                continue
            segment = dict(edge)
            segment["start"] = start
            segment["end"] = end
            if segment_index > 0 or not segment["id"]:
                segment["id"] = next_unique_id(existing_edge_ids, "e")
            existing_edge_ids.add(segment["id"])
            normalized_edges.append(segment)

    # Crossing splits can reveal duplicates that did not exist before. Keep
    # the first segment and leave its road-enabled state unchanged.
    deduplicated_edges = []
    seen_edge_keys.clear()
    for edge in normalized_edges:
        key = tuple(sorted((edge["start"], edge["end"])))
        if key in seen_edge_keys:
            stats["removed_duplicate_edges"] += 1
            continue
        seen_edge_keys.add(key)
        deduplicated_edges.append(edge)

    normalized_graph = {
        "version": graph.get("version", 1),
        "source": f"{graph.get('source', ICITY_BASE_OBJECT)} Normalized",
        "nodes": nodes,
        "edges": deduplicated_edges,
        # Existing face loops cannot safely survive arbitrary node merges and
        # edge splits. Face reconstruction belongs to the later apply stage.
        "faces": [],
    }
    return normalized_graph, stats


def format_normalization_summary(stats: dict) -> str:
    """Create a compact user-facing summary of a normalization pass."""

    return (
        f"Merged {stats['merged_nodes']} nodes; added {stats['intersection_nodes']} intersections; "
        f"split {stats['split_edges']} edges; removed "
        f"{stats['removed_invalid_edges'] + stats['removed_short_edges'] + stats['removed_duplicate_edges']} edges"
    )


def _set_collection_item_values(item, values: dict) -> None:
    """Set Blender PropertyGroup fields from a plain dict.

    Blender collection items use RNA properties, but tests use tiny fake items.
    Keeping assignment through this helper lets both environments share the
    same draft-loading path.
    """

    for key, value in values.items():
        setattr(item, key, value)


def populate_layout_draft(scene, graph: dict) -> None:
    """Load graph JSON into editable Scene collection properties."""

    scene.icity_layout_nodes.clear()
    scene.icity_layout_edges.clear()

    for node in graph.get("nodes", []):
        item = scene.icity_layout_nodes.add()
        _set_collection_item_values(
            item,
            {
                "node_id": node.get("id", ""),
                "source_index": int(node.get("source_index", -1)),
                "x": float(node.get("x", 0.0)),
                "y": float(node.get("y", 0.0)),
                "z": float(node.get("z", 0.0)),
            },
        )

    for edge in graph.get("edges", []):
        item = scene.icity_layout_edges.add()
        enabled = edge.get("enabled_as_road")
        _set_collection_item_values(
            item,
            {
                "edge_id": edge.get("id", ""),
                "source_index": int(edge.get("source_index", -1)),
                "start_node_id": edge.get("start", ""),
                "end_node_id": edge.get("end", ""),
                "enabled_as_road": True if enabled is None else bool(enabled),
            },
        )


def build_layout_graph_from_draft(scene) -> dict:
    """Serialize the current editable UI draft back to layout graph JSON."""

    nodes = [
        {
            "id": node.node_id,
            "source_index": node.source_index,
            "x": node.x,
            "y": node.y,
            "z": node.z,
        }
        for node in scene.icity_layout_nodes
    ]
    edges = [
        {
            "id": edge.edge_id,
            "source_index": edge.source_index,
            "start": edge.start_node_id,
            "end": edge.end_node_id,
            "enabled_as_road": edge.enabled_as_road,
        }
        for edge in scene.icity_layout_edges
    ]
    return {
        "version": 1,
        "source": f"{ICITY_BASE_OBJECT} Draft",
        "nodes": nodes,
        "edges": edges,
        "faces": [],
    }


def next_unique_id(existing_ids, prefix: str) -> str:
    """Return the first unused deterministic ID for a new draft item."""

    existing = set(existing_ids)
    index = 0
    while f"{prefix}{index}" in existing:
        index += 1
    return f"{prefix}{index}"


def add_draft_node(scene) -> int:
    """Append a new node draft row and return its collection index."""

    node_id = next_unique_id((node.node_id for node in scene.icity_layout_nodes), "n")
    item = scene.icity_layout_nodes.add()
    _set_collection_item_values(
        item,
        {
            "node_id": node_id,
            "source_index": -1,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        },
    )
    return len(scene.icity_layout_nodes) - 1


def remove_draft_node(scene, node_index: int) -> tuple[str, int]:
    """Remove one node and every edge that references it.

    Returning the removed node ID and affected-edge count gives the Blender
    operator enough information to report the destructive draft-only change.
    """

    if node_index < 0 or node_index >= len(scene.icity_layout_nodes):
        raise IndexError("No valid draft node is selected.")

    node_id = scene.icity_layout_nodes[node_index].node_id
    affected_edge_indexes = [
        index
        for index, edge in enumerate(scene.icity_layout_edges)
        if edge.start_node_id == node_id or edge.end_node_id == node_id
    ]
    # Blender collection indexes shift after removal, so delete backwards.
    for edge_index in reversed(affected_edge_indexes):
        scene.icity_layout_edges.remove(edge_index)
    scene.icity_layout_nodes.remove(node_index)
    return node_id, len(affected_edge_indexes)


def add_draft_edge(scene) -> int:
    """Append a road edge using the first two available draft nodes."""

    if len(scene.icity_layout_nodes) < 2:
        raise ValueError("At least two draft nodes are required before adding an edge.")

    edge_id = next_unique_id((edge.edge_id for edge in scene.icity_layout_edges), "e")
    item = scene.icity_layout_edges.add()
    _set_collection_item_values(
        item,
        {
            "edge_id": edge_id,
            "source_index": -1,
            "start_node_id": scene.icity_layout_nodes[0].node_id,
            "end_node_id": scene.icity_layout_nodes[1].node_id,
            "enabled_as_road": True,
        },
    )
    return len(scene.icity_layout_edges) - 1


def remove_draft_edge(scene, edge_index: int) -> str:
    """Remove one selected edge draft row and return its ID."""

    if edge_index < 0 or edge_index >= len(scene.icity_layout_edges):
        raise IndexError("No valid draft edge is selected.")
    edge_id = scene.icity_layout_edges[edge_index].edge_id
    scene.icity_layout_edges.remove(edge_index)
    return edge_id


def format_validation_summary(validation: dict) -> str:
    """Create a short status line suitable for Blender's narrow sidebar."""

    return f"{len(validation['errors'])} errors, {len(validation['warnings'])} warnings"


def write_validation_details(scene, validation: dict) -> None:
    """Store the first validation messages for direct sidebar display."""

    messages = []
    messages.extend(f"ERROR: {message}" for message in validation["errors"])
    messages.extend(f"WARNING: {message}" for message in validation["warnings"])
    scene.icity_layout_validation_details = "\n".join(messages[:8])


def group_attributes_by_domain(report: dict) -> dict[str, list[dict]]:
    """Group attribute summaries for a compact human-readable UI."""

    grouped: dict[str, list[dict]] = {}
    for attribute in report.get("attributes", []):
        grouped.setdefault(attribute["domain"], []).append(attribute)
    return grouped


def key_attribute_status(report: dict) -> list[dict]:
    """Return the known layout attributes that exist in the inspected mesh."""

    return [
        attribute
        for attribute in report.get("attributes", [])
        if attribute["name"] in KEY_LAYOUT_ATTRIBUTES
    ]


def inspect_icity_base_contract() -> dict:
    """Inspect the live ICity Base object without changing scene data."""

    base_object = bpy.data.objects.get(ICITY_BASE_OBJECT)
    if base_object is None:
        raise RuntimeError("ICity Base was not found. Run iCity Start first.")
    mesh = getattr(base_object, "data", None)
    if mesh is None:
        raise RuntimeError("ICity Base does not contain readable mesh data.")
    return inspect_mesh_contract(mesh)


def write_contract_report_text(report: dict):
    """Write the report to a Blender Text datablock for easy inspection.

    A Text datablock is preferable to console-only output because addon users
    commonly launch Blender without a visible system console.
    """

    text = bpy.data.texts.get(LAYOUT_CONTRACT_TEXT)
    if text is None:
        text = bpy.data.texts.new(LAYOUT_CONTRACT_TEXT)
    text.clear()
    text.write(format_contract_report(report))
    return text


def write_layout_graph_text(graph: dict):
    """Write the concise, user-facing layout graph to a Text datablock."""

    text = bpy.data.texts.get(LAYOUT_GRAPH_TEXT)
    if text is None:
        text = bpy.data.texts.new(LAYOUT_GRAPH_TEXT)
    text.clear()
    text.write(format_layout_graph_export(graph))
    return text


class ICITY_OT_InspectLayoutContract(Operator):
    """Create a read-only report of the mesh contract used by the city."""

    bl_idname = "icity.inspect_layout_contract"
    bl_label = "Inspect ICity Base Contract"
    bl_description = "Read ICity Base mesh counts and attribute definitions without modifying the city"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _last_contract_report
        try:
            report = inspect_icity_base_contract()
            write_contract_report_text(report)
        except Exception as exc:  # pragma: no cover - surfaced in Blender UI
            self.report({"ERROR"}, f"Layout contract inspection failed: {exc}")
            return {"CANCELLED"}

        # The sidebar shows a concise visual summary. The Text datablock keeps
        # the exhaustive JSON report available for developers and debugging.
        _last_contract_report = report
        # Keep only a compact summary on Scene. The complete report remains in
        # the Text datablock and does not bloat Blender's sidebar state.
        context.scene.icity_layout_contract_summary = (
            f"{report['vertices']} nodes, {report['edges']} edges, "
            f"{report['polygons']} faces, {len(report['attributes'])} attributes"
        )
        self.report({"INFO"}, f"Report written to Text Editor: {LAYOUT_CONTRACT_TEXT}")
        return {"FINISHED"}


class ICITY_OT_ExportLayoutGraph(Operator):
    """Export the current read-only point/line graph as concise JSON."""

    bl_idname = "icity.export_layout_graph"
    bl_label = "Export Layout Graph JSON"
    bl_description = "Export current ICity Base nodes, edges, and face loops as a layout graph JSON draft"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _last_contract_report
        try:
            if _last_contract_report is None:
                _last_contract_report = inspect_icity_base_contract()
            graph = build_layout_graph_export(_last_contract_report)
            write_layout_graph_text(graph)
        except Exception as exc:  # pragma: no cover - surfaced in Blender UI
            self.report({"ERROR"}, f"Layout graph export failed: {exc}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Layout graph written to Text Editor: {LAYOUT_GRAPH_TEXT}")
        return {"FINISHED"}


class ICITY_LayoutNodeDraft(PropertyGroup):
    """One editable node row in the layout-control draft."""

    node_id: StringProperty(name="ID", default="")
    source_index: IntProperty(name="Source Index", default=-1)
    x: FloatProperty(name="X", default=0.0)
    y: FloatProperty(name="Y", default=0.0)
    z: FloatProperty(name="Z", default=0.0)


class ICITY_LayoutEdgeDraft(PropertyGroup):
    """One editable road connection row in the layout-control draft."""

    edge_id: StringProperty(name="ID", default="")
    source_index: IntProperty(name="Source Index", default=-1)
    start_node_id: StringProperty(name="Start", default="")
    end_node_id: StringProperty(name="End", default="")
    enabled_as_road: BoolProperty(name="Road", default=True)


class ICITY_UL_LayoutNodeList(UIList):
    """Compact UI list for layout nodes.

    Detailed coordinate editing happens below the list for the active row; the
    row itself stays compact so the list remains readable for larger layouts.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.node_id or f"n{index}", icon="VERTEXSEL")
        row.label(text=f"({item.x:.2f}, {item.y:.2f})")


class ICITY_UL_LayoutEdgeList(UIList):
    """Compact UI list for editable road connections."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        road_icon = "CHECKBOX_HLT" if item.enabled_as_road else "CHECKBOX_DEHLT"
        row.label(text=item.edge_id or f"e{index}", icon="EDGESEL")
        row.label(text=f"{item.start_node_id} -> {item.end_node_id}", icon=road_icon)


class ICITY_OT_LoadLayoutDraftFromBase(Operator):
    """Load the current ICity Base graph into editable UI draft rows."""

    bl_idname = "icity.load_layout_draft_from_base"
    bl_label = "Load Draft From ICity Base"
    bl_description = "Load current ICity Base nodes and edges into an editable draft without modifying the city"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _last_contract_report
        try:
            _last_contract_report = inspect_icity_base_contract()
            graph = build_layout_graph_export(_last_contract_report)
            populate_layout_draft(context.scene, graph)
            validation = validate_layout_graph(graph)
            write_validation_details(context.scene, validation)
        except Exception as exc:  # pragma: no cover - surfaced in Blender UI
            self.report({"ERROR"}, f"Load layout draft failed: {exc}")
            return {"CANCELLED"}

        context.scene.icity_layout_draft_summary = (
            f"Draft: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, "
            f"{len(validation['errors'])} errors, {len(validation['warnings'])} warnings"
        )
        self.report({"INFO"}, "Layout draft loaded from ICity Base.")
        return {"FINISHED"}


class ICITY_OT_ExportLayoutDraft(Operator):
    """Export the editable UI draft as layout graph JSON."""

    bl_idname = "icity.export_layout_draft"
    bl_label = "Export Draft JSON"
    bl_description = "Export the editable node and edge draft as layout graph JSON"
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            graph = build_layout_graph_from_draft(context.scene)
            validation = validate_layout_graph(graph)
            write_layout_graph_text(graph)
        except Exception as exc:  # pragma: no cover - surfaced in Blender UI
            self.report({"ERROR"}, f"Export layout draft failed: {exc}")
            return {"CANCELLED"}

        context.scene.icity_layout_draft_summary = (
            f"Draft exported: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, "
            f"{len(validation['errors'])} errors, {len(validation['warnings'])} warnings"
        )
        if validation["errors"]:
            self.report({"WARNING"}, "Draft exported with validation errors. Check node and edge IDs.")
        else:
            self.report({"INFO"}, f"Draft written to Text Editor: {LAYOUT_GRAPH_TEXT}")
        return {"FINISHED"}


class ICITY_OT_AddLayoutDraftNode(Operator):
    bl_idname = "icity.add_layout_draft_node"
    bl_label = "Add Node"
    bl_description = "Add a new node to the editable draft only"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.icity_layout_node_index = add_draft_node(context.scene)
        self.report({"INFO"}, "Draft node added.")
        return {"FINISHED"}


class ICITY_OT_RemoveLayoutDraftNode(Operator):
    bl_idname = "icity.remove_layout_draft_node"
    bl_label = "Remove Node"
    bl_description = "Remove the selected draft node and its connected draft edges"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            node_id, affected_edges = remove_draft_node(
                context.scene,
                context.scene.icity_layout_node_index,
            )
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        context.scene.icity_layout_node_index = min(
            context.scene.icity_layout_node_index,
            max(len(context.scene.icity_layout_nodes) - 1, 0),
        )
        context.scene.icity_layout_edge_index = min(
            context.scene.icity_layout_edge_index,
            max(len(context.scene.icity_layout_edges) - 1, 0),
        )
        self.report({"INFO"}, f"Removed {node_id} and {affected_edges} connected edge(s).")
        return {"FINISHED"}


class ICITY_OT_AddLayoutDraftEdge(Operator):
    bl_idname = "icity.add_layout_draft_edge"
    bl_label = "Add Edge"
    bl_description = "Add a new edge to the editable draft only"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            context.scene.icity_layout_edge_index = add_draft_edge(context.scene)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Draft edge added.")
        return {"FINISHED"}


class ICITY_OT_RemoveLayoutDraftEdge(Operator):
    bl_idname = "icity.remove_layout_draft_edge"
    bl_label = "Remove Edge"
    bl_description = "Remove the selected edge from the editable draft only"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            edge_id = remove_draft_edge(context.scene, context.scene.icity_layout_edge_index)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        context.scene.icity_layout_edge_index = min(
            context.scene.icity_layout_edge_index,
            max(len(context.scene.icity_layout_edges) - 1, 0),
        )
        self.report({"INFO"}, f"Removed draft edge {edge_id}.")
        return {"FINISHED"}


class ICITY_OT_ValidateLayoutDraft(Operator):
    bl_idname = "icity.validate_layout_draft"
    bl_label = "Validate Draft"
    bl_description = "Validate draft IDs and edge endpoint references without modifying the city"
    bl_options = {"REGISTER"}

    def execute(self, context):
        graph = build_layout_graph_from_draft(context.scene)
        validation = validate_layout_graph(graph)
        write_validation_details(context.scene, validation)
        context.scene.icity_layout_draft_summary = f"Draft validation: {format_validation_summary(validation)}"
        if validation["errors"]:
            self.report({"WARNING"}, "Draft contains validation errors.")
        else:
            self.report({"INFO"}, "Draft validation completed.")
        return {"FINISHED"}


class ICITY_OT_NormalizeLayoutDraft(Operator):
    bl_idname = "icity.normalize_layout_draft"
    bl_label = "Normalize Draft"
    bl_description = "Merge nearby nodes, split crossing edges, and remove duplicate draft edges without modifying ICity Base"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            graph = build_layout_graph_from_draft(context.scene)
            normalized_graph, stats = normalize_layout_graph(
                graph,
                merge_distance=context.scene.icity_layout_merge_distance,
                intersection_tolerance=context.scene.icity_layout_intersection_tolerance,
                minimum_edge_length=context.scene.icity_layout_minimum_edge_length,
            )
            populate_layout_draft(context.scene, normalized_graph)
            validation = validate_layout_graph(normalized_graph)
            write_validation_details(context.scene, validation)
            write_layout_graph_text(normalized_graph)
        except Exception as exc:  # pragma: no cover - surfaced in Blender UI
            self.report({"ERROR"}, f"Normalize layout draft failed: {exc}")
            return {"CANCELLED"}

        context.scene.icity_layout_node_index = min(
            context.scene.icity_layout_node_index,
            max(len(context.scene.icity_layout_nodes) - 1, 0),
        )
        context.scene.icity_layout_edge_index = min(
            context.scene.icity_layout_edge_index,
            max(len(context.scene.icity_layout_edges) - 1, 0),
        )
        context.scene.icity_layout_draft_summary = (
            f"Draft normalized: {len(normalized_graph['nodes'])} nodes, "
            f"{len(normalized_graph['edges'])} edges. {format_normalization_summary(stats)}"
        )
        if validation["errors"]:
            self.report({"WARNING"}, "Draft normalized but still has validation errors.")
        else:
            self.report({"INFO"}, "Draft normalized and exported.")
        return {"FINISHED"}


class ICITY_PT_LayoutControlPanel(Panel):
    """Entry point for layout-control phases.

    Phase 0 intentionally exposes diagnostics only. Editing and applying a
    draft are added later, after the real ICity attribute contract is known.
    """

    bl_label = "ICity Layout Control"
    bl_idname = "ICITY_PT_layout_control_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"

    def draw(self, context):
        layout = self.layout

        phase_box = layout.box()
        phase_box.label(text="Phase 0: Contract Inspection", icon="INFO")
        phase_box.label(text="Read-only: does not modify ICity Base")
        phase_box.operator("icity.inspect_layout_contract", icon="VIEWZOOM")

        if _last_contract_report is None:
            phase_box.label(text="Click Inspect to read the current city.")
            return

        # Present the mesh topology as four large, scan-friendly counters.
        # These are more useful to users than opening the raw JSON report.
        topology_box = layout.box()
        topology_box.label(text="Current ICity Base", icon="MESH_DATA")
        row = topology_box.row(align=True)
        row.label(text=f"Nodes: {_last_contract_report['vertices']}")
        row.label(text=f"Edges: {_last_contract_report['edges']}")
        row = topology_box.row(align=True)
        row.label(text=f"Faces: {_last_contract_report['polygons']}")
        row.label(text=f"Attributes: {len(_last_contract_report['attributes'])}")
        topology_box.operator("icity.export_layout_graph", icon="EXPORT")

        domain_box = layout.box()
        domain_box.label(text="Attributes by Storage Domain", icon="GROUP_VERTEX")
        grouped = group_attributes_by_domain(_last_contract_report)
        for domain in ("POINT", "EDGE", "FACE", "CORNER", "CURVE", "INSTANCE"):
            attributes = grouped.get(domain, [])
            if not attributes:
                continue
            domain_box.label(text=f"{domain}: {len(attributes)}")

        key_box = layout.box()
        key_box.label(text="Known Layout Attributes", icon="KEYINGSET")
        known_attributes = key_attribute_status(_last_contract_report)
        if not known_attributes:
            key_box.label(text="No known layout attributes found", icon="ERROR")
        for attribute in known_attributes:
            key_box.label(
                text=(
                    f"{attribute['name']} | {attribute['domain']} | "
                    f"{attribute['data_type']} | {attribute['length']} values"
                )
            )

        node_box = layout.box()
        node_box.label(text="Nodes (ICity Base Local Coordinates)", icon="VERTEXSEL")
        for node in _last_contract_report["node_rows"]:
            coordinate = _coordinate_components(node["coordinate"])
            # ICity Base is expected to be planar, but keep Z visible so an
            # accidental non-planar layout is immediately obvious.
            node_box.label(
                text=(
                    f"#{node['index']}: X {coordinate[0]:.3f}, "
                    f"Y {coordinate[1]:.3f}, Z {coordinate[2]:.3f}"
                )
            )

        edge_box = layout.box()
        edge_box.label(text="Edges (Node Connections)", icon="EDGESEL")
        for edge in _last_contract_report["edge_rows"]:
            vertices = edge["vertices"]
            road_state = edge["enabled_as_road"]
            if road_state is None:
                state_text = "Road status unknown"
            else:
                state_text = "Road enabled" if road_state else "Road disabled"
            edge_box.label(
                text=f"#{edge['index']}: {vertices[0]} -> {vertices[1]} | {state_text}"
            )

        details_box = layout.box()
        details_box.label(text="Developer Details", icon="TEXT")
        details_box.label(text=f"Text Editor: {LAYOUT_CONTRACT_TEXT}")
        details_box.label(text=f"Layout JSON: {LAYOUT_GRAPH_TEXT}")

        draft_box = layout.box()
        draft_box.label(text="Phase 2 Draft Editor (No Apply Yet)", icon="GREASEPENCIL")
        row = draft_box.row(align=True)
        row.operator("icity.load_layout_draft_from_base", icon="IMPORT")
        row.operator("icity.export_layout_draft", icon="EXPORT")
        draft_box.operator("icity.validate_layout_draft", icon="CHECKMARK")
        if context.scene.icity_layout_draft_summary:
            draft_box.label(text=context.scene.icity_layout_draft_summary)
        if context.scene.icity_layout_validation_details:
            validation_box = draft_box.box()
            validation_box.label(text="Validation Details", icon="INFO")
            for line in context.scene.icity_layout_validation_details.splitlines():
                validation_box.label(text=line, icon="ERROR" if line.startswith("ERROR:") else "INFO")

        normalize_box = draft_box.box()
        normalize_box.label(text="Phase 3 Topology Normalize (Draft Only)", icon="MODIFIER")
        normalize_box.prop(context.scene, "icity_layout_merge_distance")
        normalize_box.prop(context.scene, "icity_layout_intersection_tolerance")
        normalize_box.prop(context.scene, "icity_layout_minimum_edge_length")
        normalize_box.operator("icity.normalize_layout_draft", icon="AUTOMERGE_ON")

        node_list_box = draft_box.box()
        node_list_box.label(text="Editable Nodes", icon="VERTEXSEL")
        node_list_box.template_list(
            "ICITY_UL_LayoutNodeList",
            "",
            context.scene,
            "icity_layout_nodes",
            context.scene,
            "icity_layout_node_index",
            rows=4,
        )
        node_actions = node_list_box.row(align=True)
        node_actions.operator("icity.add_layout_draft_node", icon="ADD")
        node_actions.operator("icity.remove_layout_draft_node", icon="REMOVE")
        if 0 <= context.scene.icity_layout_node_index < len(context.scene.icity_layout_nodes):
            node = context.scene.icity_layout_nodes[context.scene.icity_layout_node_index]
            node_list_box.prop(node, "node_id")
            coord_row = node_list_box.row(align=True)
            coord_row.prop(node, "x")
            coord_row.prop(node, "y")
            coord_row.prop(node, "z")

        edge_list_box = draft_box.box()
        edge_list_box.label(text="Editable Edges", icon="EDGESEL")
        edge_list_box.template_list(
            "ICITY_UL_LayoutEdgeList",
            "",
            context.scene,
            "icity_layout_edges",
            context.scene,
            "icity_layout_edge_index",
            rows=4,
        )
        edge_actions = edge_list_box.row(align=True)
        edge_actions.operator("icity.add_layout_draft_edge", icon="ADD")
        edge_actions.operator("icity.remove_layout_draft_edge", icon="REMOVE")
        if 0 <= context.scene.icity_layout_edge_index < len(context.scene.icity_layout_edges):
            edge = context.scene.icity_layout_edges[context.scene.icity_layout_edge_index]
            edge_list_box.prop(edge, "edge_id")
            endpoints = edge_list_box.row(align=True)
            endpoints.prop(edge, "start_node_id")
            endpoints.prop(edge, "end_node_id")
            edge_list_box.prop(edge, "enabled_as_road")


CLASSES = (
    ICITY_LayoutNodeDraft,
    ICITY_LayoutEdgeDraft,
    ICITY_UL_LayoutNodeList,
    ICITY_UL_LayoutEdgeList,
    ICITY_OT_InspectLayoutContract,
    ICITY_OT_ExportLayoutGraph,
    ICITY_OT_LoadLayoutDraftFromBase,
    ICITY_OT_ExportLayoutDraft,
    ICITY_OT_AddLayoutDraftNode,
    ICITY_OT_RemoveLayoutDraftNode,
    ICITY_OT_AddLayoutDraftEdge,
    ICITY_OT_RemoveLayoutDraftEdge,
    ICITY_OT_ValidateLayoutDraft,
    ICITY_OT_NormalizeLayoutDraft,
    ICITY_PT_LayoutControlPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_layout_contract_summary = bpy.props.StringProperty(
        name="Layout Contract Summary",
        default="",
        options={"HIDDEN"},
    )
    bpy.types.Scene.icity_layout_draft_summary = bpy.props.StringProperty(
        name="Layout Draft Summary",
        default="",
        options={"HIDDEN"},
    )
    bpy.types.Scene.icity_layout_validation_details = bpy.props.StringProperty(
        name="Layout Validation Details",
        default="",
        options={"HIDDEN"},
    )
    bpy.types.Scene.icity_layout_nodes = CollectionProperty(type=ICITY_LayoutNodeDraft)
    bpy.types.Scene.icity_layout_edges = CollectionProperty(type=ICITY_LayoutEdgeDraft)
    bpy.types.Scene.icity_layout_node_index = IntProperty(name="Node Index", default=0)
    bpy.types.Scene.icity_layout_edge_index = IntProperty(name="Edge Index", default=0)
    bpy.types.Scene.icity_layout_merge_distance = FloatProperty(
        name="Merge Distance",
        description="Draft nodes within this distance are merged into the first matching node",
        default=0.1,
        min=0.0,
    )
    bpy.types.Scene.icity_layout_intersection_tolerance = FloatProperty(
        name="Intersection Tolerance",
        description="Numerical tolerance for detecting proper XY edge crossings",
        default=0.001,
        min=0.000001,
    )
    bpy.types.Scene.icity_layout_minimum_edge_length = FloatProperty(
        name="Minimum Edge Length",
        description="Draft edges shorter than this value are removed during normalization",
        default=0.001,
        min=0.0,
    )


def unregister() -> None:
    for property_name in (
        "icity_layout_edge_index",
        "icity_layout_node_index",
        "icity_layout_minimum_edge_length",
        "icity_layout_intersection_tolerance",
        "icity_layout_merge_distance",
        "icity_layout_edges",
        "icity_layout_nodes",
        "icity_layout_validation_details",
        "icity_layout_draft_summary",
        "icity_layout_contract_summary",
    ):
        if hasattr(bpy.types.Scene, property_name):
            delattr(bpy.types.Scene, property_name)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

"""Standalone traffic and crowd module for the ICity addon."""

from __future__ import annotations

import importlib
import importlib.util
import math
from pathlib import Path

import bpy
from bpy.props import FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector

if "ecology_common" in locals():
    importlib.reload(ecology_common)
else:
    try:
        from . import ecology_common
    except ImportError:
        module_path = Path(__file__).resolve().with_name("ecology_common.py")
        spec = importlib.util.spec_from_file_location("traffic_extension_ecology_common", module_path)
        ecology_common = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(ecology_common)

if "asset_registry" in locals():
    importlib.reload(asset_registry)
else:
    try:
        from . import asset_registry
    except ImportError:
        module_path = Path(__file__).resolve().with_name("asset_registry.py")
        spec = importlib.util.spec_from_file_location("traffic_extension_asset_registry", module_path)
        asset_registry = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(asset_registry)


ICITY_ROOT_COLLECTION = ecology_common.ICITY_ROOT_COLLECTION
ICITY_BASE_OBJECT = ecology_common.ICITY_BASE_OBJECT
remove_collection_recursive = ecology_common.remove_collection_recursive
TRAFFIC_ROOT_COLLECTION = "ICity Traffic Crowd"
TRAFFIC_VEHICLE_COLLECTION = "ICity Traffic Vehicles"
TRAFFIC_PEDESTRIAN_COLLECTION = "ICity Traffic Pedestrians"
TRAFFIC_PATH_COLLECTION = "ICity Traffic Paths"

TRAFFIC_ROAD_INNER_OBJECT = "ICITY_TRAFFIC_RoadInner"
TRAFFIC_ROAD_OUTER_OBJECT = "ICITY_TRAFFIC_RoadOuter"
TRAFFIC_WALKWAY_INNER_OBJECT = "ICITY_TRAFFIC_WalkwayInner"
TRAFFIC_WALKWAY_OUTER_OBJECT = "ICITY_TRAFFIC_WalkwayOuter"

TRAFFIC_ROAD_MATERIAL = "ICITY_TRAFFIC_Road_Material"
TRAFFIC_WALKWAY_MATERIAL = "ICITY_TRAFFIC_Walkway_Material"
TRAFFIC_CAR_MATERIAL = "ICITY_TRAFFIC_Car_Material"
TRAFFIC_TAXI_MATERIAL = "ICITY_TRAFFIC_Taxi_Material"
TRAFFIC_BUS_MATERIAL = "ICITY_TRAFFIC_Bus_Material"
TRAFFIC_PEDESTRIAN_MATERIAL = "ICITY_TRAFFIC_Pedestrian_Material"
TRAFFIC_BUNDLED_VEHICLE_ASSET_ID = "vehicle_chevrolet_m1009_01"
TRAFFIC_BUNDLED_VEHICLE_DEFAULTS = {
    "rotation_z_correction": math.pi * 0.5,
    "scale_ratio": 0.54,
    "ground_offset": 0.035,
    "lane_offset": 0.6,
    "sample_spacing": 0.75,
    "smoothing_iterations": 3,
    "corner_rounding_radius": 2.0,
    "corner_rounding_segments": 7,
    "corner_max_angle_deg": 135.0,
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _copy_vector(point: Vector) -> Vector:
    return point.copy() if hasattr(point, "copy") else Vector((point.x, point.y, point.z))


def _vector_equals(a: Vector, b: Vector) -> bool:
    return a.x == b.x and a.y == b.y and a.z == b.z


def extract_road_edge_chains(
    vertices: list[Vector],
    edge_vertex_indices: list[tuple[int, int]],
    road_deleted_flags: list[bool],
) -> list[list[Vector]]:
    active_edges = [
        edge_vertex_indices[index]
        for index in range(min(len(edge_vertex_indices), len(road_deleted_flags)))
        if not road_deleted_flags[index]
    ]
    if not active_edges:
        return []

    adjacency: dict[int, list[tuple[int, int]]] = {}
    for edge_index, (start, end) in enumerate(active_edges):
        adjacency.setdefault(start, []).append((edge_index, end))
        adjacency.setdefault(end, []).append((edge_index, start))

    visited_edges: set[int] = set()
    chains: list[list[Vector]] = []

    def walk_chain(start_vertex: int, first_edge_index: int) -> list[Vector]:
        chain = [_copy_vector(vertices[start_vertex])]
        current_vertex = start_vertex
        current_edge_index = first_edge_index
        previous_edge_index = None

        while current_edge_index is not None:
            visited_edges.add(current_edge_index)
            edge_start, edge_end = active_edges[current_edge_index]
            next_vertex = edge_end if edge_start == current_vertex else edge_start
            chain.append(_copy_vector(vertices[next_vertex]))

            next_edge_index = None
            if len(adjacency.get(next_vertex, [])) == 2:
                for candidate_edge_index, _ in adjacency[next_vertex]:
                    if candidate_edge_index != current_edge_index and candidate_edge_index not in visited_edges:
                        next_edge_index = candidate_edge_index
                        break
            else:
                for candidate_edge_index, _ in adjacency.get(next_vertex, []):
                    if candidate_edge_index not in visited_edges and candidate_edge_index != previous_edge_index:
                        next_edge_index = candidate_edge_index
                        break

            previous_edge_index = current_edge_index
            current_vertex = next_vertex
            current_edge_index = next_edge_index
        return chain

    start_vertices = [vertex_index for vertex_index, links in adjacency.items() if len(links) != 2]
    for start_vertex in start_vertices:
        for edge_index, _ in adjacency.get(start_vertex, []):
            if edge_index in visited_edges:
                continue
            chain = walk_chain(start_vertex, edge_index)
            if len(chain) >= 2:
                chains.append(chain)

    for edge_index, (start_vertex, _) in enumerate(active_edges):
        if edge_index in visited_edges:
            continue
        chain = walk_chain(start_vertex, edge_index)
        if len(chain) >= 2:
            chains.append(chain)

    return chains


def vehicle_motion_points_from_chain(chain: list[Vector]) -> list[Vector]:
    if len(chain) <= 2:
        return [_copy_vector(point) for point in chain]
    if _vector_equals(chain[0], chain[-1]):
        return [_copy_vector(point) for point in chain[:-1]]
    return [_copy_vector(point) for point in chain] + [_copy_vector(point) for point in reversed(chain[1:-1])]


def _chain_length(chain: list[Vector]) -> float:
    if len(chain) < 2:
        return 0.0
    return sum((chain[index + 1] - chain[index]).length for index in range(len(chain) - 1))


def get_base_object():
    return bpy.data.objects.get(ICITY_BASE_OBJECT)


def extract_vehicle_road_paths_from_scene() -> list[list[Vector]]:
    base_object = get_base_object()
    if base_object is None:
        return []

    mesh = getattr(base_object, "data", None)
    if mesh is None:
        return []
    attributes = getattr(mesh, "attributes", None)
    if attributes is None:
        return []
    road_deleted_attribute = attributes.get("Road del")
    if road_deleted_attribute is None:
        return []

    vertices = []
    matrix_world = getattr(base_object, "matrix_world", None)
    for vertex in getattr(mesh, "vertices", []):
        point = vertex.co
        if matrix_world is not None and hasattr(matrix_world, "__matmul__"):
            point = matrix_world @ point
        vertices.append(_copy_vector(point))

    edge_vertex_indices = [tuple(edge.vertices) for edge in getattr(mesh, "edges", [])]
    road_deleted_flags = [
        bool(getattr(data, "value", getattr(data, "value_bool", True)))
        for data in getattr(road_deleted_attribute, "data", [])
    ]
    chains = extract_road_edge_chains(vertices, edge_vertex_indices, road_deleted_flags)
    chains = [chain for chain in chains if len(chain) >= 2 and _chain_length(chain) >= 6.0]
    chains.sort(key=_chain_length, reverse=True)
    return chains


def compute_traffic_layout(center: Vector, city_radius: float, ground_z: float, settings) -> dict:
    traffic_outer_offset = max(getattr(settings, "traffic_outer_offset", 10.0), 4.0)
    traffic_lane_gap = max(getattr(settings, "traffic_lane_gap", 2.4), 1.0)
    pedestrian_outer_gap = max(getattr(settings, "pedestrian_outer_gap", 3.2), 1.2)
    pedestrian_lane_gap = max(getattr(settings, "pedestrian_lane_gap", 1.6), 0.8)

    vehicle_lane_inner_x = city_radius + traffic_outer_offset
    vehicle_lane_inner_y = max(city_radius * 0.78 + traffic_outer_offset * 0.6, city_radius + traffic_outer_offset * 0.5)
    vehicle_lane_outer_x = vehicle_lane_inner_x + traffic_lane_gap
    vehicle_lane_outer_y = vehicle_lane_inner_y + traffic_lane_gap * 0.92

    pedestrian_lane_inner_x = vehicle_lane_outer_x + pedestrian_outer_gap
    pedestrian_lane_inner_y = vehicle_lane_outer_y + pedestrian_outer_gap * 0.92
    pedestrian_lane_outer_x = pedestrian_lane_inner_x + pedestrian_lane_gap
    pedestrian_lane_outer_y = pedestrian_lane_inner_y + pedestrian_lane_gap * 0.92

    return {
        "center": Vector((center.x, center.y, ground_z)),
        "vehicle_lane_inner_x": vehicle_lane_inner_x,
        "vehicle_lane_inner_y": vehicle_lane_inner_y,
        "vehicle_lane_outer_x": vehicle_lane_outer_x,
        "vehicle_lane_outer_y": vehicle_lane_outer_y,
        "pedestrian_lane_inner_x": pedestrian_lane_inner_x,
        "pedestrian_lane_inner_y": pedestrian_lane_inner_y,
        "pedestrian_lane_outer_x": pedestrian_lane_outer_x,
        "pedestrian_lane_outer_y": pedestrian_lane_outer_y,
        "road_z": ground_z + 0.06,
        "walkway_z": ground_z + 0.1,
    }


def vehicle_type_sequence(settings) -> list[str]:
    cars = max(int(getattr(settings, "car_count", 0)), 0)
    taxis = max(int(getattr(settings, "taxi_count", 0)), 0)
    buses = max(int(getattr(settings, "bus_count", 0)), 0)

    sequence: list[str] = ["BUS"] * buses
    while cars > 0 or taxis > 0:
        if taxis > 0:
            sequence.append("TAXI")
            taxis -= 1
        if cars > 0:
            sequence.append("CAR")
            cars -= 1
        if cars > 0:
            sequence.append("CAR")
            cars -= 1
    return sequence


def clear_traffic_crowd() -> None:
    collection = bpy.data.collections.get(TRAFFIC_ROOT_COLLECTION)
    if collection is not None:
        remove_collection_recursive(collection)


def _build_flat_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.55,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = ecology_common.get_or_create_material(name)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (260, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (20, 0)
    bsdf.inputs["Base Color"].default_value = color
    ecology_common.ensure_principled_input(bsdf, ("Metallic",), metallic)
    ecology_common.ensure_principled_input(bsdf, ("Roughness",), roughness)

    if emission_strength > 0.0:
        ecology_common.ensure_principled_input(bsdf, ("Emission Strength",), emission_strength)
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input is not None:
            emission_input.default_value = color

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def _road_material() -> bpy.types.Material:
    return _build_flat_material(TRAFFIC_ROAD_MATERIAL, (0.08, 0.08, 0.09, 1.0), roughness=0.78)


def _walkway_material() -> bpy.types.Material:
    return _build_flat_material(TRAFFIC_WALKWAY_MATERIAL, (0.54, 0.50, 0.45, 1.0), roughness=0.86)


def _vehicle_material(vehicle_type: str) -> bpy.types.Material:
    if vehicle_type == "BUS":
        return _build_flat_material(TRAFFIC_BUS_MATERIAL, (0.82, 0.24, 0.18, 1.0), metallic=0.18, roughness=0.34)
    if vehicle_type == "TAXI":
        return _build_flat_material(TRAFFIC_TAXI_MATERIAL, (0.94, 0.78, 0.16, 1.0), metallic=0.16, roughness=0.26)
    return _build_flat_material(TRAFFIC_CAR_MATERIAL, (0.15, 0.35, 0.78, 1.0), metallic=0.22, roughness=0.28)


def _pedestrian_material() -> bpy.types.Material:
    return _build_flat_material(TRAFFIC_PEDESTRIAN_MATERIAL, (0.84, 0.58, 0.40, 1.0), roughness=0.66)


def _manifest_object_asset(asset_id: str) -> dict | None:
    try:
        manifest = asset_registry.load_manifest()
        return asset_registry.get_object_asset(manifest, asset_id)
    except Exception:
        return None


def bundled_vehicle_profile(vehicle_type: str) -> dict:
    profile = dict(TRAFFIC_BUNDLED_VEHICLE_DEFAULTS)
    if vehicle_type not in {"CAR", "TAXI"}:
        return profile

    asset = _manifest_object_asset(TRAFFIC_BUNDLED_VEHICLE_ASSET_ID) or {}
    for key in tuple(profile.keys()):
        if key in asset:
            profile[key] = asset[key]
    return profile


def _lerp_point(a: Vector, b: Vector, factor: float) -> Vector:
    return a * (1.0 - factor) + b * factor


def _resample_polyline(points: list[Vector], spacing: float) -> list[Vector]:
    if len(points) <= 2:
        return [_copy_vector(point) for point in points]

    spacing = max(float(spacing), 0.1)
    result = [_copy_vector(points[0])]
    remaining = spacing
    current = _copy_vector(points[0])

    for next_point in points[1:]:
        segment_start = current
        segment_end = _copy_vector(next_point)
        segment = segment_end - segment_start
        segment_length = segment.length

        while segment_length >= remaining and segment_length > 0.0:
            factor = remaining / segment_length
            sample = _lerp_point(segment_start, segment_end, factor)
            result.append(sample)
            segment_start = sample
            segment = segment_end - segment_start
            segment_length = segment.length
            remaining = spacing

        remaining -= segment_length
        current = segment_end

    if not _vector_equals(result[-1], points[-1]):
        result.append(_copy_vector(points[-1]))
    return result


def _smooth_open_polyline(points: list[Vector], iterations: int) -> list[Vector]:
    smoothed = [_copy_vector(point) for point in points]
    for _ in range(max(int(iterations), 0)):
        if len(smoothed) <= 2:
            break
        refined = [_copy_vector(smoothed[0])]
        for index in range(len(smoothed) - 1):
            start = smoothed[index]
            end = smoothed[index + 1]
            q_point = start * 0.75 + end * 0.25
            r_point = start * 0.25 + end * 0.75
            if index == 0:
                refined.append(r_point)
            elif index == len(smoothed) - 2:
                refined.append(q_point)
            else:
                refined.extend((q_point, r_point))
        refined.append(_copy_vector(smoothed[-1]))
        smoothed = refined
    return smoothed


def _cross_2d(a: Vector, b: Vector) -> float:
    return a.x * b.y - a.y * b.x


def _dot_2d(a: Vector, b: Vector) -> float:
    return a.x * b.x + a.y * b.y


def _rounded_corner_points(
    previous_point: Vector,
    corner_point: Vector,
    next_point: Vector,
    radius: float,
    segments: int,
    max_angle_deg: float,
) -> list[Vector]:
    incoming = corner_point - previous_point
    outgoing = next_point - corner_point
    incoming_length = incoming.length
    outgoing_length = outgoing.length
    if incoming_length == 0.0 or outgoing_length == 0.0:
        return [_copy_vector(corner_point)]

    incoming_dir = incoming * (1.0 / incoming_length)
    outgoing_dir = outgoing * (1.0 / outgoing_length)
    turn_cos = _clamp(_dot_2d(incoming_dir, outgoing_dir), -1.0, 1.0)
    angle_deg = math.degrees(math.acos(turn_cos))
    if angle_deg <= 1.0 or angle_deg >= float(max_angle_deg):
        return [_copy_vector(corner_point)]

    trim_distance = min(float(radius), incoming_length * 0.35, outgoing_length * 0.35)
    if trim_distance <= 1e-5:
        return [_copy_vector(corner_point)]

    entry_point = corner_point - incoming_dir * trim_distance
    exit_point = corner_point + outgoing_dir * trim_distance

    incoming_normal = Vector((-incoming_dir.y, incoming_dir.x, 0.0))
    outgoing_normal = Vector((-outgoing_dir.y, outgoing_dir.x, 0.0))
    turn_sign = 1.0 if _cross_2d(incoming_dir, outgoing_dir) >= 0.0 else -1.0
    incoming_normal = incoming_normal * turn_sign
    outgoing_normal = outgoing_normal * turn_sign

    center = None
    determinant = _cross_2d(incoming_normal, outgoing_normal)
    if abs(determinant) > 1e-5:
        delta = exit_point - entry_point
        t_value = _cross_2d(delta, outgoing_normal) / determinant
        center = entry_point + incoming_normal * t_value

    if center is None:
        return [entry_point, exit_point]

    start_angle = math.atan2(entry_point.y - center.y, entry_point.x - center.x)
    end_angle = math.atan2(exit_point.y - center.y, exit_point.x - center.x)

    if turn_sign > 0.0 and end_angle <= start_angle:
        end_angle += math.tau
    elif turn_sign < 0.0 and end_angle >= start_angle:
        end_angle -= math.tau

    arc_points = [entry_point]
    total_segments = max(int(segments), 2)
    for step in range(1, total_segments):
        factor = step / total_segments
        angle = start_angle + (end_angle - start_angle) * factor
        arc_points.append(Vector((center.x + math.cos(angle) * trim_distance, center.y + math.sin(angle) * trim_distance, corner_point.z)))
    arc_points.append(exit_point)
    return arc_points


def _round_sharp_corners(
    points: list[Vector],
    radius: float,
    segments: int,
    max_angle_deg: float,
) -> list[Vector]:
    if len(points) <= 2 or radius <= 0.0:
        return [_copy_vector(point) for point in points]

    rounded = [_copy_vector(points[0])]
    for index in range(1, len(points) - 1):
        arc_points = _rounded_corner_points(
            points[index - 1],
            points[index],
            points[index + 1],
            radius,
            segments,
            max_angle_deg,
        )
        rounded.extend(arc_points)
    rounded.append(_copy_vector(points[-1]))
    return rounded


def prepare_vehicle_path(
    chain: list[Vector],
    *,
    lane_offset: float,
    sample_spacing: float,
    smoothing_iterations: int,
    corner_rounding_radius: float,
    corner_rounding_segments: int,
    corner_max_angle_deg: float,
) -> list[Vector]:
    if len(chain) <= 2:
        if abs(lane_offset) > 1e-6:
            return _offset_chain(chain, lane_offset)
        return [_copy_vector(point) for point in chain]

    prepared = _offset_chain(chain, lane_offset) if abs(lane_offset) > 1e-6 else [_copy_vector(point) for point in chain]
    prepared = _round_sharp_corners(
        prepared,
        float(corner_rounding_radius),
        int(corner_rounding_segments),
        float(corner_max_angle_deg),
    )
    prepared = _resample_polyline(prepared, sample_spacing)
    prepared = _smooth_open_polyline(prepared, smoothing_iterations)
    return _resample_polyline(prepared, sample_spacing)


def _append_collection_hierarchy(manifest: dict, asset: dict, collection) -> dict:
    object_path = asset_registry.resolve_asset_path(manifest, asset)
    if not object_path.exists():
        raise asset_registry.AssetRegistryError(f"object file does not exist: {object_path}")

    target_kind, target_name = asset_registry.blend_asset_target(asset)
    if target_kind != "collection":
        raise asset_registry.AssetRegistryError(f"traffic vehicle asset must use collection target: {asset.get('id', '')}")

    with bpy.data.libraries.load(str(object_path), link=False) as (data_from, data_to):
        if target_name not in data_from.collections:
            raise asset_registry.AssetRegistryError(f"collection {target_name} not found in {object_path}")
        data_to.collections = [target_name]

    appended_collection = data_to.collections[0]
    collection.children.link(appended_collection)

    members = list(appended_collection.objects)
    root_name = str(asset.get("object_name", "")).strip()
    root = next((obj for obj in members if obj.name == root_name), None)
    if root is None:
        root = next((obj for obj in members if obj.parent is None), None)
    if root is None:
        raise asset_registry.AssetRegistryError(f"collection asset has no usable root object: {asset.get('id', '')}")

    for obj in members:
        obj.hide_render = True
        obj.hide_viewport = True
        obj.hide_select = True

    return {"collection": appended_collection, "root": root, "members": members}


def _load_bundled_vehicle_template(vehicle_type: str, collection):
    if vehicle_type not in {"CAR", "TAXI"}:
        return None

    try:
        manifest = asset_registry.load_manifest()
        asset = asset_registry.get_object_asset(manifest, TRAFFIC_BUNDLED_VEHICLE_ASSET_ID)
        return _append_collection_hierarchy(manifest, asset, collection)
    except Exception:
        return None


def _copy_hierarchy_member(source, name: str):
    obj = source.copy()
    if getattr(source, "animation_data", None) is not None:
        obj.animation_data_clear()
    obj.name = name
    return obj


def _create_collection_vehicle_follower(
    *,
    name: str,
    collection,
    vehicle_type: str,
    template: dict,
    path_obj,
    frame_start: int,
    frame_end: int,
    phase_start: float,
    scale: float,
    rotation_z_correction: float,
    ground_offset: float,
) -> bpy.types.Object:
    carrier = bpy.data.objects.new(f"{name}_Carrier", None)
    carrier.empty_display_type = "PLAIN_AXES"
    carrier.empty_display_size = 0.12
    carrier.hide_render = True
    carrier.hide_select = True
    collection.objects.link(carrier)

    path_points_world = [Vector((point.co.x, point.co.y, point.co.z)) for point in path_obj.data.splines[0].points]
    ecology_common.keyframe_path_motion(
        carrier,
        path_points_world,
        path_obj.location,
        frame_start,
        frame_end,
        phase_start,
        sample_count=max(12, len(path_points_world)),
    )

    duplicates = {}
    root_source = template["root"]
    root_clone = None
    for source in template["members"]:
        clone = _copy_hierarchy_member(source, f"{name}_{source.name}")
        collection.objects.link(clone)
        clone.hide_render = False
        clone.hide_viewport = False
        clone.hide_select = False
        duplicates[source] = clone
        if source == root_source:
            root_clone = clone

    if root_clone is None:
        raise RuntimeError(f"Vehicle template root missing for {vehicle_type}")

    for source, clone in duplicates.items():
        parent = source.parent
        if parent in duplicates:
            clone.parent = duplicates[parent]
        else:
            clone.parent = carrier
        if hasattr(source, "matrix_parent_inverse") and hasattr(source.matrix_parent_inverse, "copy"):
            clone.matrix_parent_inverse = source.matrix_parent_inverse.copy()

    root_clone.location = Vector((0.0, 0.0, ground_offset))
    root_clone.rotation_euler = (0.0, 0.0, rotation_z_correction)
    root_clone.scale = (scale, scale, scale)
    return root_clone


def _vehicle_mesh(vehicle_type: str, scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    if vehicle_type == "BUS":
        vertices = [
            (-1.80, -0.50, 0.00),
            (-1.80, 0.50, 0.00),
            (1.90, -0.50, 0.00),
            (1.90, 0.50, 0.00),
            (-1.55, -0.44, 0.82),
            (-1.55, 0.44, 0.82),
            (1.55, -0.44, 0.82),
            (1.55, 0.44, 0.82),
        ]
    else:
        vertices = [
            (-1.10, -0.46, 0.00),
            (-1.10, 0.46, 0.00),
            (1.12, -0.46, 0.00),
            (1.12, 0.46, 0.00),
            (-0.78, -0.40, 0.56),
            (-0.78, 0.40, 0.56),
            (0.42, -0.40, 0.62),
            (0.42, 0.40, 0.62),
            (0.96, -0.28, 0.40),
            (0.96, 0.28, 0.40),
        ]
    faces = [
        (0, 1, 5, 4),
        (0, 2, 6, 4),
        (1, 3, 7, 5),
        (2, 3, 7 if len(vertices) == 8 else 9, 6 if len(vertices) == 8 else 8),
        (4, 5, 7, 6),
        (0, 1, 3, 2),
    ]
    if len(vertices) == 10:
        faces.extend(
            [
                (6, 7, 9, 8),
                (2, 8, 9, 3),
            ]
        )
    return ([(x * scale, y * scale, z * scale) for x, y, z in vertices], faces)


def _pedestrian_mesh(scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    vertices = [
        (-0.16, -0.12, 0.00),
        (-0.16, 0.12, 0.00),
        (0.16, -0.12, 0.00),
        (0.16, 0.12, 0.00),
        (-0.14, -0.10, 0.58),
        (-0.14, 0.10, 0.58),
        (0.14, -0.10, 0.58),
        (0.14, 0.10, 0.58),
        (-0.10, -0.10, 0.82),
        (-0.10, 0.10, 0.82),
        (0.10, -0.10, 0.82),
        (0.10, 0.10, 0.82),
    ]
    faces = [
        (0, 1, 5, 4),
        (0, 2, 6, 4),
        (2, 3, 7, 6),
        (1, 3, 7, 5),
        (4, 5, 7, 6),
        (8, 9, 11, 10),
        (4, 5, 9, 8),
        (6, 7, 11, 10),
        (4, 6, 10, 8),
        (5, 7, 11, 9),
    ]
    return ([(x * scale, y * scale, z * scale) for x, y, z in vertices], faces)


def _ellipse_points(center: Vector, radius_x: float, radius_y: float, z: float, count: int) -> list[Vector]:
    return ecology_common.ellipse_points(Vector((center.x, center.y)), radius_x, radius_y, 0.0, count, z)


def _build_vehicle_and_walkway_surfaces(layout: dict, settings, vehicle_collection, pedestrian_collection) -> dict:
    center = layout["center"]
    road_width = _clamp(getattr(settings, "road_width", 3.4), 1.8, 12.0)
    walkway_width = _clamp(getattr(settings, "walkway_width", 1.8), 0.8, 6.0)

    inner_vehicle_points = _ellipse_points(
        center,
        layout["vehicle_lane_inner_x"],
        layout["vehicle_lane_inner_y"],
        layout["road_z"],
        48,
    )
    outer_vehicle_points = _ellipse_points(
        center,
        layout["vehicle_lane_outer_x"],
        layout["vehicle_lane_outer_y"],
        layout["road_z"] + 0.01,
        48,
    )
    inner_walk_points = _ellipse_points(
        center,
        layout["pedestrian_lane_inner_x"],
        layout["pedestrian_lane_inner_y"],
        layout["walkway_z"],
        56,
    )
    outer_walk_points = _ellipse_points(
        center,
        layout["pedestrian_lane_outer_x"],
        layout["pedestrian_lane_outer_y"],
        layout["walkway_z"] + 0.01,
        56,
    )

    ecology_common.create_strip_from_closed_points(
        TRAFFIC_ROAD_INNER_OBJECT,
        inner_vehicle_points,
        road_width,
        vehicle_collection,
        Vector((0.0, 0.0, 0.0)),
        _road_material(),
    )
    ecology_common.create_strip_from_closed_points(
        TRAFFIC_ROAD_OUTER_OBJECT,
        outer_vehicle_points,
        road_width,
        vehicle_collection,
        Vector((0.0, 0.0, 0.0)),
        _road_material(),
    )
    ecology_common.create_strip_from_closed_points(
        TRAFFIC_WALKWAY_INNER_OBJECT,
        inner_walk_points,
        walkway_width,
        pedestrian_collection,
        Vector((0.0, 0.0, 0.0)),
        _walkway_material(),
    )
    ecology_common.create_strip_from_closed_points(
        TRAFFIC_WALKWAY_OUTER_OBJECT,
        outer_walk_points,
        walkway_width,
        pedestrian_collection,
        Vector((0.0, 0.0, 0.0)),
        _walkway_material(),
    )
    return {
        "inner_vehicle_points": inner_vehicle_points,
        "outer_vehicle_points": outer_vehicle_points,
        "inner_walk_points": inner_walk_points,
        "outer_walk_points": outer_walk_points,
    }


def _generate_vehicles(settings, path_collection, vehicle_collection, surface_points: dict) -> None:
    frame_start = settings.animation_start
    frame_end = settings.animation_end
    frame_count = max(frame_end - frame_start, 2)

    path_inner = ecology_common.create_follow_path(
        "ICITY_TRAFFIC_Path_InnerRoad",
        surface_points["inner_vehicle_points"],
        path_collection,
        Vector((0.0, 0.0, 0.0)),
        frame_count,
    )
    path_outer = ecology_common.create_follow_path(
        "ICITY_TRAFFIC_Path_OuterRoad",
        surface_points["outer_vehicle_points"],
        path_collection,
        Vector((0.0, 0.0, 0.0)),
        frame_count,
    )

    sequence = vehicle_type_sequence(settings)
    total = max(len(sequence), 1)
    base_vehicle_scale = _clamp(getattr(settings, "vehicle_scale", 0.78), 0.3, 2.4)
    bus_scale = _clamp(getattr(settings, "bus_scale", 1.18), 0.5, 3.0)
    vehicle_templates: dict[str, dict | None] = {}

    for index, vehicle_type in enumerate(sequence):
        phase = index / total
        path_obj = path_outer if vehicle_type == "BUS" else path_inner
        mesh_scale = bus_scale if vehicle_type == "BUS" else base_vehicle_scale
        profile = bundled_vehicle_profile(vehicle_type)
        template = vehicle_templates.get(vehicle_type)
        if vehicle_type not in vehicle_templates:
            template = _load_bundled_vehicle_template(vehicle_type, vehicle_collection)
            vehicle_templates[vehicle_type] = template
        name = f"ICITY_TRAFFIC_{vehicle_type}_{index + 1}"
        if template is not None:
            _create_collection_vehicle_follower(
                name=name,
                collection=vehicle_collection,
                vehicle_type=vehicle_type,
                template=template,
                path_obj=path_obj,
                frame_start=frame_start,
                frame_end=frame_end,
                phase_start=phase,
                scale=mesh_scale * float(profile["scale_ratio"]),
                rotation_z_correction=float(profile["rotation_z_correction"]),
                ground_offset=float(profile["ground_offset"]),
            )
            continue

        vertices, faces = _vehicle_mesh(vehicle_type, mesh_scale)
        ecology_common.create_follower(
            name=name,
            collection=vehicle_collection,
            mesh_vertices=vertices,
            mesh_faces=faces,
            material=_vehicle_material(vehicle_type),
            path_obj=path_obj,
            frame_start=frame_start,
            frame_end=frame_end,
            phase_start=phase,
            bobbing=(0.02, 0.05),
        )


def _offset_chain(points: list[Vector], offset: float) -> list[Vector]:
    if len(points) < 2:
        return [_copy_vector(point) for point in points]
    shifted_points: list[Vector] = []
    for index, point in enumerate(points):
        previous_point = points[index - 1] if index > 0 else points[index]
        next_point = points[index + 1] if index < len(points) - 1 else points[index]
        tangent = next_point - previous_point
        tangent_length = math.sqrt(tangent.x * tangent.x + tangent.y * tangent.y)
        if tangent_length == 0.0:
            normal = Vector((0.0, 1.0, 0.0))
        else:
            normal = Vector((-tangent.y / tangent_length, tangent.x / tangent_length, 0.0))
        shifted_points.append(Vector((point.x + normal.x * offset, point.y + normal.y * offset, point.z)))
    return shifted_points


def _generate_vehicles_on_road_paths(settings, path_collection, vehicle_collection, road_paths: list[list[Vector]]) -> None:
    sequence = vehicle_type_sequence(settings)
    if not road_paths or not sequence:
        return

    frame_start = settings.animation_start
    frame_end = settings.animation_end
    frame_count = max(frame_end - frame_start, 2)
    base_vehicle_scale = _clamp(getattr(settings, "vehicle_scale", 0.78), 0.3, 2.4)
    bus_scale = _clamp(getattr(settings, "bus_scale", 1.18), 0.5, 3.0)

    passenger_profile = bundled_vehicle_profile("CAR")
    bus_profile = bundled_vehicle_profile("BUS")
    passenger_route_paths = []
    bus_route_paths = []
    lane_offset = abs(float(passenger_profile["lane_offset"]))
    passenger_offsets = (lane_offset, -lane_offset) if lane_offset > 1e-6 else (0.0,)

    for route_index, road_path in enumerate(road_paths):
        prepared_bus_path = prepare_vehicle_path(
            road_path,
            lane_offset=0.0,
            sample_spacing=float(bus_profile["sample_spacing"]),
            smoothing_iterations=int(bus_profile["smoothing_iterations"]),
            corner_rounding_radius=float(bus_profile["corner_rounding_radius"]),
            corner_rounding_segments=int(bus_profile["corner_rounding_segments"]),
            corner_max_angle_deg=float(bus_profile["corner_max_angle_deg"]),
        )
        bus_motion_points = vehicle_motion_points_from_chain(prepared_bus_path)
        if len(bus_motion_points) >= 2:
            path_obj = ecology_common.create_follow_path(
                f"ICITY_TRAFFIC_RoadPath_Bus_{route_index + 1}",
                bus_motion_points,
                path_collection,
                Vector((0.0, 0.0, 0.0)),
                frame_count,
            )
            bus_route_paths.append(path_obj)

        for lane_index, offset in enumerate(passenger_offsets):
            prepared_path = prepare_vehicle_path(
                road_path,
                lane_offset=offset,
                sample_spacing=float(passenger_profile["sample_spacing"]),
                smoothing_iterations=int(passenger_profile["smoothing_iterations"]),
                corner_rounding_radius=float(passenger_profile["corner_rounding_radius"]),
                corner_rounding_segments=int(passenger_profile["corner_rounding_segments"]),
                corner_max_angle_deg=float(passenger_profile["corner_max_angle_deg"]),
            )
            motion_points = vehicle_motion_points_from_chain(prepared_path)
            if len(motion_points) < 2:
                continue
            path_obj = ecology_common.create_follow_path(
                f"ICITY_TRAFFIC_RoadPath_{route_index + 1}_Lane_{lane_index + 1}",
                motion_points,
                path_collection,
                Vector((0.0, 0.0, 0.0)),
                frame_count,
            )
            passenger_route_paths.append(path_obj)

    if not passenger_route_paths and not bus_route_paths:
        return

    total = max(len(sequence), 1)
    vehicle_templates: dict[str, dict | None] = {}
    for index, vehicle_type in enumerate(sequence):
        path_pool = bus_route_paths if vehicle_type == "BUS" and bus_route_paths else passenger_route_paths or bus_route_paths
        if not path_pool:
            continue
        path_obj = path_pool[index % len(path_pool)]
        mesh_scale = bus_scale if vehicle_type == "BUS" else base_vehicle_scale
        profile = bundled_vehicle_profile(vehicle_type)
        template = vehicle_templates.get(vehicle_type)
        if vehicle_type not in vehicle_templates:
            template = _load_bundled_vehicle_template(vehicle_type, vehicle_collection)
            vehicle_templates[vehicle_type] = template
        name = f"ICITY_TRAFFIC_{vehicle_type}_{index + 1}"
        if template is not None:
            _create_collection_vehicle_follower(
                name=name,
                collection=vehicle_collection,
                vehicle_type=vehicle_type,
                template=template,
                path_obj=path_obj,
                frame_start=frame_start,
                frame_end=frame_end,
                phase_start=index / total,
                scale=mesh_scale * float(profile["scale_ratio"]),
                rotation_z_correction=float(profile["rotation_z_correction"]),
                ground_offset=float(profile["ground_offset"]),
            )
            continue

        vertices, faces = _vehicle_mesh(vehicle_type, mesh_scale)
        ecology_common.create_follower(
            name=name,
            collection=vehicle_collection,
            mesh_vertices=vertices,
            mesh_faces=faces,
            material=_vehicle_material(vehicle_type),
            path_obj=path_obj,
            frame_start=frame_start,
            frame_end=frame_end,
            phase_start=index / total,
            bobbing=(0.02, 0.05),
        )


def _generate_pedestrians_near_road_paths(settings, path_collection, pedestrian_collection, road_paths: list[list[Vector]]) -> None:
    pedestrian_count = max(getattr(settings, "pedestrian_count", 0), 0)
    if not road_paths or pedestrian_count == 0:
        return

    frame_start = settings.animation_start
    frame_end = settings.animation_end
    frame_count = max(frame_end - frame_start, 2)
    pedestrian_scale = _clamp(getattr(settings, "pedestrian_scale", 0.92), 0.4, 2.2)
    vertices, faces = _pedestrian_mesh(pedestrian_scale)

    route_paths = []
    for route_index, road_path in enumerate(road_paths):
        offset = 1.25 if route_index % 2 == 0 else -1.25
        motion_points = vehicle_motion_points_from_chain(_offset_chain(road_path, offset))
        if len(motion_points) < 2:
            continue
        path_obj = ecology_common.create_follow_path(
            f"ICITY_TRAFFIC_WalkPath_{route_index + 1}",
            motion_points,
            path_collection,
            Vector((0.0, 0.0, 0.0)),
            frame_count,
        )
        route_paths.append(path_obj)
    if not route_paths:
        return

    for index in range(pedestrian_count):
        ecology_common.create_follower(
            name=f"ICITY_TRAFFIC_Pedestrian_{index + 1}",
            collection=pedestrian_collection,
            mesh_vertices=vertices,
            mesh_faces=faces,
            material=_pedestrian_material(),
            path_obj=route_paths[index % len(route_paths)],
            frame_start=frame_start,
            frame_end=frame_end,
            phase_start=index / max(pedestrian_count, 1),
            bobbing=(0.0, 0.04),
        )


def _generate_pedestrians(settings, path_collection, pedestrian_collection, surface_points: dict) -> None:
    frame_start = settings.animation_start
    frame_end = settings.animation_end
    frame_count = max(frame_end - frame_start, 2)
    pedestrian_count = max(getattr(settings, "pedestrian_count", 0), 0)
    if pedestrian_count == 0:
        return

    path_inner = ecology_common.create_follow_path(
        "ICITY_TRAFFIC_Path_InnerWalk",
        surface_points["inner_walk_points"],
        path_collection,
        Vector((0.0, 0.0, 0.0)),
        frame_count,
    )
    path_outer = ecology_common.create_follow_path(
        "ICITY_TRAFFIC_Path_OuterWalk",
        list(reversed(surface_points["outer_walk_points"])),
        path_collection,
        Vector((0.0, 0.0, 0.0)),
        frame_count,
    )
    vertices, faces = _pedestrian_mesh(_clamp(getattr(settings, "pedestrian_scale", 0.92), 0.4, 2.2))
    for index in range(pedestrian_count):
        use_outer = index % 2 == 0
        phase = index / pedestrian_count
        ecology_common.create_follower(
            name=f"ICITY_TRAFFIC_Pedestrian_{index + 1}",
            collection=pedestrian_collection,
            mesh_vertices=vertices,
            mesh_faces=faces,
            material=_pedestrian_material(),
            path_obj=path_outer if use_outer else path_inner,
            frame_start=frame_start,
            frame_end=frame_end,
            phase_start=phase,
            bobbing=(0.0, 0.04),
        )


def generate_traffic_crowd(context: bpy.types.Context) -> None:
    settings = context.scene.icity_traffic_settings
    root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root_collection is None:
        raise RuntimeError("Please run iCity Start before generating traffic and crowd.")

    clear_traffic_crowd()

    traffic_root = ecology_common.get_or_create_child_collection(root_collection, TRAFFIC_ROOT_COLLECTION)
    vehicle_collection = ecology_common.get_or_create_child_collection(traffic_root, TRAFFIC_VEHICLE_COLLECTION)
    pedestrian_collection = ecology_common.get_or_create_child_collection(traffic_root, TRAFFIC_PEDESTRIAN_COLLECTION)
    path_collection = ecology_common.get_or_create_child_collection(traffic_root, TRAFFIC_PATH_COLLECTION)

    road_paths = extract_vehicle_road_paths_from_scene()
    if road_paths:
        _generate_vehicles_on_road_paths(settings, path_collection, vehicle_collection, road_paths)
        _generate_pedestrians_near_road_paths(settings, path_collection, pedestrian_collection, road_paths)
    else:
        center, city_radius, ground_z = ecology_common.get_city_bounds()
        layout = compute_traffic_layout(center, city_radius, ground_z, settings)
        surface_points = _build_vehicle_and_walkway_surfaces(layout, settings, vehicle_collection, pedestrian_collection)
        _generate_vehicles(settings, path_collection, vehicle_collection, surface_points)
        _generate_pedestrians(settings, path_collection, pedestrian_collection, surface_points)

    context.scene.frame_start = settings.animation_start
    context.scene.frame_end = settings.animation_end
    context.scene.frame_set(settings.animation_start)


class ICITY_TrafficSettings(PropertyGroup):
    animation_start: IntProperty(name="Start Frame", default=1, min=1, max=100000)
    animation_end: IntProperty(name="End Frame", default=250, min=2, max=100000)

    car_count: IntProperty(name="Cars", default=6, min=0, max=60)
    taxi_count: IntProperty(name="Taxis", default=2, min=0, max=30)
    bus_count: IntProperty(name="Buses", default=1, min=0, max=12)
    pedestrian_count: IntProperty(name="Pedestrians", default=12, min=0, max=80)

    traffic_outer_offset: FloatProperty(name="Traffic Offset", default=10.0, min=4.0, max=80.0)
    traffic_lane_gap: FloatProperty(name="Lane Gap", default=2.4, min=1.0, max=10.0)
    pedestrian_outer_gap: FloatProperty(name="Walkway Offset", default=3.2, min=1.2, max=16.0)
    pedestrian_lane_gap: FloatProperty(name="Walk Lane Gap", default=1.6, min=0.8, max=8.0)

    road_width: FloatProperty(name="Road Width", default=3.4, min=1.8, max=12.0)
    walkway_width: FloatProperty(name="Walkway Width", default=1.8, min=0.8, max=6.0)
    vehicle_scale: FloatProperty(name="Vehicle Scale", default=0.78, min=0.3, max=2.4)
    bus_scale: FloatProperty(name="Bus Scale", default=1.18, min=0.5, max=3.0)
    pedestrian_scale: FloatProperty(name="Pedestrian Scale", default=0.92, min=0.4, max=2.2)


class ICITY_OT_GenerateTrafficCrowd(Operator):
    bl_idname = "icity.generate_traffic_crowd"
    bl_label = "Generate / Update"
    bl_description = "Generate standalone traffic and crowd around the current iCity scene"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        settings = context.scene.icity_traffic_settings
        if settings.animation_end <= settings.animation_start:
            self.report({"ERROR"}, "End Frame must be greater than Start Frame.")
            return {"CANCELLED"}
        try:
            generate_traffic_crowd(context)
        except Exception as exc:  # pragma: no cover
            self.report({"ERROR"}, f"Traffic and crowd generation failed: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, "ICity traffic and crowd generated.")
        return {"FINISHED"}


class ICITY_OT_ClearTrafficCrowd(Operator):
    bl_idname = "icity.clear_traffic_crowd"
    bl_label = "Clear"
    bl_description = "Clear standalone traffic and crowd generated by this module"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        clear_traffic_crowd()
        self.report({"INFO"}, "ICity traffic and crowd cleared.")
        return {"FINISHED"}


class ICITY_PT_TrafficCrowdPanel(Panel):
    bl_label = "ICity Traffic & Crowd"
    bl_idname = "ICITY_PT_traffic_crowd_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.icity_traffic_settings

        count_box = layout.box()
        count_box.label(text="Dynamic Agents", icon="OUTLINER_COLLECTION")
        count_box.prop(settings, "car_count")
        count_box.prop(settings, "taxi_count")
        count_box.prop(settings, "bus_count")
        count_box.prop(settings, "pedestrian_count")

        band_box = layout.box()
        band_box.label(text="Layout", icon="ORIENTATION_VIEW")
        band_box.prop(settings, "traffic_outer_offset")
        band_box.prop(settings, "traffic_lane_gap")
        band_box.prop(settings, "pedestrian_outer_gap")
        band_box.prop(settings, "pedestrian_lane_gap")
        band_box.prop(settings, "road_width")
        band_box.prop(settings, "walkway_width")

        scale_box = layout.box()
        scale_box.label(text="Scale", icon="EMPTY_AXIS")
        scale_box.prop(settings, "vehicle_scale")
        scale_box.prop(settings, "bus_scale")
        scale_box.prop(settings, "pedestrian_scale")

        anim_box = layout.box()
        anim_box.label(text="Animation", icon="TIME")
        anim_box.prop(settings, "animation_start")
        anim_box.prop(settings, "animation_end")

        row = layout.row(align=True)
        row.operator("icity.generate_traffic_crowd", icon="PLAY")
        row.operator("icity.clear_traffic_crowd", icon="TRASH")


CLASSES = (
    ICITY_TrafficSettings,
    ICITY_OT_GenerateTrafficCrowd,
    ICITY_OT_ClearTrafficCrowd,
    ICITY_PT_TrafficCrowdPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_traffic_settings = PointerProperty(type=ICITY_TrafficSettings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "icity_traffic_settings"):
        del bpy.types.Scene.icity_traffic_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

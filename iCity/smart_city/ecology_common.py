"""Shared helpers for the standalone ICity ecology extension."""

from __future__ import annotations

import math
from typing import Iterable

import bpy
from mathutils import Vector
from mathutils import noise as mathnoise


ICITY_ROOT_COLLECTION = "ICity"
ICITY_BASE_OBJECT = "ICity Base"
ECOLOGY_COLLECTION = "ICity Ecology"
ECOLOGY_TERRAIN_COLLECTION = "ICity Ecology Terrain"
ECOLOGY_WATER_COLLECTION = "ICity Ecology Water"
ECOLOGY_BOAT_COLLECTION = "ICity Ecology Boats"
ECOLOGY_TRAFFIC_COLLECTION = "ICity Ecology Traffic"
ECOLOGY_CROWD_COLLECTION = "ICity Ecology Crowd"
ECOLOGY_PATH_COLLECTION = "ICity Ecology Paths"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge0 == edge1:
        return 0.0
    factor = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return factor * factor * (3.0 - 2.0 * factor)


def rotate_2d(point: Vector, angle: float) -> Vector:
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vector((point.x * cos_a - point.y * sin_a, point.x * sin_a + point.y * cos_a))


def rotate_2d_inverse(point: Vector, angle: float) -> Vector:
    return rotate_2d(point, -angle)


def evaluate_noise(position: Vector, seed: int, scale: float, octaves: int = 4) -> float:
    sample = Vector(
        (
            position.x * scale + seed * 0.173,
            position.y * scale - seed * 0.217,
            seed * 0.071,
        )
    )
    return mathnoise.fractal(sample, 1.0, 2.0, octaves)


def evaluate_turbulence(position: Vector, seed: int, scale: float, octaves: int = 4) -> float:
    sample = Vector(
        (
            position.x * scale - seed * 0.113,
            position.y * scale + seed * 0.131,
            seed * 0.053,
        )
    )
    return mathnoise.turbulence(sample, octaves, False)


def object_world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    if getattr(obj, "bound_box", None):
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    else:
        corners = [obj.matrix_world.translation.copy()]
    min_corner = Vector(
        (
            min(corner.x for corner in corners),
            min(corner.y for corner in corners),
            min(corner.z for corner in corners),
        )
    )
    max_corner = Vector(
        (
            max(corner.x for corner in corners),
            max(corner.y for corner in corners),
            max(corner.z for corner in corners),
        )
    )
    return min_corner, max_corner


def merge_bounds(bounds: Iterable[tuple[Vector, Vector]]) -> tuple[Vector, Vector] | None:
    bounds = list(bounds)
    if not bounds:
        return None
    min_corner = Vector(
        (
            min(bound[0].x for bound in bounds),
            min(bound[0].y for bound in bounds),
            min(bound[0].z for bound in bounds),
        )
    )
    max_corner = Vector(
        (
            max(bound[1].x for bound in bounds),
            max(bound[1].y for bound in bounds),
            max(bound[1].z for bound in bounds),
        )
    )
    return min_corner, max_corner


def get_city_bounds() -> tuple[Vector, float, float]:
    base_object = bpy.data.objects.get(ICITY_BASE_OBJECT)
    if base_object is not None:
        min_corner, max_corner = object_world_bounds(base_object)
    else:
        root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
        if root_collection is None:
            return Vector((0.0, 0.0, 0.0)), 30.0, 0.0
        object_bounds = []
        for obj in root_collection.all_objects:
            if obj.name.startswith("ICITY_ECO_"):
                continue
            if any(collection.name == "ICity Assets" for collection in obj.users_collection):
                continue
            if obj.type in {"MESH", "CURVE", "SURFACE", "FONT"}:
                object_bounds.append(object_world_bounds(obj))
        merged = merge_bounds(object_bounds)
        if merged is None:
            return Vector((0.0, 0.0, 0.0)), 30.0, 0.0
        min_corner, max_corner = merged
    center = (min_corner + max_corner) * 0.5
    radius = max(max_corner.x - min_corner.x, max_corner.y - min_corner.y) * 0.5
    radius = max(radius, 20.0)
    return center, radius, min_corner.z


def get_or_create_child_collection(
    parent: bpy.types.Collection, name: str
) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    if parent.children.get(collection.name) is None:
        parent.children.link(collection)
    return collection


def remove_object_and_data(obj: bpy.types.Object) -> None:
    data = getattr(obj, "data", None)
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is None or data.users != 0:
        return
    if isinstance(data, bpy.types.Mesh):
        bpy.data.meshes.remove(data)
    elif isinstance(data, bpy.types.Curve):
        bpy.data.curves.remove(data)


def remove_collection_recursive(collection: bpy.types.Collection) -> None:
    for child in list(collection.children):
        remove_collection_recursive(child)
    for obj in list(collection.objects):
        remove_object_and_data(obj)
    for parent in list(bpy.data.collections):
        if parent.children.get(collection.name) is not None:
            parent.children.unlink(collection)
    if bpy.context.scene.collection.children.get(collection.name) is not None:
        bpy.context.scene.collection.children.unlink(collection)
    bpy.data.collections.remove(collection)


def clear_existing_ecology() -> None:
    ecology_collection = bpy.data.collections.get(ECOLOGY_COLLECTION)
    if ecology_collection is not None:
        remove_collection_recursive(ecology_collection)


def create_mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    collection: bpy.types.Collection,
    location: Vector,
    material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    if material is not None:
        mesh.materials.clear()
        mesh.materials.append(material)
    return obj


def distance_to_segment_2d(point: Vector, start: Vector, end: Vector) -> float:
    segment = end - start
    if segment.length_squared == 0.0:
        return (point - start).length
    factor = clamp((point - start).dot(segment) / segment.length_squared, 0.0, 1.0)
    projection = start + segment * factor
    return (point - projection).length


def distance_to_polyline(point: Vector, points: list[Vector]) -> float:
    return min(
        distance_to_segment_2d(point, points[index], points[index + 1])
        for index in range(len(points) - 1)
    )


def add_subdivision_modifier(obj: bpy.types.Object, levels: int, render_levels: int) -> None:
    modifier = obj.modifiers.new(name="ICITY_ECO_Subdivision", type="SUBSURF")
    modifier.levels = levels
    modifier.render_levels = render_levels


def add_wave_modifier(obj: bpy.types.Object, seed: int, height: float, width: float) -> None:
    modifier = obj.modifiers.new(name="ICITY_ECO_Wave", type="WAVE")
    modifier.height = height
    modifier.width = width
    modifier.speed = 0.18
    modifier.narrowness = 1.5
    modifier.use_x = True
    modifier.use_y = True
    modifier.time_offset = seed * 0.35


def ensure_principled_input(
    node: bpy.types.Node,
    socket_names: Iterable[str],
    value,
) -> None:
    for socket_name in socket_names:
        socket = node.inputs.get(socket_name)
        if socket is not None:
            socket.default_value = value
            return


def get_or_create_material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    return material


def ellipse_points(
    center: Vector,
    radius_x: float,
    radius_y: float,
    rotation: float,
    count: int,
    z: float,
) -> list[Vector]:
    points = []
    for index in range(count):
        angle = (index / count) * math.tau
        local = Vector((math.cos(angle) * radius_x, math.sin(angle) * radius_y))
        world = center + rotate_2d(local, rotation)
        points.append(Vector((world.x, world.y, z)))
    return points


def create_strip_from_closed_points(
    name: str,
    points: list[Vector],
    width: float,
    collection: bpy.types.Collection,
    location: Vector,
    material: bpy.types.Material,
) -> bpy.types.Object:
    half_width = width * 0.5
    left_vertices = []
    right_vertices = []
    point_count = len(points)
    for index, point in enumerate(points):
        previous_point = points[index - 1]
        next_point = points[(index + 1) % point_count]
        tangent = (next_point - previous_point).normalized()
        normal = Vector((-tangent.y, tangent.x, 0.0))
        left_vertices.append((point.x + normal.x * half_width, point.y + normal.y * half_width, point.z))
        right_vertices.append((point.x - normal.x * half_width, point.y - normal.y * half_width, point.z))

    vertices = left_vertices + right_vertices
    faces = []
    for index in range(point_count):
        next_index = (index + 1) % point_count
        right_index = point_count + index
        right_next_index = point_count + next_index
        faces.append((index, next_index, right_next_index, right_index))

    return create_mesh_object(name, vertices, faces, collection, location, material)


def set_linear_interpolation(action: bpy.types.Action | None) -> None:
    if action is None:
        return
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"


def add_cycles_modifier(action: bpy.types.Action | None) -> None:
    if action is None:
        return
    for fcurve in action.fcurves:
        modifier = fcurve.modifiers.new(type="CYCLES")
        modifier.mode_before = "REPEAT"
        modifier.mode_after = "REPEAT"


def _sample_path_point(path_points: list[Vector], offset_factor: float) -> Vector:
    if not path_points:
        return Vector((0.0, 0.0, 0.0))
    point_count = len(path_points)
    position = (offset_factor % 1.0) * point_count
    base_index = int(math.floor(position)) % point_count
    next_index = (base_index + 1) % point_count
    blend = position - math.floor(position)
    return path_points[base_index] * (1.0 - blend) + path_points[next_index] * blend


def keyframe_path_motion(
    carrier: bpy.types.Object,
    path_points: list[Vector],
    terrain_origin: Vector,
    frame_start: int,
    frame_end: int,
    phase_start: float,
    sample_count: int = 16,
) -> None:
    frame_span = max(frame_end - frame_start, 1)
    total_samples = max(sample_count, 4)
    carrier.rotation_mode = "XYZ"
    for sample_index in range(total_samples + 1):
        factor = sample_index / total_samples
        frame = int(round(frame_start + frame_span * factor))
        point = _sample_path_point(path_points, phase_start + factor)
        next_point = _sample_path_point(path_points, phase_start + factor + (1.0 / (total_samples * 4.0)))
        delta = next_point - point
        carrier.location = terrain_origin + point
        carrier.rotation_euler = (0.0, 0.0, math.atan2(delta.y, delta.x))
        carrier.keyframe_insert(data_path="location", frame=frame)
        carrier.keyframe_insert(data_path="rotation_euler", frame=frame)
    set_linear_interpolation(carrier.animation_data.action if carrier.animation_data else None)
    add_cycles_modifier(carrier.animation_data.action if carrier.animation_data else None)


def create_follow_path(
    name: str,
    path_points: list[Vector],
    collection: bpy.types.Collection,
    location: Vector,
    frame_count: int,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 24
    curve_data.use_path = True
    curve_data.path_duration = max(frame_count, 2)
    spline = curve_data.splines.new("NURBS")
    spline.points.add(len(path_points) - 1)
    spline.order_u = min(4, len(path_points))
    spline.use_cyclic_u = True
    for index, point in enumerate(path_points):
        spline.points[index].co = (point.x, point.y, point.z, 1.0)
    path_obj = bpy.data.objects.new(name, curve_data)
    path_obj.location = location
    path_obj.hide_render = True
    path_obj.hide_viewport = True
    path_obj.hide_select = True
    collection.objects.link(path_obj)
    return path_obj


def create_follower(
    name: str,
    collection: bpy.types.Collection,
    mesh_vertices: list[tuple[float, float, float]],
    mesh_faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    path_obj: bpy.types.Object,
    frame_start: int,
    frame_end: int,
    phase_start: float,
    bobbing: tuple[float, float] | None = None,
) -> bpy.types.Object:
    carrier = bpy.data.objects.new(f"{name}_Carrier", None)
    carrier.empty_display_type = "PLAIN_AXES"
    carrier.empty_display_size = 0.12
    carrier.hide_render = True
    carrier.hide_select = True
    collection.objects.link(carrier)

    path_points_world = [
        Vector((point.co.x, point.co.y, point.co.z))
        for point in path_obj.data.splines[0].points
    ]
    keyframe_path_motion(
        carrier,
        path_points_world,
        path_obj.location,
        frame_start,
        frame_end,
        phase_start,
        sample_count=max(12, len(path_points_world)),
    )

    obj = create_mesh_object(name, mesh_vertices, mesh_faces, collection, Vector((0.0, 0.0, 0.0)), material)
    obj.parent = carrier
    obj.location = Vector((0.0, 0.0, 0.0))
    obj.rotation_mode = "XYZ"

    if bobbing is not None:
        low, high = bobbing
        for frame, z_value in (
            (frame_start, low),
            (frame_start + (frame_end - frame_start) * 0.5, high),
            (frame_end, low),
        ):
            obj.location = Vector((0.0, 0.0, z_value))
            obj.keyframe_insert(data_path="location", frame=frame)
        add_cycles_modifier(obj.animation_data.action if obj.animation_data else None)

    return obj


def compute_layout(center: Vector, city_radius: float, ground_z: float, settings) -> dict:
    angle = math.radians((settings.seed * 41) % 360)
    direction = Vector((math.cos(angle), math.sin(angle)))
    side = Vector((-direction.y, direction.x))

    terrain_radius = city_radius + settings.terrain_margin
    lake_radius_x = settings.lake_radius * 1.12
    lake_radius_y = settings.lake_radius * 0.78
    safe_buffer = max(6.0, min(settings.terrain_margin * 0.22, settings.lake_radius * 0.55))
    lake_distance = city_radius + max(lake_radius_x, lake_radius_y) + safe_buffer
    lake_center = direction * lake_distance + side * (settings.lake_radius * 0.18)
    lake_rotation = angle + math.pi * 0.35

    water_level = 0.08 - settings.lake_depth * 0.38
    terrain_origin = Vector((center.x, center.y, ground_z - 0.25))

    river_start = lake_center + direction * (settings.lake_radius * 0.78)
    river_outer_distance = max(terrain_radius * 0.94, lake_distance + settings.lake_radius * 1.35)
    river_points = [
        river_start,
        river_start + direction * (settings.lake_radius * 0.70) + side * (settings.river_width * 0.75),
        direction * (river_outer_distance * 0.78) + side * (settings.river_width * 1.8),
        direction * river_outer_distance,
    ]
    traffic_outer = max(settings.traffic_loop_radius_x, settings.traffic_loop_radius_y) + settings.road_width * 0.5
    traffic_distance = city_radius + traffic_outer + max(4.0, safe_buffer * 0.72)
    traffic_center = -direction * traffic_distance - side * (settings.terrain_margin * 0.06)
    traffic_rotation = angle + math.pi * 0.08
    crowd_center = lake_center

    return {
        "center": center,
        "terrain_origin": terrain_origin,
        "city_radius": city_radius,
        "terrain_radius": terrain_radius,
        "lake_center": lake_center,
        "lake_rotation": lake_rotation,
        "lake_radius_x": lake_radius_x,
        "lake_radius_y": lake_radius_y,
        "water_level": water_level,
        "direction": direction,
        "side": side,
        "city_safe_radius": city_radius + safe_buffer,
        "river_points": river_points,
        "traffic_center": traffic_center,
        "traffic_rotation": traffic_rotation,
        "crowd_center": crowd_center,
    }

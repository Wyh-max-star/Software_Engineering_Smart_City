"""Water and terrain generation for the standalone ICity ecology extension."""

from __future__ import annotations

import math

import bpy
from mathutils import Vector

try:
    from .ecology_common import (
        add_cycles_modifier,
        add_subdivision_modifier,
        add_wave_modifier,
        clamp,
        compute_ecology_asset_anchors,
        create_follow_path,
        create_mesh_object,
        distance_to_polyline,
        ensure_principled_input,
        evaluate_noise,
        evaluate_turbulence,
        get_or_create_material,
        keyframe_path_motion,
        rotate_2d,
        rotate_2d_inverse,
        set_linear_interpolation,
        smoothstep,
    )
except ImportError:
    from ecology_common import (
        add_cycles_modifier,
        add_subdivision_modifier,
        add_wave_modifier,
        clamp,
        compute_ecology_asset_anchors,
        create_follow_path,
        create_mesh_object,
        distance_to_polyline,
        ensure_principled_input,
        evaluate_noise,
        evaluate_turbulence,
        get_or_create_material,
        keyframe_path_motion,
        rotate_2d,
        rotate_2d_inverse,
        set_linear_interpolation,
        smoothstep,
    )


TERRAIN_OBJECT_NAME = "ICITY_ECO_Terrain"
LAKE_OBJECT_NAME = "ICITY_ECO_Lake"
RIVER_OBJECT_NAME = "ICITY_ECO_River"

TERRAIN_MATERIAL_NAME = "ICITY_ECO_Terrain_Material"
WATER_MATERIAL_NAME = "ICITY_ECO_Water_Material"
BOAT_MATERIAL_NAME = "ICITY_ECO_Boat_Material"
TREE_MATERIAL_NAME = "ICITY_ECO_Tree_Material"
SHRUB_MATERIAL_NAME = "ICITY_ECO_Shrub_Material"
DOCK_MATERIAL_NAME = "ICITY_ECO_Dock_Material"

TREE_MESH_NAME = "ICITY_ECO_TreeCluster_Mesh"
SHRUB_MESH_NAME = "ICITY_ECO_ShrubPatch_Mesh"
DOCK_MESH_NAME = "ICITY_ECO_Dock_Mesh"


def build_terrain_material() -> bpy.types.Material:
    material = get_or_create_material(TERRAIN_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (380, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (160, 0)
    ensure_principled_input(bsdf, ("Roughness",), 0.92)

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-640, 0)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-440, 0)
    mapping.inputs["Scale"].default_value = (0.045, 0.045, 0.045)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-240, 0)
    noise.inputs["Scale"].default_value = 6.5
    noise.inputs["Detail"].default_value = 9.0
    noise.inputs["Roughness"].default_value = 0.65

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-40, 0)
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = (0.11, 0.25, 0.08, 1.0)
    ramp.color_ramp.elements[1].position = 0.68
    ramp.color_ramp.elements[1].color = (0.36, 0.29, 0.18, 1.0)
    ramp.color_ramp.elements.new(0.9).color = (0.58, 0.54, 0.46, 1.0)

    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_water_material() -> bpy.types.Material:
    material = get_or_create_material(WATER_MATERIAL_NAME)
    material.blend_method = "BLEND"
    material.shadow_method = "NONE"

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (360, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 0)
    bsdf.inputs["Base Color"].default_value = (0.09, 0.35, 0.54, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.08)
    ensure_principled_input(bsdf, ("IOR",), 1.333)
    ensure_principled_input(bsdf, ("Transmission Weight", "Transmission"), 0.72)

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-620, -40)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-420, -40)
    mapping.inputs["Scale"].default_value = (9.0, 9.0, 9.0)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-220, -40)
    noise.inputs["Scale"].default_value = 14.0
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.55

    bump = nodes.new("ShaderNodeBump")
    bump.location = (-30, -120)
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.2

    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_boat_material() -> bpy.types.Material:
    material = get_or_create_material(BOAT_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.72, 0.22, 0.17, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.42)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_tree_material() -> bpy.types.Material:
    material = get_or_create_material(TREE_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.14, 0.32, 0.13, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.86)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_shrub_material() -> bpy.types.Material:
    material = get_or_create_material(SHRUB_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.26, 0.44, 0.16, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.92)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_dock_material() -> bpy.types.Material:
    material = get_or_create_material(DOCK_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.45, 0.34, 0.21, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.88)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def append_box(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
    min_corner: tuple[float, float, float],
    max_corner: tuple[float, float, float],
) -> None:
    base_index = len(vertices)
    x0, y0, z0 = min_corner
    x1, y1, z1 = max_corner
    vertices.extend(
        [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
    )
    faces.extend(
        [
            (base_index + 0, base_index + 1, base_index + 2, base_index + 3),
            (base_index + 4, base_index + 5, base_index + 6, base_index + 7),
            (base_index + 0, base_index + 1, base_index + 5, base_index + 4),
            (base_index + 1, base_index + 2, base_index + 6, base_index + 5),
            (base_index + 2, base_index + 3, base_index + 7, base_index + 6),
            (base_index + 3, base_index + 0, base_index + 4, base_index + 7),
        ]
    )


def build_tree_cluster_mesh() -> bpy.types.Mesh:
    existing = bpy.data.meshes.get(TREE_MESH_NAME)
    if existing is not None and existing.users == 0:
        bpy.data.meshes.remove(existing)

    mesh = bpy.data.meshes.new(TREE_MESH_NAME)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for x_offset, canopy_scale, height_scale in ((0.0, 1.0, 1.0), (-0.95, 0.72, 0.82), (0.95, 0.78, 0.88)):
        append_box(vertices, faces, (x_offset - 0.10, -0.10, 0.0), (x_offset + 0.10, 0.10, 1.2 * height_scale))
        append_box(
            vertices,
            faces,
            (x_offset - 0.52 * canopy_scale, -0.46 * canopy_scale, 1.0 * height_scale),
            (x_offset + 0.52 * canopy_scale, 0.46 * canopy_scale, 1.9 * height_scale),
        )
        append_box(
            vertices,
            faces,
            (x_offset - 0.34 * canopy_scale, -0.30 * canopy_scale, 1.8 * height_scale),
            (x_offset + 0.34 * canopy_scale, 0.30 * canopy_scale, 2.28 * height_scale),
        )

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(build_tree_material())
    return mesh


def build_shrub_patch_mesh() -> bpy.types.Mesh:
    existing = bpy.data.meshes.get(SHRUB_MESH_NAME)
    if existing is not None and existing.users == 0:
        bpy.data.meshes.remove(existing)

    mesh = bpy.data.meshes.new(SHRUB_MESH_NAME)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for x_offset, y_offset, scale in ((0.0, 0.0, 1.0), (-0.44, 0.16, 0.7), (0.42, -0.12, 0.78)):
        append_box(
            vertices,
            faces,
            (x_offset - 0.42 * scale, y_offset - 0.32 * scale, 0.0),
            (x_offset + 0.42 * scale, y_offset + 0.32 * scale, 0.62 * scale),
        )
        append_box(
            vertices,
            faces,
            (x_offset - 0.26 * scale, y_offset - 0.22 * scale, 0.62 * scale),
            (x_offset + 0.26 * scale, y_offset + 0.22 * scale, 0.92 * scale),
        )

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(build_shrub_material())
    return mesh


def build_dock_mesh() -> bpy.types.Mesh:
    existing = bpy.data.meshes.get(DOCK_MESH_NAME)
    if existing is not None and existing.users == 0:
        bpy.data.meshes.remove(existing)

    mesh = bpy.data.meshes.new(DOCK_MESH_NAME)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    append_box(vertices, faces, (-1.6, -0.72, 0.0), (1.6, 0.72, 0.16))
    append_box(vertices, faces, (-1.56, -0.72, -0.68), (-1.34, -0.50, 0.0))
    append_box(vertices, faces, (-1.56, 0.50, -0.68), (-1.34, 0.72, 0.0))
    append_box(vertices, faces, (1.34, -0.72, -0.68), (1.56, -0.50, 0.0))
    append_box(vertices, faces, (1.34, 0.50, -0.68), (1.56, 0.72, 0.0))
    append_box(vertices, faces, (-0.92, -0.08, 0.16), (0.92, 0.08, 0.34))

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(build_dock_material())
    return mesh


def create_asset_instance(
    name: str,
    mesh: bpy.types.Mesh,
    collection: bpy.types.Collection,
    location: Vector,
    rotation_z: float,
    scale: float,
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rotation_z)
    obj.scale = (scale, scale, scale)
    collection.objects.link(obj)
    return obj


def elliptical_distance(local_point: Vector, layout: dict) -> float:
    delta = local_point - layout["lake_center"]
    rotated = rotate_2d_inverse(delta, layout["lake_rotation"])
    return math.sqrt(
        (rotated.x / layout["lake_radius_x"]) ** 2
        + (rotated.y / layout["lake_radius_y"]) ** 2
    )


def terrain_height(local_point: Vector, layout: dict, settings) -> float:
    distance_from_center = local_point.length
    terrain_radius = layout["terrain_radius"]
    city_radius = layout["city_radius"]
    city_safe_radius = layout.get("city_safe_radius", city_radius)

    if distance_from_center <= city_safe_radius:
        return -0.04

    edge_factor = smoothstep(city_safe_radius, terrain_radius, distance_from_center)
    ridge_noise = evaluate_noise(local_point, settings.seed, 0.018, octaves=5)
    ridge_noise = 0.5 + ridge_noise * 0.5
    detail_noise = evaluate_turbulence(local_point, settings.seed + 9, 0.05, octaves=4)

    plateau_height = 0.08
    height = plateau_height
    height += settings.mountain_height * (edge_factor ** 1.45) * (0.52 + ridge_noise * 0.48)
    height += settings.noise_strength * edge_factor * (detail_noise - 0.18)

    lake_distance = elliptical_distance(local_point, layout)
    lake_mask = 1.0 - smoothstep(0.86, 1.05, lake_distance)
    shore_mask = 1.0 - smoothstep(1.0, 1.35, lake_distance)
    if lake_mask > 0.0:
        lake_floor = layout["water_level"] - settings.lake_depth * (0.42 + 0.58 * lake_mask)
        height = min(height, lake_floor)
    else:
        height -= shore_mask * settings.lake_depth * 0.22

    river_distance = distance_to_polyline(local_point, layout["river_points"])
    river_mask = 1.0 - smoothstep(settings.river_width * 0.55, settings.river_width * 1.7, river_distance)
    if river_mask > 0.0:
        river_floor = layout["water_level"] - settings.river_depth * (0.35 + 0.65 * river_mask)
        height = min(height, river_floor)
        height -= river_mask * 0.08

    return height


def create_terrain(layout: dict, settings, collection: bpy.types.Collection) -> bpy.types.Object:
    resolution = settings.terrain_resolution
    terrain_radius = layout["terrain_radius"]
    step = (terrain_radius * 2.0) / resolution

    vertices: list[tuple[float, float, float]] = []
    for y_index in range(resolution + 1):
        y = -terrain_radius + y_index * step
        for x_index in range(resolution + 1):
            x = -terrain_radius + x_index * step
            point = Vector((x, y))
            vertices.append((x, y, terrain_height(point, layout, settings)))

    faces: list[tuple[int, int, int, int]] = []
    row_size = resolution + 1
    for y_index in range(resolution):
        for x_index in range(resolution):
            index = y_index * row_size + x_index
            faces.append((index, index + 1, index + row_size + 1, index + row_size))

    terrain_obj = create_mesh_object(
        TERRAIN_OBJECT_NAME,
        vertices,
        faces,
        collection,
        layout["terrain_origin"],
        build_terrain_material(),
    )
    add_subdivision_modifier(terrain_obj, levels=1, render_levels=2)
    return terrain_obj


def create_lake(layout: dict, settings, collection: bpy.types.Collection) -> bpy.types.Object:
    segments = 72
    vertices = [(layout["lake_center"].x, layout["lake_center"].y, layout["water_level"])]
    faces = []
    for index in range(segments):
        angle = (index / segments) * math.tau
        radius_bias = 1.0 + evaluate_noise(
            Vector((math.cos(angle), math.sin(angle))), settings.seed + 23, 1.9, octaves=2
        ) * 0.08
        ellipse_point = Vector(
            (
                math.cos(angle) * layout["lake_radius_x"] * radius_bias,
                math.sin(angle) * layout["lake_radius_y"] * radius_bias,
            )
        )
        point = layout["lake_center"] + rotate_2d(ellipse_point, layout["lake_rotation"])
        vertices.append((point.x, point.y, layout["water_level"]))

    for index in range(1, segments + 1):
        next_index = 1 if index == segments else index + 1
        faces.append((0, index, next_index))

    lake_obj = create_mesh_object(
        LAKE_OBJECT_NAME,
        vertices,
        faces,
        collection,
        layout["terrain_origin"],
        build_water_material(),
    )
    add_subdivision_modifier(lake_obj, levels=2, render_levels=2)
    add_wave_modifier(lake_obj, settings.seed, height=0.06, width=max(settings.lake_radius * 0.26, 1.0))
    return lake_obj


def create_river(layout: dict, settings, collection: bpy.types.Collection) -> bpy.types.Object:
    vertices = []
    faces = []
    points = layout["river_points"]
    for index, point in enumerate(points):
        if index == 0:
            tangent = points[index + 1] - point
        elif index == len(points) - 1:
            tangent = point - points[index - 1]
        else:
            tangent = points[index + 1] - points[index - 1]
        tangent = tangent.normalized()
        normal = Vector((-tangent.y, tangent.x))
        taper = 1.0 - (index / max(1, len(points) - 1)) * 0.22
        half_width = settings.river_width * 0.5 * taper
        left = (point.x + normal.x * half_width, point.y + normal.y * half_width, layout["water_level"] - 0.04)
        right = (point.x - normal.x * half_width, point.y - normal.y * half_width, layout["water_level"] - 0.04)
        vertices.extend((left, right))
        if index > 0:
            base = index * 2
            faces.append((base - 2, base, base + 1, base - 1))

    river_obj = create_mesh_object(
        RIVER_OBJECT_NAME,
        vertices,
        faces,
        collection,
        layout["terrain_origin"],
        build_water_material(),
    )
    add_subdivision_modifier(river_obj, levels=2, render_levels=2)
    add_wave_modifier(river_obj, settings.seed + 5, height=0.03, width=max(settings.river_width * 1.4, 0.8))
    return river_obj


def build_boat_mesh(scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    vertices = [
        (-1.20, -0.34, 0.00),
        (-1.20, 0.34, 0.00),
        (0.34, -0.48, 0.00),
        (0.34, 0.48, 0.00),
        (1.18, 0.00, 0.06),
        (-0.98, -0.24, 0.48),
        (-0.98, 0.24, 0.48),
        (0.24, -0.32, 0.56),
        (0.24, 0.32, 0.56),
        (0.86, 0.00, 0.44),
    ]
    faces = [
        (0, 1, 6, 5),
        (0, 2, 7, 5),
        (2, 4, 9, 7),
        (4, 3, 8, 9),
        (3, 1, 6, 8),
        (5, 7, 8, 6),
        (7, 9, 8),
        (0, 1, 3, 2),
        (2, 3, 4),
    ]
    scaled_vertices = [(x * scale, y * scale, z * scale) for x, y, z in vertices]
    return scaled_vertices, faces


def create_boat_animation(
    boat_index: int,
    layout: dict,
    settings,
    collection: bpy.types.Collection,
) -> None:
    scale = clamp(min(layout["lake_radius_x"], layout["lake_radius_y"]) * 0.09, 0.6, 1.3)
    route_scale = 0.56 - boat_index * 0.05
    route_scale = max(route_scale, 0.34)
    phase = (boat_index / max(1, settings.boat_count)) * math.tau
    route_points = []
    route_height = layout["water_level"] + 0.16 * scale
    for step in range(8):
        angle = phase + (step / 8.0) * math.tau
        ellipse = Vector(
            (
                math.cos(angle) * layout["lake_radius_x"] * route_scale,
                math.sin(angle) * layout["lake_radius_y"] * route_scale * 0.86,
            )
        )
        point = layout["lake_center"] + rotate_2d(ellipse, layout["lake_rotation"])
        route_points.append(Vector((point.x, point.y, route_height + math.sin(angle * 2.0) * 0.03 * scale)))

    path_obj = create_follow_path(
        name=f"ICITY_ECO_BoatPath_{boat_index + 1}",
        path_points=route_points,
        collection=collection,
        location=layout["terrain_origin"],
        frame_count=settings.animation_end - settings.animation_start,
    )

    carrier = bpy.data.objects.new(f"ICITY_ECO_BoatCarrier_{boat_index + 1}", None)
    carrier.empty_display_type = "PLAIN_AXES"
    carrier.empty_display_size = 0.15
    carrier.hide_render = True
    carrier.hide_select = True
    collection.objects.link(carrier)

    keyframe_path_motion(
        carrier,
        route_points,
        path_obj.location,
        settings.animation_start,
        settings.animation_end,
        0.0,
        sample_count=max(12, len(route_points)),
    )

    boat_vertices, boat_faces = build_boat_mesh(scale)
    boat_obj = create_mesh_object(
        f"ICITY_ECO_Boat_{boat_index + 1}",
        boat_vertices,
        boat_faces,
        collection,
        Vector((0.0, 0.0, 0.0)),
        build_boat_material(),
    )
    boat_obj.parent = carrier
    boat_obj.location = Vector((0.0, 0.0, 0.0))
    boat_obj.rotation_mode = "XYZ"

    for frame, rotation_x, rotation_y in (
        (settings.animation_start, -0.05, 0.02),
        (settings.animation_start + (settings.animation_end - settings.animation_start) * 0.5, 0.05, -0.025),
        (settings.animation_end, -0.05, 0.02),
    ):
        boat_obj.rotation_euler = (rotation_x, rotation_y, 0.0)
        boat_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    add_cycles_modifier(boat_obj.animation_data.action if boat_obj.animation_data else None)


def create_boats(layout: dict, settings, collection: bpy.types.Collection) -> None:
    for boat_index in range(settings.boat_count):
        create_boat_animation(boat_index, layout, settings, collection)


def create_ecology_assets(layout: dict, settings, collection: bpy.types.Collection) -> None:
    anchors = compute_ecology_asset_anchors(layout, settings)
    dock_mesh = build_dock_mesh()
    tree_mesh = build_tree_cluster_mesh()
    shrub_mesh = build_shrub_patch_mesh()

    dock_center = anchors["dock_center"]
    dock_location = layout["terrain_origin"] + Vector((dock_center.x, dock_center.y, layout["water_level"] + 0.05))
    create_asset_instance(
        "ICITY_ECO_Dock_01",
        dock_mesh,
        collection,
        dock_location,
        anchors["dock_rotation"],
        1.0,
    )

    for index, point in enumerate(anchors["tree_points"], start=1):
        ground_height = terrain_height(Vector((point.x, point.y)), layout, settings)
        create_asset_instance(
            f"ICITY_ECO_TreeCluster_{index:02d}",
            tree_mesh,
            collection,
            layout["terrain_origin"] + Vector((point.x, point.y, ground_height + 0.04)),
            math.radians((settings.seed * 19 + index * 37) % 360),
            0.92 + (index % 3) * 0.09,
        )

    for index, point in enumerate(anchors["shrub_points"], start=1):
        ground_height = terrain_height(Vector((point.x, point.y)), layout, settings)
        create_asset_instance(
            f"ICITY_ECO_ShrubPatch_{index:02d}",
            shrub_mesh,
            collection,
            layout["terrain_origin"] + Vector((point.x, point.y, ground_height + 0.02)),
            math.radians((settings.seed * 11 + index * 29) % 360),
            0.88 + (index % 2) * 0.10,
        )


def generate_water_system(
    layout: dict,
    settings,
    terrain_collection: bpy.types.Collection,
    water_collection: bpy.types.Collection,
    boat_collection: bpy.types.Collection,
    asset_collection: bpy.types.Collection,
) -> None:
    create_terrain(layout, settings, terrain_collection)
    create_lake(layout, settings, water_collection)
    if settings.generate_river:
        create_river(layout, settings, water_collection)
    create_boats(layout, settings, boat_collection)
    create_ecology_assets(layout, settings, asset_collection)

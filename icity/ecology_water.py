"""Plot-based terrain, lake, river, and boat generation for the ICity ecology extension."""

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
        create_mesh_object,
        distance_to_polyline,
        ensure_principled_input,
        evaluate_noise,
        evaluate_turbulence,
        get_or_create_material,
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
        create_mesh_object,
        distance_to_polyline,
        ensure_principled_input,
        evaluate_noise,
        evaluate_turbulence,
        get_or_create_material,
        rotate_2d,
        rotate_2d_inverse,
        set_linear_interpolation,
        smoothstep,
    )


TERRAIN_OBJECT_NAME = "ICITY_ECO_Terrain"
LAKE_OBJECT_NAME = "ICITY_ECO_Lake"
RIVER_OBJECT_NAME = "ICITY_ECO_River"
PLOT_GUIDE_OBJECT_NAME = "ICITY_ECO_PlotGuide"
PLOT_COLLECTION_PREFIX = "ICITY_ECO_Plot_"

TERRAIN_MATERIAL_NAME = "ICITY_ECO_Terrain_Material"
WATER_MATERIAL_NAME = "ICITY_ECO_Water_Material"
BOAT_MATERIAL_NAME = "ICITY_ECO_Boat_Material"
DEBUG_MARKER_MATERIAL_NAME = "ICITY_ECO_Debug_Marker_Material"


def plot_collection_name(plot_index: int) -> str:
    return f"{PLOT_COLLECTION_PREFIX}{plot_index:03d}"


def next_plot_index(plots_collection: bpy.types.Collection) -> int:
    indices = []
    for child in plots_collection.children:
        if not child.name.startswith(PLOT_COLLECTION_PREFIX):
            continue
        suffix = child.name[len(PLOT_COLLECTION_PREFIX) :]
        digits = "".join(character for character in suffix if character.isdigit())
        if digits:
            indices.append(int(digits))
    return max(indices, default=0) + 1


def compute_plot_location(center: Vector, city_radius: float, settings, plot_index: int) -> Vector:
    angle = math.radians((settings.seed * 37 + (plot_index - 1) * 73) % 360)
    radial_offset = city_radius + settings.plot_offset + max(settings.plot_width, settings.plot_depth) * 0.5
    return Vector(
        (
            center.x + math.cos(angle) * radial_offset,
            center.y + math.sin(angle) * radial_offset,
            0.0,
        )
    )


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


def build_water_material(debug_visuals: bool = False) -> bpy.types.Material:
    material = get_or_create_material(WATER_MATERIAL_NAME)
    if hasattr(material, "blend_method"):
        material.blend_method = "OPAQUE"
    if hasattr(material, "shadow_method"):
        material.shadow_method = "OPAQUE"
    if hasattr(material, "diffuse_color"):
        material.diffuse_color = (0.06, 0.32, 0.78, 1.0)

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (360, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 0)
    bsdf.inputs["Base Color"].default_value = (0.06, 0.32, 0.78, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.18)
    ensure_principled_input(bsdf, ("IOR",), 1.333)
    ensure_principled_input(bsdf, ("Transmission Weight", "Transmission"), 0.0)

    if debug_visuals:
        emission = nodes.new("ShaderNodeEmission")
        emission.location = (120, 180)
        emission.inputs["Color"].default_value = (0.05, 0.52, 1.0, 1.0)
        emission.inputs["Strength"].default_value = 3.2

        add_shader = nodes.new("ShaderNodeAddShader")
        add_shader.location = (260, 60)

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
    if debug_visuals:
        links.new(bsdf.outputs["BSDF"], add_shader.inputs[0])
        links.new(emission.outputs["Emission"], add_shader.inputs[1])
        links.new(add_shader.outputs["Shader"], output.inputs["Surface"])
    else:
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_boat_material(
    material_name: str,
    base_color: tuple[float, float, float, float],
    debug_visuals: bool = False,
) -> bpy.types.Material:
    material = get_or_create_material(material_name)
    if hasattr(material, "diffuse_color"):
        material.diffuse_color = base_color
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = base_color
    ensure_principled_input(bsdf, ("Roughness",), 0.34)

    if debug_visuals:
        emission = nodes.new("ShaderNodeEmission")
        emission.location = (80, 180)
        emission.inputs["Color"].default_value = base_color
        emission.inputs["Strength"].default_value = 4.0

        add_shader = nodes.new("ShaderNodeAddShader")
        add_shader.location = (220, 60)
        links.new(bsdf.outputs["BSDF"], add_shader.inputs[0])
        links.new(emission.outputs["Emission"], add_shader.inputs[1])
        links.new(add_shader.outputs["Shader"], output.inputs["Surface"])
    else:
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_debug_marker_material() -> bpy.types.Material:
    material = get_or_create_material(DEBUG_MARKER_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (220, 0)
    emission = nodes.new("ShaderNodeEmission")
    emission.location = (0, 0)
    emission.inputs["Color"].default_value = (1.0, 0.1, 0.8, 1.0)
    emission.inputs["Strength"].default_value = 6.0
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def build_debug_marker_mesh(scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    marker_scale = max(scale * 0.35, 0.6)
    vertices = [
        (0.0, 0.0, 1.8 * marker_scale),
        (-0.5 * marker_scale, -0.5 * marker_scale, 0.0),
        (0.5 * marker_scale, -0.5 * marker_scale, 0.0),
        (0.5 * marker_scale, 0.5 * marker_scale, 0.0),
        (-0.5 * marker_scale, 0.5 * marker_scale, 0.0),
        (0.0, 0.0, -0.8 * marker_scale),
    ]
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (0, 3, 4),
        (0, 4, 1),
        (5, 2, 1),
        (5, 3, 2),
        (5, 4, 3),
        (5, 1, 4),
    ]
    return vertices, faces


def try_build_material(builder, *args):
    try:
        return builder(*args)
    except Exception as exc:  # pragma: no cover
        print(f"[ICity Ecology] material fallback: {exc}")
        return None


def try_add_modifier(callback, *args, **kwargs) -> None:
    try:
        callback(*args, **kwargs)
    except Exception as exc:  # pragma: no cover
        print(f"[ICity Ecology] modifier fallback: {exc}")


def pseudo_random(seed: int, index: int, channel: int = 0) -> float:
    value = math.sin(seed * 12.9898 + index * 78.233 + channel * 37.719) * 43758.5453
    return value - math.floor(value)


def build_plot_outline_vertices(settings, segment_count: int = 32) -> list[tuple[float, float, float]]:
    half_x = settings.plot_width * 0.5
    half_y = settings.plot_depth * 0.5
    shape = settings.plot_shape

    if shape == "RECTANGLE":
        return [
            (-half_x, -half_y, 0.0),
            (half_x, -half_y, 0.0),
            (half_x, half_y, 0.0),
            (-half_x, half_y, 0.0),
        ]

    if shape == "ELLIPSE":
        vertices = []
        for index in range(segment_count):
            angle = math.tau * index / segment_count
            vertices.append((math.cos(angle) * half_x, math.sin(angle) * half_y, 0.0))
        return vertices

    radius = min(half_x, half_y) * 0.30
    inner_x = max(half_x - radius, 0.01)
    inner_y = max(half_y - radius, 0.01)
    arc_segments = max(4, segment_count // 4)
    corner_centers = [
        (inner_x, inner_y, 0.0),
        (-inner_x, inner_y, math.pi * 0.5),
        (-inner_x, -inner_y, math.pi),
        (inner_x, -inner_y, math.pi * 1.5),
    ]
    vertices = []
    for center_x, center_y, start_angle in corner_centers:
        for step in range(arc_segments):
            angle = start_angle + (step / max(1, arc_segments - 1)) * (math.pi * 0.5)
            vertices.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius, 0.0))
    return vertices


def point_inside_plot_shape(local_point: Vector, layout: dict, padding: float = 0.0) -> bool:
    half_x = max(layout["half_x"] - padding, 0.01)
    half_y = max(layout["half_y"] - padding, 0.01)
    shape = layout["plot_shape"]

    if shape == "RECTANGLE":
        return abs(local_point.x) <= half_x and abs(local_point.y) <= half_y

    if shape == "ELLIPSE":
        return (local_point.x / half_x) ** 2 + (local_point.y / half_y) ** 2 <= 1.0

    corner_radius = min(half_x, half_y) * 0.30
    inner_x = max(half_x - corner_radius, 0.0)
    inner_y = max(half_y - corner_radius, 0.0)
    abs_x = abs(local_point.x)
    abs_y = abs(local_point.y)
    if abs_x <= inner_x or abs_y <= inner_y:
        return abs_x <= half_x and abs_y <= half_y
    dx = abs_x - inner_x
    dy = abs_y - inner_y
    return dx * dx + dy * dy <= corner_radius * corner_radius


def plot_shape_distance(local_point: Vector, layout: dict) -> float:
    half_x = max(layout["half_x"], 0.001)
    half_y = max(layout["half_y"], 0.001)
    shape = layout["plot_shape"]
    abs_x = abs(local_point.x)
    abs_y = abs(local_point.y)

    if shape == "RECTANGLE":
        return max(abs_x / half_x, abs_y / half_y)

    if shape == "ELLIPSE":
        return math.sqrt((local_point.x / half_x) ** 2 + (local_point.y / half_y) ** 2)

    return max(abs_x / half_x, abs_y / half_y)


def edge_falloff(local_point: Vector, layout: dict) -> float:
    distance = plot_shape_distance(local_point, layout)
    return clamp(1.0 - smoothstep(0.58, 1.0, distance), 0.0, 1.0)


def set_parent_keep_transform(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world_matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()
    obj.matrix_world = world_matrix


def create_plot_guide(plot_index: int, base_location: Vector, settings, collection: bpy.types.Collection) -> bpy.types.Object:
    vertices = build_plot_outline_vertices(settings)
    faces = [tuple(range(len(vertices)))]
    guide_obj = create_mesh_object(
        f"{PLOT_GUIDE_OBJECT_NAME}_{plot_index:03d}",
        vertices,
        faces,
        collection,
        base_location,
        None,
    )
    guide_obj.display_type = "WIRE"
    guide_obj.show_wire = True
    guide_obj.hide_render = True
    guide_obj["icity_ecology_plot"] = True
    guide_obj["icity_plot_type"] = settings.ecology_plot_mode
    return guide_obj


def build_plot_layout(plot_index: int, base_location: Vector, settings) -> dict:
    plot_seed = settings.seed + plot_index * 97
    plot_kind = settings.ecology_plot_mode
    half_x = settings.plot_width * 0.5
    half_y = settings.plot_depth * 0.5
    short_side = min(half_x, half_y)

    direction_angle = math.radians((plot_seed * 31) % 360)
    direction = Vector((math.cos(direction_angle), math.sin(direction_angle)))
    side = Vector((-direction.y, direction.x))

    lake_radius_x = min(settings.lake_radius * 1.18, half_x * 0.38)
    lake_radius_y = min(settings.lake_radius * 0.92, half_y * 0.34)
    lake_center = direction * (short_side * 0.08) + side * (short_side * 0.03)
    water_level = 0.03
    mountain_band = short_side * (0.34 if plot_kind == "LAKE_RING" else 0.18)

    river_start = lake_center + direction * (lake_radius_x * 0.88)
    river_points = [
        river_start,
        river_start + direction * (short_side * 0.24) + side * (short_side * 0.05),
        direction * (short_side * 0.72) + side * (short_side * 0.10),
        direction * (short_side * 0.94),
    ]

    layout = {
        "plot_index": plot_index,
        "plot_kind": plot_kind,
        "plot_shape": settings.plot_shape,
        "terrain_origin": base_location,
        "half_x": half_x,
        "half_y": half_y,
        "mountain_band": mountain_band,
        "direction": direction,
        "side": side,
        "lake_center": lake_center,
        "lake_rotation": direction_angle + math.pi * 0.27,
        "lake_radius_x": lake_radius_x,
        "lake_radius_y": lake_radius_y,
        "water_level": water_level,
        "river_points": river_points,
        "plot_seed": plot_seed,
        "has_lake": plot_kind == "LAKE_RING",
    }
    layout["peak_specs"] = build_peak_specs(layout, settings)
    return layout


def build_peak_specs(layout: dict, settings) -> list[dict]:
    peak_specs = []
    short_side = min(layout["half_x"], layout["half_y"])
    peak_count = max(2, int(settings.mountain_peak_count))
    for peak_index in range(peak_count):
        angle_noise = pseudo_random(layout["plot_seed"], peak_index, 0)
        radius_noise = pseudo_random(layout["plot_seed"], peak_index, 1)
        width_noise = pseudo_random(layout["plot_seed"], peak_index, 2)
        depth_noise = pseudo_random(layout["plot_seed"], peak_index, 3)
        rotation_noise = pseudo_random(layout["plot_seed"], peak_index, 4)
        amplitude_noise = pseudo_random(layout["plot_seed"], peak_index, 5)

        angle = (peak_index / peak_count) * math.tau + (angle_noise - 0.5) * 1.15
        if layout["plot_kind"] == "LAKE_RING":
            orbit_radius = short_side * (0.44 + radius_noise * 0.24)
            center = (
                layout["lake_center"]
                + layout["direction"] * (math.cos(angle) * orbit_radius)
                + layout["side"] * (math.sin(angle) * orbit_radius * 0.82)
            )
            radius_x = short_side * (0.26 + width_noise * 0.18)
            radius_y = short_side * (0.18 + depth_noise * 0.14)
        else:
            orbit_radius = short_side * (0.16 + radius_noise * 0.34)
            center = (
                layout["direction"] * (math.cos(angle) * orbit_radius)
                + layout["side"] * (math.sin(angle) * orbit_radius * 0.90)
            )
            radius_x = short_side * (0.30 + width_noise * 0.20)
            radius_y = short_side * (0.20 + depth_noise * 0.15)

        peak_specs.append(
            {
                "center": center,
                "radius_x": radius_x,
                "radius_y": radius_y,
                "rotation": angle + (rotation_noise - 0.5) * 0.9,
                "amplitude": 0.26 + amplitude_noise * 0.30,
            }
        )
    return peak_specs


def elliptical_distance(local_point: Vector, layout: dict) -> float:
    delta = local_point - layout["lake_center"]
    rotated = rotate_2d_inverse(delta, layout["lake_rotation"])
    return math.sqrt(
        (rotated.x / max(layout["lake_radius_x"], 0.001)) ** 2
        + (rotated.y / max(layout["lake_radius_y"], 0.001)) ** 2
    )


def elliptical_distance_to_center(
    local_point: Vector,
    center: Vector,
    radius_x: float,
    radius_y: float,
    rotation: float,
) -> float:
    delta = local_point - center
    rotated = rotate_2d_inverse(delta, rotation)
    return math.sqrt(
        (rotated.x / max(radius_x, 0.001)) ** 2
        + (rotated.y / max(radius_y, 0.001)) ** 2
    )


def plot_distance(local_point: Vector, layout: dict) -> float:
    return math.sqrt(
        (local_point.x / max(layout["half_x"] * 0.92, 0.001)) ** 2
        + (local_point.y / max(layout["half_y"] * 0.92, 0.001)) ** 2
    )


def band_mask(distance: float, inner_start: float, inner_end: float, outer_start: float, outer_end: float) -> float:
    return smoothstep(inner_start, inner_end, distance) * (1.0 - smoothstep(outer_start, outer_end, distance))


def hill_mask(
    local_point: Vector,
    center: Vector,
    radius_x: float,
    radius_y: float,
    rotation: float,
) -> float:
    distance = elliptical_distance_to_center(local_point, center, radius_x, radius_y, rotation)
    return 1.0 - smoothstep(0.0, 1.0, distance)


def peak_influence(local_point: Vector, layout: dict) -> float:
    influence = 0.0
    for peak in layout["peak_specs"]:
        influence += peak["amplitude"] * hill_mask(
            local_point,
            peak["center"],
            peak["radius_x"],
            peak["radius_y"],
            peak["rotation"],
        )
    return influence


def terrain_height(local_point: Vector, layout: dict, settings) -> float:
    ridge_noise = evaluate_noise(local_point, layout["plot_seed"], 0.028, octaves=5)
    ridge_noise = 0.5 + ridge_noise * 0.5
    detail_noise = evaluate_turbulence(local_point, layout["plot_seed"] + 11, 0.06, octaves=4)
    macro_noise = 0.5 + evaluate_noise(local_point, layout["plot_seed"] + 23, 0.012, octaves=3) * 0.5
    macro_turbulence = evaluate_turbulence(local_point, layout["plot_seed"] + 37, 0.024, octaves=3)
    edge_softening = edge_falloff(local_point, layout)
    base_noise = settings.noise_strength * 0.20 * (detail_noise - 0.16)
    secondary_noise = settings.noise_strength * 0.14 * (ridge_noise - 0.5)
    mountain_noise = settings.mountain_height * 0.06 * (ridge_noise - 0.15)
    peaks = peak_influence(local_point, layout)

    # Ridged noise: folding the noise around zero with abs() creates sharp creases
    # instead of rounded blobs, which gives the mountains crisp ridge lines and
    # rocky edges. Its strength is driven by the Terrain Noise slider so cranking
    # that value up makes the relief progressively more rugged/angular.
    ridge_raw = evaluate_noise(local_point, layout["plot_seed"] + 53, 0.05, octaves=6)
    ridged = 1.0 - abs(ridge_raw)
    ridged = ridged * ridged
    ridge_relief = settings.noise_strength * ridged

    if layout["plot_kind"] == "MOUNTAIN_ONLY":
        broad_land = settings.mountain_height * (0.24 + macro_noise * 0.34 + macro_turbulence * 0.18)
        height = 0.18 + base_noise + secondary_noise + mountain_noise + broad_land
        height += settings.mountain_height * peaks * 0.88
        height += settings.noise_strength * (0.28 + peaks * 0.18) * (detail_noise - 0.08)
        height += ridge_relief * (0.45 + peaks * 0.65)
        return height * edge_softening

    broad_land = settings.mountain_height * (0.18 + macro_noise * 0.26 + macro_turbulence * 0.14)
    height = 0.14 + base_noise + secondary_noise + mountain_noise
    lake_distance = elliptical_distance(local_point, layout)
    land_mask = smoothstep(0.82, 1.02, lake_distance)
    shore_mask = band_mask(lake_distance, 0.88, 1.02, 1.26, 1.64)
    far_land = smoothstep(1.00, 1.90, lake_distance)

    height += land_mask * broad_land
    height += land_mask * settings.mountain_height * (peaks * 0.74 + far_land * 0.18)
    height += land_mask * settings.noise_strength * (0.26 + macro_turbulence * 0.06) * (detail_noise - 0.08)
    height += land_mask * ridge_relief * (0.35 + peaks * 0.55)
    height += shore_mask * (0.24 + settings.noise_strength * 0.04)
    height *= edge_softening

    lake_mask = 1.0 - smoothstep(0.72, 1.02, lake_distance)
    lake_shallow_mask = 1.0 - smoothstep(0.92, 1.48, lake_distance)
    if lake_mask > 0.0:
        lake_floor = layout["water_level"] - settings.lake_depth * (0.06 + 0.16 * lake_mask)
        height = min(height, lake_floor)
    else:
        height -= lake_shallow_mask * settings.lake_depth * 0.10

    return height


def create_terrain(layout: dict, settings, collection: bpy.types.Collection) -> bpy.types.Object:
    resolution_x = settings.terrain_resolution
    resolution_y = max(8, round(settings.terrain_resolution * (layout["half_y"] / max(layout["half_x"], 1.0))))
    step_x = (layout["half_x"] * 2.0) / resolution_x
    step_y = (layout["half_y"] * 2.0) / resolution_y

    vertices: list[tuple[float, float, float]] = []
    for y_index in range(resolution_y + 1):
        y = -layout["half_y"] + y_index * step_y
        for x_index in range(resolution_x + 1):
            x = -layout["half_x"] + x_index * step_x
            point = Vector((x, y))
            vertices.append((x, y, terrain_height(point, layout, settings)))

    faces: list[tuple[int, int, int, int]] = []
    row_size = resolution_x + 1
    for y_index in range(resolution_y):
        y = -layout["half_y"] + y_index * step_y
        for x_index in range(resolution_x):
            x = -layout["half_x"] + x_index * step_x
            corners = [
                Vector((x, y)),
                Vector((x + step_x, y)),
                Vector((x + step_x, y + step_y)),
                Vector((x, y + step_y)),
            ]
            if not all(point_inside_plot_shape(corner, layout, padding=0.0) for corner in corners):
                continue
            index = y_index * row_size + x_index
            faces.append((index, index + 1, index + row_size + 1, index + row_size))

    terrain_obj = create_mesh_object(
        f"{TERRAIN_OBJECT_NAME}_{layout['plot_index']:03d}",
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
    debug_visuals = getattr(settings, "debug_water_boats", False)
    surface_level = layout["water_level"] + (0.9 if debug_visuals else 0.0)
    bottom_level = surface_level - (0.22 if debug_visuals else 0.10)
    layout["water_surface_level"] = surface_level
    vertices = [(layout["lake_center"].x, layout["lake_center"].y, surface_level)]
    faces = []
    top_ring: list[tuple[float, float, float]] = []
    for index in range(segments):
        angle = (index / segments) * math.tau
        radius_bias = 1.0 + evaluate_noise(
            Vector((math.cos(angle), math.sin(angle))), layout["plot_seed"] + 23, 1.9, octaves=2
        ) * 0.08
        ellipse_point = Vector(
            (
                math.cos(angle) * layout["lake_radius_x"] * radius_bias,
                math.sin(angle) * layout["lake_radius_y"] * radius_bias,
            )
        )
        point = layout["lake_center"] + rotate_2d(ellipse_point, layout["lake_rotation"])
        top_ring.append((point.x, point.y, surface_level))
        vertices.append((point.x, point.y, surface_level))

    for index in range(1, segments + 1):
        next_index = 1 if index == segments else index + 1
        faces.append((0, index, next_index))

    bottom_center_index = len(vertices)
    vertices.append((layout["lake_center"].x, layout["lake_center"].y, bottom_level))
    bottom_ring_start = len(vertices)
    for x, y, _ in top_ring:
        vertices.append((x, y, bottom_level))

    for index in range(bottom_ring_start, bottom_ring_start + segments):
        next_index = bottom_ring_start if index == bottom_ring_start + segments - 1 else index + 1
        faces.append((bottom_center_index, next_index, index))

    for ring_index in range(segments):
        top_index = 1 + ring_index
        top_next = 1 if ring_index == segments - 1 else top_index + 1
        bottom_index = bottom_ring_start + ring_index
        bottom_next = bottom_ring_start if ring_index == segments - 1 else bottom_index + 1
        faces.append((top_index, top_next, bottom_next, bottom_index))

    water_material = try_build_material(build_water_material, debug_visuals)
    lake_obj = create_mesh_object(
        f"{LAKE_OBJECT_NAME}_{layout['plot_index']:03d}",
        vertices,
        faces,
        collection,
        layout["terrain_origin"],
        water_material,
    )
    lake_obj.color = (0.00, 0.82, 1.0, 1.0) if debug_visuals else (0.06, 0.32, 0.78, 1.0)
    if debug_visuals:
        lake_obj.show_in_front = True
    try_add_modifier(add_subdivision_modifier, lake_obj, levels=2, render_levels=2)
    try_add_modifier(
        add_wave_modifier,
        lake_obj,
        layout["plot_seed"],
        height=0.05,
        width=max(settings.lake_radius * 0.24, 1.0),
    )
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
        f"{RIVER_OBJECT_NAME}_{layout['plot_index']:03d}",
        vertices,
        faces,
        collection,
        layout["terrain_origin"],
        build_water_material(),
    )
    add_subdivision_modifier(river_obj, levels=2, render_levels=2)
    add_wave_modifier(river_obj, layout["plot_seed"] + 5, height=0.03, width=max(settings.river_width * 1.4, 0.8))
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


def compute_boat_route(
    boat_index: int,
    layout: dict,
    settings,
    scale: float,
    sample_count: int,
) -> list[Vector]:
    boat_count = max(1, settings.boat_count)
    plot_seed = layout["plot_seed"] + boat_index * 137

    # Every boat circles the lake the same way at an evenly spaced starting
    # angle, so at any frame the boats stay 360/boat_count degrees apart and
    # never collapse on top of each other. A small per-boat lane offset keeps
    # them from tracing the exact same circle when there are only a couple.
    angular_offset = (boat_index / boat_count) * math.tau
    lane_factor = 0.46 + (0.12 if boat_index % 2 else -0.12)
    wobble_phase = pseudo_random(plot_seed, boat_index, 2) * math.tau
    radial_wobble_limit = 0.02
    base_height = layout.get("water_surface_level", layout["water_level"]) + scale * 0.05

    route_points = []
    for step in range(sample_count):
        angle = angular_offset + (step / sample_count) * math.tau
        radial_wobble = math.sin(angle * 2.0 + wobble_phase) * radial_wobble_limit
        factor = lane_factor + radial_wobble
        ellipse = Vector(
            (
                math.cos(angle) * layout["lake_radius_x"] * factor,
                math.sin(angle) * layout["lake_radius_y"] * factor,
            )
        )
        point = layout["lake_center"] + rotate_2d(ellipse, layout["lake_rotation"])
        bobbing = math.sin(angle * 2.2 + boat_index * 0.9) * scale * 0.03
        route_points.append(Vector((point.x, point.y, base_height + bobbing)))
    return route_points


def compute_boat_rotation(current_point: Vector, next_point: Vector, step_index: int, scale: float) -> tuple[float, float, float]:
    tangent = next_point - current_point
    yaw = math.atan2(tangent.y, tangent.x)
    roll = math.sin((step_index / 12.0) * math.tau) * 0.045
    pitch = math.cos((step_index / 10.0) * math.tau) * 0.025
    return pitch, roll, yaw


def create_boat_animation(
    boat_index: int,
    layout: dict,
    settings,
    collection: bpy.types.Collection,
    terrain_obj: bpy.types.Object,
) -> None:
    debug_visuals = getattr(settings, "debug_water_boats", False)
    boat_count = max(1, settings.boat_count)
    # Boats shrink both with a smaller lake and with a higher boat count so that
    # several of them stay clearly separated instead of piling up into a single
    # blob near the lake centre.
    lake_extent = min(layout["lake_radius_x"], layout["lake_radius_y"])
    crowd_scale = 1.0 / (1.0 + 0.20 * (boat_count - 1))
    base_scale = lake_extent * (0.10 if debug_visuals else 0.075) * crowd_scale
    scale = clamp(base_scale, 0.45, 1.6)
    route_points = compute_boat_route(boat_index, layout, settings, scale, sample_count=24)
    boat_palette = (
        (0.95, 0.28, 0.12, 1.0),
        (0.96, 0.68, 0.16, 1.0),
        (0.84, 0.34, 0.18, 1.0),
        (0.92, 0.52, 0.14, 1.0),
        (0.98, 0.50, 0.28, 1.0),
        (0.85, 0.64, 0.18, 1.0),
    )

    plot_tag = f"P{layout['plot_index']:03d}"
    boat_vertices, boat_faces = build_boat_mesh(scale)
    boat_color = boat_palette[boat_index % len(boat_palette)]
    boat_material = try_build_material(
        build_boat_material,
        f"{BOAT_MATERIAL_NAME}_{boat_index + 1}",
        boat_color,
        debug_visuals,
    )
    start_point = route_points[0]
    start_world_location = layout["terrain_origin"] + start_point

    boat_obj = create_mesh_object(
        f"ICITY_ECO_{plot_tag}_Boat_{boat_index + 1}",
        boat_vertices,
        boat_faces,
        collection,
        start_world_location,
        boat_material,
    )
    boat_obj.color = boat_color
    # Keep the boat parented to the terrain so moving/rotating the whole plot
    # carries the boats along with it. The dashed "relationship line" this
    # normally draws in the viewport is turned off via the overlay setting in
    # hide_relationship_lines(); it never appears in a render either way.
    set_parent_keep_transform(boat_obj, terrain_obj)
    boat_obj.rotation_mode = "XYZ"
    boat_obj.hide_select = True
    if debug_visuals:
        boat_obj.show_in_front = True

        marker_vertices, marker_faces = build_debug_marker_mesh(scale)
        marker_obj = create_mesh_object(
            f"ICITY_ECO_{plot_tag}_BoatMarker_{boat_index + 1}",
            marker_vertices,
            marker_faces,
            collection,
            start_world_location + Vector((0.0, 0.0, scale * 0.9)),
            try_build_material(build_debug_marker_material),
        )
        set_parent_keep_transform(marker_obj, terrain_obj)
        marker_obj.hide_select = True
        marker_obj.show_in_front = True

    frame_span = max(1, settings.animation_end - settings.animation_start)
    point_count = len(route_points)
    for step_index, point in enumerate(route_points + [route_points[0]]):
        if step_index == point_count:
            frame = settings.animation_end
            next_point = route_points[1] if point_count > 1 else route_points[0]
        else:
            frame = settings.animation_start + round(frame_span * step_index / point_count)
            next_point = route_points[(step_index + 1) % point_count]

        boat_obj.location = point
        boat_obj.rotation_euler = compute_boat_rotation(point, next_point, step_index, scale)
        boat_obj.keyframe_insert(data_path="location", frame=frame)
        boat_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

        if debug_visuals:
            marker_obj.location = point + Vector((0.0, 0.0, scale * 0.9))
            marker_obj.keyframe_insert(data_path="location", frame=frame)

    set_linear_interpolation(boat_obj.animation_data.action if boat_obj.animation_data else None)
    add_cycles_modifier(boat_obj.animation_data.action if boat_obj.animation_data else None)
    if debug_visuals:
        set_linear_interpolation(marker_obj.animation_data.action if marker_obj.animation_data else None)
        add_cycles_modifier(marker_obj.animation_data.action if marker_obj.animation_data else None)


def create_boats(
    layout: dict,
    settings,
    collection: bpy.types.Collection,
    terrain_obj: bpy.types.Object,
) -> None:
    created = 0
    for boat_index in range(settings.boat_count):
        create_boat_animation(boat_index, layout, settings, collection, terrain_obj)
        created += 1
    boat_objects = [obj for obj in collection.objects if "_Boat_" in obj.name]
    print(
        f"[ICity Ecology] plot {layout['plot_index']:03d}: requested {settings.boat_count} boats, "
        f"created {created}, boat objects now in collection: {len(boat_objects)}"
    )


def populate_plot(
    plot_index: int,
    plot_center: Vector,
    base_z: float,
    settings,
    plot_collection: bpy.types.Collection,
    terrain_collection: bpy.types.Collection,
    water_collection: bpy.types.Collection,
    boat_collection: bpy.types.Collection,
) -> bpy.types.Object:
    base_location = Vector((plot_center.x, plot_center.y, base_z + settings.plot_ground_offset))
    guide_obj = create_plot_guide(plot_index, base_location, settings, plot_collection)
    layout = build_plot_layout(plot_index, base_location, settings)

    terrain_obj = create_terrain(layout, settings, terrain_collection)
    set_parent_keep_transform(guide_obj, terrain_obj)
    if layout["has_lake"]:
        lake_obj = create_lake(layout, settings, water_collection)
        set_parent_keep_transform(lake_obj, terrain_obj)
        if settings.boat_count > 0:
            create_boats(layout, settings, boat_collection, terrain_obj)
    return terrain_obj

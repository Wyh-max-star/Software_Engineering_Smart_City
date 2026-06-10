"""Traffic and crowd generation for the standalone ICity ecology extension."""

from __future__ import annotations

import bpy

try:
    from .ecology_common import (
        create_follow_path,
        create_follower,
        create_strip_from_closed_points,
        ellipse_points,
        ensure_principled_input,
        get_or_create_material,
    )
except ImportError:
    from ecology_common import (
        create_follow_path,
        create_follower,
        create_strip_from_closed_points,
        ellipse_points,
        ensure_principled_input,
        get_or_create_material,
    )


ROAD_OBJECT_NAME = "ICITY_ECO_ScenicRoad"
WALKWAY_OBJECT_NAME = "ICITY_ECO_LakesideWalkway"

ROAD_MATERIAL_NAME = "ICITY_ECO_Road_Material"
WALKWAY_MATERIAL_NAME = "ICITY_ECO_Walkway_Material"
CAR_MATERIAL_NAME = "ICITY_ECO_Car_Material"
PEDESTRIAN_MATERIAL_NAME = "ICITY_ECO_Pedestrian_Material"


def build_road_material() -> bpy.types.Material:
    material = get_or_create_material(ROAD_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (320, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (120, 0)
    bsdf.inputs["Base Color"].default_value = (0.08, 0.08, 0.09, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.76)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-280, 0)
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 4.0

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.location = (-80, 0)
    color_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.055, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.13, 0.13, 0.14, 1.0)

    links.new(noise.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_walkway_material() -> bpy.types.Material:
    material = get_or_create_material(WALKWAY_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.54, 0.48, 0.41, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.88)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_car_material() -> bpy.types.Material:
    material = get_or_create_material(CAR_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.14, 0.22, 0.74, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.32)
    ensure_principled_input(bsdf, ("Metallic",), 0.22)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_pedestrian_material() -> bpy.types.Material:
    material = get_or_create_material(PEDESTRIAN_MATERIAL_NAME)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (280, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    bsdf.inputs["Base Color"].default_value = (0.82, 0.56, 0.38, 1.0)
    ensure_principled_input(bsdf, ("Roughness",), 0.68)

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_car_mesh(scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
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
        (2, 3, 9, 8),
        (4, 5, 7, 6),
        (6, 7, 9, 8),
        (0, 1, 3, 2),
        (2, 8, 9, 3),
    ]
    return ([(x * scale, y * scale, z * scale) for x, y, z in vertices], faces)


def build_pedestrian_mesh(scale: float) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    torso = [
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
    return ([(x * scale, y * scale, z * scale) for x, y, z in torso], faces)


def generate_traffic_system(
    layout: dict,
    settings,
    traffic_collection: bpy.types.Collection,
    crowd_collection: bpy.types.Collection,
    path_collection: bpy.types.Collection,
) -> None:
    traffic_z = max(layout["water_level"] + settings.lake_depth + 0.45, 0.12)
    traffic_points = ellipse_points(
        layout["traffic_center"],
        max(settings.traffic_loop_radius_x, 6.0),
        max(settings.traffic_loop_radius_y, 4.0),
        layout["traffic_rotation"],
        48,
        traffic_z,
    )
    road_obj = create_strip_from_closed_points(
        ROAD_OBJECT_NAME,
        traffic_points,
        settings.road_width,
        traffic_collection,
        layout["terrain_origin"],
        build_road_material(),
    )
    road_obj.location.z += 0.02

    traffic_path = create_follow_path(
        "ICITY_ECO_CarPath",
        traffic_points,
        path_collection,
        layout["terrain_origin"],
        settings.animation_end - settings.animation_start,
    )
    car_vertices, car_faces = build_car_mesh(settings.car_scale)
    for car_index in range(settings.car_count):
        phase = car_index / max(1, settings.car_count)
        car_obj = create_follower(
            name=f"ICITY_ECO_Car_{car_index + 1}",
            collection=traffic_collection,
            mesh_vertices=car_vertices,
            mesh_faces=car_faces,
            material=build_car_material(),
            path_obj=traffic_path,
            frame_start=settings.animation_start,
            frame_end=settings.animation_end,
            phase_start=phase,
            bobbing=(0.04, 0.07),
        )
        yaw = 0.0 if (car_index % 2 == 0) else 0.02
        for frame, tilt in (
            (settings.animation_start, yaw),
            (settings.animation_start + (settings.animation_end - settings.animation_start) * 0.5, -yaw),
            (settings.animation_end, yaw),
        ):
            car_obj.rotation_euler = (0.0, 0.0, tilt)
            car_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

    walkway_points_outer = ellipse_points(
        layout["crowd_center"],
        layout["lake_radius_x"] + settings.walkway_offset,
        layout["lake_radius_y"] + settings.walkway_offset * 0.82,
        layout["lake_rotation"],
        56,
        layout["water_level"] + 0.04,
    )
    walkway_obj = create_strip_from_closed_points(
        WALKWAY_OBJECT_NAME,
        walkway_points_outer,
        settings.walkway_width,
        crowd_collection,
        layout["terrain_origin"],
        build_walkway_material(),
    )
    walkway_obj.location.z += 0.01

    crowd_path_outer = create_follow_path(
        "ICITY_ECO_CrowdPathOuter",
        walkway_points_outer,
        path_collection,
        layout["terrain_origin"],
        settings.animation_end - settings.animation_start,
    )
    walkway_points_inner = ellipse_points(
        layout["crowd_center"],
        max(layout["lake_radius_x"] + settings.walkway_offset - settings.walkway_width * 0.42, 1.5),
        max(layout["lake_radius_y"] + (settings.walkway_offset - settings.walkway_width * 0.42) * 0.82, 1.2),
        layout["lake_rotation"],
        56,
        layout["water_level"] + 0.04,
    )
    crowd_path_inner = create_follow_path(
        "ICITY_ECO_CrowdPathInner",
        list(reversed(walkway_points_inner)),
        path_collection,
        layout["terrain_origin"],
        settings.animation_end - settings.animation_start,
    )

    pedestrian_vertices, pedestrian_faces = build_pedestrian_mesh(settings.pedestrian_scale)
    for crowd_index in range(settings.crowd_count):
        use_outer = crowd_index % 2 == 0
        path_obj = crowd_path_outer if use_outer else crowd_path_inner
        phase = crowd_index / max(1, settings.crowd_count)
        pedestrian = create_follower(
            name=f"ICITY_ECO_Pedestrian_{crowd_index + 1}",
            collection=crowd_collection,
            mesh_vertices=pedestrian_vertices,
            mesh_faces=pedestrian_faces,
            material=build_pedestrian_material(),
            path_obj=path_obj,
            frame_start=settings.animation_start,
            frame_end=settings.animation_end + int((crowd_index % 3) * 18),
            phase_start=phase,
            bobbing=(0.0, 0.03),
        )
        arm_sway = 0.14 if use_outer else -0.14
        for frame, rot_y in (
            (settings.animation_start, arm_sway),
            (settings.animation_start + (settings.animation_end - settings.animation_start) * 0.5, -arm_sway),
            (settings.animation_end, arm_sway),
        ):
            pedestrian.rotation_euler = (0.0, rot_y, 0.0)
            pedestrian.keyframe_insert(data_path="rotation_euler", frame=frame)

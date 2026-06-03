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


ICITY_ROOT_COLLECTION = ecology_common.ICITY_ROOT_COLLECTION
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


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


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

    for index, vehicle_type in enumerate(sequence):
        phase = index / total
        path_obj = path_outer if vehicle_type == "BUS" else path_inner
        mesh_scale = bus_scale if vehicle_type == "BUS" else base_vehicle_scale
        vertices, faces = _vehicle_mesh(vehicle_type, mesh_scale)
        ecology_common.create_follower(
            name=f"ICITY_TRAFFIC_{vehicle_type}_{index + 1}",
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

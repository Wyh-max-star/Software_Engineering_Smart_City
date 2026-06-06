"""Standalone pedestrian (crowd) simulation module for the ICity addon.

This module animates real character rigs (the ``Standing.fbx`` idle pose and the
``Walking.fbx`` walk cycle that ship with the project) so that the generated city
is populated with believable pedestrians:

- walkers stride along sidewalks that are offset to the *side* of the real iCity
  road graph, never on the road itself, and the two sides of a street flow in
  opposite directions (keep-to-one-side behaviour);
- idlers stand at sidewalk corners / intersections facing the street, the way
  people wait at crossings;
- every agent faces its direction of travel, walks at a slightly randomised
  speed, and is spread out along the sidewalk so the crowd never marches in
  lock-step.

The heavy ``bpy`` work (FBX import, rig instancing) is isolated from the pure
geometry planning helpers (`plan_sidewalk_routes`, `plan_idle_spots`, ...) so the
social-layout logic stays unit-testable outside Blender.
"""

from __future__ import annotations

import importlib
import importlib.util
import math
import random
from pathlib import Path

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector


def _load_sibling(module_name: str, file_name: str):
    """Import a sibling module both as a package member and as a loose file.

    Mirrors the import strategy already used by ``traffic_extension`` so the
    module works whether the addon is loaded as a package or the file is run in
    isolation (e.g. unit tests).
    """

    try:
        package = importlib.import_module(f".{module_name}", __package__) if __package__ else None
    except Exception:  # pragma: no cover - fall through to file based import
        package = None
    if package is not None:
        return package

    module_path = Path(__file__).resolve().with_name(file_name)
    spec = importlib.util.spec_from_file_location(f"pedestrian_extension_{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ecology_common = _load_sibling("ecology_common", "ecology_common.py")
traffic_extension = _load_sibling("traffic_extension", "traffic_extension.py")


ICITY_ROOT_COLLECTION = ecology_common.ICITY_ROOT_COLLECTION
get_or_create_child_collection = ecology_common.get_or_create_child_collection
add_cycles_modifier = ecology_common.add_cycles_modifier
set_linear_interpolation = ecology_common.set_linear_interpolation
object_world_bounds = ecology_common.object_world_bounds
merge_bounds = ecology_common.merge_bounds
ellipse_points = ecology_common.ellipse_points
get_city_bounds = ecology_common.get_city_bounds


PED_ROOT_COLLECTION = "ICity Pedestrians"
PED_SOURCE_COLLECTION = "ICity Pedestrian Sources"
PED_WALKER_COLLECTION = "ICity Pedestrian Walkers"
PED_IDLER_COLLECTION = "ICity Pedestrian Idlers"
PED_PATH_COLLECTION = "ICity Pedestrian Paths"

PEOPLE_DIR = Path(__file__).resolve().parents[1] / "assets" / "Assets" / "Default" / "People"
WALKING_FBX = PEOPLE_DIR / "Walking.fbx"
STANDING_FBX = PEOPLE_DIR / "Standing.fbx"

DEFAULT_PERSON_HEIGHT = 1.72


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


# ---------------------------------------------------------------------------
# Pure planning helpers (no bpy.ops, unit-testable with the stub Vector)
# ---------------------------------------------------------------------------


def sidewalk_offset(road_width: float, sidewalk_margin: float) -> float:
    """Lateral distance from a road centreline to the pedestrian sidewalk."""

    return max(road_width, 0.0) * 0.5 + max(sidewalk_margin, 0.0)


def _segment_normal(previous_point: Vector, next_point: Vector) -> Vector:
    tangent = next_point - previous_point
    length = math.sqrt(tangent.x * tangent.x + tangent.y * tangent.y)
    if length == 0.0:
        return Vector((0.0, 1.0, 0.0))
    return Vector((-tangent.y / length, tangent.x / length, 0.0))


def polyline_loop_length(points: list[Vector]) -> float:
    """Total length of a closed polyline (last point wraps to the first)."""

    count = len(points)
    if count < 2:
        return 0.0
    return sum((points[(index + 1) % count] - points[index]).length for index in range(count))


def plan_sidewalk_routes(
    road_paths: list[list[Vector]],
    offset: float,
    z_lift: float,
) -> list[dict]:
    """Build walkable sidewalk routes flanking every road chain.

    ``offset`` is the lateral distance from the road centreline to the middle of
    the sidewalk (ideally read from the iCity ``Road lanes width`` /
    ``side walk offset`` attributes so people land on the pavement, not the
    roadway). Each road chain yields two routes, one per side, travelling in
    opposite directions so foot traffic mimics real keep-to-one-side pavements.
    """

    routes: list[dict] = []
    for chain in road_paths:
        if len(chain) < 2:
            continue
        for side in (1.0, -1.0):
            shifted = traffic_extension._offset_chain(chain, offset * side)
            motion_points = traffic_extension.vehicle_motion_points_from_chain(shifted)
            if side < 0.0:
                motion_points = list(reversed(motion_points))
            if len(motion_points) < 2:
                continue
            lifted = [Vector((point.x, point.y, point.z + z_lift)) for point in motion_points]
            routes.append({"points": lifted, "side": side})
    return routes


def plan_fallback_loop_routes(
    center: Vector,
    city_radius: float,
    ground_z: float,
    sidewalk_margin: float,
    z_lift: float,
) -> list[dict]:
    """Outer ring sidewalks used when the scene exposes no readable road graph."""

    base = city_radius + max(sidewalk_margin, 1.5) + 4.0
    minor_floor = city_radius + max(sidewalk_margin, 1.5)
    routes: list[dict] = []
    for ring_index, side in enumerate((1.0, -1.0)):
        radius_x = base + ring_index * 2.2
        radius_y = max(base * 0.82, minor_floor) + ring_index * 1.8
        loop = ellipse_points(
            Vector((center.x, center.y)),
            radius_x,
            radius_y,
            0.0,
            64,
            ground_z + z_lift,
        )
        if side < 0.0:
            loop = list(reversed(loop))
        routes.append({"points": loop, "side": side})
    return routes


def plan_idle_spots(
    road_paths: list[list[Vector]],
    offset: float,
    idle_count: int,
    seed: int,
    z_lift: float,
) -> list[tuple[Vector, float]]:
    """Pick standing spots at intersections / corners facing the street.

    Anchors are taken from chain endpoints (which are road intersections) and a
    mid-chain point. Each anchor is pushed onto the sidewalk by ``offset`` and
    the person is rotated to look back toward the road, like waiting at a crossing.
    """

    if idle_count <= 0 or not road_paths:
        return []

    rng = random.Random(seed)
    candidates: list[tuple[Vector, float]] = []
    for chain in road_paths:
        if len(chain) < 2:
            continue
        anchor_indices = {0, len(chain) - 1, len(chain) // 2}
        for index in sorted(anchor_indices):
            point = chain[index]
            previous_point = chain[max(index - 1, 0)]
            next_point = chain[min(index + 1, len(chain) - 1)]
            normal = _segment_normal(previous_point, next_point)
            side = 1.0 if rng.random() < 0.5 else -1.0
            position = Vector(
                (
                    point.x + normal.x * offset * side,
                    point.y + normal.y * offset * side,
                    point.z + z_lift,
                )
            )
            # Face back toward the road centreline (opposite the offset normal).
            facing = math.atan2(-normal.y * side, -normal.x * side)
            candidates.append((position, facing))

    rng.shuffle(candidates)
    return candidates[:idle_count]


def plan_fallback_idle_spots(
    center: Vector,
    city_radius: float,
    ground_z: float,
    sidewalk_margin: float,
    idle_count: int,
    z_lift: float,
) -> list[tuple[Vector, float]]:
    if idle_count <= 0:
        return []
    base = city_radius + max(sidewalk_margin, 1.5) + 4.0
    spots: list[tuple[Vector, float]] = []
    for index in range(idle_count):
        angle = (index / max(idle_count, 1)) * math.tau
        position = Vector(
            (
                center.x + math.cos(angle) * base,
                center.y + math.sin(angle) * base * 0.82,
                ground_z + z_lift,
            )
        )
        # Look inward toward the city centre.
        facing = math.atan2(center.y - position.y, center.x - position.x)
        spots.append((position, facing))
    return spots


# ---------------------------------------------------------------------------
# Blender-side rig handling
# ---------------------------------------------------------------------------


def _create_empty(name: str, collection: bpy.types.Collection) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.12
    empty.hide_render = True
    empty.hide_select = True
    collection.objects.link(empty)
    return empty


def read_pedestrian_offset_from_scene():
    """Read the real sidewalk offset from the iCity base-mesh edge attributes.

    iCity stores ``Road lanes width`` (total roadway width) and
    ``side walk offset`` (sidewalk width) per road edge. Placing pedestrians at
    ``roadway_half_width + sidewalk_width / 2`` puts them on the centre of the
    pavement instead of on the road / parking lane. Returns ``None`` when the
    attributes are unavailable so callers can fall back to panel values.
    """

    base = traffic_extension.get_base_object()
    mesh = getattr(base, "data", None)
    attributes = getattr(mesh, "attributes", None)
    if attributes is None:
        return None

    road_deleted = attributes.get("Road del")
    lanes_width = attributes.get("Road lanes width")
    if road_deleted is None or lanes_width is None:
        return None
    sidewalk = attributes.get("side walk offset")

    scale = 1.0
    matrix_world = getattr(base, "matrix_world", None)
    if matrix_world is not None and hasattr(matrix_world, "to_scale"):
        world_scale = matrix_world.to_scale()
        scale = (abs(world_scale.x) + abs(world_scale.y)) * 0.5

    road_data = getattr(road_deleted, "data", [])
    lane_data = getattr(lanes_width, "data", [])
    sidewalk_data = getattr(sidewalk, "data", None)

    offsets: list[float] = []
    for index in range(min(len(road_data), len(lane_data))):
        deleted = bool(getattr(road_data[index], "value", getattr(road_data[index], "value_bool", True)))
        if deleted:
            continue
        width = float(getattr(lane_data[index], "value", 0.0))
        sidewalk_width = 0.0
        if sidewalk_data is not None and index < len(sidewalk_data):
            sidewalk_width = float(getattr(sidewalk_data[index], "value", 0.0))
        offsets.append((width * 0.5 + sidewalk_width * 0.5) * scale)

    if not offsets:
        return None
    offsets.sort()
    return offsets[len(offsets) // 2]


def _keyframe_pedestrian_motion(
    carrier: bpy.types.Object,
    path_points: list[Vector],
    frame_start: int,
    frame_end: int,
    phase_start: float,
    speed_per_frame: float,
    stop_chance: float,
    rng: random.Random,
) -> None:
    """Walk the carrier along ``path_points`` with occasional pauses.

    The carrier advances at a constant ``speed_per_frame`` (world units / frame),
    but every so often holds its position for a short while, producing natural
    stop-and-go foot traffic. The character's own walk cycle keeps looping, so a
    held position reads as someone pausing on the spot.
    """

    loop_length = max(polyline_loop_length(path_points), 0.001)
    phase_per_frame = speed_per_frame / loop_length
    carrier.rotation_mode = "XYZ"

    def heading_at(phase: float) -> float:
        here = ecology_common._sample_path_point(path_points, phase % 1.0)
        ahead = ecology_common._sample_path_point(path_points, (phase + 0.0025) % 1.0)
        delta = ahead - here
        return math.atan2(delta.y, delta.x)

    def place(phase: float, frame: int, heading: float) -> None:
        point = ecology_common._sample_path_point(path_points, phase % 1.0)
        carrier.location = Vector((point.x, point.y, point.z))
        carrier.rotation_euler = (0.0, 0.0, heading)
        carrier.keyframe_insert(data_path="location", frame=frame)
        carrier.keyframe_insert(data_path="rotation_euler", frame=frame)

    phase = phase_start
    heading = heading_at(phase)
    place(phase, frame_start, heading)

    frame = frame_start
    while frame < frame_end:
        if stop_chance > 0.0 and rng.random() < stop_chance:
            pause = rng.randint(18, 60)
            next_frame = min(frame + pause, frame_end)
            place(phase, next_frame, heading)  # hold position -> a stop
            frame = next_frame
            continue
        step = rng.randint(24, 80)
        next_frame = min(frame + step, frame_end)
        heading = heading_at(phase)
        phase += phase_per_frame * (next_frame - frame)
        place(phase, next_frame, heading)
        frame = next_frame

    action = carrier.animation_data.action if carrier.animation_data else None
    set_linear_interpolation(action)


def _import_fbx_template(fbx_path: Path, collection: bpy.types.Collection) -> dict:
    """Import an animated character FBX once and return it as a hidden template.

    The returned objects stay hidden in the source collection; runtime
    pedestrians are lightweight copies of them so the heavy FBX is only parsed
    once per generation.
    """

    if not fbx_path.exists():
        raise RuntimeError(f"Character file not found: {fbx_path}")

    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    new_objects = [obj for obj in bpy.data.objects if obj not in before]
    if not new_objects:
        raise RuntimeError(f"FBX import produced no objects: {fbx_path}")

    new_set = set(new_objects)
    for obj in new_objects:
        for linked in list(obj.users_collection):
            linked.objects.unlink(obj)
        collection.objects.link(obj)
        obj.hide_viewport = True
        obj.hide_render = True
        obj.hide_select = True

    armature = next((obj for obj in new_objects if obj.type == "ARMATURE"), None)
    mesh_objects = [obj for obj in new_objects if obj.type == "MESH"]
    roots = [obj for obj in new_objects if obj.parent not in new_set]

    action = None
    if armature is not None and armature.animation_data is not None:
        action = armature.animation_data.action
        if action is not None:
            add_cycles_modifier(action)

    bounds_objects = mesh_objects or new_objects
    merged = merge_bounds(object_world_bounds(obj) for obj in bounds_objects)
    world_height = max(merged[1].z - merged[0].z, 0.001) if merged is not None else DEFAULT_PERSON_HEIGHT

    return {
        "objects": new_objects,
        "roots": roots,
        "armature": armature,
        "mesh_objects": mesh_objects,
        "action": action,
        "world_height": world_height,
    }


def _instantiate_rig(template: dict, collection: bpy.types.Collection) -> dict:
    """Create a lightweight copy of a template rig linked into ``collection``.

    Object data (mesh / armature) and the animation action are shared with the
    template; only the objects themselves are duplicated, and armature modifiers
    are repointed at the copied armature.
    """

    copies: dict = {}
    for obj in template["objects"]:
        new_obj = obj.copy()
        new_obj.hide_viewport = False
        new_obj.hide_render = False
        new_obj.hide_select = False
        for linked in list(new_obj.users_collection):
            linked.objects.unlink(new_obj)
        collection.objects.link(new_obj)
        copies[obj] = new_obj

    template_set = set(template["objects"])
    for obj in template["objects"]:
        new_obj = copies[obj]
        if obj.parent in template_set:
            new_obj.parent = copies[obj.parent]
            new_obj.matrix_parent_inverse = obj.matrix_parent_inverse.copy()
        for modifier in new_obj.modifiers:
            target = getattr(modifier, "object", None)
            if target in template_set:
                modifier.object = copies[target]
    return copies


def _attach_rig(
    template: dict,
    collection: bpy.types.Collection,
    anchor: bpy.types.Object,
    facing_offset: float,
    height_factor: float,
    lateral: float,
) -> dict:
    """Mount a fresh rig copy under ``anchor`` with facing / scale correction.

    The rig copy keeps the looping action it inherited from the template via
    ``obj.copy()`` (including its slot binding), so every instance plays the
    walk / idle clip without any fragile per-instance action reassignment.
    """

    mount = _create_empty(f"{anchor.name}_Mount", collection)
    mount.parent = anchor
    mount.location = Vector((0.0, lateral, 0.0))
    mount.rotation_euler = (0.0, 0.0, facing_offset)
    mount.scale = (height_factor, height_factor, height_factor)

    copies = _instantiate_rig(template, collection)
    for root in template["roots"]:
        copies[root].parent = mount
    return copies


def _height_factor(template: dict, target_height: float) -> float:
    return max(target_height, 0.1) / max(template["world_height"], 0.001)


def _spawn_walkers(
    routes: list[dict],
    template: dict,
    collection: bpy.types.Collection,
    path_collection: bpy.types.Collection,
    settings,
) -> int:
    walker_count = max(int(getattr(settings, "walker_count", 0)), 0)
    if walker_count == 0 or not routes:
        return 0

    rng = random.Random(int(getattr(settings, "seed", 0)) + 101)
    frame_start = settings.animation_start
    frame_end = settings.animation_end
    height_factor = _height_factor(template, settings.person_height)
    facing_offset = math.radians(settings.facing_offset_deg)
    base_speed = max(getattr(settings, "walk_speed", 0.06), 0.001)
    speed_variation = _clamp(getattr(settings, "walk_speed_variation", 0.3), 0.0, 0.9)
    stop_chance = _clamp(getattr(settings, "stop_chance", 0.3), 0.0, 0.95)
    lateral_jitter = max(getattr(settings, "lateral_jitter", 0.25), 0.0)

    spawned = 0
    for index in range(walker_count):
        route = routes[index % len(routes)]
        speed = max(base_speed * (1.0 + rng.uniform(-1.0, 1.0) * speed_variation), 0.001)
        phase = (index / walker_count) + rng.uniform(-0.05, 0.05)

        carrier = _create_empty(f"ICITY_PED_Walker_{index + 1}", collection)
        _keyframe_pedestrian_motion(
            carrier,
            route["points"],
            frame_start,
            frame_end,
            phase,
            speed,
            stop_chance,
            rng,
        )

        lateral = rng.uniform(-lateral_jitter, lateral_jitter)
        _attach_rig(template, collection, carrier, facing_offset, height_factor, lateral)
        spawned += 1
    return spawned


def _spawn_idlers(
    idle_spots: list[tuple[Vector, float]],
    template: dict,
    collection: bpy.types.Collection,
    settings,
) -> int:
    if not idle_spots:
        return 0

    rng = random.Random(int(getattr(settings, "seed", 0)) + 202)
    height_factor = _height_factor(template, settings.person_height)
    facing_offset = math.radians(settings.facing_offset_deg)

    spawned = 0
    for index, (position, facing) in enumerate(idle_spots):
        anchor = _create_empty(f"ICITY_PED_Idler_{index + 1}", collection)
        anchor.location = position
        anchor.rotation_euler = (0.0, 0.0, facing + rng.uniform(-0.25, 0.25))

        _attach_rig(template, collection, anchor, facing_offset, height_factor, 0.0)
        spawned += 1
    return spawned


def _collect_objects(collection: bpy.types.Collection, sink: list) -> None:
    for child in list(collection.children):
        _collect_objects(child, sink)
    for obj in list(collection.objects):
        sink.append(obj)


def clear_pedestrians() -> None:
    """Remove everything this module generated, including orphaned rig data."""

    collection = bpy.data.collections.get(PED_ROOT_COLLECTION)
    if collection is None:
        return

    objects: list = []
    _collect_objects(collection, objects)

    data_blocks = set()
    actions = set()
    for obj in objects:
        if getattr(obj, "data", None) is not None:
            data_blocks.add(obj.data)
        animation_data = getattr(obj, "animation_data", None)
        if animation_data is not None and animation_data.action is not None:
            actions.add(animation_data.action)

    for obj in objects:
        for linked in list(obj.users_collection):
            linked.objects.unlink(obj)
        bpy.data.objects.remove(obj, do_unlink=True)

    for action in actions:
        if action.users == 0:
            bpy.data.actions.remove(action)
    for data in data_blocks:
        if getattr(data, "users", 1) != 0:
            continue
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Armature):
            bpy.data.armatures.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)

    ecology_common.remove_collection_recursive(collection)


def generate_pedestrians(context: bpy.types.Context) -> dict:
    settings = context.scene.icity_pedestrian_settings
    root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root_collection is None:
        raise RuntimeError("Please run iCity Start before generating pedestrians.")

    clear_pedestrians()

    ped_root = get_or_create_child_collection(root_collection, PED_ROOT_COLLECTION)
    source_collection = get_or_create_child_collection(ped_root, PED_SOURCE_COLLECTION)
    walker_collection = get_or_create_child_collection(ped_root, PED_WALKER_COLLECTION)
    idler_collection = get_or_create_child_collection(ped_root, PED_IDLER_COLLECTION)
    path_collection = get_or_create_child_collection(ped_root, PED_PATH_COLLECTION)

    walk_template = _import_fbx_template(WALKING_FBX, source_collection)
    stand_template = _import_fbx_template(STANDING_FBX, source_collection)

    z_lift = 0.05
    road_paths = traffic_extension.extract_vehicle_road_paths_from_scene()
    if road_paths:
        measured = read_pedestrian_offset_from_scene()
        if measured is not None and measured > 0.0:
            offset = measured + settings.sidewalk_margin
        else:
            offset = settings.road_width * 0.5 + max(settings.sidewalk_margin, 1.5)
        routes = plan_sidewalk_routes(road_paths, offset, z_lift)
        idle_spots = plan_idle_spots(road_paths, offset, settings.idle_count, int(settings.seed), z_lift)
    else:
        center, city_radius, ground_z = get_city_bounds()
        routes = plan_fallback_loop_routes(center, city_radius, ground_z, settings.sidewalk_margin, z_lift)
        idle_spots = plan_fallback_idle_spots(
            center, city_radius, ground_z, settings.sidewalk_margin, settings.idle_count, z_lift
        )

    walkers = _spawn_walkers(routes, walk_template, walker_collection, path_collection, settings)
    idlers = _spawn_idlers(idle_spots, stand_template, idler_collection, settings)

    context.scene.frame_start = settings.animation_start
    context.scene.frame_end = settings.animation_end
    context.scene.frame_set(settings.animation_start)
    return {"walkers": walkers, "idlers": idlers, "used_road_graph": bool(road_paths)}


class ICITY_PedestrianSettings(PropertyGroup):
    animation_start: IntProperty(name="Start Frame", default=1, min=1, max=100000)
    animation_end: IntProperty(name="End Frame", default=250, min=2, max=100000)

    walker_count: IntProperty(name="Walkers", default=16, min=0, max=200)
    idle_count: IntProperty(name="Idlers", default=8, min=0, max=120)

    road_width: FloatProperty(
        name="Road Width",
        description="Fallback roadway width when the iCity road attributes cannot be read",
        default=3.4,
        min=1.0,
        max=12.0,
    )
    sidewalk_margin: FloatProperty(
        name="Sidewalk Nudge",
        description="Extra outward offset added to the auto-detected sidewalk (negative moves toward the road)",
        default=0.0,
        min=-3.0,
        max=8.0,
    )

    person_height: FloatProperty(name="Person Height (m)", default=DEFAULT_PERSON_HEIGHT, min=0.5, max=3.0)
    facing_offset_deg: FloatProperty(name="Facing Offset", default=90.0, min=-180.0, max=180.0)

    walk_speed: FloatProperty(
        name="Walk Speed",
        description="Walking speed in world units per frame (lower = slower)",
        default=0.06,
        min=0.005,
        max=0.5,
    )
    walk_speed_variation: FloatProperty(name="Speed Variation", default=0.3, min=0.0, max=0.9)
    stop_chance: FloatProperty(
        name="Stop Chance",
        description="How often walkers pause (walk-and-stop); 0 = never stop",
        default=0.3,
        min=0.0,
        max=0.95,
    )
    lateral_jitter: FloatProperty(name="Lateral Jitter", default=0.25, min=0.0, max=2.0)
    seed: IntProperty(name="Seed", default=7, min=0, max=100000)


class ICITY_OT_GeneratePedestrians(Operator):
    bl_idname = "icity.generate_pedestrians"
    bl_label = "Generate / Update"
    bl_description = "Populate the current iCity scene with animated pedestrians"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        settings = context.scene.icity_pedestrian_settings
        if settings.animation_end <= settings.animation_start:
            self.report({"ERROR"}, "End Frame must be greater than Start Frame.")
            return {"CANCELLED"}
        try:
            result = generate_pedestrians(context)
        except Exception as exc:  # pragma: no cover - surfaced to the Blender UI
            self.report({"ERROR"}, f"Pedestrian generation failed: {exc}")
            return {"CANCELLED"}
        source = "road graph" if result["used_road_graph"] else "outer ring fallback"
        self.report(
            {"INFO"},
            f"ICity pedestrians generated ({result['walkers']} walkers, {result['idlers']} idlers, {source}).",
        )
        return {"FINISHED"}


class ICITY_OT_ClearPedestrians(Operator):
    bl_idname = "icity.clear_pedestrians"
    bl_label = "Clear"
    bl_description = "Clear pedestrians generated by this module"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        clear_pedestrians()
        self.report({"INFO"}, "ICity pedestrians cleared.")
        return {"FINISHED"}


class ICITY_PT_PedestrianPanel(Panel):
    bl_label = "ICity Pedestrians"
    bl_idname = "ICITY_PT_pedestrian_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.icity_pedestrian_settings

        count_box = layout.box()
        count_box.label(text="Crowd", icon="OUTLINER_OB_ARMATURE")
        count_box.prop(settings, "walker_count")
        count_box.prop(settings, "idle_count")

        layout_box = layout.box()
        layout_box.label(text="Sidewalks", icon="ORIENTATION_VIEW")
        layout_box.prop(settings, "sidewalk_margin")
        layout_box.prop(settings, "road_width")

        move_box = layout.box()
        move_box.label(text="Movement", icon="FORCE_FORCE")
        move_box.prop(settings, "walk_speed")
        move_box.prop(settings, "walk_speed_variation")
        move_box.prop(settings, "stop_chance")
        move_box.prop(settings, "lateral_jitter")

        look_box = layout.box()
        look_box.label(text="Characters", icon="POSE_HLT")
        look_box.prop(settings, "person_height")
        look_box.prop(settings, "facing_offset_deg")
        look_box.prop(settings, "seed")

        anim_box = layout.box()
        anim_box.label(text="Animation", icon="TIME")
        anim_box.prop(settings, "animation_start")
        anim_box.prop(settings, "animation_end")

        row = layout.row(align=True)
        row.operator("icity.generate_pedestrians", icon="PLAY")
        row.operator("icity.clear_pedestrians", icon="TRASH")


CLASSES = (
    ICITY_PedestrianSettings,
    ICITY_OT_GeneratePedestrians,
    ICITY_OT_ClearPedestrians,
    ICITY_PT_PedestrianPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_pedestrian_settings = PointerProperty(type=ICITY_PedestrianSettings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "icity_pedestrian_settings"):
        del bpy.types.Scene.icity_pedestrian_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

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
iter_action_fcurves = ecology_common.iter_action_fcurves
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


SIDEWALK_LANES = 3


def normalize_band(near: float, far: float) -> tuple[float, float]:
    """Return a sane (near, far) sidewalk band: non-negative and near <= far."""

    near = max(near, 0.0)
    far = max(far, 0.0)
    if far < near:
        near, far = far, near
    return near, far


def band_distances(near: float, far: float, lanes: int = SIDEWALK_LANES) -> list[float]:
    """Evenly spaced walking-line distances spanning the sidewalk band."""

    near, far = normalize_band(near, far)
    if lanes <= 1 or far == near:
        return [(near + far) * 0.5]
    return [near + (far - near) * (index / (lanes - 1)) for index in range(lanes)]


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
    near: float,
    far: float,
    z_lift: float,
) -> list[dict]:
    """Build walkable sidewalk routes flanking every road chain.

    The sidewalk is the band between ``near`` and ``far`` metres from the road
    centreline. For each road chain and each side we lay several walking lines
    spread across that band, so walkers fill the pavement. The two sides travel
    in opposite directions, mimicking real keep-to-one-side foot traffic.
    """

    distances = band_distances(near, far)
    routes: list[dict] = []
    for chain in road_paths:
        if len(chain) < 2:
            continue
        for side in (1.0, -1.0):
            for distance in distances:
                shifted = traffic_extension._offset_chain(chain, distance * side)
                motion_points = traffic_extension.vehicle_motion_points_from_chain(shifted)
                if side < 0.0:
                    motion_points = list(reversed(motion_points))
                if len(motion_points) < 2:
                    continue
                lifted = [Vector((point.x, point.y, point.z + z_lift)) for point in motion_points]
                routes.append({"points": lifted, "side": side, "distance": distance})
    return routes


def plan_fallback_loop_routes(
    center: Vector,
    city_radius: float,
    ground_z: float,
    near: float,
    far: float,
    z_lift: float,
) -> list[dict]:
    """Outer ring sidewalks used when the scene exposes no readable road graph."""

    near, far = normalize_band(near, far)
    routes: list[dict] = []
    for side, distance in ((1.0, near), (-1.0, far)):
        radius = city_radius + max(distance, 1.5)
        loop = ellipse_points(
            Vector((center.x, center.y)),
            radius,
            max(radius * 0.82, city_radius + 1.0),
            0.0,
            64,
            ground_z + z_lift,
        )
        if side < 0.0:
            loop = list(reversed(loop))
        routes.append({"points": loop, "side": side, "distance": distance})
    return routes


def _idle_candidate(
    point: Vector,
    previous_point: Vector,
    next_point: Vector,
    near: float,
    far: float,
    rng: random.Random,
    z_lift: float,
) -> tuple[Vector, float]:
    """Push one anchor onto the sidewalk band and face it back toward the road."""

    normal = _segment_normal(previous_point, next_point)
    side = 1.0 if rng.random() < 0.5 else -1.0
    # Stand dead-centre of the band so idlers are guaranteed within [near, far].
    distance = (near + far) * 0.5
    position = Vector(
        (
            point.x + normal.x * distance * side,
            point.y + normal.y * distance * side,
            point.z + z_lift,
        )
    )
    # Face back toward the road centreline (opposite the offset normal).
    facing = math.atan2(-normal.y * side, -normal.x * side)
    return position, facing


def corner_vertex_flags(chain: list[Vector], window: int = 2, total_turn_deg: float = 30.0) -> list[bool]:
    """Mark chain vertices that sit on a road bend (a corner).

    iCity rounds the city's corners, so the road centreline curves there; pushing
    a sidewalk point outward at such a bend overshoots the rounded edge and hangs
    over the void. A vertex is flagged when the road turns by more than
    ``total_turn_deg`` within ``window`` vertices of it — this catches both a
    single sharp corner and a rounded one spread over several small turns.
    Endpoints are never flagged (they are intersections handled separately).
    """

    count = len(chain)
    flags = [False] * count
    if count < 3:
        return flags

    turns = [0.0] * count
    for index in range(1, count - 1):
        incoming = chain[index] - chain[index - 1]
        outgoing = chain[index + 1] - chain[index]
        cross = incoming.x * outgoing.y - incoming.y * outgoing.x
        dot = incoming.x * outgoing.x + incoming.y * outgoing.y
        turns[index] = abs(math.atan2(cross, dot))

    threshold = math.radians(total_turn_deg)
    for index in range(1, count - 1):
        low = max(1, index - window)
        high = min(count - 2, index + window)
        if sum(turns[neighbour] for neighbour in range(low, high + 1)) > threshold:
            flags[index] = True
    return flags


def plan_idle_spots(
    road_paths: list[list[Vector]],
    near: float,
    far: float,
    idle_count: int,
    seed: int,
    z_lift: float,
) -> list[tuple[Vector, float]]:
    """Pick standing spots along the straight parts of the sidewalk band.

    Anchors are sampled *off* the road nodes — at segment midpoints and interior
    vertices — never at the chain endpoints (intersections) and never on a road
    bend (a corner), so idlers don't end up standing in a crossing road or hung
    over the void at the city's rounded corners. Each kept anchor is pushed the
    same ``[near, far]`` distance onto the pavement that the walkers use.
    """

    if idle_count <= 0 or not road_paths:
        return []

    near, far = normalize_band(near, far)
    rng = random.Random(seed)
    candidates: list[tuple[Vector, float]] = []
    for chain in road_paths:
        if len(chain) < 2:
            continue
        is_corner = corner_vertex_flags(chain)
        anchors: list[tuple[Vector, Vector, Vector]] = []
        # Segment midpoints — skip a segment touching a corner vertex.
        for index in range(len(chain) - 1):
            if is_corner[index] or is_corner[index + 1]:
                continue
            a, b = chain[index], chain[index + 1]
            mid = Vector(((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, (a.z + b.z) * 0.5))
            anchors.append((mid, a, b))
        # Interior vertices, skipping the endpoints and any corner vertex.
        for index in range(1, len(chain) - 1):
            if is_corner[index]:
                continue
            anchors.append((chain[index], chain[index - 1], chain[index + 1]))
        for point, previous_point, next_point in anchors:
            candidates.append(_idle_candidate(point, previous_point, next_point, near, far, rng, z_lift))

    rng.shuffle(candidates)
    return candidates[:idle_count]


def plan_fallback_idle_spots(
    center: Vector,
    city_radius: float,
    ground_z: float,
    near: float,
    far: float,
    idle_count: int,
    z_lift: float,
) -> list[tuple[Vector, float]]:
    if idle_count <= 0:
        return []
    near, far = normalize_band(near, far)
    base = city_radius + (near + far) * 0.5
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


def _drifts_monotonically(values: list[float]) -> bool:
    """True if a channel trends one way (locomotion) rather than oscillating.

    A forward-walking root translates steadily across the clip, so its net
    displacement is large relative to its overall range. A hip bob or sway
    returns to where it started, so its net displacement is tiny next to its
    range. We use that contrast to tell root motion apart from pose motion.
    """

    if len(values) < 2:
        return False
    net = abs(values[-1] - values[0])
    amplitude = max(values) - min(values)
    return net > 0.01 and net > 0.5 * amplitude


def _root_bone_names(armature) -> set:
    data = getattr(armature, "data", None) if armature is not None else None
    return {bone.name for bone in getattr(data, "bones", []) if getattr(bone, "parent", None) is None}


def _flatten_fcurve(fcurve) -> None:
    points = fcurve.keyframe_points
    if not len(points):
        return
    base = points[0].co[1]
    for keyframe in points:
        keyframe.co[1] = base
        keyframe.handle_left[1] = base
        keyframe.handle_right[1] = base
    fcurve.update()


def _strip_root_motion(armature, action) -> None:
    """Pin a walk/idle clip in place by removing forward locomotion drift.

    The bundled character clips translate the whole body forward; once the clip
    loops (``add_cycles_modifier``) the body snaps back to the clip's start,
    which reads as the pedestrian teleporting every few dozen frames. The
    carrier empty is what actually moves a pedestrian through the world, so any
    root location channel that drifts one way (rather than oscillating like a
    hip bob) is flattened, leaving an in-place stride the carrier can transport.
    """

    if action is None:
        return
    roots = _root_bone_names(armature)
    for fcurve in iter_action_fcurves(action):
        data_path = getattr(fcurve, "data_path", "")
        is_object_location = data_path == "location"
        is_root_bone_location = data_path.endswith(".location") and any(
            f'bones["{name}"]' in data_path for name in roots
        )
        if not (is_object_location or is_root_bone_location):
            continue
        values = [keyframe.co[1] for keyframe in fcurve.keyframe_points]
        if _drifts_monotonically(values):
            _flatten_fcurve(fcurve)


def _center_template_horizontally(roots: list, armature, action, merged) -> None:
    """Slide a character so its horizontal footprint sits on its anchor.

    The bundled clips do not always pose the character over the armature origin,
    so an instance placed at an anchor can render up to ~half a metre to the
    side. With a narrow sidewalk band (e.g. 6.3-6.8 m) that drift is enough to
    push a *standing* idler clean out of the band. We measure the footprint
    centre at import and move every root by the negative of that offset — through
    the object's location channel if the armature animates it, otherwise through
    its static location — so the rendered body lands exactly on the anchor.
    """

    if merged is None:
        return
    cx = (merged[0].x + merged[1].x) * 0.5
    cy = (merged[0].y + merged[1].y) * 0.5
    # A large offset means the rig imported somewhere unexpected; leave it rather
    # than risk flinging every pedestrian across the map.
    if max(abs(cx), abs(cy)) > 3.0:
        return

    animated_axes = set()
    if armature is not None and action is not None:
        for fcurve in iter_action_fcurves(action):
            if getattr(fcurve, "data_path", "") != "location":
                continue
            axis = getattr(fcurve, "array_index", -1)
            if axis not in (0, 1):
                continue
            shift = cx if axis == 0 else cy
            for keyframe in fcurve.keyframe_points:
                keyframe.co[1] -= shift
                keyframe.handle_left[1] -= shift
                keyframe.handle_right[1] -= shift
            fcurve.update()
            animated_axes.add(axis)

    for root in roots:
        is_armature = root is armature
        if not (is_armature and 0 in animated_axes):
            root.location.x -= cx
        if not (is_armature and 1 in animated_axes):
            root.location.y -= cy


def _create_empty(name: str, collection: bpy.types.Collection) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.12
    empty.hide_render = True
    empty.hide_select = True
    collection.objects.link(empty)
    return empty


MOTION_SAMPLE_STEP = 6


def _keyframe_pedestrian_motion(
    carrier: bpy.types.Object,
    path_points: list[Vector],
    frame_start: int,
    frame_end: int,
    phase_start: float,
    speed_per_frame: float,
) -> None:
    """Walk the carrier steadily along ``path_points`` at a constant speed.

    The carrier advances at ``speed_per_frame`` (world units / frame) without
    pausing, so every walker keeps moving the whole animation. Keyframes are
    sampled often enough (``MOTION_SAMPLE_STEP``) to follow road curves and keep
    the character facing its direction of travel.
    """

    loop_length = max(polyline_loop_length(path_points), 0.001)
    phase_per_frame = speed_per_frame / loop_length
    carrier.rotation_mode = "XYZ"

    def heading_at(phase: float) -> float:
        here = ecology_common._sample_path_point(path_points, phase % 1.0)
        ahead = ecology_common._sample_path_point(path_points, (phase + 0.0025) % 1.0)
        delta = ahead - here
        return math.atan2(delta.y, delta.x)

    def place(phase: float, frame: int) -> None:
        point = ecology_common._sample_path_point(path_points, phase % 1.0)
        carrier.location = Vector((point.x, point.y, point.z))
        carrier.rotation_euler = (0.0, 0.0, heading_at(phase))
        carrier.keyframe_insert(data_path="location", frame=frame)
        carrier.keyframe_insert(data_path="rotation_euler", frame=frame)

    phase = phase_start
    place(phase, frame_start)

    frame = frame_start
    while frame < frame_end:
        next_frame = min(frame + MOTION_SAMPLE_STEP, frame_end)
        phase += phase_per_frame * (next_frame - frame)
        place(phase, next_frame)
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
            _strip_root_motion(armature, action)
            add_cycles_modifier(action)

    bounds_objects = mesh_objects or new_objects
    merged = merge_bounds(object_world_bounds(obj) for obj in bounds_objects)
    world_height = max(merged[1].z - merged[0].z, 0.001) if merged is not None else DEFAULT_PERSON_HEIGHT

    # Pull the body onto the armature origin so instances land on their anchors.
    _center_template_horizontally(roots, armature, action, merged)

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
    base_speed = max(getattr(settings, "walk_speed", 0.2), 0.001)
    speed_variation = _clamp(getattr(settings, "walk_speed_variation", 0.3), 0.0, 0.9)

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
        )

        lateral = rng.uniform(-0.2, 0.2)
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
    near, far = normalize_band(settings.sidewalk_near, settings.sidewalk_far)
    road_paths = traffic_extension.extract_vehicle_road_paths_from_scene()
    if road_paths:
        routes = plan_sidewalk_routes(road_paths, near, far, z_lift)
        idle_spots = plan_idle_spots(road_paths, near, far, settings.idle_count, int(settings.seed), z_lift)
    else:
        center, city_radius, ground_z = get_city_bounds()
        routes = plan_fallback_loop_routes(center, city_radius, ground_z, near, far, z_lift)
        idle_spots = plan_fallback_idle_spots(
            center, city_radius, ground_z, near, far, settings.idle_count, z_lift
        )

    walkers = _spawn_walkers(routes, walk_template, walker_collection, path_collection, settings)
    idlers = _spawn_idlers(idle_spots, stand_template, idler_collection, settings)

    context.scene.frame_start = settings.animation_start
    context.scene.frame_end = settings.animation_end
    context.scene.frame_set(settings.animation_start)
    return {
        "walkers": walkers,
        "idlers": idlers,
        "used_road_graph": bool(road_paths),
        "near": near,
        "far": far,
    }


class ICITY_PedestrianSettings(PropertyGroup):
    animation_start: IntProperty(name="Start Frame", default=1, min=1, max=100000)
    animation_end: IntProperty(name="End Frame", default=250, min=2, max=100000)

    walker_count: IntProperty(name="Walkers", default=16, min=0, max=200)
    idle_count: IntProperty(name="Idlers", default=8, min=0, max=120)

    sidewalk_near: FloatProperty(
        name="Sidewalk Near",
        description="Nearest distance from the road centreline that pedestrians may walk (inner edge of the pavement)",
        default=6.3,
        min=0.0,
        max=40.0,
    )
    sidewalk_far: FloatProperty(
        name="Sidewalk Far",
        description="Farthest distance from the road centreline that pedestrians may walk (outer edge of the pavement)",
        default=6.8,
        min=0.0,
        max=40.0,
    )

    person_height: FloatProperty(name="Person Height (m)", default=DEFAULT_PERSON_HEIGHT, min=0.5, max=3.0)
    facing_offset_deg: FloatProperty(name="Facing Offset", default=90.0, min=-180.0, max=180.0)

    walk_speed: FloatProperty(
        name="Walk Speed",
        description="Walking speed in world units per frame (lower = slower)",
        default=0.2,
        min=0.005,
        max=0.5,
    )
    walk_speed_variation: FloatProperty(name="Speed Variation", default=0.3, min=0.0, max=0.9)
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
            (
                f"ICity pedestrians: {result['walkers']} walkers, {result['idlers']} idlers, {source}; "
                f"sidewalk band {result['near']:.1f}-{result['far']:.1f} m from road centre. "
                "Adjust 'Sidewalk Near/Far' to move them onto the pavement."
            ),
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
        layout_box.label(text="Sidewalk Band (from road centre)", icon="ORIENTATION_VIEW")
        layout_box.prop(settings, "sidewalk_near")
        layout_box.prop(settings, "sidewalk_far")

        move_box = layout.box()
        move_box.label(text="Movement", icon="FORCE_FORCE")
        move_box.prop(settings, "walk_speed")
        move_box.prop(settings, "walk_speed_variation")

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

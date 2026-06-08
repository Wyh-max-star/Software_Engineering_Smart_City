"""Standalone asset-expansion module for the ICity addon."""

from __future__ import annotations

import math
from pathlib import Path
from types import SimpleNamespace

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector


ICITY_ROOT_COLLECTION = "ICity"
ICITY_BASE_OBJECT = "ICity Base"
ICITY_ROAD_OBJECT = "ICity Road"
ICITY_ROAD_NODE_GROUP = "Road 2"
ICITY_MATERIAL_LIBRARY_OBJECT = "ICity_Materials"

ASSET_ROOT_COLLECTION = "ICity Asset Expansion"
ASSET_STREETLIGHT_COLLECTION = "ICity Asset Streetlights"
ASSET_ROADSIDE_COLLECTION = "ICity Roadside Props"

STREETLIGHT_MESH_NAME = "ICITY_ASSET_Streetlight_Mesh"
STREETLIGHT_METAL_MATERIAL = "ICITY_ASSET_Streetlight_Metal"
STREETLIGHT_EMISSION_MATERIAL = "ICITY_ASSET_Streetlight_Emission"

ICON_LIBRARY_SENTINEL = "generated_material_asset.blend"

SURFACE_ASSET_LIBRARY = {
    "ASPHALT_MARKED": {
        "material_name": "ICITY_ASSET_Asphalt_Marked",
        "label": "Asphalt Marked",
        "base": "Road 4 clean_BaseColor.jpg",
        "roughness": "Road 4 clean_Roughness.jpg",
        "normal": "Road 4 clean_Normal.jpg",
        "detail": "Road 4 clean_Height.jpg",
        "markings": "RoadLines010_2K-JPG_Opacity.jpg",
        "lane_color": (0.94, 0.91, 0.74, 1.0),
        "fallback_a": (0.09, 0.10, 0.11, 1.0),
        "fallback_b": (0.19, 0.19, 0.20, 1.0),
        "metallic": 0.02,
        "roughness_value": 0.67,
    },
    "CONCRETE_BOULEVARD": {
        "material_name": "ICITY_ASSET_Concrete_Boulevard",
        "label": "Concrete Boulevard",
        "base": "Concrete014_2K-JPG_Color.jpg",
        "roughness": "Concrete014_2K-JPG_Roughness.jpg",
        "normal": "Concrete014_2K-JPG_NormalGL.jpg",
        "detail": "Concrete014_2K-JPG_Displacement.jpg",
        "markings": "",
        "lane_color": (1.0, 1.0, 1.0, 1.0),
        "fallback_a": (0.44, 0.44, 0.43, 1.0),
        "fallback_b": (0.64, 0.63, 0.61, 1.0),
        "metallic": 0.0,
        "roughness_value": 0.82,
    },
    "BOARDWALK_WARM": {
        "material_name": "ICITY_ASSET_Boardwalk_Warm",
        "label": "Boardwalk Warm",
        "base": "1K-american_oak_2_basecolor-min.jpg",
        "roughness": "1K-american_oak_2_roughness-min.jpg",
        "normal": "1K-american_oak_2_normal-min.jpg",
        "detail": "1K-american_oak_2_ao-min.jpg",
        "markings": "",
        "lane_color": (1.0, 1.0, 1.0, 1.0),
        "fallback_a": (0.38, 0.28, 0.18, 1.0),
        "fallback_b": (0.57, 0.42, 0.27, 1.0),
        "metallic": 0.0,
        "roughness_value": 0.58,
    },
}

DIRECT_SURFACE_KEYWORDS = (
    "road",
    "street",
    "lane",
    "curb",
    "sidewalk",
    "walkway",
    "path",
    "crosswalk",
    "asphalt",
)

ROADSIDE_ASSET_LIBRARY = {
    "PLANTER": {
        "label": "Planter Box",
        "mesh_name": "ICITY_ASSET_Planter_Mesh",
        "material_name": "ICITY_ASSET_Planter_Material",
        "color": (0.46, 0.33, 0.24, 1.0),
    },
    "BOLLARD": {
        "label": "Bollard Cluster",
        "mesh_name": "ICITY_ASSET_Bollard_Mesh",
        "material_name": "ICITY_ASSET_Bollard_Material",
        "color": (0.18, 0.19, 0.21, 1.0),
    },
    "BENCH": {
        "label": "Bench Variant",
        "mesh_name": "ICITY_ASSET_Bench_Mesh",
        "material_name": "ICITY_ASSET_Bench_Material",
        "color": (0.52, 0.39, 0.24, 1.0),
    },
    "BUS_STOP": {
        "label": "Bus Stop Sign",
        "mesh_name": "ICITY_ASSET_BusStop_Mesh",
        "material_name": "ICITY_ASSET_BusStop_Material",
        "color": (0.14, 0.39, 0.69, 1.0),
    },
}

ROAD_ASSET_NODE_SPECS = {
    "STREETLIGHT": {
        "node_name": "Light",
        "placement_mode": "OBJECT",
        "asset_input_index": 4,
        "spacing_input_index": 10,
        "lateral_offset_input_index": 11,
        "depth_offset_input_index": 12,
        "visibility_inputs": ("Light V", "Light R"),
    },
    "BENCH": {
        "node_name": "Bench",
        "placement_mode": "OBJECT",
        "asset_input_index": 4,
        "spacing_input_index": 10,
        "lateral_offset_input_index": 11,
        "depth_offset_input_index": 12,
        "visibility_inputs": ("Bench V", "Bench R"),
    },
    "BOLLARD": {
        "node_name": "Bollard",
        "placement_mode": "OBJECT",
        "asset_input_index": 4,
        "spacing_input_index": 10,
        "lateral_offset_input_index": 11,
        "depth_offset_input_index": 12,
        "visibility_inputs": ("Bollard V", "Bollard R"),
    },
}


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def road_asset_spec_for_style(style_key: str) -> dict | None:
    return ROAD_ASSET_NODE_SPECS.get(style_key)


def road_asset_node_available(node_group, spec: dict | None) -> bool:
    if node_group is None or spec is None:
        return False
    nodes = getattr(node_group, "nodes", None)
    if nodes is None:
        return False
    node = nodes.get(spec["node_name"])
    if node is None:
        return False

    required_indexes = [spec["asset_input_index"]]
    for key in ("spacing_input_index", "lateral_offset_input_index", "depth_offset_input_index"):
        index = spec.get(key)
        if index is not None:
            required_indexes.append(index)
    return len(getattr(node, "inputs", [])) > max(required_indexes)


def road_asset_styles_for_scope(scope: str, roadside_style: str | None = None) -> tuple[str, ...]:
    if scope == "STREETLIGHT":
        return ("STREETLIGHT",)
    if scope != "ROADSIDE":
        return tuple()
    if roadside_style in {"BENCH", "BOLLARD"}:
        return (roadside_style,)
    if roadside_style in {None, "MIXED"}:
        return ("BENCH", "BOLLARD")
    return tuple()


def ensure_principled_input(node: bpy.types.Node, socket_names, value) -> None:
    for socket_name in socket_names:
        socket = node.inputs.get(socket_name)
        if socket is not None:
            socket.default_value = value
            return


def addon_directory() -> Path:
    return Path(__file__).resolve().parents[1]


def texture_directory() -> Path:
    return addon_directory() / "assets" / "textures"


def texture_directories() -> tuple[Path, ...]:
    return (
        texture_directory(),
        addon_directory() / "assets" / "Assets" / "Default" / "textures",
    )


def icon_hint_path() -> str:
    return str(addon_directory() / "assets" / "icons" / ICON_LIBRARY_SENTINEL)


def get_texture_path(filename: str) -> Path | None:
    if not filename:
        return None
    for directory in texture_directories():
        path = directory / filename
        if path.exists():
            return path
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        matches = sorted(directory.glob(f"{stem}*{suffix}"))
        if matches:
            return matches[0]
    return None


def load_image(filepath: Path | None, colorspace: str) -> bpy.types.Image | None:
    if filepath is None:
        return None
    image = bpy.data.images.load(str(filepath), check_existing=True)
    try:
        image.colorspace_settings.name = colorspace
    except TypeError:
        pass
    return image


def get_or_create_material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    return material


def build_flat_material(name: str, color: tuple[float, float, float, float], *, metallic: float = 0.0, roughness: float = 0.55) -> bpy.types.Material:
    material = get_or_create_material(name)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (240, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (20, 0)
    bsdf.inputs["Base Color"].default_value = color
    ensure_principled_input(bsdf, ("Metallic",), metallic)
    ensure_principled_input(bsdf, ("Roughness",), roughness)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def configure_texture_mapping(mapping: bpy.types.Node, uv_scale: float) -> None:
    mapping.inputs["Scale"].default_value = (uv_scale, uv_scale, uv_scale)


def add_fallback_surface_nodes(
    nodes: bpy.types.Nodes,
    links: bpy.types.NodeLinks,
    bsdf: bpy.types.Node,
    uv_scale: float,
    config: dict,
    use_markings: bool,
) -> None:
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-820, 0)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-620, 0)
    configure_texture_mapping(mapping, uv_scale)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, 40)
    noise.inputs["Scale"].default_value = 7.0
    noise.inputs["Detail"].default_value = 12.0
    noise.inputs["Roughness"].default_value = 0.6

    detail = nodes.new("ShaderNodeTexWave")
    detail.location = (-400, -180)
    detail.inputs["Scale"].default_value = 18.0
    detail.inputs["Distortion"].default_value = 1.6
    detail.bands_direction = "DIAGONAL"

    mix = nodes.new("ShaderNodeMixRGB")
    mix.location = (-180, 20)
    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = config["fallback_a"]
    mix.inputs["Color2"].default_value = config["fallback_b"]

    bump = nodes.new("ShaderNodeBump")
    bump.location = (-160, -180)
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.04

    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(mapping.outputs["Vector"], detail.inputs["Vector"])
    links.new(noise.outputs["Fac"], mix.inputs["Fac"])
    links.new(detail.outputs["Color"], bump.inputs["Height"])

    if use_markings:
        stripe = nodes.new("ShaderNodeTexWave")
        stripe.location = (-400, 260)
        stripe.wave_type = "BANDS"
        stripe.bands_direction = "Y"
        stripe.inputs["Scale"].default_value = 3.5
        stripe.inputs["Distortion"].default_value = 0.0

        stripe_ramp = nodes.new("ShaderNodeValToRGB")
        stripe_ramp.location = (-180, 260)
        stripe_ramp.color_ramp.elements[0].position = 0.46
        stripe_ramp.color_ramp.elements[1].position = 0.54

        stripe_mix = nodes.new("ShaderNodeMixRGB")
        stripe_mix.location = (40, 100)
        stripe_mix.inputs["Color2"].default_value = config["lane_color"]

        links.new(mapping.outputs["Vector"], stripe.inputs["Vector"])
        links.new(stripe.outputs["Color"], stripe_ramp.inputs["Fac"])
        links.new(stripe_ramp.outputs["Color"], stripe_mix.inputs["Fac"])
        links.new(mix.outputs["Color"], stripe_mix.inputs["Color1"])
        links.new(stripe_mix.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def build_surface_material(settings, style_key: str) -> bpy.types.Material:
    config = SURFACE_ASSET_LIBRARY[style_key]
    material = get_or_create_material(config["material_name"])
    if hasattr(material, "sna_asset_category_path_material"):
        material.sna_asset_category_path_material = icon_hint_path()
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (760, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (520, 0)
    ensure_principled_input(bsdf, ("Metallic",), config["metallic"])
    ensure_principled_input(bsdf, ("Roughness",), config["roughness_value"])

    images = {
        "base": load_image(get_texture_path(config["base"]), "sRGB"),
        "roughness": load_image(get_texture_path(config["roughness"]), "Non-Color"),
        "normal": load_image(get_texture_path(config["normal"]), "Non-Color"),
        "detail": load_image(get_texture_path(config["detail"]), "Non-Color"),
        "markings": load_image(get_texture_path(config["markings"]), "Non-Color"),
    }

    use_fallback = images["base"] is None
    use_markings = bool(settings.enable_lane_markings and images["markings"] is not None and style_key == "ASPHALT_MARKED")

    if use_fallback:
        add_fallback_surface_nodes(
            nodes,
            links,
            bsdf,
            settings.texture_uv_scale,
            config,
            style_key == "ASPHALT_MARKED" and settings.enable_lane_markings,
        )
    else:
        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = (-980, 0)

        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (-780, 0)
        configure_texture_mapping(mapping, settings.texture_uv_scale)

        base_tex = nodes.new("ShaderNodeTexImage")
        base_tex.location = (-560, 120)
        base_tex.image = images["base"]
        base_tex.interpolation = "Smart"

        roughness_tex = nodes.new("ShaderNodeTexImage")
        roughness_tex.location = (-560, -80)
        roughness_tex.image = images["roughness"]
        roughness_tex.interpolation = "Smart"

        normal_tex = nodes.new("ShaderNodeTexImage")
        normal_tex.location = (-560, -280)
        normal_tex.image = images["normal"]
        normal_tex.interpolation = "Smart"

        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.location = (-320, -280)
        normal_map.inputs["Strength"].default_value = settings.texture_normal_strength

        links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], base_tex.inputs["Vector"])
        links.new(mapping.outputs["Vector"], roughness_tex.inputs["Vector"])
        links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])

        if images["detail"] is not None:
            detail_tex = nodes.new("ShaderNodeTexImage")
            detail_tex.location = (-560, 300)
            detail_tex.image = images["detail"]
            detail_tex.interpolation = "Smart"

            detail_ramp = nodes.new("ShaderNodeValToRGB")
            detail_ramp.location = (-320, 300)
            detail_ramp.color_ramp.elements[0].position = 0.28
            detail_ramp.color_ramp.elements[1].position = 0.78

            color_mix = nodes.new("ShaderNodeMixRGB")
            color_mix.location = (-80, 140)
            color_mix.blend_type = "MULTIPLY"
            color_mix.inputs["Fac"].default_value = 0.18

            links.new(mapping.outputs["Vector"], detail_tex.inputs["Vector"])
            links.new(detail_tex.outputs["Color"], detail_ramp.inputs["Fac"])
            links.new(detail_ramp.outputs["Color"], color_mix.inputs["Color2"])
            links.new(base_tex.outputs["Color"], color_mix.inputs["Color1"])
            base_color_output = color_mix.outputs["Color"]
        else:
            base_color_output = base_tex.outputs["Color"]

        if use_markings:
            mask_ramp = nodes.new("ShaderNodeValToRGB")
            mask_ramp.location = (-320, 520)
            mask_ramp.color_ramp.elements[0].position = 0.18
            mask_ramp.color_ramp.elements[1].position = 0.8

            markings_tex = nodes.new("ShaderNodeTexImage")
            markings_tex.location = (-560, 520)
            markings_tex.image = images["markings"]
            markings_tex.interpolation = "Closest"

            markings_mix = nodes.new("ShaderNodeMixRGB")
            markings_mix.location = (140, 140)
            markings_mix.inputs["Color2"].default_value = config["lane_color"]

            links.new(mapping.outputs["Vector"], markings_tex.inputs["Vector"])
            links.new(markings_tex.outputs["Color"], mask_ramp.inputs["Fac"])
            links.new(mask_ramp.outputs["Color"], markings_mix.inputs["Fac"])
            links.new(base_color_output, markings_mix.inputs["Color1"])
            links.new(markings_mix.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            links.new(base_color_output, bsdf.inputs["Base Color"])

        if images["roughness"] is not None:
            links.new(roughness_tex.outputs["Color"], bsdf.inputs["Roughness"])
        if images["normal"] is not None:
            links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def material_already_registered(material: bpy.types.Material) -> bool:
    material_library = bpy.data.objects.get(ICITY_MATERIAL_LIBRARY_OBJECT)
    if material_library is None or not hasattr(material_library.data, "materials"):
        return False
    return any(slot_material and slot_material.name == material.name for slot_material in material_library.data.materials)


def register_material_in_icity_library(material: bpy.types.Material) -> bool:
    material_library = bpy.data.objects.get(ICITY_MATERIAL_LIBRARY_OBJECT)
    if material_library is None or not hasattr(material_library.data, "materials"):
        return False
    if material_already_registered(material):
        return True
    material_library.data.materials.append(material)
    return True


def assign_material_to_road_system(material: bpy.types.Material, slot_name: str) -> bool:
    node_group = bpy.data.node_groups.get(ICITY_ROAD_NODE_GROUP)
    if node_group is None:
        return False
    node = node_group.nodes.get(slot_name)
    if node is None or len(node.inputs) < 3:
        return False
    node.inputs[2].default_value = material
    road_object = bpy.data.objects.get(ICITY_ROAD_OBJECT)
    if road_object is not None:
        road_object.update_tag(refresh={"DATA"})
    return True


def assign_material_to_object_data(
    obj: bpy.types.Object,
    material: bpy.types.Material,
    replace_all_slots: bool,
) -> bool:
    if obj.type not in {"MESH", "CURVE", "SURFACE", "FONT"}:
        return False
    data = getattr(obj, "data", None)
    if data is None or not hasattr(data, "materials"):
        return False
    materials = data.materials
    if len(materials) == 0:
        materials.append(material)
        return True
    if replace_all_slots:
        for index in range(len(materials)):
            materials[index] = material
    else:
        materials[0] = material
    obj.update_tag(refresh={"DATA"})
    return True


def discover_surface_targets(context: bpy.types.Context, target_mode: str) -> list[bpy.types.Object]:
    if target_mode == "SELECTED":
        return [obj for obj in context.selected_objects if obj.type in {"MESH", "CURVE", "SURFACE", "FONT"}]

    root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root_collection is None:
        return [obj for obj in context.selected_objects if obj.type in {"MESH", "CURVE", "SURFACE", "FONT"}]

    candidates = []
    for obj in root_collection.all_objects:
        if obj.type not in {"MESH", "CURVE", "SURFACE", "FONT"}:
            continue
        name = obj.name.lower()
        if any(keyword in name for keyword in DIRECT_SURFACE_KEYWORDS):
            candidates.append(obj)
            continue
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group is not None:
                if "road" in modifier.node_group.name.lower():
                    candidates.append(obj)
                    break
    unique_by_name = {}
    for obj in candidates:
        unique_by_name[obj.name] = obj
    return list(unique_by_name.values())


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


def get_city_bounds() -> tuple[Vector, float, float]:
    base_object = bpy.data.objects.get(ICITY_BASE_OBJECT)
    if base_object is not None:
        min_corner, max_corner = object_world_bounds(base_object)
    else:
        root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
        if root_collection is None or len(root_collection.all_objects) == 0:
            return Vector((0.0, 0.0, 0.0)), 28.0, 0.0
        bounds = [
            object_world_bounds(obj)
            for obj in root_collection.all_objects
            if obj.type in {"MESH", "CURVE", "SURFACE", "FONT"}
        ]
        if not bounds:
            return Vector((0.0, 0.0, 0.0)), 28.0, 0.0
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
    center = (min_corner + max_corner) * 0.5
    radius = max(max_corner.x - min_corner.x, max_corner.y - min_corner.y) * 0.5
    return center, max(radius, 20.0), min_corner.z


def get_or_create_child_collection(parent: bpy.types.Collection, name: str) -> bpy.types.Collection:
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
    elif isinstance(data, bpy.types.Light):
        bpy.data.lights.remove(data)


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


def clear_collection_contents(collection_name: str) -> None:
    collection = bpy.data.collections.get(collection_name)
    if collection is not None:
        remove_collection_recursive(collection)


def get_asset_root_collection() -> bpy.types.Collection:
    root = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root is None:
        root = bpy.context.scene.collection
    return get_or_create_child_collection(root, ASSET_ROOT_COLLECTION)


def get_road_node_group():
    return bpy.data.node_groups.get(ICITY_ROAD_NODE_GROUP)


def get_road_object():
    return bpy.data.objects.get(ICITY_ROAD_OBJECT)


def get_road_geometry_nodes_modifier():
    road_object = get_road_object()
    if road_object is None:
        return None
    for modifier in getattr(road_object, "modifiers", []):
        if modifier.type != "NODES":
            continue
        if modifier.node_group is None:
            continue
        if modifier.node_group.name == ICITY_ROAD_NODE_GROUP:
            return modifier
    return None


def set_modifier_interface_bool(modifier, input_name: str, value: bool) -> bool:
    if modifier is None or modifier.node_group is None:
        return False
    items_tree = getattr(modifier.node_group.interface, "items_tree", None)
    if items_tree is None:
        return False
    interface_item = items_tree.get(input_name)
    if interface_item is None:
        return False
    modifier[interface_item.identifier] = value
    return True


def enable_road_asset_visibility(spec: dict | None) -> None:
    if spec is None:
        return
    modifier = get_road_geometry_nodes_modifier()
    if modifier is None:
        return
    for input_name in spec.get("visibility_inputs", ()):
        set_modifier_interface_bool(modifier, input_name, True)


def clear_road_asset_assignments() -> None:
    clear_scoped_road_asset_assignments(tuple(ROAD_ASSET_NODE_SPECS.keys()))


def clear_scoped_road_asset_assignments(style_keys: tuple[str, ...]) -> None:
    node_group = get_road_node_group()
    if node_group is None:
        return
    for style_key in style_keys:
        spec = road_asset_spec_for_style(style_key)
        if spec is None:
            continue
        node = node_group.nodes.get(spec["node_name"])
        if node is None or len(node.inputs) <= spec["asset_input_index"]:
            continue
        node.inputs[spec["asset_input_index"]].default_value = None
    road_object = get_road_object()
    if road_object is not None:
        road_object.update_tag(refresh={"DATA"})


def clear_streetlights() -> None:
    clear_collection_contents(ASSET_STREETLIGHT_COLLECTION)


def clear_roadside_assets(roadside_style: str | None = None) -> None:
    clear_collection_contents(ASSET_ROADSIDE_COLLECTION)


def estimated_spacing_from_count(radius: float, count: int, minimum: float) -> float:
    safe_radius = max(radius, 1.0)
    safe_count = max(count, 1)
    return max(minimum, (2.0 * math.pi * safe_radius) / safe_count)


def estimated_lateral_offset(user_offset: float, minimum: float, maximum: float) -> float:
    return clamp(user_offset * 0.25, minimum, maximum)


def configure_road_asset_node(node, spec: dict, asset_value, spacing: float, lateral_offset: float, depth_offset: float) -> None:
    node.inputs[spec["asset_input_index"]].default_value = asset_value
    node.inputs[spec["spacing_input_index"]].default_value = spacing
    node.inputs[spec["lateral_offset_input_index"]].default_value = lateral_offset
    node.inputs[spec["depth_offset_input_index"]].default_value = depth_offset


def create_streetlight_source_object(collection: bpy.types.Collection, mesh: bpy.types.Mesh, settings) -> bpy.types.Object:
    obj = bpy.data.objects.new("ICITY_ASSET_Streetlight_Source", mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.hide_viewport = True
    obj.hide_render = True
    collection.objects.link(obj)

    bevel = obj.modifiers.new(name="ICITY_ASSET_Bevel", type="BEVEL")
    bevel.width = 0.02
    bevel.segments = 2

    light_data = bpy.data.lights.new(name="ICITY_ASSET_Streetlight_Source_Light", type="POINT")
    light_data.energy = settings.streetlight_light_power
    light_data.shadow_soft_size = 0.45
    light_data.color = (1.0, 0.88, 0.72)
    light_object = bpy.data.objects.new(light_data.name, light_data)
    light_object.parent = obj
    light_object.location = (settings.streetlight_arm_length - 0.08, 0.0, settings.streetlight_height - 0.34)
    light_object.hide_viewport = True
    light_object.hide_render = True
    collection.objects.link(light_object)
    return obj


def try_generate_streetlights_on_road_system(collection: bpy.types.Collection, radius: float, settings) -> bool:
    spec = road_asset_spec_for_style("STREETLIGHT")
    node_group = get_road_node_group()
    if not road_asset_node_available(node_group, spec):
        return False

    metal_material, emission_material = build_streetlight_materials(settings)
    mesh = build_streetlight_mesh(settings)
    mesh.materials.clear()
    mesh.materials.append(metal_material)
    mesh.materials.append(emission_material)
    source_object = create_streetlight_source_object(collection, mesh, settings)

    node = node_group.nodes.get(spec["node_name"])
    spacing = estimated_spacing_from_count(radius, settings.streetlight_count, 6.0)
    lateral_offset = estimated_lateral_offset(settings.streetlight_offset, 0.8, 4.0)
    configure_road_asset_node(
        node,
        spec,
        source_object,
        spacing,
        lateral_offset,
        settings.streetlight_base_z_offset,
    )
    enable_road_asset_visibility(spec)

    road_object = get_road_object()
    if road_object is not None:
        road_object.update_tag(refresh={"DATA"})
    return True


def try_generate_roadside_assets_on_road_system(collection: bpy.types.Collection, style_key: str, radius: float, settings) -> bool:
    spec = road_asset_spec_for_style(style_key)
    node_group = get_road_node_group()
    if not road_asset_node_available(node_group, spec):
        return False

    mesh = _build_roadside_prop_mesh(style_key)
    mesh.materials.clear()
    mesh.materials.append(build_roadside_prop_material(style_key))
    source_object = bpy.data.objects.new(f"ICITY_ASSET_{style_key}_Source", mesh)
    source_object.location = (0.0, 0.0, 0.0)
    source_object.hide_viewport = True
    source_object.hide_render = True
    source_object.scale = (settings.roadside_asset_scale, settings.roadside_asset_scale, settings.roadside_asset_scale)
    collection.objects.link(source_object)

    node = node_group.nodes.get(spec["node_name"])
    spacing = estimated_spacing_from_count(radius, settings.roadside_asset_count, 4.0)
    lateral_offset = estimated_lateral_offset(settings.roadside_asset_offset, 0.4, 3.0)
    configure_road_asset_node(node, spec, source_object, spacing, lateral_offset, 0.0)
    enable_road_asset_visibility(spec)

    road_object = get_road_object()
    if road_object is not None:
        road_object.update_tag(refresh={"DATA"})
    return True


def append_box(
    vertices: list[tuple[float, float, float]],
    face_data: list[tuple[tuple[int, ...], int]],
    min_corner: tuple[float, float, float],
    max_corner: tuple[float, float, float],
    material_index: int,
) -> None:
    x0, y0, z0 = min_corner
    x1, y1, z1 = max_corner
    start = len(vertices)
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
    faces = (
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    )
    for face in faces:
        face_data.append((tuple(start + index for index in face), material_index))


def build_streetlight_materials(settings) -> tuple[bpy.types.Material, bpy.types.Material]:
    metal = get_or_create_material(STREETLIGHT_METAL_MATERIAL)
    metal_nodes = metal.node_tree.nodes
    metal_links = metal.node_tree.links
    metal_nodes.clear()

    metal_output = metal_nodes.new("ShaderNodeOutputMaterial")
    metal_output.location = (260, 0)

    metal_bsdf = metal_nodes.new("ShaderNodeBsdfPrincipled")
    metal_bsdf.location = (40, 0)
    metal_bsdf.inputs["Base Color"].default_value = (0.11, 0.12, 0.13, 1.0)
    ensure_principled_input(metal_bsdf, ("Metallic",), 0.82)
    ensure_principled_input(metal_bsdf, ("Roughness",), 0.33)
    metal_links.new(metal_bsdf.outputs["BSDF"], metal_output.inputs["Surface"])

    lamp = get_or_create_material(STREETLIGHT_EMISSION_MATERIAL)
    lamp_nodes = lamp.node_tree.nodes
    lamp_links = lamp.node_tree.links
    lamp_nodes.clear()

    lamp_output = lamp_nodes.new("ShaderNodeOutputMaterial")
    lamp_output.location = (240, 0)

    emission = lamp_nodes.new("ShaderNodeEmission")
    emission.location = (20, 0)
    emission.inputs["Color"].default_value = (1.0, 0.88, 0.68, 1.0)
    emission.inputs["Strength"].default_value = settings.streetlight_emission_strength
    lamp_links.new(emission.outputs["Emission"], lamp_output.inputs["Surface"])
    return metal, lamp


def build_streetlight_mesh(settings) -> bpy.types.Mesh:
    existing = bpy.data.meshes.get(STREETLIGHT_MESH_NAME)
    if existing is not None and existing.users == 0:
        bpy.data.meshes.remove(existing)

    mesh = bpy.data.meshes.new(STREETLIGHT_MESH_NAME)
    vertices: list[tuple[float, float, float]] = []
    face_data: list[tuple[tuple[int, ...], int]] = []

    pole_half = 0.085
    base_half = 0.2
    height = settings.streetlight_height
    arm_length = clamp(settings.streetlight_arm_length, 0.6, 2.6)
    lamp_z = max(0.6, height - 0.22)

    append_box(vertices, face_data, (-base_half, -base_half, 0.0), (base_half, base_half, 0.18), 0)
    append_box(vertices, face_data, (-pole_half, -pole_half, 0.18), (pole_half, pole_half, height), 0)
    append_box(vertices, face_data, (0.0, -0.05, height - 0.08), (arm_length, 0.05, height), 0)
    append_box(vertices, face_data, (arm_length - 0.2, -0.12, lamp_z - 0.07), (arm_length + 0.08, 0.12, lamp_z + 0.07), 0)
    append_box(vertices, face_data, (arm_length - 0.15, -0.09, lamp_z - 0.16), (arm_length + 0.02, 0.09, lamp_z - 0.1), 1)

    mesh.from_pydata(vertices, [], [face for face, _ in face_data])
    mesh.update()
    for polygon, (_, material_index) in zip(mesh.polygons, face_data):
        polygon.material_index = material_index
    return mesh


def create_streetlight_instance(
    collection: bpy.types.Collection,
    mesh: bpy.types.Mesh,
    location: Vector,
    rotation_z: float,
    index: int,
    settings,
) -> None:
    obj = bpy.data.objects.new(f"ICITY_ASSET_Streetlight_{index:03d}", mesh)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rotation_z)
    collection.objects.link(obj)

    bevel = obj.modifiers.new(name="ICITY_ASSET_Bevel", type="BEVEL")
    bevel.width = 0.02
    bevel.segments = 2

    light_data = bpy.data.lights.new(name=f"ICITY_ASSET_Streetlight_Light_{index:03d}", type="POINT")
    light_data.energy = settings.streetlight_light_power
    light_data.shadow_soft_size = 0.45
    light_data.color = (1.0, 0.88, 0.72)
    light_object = bpy.data.objects.new(light_data.name, light_data)
    light_object.parent = obj
    light_object.location = (settings.streetlight_arm_length - 0.08, 0.0, settings.streetlight_height - 0.34)
    collection.objects.link(light_object)


def point_in_city_core(point: Vector, center: Vector, radius: float) -> bool:
    local_x = abs(point.x - center.x)
    local_y = abs(point.y - center.y)
    return local_x < radius * 0.78 and local_y < radius * 0.58


def _perimeter_positions(center: Vector, half_x: float, half_y: float, count: int, base_z: float) -> list[tuple[Vector, float]]:
    width = half_x * 2.0
    depth = half_y * 2.0
    perimeter = (width + depth) * 2.0
    spacing = perimeter / max(1, count)
    positions = []

    for index in range(max(1, count)):
        distance = index * spacing
        if distance < width:
            x = center.x - half_x + distance
            y = center.y - half_y
            rotation = math.pi * 0.5
        elif distance < width + depth:
            x = center.x + half_x
            y = center.y - half_y + (distance - width)
            rotation = math.pi
        elif distance < (width * 2.0) + depth:
            x = center.x + half_x - (distance - width - depth)
            y = center.y + half_y
            rotation = -math.pi * 0.5
        else:
            x = center.x - half_x
            y = center.y + half_y - (distance - width - depth - width)
            rotation = 0.0
        positions.append((Vector((x, y, base_z)), rotation))
    return positions


def perimeter_positions(center: Vector, radius: float, settings) -> list[tuple[Vector, float]]:
    lateral_offset = max(settings.streetlight_offset * 0.55, radius * 0.10)
    half_x = radius + max(settings.streetlight_offset, radius * 0.12)
    half_y = max(radius * 0.72 + settings.streetlight_offset, radius + lateral_offset)
    return _perimeter_positions(
        center,
        half_x,
        half_y,
        max(1, settings.streetlight_count),
        settings.streetlight_base_z_offset,
    )


def _downsample_positions(positions: list[tuple[Vector, float]], count: int) -> list[tuple[Vector, float]]:
    if len(positions) <= count:
        return positions
    sampled = []
    for index in range(count):
        sample_index = int(round(index * (len(positions) - 1) / max(1, count - 1)))
        sampled.append(positions[sample_index])
    return sampled


def filtered_perimeter_positions(center: Vector, radius: float, settings) -> list[tuple[Vector, float]]:
    candidate_count = max(settings.streetlight_count * 3, 24)
    candidate_offset = max(settings.streetlight_offset, radius * 0.18)
    candidate_half_x = radius + candidate_offset
    candidate_half_y = max(radius * 0.84 + candidate_offset, radius + candidate_offset * 0.62)
    candidates = _perimeter_positions(
        center,
        candidate_half_x,
        candidate_half_y,
        candidate_count,
        settings.streetlight_base_z_offset,
    )
    filtered = [(point, rotation) for point, rotation in candidates if not point_in_city_core(point, center, radius)]
    if len(filtered) < settings.streetlight_count:
        filtered = perimeter_positions(center, radius, settings)
    return _downsample_positions(filtered, max(1, settings.streetlight_count))


def streetlight_positions_with_fallback(
    center: Vector,
    radius: float,
    settings,
    *,
    anchor_candidates: list[tuple[Vector, float]] | None = None,
    road_node_supported: bool = False,
) -> list[tuple[Vector, float]]:
    if road_node_supported and anchor_candidates:
        return _downsample_positions(anchor_candidates, max(1, settings.streetlight_count))
    return filtered_perimeter_positions(center, radius, settings)


def roadside_prop_positions(center: Vector, radius: float, settings) -> list[tuple[Vector, float]]:
    proxy = SimpleNamespace(
        streetlight_offset=max(settings.roadside_asset_offset + radius * 0.12, radius * 0.32),
        streetlight_count=settings.roadside_asset_count,
        streetlight_base_z_offset=0.0,
    )
    return filtered_perimeter_positions(center, radius, proxy)


def build_roadside_prop_material(style_key: str) -> bpy.types.Material:
    config = ROADSIDE_ASSET_LIBRARY[style_key]
    metallic = 0.0 if style_key in {"PLANTER", "BENCH"} else 0.18
    roughness = 0.62 if style_key == "PLANTER" else 0.48
    return build_flat_material(config["material_name"], config["color"], metallic=metallic, roughness=roughness)


def _build_roadside_prop_mesh(style_key: str) -> bpy.types.Mesh:
    config = ROADSIDE_ASSET_LIBRARY[style_key]
    existing = bpy.data.meshes.get(config["mesh_name"])
    if existing is not None and existing.users == 0:
        bpy.data.meshes.remove(existing)

    mesh = bpy.data.meshes.new(config["mesh_name"])
    vertices: list[tuple[float, float, float]] = []
    face_data: list[tuple[tuple[int, ...], int]] = []

    if style_key == "PLANTER":
        append_box(vertices, face_data, (-0.62, -0.24, 0.0), (0.62, 0.24, 0.52), 0)
        append_box(vertices, face_data, (-0.48, -0.14, 0.52), (0.48, 0.14, 0.86), 0)
    elif style_key == "BOLLARD":
        for x in (-0.32, 0.0, 0.32):
            append_box(vertices, face_data, (x - 0.06, -0.06, 0.0), (x + 0.06, 0.06, 0.88), 0)
    elif style_key == "BENCH":
        append_box(vertices, face_data, (-0.68, -0.18, 0.46), (0.68, 0.18, 0.60), 0)
        append_box(vertices, face_data, (-0.68, 0.12, 0.60), (0.68, 0.24, 1.02), 0)
        for x in (-0.46, 0.46):
            append_box(vertices, face_data, (x - 0.05, -0.14, 0.0), (x + 0.05, 0.14, 0.46), 0)
    else:
        append_box(vertices, face_data, (-0.06, -0.06, 0.0), (0.06, 0.06, 1.56), 0)
        append_box(vertices, face_data, (-0.50, -0.08, 1.18), (0.50, 0.08, 1.32), 0)
        append_box(vertices, face_data, (0.18, -0.28, 0.70), (0.56, -0.12, 1.22), 0)

    mesh.from_pydata(vertices, [], [face for face, _ in face_data])
    mesh.update()
    for polygon, (_, material_index) in zip(mesh.polygons, face_data):
        polygon.material_index = material_index
    return mesh


def create_roadside_prop_instance(
    collection: bpy.types.Collection,
    mesh: bpy.types.Mesh,
    location: Vector,
    rotation_z: float,
    index: int,
    style_key: str,
    scale: float,
) -> None:
    obj = bpy.data.objects.new(f"ICITY_ASSET_{style_key}_{index:03d}", mesh)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rotation_z)
    obj.scale = (scale, scale, scale)
    collection.objects.link(obj)


def roadside_style_keys(settings) -> list[str]:
    if settings.roadside_asset_style == "MIXED":
        return list(ROADSIDE_ASSET_LIBRARY.keys())
    return [settings.roadside_asset_style]


class ICITY_AssetSettings(PropertyGroup):
    surface_style: EnumProperty(
        name="Surface Style",
        description="新添加的 2D 纹理资产方案",
        items=[
            ("ASPHALT_MARKED", "Asphalt Marked", "带道路标线的沥青纹理"),
            ("CONCRETE_BOULEVARD", "Concrete Boulevard", "城市混凝土道路纹理"),
            ("BOARDWALK_WARM", "Boardwalk Warm", "暖色木质步道纹理"),
        ],
        default="ASPHALT_MARKED",
    )
    surface_target_mode: EnumProperty(
        name="Apply Target",
        description="纹理资产替换目标",
        items=[
            ("ROAD_SYSTEM", "ICity Road System", "优先写入原 ICity 的道路节点材质槽"),
            ("AUTO_DISCOVERY", "Auto Discover", "自动搜索 ICity 中的道路/步道对象"),
            ("SELECTED", "Selected Objects", "只替换当前选中的对象"),
        ],
        default="ROAD_SYSTEM",
    )
    surface_slot: EnumProperty(
        name="Road Slot",
        description="写回原 ICity 道路系统时替换哪个材质槽",
        items=[
            ("Road", "Road", "道路主材质"),
            ("Curb", "Curb", "路沿材质"),
            ("Sidewalk", "Sidewalk", "步道材质"),
        ],
        default="Road",
    )
    texture_uv_scale: FloatProperty(
        name="Texture Scale",
        description="纹理平铺密度",
        default=3.2,
        min=0.4,
        max=20.0,
    )
    texture_normal_strength: FloatProperty(
        name="Normal Strength",
        description="法线强度",
        default=0.85,
        min=0.0,
        max=4.0,
    )
    enable_lane_markings: BoolProperty(
        name="Enable Lane Markings",
        description="在沥青材质上叠加道路标线纹理",
        default=True,
    )
    replace_all_slots: BoolProperty(
        name="Replace All Slots",
        description="直接替换对象上的全部材质槽",
        default=False,
    )
    add_to_icity_material_library: BoolProperty(
        name="Register In ICity",
        description="把新材质注册到 ICity_Materials，便于原系统继续识别",
        default=True,
    )
    streetlight_count: IntProperty(
        name="Streetlight Count",
        description="批量生成的路灯数量",
        default=20,
        min=4,
        max=200,
    )
    streetlight_offset: FloatProperty(
        name="Streetlight Offset",
        description="路灯相对城市边界向外偏移的距离",
        default=7.5,
        min=1.0,
        max=80.0,
    )
    streetlight_height: FloatProperty(
        name="Streetlight Height",
        description="路灯高度",
        default=5.8,
        min=2.5,
        max=18.0,
    )
    streetlight_arm_length: FloatProperty(
        name="Arm Length",
        description="路灯横臂长度",
        default=1.35,
        min=0.4,
        max=3.0,
    )
    streetlight_light_power: FloatProperty(
        name="Lamp Power",
        description="点光源强度",
        default=950.0,
        min=0.0,
        max=50000.0,
    )
    streetlight_emission_strength: FloatProperty(
        name="Glow Strength",
        description="灯罩自发光强度",
        default=7.5,
        min=0.0,
        max=100.0,
    )
    streetlight_base_z_offset: FloatProperty(
        name="Base Z Offset",
        description="整体路灯底座的高度偏移",
        default=0.0,
        min=-5.0,
        max=20.0,
    )
    roadside_asset_style: EnumProperty(
        name="Roadside Style",
        description="Roadside support asset style",
        items=[
            ("MIXED", "Mixed", "Generate a mixed batch of roadside assets"),
            ("PLANTER", "Planter Box", "Generate planter boxes"),
            ("BOLLARD", "Bollard Cluster", "Generate bollard clusters"),
            ("BENCH", "Bench Variant", "Generate benches"),
            ("BUS_STOP", "Bus Stop Sign", "Generate bus stop signs"),
        ],
        default="MIXED",
    )
    roadside_asset_count: IntProperty(
        name="Roadside Count",
        description="Number of roadside support assets to place",
        default=12,
        min=4,
        max=80,
    )
    roadside_asset_offset: FloatProperty(
        name="Roadside Offset",
        description="Distance from the city edge to roadside support assets",
        default=5.5,
        min=1.0,
        max=40.0,
    )
    roadside_asset_scale: FloatProperty(
        name="Roadside Scale",
        description="Unified scale applied to generated roadside support assets",
        default=1.0,
        min=0.4,
        max=3.0,
    )


class ICITY_OT_ApplySurfaceAsset(Operator):
    bl_idname = "icity.apply_asset_surface"
    bl_label = "Apply Surface Asset"
    bl_description = "添加并替换新的 2D 道路/步道纹理资产"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        settings = context.scene.icity_asset_settings
        material = build_surface_material(settings, settings.surface_style)

        registered = False
        if settings.add_to_icity_material_library:
            registered = register_material_in_icity_library(material)

        if settings.surface_target_mode == "ROAD_SYSTEM":
            assigned = assign_material_to_road_system(material, settings.surface_slot)
            if assigned:
                for obj in discover_surface_targets(context, "AUTO_DISCOVERY"):
                    assign_material_to_object_data(obj, material, settings.replace_all_slots)
            if not assigned:
                targets = discover_surface_targets(context, "AUTO_DISCOVERY")
                if not targets:
                    self.report({"ERROR"}, "未找到可替换的 ICity 道路系统或道路对象。")
                    return {"CANCELLED"}
                changed = 0
                for obj in targets:
                    changed += int(assign_material_to_object_data(obj, material, settings.replace_all_slots))
                self.report(
                    {"INFO"},
                    f"已为 {changed} 个对象应用 {SURFACE_ASSET_LIBRARY[settings.surface_style]['label']}，并创建新 2D 资产。"
                    + (" 已注册到 ICity_Materials。" if registered else ""),
                )
                return {"FINISHED"}
            self.report(
                {"INFO"},
                f"已将 {SURFACE_ASSET_LIBRARY[settings.surface_style]['label']} 写入 ICity 道路系统 {settings.surface_slot} 槽位。"
                + (" 已注册到 ICity_Materials。" if registered else ""),
            )
            return {"FINISHED"}

        targets = discover_surface_targets(context, settings.surface_target_mode)
        if not targets:
            self.report({"ERROR"}, "没有找到可替换材质的目标对象。")
            return {"CANCELLED"}

        changed = 0
        for obj in targets:
            changed += int(assign_material_to_object_data(obj, material, settings.replace_all_slots))
        self.report(
            {"INFO"},
            f"已为 {changed} 个对象应用 {SURFACE_ASSET_LIBRARY[settings.surface_style]['label']}。"
            + (" 已注册到 ICity_Materials。" if registered else ""),
        )
        return {"FINISHED"}


class ICITY_OT_GenerateStreetlights(Operator):
    bl_idname = "icity.generate_streetlights"
    bl_label = "Generate Streetlights"
    bl_description = "生成新的 3D 路灯资产并布置到城市周边"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None or bpy.context.scene is not None

    def execute(self, context):
        settings = context.scene.icity_asset_settings
        clear_streetlights()

        asset_root = get_asset_root_collection()
        light_collection = get_or_create_child_collection(asset_root, ASSET_STREETLIGHT_COLLECTION)
        center, radius, ground_z = get_city_bounds()

        metal_material, emission_material = build_streetlight_materials(settings)
        mesh = build_streetlight_mesh(settings)
        mesh.materials.clear()
        mesh.materials.append(metal_material)
        mesh.materials.append(emission_material)

        positions = filtered_perimeter_positions(center, radius, settings)
        for index, (location, rotation) in enumerate(positions):
            create_streetlight_instance(
                light_collection,
                mesh,
                Vector((location.x, location.y, ground_z + location.z)),
                rotation,
                index,
                settings,
            )

        self.report({"INFO"}, f"已生成 {len(positions)} 组新 3D 路灯资产。")
        return {"FINISHED"}


class ICITY_OT_GenerateRoadsideAssets(Operator):
    bl_idname = "icity.generate_roadside_assets"
    bl_label = "Generate Roadside Props"
    bl_description = "Generate procedural roadside support assets around the city edge"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None or bpy.context.scene is not None

    def execute(self, context):
        settings = context.scene.icity_asset_settings
        asset_root = get_asset_root_collection()
        clear_roadside_assets(settings.roadside_asset_style)
        roadside_collection = get_or_create_child_collection(asset_root, ASSET_ROADSIDE_COLLECTION)
        center, radius, ground_z = get_city_bounds()

        positions = roadside_prop_positions(center, radius, settings)
        style_keys = roadside_style_keys(settings)
        if not positions:
            self.report({"ERROR"}, "No valid roadside prop positions were found.")
            return {"CANCELLED"}

        meshes = {}
        for style_key in style_keys:
            mesh = _build_roadside_prop_mesh(style_key)
            mesh.materials.clear()
            mesh.materials.append(build_roadside_prop_material(style_key))
            meshes[style_key] = mesh

        for index, (location, rotation) in enumerate(positions):
            style_key = style_keys[index % len(style_keys)]
            create_roadside_prop_instance(
                roadside_collection,
                meshes[style_key],
                Vector((location.x, location.y, ground_z)),
                rotation,
                index,
                style_key,
                settings.roadside_asset_scale,
            )

        self.report({"INFO"}, f"Generated {len(positions)} roadside support assets.")
        return {"FINISHED"}


class ICITY_OT_ClearAssetExpansion(Operator):
    bl_idname = "icity.clear_asset_expansion"
    bl_label = "Clear Generated Assets"
    bl_description = "Clear generated smart city streetlights and roadside props"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clear_streetlights()
        clear_roadside_assets()
        asset_root = bpy.data.collections.get(ASSET_ROOT_COLLECTION)
        if asset_root is not None and len(asset_root.children) == 0 and len(asset_root.objects) == 0:
            remove_collection_recursive(asset_root)
        self.report({"INFO"}, "Cleared generated streetlight and roadside assets.")
        return {"FINISHED"}


class ICITY_PT_AssetExpansionPanel(Panel):
    bl_label = "ICity Asset Expansion"
    bl_idname = "ICITY_PT_ASSET_EXPANSION_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.scene.icity_asset_settings

        intro = layout.box()
        intro.label(text="独立扩展：2D 纹理资产 + 3D 路灯资产。", icon="ASSET_MANAGER")
        intro.label(text="不直接改原有大资产面板，便于团队 merge。", icon="OUTLINER_COLLECTION")

        texture_box = layout.box()
        texture_box.label(text="2D Surface Asset", icon="TEXTURE")
        texture_box.prop(settings, "surface_style")
        texture_box.prop(settings, "surface_target_mode")
        if settings.surface_target_mode == "ROAD_SYSTEM":
            texture_box.prop(settings, "surface_slot")
        texture_box.prop(settings, "texture_uv_scale")
        texture_box.prop(settings, "texture_normal_strength")
        texture_box.prop(settings, "enable_lane_markings")
        texture_box.prop(settings, "replace_all_slots")
        texture_box.prop(settings, "add_to_icity_material_library")
        texture_box.operator("icity.apply_asset_surface", text="Create / Replace Texture", icon="MATERIAL")

        streetlight_box = layout.box()
        streetlight_box.label(text="3D Streetlight Asset", icon="LIGHT_POINT")
        streetlight_box.prop(settings, "streetlight_count")
        streetlight_box.prop(settings, "streetlight_offset")
        streetlight_box.prop(settings, "streetlight_height")
        streetlight_box.prop(settings, "streetlight_arm_length")
        streetlight_box.prop(settings, "streetlight_light_power")
        streetlight_box.prop(settings, "streetlight_emission_strength")
        streetlight_box.prop(settings, "streetlight_base_z_offset")

        row = streetlight_box.row(align=True)
        row.scale_y = 1.3
        row.operator("icity.generate_streetlights", text="Generate Streetlights", icon="LIGHT_POINT")
        row.operator("icity.clear_asset_expansion", text="Clear", icon="TRASH")

        roadside_box = layout.box()
        roadside_box.label(text="Roadside Support Assets", icon="OUTLINER_OB_EMPTY")
        roadside_box.prop(settings, "roadside_asset_style")
        roadside_box.prop(settings, "roadside_asset_count")
        roadside_box.prop(settings, "roadside_asset_offset")
        roadside_box.prop(settings, "roadside_asset_scale")
        roadside_box.operator("icity.generate_roadside_assets", text="Generate Roadside Props", icon="ASSET_MANAGER")


CLASSES = (
    ICITY_AssetSettings,
    ICITY_OT_ApplySurfaceAsset,
    ICITY_OT_GenerateStreetlights,
    ICITY_OT_GenerateRoadsideAssets,
    ICITY_OT_ClearAssetExpansion,
    ICITY_PT_AssetExpansionPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_asset_settings = PointerProperty(type=ICITY_AssetSettings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "icity_asset_settings"):
        del bpy.types.Scene.icity_asset_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

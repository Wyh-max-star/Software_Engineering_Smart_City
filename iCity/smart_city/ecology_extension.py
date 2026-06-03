"""Entry module for the standalone ICity ecology extension."""

from __future__ import annotations

import importlib

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

if "ecology_common" in locals():
    importlib.reload(ecology_common)
    importlib.reload(ecology_water)
    importlib.reload(ecology_traffic)
else:
    try:
        from . import ecology_common, ecology_traffic, ecology_water
    except ImportError:
        import ecology_common
        import ecology_traffic
        import ecology_water


ECOLOGY_BOAT_COLLECTION = ecology_common.ECOLOGY_BOAT_COLLECTION
ECOLOGY_COLLECTION = ecology_common.ECOLOGY_COLLECTION
ECOLOGY_CROWD_COLLECTION = ecology_common.ECOLOGY_CROWD_COLLECTION
ECOLOGY_ASSET_COLLECTION = ecology_common.ECOLOGY_ASSET_COLLECTION
ECOLOGY_PATH_COLLECTION = ecology_common.ECOLOGY_PATH_COLLECTION
ECOLOGY_TERRAIN_COLLECTION = ecology_common.ECOLOGY_TERRAIN_COLLECTION
ECOLOGY_TRAFFIC_COLLECTION = ecology_common.ECOLOGY_TRAFFIC_COLLECTION
ECOLOGY_WATER_COLLECTION = ecology_common.ECOLOGY_WATER_COLLECTION
ICITY_ROOT_COLLECTION = ecology_common.ICITY_ROOT_COLLECTION


def generate_ecology(context: bpy.types.Context) -> None:
    settings = context.scene.icity_ecology_settings
    root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root_collection is None:
        raise RuntimeError("请先在原 ICity 面板中点击 Start，生成基础城市场景。")
    if not settings.enable_ecology_block and not settings.enable_traffic_block:
        raise RuntimeError("请至少启用一个生成分区。")

    ecology_common.clear_existing_ecology()

    ecology_collection = ecology_common.get_or_create_child_collection(root_collection, ECOLOGY_COLLECTION)
    terrain_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_TERRAIN_COLLECTION)
    water_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_WATER_COLLECTION)
    boat_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_BOAT_COLLECTION)
    asset_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_ASSET_COLLECTION)
    traffic_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_TRAFFIC_COLLECTION)
    crowd_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_CROWD_COLLECTION)
    path_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_PATH_COLLECTION)

    center, city_radius, ground_z = ecology_common.get_city_bounds()
    layout = ecology_common.compute_layout(center, city_radius, ground_z, settings)

    if settings.enable_ecology_block:
        ecology_water.generate_water_system(
            layout,
            settings,
            terrain_collection,
            water_collection,
            boat_collection,
            asset_collection,
        )
    if settings.enable_traffic_block:
        ecology_traffic.generate_traffic_system(layout, settings, traffic_collection, crowd_collection, path_collection)

    context.scene.frame_start = settings.animation_start
    context.scene.frame_end = settings.animation_end
    context.scene.frame_set(settings.animation_start)


class ICITY_EcologySettings(PropertyGroup):
    enable_ecology_block: BoolProperty(
        name="Enable Ecology",
        description="生成地形、湖泊、河流与船只",
        default=True,
    )
    enable_traffic_block: BoolProperty(
        name="Enable Traffic & Crowd",
        description="生成汽车、人群、环路和步道",
        default=True,
    )
    seed: IntProperty(
        name="Seed",
        description="生态场景随机种子",
        default=12,
        min=0,
        max=999999,
    )
    terrain_margin: FloatProperty(
        name="Terrain Margin",
        description="城市边缘向外扩展的生态区域宽度",
        default=55.0,
        min=20.0,
        max=300.0,
    )
    terrain_resolution: IntProperty(
        name="Terrain Resolution",
        description="地形网格分辨率，越高越细致",
        default=96,
        min=32,
        max=180,
    )
    mountain_height: FloatProperty(
        name="Mountain Height",
        description="外围山峦的最高抬升强度",
        default=11.0,
        min=2.0,
        max=30.0,
    )
    noise_strength: FloatProperty(
        name="Terrain Noise",
        description="地形细节起伏强度",
        default=2.8,
        min=0.5,
        max=10.0,
    )
    lake_radius: FloatProperty(
        name="Lake Radius",
        description="湖泊基础半径",
        default=16.0,
        min=6.0,
        max=40.0,
    )
    lake_depth: FloatProperty(
        name="Lake Depth",
        description="湖泊下凹深度",
        default=7.5,
        min=2.0,
        max=20.0,
    )
    generate_river: BoolProperty(
        name="Generate River",
        description="是否从湖泊向外生成河道",
        default=True,
    )
    river_width: FloatProperty(
        name="River Width",
        description="河道平均宽度",
        default=7.0,
        min=2.0,
        max=20.0,
    )
    river_depth: FloatProperty(
        name="River Depth",
        description="河床下凹深度",
        default=2.8,
        min=0.5,
        max=8.0,
    )
    boat_count: IntProperty(
        name="Boat Count",
        description="湖面动态船只数量",
        default=2,
        min=1,
        max=6,
    )
    animation_start: IntProperty(
        name="Start Frame",
        description="动画开始帧",
        default=1,
        min=1,
        max=100000,
    )
    animation_end: IntProperty(
        name="End Frame",
        description="动画结束帧",
        default=250,
        min=2,
        max=100000,
    )
    car_count: IntProperty(
        name="Car Count",
        description="动态汽车数量",
        default=5,
        min=1,
        max=20,
    )
    crowd_count: IntProperty(
        name="Crowd Count",
        description="动态行人数量",
        default=10,
        min=1,
        max=40,
    )
    road_width: FloatProperty(
        name="Road Width",
        description="生成的环形道路宽度",
        default=3.8,
        min=1.6,
        max=10.0,
    )
    walkway_width: FloatProperty(
        name="Walkway Width",
        description="湖边步道宽度",
        default=2.1,
        min=0.8,
        max=6.0,
    )
    walkway_offset: FloatProperty(
        name="Walkway Offset",
        description="步道相对湖岸的外扩距离",
        default=3.6,
        min=1.0,
        max=12.0,
    )
    traffic_loop_radius_x: FloatProperty(
        name="Traffic Radius X",
        description="汽车环路横向半径",
        default=14.0,
        min=6.0,
        max=60.0,
    )
    traffic_loop_radius_y: FloatProperty(
        name="Traffic Radius Y",
        description="汽车环路纵向半径",
        default=8.5,
        min=4.0,
        max=40.0,
    )
    car_scale: FloatProperty(
        name="Car Scale",
        description="汽车模型比例",
        default=0.82,
        min=0.3,
        max=2.0,
    )
    pedestrian_scale: FloatProperty(
        name="Pedestrian Scale",
        description="行人模型比例",
        default=0.95,
        min=0.4,
        max=2.0,
    )


class ICITY_OT_GenerateEcology(Operator):
    bl_idname = "icity.generate_ecology"
    bl_label = "Generate Ecology"
    bl_description = "生成生态水域、交通环路与动态人群"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None

    def execute(self, context):
        settings = context.scene.icity_ecology_settings
        if settings.animation_end <= settings.animation_start:
            self.report({"ERROR"}, "End Frame 必须大于 Start Frame。")
            return {"CANCELLED"}
        try:
            generate_ecology(context)
        except Exception as exc:  # pragma: no cover
            self.report({"ERROR"}, f"扩展场景生成失败: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, "ICity 扩展场景已生成。")
        return {"FINISHED"}


class ICITY_OT_ClearEcology(Operator):
    bl_idname = "icity.clear_ecology"
    bl_label = "Clear Ecology"
    bl_description = "移除当前扩展生成的生态、交通与人群内容"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ecology_common.clear_existing_ecology()
        self.report({"INFO"}, "ICity 扩展场景已清理。")
        return {"FINISHED"}


class ICITY_PT_EcologyPanel(Panel):
    bl_label = "ICity Ecology"
    bl_idname = "ICITY_PT_ECOLOGY_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if bpy.data.collections.get(ICITY_ROOT_COLLECTION) is None:
            box = layout.box()
            box.label(text="先在原 ICity 面板点击 Start。", icon="INFO")
            return

        settings = context.scene.icity_ecology_settings

        intro_box = layout.box()
        intro_box.label(text="独立扩展，不修改原有 ICity 主面板。", icon="OUTLINER_COLLECTION")
        intro_box.label(text="生态水域与交通人群分模块实现。", icon="MESH_GRID")

        global_box = layout.box()
        global_box.label(text="Global", icon="PREFERENCES")
        global_box.prop(settings, "seed")
        global_box.prop(settings, "animation_start")
        global_box.prop(settings, "animation_end")

        ecology_box = layout.box()
        ecology_box.label(text="Ecology / Lake Block", icon="MOD_OCEAN")
        ecology_box.prop(settings, "enable_ecology_block")
        ecology_col = ecology_box.column()
        ecology_col.enabled = settings.enable_ecology_block
        ecology_col.prop(settings, "terrain_margin")
        ecology_col.prop(settings, "terrain_resolution")
        ecology_col.prop(settings, "mountain_height")
        ecology_col.prop(settings, "noise_strength")
        ecology_col.prop(settings, "lake_radius")
        ecology_col.prop(settings, "lake_depth")
        ecology_col.prop(settings, "generate_river")
        river_col = ecology_col.column()
        river_col.enabled = settings.generate_river
        river_col.prop(settings, "river_width")
        river_col.prop(settings, "river_depth")
        ecology_col.prop(settings, "boat_count")

        traffic_box = layout.box()
        traffic_box.label(text="Traffic & Crowd Block", icon="OUTLINER_OB_CURVE")
        traffic_box.prop(settings, "enable_traffic_block")
        traffic_col = traffic_box.column()
        traffic_col.enabled = settings.enable_traffic_block
        traffic_col.prop(settings, "car_count")
        traffic_col.prop(settings, "crowd_count")
        traffic_col.prop(settings, "road_width")
        traffic_col.prop(settings, "traffic_loop_radius_x")
        traffic_col.prop(settings, "traffic_loop_radius_y")
        traffic_col.prop(settings, "walkway_width")
        traffic_col.prop(settings, "walkway_offset")
        traffic_col.prop(settings, "car_scale")
        traffic_col.prop(settings, "pedestrian_scale")

        button_row = layout.row(align=True)
        button_row.scale_y = 1.4
        button_row.operator("icity.generate_ecology", text="Generate / Update", icon="PLAY")
        button_row.operator("icity.clear_ecology", text="Clear", icon="TRASH")


CLASSES = (
    ICITY_EcologySettings,
    ICITY_OT_GenerateEcology,
    ICITY_OT_ClearEcology,
    ICITY_PT_EcologyPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_ecology_settings = PointerProperty(type=ICITY_EcologySettings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "icity_ecology_settings"):
        del bpy.types.Scene.icity_ecology_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

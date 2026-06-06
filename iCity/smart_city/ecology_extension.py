"""Entry module for the standalone ICity ecology extension."""

from __future__ import annotations

import importlib

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector

if "ecology_common" in locals():
    importlib.reload(ecology_common)
    importlib.reload(ecology_water)
else:
    try:
        from . import ecology_common, ecology_water
    except ImportError:
        import ecology_common
        import ecology_water


ECOLOGY_BOAT_COLLECTION = ecology_common.ECOLOGY_BOAT_COLLECTION
ECOLOGY_COLLECTION = ecology_common.ECOLOGY_COLLECTION
ECOLOGY_TERRAIN_COLLECTION = ecology_common.ECOLOGY_TERRAIN_COLLECTION
ECOLOGY_WATER_COLLECTION = ecology_common.ECOLOGY_WATER_COLLECTION
ICITY_ROOT_COLLECTION = ecology_common.ICITY_ROOT_COLLECTION

ECOLOGY_PLOTS_COLLECTION = "ICity Ecology Plots"


def require_city_root() -> bpy.types.Collection:
    root_collection = bpy.data.collections.get(ICITY_ROOT_COLLECTION)
    if root_collection is None:
        raise RuntimeError("请先在原 ICity 面板中点击 Start，生成基础城市场景。")
    return root_collection


def ensure_ecology_root(root_collection: bpy.types.Collection) -> bpy.types.Collection:
    return ecology_common.get_or_create_child_collection(root_collection, ECOLOGY_COLLECTION)


def try_start_animation_playback(context: bpy.types.Context) -> None:
    screen = getattr(context, "screen", None)
    if screen is None:
        return
    if getattr(screen, "is_animation_playing", False):
        return
    try:
        bpy.ops.screen.animation_play()
    except Exception as exc:  # pragma: no cover
        print(f"[ICity Ecology] playback fallback: {exc}")


def hide_relationship_lines(context: bpy.types.Context) -> None:
    # Collect every 3D viewport across all open windows, not just the one in
    # the operator context, so the parent relationship overlay never lingers in
    # a second window or a re-opened editor.
    screens = []
    window_manager = getattr(bpy.context, "window_manager", None)
    if window_manager is not None:
        for window in window_manager.windows:
            if window.screen is not None:
                screens.append(window.screen)
    context_screen = getattr(context, "screen", None)
    if context_screen is not None and context_screen not in screens:
        screens.append(context_screen)

    for screen in screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                overlay = getattr(space, "overlay", None)
                if overlay is None:
                    continue
                # Only turn off the dashed parent relationship line. Leave the
                # grid floor and axes alone so the viewport's ground plane does
                # not disappear after generating a plot.
                if hasattr(overlay, "show_relationship_lines"):
                    overlay.show_relationship_lines = False


def add_ecology_plot(context: bpy.types.Context) -> tuple[bpy.types.Object, int]:
    settings = context.scene.icity_ecology_settings
    root_collection = require_city_root()
    ecology_collection = ensure_ecology_root(root_collection)
    plots_collection = ecology_common.get_or_create_child_collection(ecology_collection, ECOLOGY_PLOTS_COLLECTION)

    plot_index = ecology_water.next_plot_index(plots_collection)
    plot_collection_name = ecology_water.plot_collection_name(plot_index)
    plot_collection = ecology_common.get_or_create_child_collection(plots_collection, plot_collection_name)
    terrain_collection = ecology_common.get_or_create_child_collection(
        plot_collection, f"{plot_collection_name}_{ECOLOGY_TERRAIN_COLLECTION.split()[-1]}"
    )
    water_collection = ecology_common.get_or_create_child_collection(
        plot_collection, f"{plot_collection_name}_{ECOLOGY_WATER_COLLECTION.split()[-1]}"
    )
    boat_collection = ecology_common.get_or_create_child_collection(
        plot_collection, f"{plot_collection_name}_{ECOLOGY_BOAT_COLLECTION.split()[-1]}"
    )

    center, city_radius, ground_z = ecology_common.get_city_bounds()
    if settings.plot_use_cursor:
        cursor = context.scene.cursor.location.copy()
        plot_center = Vector((cursor.x, cursor.y, cursor.z))
        base_z = cursor.z
    else:
        plot_center = ecology_water.compute_plot_location(center, city_radius, settings, plot_index)
        base_z = ground_z

    terrain_obj = ecology_water.populate_plot(
        plot_index,
        plot_center,
        base_z,
        settings,
        plot_collection,
        terrain_collection,
        water_collection,
        boat_collection,
    )

    for obj in context.selected_objects:
        obj.select_set(False)
    terrain_obj.hide_select = False
    terrain_obj.select_set(True)
    context.view_layer.objects.active = terrain_obj
    hide_relationship_lines(context)

    context.scene.frame_start = settings.animation_start
    context.scene.frame_end = settings.animation_end
    context.scene.frame_set(settings.animation_start)
    # Do not auto-start playback after generating. The boats keep their keyframed
    # animation; the user can press Play (Spacebar) whenever they want to see it.
    # Count the boat meshes that actually landed in the collection instead of
    # reporting the slider value, so the header message reflects reality.
    actual_boats = len([obj for obj in boat_collection.objects if "_Boat_" in obj.name])
    terrain_obj["icity_generated_boats"] = actual_boats
    return terrain_obj, actual_boats


class ICITY_EcologySettings(PropertyGroup):
    enable_ecology_block: BoolProperty(
        name="Enable Ecology",
        description="启用生态地块生成功能",
        default=True,
    )
    seed: IntProperty(
        name="Seed",
        description="生态场景随机种子",
        default=12,
        min=0,
        max=999999,
    )
    ecology_plot_mode: EnumProperty(
        name="Plot Mode",
        description="当前要添加的生态平面类型",
        items=[
            ("LAKE_RING", "Lake + Mountains", "在平面上生成湖泊，并在外围形成环山"),
            ("MOUNTAIN_ONLY", "Mountain Only", "在平面上生成纯山地场景"),
            ("RIVER_VALLEY", "River Valley", "中间一条蜿蜒的河，两岸抬升成山的河谷地形"),
        ],
        default="LAKE_RING",
    )
    plot_shape: EnumProperty(
        name="Plot Shape",
        description="生态平面的外轮廓形状",
        items=[
            ("RECTANGLE", "Rectangle", "矩形地块"),
            ("ELLIPSE", "Ellipse", "椭圆地块"),
        ],
        default="ELLIPSE",
    )
    plot_width: FloatProperty(
        name="Plot Width",
        description="生态平面宽度",
        default=96.0,
        min=20.0,
        max=300.0,
    )
    plot_depth: FloatProperty(
        name="Plot Depth",
        description="生态平面纵深",
        default=82.0,
        min=20.0,
        max=300.0,
    )
    plot_offset: FloatProperty(
        name="Plot Offset",
        description="自动放置时，生态平面相对城市边界向外偏移的距离",
        default=22.0,
        min=4.0,
        max=200.0,
    )
    plot_ground_offset: FloatProperty(
        name="Plot Height Offset",
        description="生态平面的整体高度偏移",
        default=0.0,
        min=-20.0,
        max=20.0,
    )
    plot_use_cursor: BoolProperty(
        name="Use 3D Cursor",
        description="开启后，新的生态平面会生成到 3D Cursor 位置",
        default=False,
    )
    terrain_resolution: IntProperty(
        name="Terrain Resolution",
        description="地形网格分辨率，越高越细致（越高生成越慢）",
        default=128,
        min=32,
        max=256,
    )
    mountain_height: FloatProperty(
        name="Mountain Height",
        description="山体最高抬升强度",
        default=18.0,
        min=2.0,
        soft_max=80.0,
        max=200.0,
    )
    noise_strength: FloatProperty(
        name="Terrain Noise",
        description="地形细节与棱线起伏强度，越大山越崎岖、棱角越多",
        default=5.2,
        min=0.5,
        soft_max=30.0,
        max=60.0,
    )
    mountain_peak_count: IntProperty(
        name="Peak Count",
        description="山峰簇的数量，配合 Seed 会影响山峰位置分布",
        default=6,
        min=2,
        max=10,
    )
    lake_radius: FloatProperty(
        name="Lake Radius",
        description="湖泊基础半径",
        default=22.0,
        min=6.0,
        max=40.0,
    )
    lake_depth: FloatProperty(
        name="Lake Depth",
        description="湖泊下凹深度",
        default=10.5,
        min=2.0,
        max=20.0,
    )
    debug_water_boats: BoolProperty(
        name="Debug Water & Boats",
        description="用夸张的高亮方式显示湖水和船只，便于确认是否成功生成",
        default=False,
    )
    generate_river: BoolProperty(
        name="Generate River",
        description="是否从湖泊向外生成河道",
        default=False,
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
        default=3.5,
        min=0.5,
        soft_max=12.0,
        max=30.0,
    )
    river_source_width: FloatProperty(
        name="River Source Width",
        description="河谷模式：河流源头（起点）的宽度",
        default=6.0,
        min=1.0,
        soft_max=40.0,
        max=120.0,
    )
    river_mouth_width: FloatProperty(
        name="River Mouth Width",
        description="河谷模式：河流尽头（出口）的宽度，通常比源头宽",
        default=14.0,
        min=1.0,
        soft_max=60.0,
        max=160.0,
    )
    river_meander: FloatProperty(
        name="River Meander",
        description="河谷模式：河流的曲折度。0 = 笔直，越大蜿蜒幅度越大",
        default=0.35,
        min=0.0,
        max=1.0,
    )
    river_bend_count: IntProperty(
        name="River Bends",
        description="河谷模式：河流从源头到尽头的弯曲次数",
        default=3,
        min=1,
        max=8,
    )
    boat_count: IntProperty(
        name="Boat Count",
        description="湖面动态船只数量",
        default=3,
        min=0,
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


class ICITY_OT_AddEcologyPlot(Operator):
    bl_idname = "icity.add_ecology_plot"
    bl_label = "Add Ecology Plot"
    bl_description = "在城市旁边新增一个独立生态平面，并按当前模式生成山地或湖泊"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None

    def execute(self, context):
        settings = context.scene.icity_ecology_settings
        if not settings.enable_ecology_block:
            self.report({"ERROR"}, "请先启用 Ecology Block。")
            return {"CANCELLED"}
        if settings.animation_end <= settings.animation_start:
            self.report({"ERROR"}, "End Frame 必须大于 Start Frame。")
            return {"CANCELLED"}
        try:
            _, boat_count = add_ecology_plot(context)
        except Exception as exc:  # pragma: no cover
            self.report({"ERROR"}, f"生态地块生成失败: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"新的生态平面已生成，本次船只数量: {boat_count}")
        return {"FINISHED"}


class ICITY_OT_ClearEcology(Operator):
    bl_idname = "icity.clear_ecology"
    bl_label = "Clear All"
    bl_description = "移除当前扩展生成的生态地块内容"
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
        intro_box.label(text="生态块改为独立平面，可重复添加多块。", icon="MESH_GRID")

        global_box = layout.box()
        global_box.label(text="Global", icon="PREFERENCES")
        global_box.prop(settings, "seed")
        global_box.prop(settings, "animation_start")
        global_box.prop(settings, "animation_end")

        ecology_box = layout.box()
        ecology_box.label(text="Ecology Plot Block", icon="MOD_OCEAN")
        ecology_box.prop(settings, "enable_ecology_block")
        ecology_col = ecology_box.column()
        ecology_col.enabled = settings.enable_ecology_block
        ecology_col.prop(settings, "ecology_plot_mode")
        ecology_col.prop(settings, "plot_shape")
        ecology_col.prop(settings, "plot_width")
        ecology_col.prop(settings, "plot_depth")
        ecology_col.prop(settings, "plot_offset")
        ecology_col.prop(settings, "plot_ground_offset")
        ecology_col.prop(settings, "plot_use_cursor")
        ecology_col.prop(settings, "terrain_resolution")
        ecology_col.prop(settings, "mountain_height")
        ecology_col.prop(settings, "noise_strength")
        ecology_col.prop(settings, "mountain_peak_count")

        if settings.ecology_plot_mode == "LAKE_RING":
            ecology_col.prop(settings, "lake_radius")
            ecology_col.prop(settings, "lake_depth")
            ecology_col.prop(settings, "debug_water_boats")
            ecology_col.prop(settings, "boat_count")
        elif settings.ecology_plot_mode == "RIVER_VALLEY":
            ecology_col.prop(settings, "river_source_width")
            ecology_col.prop(settings, "river_mouth_width")
            ecology_col.prop(settings, "river_depth")
            ecology_col.prop(settings, "river_meander")
            ecology_col.prop(settings, "river_bend_count")

        ecology_hint = ecology_box.box()
        ecology_hint.label(text="每点一次 Add Plot，就会新增一个独立生态平面。", icon="INFO")
        ecology_hint.label(text="开启 Use 3D Cursor 后，可把平面放到指定位置。", icon="EMPTY_AXIS")
        ecology_hint.label(text="若全是绿色，请切到 Material Preview 或 Rendered。", icon="SHADING_RENDERED")
        ecology_hint.label(text="若还不明显，把 Solid 模式的 Color 改成 Material 或 Object。", icon="HIDE_OFF")
        ecology_button_row = ecology_box.row(align=True)
        ecology_button_row.scale_y = 1.25
        ecology_button_row.operator("icity.add_ecology_plot", text="Add Plot", icon="MESH_PLANE")

        button_row = layout.row(align=True)
        button_row.scale_y = 1.35
        button_row.operator("icity.clear_ecology", text="Clear All", icon="TRASH")


CLASSES = (
    ICITY_EcologySettings,
    ICITY_OT_AddEcologyPlot,
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

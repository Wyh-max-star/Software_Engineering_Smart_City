# -*- coding: utf-8 -*-
"""模板化整城生成 + 自然语言编辑 —— iCity 扩展模块（Blender 层）。

在 ICity 侧栏加"模板化生成"面板：
  ① 选模板(0/1/2) 一键配置整城（街道资产走原版 road_apply + 场景维度走 smart_city 算子）；
  ② 自然语言输入 → DeepSeek/规则 解析 → 应用。
纯逻辑（解析/数据/换算）在 template_core.py，本文件只管 Blender 算子/面板/应用。
"""

from __future__ import annotations

import bpy
from bpy.props import EnumProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup

try:
    from . import template_core
except ImportError:  # 脱包导入(测试/脚本)
    import template_core

# 从 core 取常量(便于本文件直接引用)
STREET_CATS = template_core.STREET_CATS
MATERIAL_CATS = template_core.MATERIAL_CATS
CAT_TITLE = template_core.CAT_TITLE
ALL_CATS = template_core.ALL_CATS
SCENE_DIMS = template_core.SCENE_DIMS
SCENE_DIM_TITLE = template_core.SCENE_DIM_TITLE
SCENE_CLEAR_OPS = template_core.SCENE_CLEAR_OPS
LLM_ENABLED = template_core.LLM_ENABLED
WEATHER_MODES = template_core.WEATHER_MODES
WEATHER_MODE_TITLE = template_core.WEATHER_MODE_TITLE
_log = template_core._log

# ============ 增量合并状态（多轮自然语言对话） ============
_last_scene_cfg = {}   # 上一次场景维度配置
_last_asset_sel = {}   # 上一次资产选择

def _merge_incremental(new_scene, new_assets):
    """将本次新参数与上次保存的参数增量合并。
    新设定的维度/资产覆盖旧值；未设定的保留旧值（保留之前结果，只叠加新修改）。
    返回 (merged_scene, merged_assets)。
    """
    global _last_scene_cfg, _last_asset_sel
    # 场景维度：新值覆盖，未设定保留旧值
    merged_scene = dict(_last_scene_cfg)
    for k, v in new_scene.items():
        if v:
            merged_scene[k] = v
    # 资产：新值覆盖，未设定保留旧值
    merged_assets = dict(_last_asset_sel)
    for k, v in new_assets.items():
        if v is not None:
            merged_assets[k] = v
    return merged_scene, merged_assets


# ---------------- 街道资产应用（已 Blender 验证）----------------
def enter_edit_select_all(base):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    icmod = template_core.get_icity_module()
    if icmod is not None:
        icmod.variables["sna_edit_city"] = True
    bpy.context.view_layer.update()


def apply_street_asset(asset_type, asset_name):
    scene = bpy.context.scene
    scene.sna_street_asset_type = asset_type
    bpy.context.view_layer.update()
    try:
        scene.sna_street_asset_browser = asset_name
    except Exception as e:
        _log(f"!! 设 {asset_type} '{asset_name}' 失败: {e}")
        return False
    try:
        bpy.ops.sna.road_apply_5c3ab()
        _log(f"  OK {asset_type} = {asset_name}")
        return True
    except Exception as e:
        _log(f"!! road_apply 失败({asset_type}): {e}")
        return False


def apply_road_material(material_name, mat_type="Road"):
    scene = bpy.context.scene
    scene.sna_street_asset_type = "Texture"
    scene.sna_road_materials_type_ = mat_type
    bpy.context.view_layer.update()
    try:
        scene.sna_road_materials_browser = material_name
    except Exception as e:
        _log(f"!! 设路面材质 '{material_name}' 失败: {e}")
        return False
    try:
        bpy.ops.sna.road_apply_5c3ab()
        _log(f"  OK 路面 = {material_name}")
        return True
    except Exception as e:
        _log(f"!! road_apply 失败(材质): {e}")
        return False


def apply_selection(base, sel):
    """街道资产: sel = {类别:资产名或None}，只应用非空项。"""
    results = []
    for cat, itype in STREET_CATS.items():
        if sel.get(cat):
            enter_edit_select_all(base)
            results.append((CAT_TITLE.get(cat, cat), apply_street_asset(itype, sel[cat])))
    for cat, mtype in MATERIAL_CATS.items():
        if sel.get(cat):
            enter_edit_select_all(base)
            results.append((CAT_TITLE.get(cat, cat), apply_road_material(sel[cat], mtype)))
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    return results


# ---------------- 场景维度应用（走 smart_city 算子，自动跳过）----------------
def _op_exists(idname):
    mod, op = idname.split(".", 1)
    grp = getattr(bpy.ops, mod, None)
    return grp is not None and hasattr(grp, op)


def _call_op(idname):
    mod, op = idname.split(".", 1)
    getattr(getattr(bpy.ops, mod), op)()


def _settings_present(attr):
    return hasattr(bpy.context.scene, attr)


def smart_city_available():
    return any(_settings_present(attr) for _, attr, _, _, _ in SCENE_DIMS)


def _apply_one_dimension(name, cfg, attr, gen_op, pre_clear_op, set_enable, results):
    title = SCENE_DIM_TITLE.get(name, name)
    if not cfg or cfg.get("enable") is False:
        return
    if cfg.get("_clear"):  # 清空意图(去掉X)
        clear_op = SCENE_CLEAR_OPS.get(name)
        if clear_op and _op_exists(clear_op):
            try:
                _call_op(clear_op)
                _log(f"  OK 清空 {name}")
                results.append((title + "(清空)", True))
            except Exception as e:
                _log(f"  !! 清空 {name} 失败: {e}")
                results.append((title + "(清空)", False))
        else:
            results.append((title + "(清空)", None))
        return
    if not (_settings_present(attr) and _op_exists(gen_op)):
        results.append((title, None))  # None = 跳过(未装 smart_city)
        return
    settings = getattr(bpy.context.scene, attr)
    if set_enable:
        try:
            setattr(settings, set_enable[0], set_enable[1])
        except Exception:
            pass
    for key, val in cfg.items():
        if key == "enable" or key.startswith("_"):
            continue
        if not hasattr(settings, key):
            _log(f"  跳过未知属性 {attr}.{key}")
            continue
        try:
            setattr(settings, key, val)  # Blender 会按属性 min/max 自动夹取
        except Exception as e:
            _log(f"  !! 设 {attr}.{key}={val} 失败: {e}")
    if pre_clear_op and _op_exists(pre_clear_op):
        try:
            _call_op(pre_clear_op)
        except Exception as e:
            _log(f"  clear 失败 {pre_clear_op}: {e}")
    try:
        _call_op(gen_op)
        _log(f"  OK 场景维度 {name}")
        results.append((title, True))
    except Exception as e:
        _log(f"  !! {gen_op} 失败: {e}")
        results.append((title, False))


def apply_scene_dimensions(scene_cfg):
    """scene_cfg = {维度名: {enable, 属性...}}，依 SCENE_DIMS 顺序应用。"""
    results = []
    if not scene_cfg:
        return results
    for name, attr, gen_op, pre_clear_op, set_enable in SCENE_DIMS:
        _apply_one_dimension(name, scene_cfg.get(name), attr, gen_op, pre_clear_op, set_enable, results)
    return results


def _fmt_results(results):
    def mark(ok):
        return "ok" if ok is True else ("跳过" if ok is None else "X")
    return "、".join(f"{n}={mark(ok)}" for n, ok in results)


# ---------------- 天气/天色控制 + 雨/雪粒子系统 ----------------
_WEATHER_EMITTER_NAME = "ICity_Weather_Emitter"


def _clear_weather_particles():
    """移除旧的雨/雪粒子发射器。"""
    old = bpy.data.objects.get(_WEATHER_EMITTER_NAME)
    if old:
        # 先删除 particle 系统占用的 material，再删物体
        for mod in old.modifiers:
            if mod.type == 'PARTICLE_SYSTEM':
                ps = mod.particle_system
                if ps and ps.settings:
                    mat_name = ps.settings.material_slot
                    if mat_name and isinstance(mat_name, str) and mat_name.startswith("ICity_Weather_"):
                        mat = bpy.data.materials.get(mat_name)
                        if mat:
                            bpy.data.materials.remove(mat, do_unlink=True)
        bpy.data.objects.remove(old, do_unlink=True)


def _create_weather_material(weather_type):
    """创建雨或雪的粒子材质。"""
    name = f"ICity_Weather_{weather_type}"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    if weather_type == "rainy":
        # 半透明蓝色雨水材质
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (0.7, 0.8, 1.0, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.0
        bsdf.inputs["Alpha"].default_value = 0.6
        mat.blend_method = 'BLEND'
    else:  # snowy
        # 白色雪材质
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
        bsdf.inputs["Alpha"].default_value = 0.85
        mat.blend_method = 'BLEND'
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _ensure_weather_particles(weather_type):
    """在场景上方创建雨/雪粒子发射器。"""
    _clear_weather_particles()
    if weather_type not in ("rainy", "snowy"):
        return
    # 切换 OBJECT 模式以保证 primitive 创建
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 60))
    emitter = bpy.context.active_object
    emitter.name = _WEATHER_EMITTER_NAME
    emitter.display_type = 'WIRE'
    emitter.hide_viewport = False  # 发射器必须可见，粒子才会显示
    emitter.hide_render = True
    emitter.hide_select = True

    mat = _create_weather_material(weather_type)
    if emitter.data.materials:
        emitter.data.materials[0] = mat
    else:
        emitter.data.materials.append(mat)

    # 添加粒子系统
    mod = emitter.modifiers.new(name="WeatherParticles", type='PARTICLE_SYSTEM')
    psys = mod.particle_system
    settings = psys.settings
    settings.emit_from = 'FACE'
    settings.distribution = 'RAND'
    settings.frame_start = -60   # 提前发射，打开时雨雪已在空中
    settings.frame_end = 5000    # 一直持续发射，连绵不绝
    settings.lifetime = 80       # 寿命足够落到地面
    settings.lifetime_random = 0.3

    if weather_type == "rainy":
        settings.count = 25000            # 雨滴数量
        settings.normal_factor = -40     # 快速下落
        settings.particle_size = 0.8
        settings.render_type = 'LINE'    # 渲染为细线 = 雨丝
        try:
            settings.line_length = 0.5   # 雨丝长度 0.5 米
        except Exception:
            pass
    else:  # snowy
        settings.count = 3000            # 雪花数量
        settings.normal_factor = -5      # 缓慢飘落
        settings.particle_size = 0.6
        settings.render_type = 'HALO'    # 渲染为光晕点 = 雪点
        # 雪花旋转
        try:
            settings.rotation_mode = 'GLOBAL'
            settings.angular_velocity_factor = 0.5
        except Exception:
            pass
    # 跳到第 60 帧，让粒子已经下落一段距离
    try:
        bpy.context.scene.frame_current = 60
    except Exception:
        pass


def _set_eevee_fog(enable):
    """启用/关闭 Eevee 体积雾。"""
    scene = bpy.context.scene
    try:
        scene.eevee.use_volumetric_lights = enable
        scene.eevee.use_volumetric_shadows = enable
        scene.eevee.volumetric_start = 0.1
        scene.eevee.volumetric_end = 200
        scene.eevee.volumetric_tile_size = '8'
    except Exception:
        pass
    if enable:
        # 创建一个雾盒（体积散射）
        fog_obj = bpy.data.objects.get("ICity_Fog_Box")
        if not fog_obj:
            bpy.ops.mesh.primitive_cube_add(size=500, location=(0, 0, 20))
            fog_obj = bpy.context.active_object
            fog_obj.name = "ICity_Fog_Box"
            fog_mat = bpy.data.materials.new(name="ICity_Fog_Material")
            fog_mat.use_nodes = True
            nodes = fog_mat.node_tree.nodes
            links = fog_mat.node_tree.links
            nodes.clear()
            vol = nodes.new("ShaderNodeVolumePrincipled")
            vol.inputs["Color"].default_value = (0.7, 0.7, 0.75, 1.0)
            vol.inputs["Density"].default_value = 0.05
            vol.inputs["Anisotropy"].default_value = 0.0
            out = nodes.new("ShaderNodeOutputMaterial")
            links.new(vol.outputs["Volume"], out.inputs["Volume"])
            if fog_obj.data.materials:
                fog_obj.data.materials[0] = fog_mat
            else:
                fog_obj.data.materials.append(fog_mat)
        fog_obj.hide_viewport = False
    else:
        fog_obj = bpy.data.objects.get("ICity_Fog_Box")
        if fog_obj:
            fog_obj.hide_viewport = True


def apply_weather(weather_mode):
    """根据 weather_mode 调整场景天色、灯光、粒子效果。"""
    if weather_mode not in WEATHER_MODES:
        return "未知天气模式"
    # 1) 先清除旧粒子+雾
    _clear_weather_particles()
    _set_eevee_fog(False)
    # 2) 世界背景
    world = bpy.context.scene.world
    if world and world.node_tree:
        bg_node = None
        for node in world.node_tree.nodes:
            if node.type == "BACKGROUND":
                bg_node = node
                break
        if bg_node is None:
            return "未找到 World Background 节点"
        strength_input = bg_node.inputs.get("Strength")
        color_input = bg_node.inputs.get("Color")
        if weather_mode == "sunny":
            if strength_input: strength_input.default_value = 1.0
            if color_input: color_input.default_value = (0.6, 0.8, 1.0, 1.0)
            _log("  天气: 晴朗")
        elif weather_mode == "cloudy":
            if strength_input: strength_input.default_value = 0.35
            if color_input: color_input.default_value = (0.5, 0.5, 0.55, 1.0)
            _log("  天气: 阴天/天色变暗")
        elif weather_mode == "rainy":
            if strength_input: strength_input.default_value = 0.2
            if color_input: color_input.default_value = (0.35, 0.35, 0.4, 1.0)
            _log("  天气: 雨天")
            _ensure_weather_particles("rainy")
        elif weather_mode == "night":
            if strength_input: strength_input.default_value = 0.02
            if color_input: color_input.default_value = (0.02, 0.02, 0.08, 1.0)
            _log("  天气: 夜晚")
        elif weather_mode == "foggy":
            if strength_input: strength_input.default_value = 0.3
            if color_input: color_input.default_value = (0.55, 0.55, 0.6, 1.0)
            _log("  天气: 起雾")
            _set_eevee_fog(True)
        elif weather_mode == "sunset":
            if strength_input: strength_input.default_value = 0.6
            if color_input: color_input.default_value = (1.0, 0.6, 0.2, 1.0)
            _log("  天气: 黄昏")
        elif weather_mode == "snowy":
            if strength_input: strength_input.default_value = 0.25
            if color_input: color_input.default_value = (0.5, 0.55, 0.6, 1.0)
            _log("  天气: 下雪")
            _ensure_weather_particles("snowy")
    # 3) 调整 ICity Road light 亮度
    road_light = bpy.data.lights.get("ICity Road light")
    if road_light:
        if weather_mode == "night":
            road_light.energy = 5000
            road_light.color = (1.0, 0.9, 0.7)
        elif weather_mode == "sunset":
            road_light.energy = 4000
            road_light.color = (1.0, 0.7, 0.4)
        elif weather_mode in ("cloudy", "rainy", "foggy", "snowy"):
            road_light.energy = 3000
            road_light.color = (1.0, 1.0, 0.95)
        else:  # sunny
            road_light.energy = 1000
            road_light.color = (1.0, 1.0, 1.0)
    return WEATHER_MODE_TITLE.get(weather_mode, weather_mode)


# ---------------- 模板下拉（动态枚举）----------------
_enum_cache = []


def template_enum_items(self, context):
    _enum_cache.clear()
    for t in template_core.load_templates():
        tid = str(t.get("id"))
        _enum_cache.append((tid, f"{tid} · {t.get('name', tid)}", t.get("_comment", "")))
    if not _enum_cache:
        _enum_cache.append(("NONE", "(未找到 templates.json)", ""))
    return _enum_cache


# ---------------- PropertyGroup ----------------
class ICITY_TemplateSettings(PropertyGroup):
    template_id: EnumProperty(
        name="模板", description="选择要应用的城市模板", items=template_enum_items)
    nl_command: StringProperty(
        name="自然语言指令", description="如：车水马龙、有山有湖、把树换成金黄的",
        default="车水马龙、有山有湖、街上很多人")


# ---------------- Operators ----------------
class ICITY_OT_ApplyTemplate(Operator):
    bl_idname = "icity.apply_template"
    bl_label = "应用模板 Apply Template"
    bl_description = "把选中的模板(街道资产 + 交通/人群/生态等)一次性应用到全城"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.icity_template_settings
        tid = settings.template_id
        tpl = next((t for t in template_core.load_templates() if str(t.get("id")) == str(tid)), None)
        if not tpl:
            self.report({'ERROR'}, f"模板 {tid} 未找到（检查 templates.json）")
            return {'CANCELLED'}
        base = bpy.data.objects.get("ICity Base")
        if not base:
            self.report({'ERROR'}, "场景没有 ICity Base，请先点 ICity 的 Start")
            return {'CANCELLED'}
        pl = tpl.get("plugin", {})
        sel = {c: pl.get(c) for c in ALL_CATS}
        _log("=" * 30, "应用模板", tid, tpl.get("name", ""))
        results = apply_selection(base, sel)
        results += apply_scene_dimensions(tpl.get("scene"))
        fails = [n for n, ok in results if ok is False]
        skipped = [n for n, ok in results if ok is None]
        msg = f"模板{tid}「{tpl.get('name','')}」: {_fmt_results(results)}"
        if fails:
            self.report({'WARNING'}, msg + "（部分失败，详见控制台）")
        elif skipped:
            self.report({'INFO'}, msg + "（含跳过项，可能未装smart_city）关Proxy+材质预览看效果")
        else:
            self.report({'INFO'}, msg + " ✓ 关Proxy+材质预览看效果")
        return {'FINISHED'}


class ICITY_OT_ApplyNaturalLanguage(Operator):
    bl_idname = "icity.apply_nl_command"
    bl_label = "解析并应用 Parse & Apply"
    bl_description = "用自然语言(DeepSeek/规则)解析并应用 资产 + 场景维度"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.icity_template_settings
        text = (settings.nl_command or "").strip()
        if not text:
            self.report({'WARNING'}, "请先写一句话，如：车水马龙、有山有湖、把树换成金黄的")
            return {'CANCELLED'}
        base = bpy.data.objects.get("ICity Base")
        if not base:
            self.report({'ERROR'}, "场景没有 ICity Base，请先点 ICity 的 Start")
            return {'CANCELLED'}
        sel, engine = template_core.parse_command(text)
        _log("=" * 30, f"自然语言[{engine}]:", text, "->", sel)
        if not template_core._has_content(sel):
            self.report({'WARNING'}, f"[{engine}] 没听懂。试试含 棕榈/金黄/脏/车水马龙/有山有湖/很多人 等词")
            return {'CANCELLED'}
        new_assets = {k: v for k, v in sel.items() if k != "_scene"}
        new_scene = sel.get("_scene") or {}
        # 增量合并：保留上次结果，只叠加新修改
        merged_scene, merged_assets = _merge_incremental(new_scene, new_assets)
        _log(f"增量合并: scene={merged_scene}  assets={merged_assets}")
        results = apply_selection(base, merged_assets)
        results += apply_scene_dimensions(merged_scene)
        # 天气应用
        weather = merged_scene.get("weather")
        if weather and weather in WEATHER_MODES:
            weather_label = apply_weather(weather)
            results.append((f"天气({weather_label})", True))
        # 保存本次合并结果，供下次增量
        global _last_scene_cfg, _last_asset_sel
        _last_scene_cfg = merged_scene
        _last_asset_sel = merged_assets
        self.report({'INFO'}, f"[{engine}] 已应用: {_fmt_results(results)} ✓ 关Proxy+材质预览看效果")
        return {'FINISHED'}


# ---------------- Panel ----------------
class ICITY_PT_TemplatePanel(Panel):
    bl_label = "模板化生成 Template"
    bl_idname = "ICITY_PT_TEMPLATE_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ICity"
    bl_order = 100

    def draw(self, context):
        layout = self.layout
        settings = context.scene.icity_template_settings

        layout.label(text="① 选模板一键应用(整城)", icon='PRESET')
        layout.prop(settings, "template_id", text="模板")
        tpl = next((t for t in template_core.load_templates()
                    if str(t.get("id")) == str(settings.template_id)), None)
        if tpl:
            pl = tpl.get("plugin", {})
            sc = tpl.get("scene", {})
            box = layout.box()
            box.label(text=tpl.get("name", ""))
            box.label(text="树: " + pl.get("tree", "-") + " / 椅: " + pl.get("bench", "-"))
            box.label(text="路面: " + pl.get("road_material", "-"))
            tr = sc.get("traffic", {}); pe = sc.get("pedestrian", {}); ec = sc.get("ecology", {})
            eco = ec.get("ecology_plot_mode", "无") if ec.get("enable", True) else "无"
            box.label(text=f"车{tr.get('car_count', '-')}/出租{tr.get('taxi_count', '-')}/公交{tr.get('bus_count', '-')} · 行人{pe.get('walker_count', '-')} · 生态{eco}")
        layout.operator("icity.apply_template", icon='PLAY')
        if not smart_city_available():
            layout.label(text="未检测到 smart_city：场景维度会跳过", icon='ERROR')

        layout.separator()

        layout.label(text="② 自然语言编辑", icon='OUTLINER_DATA_FONT')
        layout.prop(settings, "nl_command", text="")
        layout.operator("icity.apply_nl_command", icon='PLAY')
        col = layout.column(align=True)
        col.scale_y = 0.8
        engine = "DeepSeek" if (LLM_ENABLED and template_core.get_api_key()) else "规则(未配key)"
        col.label(text=f"解析引擎: {engine}", icon='INFO')
        col.label(text="例: 车水马龙、有山有湖、街上很多人")
        col.label(text="天气: 天色变暗 / 雨天 / 夜晚 / 晴天")


CLASSES = (
    ICITY_TemplateSettings,
    ICITY_OT_ApplyTemplate,
    ICITY_OT_ApplyNaturalLanguage,
    ICITY_PT_TemplatePanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.icity_template_settings = PointerProperty(type=ICITY_TemplateSettings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "icity_template_settings"):
        del bpy.types.Scene.icity_template_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

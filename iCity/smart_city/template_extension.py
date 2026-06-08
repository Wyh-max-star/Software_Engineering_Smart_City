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
_log = template_core._log


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
        asset_sel = {k: v for k, v in sel.items() if k != "_scene"}
        results = apply_selection(base, asset_sel)
        results += apply_scene_dimensions(sel.get("_scene"))
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
        col.label(text="应用后关 Proxy mode + 切材质预览")


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

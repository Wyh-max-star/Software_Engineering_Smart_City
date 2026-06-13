"""Human-readable test subject catalog for report generation.

Reports reference **what** is under test (module / feature / operator), not
``test_*.py`` paths or ``TestCase`` method names.
"""

from __future__ import annotations

import re

# (classname prefix, subject id) — first match wins
_CLASS_PREFIXES: tuple[tuple[str, str], ...] = (
    ("test_asset_extension.", "asset_extension"),
    ("test_asset_registry.", "asset_registry"),
    ("test_ecology_common.", "ecology_common"),
    ("test_ecology_water.", "ecology_water"),
    ("test_pedestrian_extension.", "pedestrian_extension"),
    ("test_traffic_extension.", "traffic_extension"),
    ("test_layout_control.", "layout_control"),
    ("test_layout_sketch.", "layout_sketch"),
    ("test_layout_operators_mock.", "layout_operators"),
    ("test_template_core.", "template_core"),
    ("test_nl_editing_guide.", "nl_editing"),
    ("test_template_extension.", "template_extension"),
    ("test_template_frontend_parity.", "template_frontend"),
    ("test_frontend_static_contracts.", "frontend_app"),
    ("test_mock_integration.", "mock_boundaries"),
    ("test_operators_mock.", "operators"),
    ("test_smart_city_extensions.", "cross_module"),
    ("test_smart_city_pedestrians.", "pedestrian_legacy"),
    ("test_smart_city_layout_samples.", "layout_samples"),
)

SUBJECTS: dict[str, dict] = {
    "asset_extension": {
        "name": "资产扩充",
        "product": "asset_extension",
        "scope": "路灯周长布点、城市核心区过滤、路面纹理查找、路边节点规格、网格 append",
    },
    "asset_registry": {
        "name": "资产注册表",
        "product": "asset_registry · templates.json / asset_manifest.json",
        "scope": "manifest 加载与校验、procedural 资产、blend 目标解析、路径拼接",
    },
    "ecology_common": {
        "name": "生态布局与几何",
        "product": "ecology_common",
        "scope": "clamp / smoothstep、椭圆与路径采样、布局不变式（生态/交通远离城心）",
    },
    "ecology_water": {
        "name": "生态水域与地形",
        "product": "ecology_water · 地块模式",
        "scope": "LAKE_RING / RIVER_VALLEY / MOUNTAIN_ONLY 地块、湖泊/河流几何、terrain_height、船只网格",
    },
    "pedestrian_extension": {
        "name": "人群路径规划",
        "product": "pedestrian_extension",
        "scope": "人行道带宽、转角检测、站立点/环线 fallback、路线规划",
    },
    "traffic_extension": {
        "name": "交通布局与路径",
        "product": "traffic_extension",
        "scope": "道路链提取、车道布局、车辆路径预处理/重采样、车型序列、车辆随机分配（路线/相位/缩放）",
    },
    "layout_control": {
        "name": "布局控制 Draft",
        "product": "layout_control · ICity Base 图编辑",
        "scope": "节点坐标 CRUD、边调整、校验/规范化、Apply 载荷、Preview 几何、Apply/Load 算子契约",
    },
    "layout_sketch": {
        "name": "草图布局识别",
        "product": "layout_sketch",
        "scope": "黑线草图二值化、骨架细化、像素路径追踪、矩形/道路图转 LayoutGraph",
    },
    "layout_operators": {
        "name": "布局控制算子契约",
        "product": "icity.* layout 算子",
        "scope": "Inspect/Load/Validate/Normalize/Import Sketch·JSON、Draft 节点边 CRUD（Mock）",
    },
    "template_core": {
        "name": "模板与自然语言解析",
        "product": "template_core · manifests/templates.json",
        "scope": "关键词规则、档位→数值换算、7 种天气、LLM(DeepSeek) 解析与回退、catalog 数据完整性",
    },
    "nl_editing": {
        "name": "自然语言编辑（天气与增量）",
        "product": "template_core · template_extension · NL README",
        "scope": "7 类资产、场景维度、7 种天气、多轮增量合并、组合指令、apply_weather Mock",
    },
    "template_extension": {
        "name": "模板场景应用编排",
        "product": "template_extension",
        "scope": "街道资产 apply_selection、场景维度 apply_scene_dimensions、road_apply 调用链",
    },
    "template_frontend": {
        "name": "前后端模板数据",
        "product": "frontend/templates.ts ↔ templates.json",
        "scope": "模板 0/1/2 名称/编号/资产名/场景概要、catalog 校验、预览图、角色与 getTemplate 回退",
    },
    "frontend_app": {
        "name": "前端应用静态契约",
        "product": "frontend/App.tsx · React 多角色原型",
        "scope": "RBAC 权限矩阵、路由守卫、角色工作流文案、localStorage 键、Blender 入口参数字段、模板商城",
    },
    "mock_boundaries": {
        "name": "Mock 依赖边界",
        "product": "跨模块 I/O 与 manifest 注入",
        "scope": "纹理目录 @patch、manifest 打开失败、车辆 manifest 合并",
    },
    "operators": {
        "name": "Blender 算子契约",
        "product": "icity.* 算子 execute / poll",
        "scope": "资产/生态/交通/人群/模板/自然语言算子 FINISHED·CANCELLED 行为（Mock 流水线）",
    },
    "cross_module": {
        "name": "跨模块布局不变式",
        "product": "smart_city 多模块协同",
        "scope": "交通/生态地块远离城心、行人复用交通 offset、纹理编号副本",
    },
    "pedestrian_legacy": {
        "name": "行人动画与网格",
        "product": "pedestrian_extension（扩展场景）",
        "scope": "locomotion/bob 区分、FBX 模板居中、路线与站立点扩展",
    },
    "layout_samples": {
        "name": "布局采样回归",
        "product": "ecology_common 多 seed",
        "scope": "多随机种子下生态/交通环带始终落在城市外围",
    },
}

MOCK_SCOPES: tuple[tuple[str, str], ...] = (
    ("template_core.LlmParseTests", "DeepSeek HTTP 响应解析"),
    ("template_core.ParseCommandTests", "自然语言 parse_command 编排"),
    ("test_mock_integration.", "manifest / 纹理 / 车辆 profile 边界"),
    ("test_operators_mock.", "算子 execute 契约（Mock 流水线）"),
)


def subject_id_for(classname: str) -> str:
    for prefix, sid in _CLASS_PREFIXES:
        if classname.startswith(prefix):
            return sid
    return "other"


def subject_for(classname: str) -> dict:
    sid = subject_id_for(classname)
    if sid in SUBJECTS:
        return SUBJECTS[sid]
    return {
        "name": "其他",
        "product": classname.split(".")[0],
        "scope": "（未登记测试对象，请在 test_catalog.py 补充）",
    }


def humanize_method(method_name: str) -> str:
    label = method_name
    if label.startswith("test_"):
        label = label[5:]
    return re.sub(r"\s+", " ", label.replace("_", " "))


def describe_failure(classname: str, method_name: str) -> str:
    subj = subject_for(classname)
    return f"{subj['name']} — {humanize_method(method_name)}"


def group_records_by_subject(records: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Group by (box, subject_id)."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for record in records:
        sid = subject_id_for(record["classname"])
        key = (record["box"], sid)
        groups.setdefault(key, []).append(record)
    return groups

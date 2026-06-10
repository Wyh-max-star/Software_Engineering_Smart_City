# -*- coding: utf-8 -*-
"""模板化 + 自然语言 配置的【纯逻辑】核心（不依赖 bpy，可脱 Blender 单元测试）。

职责：读取 templates.json、关键词/LLM(DeepSeek) 解析、档位→数值换算、prompt 构造。
Blender 相关（算子、面板、应用到场景）在 template_extension.py。
数据文件：本目录 manifests/templates.json（唯一源）。DeepSeek key：内置 DEFAULT_API_KEY，可用环境变量 DEEPSEEK_API_KEY 覆盖。
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path

# ============ LLM 配置 ============
LLM_ENABLED = True
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-v4-flash"
LLM_TIMEOUT = 25

# —— 街道资产(走原版 icity road_apply) ——
STREET_CATS = {"tree": "Tree", "bench": "Bench", "light": "Light", "bollard": "Bollard"}
MATERIAL_CATS = {"road_material": "Road", "curb": "Curb", "sidewalk": "Sidewalk"}
CAT_TITLE = {"tree": "树", "bench": "座椅", "light": "路灯", "bollard": "隔离柱",
             "road_material": "路面材质", "curb": "路缘石", "sidewalk": "人行道"}
ALL_CATS = list(STREET_CATS) + list(MATERIAL_CATS)
# LLM 控制全部 7 种资产（树/座椅/路灯/隔离柱/路面/路缘/人行道）
LLM_CATS = list(ALL_CATS)

# —— 场景维度(走队友 smart_city 算子) ——
# (维度名, 场景属性组, 生成算子, 先清算子或None, (强制设的enable属性,值)或None)
SCENE_DIMS = [
    ("surface",     "icity_asset_settings",      "icity.apply_asset_surface",      None,                None),
    ("streetlights", "icity_asset_settings",     "icity.generate_streetlights",    None,                None),
    ("roadside",    "icity_asset_settings",      "icity.generate_roadside_assets", None,                None),
    ("traffic",     "icity_traffic_settings",    "icity.generate_traffic",         None,                None),
    ("pedestrian",  "icity_pedestrian_settings", "icity.generate_pedestrians",     None,                None),
    ("ecology",     "icity_ecology_settings",    "icity.add_ecology_plot",         "icity.clear_ecology",
        ("enable_ecology_block", True)),  # ecology 是追加式，必须先清并强制 enable
]
SCENE_DIM_TITLE = {"surface": "路面材质", "streetlights": "路灯", "roadside": "路边设施",
                   "traffic": "交通", "pedestrian": "人群", "ecology": "生态"}
# 各维度的"清空"算子(自然语言"去掉X"时调用)
SCENE_CLEAR_OPS = {
    "traffic": "icity.clear_traffic",
    "pedestrian": "icity.clear_pedestrians",
    "ecology": "icity.clear_ecology",
    "streetlights": "icity.clear_asset_expansion",
    "roadside": "icity.clear_asset_expansion",
}
LEVELS = ("none", "low", "medium", "high", "max")
SURFACE_STYLES = ("ASPHALT_MARKED", "CONCRETE_BOULEVARD", "BOARDWALK_WARM")
ECO_MODES = ("LAKE_RING", "MOUNTAIN_ONLY", "RIVER_VALLEY")
# 天气模式（新增）
WEATHER_MODES = ("sunny", "cloudy", "rainy", "night", "foggy", "sunset", "snowy")
WEATHER_MODE_TITLE = {"sunny": "晴天", "cloudy": "阴天/天色变暗", "rainy": "雨天",
                      "night": "夜晚", "foggy": "起雾/雾天", "sunset": "黄昏/夕阳",
                      "snowy": "下雪"}


def _log(*a):
    print("[模板插件]", *a)


# ---------------- 数据读取（路径相对本模块，规范） ----------------
def templates_json_path() -> Path:
    return Path(__file__).resolve().parent / "manifests" / "templates.json"


def load_data():
    try:
        with open(templates_json_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _log("读取 templates.json 失败:", e)
        return {}


def load_templates():
    return load_data().get("templates", [])


def load_catalog_scene():
    return load_data().get("catalog_scene", {})


def catalog_items(category):
    cat = load_data().get("catalog", {}).get(category, {})
    return [(it.get("asset", ""), it.get("desc", "")) for it in cat.get("items", [])]


def valid_assets(category):
    return {a for a, _ in catalog_items(category) if a}


def get_icity_module():
    """找到 icity 插件模块（用于读 sna_edit_city）。只看 sys.modules，无需 bpy。"""
    for name in ("icity", "ICity", "iCity"):
        m = sys.modules.get(name)
        if m and hasattr(m, "variables"):
            return m
    for name, m in sys.modules.items():
        if m is not None and hasattr(m, "variables") and isinstance(getattr(m, "variables"), dict) \
           and "sna_edit_city" in getattr(m, "variables"):
            return m
    return None


# ---------------- 档位 → 具体数值 ----------------
def expand_scene(raw):
    """把定性 {traffic:'high',ecology_mode:'LAKE_RING',...} 换成 apply_scene_dimensions 能用的具体参数。"""
    if not isinstance(raw, dict):
        return {}
    cs = load_catalog_scene()
    out = {}

    def fill(dim_key, count_keys, level):
        if not (isinstance(level, str) and level in LEVELS):
            return
        if level == "none":            # 去掉车/人 -> 清空
            out[dim_key] = {"_clear": True}
            return
        lvls = cs.get(dim_key, {}).get("levels", {})
        d = {"enable": True}
        for k in count_keys:
            m = lvls.get(k, {})
            if level in m:
                d[k] = m[level]
        out[dim_key] = d

    fill("traffic", ("car_count", "taxi_count", "bus_count"), raw.get("traffic"))
    fill("pedestrian", ("walker_count", "idle_count"), raw.get("pedestrian"))

    st = raw.get("surface")
    if isinstance(st, str) and st in SURFACE_STYLES:
        out["surface"] = {"enable": True, "surface_style": st,
                          "surface_target_mode": "ROAD_SYSTEM", "surface_slot": "Road"}

    mode = raw.get("ecology_mode")
    if mode == "NONE":                 # 去掉山/湖/河 -> 清空生态
        out["ecology"] = {"_clear": True}
    elif isinstance(mode, str) and mode in ECO_MODES:
        d = {"enable": True, "ecology_plot_mode": mode}
        inten = raw.get("ecology_intensity")
        intmap = cs.get("ecology", {}).get("intensity", {})
        if isinstance(inten, str):
            for k in ("mountain_height", "lake_radius", "boat_count"):
                m = intmap.get(k, {})
                if inten in m:
                    d[k] = m[inten]
        out["ecology"] = d
    # 天气：直接透传
    w = raw.get("weather")
    if isinstance(w, str) and w in WEATHER_MODES:
        out["weather"] = w
    return out


# ---------------- 关键词规则解析（离线兜底） ----------------
def rule_parse(text):
    """资产部分。"""
    sel = {c: None for c in ALL_CATS}
    if any(k in text for k in ("棕榈", "椰子", "热带", "海滨", "沙滩", "度假", "南国")):
        sel["tree"] = "Tree14_Tree_ICity_Default"
    elif any(k in text for k in ("金黄", "金色", "秋天", "秋季", "黄叶", "秋")):
        sel["tree"] = "Tree7_Tree_ICity_Default"
    elif any(k in text for k in ("垂柳", "柳树", "柳")):
        sel["tree"] = "Tree4_Tree_ICity_Default"
    elif any(k in text for k in ("白桦", "桦树", "稀疏")):
        sel["tree"] = "Tree11_Tree_ICity_Default"
    elif any(k in text for k in ("绿树", "绿色", "普通树", "常规", "茂密", "公园")):
        sel["tree"] = "Tree1_Tree_ICity_Default"
    if any(k in text for k in ("龟裂", "裂缝", "裂纹", "坑洼")):
        sel["road_material"] = "ICity_Road 11 dirty_Default"
    elif any(k in text for k in ("脏", "破旧", "老旧", "陈旧", "破")):
        sel["road_material"] = "ICity_Road 8 dirty_Default"
    elif any(k in text for k in ("干净", "整洁", "崭新", "平整", "新路", "新的路")):
        sel["road_material"] = "ICity_Road 4 clean_Default"
    if any(k in text for k in ("现代", "金属", "黑色", "简约", "通透")):
        sel["bench"] = "Bench11_Bench_ICity_Default"
    elif any(k in text for k in ("木质", "木椅", "复古", "传统", "经典", "木头")):
        sel["bench"] = "Bench1_Bench_ICity_Default"
    elif any(k in text for k in ("无靠背", "条凳", "简易")):
        sel["bench"] = "Bench8_Bench_ICity_Default"
    if any(k in text for k in ("方形灯", "LED灯", "现代路灯")):
        sel["light"] = "Light6_Light_ICity_Default"
    elif any(k in text for k in ("路灯", "街灯", "照明", "路边灯")):
        sel["light"] = "Light1_Light_ICity_Default"
    if any(k in text for k in ("黄黑隔离柱", "警示柱", "防撞")):
        sel["bollard"] = "Bollard4_Bollard_Default_ICity"
    elif any(k in text for k in ("礼宾", "红绳", "隔离栏")):
        sel["bollard"] = "Bollard9_Bollard_Default_ICity"
    elif any(k in text for k in ("铸铁", "古典柱", "石墩", "隔离柱")):
        sel["bollard"] = "Bollard3_Bollard_Default_ICity"
    if any(k in text for k in ("黄黑路缘", "警示路缘")):
        sel["curb"] = "ICity_Curb yellow black_Default"
    elif any(k in text for k in ("路缘", "缘石")):
        sel["curb"] = "ICity_Curb grey_Default"
    if "人行道" in text:
        sel["sidewalk"] = "ICity_Sidewalk 1_Default"
    return sel


def rule_parse_scene(text):
    """场景维度，定性。"""
    sc = {}
    if any(k in text for k in ("车水马龙", "拥堵", "繁华", "车多", "堵车", "车流密集")):
        sc["traffic"] = "high"
    elif any(k in text for k in ("步行街", "无车", "禁车", "没有车", "去掉车", "去掉交通", "去掉车流", "清空车")):
        sc["traffic"] = "none"
    elif any(k in text for k in ("车少", "宁静", "冷清", "稀疏的车")):
        sc["traffic"] = "low"
    if any(k in text for k in ("人潮", "熙熙攘攘", "很多人", "人多", "热闹", "人山人海", "人来人往")):
        sc["pedestrian"] = "high"
    elif any(k in text for k in ("去掉人", "去掉行人", "去掉人群", "清空人", "没有人", "没人")):
        sc["pedestrian"] = "none"
    elif any(k in text for k in ("人少", "空城", "僻静")):
        sc["pedestrian"] = "low"
    if any(k in text for k in ("去掉山", "去掉湖", "去掉河", "去掉山水", "没有山", "没有水", "不要山", "不要湖", "移除生态", "清空生态", "去掉生态", "去掉自然")):
        sc["ecology_mode"] = "NONE"
    elif any(k in text for k in ("湖光山色", "有山有湖", "有湖有山", "滨水", "湖泊", "湖")):
        sc["ecology_mode"] = "LAKE_RING"
        sc["ecology_intensity"] = "medium"
    elif any(k in text for k in ("河谷", "河流", "小河", "蜿蜒的河", "江", "河")):
        sc["ecology_mode"] = "RIVER_VALLEY"
        sc["ecology_intensity"] = "medium"
    elif any(k in text for k in ("群山", "山地", "山峦", "只有山", "崇山")):
        sc["ecology_mode"] = "MOUNTAIN_ONLY"
        sc["ecology_intensity"] = "medium"
    if any(k in text for k in ("木栈道", "栈道", "海边", "海滨木")):
        sc["surface"] = "BOARDWALK_WARM"
    elif any(k in text for k in ("林荫大道", "大道", "广场", "混凝土")):
        sc["surface"] = "CONCRETE_BOULEVARD"
    elif any(k in text for k in ("主干道", "车道线", "柏油", "沥青")):
        sc["surface"] = "ASPHALT_MARKED"
    # 天气解析（自然语言控制天色/天气）
    if any(k in text for k in ("天黑", "夜晚", "晚上", "夜间", "深夜", "入夜")):
        sc["weather"] = "night"
    elif any(k in text for k in ("天色变暗", "阴天", "多云", "阴沉")):
        sc["weather"] = "cloudy"
    elif any(k in text for k in ("雨天", "下雨", "阴雨", "大雨", "小雨", "暴雨", "雨")):
        sc["weather"] = "rainy"
    elif any(k in text for k in ("晴天", "晴朗", "大太阳", "阳光", "放晴", "晴")):
        sc["weather"] = "sunny"
    elif any(k in text for k in ("起雾", "雾天", "大雾", "浓雾", "迷雾", "雾蒙蒙")):
        sc["weather"] = "foggy"
    elif any(k in text for k in ("黄昏", "夕阳", "日落", "傍晚", "晚霞")):
        sc["weather"] = "sunset"
    elif any(k in text for k in ("下雪", "雪天", "大雪", "小雪", "飘雪", "暴雪", "雪花")):
        sc["weather"] = "snowy"
    return sc


# ---------------- 密钥 + DeepSeek ----------------
# 团队默认 DeepSeek API key（已商定直接内置，默认就用它）。
# 可用环境变量 DEEPSEEK_API_KEY / ICITY_LLM_KEY 覆盖（留给想用自己 key 的人）。
DEFAULT_API_KEY = "sk-ca447a1343ba49a4b982720963725cc8"


def get_api_key():
    return (os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("ICITY_LLM_KEY")
            or DEFAULT_API_KEY).strip()


def build_scene_prompt_block():
    cs = load_catalog_scene()
    if not cs:
        return ""
    lines = ["【场景维度】只输出 档位/枚举(数值由程序换算)，没提到的维度返回 null："]
    if "traffic" in cs:
        lines.append("traffic (none/low/medium/high/max): " + cs["traffic"].get("desc", ""))
    if "pedestrian" in cs:
        lines.append("pedestrian (none/low/medium/high/max): " + cs["pedestrian"].get("desc", ""))
    if "surface" in cs:
        lines.append("surface (ASPHALT_MARKED/CONCRETE_BOULEVARD/BOARDWALK_WARM): " + cs["surface"].get("desc", ""))
    if "ecology" in cs:
        lines.append("ecology_mode (LAKE_RING/MOUNTAIN_ONLY/RIVER_VALLEY/NONE): " + cs["ecology"].get("desc", ""))
    lines.append("ecology_intensity (low/medium/high)")
    lines.append("【天气】weather (sunny/cloudy/rainy/night/foggy/sunset/snowy): 晴天=sunny，天色变暗/阴天=cloudy，下雨/雨天=rainy，天黑/夜晚=night，起雾/雾天=foggy，黄昏/夕阳=sunset，下雪=snowy。没提到=null(保持不变)。")
    lines.append("【去掉某维度】明确要去掉车/人 -> 对应 none；去掉山/湖/河等自然景观 -> ecology_mode 用 NONE。没提到的维度一律 null(保持不变,不要乱填 NONE/none)。")
    return "\n".join(lines)


def build_system_prompt():
    blocks = []
    for c in LLM_CATS:
        lines = [f"【{CAT_TITLE[c]} 可选】"]
        for asset, desc in catalog_items(c):
            lines.append(f"{asset} : {desc}")
        blocks.append("\n".join(lines))
    asset_schema = ", ".join(f'"{c}":"资产名或null"' for c in LLM_CATS)
    scene_schema = ('"scene":{"traffic":"档位或null","pedestrian":"档位或null",'
                    '"surface":"枚举或null","ecology_mode":"枚举或null","ecology_intensity":"low|medium|high|null",'
                    '"weather":"sunny|cloudy|rainy|night|foggy|sunset|snowy|null"}')
    schema = "{" + asset_schema + ", " + scene_schema + "}"
    example = json.dumps({"tree": "Tree7_Tree_ICity_Default",
                          "scene": {"traffic": "high", "pedestrian": "high",
                                    "ecology_mode": "LAKE_RING", "ecology_intensity": "medium",
                                    "weather": "cloudy"}},
                         ensure_ascii=False)
    return (
        "你是 iCity 智能城市配置助手。根据用户中文描述，挑选资产并判断场景维度。\n"
        "资产：只能选清单里的【资产名】原样返回，不要编造；场景：只输出档位/枚举。没提到的一律 null。\n"
        "严格只输出 JSON，格式：" + schema + "\n\n"
        + "\n\n".join(blocks) + "\n\n"
        + build_scene_prompt_block() + "\n\n"
        + "【重要】当 ecology_mode 不是 null 也不是 NONE 时，必须同时给出 ecology_intensity(low/medium/high)。\n\n"
        + "示例：用户「车水马龙、有山有湖、街上很多人，金黄的树」 -> " + example
    )


def _http_post_json(url, headers, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    # 强制直连、绕开系统代理：科学上网代理会把国内 DeepSeek 路由到国外导致卡死。
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=ctx),
    )
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def llm_parse(text, api_key):
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    resp = _http_post_json(LLM_BASE_URL + "/chat/completions", headers, payload, LLM_TIMEOUT)
    return json.loads(resp["choices"][0]["message"]["content"])


def validate_selection(raw):
    """资产部分: 不在清单里的清成 None。"""
    out = {c: None for c in ALL_CATS}
    for c in ALL_CATS:
        v = raw.get(c)
        if isinstance(v, str) and v in valid_assets(c):
            out[c] = v
    return out


def _has_content(sel):
    """检查是否有有效内容（资产 or 场景维度 or 天气）。"""
    if any(v for k, v in sel.items() if k != "_scene"):
        return True
    scene = sel.get("_scene")
    if isinstance(scene, dict):
        # 只要 _scene 里有任何一个非空值就算有内容（含天气）
        if any(v for v in scene.values() if v):
            return True
    return False


def parse_command(text):
    """返回 (sel, engine)。sel 含资产键 + '_scene'(具体场景参数)。优先 LLM，失败退规则。"""
    key = get_api_key()
    if LLM_ENABLED and key:
        try:
            _log("调用 DeepSeek 解析中…(联网,若稍卡请等几秒)")
            raw = llm_parse(text, key)
            sel = validate_selection(raw)
            sel["_scene"] = expand_scene(raw.get("scene"))
            if _has_content(sel):
                return sel, "DeepSeek"
            _log("LLM 没解析出有效内容，退回规则。原始:", raw)
        except Exception as e:
            _log("LLM 调用失败，退回规则解析：", e)
    sel = rule_parse(text)
    sel["_scene"] = expand_scene(rule_parse_scene(text))
    return sel, "规则解析"

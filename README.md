<div align="center">

# 🏙️ 智能城市生成系统 · Smart City Generation System

**南开大学 2026 · 软件工程课程团队大作业**

基于 Blender [iCity] 插件，一键生成、自由编辑、自然语言驱动的 3D 智能城市。

![Blender](https://img.shields.io/badge/Blender-4.1-EA7600?logo=blender&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-64%20passed-2EA043)
![LLM](https://img.shields.io/badge/LLM-DeepSeek-7C3AED)
![Branch](https://img.shields.io/badge/branch-qhr-orange)

</div>



## 📑 目录

- [项目简介](#-项目简介)
- [完成进度](#-完成进度)
- [功能模块与用法](#-功能模块与用法)
- [自然语言编辑（LLM）](#-自然语言编辑llm)
- [数据文件说明](#-数据文件说明)
- [测试](#-测试)
- [安装与运行](#-安装与运行)
- [项目结构](#-项目结构)
- [文档索引](#-文档索引)

---

## ✨ 项目简介

本项目在开源 Blender 城市生成插件 **iCity** 基础上扩展，构建一套"**智能**"城市生成系统：在不改动 iCity 原始入口的前提下，于 `iCity/smart_city/` 内以规范模块化方式加入资产扩充、交通、人群、生态、**模板化生成**与**自然语言编辑**等能力，并配套**单元测试**与**模块文档**。

- 🧩 **模块化、低耦合**：每个功能是独立模块，经 `iCity/__init__.py` 最小接线注册，方便多人协作合并。
- 🧪 **可测试**：纯逻辑与 Blender 操作分层，64 个单元测试脱离 Blender 即可运行。
- 🗣️ **自然语言驱动**：接入 DeepSeek 大模型，听懂中文意境描述并落地为场景配置。

---

## 🚀 完成进度

| 模块 | 内容 | 状态 |
| :--- | :--- | :---: |
| 🏗️ 基础框架 | iCity 城市生成 + smart_city 扩展接线 | ✅ |
| 🎨 资产扩充 | 新 2D 路面材质 / 程序化 3D 路灯 / 路边设施（花箱·公交站·长椅） | ✅ |
| 🧱 场景生成模板化 | 3 套"整城"模板，一键配置街道+交通+人群+生态 | ✅ |
| 🗣️ 自然语言交互编辑 | DeepSeek 解析中文 → 场景配置，含关键词规则兜底 | ✅ |
| 🚗 交通模拟 | 小汽车 / 出租 / 公交 沿路网动画，符合车道社会规则 | ✅ |
| 🚶 人群模拟 | 人行道行走 + 路口站立，动画 | ✅ |
| 🌄 生态元素 | 地形（山）/ 湖 / 河 / 船，三种地块模式 | ✅ |
| ✅ 单元测试 | 5 个测试文件、64 个用例全部通过 | ✅ |
| 📚 文档 | 各模块 README + 设计/计划文档 | ✅ |
| 🖥️ 前端原型 | 多角色登录 + 模板商城 + 进 Blender 模拟入口（React，已并入 `frontend/`） | ⏱ |

---

## 🧩 功能模块与用法

> 通用前提：启用 iCity 插件 → 3D 视口按 **N** 打开侧栏 → **ICity** 标签 → 点 **Start** 生成城市。
> 看真实材质/颜色：关掉 **Proxy mode** + 右上角切 **材质预览**；看动画：按 **空格** 播放。

<details open>
<summary><b>🎨 ICity Asset Expansion —— 资产扩充</b></summary>

- **2D 路面材质**：选风格（沥青带车道线 / 混凝土大道 / 暖色木栈道）→ `Create / Replace Texture`。
- **3D 路灯**：设数量/高度/亮度 → `Generate Streetlights`。
- **路边设施**：选类型（花箱 / 隔离柱 / 长椅 / 公交站）→ `Generate Roadside Props`。
</details>

<details>
<summary><b>🌄 ICity Ecology —— 生态（地形/湖/河/船）</b></summary>

- 选地块模式：**Lake + Mountains**（湖+山）/ **Mountain Only**（纯山）/ **River Valley**（河谷）。
- 调地形/湖/河/船参数 → `Add Plot`（生态地块生成在城市旁，缩小视角可见）。`Clear All` 清除。
</details>

<details>
<summary><b>🚗 ICity Traffic —— 交通</b></summary>

- 设 Cars / Taxis / Buses 数量 → `Generate / Update` → 按空格看车流沿路行驶。`Clear` 清除。
</details>

<details>
<summary><b>🚶 ICity Pedestrians —— 人群</b></summary>

- 设 Walkers / Idlers 数量 → `Generate / Update` → 按空格看行人在人行道上行走、路口站立。
</details>

<details open>
<summary><b>🧱🗣️ ICity Template —— 模板化生成 + 自然语言（本仓库重点）</b></summary>

面板"**模板化生成 Template**"（侧栏底部）：

- **① 选模板一键应用（整城）**：下拉选 `0 公园城市 / 1 金秋商业街 / 2 滨海社区` → `应用模板` → 街道资产 + 交通/人群/生态 一次配齐。
- **② 自然语言编辑**：输入中文 → `解析并应用`，详见下节。

| 模板 | 树/椅/路面 | 交通 | 人群 | 生态 |
| :--- | :--- | :--- | :--- | :--- |
| 0 公园城市 | 绿树·木椅·干净 | 稀疏(4/1/1) | 12/8 | 湖+山(4船) |
| 1 金秋商业街 | 金黄·现代椅·做旧 | 车水马龙(26/10/5) | 人潮(48/22) | 无 |
| 2 滨海社区 | 棕榈·木椅·干净 | 中等(8/2/1) | 20/10 | 河谷 |
</details>

---

## 🗣️ 自然语言编辑（LLM）

输入一句中文描述，系统调 **DeepSeek**（`deepseek-v4-flash`）解析成结构化配置并应用；**API key 已内置、开箱即用**；若网络异常/无 key 自动退回**关键词规则解析**（离线可演示，不翻车）。

### 🎛️ 能控制什么

| 类别 | LLM 可控 | 说明 |
| :--- | :--- | :--- |
| 树 / 座椅 / 路面 | ✅ | 从资产清单挑最贴切的 |
| 🚗 交通车流量 | ✅ | none / low / medium / high / max |
| 🚶 人群人流量 | ✅ | none / low / medium / high / max |
| 🛣️ 路面材质风格 | ✅ | 沥青 / 混凝土 / 木栈道 |
| 🌄 生态 | ✅ | 湖+山 / 纯山 / 河谷 / 去除 |
| 去掉某维度 | ✅ | "去掉车/去掉人/去掉山湖" → 清空对应内容 |

> 灯/隔离柱/路缘/人行道等用**模板**或**关键词规则**控制；LLM 专注最常用维度以保证解析准确率。

### 🎬 演示用 Prompt（均已实测可用）

```text
车水马龙、有山有湖、街上很多人，把树换成金黄的     → 金黄树 + 高车流 + 高人流 + 湖光山色 ⭐
打造车水马龙、人潮汹涌的繁华CBD                  → 高车流 + 高人流 + 车道线沥青
宁静的山中小镇，群山环绕，车很少没什么人          → 群山生态 + 稀疏车流人流
蜿蜒河谷边的度假村，木栈道，把树换成棕榈          → 棕榈 + 木栈道 + 河谷生态
深夜空城，街上没什么人也没什么车，路面破旧        → 脏旧路面 + 空旷低车流人流
去掉山和湖                                      → 清空生态地块
```

---

## 🗂️ 数据文件说明

### `iCity/smart_city/manifests/templates.json` —— 模板与资产数据（唯一源）

| 字段 | 记录内容 |
| :--- | :--- |
| `templates` | **3 套整城模板**。每个模板含 `plugin`（街道资产：树/座椅/路灯/隔离柱/路面/路缘/人行道 的真实资产名）+ `scene`（场景维度：路面材质/路灯/路边设施/交通/人群/生态 的具体参数）。 |
| `catalog` | **全量资产清单**，按类别（tree/bench/light/bollard/road_material/curb/sidewalk/…）列出每个资产的真实名 + **外观描述 desc**（供 LLM 理解）。 |
| `catalog_scene` | **场景维度配置**：每个维度的中文描述 + "定性档位 → 具体数值"换算表（如 traffic high → 车24/出租10/公交6）。 |

> 一个"模板"= 一份整城配方：记下用哪棵树、哪种路面、多少车、多少人、要不要山水。

### `iCity/smart_city/manifests/asset_manifest.json` —— 外部资产注册表

记录可加载的纹理/模型条目：`id`、显示名、`category`、文件路径（或 `procedural://` 程序化标记）、加载参数（车辆的旋转/缩放/车道偏移等）。如车辆 `1986 Chevrolet M1009`、`Low Poly Bus`、行人 FBX 等。

---

## ✅ 测试

脱离 Blender 的纯逻辑/几何单元测试（`unittest`），`tests/` 下 **5 个文件、64 个用例全部通过**。

| 测试文件 | 用例 | 测什么 |
| :--- | :---: | :--- |
| `test_asset_registry.py` | 4 | 资产注册表加载、按 id 查找、相对路径解析、缺失文件校验 |
| `test_smart_city_extensions.py` | 28 | 交通/人行道布局几何、车道/步道带计算、路线规划（注入 bpy 桩） |
| `test_smart_city_layout_samples.py` | 4 | 城市边界、生态/布局采样计算 |
| `test_smart_city_pedestrians.py` | 14 | 行人沿路网/兜底环线的路线规划、站立点选取 |
| `test_template_core.py` | 14 | 模板/自然语言**关键词解析**、**档位→数值换算**、"去掉"清空意图、`templates.json` 数据完整性（模板资产名/枚举合法） |

```bash
python -m unittest discover tests        # 全部 64 个
python tests/test_template_core.py       # 仅模板/自然语言 14 个
```

---

## 🛠️ 安装与运行

### 1. 克隆（含 Git LFS 大文件）

`.blend`、`.obj`、`.fbx`、`.glb`、`.gltf` 等 3D 资产由 **Git LFS** 管理：

```bash
git lfs install
git lfs pull
```

### 2. 安装插件

1. 打开 Blender（4.1）。
2. `Edit > Preferences > Add-ons > Install...` 选择本仓库 `iCity/` 目录（或其打包 zip）。
3. 启用 **ICity** 插件 → 侧栏（N）即出现 iCity 原有功能与各 smart_city 扩展面板。

### 3. 上手

`Start` 生成城市 → 用上面各面板生成/编辑 → 关 Proxy + 切材质预览看效果 → 按空格看动画。

> ℹ️ **复现说明**：正常使用与复现流程（装插件 → Start → 各面板）**无任何本地路径依赖**，相对路径即可在任意机器运行。
> 原版 iCity 自带一个开发用算子 `Store all assets`（导出资产清单到本地）内含原作者绝对路径，但它**不在城市生成链路中、仅手动触发、只写不读**，对复现无影响，可忽略。

---

## 📁 项目结构

```text
Software_Engineering_Smart_City/
├── iCity/                          # Blender 插件根目录
│   ├── __init__.py                 # iCity 原始入口 + smart_city 最小接线(register)
│   ├── assets/                     # 城市底板、车辆、行人等资产(LFS)
│   └── smart_city/                 # 团队扩展包
│       ├── asset_extension.py      # 资产扩充(材质/路灯/路边设施)
│       ├── ecology_*.py            # 生态(地形/湖/河/船)
│       ├── traffic_extension.py    # 交通
│       ├── pedestrian_extension.py # 人群
│       ├── template_core.py        # 模板/自然语言 纯逻辑(可测,含 LLM 客户端)
│       ├── template_extension.py   # 模板/自然语言 Blender 面板与算子
│       ├── asset_registry.py       # 资产注册表工具
│       ├── manifests/              # templates.json · asset_manifest.json
│       └── docs/                   # 各模块说明文档
├── frontend/                       # 前端原型(React+TS+Vite)：多角色登录 + 模板商城(详见 frontend/README.md)
└── tests/                          # 单元测试(64 用例)
```

---

## 📚 文档索引

- 资产扩充面板说明：[`iCity/smart_city/docs/README_ASSET.md`](iCity/smart_city/docs/README_ASSET.md)
- 生态水域与交通人群面板说明：[`iCity/smart_city/docs/README_ECOLOGY.md`](iCity/smart_city/docs/README_ECOLOGY.md)
- 模板化生成 + 自然语言面板说明：[`iCity/smart_city/docs/README_TEMPLATE.md`](iCity/smart_city/docs/README_TEMPLATE.md)
- 前端原型说明与运行：[`frontend/README.md`](frontend/README.md)
- 资产/交通人群/生态计划：[`docs/superpowers/plans/2026-05-31-smart-city-assets-traffic-ecology.md`](docs/superpowers/plans/2026-05-31-smart-city-assets-traffic-ecology.md)

---

<div align="center">

**当前开发分支：`qhr`** · 南开大学 2026 软件工程团队作业

</div>

[iCity]: https://icity3d.com/

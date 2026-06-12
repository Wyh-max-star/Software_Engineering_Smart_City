# Software_Engineering_Smart_City

南开大学 2026 春季《软件工程》课程项目，主题为智能城市生成系统。

本仓库基于 Blender iCity 插件扩展，提供资产扩充、交通车辆、人群模拟、生态场景、模板化生成、自然语言编辑和前端原型。

## 开发分支

当前团队开发主分支为 `zmk`。本分支已合入 `qhr` 的模板化生成、自然语言模块、前端原型和独立行人模块。

## 插件目录

Blender 插件根目录为：

```text
iCity/
```

智能城市扩展模块位于：

```text
iCity/smart_city/
```

## 大文件说明

`.blend`、`.obj`、`.fbx`、`.glb`、`.gltf` 等 3D 资产通过 Git LFS 管理。首次克隆后建议执行：

```bash
git lfs install
git lfs pull
```

## 安装方式

1. 打开 Blender 4.1。
2. 进入 `Edit > Preferences > Add-ons > Install...`。
3. 选择本仓库中的 `iCity/` 目录，或选择打包后的插件压缩包。
4. 启用 `ICity` 插件。
5. 在 Blender 右侧 `N` 面板的 `ICity` 标签页中使用原版 iCity 功能和 smart_city 扩展面板。

## 当前模块

- `ICity Asset Expansion`：道路 / 步道材质替换、程序化路灯、路边设施生成与清理。
- `ICity Ecology`：城市周边地形、湖泊、河流、船只和生态场景生成。
- `ICity Traffic`：基于 `iCity Start` 道路网络的车辆动画，支持小汽车、出租车、巴士。
- `ICity Pedestrians`：独立人群模块，支持行走行人和路口站立行人。
- `ICity Template`：模板化整城生成与自然语言编辑。
- `frontend/`：React + TypeScript + Vite 前端原型，包含多角色登录和模板商城界面。

## 交通车辆资产

当前交通模块优先使用真实 `.blend` 车辆资产：

- 小汽车 / 出租车：`iCity/assets/vehicles/1986_chevrolet_m1009.blend`
- 巴士：`iCity/assets/vehicles/lowpoly_bus.blend`

车辆资产已在 `iCity/smart_city/manifests/asset_manifest.json` 中注册为 `traffic_vehicle`。如果资产加载失败，交通模块会回退到程序化代理车辆，保证面板仍可使用。

## 模板与自然语言

模板和自然语言逻辑分为两层：

- `iCity/smart_city/template_core.py`：纯逻辑层，负责模板数据、自然语言解析、档位到数值的换算，便于单元测试。
- `iCity/smart_city/template_extension.py`：Blender 面板和算子层，负责应用模板和自然语言解析结果。

模板数据位于：

```text
iCity/smart_city/manifests/templates.json
```

自然语言模块支持 DeepSeek 解析，并保留关键词规则作为离线 fallback。

## 前端原型

前端项目位于：

```text
frontend/
```

常用命令：

```bash
cd frontend
npm install
npm run build
npm run dev
```

## 测试

Python 单元测试：

```bash
python -m unittest discover tests
```

常用聚焦测试：

```bash
python -m unittest tests.test_asset_registry tests.test_smart_city_extensions -v
python -m unittest tests.test_smart_city_pedestrians tests.test_template_core -v
```

前端构建验证：

```bash
cd frontend
npm run build
```

## 项目结构

```text
Software_Engineering_Smart_City/
|-- iCity/
|   |-- __init__.py
|   |-- assets/
|   `-- smart_city/
|       |-- asset_extension.py
|       |-- asset_registry.py
|       |-- ecology_common.py
|       |-- ecology_extension.py
|       |-- ecology_water.py
|       |-- traffic_extension.py
|       |-- pedestrian_extension.py
|       |-- template_core.py
|       |-- template_extension.py
|       |-- manifests/
|       `-- docs/
|-- frontend/
|-- docs/
`-- tests/
```

## 文档索引

- 总体计划：`docs/superpowers/plans/2026-05-31-smart-city-assets-traffic-ecology.md`
- `add111` 合入评估：`docs/add111-integration-assessment.md`
- 资产扩充说明：`iCity/smart_city/docs/README_ASSET.md`
- 生态模块说明：`iCity/smart_city/docs/README_ECOLOGY.md`
- 交通模块说明：`iCity/smart_city/docs/README_TRAFFIC.md`
- 行人模块说明：`iCity/smart_city/docs/README_PEDESTRIAN.md`
- 模板 / 自然语言说明：`iCity/smart_city/docs/README_TEMPLATE.md`
- 前端原型说明：`frontend/README.md`

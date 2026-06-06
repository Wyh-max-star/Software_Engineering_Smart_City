# Software_Engineering_Smart_City

南开大学 2026 春季《软件工程》课程项目，主题为智能城市生成系统。

## 开发分支

当前团队开发分支为 `zmk`。

## Blender 插件目录

本仓库使用 `iCity/` 作为 Blender 插件根目录，智能城市扩展代码位于：

```text
iCity/smart_city/
```

## 大文件说明

`.blend`、`.obj`、`.fbx`、`.glb`、`.gltf` 等 3D 资产通过 Git LFS 管理。首次克隆后建议执行：

```bash
git lfs install
git lfs pull
```

## 插件安装方式

1. 打开 Blender。
2. 进入 `Edit > Preferences > Add-ons`。
3. 选择 `Install...`，安装仓库中的 `iCity` 插件目录或打包后的插件压缩包。
4. 启用 `ICity` 插件。
5. 在 Blender 右侧 `N` 面板中使用 iCity 原有功能与 `smart_city` 扩展功能。

## 文档索引

- 总体计划：`docs/superpowers/plans/2026-05-31-smart-city-assets-traffic-ecology.md`
- `add111` 合入评估：`docs/add111-integration-assessment.md`
- 资产扩充面板说明：`iCity/smart_city/docs/README_ASSET.md`
- 生态面板说明：`iCity/smart_city/docs/README_ECOLOGY.md`
- 交通与人群面板说明：`iCity/smart_city/docs/README_TRAFFIC.md`
- 交通车辆资产接入计划：`docs/superpowers/plans/2026-06-06-icity-traffic-vehicle-asset.md`

## 当前扩展面板

`add111` 的功能模块已经按规范化文件名合入 `iCity/smart_city/`，并通过 `iCity/__init__.py` 做最小接线。

- `ICity Asset Expansion`：道路 / 步道材质替换、程序化路灯生成与清理。
- `ICity Ecology`：地形、湖泊、河流、船只、生态资产与动画场景生成。
- `ICity Traffic & Crowd`：基于 `iCity Start` 道路网络的车辆 / 人群动画。当前车辆支持小汽车、出租车、巴士；小汽车 / 出租车优先使用 `1986 Chevrolet M1009` 资产，巴士优先使用 `Low Poly Bus` 资产，资产缺失时回退到程序化代理模型。

## 当前交通资产

- `iCity/assets/vehicles/1986_chevrolet_m1009.blend`
- `iCity/assets/vehicles/lowpoly_bus.blend`

它们都已在 `iCity/smart_city/manifests/asset_manifest.json` 中注册为 `traffic_vehicle`。

## 说明

合入时没有覆盖 `add111/__init__(1).py`，避免替换 iCity 原始入口文件。

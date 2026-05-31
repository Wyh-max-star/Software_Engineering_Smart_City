# Software_Engineering_Smart_City
南开大学26年软件工程小组作业，智能城市生成系统

## 开发分支

当前团队开发分支为 `zmk`。

## Blender 插件目录

本仓库使用 `iCity/` 作为 Blender 插件基础目录，后续智能城市扩展模块放在：

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
3. 选择 `Install...`，安装本仓库中的 `iCity` 插件目录或打包后的插件压缩包。
4. 启用 `ICity` 插件。
5. 在 Blender 侧边栏中使用 iCity 原有功能和 `smart_city` 扩展功能。

## 文档索引

- 资产、交通人群、生态元素计划：`docs/superpowers/plans/2026-05-31-smart-city-assets-traffic-ecology.md`
- `add111` 合入评估：`docs/add111-integration-assessment.md`
- 资产扩充面板说明：`iCity/smart_city/docs/README_ASSET.md`
- 生态水域与交通人群面板说明：`iCity/smart_city/docs/README_ECOLOGY.md`

## 当前扩展面板

`add111` 的功能模块已按规范化文件名合入 `iCity/smart_city/`，并通过 `iCity/__init__.py` 进行最小接线。

- `ICity Asset Expansion`：道路/步道材质替换、程序化路灯生成与清理。
- `ICity Ecology`：地形、湖泊、河流、船只、车辆、人群、路径动画生成与清理。

合入时没有复制 `add111/__init__(1).py`，避免覆盖 iCity 原始入口文件。

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

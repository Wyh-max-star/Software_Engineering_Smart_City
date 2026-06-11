# ICity 布局控制使用与验收指南

本文档面向第一次使用 Blender 和 ICity 布局控制功能的用户，同时也可作为课程项目的功能验收清单。

## 1. 功能目标

`ICity Layout Control` 用于控制 ICity 的道路和城市块布局，支持：

- 查看当前城市中的节点坐标、道路连接关系和面数量；
- 在 UI 中添加、删除、修改节点和道路边；
- 校验并整理道路拓扑；
- 在不修改真实城市的情况下预览 Draft；
- 从黑线草图中自动提取节点和道路；
- 将确认后的 Draft 应用到真实 `ICity Base`，生成道路、城市块和建筑。

## 2. 核心概念

### 2.1 ICity Base

`ICity Base` 是真实城市使用的基础网格：

- 点表示道路节点；
- 边表示道路连接；
- 闭合道路围成的面表示城市块；
- ICity 根据这些点、边、面生成道路、建筑和其他资产。

### 2.2 Draft

Draft 是布局控制面板中的可编辑草稿。

加载当前城市、手动增删点线、导入 JSON 和导入草图，修改的都是 Draft。只有点击 `Apply Draft Layout` 并确认后，Draft 才会替换真实 `ICity Base`。

### 2.3 Preview

Preview 是显示在视口中的蓝色道路、橙色节点和半透明城市块，仅用于检查 Draft，不会修改真实城市。

## 3. 使用前准备

1. 使用 Blender 4.1 打开项目并启用 ICity 插件。
2. 在右侧 ICity 原始面板中点击 `Start`，生成初始城市。
3. 将鼠标放在 3D 视口中，按 `N` 打开右侧栏。
4. 切换到 `ICity` 标签页，找到 `ICity Layout Control`。
5. 点击 `Inspect ICity Base Contract`。

检查成功后，面板会显示当前城市的节点、边、面和属性数量，并显示完整布局编辑功能。

草图导入依赖 Blender 自带 Python 环境中的 OpenCV。若面板提示缺少 OpenCV，可在命令行执行：

```powershell
"<Blender安装目录>\4.1\python\bin\python.exe" -m pip install opencv-python
```

## 4. 推荐的标准操作流程

每次修改布局时，建议严格按照以下顺序操作：

1. 获取 Draft：
   - 修改当前城市：点击 `Load Draft From ICity Base`；
   - 使用草图：选择图片并点击 `Import Sketch To Draft`；
   - 使用结构化数据：选择 JSON 并点击 `Import JSON To Draft`。
2. 在 `Editable Nodes` 和 `Editable Edges` 中检查或修改点线。
3. 点击 `Validate Draft` 检查错误。
4. 根据需要点击 `Normalize Draft` 整理拓扑。
5. 点击 `Show / Refresh Draft Preview` 检查视觉效果。
6. 保存 `.blend` 文件或创建副本。
7. 点击 `Apply Draft Layout`，检查确认框中的当前和目标拓扑数量。
8. 确认应用，等待 ICity 重新生成道路与城市内容。

## 5. 查看当前布局

### 操作步骤

1. 点击 `Inspect ICity Base Contract`。
2. 查看 `Current ICity Base` 区域：
   - `Nodes`：节点数量；
   - `Edges`：边数量；
   - `Faces`：城市块面数量；
   - `Attributes`：ICity 网格属性数量。
3. 在 `Nodes` 区域查看每个节点的 X、Y、Z 坐标。
4. 在 `Edges` 区域查看每条边连接的节点及道路启用状态。

### 预期结果

- 初始城市通常可以看到若干节点、道路边和至少一个面。
- 该操作只读取信息，不会修改城市。

## 6. 手动编辑点和道路

### 6.1 加载当前城市为 Draft

点击 `Load Draft From ICity Base`。

加载完成后：

- `Editable Nodes` 显示所有节点；
- `Editable Edges` 显示所有道路连接；
- 顶部摘要显示 Draft 的节点数、边数和校验结果。

### 6.2 修改节点坐标

1. 在 `Editable Nodes` 中选择一个节点。
2. 修改下方的 `X`、`Y`、`Z` 数值。
3. 点击 `Show / Refresh Draft Preview`。

预期结果：橙色节点和相连的蓝色道路移动到新位置，真实城市暂时不变。

布局使用 `ICity Base` 的局部 XY 平面。正常道路布局中，Z 通常保持为 `0`。

### 6.3 添加节点

1. 点击 `Add Node`。
2. 系统自动分配节点 ID，例如 `n4`。
3. 设置节点的 X、Y、Z 坐标。

新节点只有在被道路边引用后才会参与道路布局。

### 6.4 删除节点

1. 在 `Editable Nodes` 中选择节点。
2. 点击 `Remove Node`。

删除节点时，与该节点连接的 Draft 边也会同时删除。

### 6.5 添加道路边

1. 点击 `Add Edge`。
2. 在新边的 `start` 和 `end` 字段中填写已有节点 ID。
3. 保持 `enabled_as_road` 开启。
4. 点击 `Validate Draft`。

预期结果：校验无错误，刷新 Preview 后出现对应道路。

### 6.6 删除或禁用道路边

- 删除道路：选中边并点击 `Remove Edge`。
- 暂时不生成道路：关闭该边的 `enabled_as_road`。

关闭的边仍保留在 Draft 数据中，但应用后不会生成道路，也不会参与城市块闭环推断。

## 7. Draft 校验与拓扑整理

### 7.1 Validate Draft

`Validate Draft` 检查：

- 节点 ID 是否为空或重复；
- 边的 ID 是否为空或重复；
- 边引用的起点和终点是否存在；
- 是否存在自连接边；
- 是否存在重复道路。

有 `ERROR` 时不要应用 Draft，应先修正对应节点或边。

### 7.2 Normalize Draft

`Normalize Draft` 会：

- 合并距离过近的节点；
- 将落在道路内部的节点连接到道路；
- 在道路交叉处创建共享节点并拆分道路；
- 删除自连接、重复和过短的边。

参数说明：

| 参数 | 作用 | 建议 |
|---|---|---|
| `Merge Distance` | 小于该距离的节点会合并 | 默认 `0.1`；草图节点过密时可适当调大 |
| `Intersection Tolerance` | 判断道路交叉或节点落在线上的误差 | 通常保持默认值 |
| `Minimum Edge Length` | 小于该长度的边会删除 | 通常保持默认值 |

Normalize 会修改 Draft，但不会修改真实城市。

## 8. Draft 可视化预览

点击 `Show / Refresh Draft Preview` 后：

- 橙色几何体表示节点；
- 蓝色带状几何体表示启用的道路；
- 禁用道路使用单独的预览对象；
- 半透明区域表示识别到的闭合城市块。

预览参数：

- `Preview Road Width`：蓝色道路预览宽度；
- `Preview Node Radius`：橙色节点大小；
- `Preview Height`：预览相对真实城市的高度。

点击 `Clear Draft Preview` 只会清除预览，不会删除 Draft 或真实城市。

## 9. 草图布局输入

### 9.1 草图绘制要求

推荐使用以下格式：

- 白色背景；
- 黑色单线表示道路中心线；
- 尽量使用清晰、连续的线；
- 需要相交的道路应真正接触；
- 避免文字、阴影、装饰和复杂背景；
- PNG 图片优先。

手绘草图可以使用，但识别结果通常需要在 Draft 中人工检查和修正。

### 9.2 草图导入步骤

1. 在 `Import Black-Line Sketch` 区域选择草图图片。
2. 设置参数，首次测试建议：

| 参数 | 推荐值 | 说明 |
|---|---:|---|
| `Dark Threshold` | `0.45` | 越大越容易把灰色像素识别为道路 |
| `Layout Width` | `300` 至 `500` | 控制生成布局的实际宽度；太小可能没有足够空间生成建筑 |
| `Max Processing Size` | `512` | 控制识别图像尺寸 |
| `Endpoint Snap Distance` | `2.5` | 合并距离较近的草图端点 |
| `Straighten Angle` | `20` | 清理由像素锯齿产生的小折点 |

3. 点击 `Import Sketch To Draft`。
4. 检查自动生成的 Preview 和节点、边列表。
5. 点击 `Validate Draft`。
6. 必要时修改点线或执行 `Normalize Draft`。
7. 确认后点击 `Apply Draft Layout`。

### 9.3 草图导入的预期行为

- 草图会替换当前 Draft。
- 草图不会立即修改真实城市。
- Apply 后，Draft 会替换原有城市布局，不会与原布局重叠。
- 闭合道路会成为城市块面。
- 城市块足够大时，ICity 会在其中生成建筑。

## 10. 应用 Draft 到真实城市

### 操作步骤

1. 确保 `Validate Draft` 没有错误。
2. 点击 `Apply Draft Layout`。
3. 在确认框中检查：
   - `Current`：当前真实城市的节点、边、面数量；
   - `Target`：即将应用的节点、边、推断面数量。
4. 点击确认。

### 预期结果

- 原有 `ICity Base` 点、边、面被替换；
- 启用的道路边生成真实道路；
- 闭合道路生成 Procedural 城市块；
- 面积足够大的城市块生成建筑；
- Blender 不闪退；
- 面板摘要显示应用后的节点、道路和城市块数量。

Apply 是替换操作。执行前建议保存 `.blend` 文件或创建副本。

## 11. 查看诊断日志

每次 Apply 都会写入 `ICity Layout Diagnostic Log`。

打开方法：

1. 点击任意区域左上角的“编辑器类型”图标。
2. 选择 `Text Editor`。
3. 在 Text Editor 顶部的数据块下拉框中选择 `ICity Layout Diagnostic Log`。

矩形布局成功应用时，日志应类似：

```text
Draft: 4 nodes, 4 edges, 1 faces
Created 4 nodes, 4 edges, and 1 faces
Assigned Road del=False to 4 enabled roads
Assigned space type=Procedural to 1 faces
After: 4 nodes, 4 edges, 1 faces
space type check: 1 Procedural faces of 1
```

出现问题时，应保留完整日志、草图原图和操作步骤。

## 12. 功能验收测试清单

以下测试建议在全新的 Blender 场景中分别执行。每次复杂测试前重新点击 ICity `Start` 或保存独立 `.blend` 文件。

### 测试 A：启动与布局读取

1. 点击 ICity `Start`。
2. 打开 `ICity Layout Control`。
3. 点击 `Inspect ICity Base Contract`。
4. 点击 `Load Draft From ICity Base`。

通过标准：

- 面板显示节点、边、面和属性数量；
- Editable Nodes 和 Editable Edges 中存在数据；
- 没有报错，城市没有变化。

### 测试 B：手动修改节点坐标

1. 加载当前城市 Draft。
2. 选择一个节点，记录原 X、Y。
3. 将 X 或 Y 修改一个明显数值，例如增加 `20`。
4. 刷新 Draft Preview。

通过标准：

- 对应节点和相连道路预览发生移动；
- 真实城市在 Apply 前保持不变；
- Validate Draft 没有错误。

### 测试 C：手动增删点和道路

1. 点击 `Add Node`，设置坐标。
2. 点击 `Add Edge`，填写新节点与已有节点的 ID。
3. Validate 并刷新 Preview。
4. 删除刚添加的节点。

通过标准：

- 添加后 Preview 出现新节点和道路；
- 删除节点后，与其相连的边同步删除；
- Validate 不出现悬空节点引用错误。

### 测试 D：交叉道路规范化

1. 创建两条几何上相交、但不共享中心节点的道路边。
2. 点击 `Normalize Draft`。

通过标准：

- 交叉位置新增共享节点；
- 两条道路被拆分；
- Preview 中道路在交叉位置正确连接。

### 测试 E：矩形草图识别

准备一张白底黑线矩形图片。

1. 设置 `Layout Width` 为 `300` 至 `500`。
2. 点击 `Import Sketch To Draft`。
3. Validate 并刷新 Preview。
4. 点击 `Apply Draft Layout`。

通过标准：

- Draft 约为 `4 nodes, 4 edges, 1 face`；
- Apply 后形成闭合道路；
- 内部存在一个真实城市块面；
- 城市块尺寸足够时出现建筑；
- 日志中的最终数量与目标一致。

### 测试 F：田字草图识别

准备一张白底黑线田字图片。

1. 导入草图。
2. 检查 Preview。
3. 点击 Apply。

通过标准：

- 道路结构与田字草图基本一致；
- 多个城市块生成道路和建筑；
- Blender 不闪退。

已知限制：当前闭环推断可能将田字外层总闭环也识别为一个面，因此可能得到 `5 faces`，而不是仅有四个最小城市块。该问题不影响核心道路与城市生成功能。

### 测试 G：错误 Draft 拦截

1. 在某条边的端点字段中填写不存在的节点 ID，例如 `missing`。
2. 点击 `Validate Draft`。
3. 尝试刷新 Preview 或 Apply。

通过标准：

- 面板显示缺失节点引用错误；
- Preview 或 Apply 被阻止；
- 真实城市保持不变；
- Blender 不闪退。

### 测试 H：真实布局应用与日志

1. 使用一个通过 Validate 的矩形 Draft。
2. 点击 `Apply Draft Layout` 并确认。
3. 打开 `ICity Layout Diagnostic Log`。

通过标准：

- 道路、面和建筑正常生成；
- 日志包含创建节点、边、面以及设置 `Road del`、`space type` 的记录；
- 最终数量与目标数量一致；
- 无 `ERROR`，Blender 不闪退。

## 13. JSON 辅助输入

JSON 输入是辅助批量输入和测试方式，不是完成手动布局控制的必需步骤。

示例矩形：

```json
{
  "version": 1,
  "nodes": [
    {"id": "n0", "x": 0, "y": 0, "z": 0},
    {"id": "n1", "x": 100, "y": 0, "z": 0},
    {"id": "n2", "x": 100, "y": 100, "z": 0},
    {"id": "n3", "x": 0, "y": 100, "z": 0}
  ],
  "edges": [
    {"id": "e0", "start": "n0", "end": "n1", "enabled_as_road": true},
    {"id": "e1", "start": "n1", "end": "n2", "enabled_as_road": true},
    {"id": "e2", "start": "n2", "end": "n3", "enabled_as_road": true},
    {"id": "e3", "start": "n3", "end": "n0", "enabled_as_road": true}
  ],
  "faces": []
}
```

导入后系统会根据闭合道路推断城市块面。

## 14. 开发测试命令

在项目根目录运行：

```powershell
python -m py_compile iCity\smart_city\layout_control.py iCity\smart_city\layout_sketch.py
python -m unittest tests.test_smart_city_extensions -v
```

完整项目测试：

```powershell
python -m unittest discover tests
```

## 15. 已知限制

- 田字等嵌套道路图可能额外生成外层闭环面。
- 草图识别结果是可编辑初稿，不保证与原图逐像素一致。
- 抗锯齿、线条过粗、交点不清晰可能产生额外节点或边。
- 过小城市块可能有道路和面，但没有足够空间生成建筑。

# ICity 生态水域与交通人群扩展说明

这个扩展现在已经按功能拆分成多文件结构，目的是：

- 降低后续 merge 冲突
- 让生态块和交通块可以独立维护
- 让面板入口和功能实现解耦

## 当前文件结构

扩展相关文件现在是这 4 个：

- `ecology_extension.py`
- `ecology_common.py`

## 2026-06-03 Update

- The ecology generation flow now also creates a dedicated collection: `ICity Ecology Assets`.
- This collection currently contains three procedural lakefront asset types:
  - `Dock Pier`
  - `Tree Cluster`
  - `Shrub Patch`
- Placement is deterministic from the same layout seed used by the ecology block.
- The asset anchors are computed in `ecology_common.py`.
- The Blender mesh generation for these assets lives in `ecology_water.py`.
- Validation steps are documented in `BLENDER_VALIDATION_PHASE2.md`.
- `ecology_water.py`
- `ecology_traffic.py`

另外原插件只做极少量挂接：

- `__init__.py`

## 每个文件负责什么

### `ecology_extension.py`

这是总入口文件，只负责：

- Blender 面板 UI
- 参数定义 `PropertyGroup`
- 操作符 `Generate / Update`、`Clear`
- 总调度
- 注册 / 注销

如果后续要改这些内容，主要改这里：

- 新增参数滑块
- 新增按钮
- 修改面板布局
- 调整哪个按钮调用哪个功能模块

### `ecology_common.py`

这是公共工具文件，负责两大模块都要复用的底层能力：

- 集合创建和清理
- mesh 创建
- 路径动画的公共封装
- 材质辅助函数
- 计算城市边界
- 共享几何工具
- 共享布局计算

如果后续是“工具层能力”变动，改这里。

### `ecology_water.py`

这是生态水域模块，负责：

- 城市外围地形
- 湖泊
- 河流
- 动态船只

也就是说，你负责的“地形、河流、船只等生态化元素”核心逻辑主要在这里。

### `ecology_traffic.py`

这是交通与人群模块，负责：

- 动态汽车
- 动态行人
- 环形景观道路
- 湖边步道
- 对应的路径动画

## 为什么这样拆

这样拆之后，入口和功能就分开了：

- 改 UI 时，不必碰具体功能算法
- 改生态逻辑时，不必碰交通逻辑
- 改交通逻辑时，也不必碰生态逻辑

最重要的是，队友以后不需要都挤在一个大文件里改。

## 两个功能块

面板里仍然保留两大块：

- `Ecology / Lake Block`
- `Traffic & Crowd Block`

### 模块一：生态水域块

负责：

- 山地地形
- 湖泊
- 河流
- 船只

主要参数：

- `Enable Ecology`
- `Terrain Margin`
- `Terrain Resolution`
- `Mountain Height`
- `Terrain Noise`
- `Lake Radius`
- `Lake Depth`
- `Generate River`
- `River Width`
- `River Depth`
- `Boat Count`

核心代码文件：

- `ecology_water.py`

### 模块二：交通与人群块

负责：

- 汽车
- 人群
- 环路
- 步道

主要参数：

- `Enable Traffic & Crowd`
- `Car Count`
- `Crowd Count`
- `Road Width`
- `Traffic Radius X`
- `Traffic Radius Y`
- `Walkway Width`
- `Walkway Offset`
- `Car Scale`
- `Pedestrian Scale`

核心代码文件：

- `ecology_traffic.py`

## 队友后续应该怎么改

推荐分工方式：

- 改面板和参数：改 `ecology_extension.py`
- 改生态功能：改 `ecology_water.py`
- 改交通人群功能：改 `ecology_traffic.py`
- 改底层通用工具：改 `ecology_common.py`

这样最稳。

不推荐的方式：

- 所有人都继续改 `ecology_extension.py`

那样会重新回到“大文件冲突”的老问题。

## Blender 4.1 使用方式

1. 把整个 `icity` 文件夹放到 Blender 4.1 的插件目录
2. 启动 Blender 4.1
3. 在 `Edit > Preferences > Add-ons` 中启用 `ICity`
4. 打开 3D View 右侧侧边栏，找到 `ICity`
5. 在原始面板点击 `Start`
6. 打开新增的 `ICity Ecology` 面板
7. 选择启用 `Ecology / Lake Block`、`Traffic & Crowd Block` 或两者都启用
8. 点击 `Generate / Update`

如果需要清空本扩展生成的内容，点击 `Clear`。

## 运行生成后会出现的集合

扩展会在原始 `ICity` 集合下面生成：

- `ICity Ecology`
- `ICity Ecology Terrain`
- `ICity Ecology Water`
- `ICity Ecology Boats`
- `ICity Ecology Traffic`
- `ICity Ecology Crowd`
- `ICity Ecology Paths`

## 合并方式

如果队友要把这部分合进他们的版本，最小改动方式还是：

1. 复制这 4 个扩展文件
2. 保留 `__init__.py` 中已有的 `ecology_extension` 导入
3. 保留 `register()` 中的 `ecology_extension.register()`
4. 保留 `unregister()` 中的 `ecology_extension.unregister()`

也就是说，原插件仍然只知道一个入口：

- `ecology_extension.py`

而入口文件再去调用其他两个功能模块和一个公共模块。

## 当前结构的好处

- 插件外部入口没变
- 面板位置没变
- 使用方式没变
- 代码结构明显更清晰
- 后续你和队友都更容易分开改

## 代码定位建议

如果你以后只看自己负责的生态块，优先看：

- `ecology_water.py`

如果要改 UI 和参数，优先看：

- `ecology_extension.py`

如果要改交通/人群，优先看：

- `ecology_traffic.py`

如果要改共用底层工具，再看：

- `ecology_common.py`

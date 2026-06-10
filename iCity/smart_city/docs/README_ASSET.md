# ICity 资产扩充模块说明

这个模块对应作业里的这一项：

- 资产扩充：在现有系统中添加新的 2D 资产，并支持场景内纹理替换；添加至少一个新的 3D 资产，并确保其可以加载到场景中。

本次实现遵循和前两个模块一致的原则：

- 尽量少改原项目
- 不去重写原有大面板
- 单独增加一个扩展面板
- 方便后续和队友 merge


## 本次改动的文件

### 新增文件

- `asset_extension.py`
- `README_ASSET.md`

### 修改文件

- `__init__.py`

`__init__.py` 只做了最小接线：

- 导入 `asset_extension`
- 在 `register()` 中调用 `asset_extension.register()`
- 在 `unregister()` 中调用 `asset_extension.unregister()`

也就是说，原插件主体逻辑没有被重构，只是多挂了一个独立扩展模块。


## 模块结构设计

这次没有再拆成多个 `py` 文件，原因是这个“资产扩充”本身就是一个独立面板，内部虽然分成 `2D` 和 `3D` 两块，但它们都只服务于一个扩展入口。

所以现在的职责是：

- `asset_extension.py`
  - 面板
  - 属性
  - 2D 纹理资产生成与替换
  - 3D 路灯资产生成与清理

如果后面你们组还要继续扩展很多资产类型，再把它拆成：

- `asset_extension.py`
- `asset_surface.py`
- `asset_streetlight.py`

也完全可以。


## 模块一：2D 纹理资产

这一块完成的是：

- 新增至少一种新的 2D 资产
- 支持在场景中进行纹理替换

当前实现里，实际上做了 3 套可切换的表面资产：

- `Asphalt Marked`
  - 带道路标线的沥青道路材质
- `Concrete Boulevard`
  - 城市混凝土道路材质
- `Boardwalk Warm`
  - 暖色木质步道材质

### 实现方式

优先复用项目里已有的本地纹理：

- `assets/textures/Road 4 clean_BaseColor.jpg`
- `assets/textures/Concrete014_2K-JPG_Color.jpg`
- `assets/textures/1K-american_oak_2_basecolor-min.jpg`

以及对应 roughness / normal / detail 纹理。

如果这些纹理在目标环境中缺失，代码会自动回退到程序化材质，不会直接报废。

### 和原 ICity 系统的兼容方式

推荐模式是：

- `Apply Target = ICity Road System`

在这个模式下，扩展模块会优先尝试直接写入原 ICity 道路系统：

- `Road 2` 节点组
- `Road / Curb / Sidewalk` 材质槽

也就是说，它不是简单地在外面新建一个平面，而是尽量把新材质接到原有道路系统里。

同时，如果场景里存在：

- `ICity_Materials`

新材质还会被顺带注册进去，方便继续被原系统识别。

### 备用模式

如果目标场景的原始道路节点结构和预期不完全一致，还可以使用：

- `Auto Discover`
- `Selected Objects`

这两种模式会直接把新材质替换到道路、步道、路沿等对象上。


## 模块二：3D 路灯资产

这一块完成的是：

- 新增至少一个新的 3D 资产类型
- 确保其能够生成到场景中

当前实现的 3D 资产是：

- `Streetlight`

### 实现方式

不依赖外部模型文件，直接通过代码程序化生成：

- 底座
- 灯杆
- 横臂
- 灯头
- 自发光灯罩
- 点光源

这样做的好处是：

- 不需要额外下载 `.blend` / `.fbx` / `.obj`
- 更容易在 Windows 目标环境中直接运行
- 不容易因为资源路径问题失效

### 生成位置

路灯和 roadside 资产现在都使用独立生成方式，只在城市外围安全带中布置，不再直接改写原始 `ICity Road` / `Road 2` 的路侧资产插槽。

生成后的对象会被放到单独的集合里：

- `ICity Asset Expansion`
- `ICity Asset Streetlights`

这样清理时不会误删原有城市内容。


## 是否需要外部图片或模型？

不需要。

本次实现默认不依赖外部下载资源：

- 2D 纹理优先复用仓库现有 `assets/textures`
- 3D 路灯直接程序化建模

所以你现在不用再去网上找图片或者找路灯模型。

如果后面你想把展示效果再做得更“像商品级资产”，可以后续再补：

- 更高质量道路贴图
- 更精细的路灯模型
- 对应预览图标

但这不是当前模块运行的前置条件。


## Blender 4.1 使用方式

注意：我当前这台机器没有安装 Blender，所以这里只能做静态代码校验，不能做真实界面点击测试。

目标运行流程如下：

1. 在 Blender 4.1 中安装或启用 `icity` 插件
2. 打开 `3D View`
3. 在右侧 `ICity` 面板中，先使用原始功能点击 `Start`
4. 找到新增面板：
   - `ICity Asset Expansion`

### 使用 2D 纹理资产

1. 选择 `Surface Style`
2. 选择 `Apply Target`
3. 如果是 `ICity Road System`，再选择：
   - `Road`
   - `Curb`
   - `Sidewalk`
4. 点击：
   - `Create / Replace Texture`

### 使用 3D 路灯资产

1. 设置：
   - `Streetlight Count`
   - `Streetlight Offset`
   - `Streetlight Height`
   - `Arm Length`
   - `Lamp Power`
   - `Glow Strength`
2. 点击：
   - `Generate Streetlights`

### 清理生成资产

点击：

- `Clear`

会清理这个模块生成的路灯和 roadside 资产，以及对应的扩展挂接；不会删除原始 ICity 城市场景。


## merge 建议

如果你后面要和队友合并，建议按下面的理解处理：

### 这部分主要由你负责的文件

- `asset_extension.py`
- `README_ASSET.md`

### 可能发生冲突的文件

- `__init__.py`

因为所有人最后都可能在这里挂自己的扩展入口。

### 合并时要保留的内容

在 `__init__.py` 顶部导入区，保留：

- `asset_extension`

在 `register()` 末尾，保留：

- `asset_extension.register()`

在 `unregister()` 末尾，保留：

- `asset_extension.unregister()`

如果你队友也新增了别的扩展模块，最后就是并列保留各自的导入和注册调用，不要互相覆盖。


## 你后面如果要继续改，应该改哪里

- 改 2D 纹理逻辑：改 `asset_extension.py`
- 改 3D 路灯逻辑：改 `asset_extension.py`
- 改接线：改 `__init__.py`

因为这次模块规模还不大，所以暂时没有再拆子文件。


## 当前已确认的内容

- 独立扩展面板方案已接入
- 2D 纹理资产可创建并替换
- 3D 路灯资产可生成与清理
- 不依赖外部下载图片或模型

## 当前未能本地确认的内容

- Blender 4.1 真机界面点击结果
- 原始城市中的默认路灯和道路节点组不应该被这个扩展清空或改写

如果目标环境里原始道路节点命名有变化，也不用推倒重来，改 `asset_extension.py` 里的常量即可：

- `ICITY_ROAD_NODE_GROUP`
- `ICITY_ROAD_OBJECT`
- `ICITY_MATERIAL_LIBRARY_OBJECT`

## Phase 2 Placement Note

The current phase-2 placement behavior is road-system-first for supported 3D assets:

- `Streetlight` uses standalone perimeter placement
- `Bench` uses standalone perimeter placement
- `Bollard` uses standalone perimeter placement

If those original iCity sockets are unavailable in the running Blender scene, the extension falls back to the previous outer-band placement logic instead of failing.

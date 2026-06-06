# ICity Pedestrians（行人模拟）

## 这个模块做了什么

`ICity Pedestrians` 是 `smart_city` 文件夹下新增的一个**独立扩展面板**，与已有的
`ICity Traffic & Crowd`（交通）和 `ICity Ecology`（河流 / 生态）并列，挂在原版
`iCity Start` 之上。

它的目标是：**用项目自带的真实角色动画，把城市填上符合社会常理的行人。**

与原交通模块里那种“低多边形小方块行人”不同，本模块直接导入并播放：

- `iCity/assets/Assets/Default/People/Walking.fbx` —— 行走循环动画，用于**移动的行人**；
- `iCity/assets/Assets/Default/People/Standing.fbx` —— 站立 / 待机动画，用于**停留的行人**。

新增 / 修改的文件：

| 文件 | 说明 |
| --- | --- |
| `smart_city/pedestrian_extension.py` | 行人模拟的全部逻辑、操作符与面板（新增） |
| `iCity/__init__.py` | 注册 / 注销新模块（修改：导入、`register`、`unregister`） |
| `smart_city/manifests/asset_manifest.json` | 登记两个 People FBX 资产，便于路径校验（修改） |
| `smart_city/docs/README_PEDESTRIAN.md` | 本说明文档（新增） |
| `tests/test_smart_city_pedestrians.py` | 纯逻辑单元测试（新增） |

## 怎么体现“社会常理”

行人不是随机乱走的，本模块刻意编码了几条日常生活中的规律：

1. **走真实的人行道，不走机动车道 / 停车位。**
   模块复用交通模块的道路图提取（`ICity Base` 网格上的 `Road del` 道路属性）。
   关键改进：横向偏移量**不再靠猜**，而是直接读取 iCity 在每条道路边上存的
   `Road lanes width`（车行道总宽）和 `side walk offset`（人行道宽）属性，
   把行人放到 `车行道半宽 + 人行道宽/2` 处——也就是**人行道正中**，
   而不是落在车道或路边停车位上。读不到属性时才退回到面板里的估计值。
   （实现见 `read_pedestrian_offset_from_scene`。）

2. **两侧人行道方向相反（靠一侧通行）。**
   同一条街的左右两条人行道被生成为**方向相反**的两条路线，
   模拟现实中“各走各的一侧”的双向人流，而不是所有人挤在一条线上。

3. **面朝行进方向。**
   每个行人挂在一个沿路径运动的载体（carrier）上，载体每帧根据前进方向计算偏航角
   （`_keyframe_pedestrian_motion`），角色因此总是“脸朝着前进方向”走。

4. **走走停停。**
   载体并不是匀速绕圈，而是**走一段、停一会儿**：按 `Stop Chance` 概率随机插入
   “保持原地”的停顿关键帧，模拟行人偶尔驻足。速度由 `Walk Speed` 控制（见下）。

5. **停留的人站在路口 / 转角，面朝街道。**
   站立行人取自道路链的**端点（即路口）与中点**，被推到人行道上，并旋转到**回望街道**的朝向，
   就像在路口等待、张望的人。

6. **人群不整齐划一。**
   - 步速带随机扰动（`Speed Variation`），有人走得快有人走得慢；
   - 沿人行道有相位错开（phase），不会所有人挤成一团；
   - 横向有抖动（`Lateral Jitter`），不会排成一条直线；
   - 站立行人的朝向带小幅随机偏转，不会齐刷刷正对同一方向。

7. **没有可读道路图时的兜底。**
   如果当前场景拿不到道路属性，模块会退回到城市外圈的椭圆环形人行道
   （`plan_fallback_loop_routes`），保证面板始终可用。

## 技术实现要点

- **只导入一次，复制多份。** 每个 FBX（约 35 MB）在一次生成中只被
  `bpy.ops.import_scene.fbx` 导入一次，作为隐藏的“模板”放进 `ICity Pedestrian Sources`。
  每个行人都是模板的轻量复制：共享网格 / 骨架数据与动画 Action，只复制对象本身，
  并把骨骼修改器（Armature modifier）重新指向复制出来的骨架。
- **路径平移 + 原地步循环 + 停顿。** 角色的“走路姿态”由 FBX 自带 Action 提供（加 `CYCLES`
  循环修改器无限循环）；“沿街位移”由载体空物体的关键帧提供，并按 `Stop Chance` 概率
  插入“保持原地”的停顿关键帧实现走走停停。速度以**世界单位/帧**为单位由 `Walk Speed`
  控制，并按路线长度归一化，所以不同长度的人行道上行人速度一致。
- **兼容新版 Action 数据结构。** Blender 4.4+ / 5.x 把旧的扁平 `Action.fcurves`
  改成了 `layers → strips → channelbags` 的“带槽位（slotted）”结构，导入的角色动画上
  可能已经没有 `fcurves` 属性。`ecology_common.iter_action_fcurves` 同时兼容新旧两种结构
  来取曲线、加循环修改器；并且**不**逐个实例重指派 Action（复制对象时已经连槽位一起继承），
  避免在新结构下出现槽位绑定丢失。
- **自动适配身高与朝向。**
  - 身高：导入后按包围盒高度自动换算缩放，统一到 `Person Height (m)`，
    自动兼容 FBX 是以厘米还是米为单位导出的；
  - 朝向：通过 `Facing Offset`（默认 `90°`）把角色正面对齐到“前进方向”。
    若你的角色模型默认朝向不同，调这个值即可，无需改代码。
- **生成的层级结构。**

  ```
  ICity
  └─ ICity Pedestrians
     ├─ ICity Pedestrian Sources   (隐藏的 FBX 模板)
     ├─ ICity Pedestrian Walkers   (移动行人 + 路径载体)
     ├─ ICity Pedestrian Idlers    (站立行人)
     └─ ICity Pedestrian Paths     (预留)
  ```

- **干净的清除。** `Clear` 只删除 `ICity Pedestrians` 这棵子树，并顺带回收
  复制产生的孤立骨架 / 网格 / Action 数据块，**不会**动到原城市、资产扩展、生态或交通结果。

## 在 Blender 里怎么用

1. 打开原版 `ICity` 面板，点 `Start` 生成基础城市。
2. （建议）先用 `ICity Traffic & Crowd` 生成道路，让道路图可被读取，行人会贴着真实道路走。
3. 在右侧 `N` 面板找到 `ICity Pedestrians`。
4. 设置参数：
   - `Walkers` / `Idlers`：移动与停留的行人数量；
   - `Sidewalk Nudge`：在自动识别的人行道位置上再做的微调（一般保持 0）；
   - `Walk Speed`：行走速度（越小越慢）；`Stop Chance`：走走停停的停顿频率；
   - `Person Height (m)`：统一身高；`Facing Offset`：角色正面朝向修正（默认 90°）；
   - `Speed Variation` / `Lateral Jitter` / `Seed`：人群随机性；
   - `Start Frame` / `End Frame`：动画区间。
5. 点 `Generate / Update`。
6. 按时间轴 `Play` 播放，即可看到行人沿人行道走走停停、在路口站立。

## 参数速查

| 参数 | 默认 | 含义 |
| --- | --- | --- |
| Walkers | 16 | 行走的行人数量 |
| Idlers | 8 | 站立的行人数量 |
| Sidewalk Nudge | 0.0 | 在自动识别的人行道中心上再外移（负值朝车道方向，米） |
| Road Width | 3.4 | **兜底**用：读不到道路属性时的估计车道宽 |
| Walk Speed | 0.06 | 行走速度（世界单位/帧，越小越慢） |
| Speed Variation | 0.3 | 步速随机幅度 |
| Stop Chance | 0.3 | 走走停停的停顿概率（0 = 从不停） |
| Lateral Jitter | 0.25 | 横向站位随机幅度（米） |
| Person Height (m) | 1.72 | 统一目标身高（米） |
| Facing Offset | 90° | 角色正面 → 前进方向的旋转修正 |
| Seed | 7 | 随机种子（可复现） |
| Start / End Frame | 1 / 250 | 动画帧区间 |

## 测试

纯几何 / 布局逻辑（人行道偏移、双向人流、路口站立点选取、兜底环线、面板注册、
非法帧区间拒绝）已用 `tests/test_smart_city_pedestrians.py` 覆盖，
可在不启动 Blender 的情况下运行：

```bash
cd tests
python -m unittest test_smart_city_pedestrians
```

需要 `bpy` / FBX 导入的部分（真实导入、骨架复制）属于 Blender 运行期行为，
请在 Blender 内按上面的步骤手动验证。

## 已知限制（演示导向）

- 行人沿预设人行道路线行走，**不做实时避障**（不会互相躲避或停在红灯前）。
- 步循环为“原地动画 + 路径平移”，移动速度与迈步速度未严格对齐，可能有轻微滑步，属正常折中。
- **走走停停时的停顿**只让“位移”停下，FBX 的走路动画仍在循环，所以停顿时人物是
  “原地踏步”而非完全静止。若觉得别扭，把 `Stop Chance` 调到 0 即可关闭停顿。
- 所有行走的人共享同一段循环动画，腿部动作大致同步；变化主要来自不同的位置、
  速度、停顿与朝向，而非各自不同的姿态相位。
- 人行道位置依赖 iCity 的 `Road lanes width` / `side walk offset` 道路属性；
  若某些道路没有这些属性，会退回用 `Road Width` 估计，可能不如自动识别精准——
  这种情况下用 `Sidewalk Nudge` 微调即可。
- 若 `Facing Offset` 与你替换的角色模型不匹配，角色可能侧身/倒退行走，调整该参数即可。

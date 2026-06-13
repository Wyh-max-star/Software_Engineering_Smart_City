# Blender 界面测试流程（手工验收）

在自动化单元测试与 headless 脚本通过之后，用本清单在 **Blender 图形界面** 里做最终确认。  
对应课程中的**确认测试 / 系统测试**：验证真实用户操作路径、动画与时间轴、视觉效果。

---

## 准备工作

1. 安装本仓库中的 **iCity** 插件（`Edit → Preferences → Add-ons → Install`，选择仓库里的 `iCity` 目录）。
2. 勾选启用 **ICity**。
3. 新建场景或 `File → New → General`。
4. 打开右侧 **N 面板**（按 `N`），切换到 **ICity** 标签页。
5. 建议打开 **Outliner**（大纲视图），便于观察集合是否生成/清理正确。

---

## 测试顺序总览

| 步骤 | 面板 | 目的 |
|------|------|------|
| 1 | ICity（原版） | 生成基础城市，后续模块都依赖它 |
| 2 | ICity Traffic | 独立车辆与道路 |
| 3 | ICity Pedestrians | 独立人群动画（FBX 角色） |
| 4 | ICity Ecology | 地块地形 / 湖泊 / 河谷（可选） |
| 5 | ICity Asset Expansion | 路灯与路边道具（可选） |
| 6 | 时间轴播放 | 动画系统测试 |

每完成一个大步骤，在下方「记录表」里打勾并写备注。

---

## 步骤 1：基础城市（必做）

**面板**：原版 **ICity**（非 smart_city 子面板里的扩展项）。

1. 使用默认参数或课程要求的参数。
2. 点击 **Start**（或项目文档中的等价按钮），等待城市生成完成。
3. 在 Outliner 中确认出现 **`ICity`** 集合，且场景中有 **`ICity Base`**（或道路/建筑等子对象）。

**预期**

- 无 Python 报错弹窗。
- 3D 视图中能看到城市道路/地块。
- 未 Start 时，扩展面板应提示需先生成城市。

**记录**：□ 通过　□ 失败（现象：________）

---

## 步骤 2：ICity Traffic（必做）

**面板**：**ICity Traffic**（`N` 面板 → ICity 分类下）。

### 2.1 正常生成

1. 确认步骤 1 已完成。
2. 设置建议测试值：
   - Cars：`3`
   - Taxis：`1`
   - Buses：`1`
   - Start Frame：`1`，End Frame：`120`
3. 点击 **Generate / Update**。
4. 在 Outliner 中检查是否出现：
   - `ICity Traffic`
   - `ICity Traffic Vehicles`
   - `ICity Traffic Walkways`
   - `ICity Traffic Paths`

**预期**

- 状态栏或信息区提示生成成功。
- 视口中有车辆模型（可能为低模或 append 的 blend 资产）。
- **不会**删除 `ICity` 基础城市集合。

**记录**：□ 通过　□ 失败

### 2.2 动画播放

1. 保持步骤 2.1 的场景。
2. 时间轴拖到第 1 帧，点击 **播放**（空格或时间轴播放按钮）。
3. 观察至少 5–10 秒。

**预期**

- 车辆沿道路或外环路径移动，不穿透建筑主体（允许轻微贴地误差）。
- 循环动画在 End Frame 附近能衔接或重复。

**记录**：□ 通过　□ 失败

### 2.3 重复生成（回归）

1. 不删场景，再次点击 **Generate / Update**。

**预期**

- 不崩溃；旧交通内容被替换或更新，不出现大量重复同名对象堆叠。

**记录**：□ 通过　□ 失败

### 2.4 仅清理交通模块

1. 点击 **Clear**（垃圾桶图标那一侧）。
2. 检查 Outliner。

**预期**

- `ICity Traffic` 及其子集合消失。
- **`ICity` 基础城市仍在**。
- Ecology、Asset Expansion 若之前生成过，应仍保留（除非你也点了它们的 Clear）。

**记录**：□ 通过　□ 失败

### 2.5 未 Start 时的错误处理

1. `File → New` 新建空场景（或删除 `ICity` 集合后）。
2. 打开 **ICity Traffic**，直接点 **Generate / Update**。

**预期**

- 应有明确错误提示（需先运行 iCity Start），**不应**静默失败或崩溃。

**记录**：□ 通过　□ 失败

---

## 步骤 3：ICity Pedestrians（必做）

**面板**：**ICity Pedestrians**。

1. 确认步骤 1 已完成。
2. 建议值：Walkers `4`，Idlers `2`，Start `1`，End `120`。
3. 点击 **Generate / Update**。
4. 确认 Outliner 出现 `ICity Pedestrians`、`ICity Pedestrian Walkers`、`ICity Pedestrian Idlers`。
5. 播放时间轴，观察行人沿人行道行走、站立者面向道路。
6. **Clear** 后仅人群集合消失，`ICity` 仍在。

**记录**：□ 通过　□ 失败

---

## 步骤 4：ICity Ecology（可选）

**面板**：**ICity Ecology**。

1. 启用 **Ecology Plot Block**。
2. 分别测试 **LAKE_RING** 与 **RIVER_VALLEY** 模式；**Terrain Resolution** 先用 `32`–`64`。
3. 点击 **Add Plot**（可多次添加多块）。
4. 确认 `ICity Ecology Plots` 下出现 `ICITY_ECO_Plot_001` 及地形/水面对象。
5. **Clear All** 后仅生态树被移除。

**预期**

- Blender 4.5+ 不因水面材质 API 报错。

**记录**：□ 通过　□ 失败　□ 跳过

---

## 步骤 5：ICity Asset Expansion（可选）

**面板**：**ICity Asset Expansion**。

1. 在城市已 Start 的前提下：
2. **Generate Streetlights**，检查 `ICity Asset Streetlights` 与点光源数量。
3. **Clear**，确认路灯集合被移除。
4. （可选）**Apply Surface** 换道路材质，目视检查贴图是否正常。

**记录**：□ 通过　□ 失败　□ 跳过

---

## 步骤 6：模块共存（集成冒烟）

在同一城市中依次执行：

1. Start  
2. Generate Traffic  
3. Generate Pedestrians  
4. Add Ecology Plot（湖泊或河谷）  
5. Generate Streetlights  

**预期**

- 四个模块的对象可同时存在于 Outliner，互不意外删除。
- 分别 Clear 各模块时，只清理各自集合。

**记录**：□ 通过　□ 失败

---

## 自动化测试对照（建议在界面测试前先做）

在项目根目录 PowerShell：

```powershell
# 单元测试 + 报告
python tools/run_tests.py

# Blender 无界面确认测试（把 4.5 换成你的版本）
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python tests\blender\test_generate_ops.py
```

查看报告：

- `test-reports/unit-report.md`
- `test-reports/blender-report.md`

---

## 测试结果记录表（可交作业）

| 编号 | 测试项 | 结果 | 备注 |
|------|--------|------|------|
| TC-01 | iCity Start 生成城市 | | |
| TC-02 | Traffic 正常生成 | | |
| TC-03 | Traffic 动画播放 | | |
| TC-04 | Traffic Clear 不删主城 | | |
| TC-05 | 未 Start 时 Traffic 报错 | | |
| TC-06 | 单元测试 `run_tests.py` | | |
| TC-07 | Headless `test_generate_ops.py` | | |

---

## 常见问题

**Q：Traffic 生成后看不到车？**  
放大到城市外围道路一带；检查 Outliner 里 `ICity Traffic Vehicles` 是否非空；确认 End Frame > Start Frame。

**Q：与 Ecology 里的车重复？**  
新交付用 **ICity Traffic & Crowd**；Ecology 面板里的交通是旧逻辑，测试时建议关闭 `Enable Traffic & Crowd`。

**Q：贴图/资产缺失？**  
执行 `git lfs pull`；见仓库根目录 `README.md` 大文件说明。

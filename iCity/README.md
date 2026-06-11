# iCity 自然语言交互编辑子系统 — 测试指南

## 一、概述

在 Blender iCity 插件侧栏新增了 **「模板化生成」面板**，其中包含自然语言输入框。用户输入中文指令后，系统通过 DeepSeek LLM（或关键词规则兜底）解析意图，自动调整场景。

### 主要功能

| 功能 | 说明 |
|------|------|
| 资产替换 | 树、座椅、路灯、隔离柱、路面材质、路缘石、人行道（共 7 种） |
| 场景维度 | 交通流量、行人密度、生态地貌、路面风格 |
| 天气系统 | 晴天、阴天、雨天(粒子)、夜晚、起雾(体积雾)、黄昏、下雪(粒子) |
| 增量对话 | 多轮指令叠加，新指令不覆盖旧结果 |

---

## 二、修改的代码文件

### 1. `smart_city/template_core.py` — 纯逻辑层

| 行号 | 修改内容 |
|------|----------|
| L21 | LLM 模型名 `"deepseek-v4-flash"` |
| L22 | 超时从 15s → **25s** |
| L29 | `ALL_CATS` 包含全部 7 种资产 |
| L31 | `LLM_CATS = list(ALL_CATS)` — LLM 控制全部资产 |
| L57-61 | 新增 `WEATHER_MODES` / `WEATHER_MODE_TITLE` 常量（7 种天气） |
| L198-227 | `rule_parse_scene()` 新增天气关键词识别（晴天/阴天/雨天/夜晚/雾/黄昏/雪） |
| L153-156 | `expand_scene()` 新增 `weather` 透传 |
| L266-272 | `build_scene_prompt_block()` 天气描述加入 prompt |
| L286-287 | LLM 输出 schema 加入 `weather` 字段 |
| L292 | LLM 示例加入 `"weather": "cloudy"` |
| L354+ | `_has_content()` 显式检查 `_scene.weather` 字段 |
| 规则中 | 关键词冲突修复：`"黄黑"` → `"黄黑隔离柱"`，避免误匹配路缘石 |

### 2. `smart_city/template_extension.py` — Blender 执行层

| 行号 | 修改内容 |
|------|----------|
| L1-8 | 文件头文档 |
| L30-31 | 导入 `WEATHER_MODES`、`WEATHER_MODE_TITLE` |
| L34-50 | 新增 `_last_scene_cfg` / `_last_asset_sel` + `_merge_incremental()` 增量合并 |
| L189-233 | `apply_weather()` 控制 World Background + 路灯颜色/亮度 |
| L236-330 | `_ensure_weather_particles()` 创建雨/雪粒子系统 |
| L288-298 | `_clear_weather_particles()` 清理旧粒子 |
| L320-330 | `_clear_volumetric_fog()` 清理体积雾 |
| L440+ | `execute()` 集成增量合并 + 天气应用 |
| L450+ | 面板提示文字 |
| 全文件 | 与 Blender 4.1 API 兼容性修复（`RANDOM`→`RAND`、`material_slots`→`material_slot` 等） |

---

## 三、需要测试的功能

### 测试项 1：资产替换（7 种）

通过自然语言指令替换街道资产，系统应正确识别并替换对应模型/材质。

**测试样例：**

| 输入文本 | 预期效果 |
|----------|----------|
| `棕榈树` | 行道树切换为棕榈树 |
| `金黄的树` | 行道树切换为金黄色秋季树 |
| `木质长椅` | 座椅切换为木质复古款 |
| `现代简约的座椅` | 座椅切换为黑色金属款 |
| `现代路灯` | 路灯切换为方形 LED 灯 |
| `古典隔离柱` | 隔离柱切换为铸铁古典款 |
| `黄黑路缘石` | 路缘石切换为黄黑警示色 |
| `灰色人行道` | 人行道切换为灰色砖纹 |
| `干净的路面` | 路面材质切换为清洁款 |

### 测试项 2：场景维度控制

通过自然语言指令控制交通、行人、生态、路面风格。

**测试样例：**

| 输入文本 | 预期效果 |
|----------|----------|
| `车水马龙` | 车辆密集（car_count=24） |
| `车少` | 车辆稀疏 |
| `去掉车` | 清空所有车辆 |
| `很多人` | 行人增加（walker_count=40） |
| `人少` | 行人减少 |
| `去掉行人` | 清空行人 |
| `有山有湖` | 环湖生态 + 山 + 船 |
| `河谷` | 河谷生态地貌 |
| `只有山` | 仅有山体 |
| `去掉生态` | 移除所有生态元素 |
| `木栈道` | 路面切换为暖色木板路 |
| `主干道` | 路面切换为沥青车道线 |

### 测试项 3：天气系统

测试 7 种天气模式切换，需在 **Material Preview** 或 **Rendered** 视口下观察。

**测试样例：**

| 输入文本 | 预期效果 |
|----------|----------|
| `晴天` | 明亮蓝色天空，路灯低亮度 |
| `天色变暗` | 灰蓝色天空，世界变暗 |
| `下雨天` | 深灰色天空 + 蓝色雨丝粒子下落（25000 条） |
| `夜晚` | 几乎全黑天空，路灯暖黄高亮 |
| `起雾` | 灰色天空 + Eevee 体积雾弥漫场景 |
| `黄昏` | 暖橙色天空，路灯自动半亮 |
| `下雪` | 苍白天空 + 白色雪花粒子飘落 |

### 测试项 4：多轮增量对话

验证多轮指令叠加，新指令不覆盖之前的结果。

**测试流程（按顺序执行）：**

| 轮次 | 输入文本 | 预期效果 |
|------|----------|----------|
| ① | `有山有湖，车水马龙` | 基础场景：环湖+山+车流 |
| ② | `加上下雨` | 保留山湖车流，叠加雨天效果 |
| ③ | `棕榈树` | 场景不变，树换为棕榈树 |
| ④ | `木质座椅` | 场景不变，座椅换为木质款 |
| ⑤ | `去掉车` | 清空车辆，其他元素保留 |
| ⑥ | `晴天` | 天气切换为晴天，其他元素保留 |
| ⑦ | `去掉生态` | 移除山湖，行人+天气+资产保留 |

### 测试项 5：组合指令

一次输入包含多个维度的指令，验证系统能同时解析并全部应用。

| 输入文本 | 预期效果 |
|----------|----------|
| `车水马龙、有山有湖、很多人，金黄的树` | 交通+生态+行人+树木同时生效 |
| `有山有湖、下雨天、棕榈树、木质座椅、古典隔离柱、黄黑路缘石、灰色人行道` | 生态+天气+5种资产同时生效 |
| `黄昏、车水马龙` | 黄昏天空 + 车流 |
| `下雪天、人少、古典隔离柱` | 雪景 + 行人少 + 隔离柱 |

### 测试项 6：规则兜底（离线/API 失败时）

断开网络或 API Key 失效时，系统应退回关键词规则匹配。

| 输入文本 | 预期效果（规则兜底） |
|----------|----------|
| `棕榈树` | 树→Tree14 |
| `车水马龙` | traffic→high |
| `有山有湖` | ecology_plot_mode→LAKE_RING |
| `很多人` | pedestrian→high |
| `下雨天` | weather→rainy |
| `木质长椅` | bench→Bench1 |

---

## 四、测试环境与操作说明

### 环境要求

- Blender 4.1
- iCity 插件已安装（从 zip 安装或手动复制到 `scripts/addons/`）
- 网络可选（LLM 需要联网，规则模式离线可用）

### 测试步骤

1. 启动 Blender，确保 iCity 插件已启用（Edit → Preferences → Add-ons → 勾选 iCity）
2. 在 3D 视口按 **N** 打开侧栏，找到 **iCity** 标签页
3. 点击 **模板化生成** 面板
4. 在 **自然语言编辑** 输入框中输入测试指令，点击 **应用** 按钮
5. 观察 3D 视口变化（建议切换到 **Material Preview** 视口模式）
6. 按 **Window → Toggle System Console** 打开控制台，查看 `[模板插件]` 日志

### 视口模式切换

在 3D 视口右上角点击图标切换：
- 第三个球（Material Preview）：查看材质和天气效果
- 第四个球（Rendered）：查看最终渲染效果

### 检查粒子效果

雨/雪粒子需要：
1. 进入 Material Preview 或 Rendered 视口
2. 点击视口右上角 **Overlay 菜单（下箭头）** → 确保 **Particles** 勾选
3. 按 **空格键** 播放动画，观察粒子下落

---

## 五、代码覆盖率测试指引

### 核心函数覆盖

| 函数 | 所在文件 | 测试重点 |
|------|----------|----------|
| `parse_command()` | template_core.py | LLM 解析 + 规则兜底 + `_has_content` 判断 |
| `expand_scene()` | template_core.py | 场景维度档位→数值换算 |
| `validate_selection()` | template_core.py | 资产名称合法性校验 |
| `rule_parse_assets()` | template_core.py | 资产关键词匹配 |
| `rule_parse_scene()` | template_core.py | 场景/天气关键词匹配 |
| `_has_content()` | template_core.py | 含 weather 字段的非空判断 |
| `build_scene_prompt_block()` | template_core.py | LLM prompt 构造 |
| `_merge_incremental()` | template_extension.py | 增量合并逻辑 |
| `apply_weather()` | template_extension.py | 天气应用（世界背景+路灯） |
| `_ensure_weather_particles()` | template_extension.py | 雨/雪粒子创建 |
| `_clear_weather_particles()` | template_extension.py | 粒子清理 |
| `apply_selection()` | template_extension.py | 资产应用到场景 |
| `apply_scene_dimensions()` | template_extension.py | 场景维度应用到场景 |

### 分支覆盖重点

- `parse_command()`：LLM 成功 / LLM 失败退规则 / 规则无匹配
- `expand_scene()`：各档位（none/low/medium/high）→ 不同数值
- `_has_content()`：纯资产 / 纯场景 / 纯天气 / 无内容
- `_merge_incremental()`：首次 vs 多轮 / 新值 vs 旧值保留 / _clear 指令
- `apply_weather()`：7 种天气模式各一次 / 晴天到雨天的粒子清理

---

## 六、常见问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 输入后无变化 | LLM 超时且规则未匹配 | 查看控制台 `[模板插件]` 日志，检查是否退回规则解析 |
| 粒子不可见 | 视口模式不对或 Overlay 关闭 | 切换到 Material Preview，勾选 Overlay → Particles |
| 雨/雪粒子卡顿 | 粒子数量过多 | 修改 `settings.count` 降低粒子数（当前雨 25000 / 雪 15000） |
| 天气没变化 | 视口不是 Material Preview | 切换右上角视口模式 |
| 提示 "没听懂" | 输入文本无匹配关键词 | 使用上方测试样例中的指令 |
# 测试说明

本目录是 iCity 智能城市扩展的测试套件，覆盖当前 smart_city 模块：

- **Ecology**（`ecology_extension` + `ecology_water` 地块地形/湖泊/河谷）
- **Asset Expansion**（`asset_extension` 路灯、路边道具、路面材质）
- **Traffic**（`traffic_extension` 独立车辆与道路）
- **Pedestrians**（`pedestrian_extension` 独立人群动画）
- **Template + NL/LLM**（`template_core` + `template_extension` 场景模板化与自然语言编辑）

## 核心原则：自动化测试 100% Mock

**所有可通过 `python tools/run_tests.py` 运行的测试均使用标准库 `unittest.mock`，不依赖真实 Blender。**

| Mock 手段 | 用途 |
|-----------|------|
| `install_blender_mocks()` | 用 `MagicMock` 替代 `bpy` / `mathutils`（`blender_test_utils.py`） |
| `@patch` / `@patch.object` | 隔离算子流水线、manifest、纹理目录 |
| `mock_open` | 模拟 manifest / JSON 磁盘读取 |
| `make_mock_context()` | 构造算子 `execute` 所需的假 Blender context（`mock_helpers.py`） |

原 Blender headless 黑盒场景已迁移至 **`test_operators_mock.py`**。`tests/blender/test_generate_ops.py` 仅作**可选**本地冒烟，不计入 CI / 自动化套件。

---

## 一、自动化测试（命令行）

### 1. 单元测试 + 持久化报告（推荐）

```powershell
cd C:\workspace\Software_Engineering_Smart_City
pip install -r requirements-dev.txt
python tools/run_tests.py --coverage
```

生成：

| 文件 | 用途 |
|------|------|
| `test-reports/unit-report.md` | 人可读摘要（**按测试对象 + 白/灰/黑盒**，不含测试代码路径） |
| `test-reports/taxonomy-summary.md` | 盒模型 + **被测模块/功能**一览 + Mock 隔离范围 |
| `test-reports/coverage.md` | 代码覆盖率摘要 |
| `test-reports/unit-tests.xml` | JUnit XML（CI） |
| `test-reports/history/unit-report-<时间戳>.md` | 历史记录 |

> 请使用 `tools/run_tests.py` 而非裸 `unittest discover`（后者对 `tests/` 目录的 import 路径不友好）。

### 2. 测试文件与覆盖范围

| 文件 | 分类 | 覆盖模块 |
|------|------|----------|
| `test_ecology_common.py` | 白盒 | 布局/几何/路径纯函数 |
| `test_ecology_water.py` | 白盒 | 地块布局、湖泊/河谷地形、河流几何、船只网格 |
| `test_pedestrian_extension.py` | 白盒 | 人行道路线、站立点、转角检测 |
| `test_asset_extension.py` | 白盒 | 路灯周长、城市核心区过滤、路边节点、纹理（`@patch`） |
| `test_asset_registry.py` | 白盒 | 资产清单 JSON（`mock_open` / `@patch`） |
| `test_traffic_extension.py` | 白盒 | 道路链、交通布局、车辆路径、**随机 seed/路线/相位/缩放** |
| `test_layout_control.py` | 白盒/灰盒 | **布局控制**：节点坐标查看/CRUD、边调整、校验、规范化、Preview 几何 |
| `test_layout_sketch.py` | 白盒 | **草图识别**：黑线二值化、骨架细化、像素路径→LayoutGraph |
| `test_layout_operators_mock.py` | **黑盒** | 布局算子 `icity.*` 契约（Inspect/Validate/Normalize/Import/CRUD） |
| `test_template_core.py` | 白盒 | 模板 JSON、关键词/天气解析、档位换算、**LLM 解析（Mock HTTP）** |
| `test_nl_editing_guide.py` | 白盒/灰盒 | **NL 完整态**：天气、多轮增量、组合指令、apply_weather |
| `test_template_extension.py` | 灰盒 | `apply_selection` / 增量合并 `_merge_incremental` |
| `test_template_frontend_parity.py` | 灰盒 | `templates.ts` ↔ `templates.json`（资产/catalog/预览图/角色） |
| `test_frontend_static_contracts.py` | 灰盒 | `App.tsx` 角色权限、路由、插件审核、Blender 入口字段 |
| `test_mock_integration.py` | 白盒 | 标准 `@patch` 边界示例 |
| `test_operators_mock.py` | **黑盒** | 算子 `execute`/`poll` 契约（含 `icity.apply_template` / `icity.apply_nl_command`） |
| `test_smart_city_extensions.py` | 灰盒 | 跨模块不变式 |

公共工具：

- `blender_test_utils.py` — `install_blender_mocks()` + `load_module()`
- `mock_helpers.py` — `make_mock_context()` / `make_settings()`
- `test_markers.py` — `@white_box` / `@gray_box` / `@black_box`

### 3. 静态检查

```powershell
pylint iCity/smart_city
```

### 4. 可选：真实 Blender 冒烟

若需在真实 Blender 中额外验证，可手动运行（**非自动化 Mock 套件**）：

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python tests\blender\test_generate_ops.py
```

报告：`test-reports/blender-report.md`（不影响 `taxonomy-summary.md` 中的 Mock 黑盒统计）。

### 5. 性能基线（改地形时）

```powershell
python tools/profile_terrain.py --resolution 96
```

---

## 二、Blender 界面手工测试

**详细步骤见：[BLENDER_UI_TESTING.md](./BLENDER_UI_TESTING.md)**

---

## 三、CI

`.github/workflows/tests.yml` 在 push/PR 时运行 `python tools/run_tests.py --coverage` 并上传 `test-reports/`。**无需 Blender。**

---

## 四、白盒 / 灰盒 / 黑盒、Mock 与代码覆盖率

### 4.1 盒模型对照（全部 Mock 驱动）

| 类型 | 定义 | 测试文件 | Mock 方式 |
|------|------|----------|-----------|
| **白盒** | 函数/分支/数据结构 | `test_ecology_*.py`、`test_traffic_*.py`、`test_pedestrian_*.py`、`test_asset_*.py`、`test_template_core.py`、`test_layout_control.py`、`test_layout_sketch.py`、`test_mock_integration.py` | `install_blender_mocks()` + `@patch` |
| **灰盒** | 跨模块不变式 / 场景编排 / 前后端数据 / 前端静态契约 | `test_smart_city_extensions.py`、`test_template_extension.py`、`test_template_frontend_parity.py`、`test_frontend_static_contracts.py` | 同上 |
| **黑盒** | 算子可观测行为（输入→`FINISHED`/`CANCELLED`） | `test_operators_mock.py` | `@patch` 整条生成流水线 |

### 4.2 Mock 示例

**LLM 解析**（`test_template_core.py`，Mock 网络，CI 不联网）：

```python
@patch.object(tc, "_http_post_json")
def test_llm_parse_returns_json_content(self, mock_http):
    mock_http.return_value = {
        "choices": [{"message": {"content": '{"tree":"Tree1_Tree_ICity_Default","scene":{}}'}}]
    }
    result = tc.llm_parse("车水马龙", "test-key")
```

**模板算子黑盒**（`test_operators_mock.py`）：

```python
@patch.object(traffic_extension, "generate_traffic")
def test_generate_traffic_finished(self, mock_generate):
    op = traffic_extension.ICITY_OT_GenerateTraffic()
    self.assertEqual(op.execute(_traffic_context()), {"FINISHED"})
    mock_generate.assert_called_once_with(context)
```

**文件 I/O**（`test_asset_registry.py`）：

```python
@patch("pathlib.Path.open", new_callable=mock_open, read_data='{"textures": [], "objects": []}')
def test_missing_sections_default_to_empty_lists(self, mock_file):
    manifest = load_manifest(Path("/mock/root") / "asset_manifest.json", addon_root=Path("/mock/root"))
```

**Blender API**（所有 `load_module` 测试）：

```python
from blender_test_utils import install_blender_mocks, load_module
install_blender_mocks()  # 模块加载前注入 MagicMock bpy
```

### 4.3 代码覆盖率

- 配置：仓库根目录 `.coveragerc`，统计范围 `iCity/smart_city/`
- 命令：`python tools/run_tests.py --coverage`
- Mock 测试能覆盖所有不依赖真实 Blender 场景图的逻辑；算子 `execute` 分支由 `test_operators_mock.py` 触发

### 4.4 测试设计方法（作业可引用）

| 方法 | 示例 |
|------|------|
| 等价类 / 边界值 | `clamp`、`perimeter_positions(0)`、`normalize_band` |
| 路径覆盖（白盒） | `terrain_height` 三模式、`corner_vertex_flags` |
| Mock 隔离依赖 | 全部自动化测试 |
| 黑盒 / 错误推测 | Mock `RuntimeError("Please run iCity Start")` → `CANCELLED` |
| 回归 | `test-reports/history/` + CI |

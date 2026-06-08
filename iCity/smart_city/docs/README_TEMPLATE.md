# ICity Template — 模板化整城生成 + 自然语言编辑

`smart_city` 扩展模块。装好 iCity 插件即在 ICity 侧栏出现"模板化生成"面板，**无需再手动粘脚本**。

## 功能

- **① 选模板一键应用（整城）**：选模板 0/1/2 → 一次配置整座城——
  街道资产（树/座椅/路灯/隔离柱/路面/路缘/人行道，走原版 icity `road_apply`）
  + 场景维度（路面材质/路灯/路边设施/交通/人群/生态，调本仓库 smart_city 算子）。
- **② 自然语言编辑**：输入中文（如"车水马龙、有山有湖、街上很多人"）→ DeepSeek 解析 → 应用。
  - 无 key / 失败时自动退回**关键词规则解析**（离线可用，演示不翻车）。
  - 也支持"去掉车/去掉人/去掉山湖"等清空指令。

## 文件

| 文件 | 作用 |
| --- | --- |
| `smart_city/template_core.py` | **纯逻辑**（无 bpy）：读 templates.json、关键词/LLM 解析、档位→数值换算。可脱 Blender 单测。 |
| `smart_city/template_extension.py` | **Blender 层**：算子/面板/PropertyGroup/register。`ICITY_OT_ApplyTemplate`(`icity.apply_template`)、`ICITY_OT_ApplyNaturalLanguage`(`icity.apply_nl_command`)、`ICITY_PT_TemplatePanel`。 |
| `smart_city/manifests/templates.json` | **数据唯一源**：3 个整城模板 + `catalog`(资产清单) + `catalog_scene`(场景档位→数值表)。 |
| `tests/test_template_core.py` | 单元测试（unittest，无 bpy）。 |
| `iCity/__init__.py` | 接线：import + `template_extension.register()/unregister()`（与其他 smart_city 模块同样三处）。 |

## 设计要点（规范）

- **纯逻辑/Blender 分层**：解析等纯函数放 `template_core.py`，可脱 Blender 用 `unittest` 测；bpy 相关只在 `template_extension.py`。与 `asset_registry.py` 同理。
- **数据相对路径**：`template_core.templates_json_path()` = `Path(__file__).resolve().parent / "manifests" / "templates.json"`，无绝对路径。
- **DeepSeek key**：团队已商定**内置默认 key**（`template_core.DEFAULT_API_KEY`），开箱即用；可用环境变量 `DEEPSEEK_API_KEY`/`ICITY_LLM_KEY` 覆盖成自己的。注意内置 key 会随代码进版本库，可在 DeepSeek 后台随时重置。
- **自然语言双层 + 校验防错**：DeepSeek 输出 资产名/场景档位 → `validate_selection` 丢弃不存在资产、`expand_scene` 把档位按 `catalog_scene` 换算成数值。

## 用法

1. Blender 装并启用本 iCity 插件（含 smart_city）。
2. 3D 视口按 **N** ▸ **ICity** 标签 ▸ 底部 **"模板化生成 Template"** 面板。
3. 先点 ICity **Start** 生成城市。
4. 选模板 → 应用模板；或自然语言 → 解析并应用。
5. 应用后关 **Proxy mode** + 切**材质预览**看真实效果。
6. （可选）想用 DeepSeek：把自己的 key 放进 `manifests/llm_key.txt`（单独一行）。

## 测试

```bash
python tests/test_template_core.py        # 或 python -m unittest discover tests
```

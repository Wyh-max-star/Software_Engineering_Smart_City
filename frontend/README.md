# 智能城市生成系统 — 前端原型

> 团队作业的 **前端原型**：多角色登录 + 模板商城 + "进入 Blender 生成"模拟入口。
> 技术栈：React 19 + TypeScript + Vite。**纯静态前端，无后端依赖、无本地绝对路径**，`npm install` 即可在任意机器复现。

## 功能

- **多角色登录**：场景建模师 / 系统管理员 / 行业分析师，按角色显示不同权限页面（登录态存 `localStorage`）。
- **模板商城**：展示 3 个整城模板（公园城市 / 金秋商业街 / 滨海社区），每个模板配 iCity 真实缩略图（树 / 路面 / 座椅）+ 整城场景概要（交通 / 人群 / 生态）。
- **模板详情**：参数一览 + "在 Blender 中应用此模板"模拟按钮（对应插件里的模板 0/1/2）。

## 运行

```bash
cd frontend
npm install        # 首次：按 package-lock.json 锁定版本安装
npm run dev        # 本地开发（默认 http://localhost:5173）
npm run build      # 产物输出到 dist/
npm run preview    # 预览构建产物
```

> 需要 Node.js 18+。依赖版本已由 `package-lock.json` 锁定，保证不同机器装出一致的依赖树。

## 目录

| 路径 | 作用 |
| --- | --- |
| `src/templates.ts` | **模板数据源**：3 个整城模板（资产 + 场景概要 + 缩略图引用）、角色定义、`getTemplate()`。 |
| `src/App.tsx` | 主应用：登录、模板商城、模板详情、角色权限页。 |
| `src/assets/templates/` | iCity 真实缩略图（`road/tree/bench-0/1/2.png`，与插件 `templates.json` 的 3 个模板一一对应）。 |
| `public/` | 站点图标（`favicon.svg` / `icons.svg`）。 |

## 与插件的对应关系

前端模板商城的 3 个模板，与插件 `iCity/smart_city/manifests/templates.json` 中的模板 0/1/2 **数据一致**（树/路面/座椅资产、交通/人群/生态档位）。前端只做展示与"模拟应用"，真正的整城生成由 Blender 插件完成。

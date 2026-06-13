"""Shared helpers for frontend ↔ plugin parity and static contract tests."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_TS = REPO_ROOT / "frontend" / "src" / "templates.ts"
FRONTEND_APP = REPO_ROOT / "frontend" / "src" / "App.tsx"
PREVIEW_ASSETS_DIR = REPO_ROOT / "frontend" / "src" / "assets" / "templates"

# Frontend ecology summary labels keyed by templates.json ecology_plot_mode
ECOLOGY_MODE_LABELS = {
    "LAKE_RING": "湖+山",
    "RIVER_VALLEY": "河谷",
    "MOUNTAIN_ONLY": "山",
}

ROLE_IDS = ("modeler", "admin", "analyst")

STORAGE_KEYS = (
    "icity-selected-template",
    "icity-current-role",
    "icity-local-users",
    "icity-current-user",
    "icity-sidebar-collapsed",
    "icity-page-history",
)

APP_ROUTES = (
    "/login",
    "/register",
    "/dashboard",
    "/templates",
    "/templates/:id",
    "/plugin-entry",
    "/admin",
)


def parse_frontend_templates(text: str) -> dict[str, dict]:
    """Extract template metadata from ``templates.ts`` without a TS toolchain."""

    blocks: dict[str, dict] = {}
    for chunk in re.split(r"(?=^\s*id: '[012]',)", text, flags=re.MULTILINE):
        id_match = re.search(r"id: '([012])'", chunk)
        if not id_match:
            continue
        tid = id_match.group(1)

        def _field(pattern: str, cast=str):
            match = re.search(pattern, chunk, re.DOTALL)
            if not match:
                raise AssertionError(f"templates.ts 模板 {tid} 缺少字段: {pattern}")
            value = match.group(1)
            return cast(value) if cast is not str else value

        blocks[tid] = {
            "id": tid,
            "name": _field(r"name: '([^']+)'"),
            "sceneType": _field(r"sceneType: '([^']+)'"),
            "description": _field(r"description:\s*\n?\s*'([^']+)'"),
            "tree_type": _field(r"tree_type: (\d+)", int),
            "road_texture": _field(r"road_texture: (\d+)", int),
            "bench_type": _field(r"bench_type: (\d+)", int),
            "plugin_tree": _field(r"pluginValues: \{[^}]*tree: '([^']+)'"),
            "plugin_road": _field(r"pluginValues: \{[^}]*road: '([^']+)'"),
            "plugin_bench": _field(r"pluginValues: \{[^}]*bench: '([^']+)'"),
            "scene_traffic": _field(r"scene: \{[^}]*traffic: '([^']+)'"),
            "scene_pedestrian": _field(r"scene: \{[^}]*pedestrian: '([^']+)'"),
            "scene_ecology": _field(r"scene: \{[^}]*ecology: '([^']+)'"),
            "fit": _field(r"fit: '([^']+)'"),
            "tags": _field(r"tags: \[([^\]]+)\]"),
        }
    if set(blocks) != {"0", "1", "2"}:
        raise AssertionError(f"templates.ts 应包含模板 0/1/2，实际: {sorted(blocks)}")
    return blocks


def parse_frontend_roles(text: str) -> list[str]:
    roles_block = re.search(r"export const roles = \[([\s\S]*?)\]\s*as const", text)
    if not roles_block:
        raise AssertionError("templates.ts 缺少 roles 定义")
    return re.findall(r"id: '(\w+)'", roles_block.group(1))


def ecology_summary_for_backend(ecology: dict) -> str:
    if not ecology.get("enable", True):
        return "无"
    mode = ecology.get("ecology_plot_mode", "")
    return ECOLOGY_MODE_LABELS.get(mode, mode)


def resolve_template_id(templates: dict[str, dict], template_id: str | None) -> str:
    """Mirror ``getTemplate()`` fallback: unknown id → template 0."""

    if template_id and str(template_id) in templates:
        return str(template_id)
    return "0"


def first_int(text: str) -> int:
    match = re.search(r"(\d+)", text)
    if not match:
        raise AssertionError(f"无法从 '{text}' 解析整数")
    return int(match.group(1))


def role_permission(text: str, role: str, permission: str) -> bool | None:
    """Parse ``rolePermissions[role][permission]`` from App.tsx source."""

    match = re.search(
        rf"{role}:\s*\{{[^{{}}]*{permission}:\s*(true|false)",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    return match.group(1) == "true"

"""Shared asset registry for Smart City extension features.

This module keeps pure-Python manifest handling separate from Blender-specific
import and material operations so it can be tested outside Blender.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AssetRegistryError(ValueError):
    """Raised when an asset manifest is invalid or an asset id is unknown."""


def default_addon_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_manifest_path() -> Path:
    return Path(__file__).resolve().parent / "manifests" / "asset_manifest.json"


def load_manifest(
    manifest_path: str | Path | None = None,
    *,
    addon_root: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(manifest_path) if manifest_path is not None else default_manifest_path()
    root = Path(addon_root) if addon_root is not None else default_addon_root()

    with path.open("r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    manifest.setdefault("textures", [])
    manifest.setdefault("objects", [])
    manifest["_addon_root"] = str(root.resolve())
    return manifest


def get_texture_asset(manifest: dict[str, Any], asset_id: str) -> dict[str, Any]:
    return _get_asset(manifest, "textures", asset_id, "texture")


def get_object_asset(manifest: dict[str, Any], asset_id: str) -> dict[str, Any]:
    return _get_asset(manifest, "objects", asset_id, "object")


def validate_asset_paths(manifest: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for asset in list(manifest.get("textures", [])) + list(manifest.get("objects", [])):
        resolved_path = resolve_asset_path(manifest, asset)
        if not resolved_path.exists():
            issues.append(
                {
                    "asset_id": str(asset.get("id", "")),
                    "path": str(asset.get("path", "")),
                    "resolved_path": str(resolved_path),
                    "message": f"Missing asset file: {asset.get('path', '')}",
                }
            )
    return issues


def resolve_asset_path(manifest: dict[str, Any], asset: dict[str, Any]) -> Path:
    root = Path(str(manifest.get("_addon_root", default_addon_root())))
    raw_path = Path(str(asset.get("path", "")))
    if raw_path.is_absolute():
        return raw_path
    return root / raw_path


def apply_road_texture(
    asset_id: str,
    target_material_name: str,
    manifest: dict[str, Any] | None = None,
) -> None:
    """Apply a texture asset to a Blender material.

    This function requires Blender's `bpy` module and is intentionally small so
    the manifest behavior remains testable in regular Python.
    """

    bpy = _require_bpy()
    manifest = manifest or load_manifest()
    asset = get_texture_asset(manifest, asset_id)
    texture_path = resolve_asset_path(manifest, asset)
    if not texture_path.exists():
        raise AssetRegistryError(f"texture file does not exist: {texture_path}")

    material = bpy.data.materials.get(target_material_name)
    if material is None:
        raise AssetRegistryError(f"material not found: {target_material_name}")

    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    image_node = nodes.new(type="ShaderNodeTexImage")
    image_node.image = bpy.data.images.load(str(texture_path), check_existing=True)
    if principled is not None:
        material.node_tree.links.new(image_node.outputs["Color"], principled.inputs["Base Color"])


def append_object_asset(
    asset_id: str,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
    manifest: dict[str, Any] | None = None,
) -> Any:
    """Append or import a registered object asset into the current Blender scene."""

    bpy = _require_bpy()
    manifest = manifest or load_manifest()
    asset = get_object_asset(manifest, asset_id)
    object_path = resolve_asset_path(manifest, asset)
    if not object_path.exists():
        raise AssetRegistryError(f"object file does not exist: {object_path}")

    suffix = object_path.suffix.lower()
    if suffix == ".blend":
        object_name = asset.get("object_name")
        if not object_name:
            raise AssetRegistryError(f"blend asset missing object_name: {asset_id}")
        with bpy.data.libraries.load(str(object_path), link=False) as (data_from, data_to):
            if object_name not in data_from.objects:
                raise AssetRegistryError(f"object {object_name} not found in {object_path}")
            data_to.objects = [object_name]
        obj = data_to.objects[0]
        bpy.context.collection.objects.link(obj)
    elif suffix == ".obj":
        before = set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=str(object_path))
        created = [obj for obj in bpy.data.objects if obj not in before]
        if not created:
            raise AssetRegistryError(f"OBJ import created no objects: {object_path}")
        obj = created[0]
    else:
        raise AssetRegistryError(f"unsupported object asset format: {object_path.suffix}")

    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale
    return obj


def _get_asset(
    manifest: dict[str, Any],
    section: str,
    asset_id: str,
    label: str,
) -> dict[str, Any]:
    for asset in manifest.get(section, []):
        if asset.get("id") == asset_id:
            return asset
    raise AssetRegistryError(f"unknown {label} asset: {asset_id}")


def _require_bpy() -> Any:
    try:
        import bpy  # type: ignore
    except ModuleNotFoundError as exc:
        raise AssetRegistryError("Blender bpy module is required for this operation") from exc
    return bpy


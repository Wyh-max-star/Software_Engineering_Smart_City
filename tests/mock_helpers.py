"""Shared ``unittest.mock`` helpers for Smart City tests."""

from __future__ import annotations

import types
from unittest.mock import MagicMock

from blender_test_utils import Vector  # noqa: E402


def make_settings(**fields):
    return types.SimpleNamespace(**fields)


def make_mock_context(**scene_attrs) -> MagicMock:
    """Build a minimal ``bpy.types.Context`` stand-in with ``scene.*`` settings."""

    scene = MagicMock()
    for name, value in scene_attrs.items():
        setattr(scene, name, value)
    context = MagicMock()
    context.scene = scene
    return context


def make_operator():
    """Instantiate an operator class that inherits from the mocked ``Operator`` base."""

    import bpy

    class _Harness(bpy.types.Operator):
        def execute(self, context):  # pragma: no cover - overridden in tests
            return {"FINISHED"}

    return _Harness()

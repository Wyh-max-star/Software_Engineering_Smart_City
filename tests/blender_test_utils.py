"""Shared helpers for testing Blender-dependent Smart City modules.

All Blender API access is replaced with ``unittest.mock.MagicMock`` instances
(see ``install_blender_mocks``).  Pure math uses a lightweight ``Vector`` double.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from unittest.mock import MagicMock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SMART_CITY_DIR = REPO_ROOT / "iCity" / "smart_city"


class Vector:
    """Minimal stand-in for :class:`mathutils.Vector` used in tests."""

    def __init__(self, values):
        values = tuple(values)
        if len(values) == 2:
            self.x, self.y = values
            self.z = 0.0
        else:
            self.x, self.y, self.z = values

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, scalar):
        return Vector((self.x * scalar, self.y * scalar, self.z * scalar))

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Vector((self.x / scalar, self.y / scalar, self.z / scalar))

    def __neg__(self):
        return Vector((-self.x, -self.y, -self.z))

    @property
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    @property
    def length_squared(self):
        return self.x**2 + self.y**2 + self.z**2

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def normalized(self):
        length = self.length
        if length == 0.0:
            return Vector((0.0, 0.0, 0.0))
        return Vector((self.x / length, self.y / length, self.z / length))

    def copy(self):
        return Vector((self.x, self.y, self.z))

    def __repr__(self):
        return f"Vector(({self.x}, {self.y}, {self.z}))"


class _MockOperator:
    def report(self, _type, message=""):
        self.last_report = (_type, message)


class _MockPropertyGroup:
    pass


def install_blender_mocks() -> None:
    """Register ``MagicMock``-backed ``bpy`` / ``mathutils`` in :data:`sys.modules`."""

    bpy = MagicMock(name="bpy")
    bpy.data = MagicMock(name="bpy.data")
    bpy.data.collections = MagicMock(name="bpy.data.collections")
    bpy.data.collections.get = MagicMock(return_value=None)
    bpy.data.objects = MagicMock(name="bpy.data.objects")
    bpy.data.objects.get = MagicMock(return_value=None)
    bpy.data.meshes = MagicMock(name="bpy.data.meshes")
    bpy.data.materials = MagicMock(name="bpy.data.materials")
    bpy.context = MagicMock(name="bpy.context")
    bpy.context.scene = MagicMock(name="bpy.context.scene")
    bpy.utils = MagicMock(name="bpy.utils")
    bpy.app = MagicMock(name="bpy.app")
    bpy.app.version_string = "mock"

    props = types.ModuleType("bpy.props")

    def _prop_factory(*args, **kwargs):
        return kwargs.get("default")

    for name in ("BoolProperty", "CollectionProperty", "EnumProperty", "FloatProperty", "IntProperty", "PointerProperty", "StringProperty"):
        setattr(props, name, _prop_factory)

    bpy_types = types.ModuleType("bpy.types")
    bpy_types.Operator = _MockOperator
    bpy_types.Panel = _MockPropertyGroup
    bpy_types.PropertyGroup = _MockPropertyGroup
    for name in (
        "Collection",
        "Context",
        "Curve",
        "Light",
        "Material",
        "Mesh",
        "Node",
        "NodeLinks",
        "Nodes",
        "Object",
        "Action",
        "UIList",
    ):
        setattr(bpy_types, name, type(name, (), {}))

    bpy.props = props
    bpy.types = bpy_types

    mathutils = types.ModuleType("mathutils")
    mathutils.Vector = Vector
    mathutils.noise = MagicMock(name="mathutils.noise")
    mathutils.noise.fractal = MagicMock(return_value=0.0)
    mathutils.noise.turbulence = MagicMock(return_value=0.0)

    sys.modules["bpy"] = bpy
    sys.modules["bpy.props"] = props
    sys.modules["bpy.types"] = bpy_types
    sys.modules["mathutils"] = mathutils


# Backward-compatible alias used across existing tests.
install_blender_stubs = install_blender_mocks


def load_module(name: str, relative_path: str):
    """Load a Smart City module with mocked Blender APIs installed."""

    install_blender_mocks()
    smart_city_path = str(SMART_CITY_DIR)
    if smart_city_path not in sys.path:
        sys.path.insert(0, smart_city_path)

    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

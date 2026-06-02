import importlib.util
import sys
import types
import unittest
from pathlib import Path


class Vector:
    def __init__(self, values):
        if len(values) == 2:
            self.x, self.y = values
            self.z = 0.0
        else:
            self.x, self.y, self.z = values

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, scalar):
        return Vector((self.x * scalar, self.y * scalar, self.z * scalar))

    __rmul__ = __mul__

    def __neg__(self):
        return Vector((-self.x, -self.y, -self.z))

    @property
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def copy(self):
        return Vector((self.x, self.y, self.z))


def install_blender_stubs():
    bpy = types.ModuleType("bpy")
    bpy.data = types.SimpleNamespace()
    bpy.context = types.SimpleNamespace()

    props = types.ModuleType("bpy.props")
    for name in ("BoolProperty", "EnumProperty", "FloatProperty", "IntProperty", "PointerProperty"):
        setattr(props, name, lambda *args, **kwargs: None)

    bpy_types = types.ModuleType("bpy.types")
    for name in ("Operator", "Panel", "PropertyGroup", "Collection", "Object", "Material", "Action", "Node"):
        setattr(bpy_types, name, type(name, (), {}))

    mathutils = types.ModuleType("mathutils")
    mathutils.Vector = Vector
    mathutils.noise = types.SimpleNamespace(fractal=lambda *args, **kwargs: 0.0, turbulence=lambda *args, **kwargs: 0.0)

    sys.modules["bpy"] = bpy
    sys.modules["bpy.props"] = props
    sys.modules["bpy.types"] = bpy_types
    sys.modules["mathutils"] = mathutils


def load_module(name, relative_path):
    install_blender_stubs()
    module_path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SmartCityExtensionTests(unittest.TestCase):
    def test_ecology_layout_keeps_water_and_traffic_outside_city_buffer(self):
        ecology_common = load_module("ecology_common", "iCity/smart_city/ecology_common.py")
        settings = types.SimpleNamespace(
            seed=12,
            terrain_margin=55.0,
            lake_radius=16.0,
            lake_depth=7.5,
            river_width=7.0,
            traffic_loop_radius_x=14.0,
            traffic_loop_radius_y=8.5,
            road_width=3.8,
        )

        layout = ecology_common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)

        lake_clearance = layout["lake_center"].length - max(layout["lake_radius_x"], layout["lake_radius_y"])
        self.assertGreaterEqual(lake_clearance, 36.0)

        river_clearance = min(point.length for point in layout["river_points"]) - settings.river_width * 0.5
        self.assertGreaterEqual(river_clearance, 36.0)

        traffic_clearance = (
            layout["traffic_center"].length
            - max(settings.traffic_loop_radius_x, settings.traffic_loop_radius_y)
            - settings.road_width * 0.5
        )
        self.assertGreaterEqual(traffic_clearance, 34.0)

    def test_asset_texture_lookup_accepts_numbered_duplicate_files(self):
        asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")

        path = asset_extension.get_texture_path("RoadLines010_2K-JPG_Opacity.jpg")

        self.assertIsNotNone(path)
        self.assertTrue(path.name.startswith("RoadLines010_2K-JPG_Opacity"))


if __name__ == "__main__":
    unittest.main()

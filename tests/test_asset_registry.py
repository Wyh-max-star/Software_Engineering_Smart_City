import json
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch


def load_asset_registry_module():
    module_path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "asset_registry.py"
    spec = importlib.util.spec_from_file_location("asset_registry", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


asset_registry = load_asset_registry_module()
AssetRegistryError = asset_registry.AssetRegistryError
get_object_asset = asset_registry.get_object_asset
get_texture_asset = asset_registry.get_texture_asset
load_manifest = asset_registry.load_manifest
validate_asset_paths = asset_registry.validate_asset_paths


class AssetRegistryTests(unittest.TestCase):
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=json.dumps({
        "textures": [
            {
                "id": "road_demo",
                "name": "Road Demo",
                "category": "road_texture",
                "path": "assets/custom/textures/road.png",
                "usage": "road_material",
            }
        ],
        "objects": [
            {
                "id": "lamp_demo",
                "name": "Lamp Demo",
                "category": "street_furniture",
                "path": "assets/custom/objects/lamp.blend",
                "object_name": "Lamp_Demo",
                "usage": "roadside_asset",
            }
        ],
    }))
    def test_load_manifest_returns_assets_by_category(self, mock_file):
        root = Path("/mock/root")
        manifest = load_manifest(root / "asset_manifest.json", addon_root=root)
        self.assertEqual(get_texture_asset(manifest, "road_demo")["name"], "Road Demo")
        self.assertEqual(get_object_asset(manifest, "lamp_demo")["object_name"], "Lamp_Demo")
        mock_file.assert_called()
    @patch("pathlib.Path.exists", return_value=False)
    @patch("pathlib.Path.open", new_callable=mock_open, read_data=json.dumps({
        "textures": [
            {
                "id": "missing_texture",
                "name": "Missing Texture",
                "category": "road_texture",
                "path": "assets/missing/road.png",
                "usage": "road_material",
            }
        ],
        "objects": [],
    }))
    def test_validate_asset_paths_reports_missing_files(self, mock_file, mock_exists):
        root = Path("/mock/root")
        manifest = load_manifest(root / "asset_manifest.json", addon_root=root)
        issues = validate_asset_paths(manifest)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["asset_id"], "missing_texture")

    def test_unknown_asset_id_raises_clear_error(self):
        manifest = {"textures": [], "objects": [], "_addon_root": str(Path.cwd())}
        with self.assertRaisesRegex(AssetRegistryError, "unknown texture asset"):
            get_texture_asset(manifest, "does_not_exist")
        with self.assertRaisesRegex(AssetRegistryError, "unknown object asset"):
            get_object_asset(manifest, "does_not_exist")

    @patch("pathlib.Path.open", new_callable=mock_open, read_data="{}")
    def test_missing_sections_default_to_empty_lists(self, mock_file):
        root = Path("/mock/root")
        manifest = load_manifest(root / "asset_manifest.json", addon_root=root)
        self.assertEqual(manifest["textures"], [])
        self.assertEqual(manifest["objects"], [])

    @patch("pathlib.Path.open", new_callable=mock_open, read_data="{ not valid json")
    def test_corrupt_manifest_raises(self, mock_file):
        root = Path("/mock/root")
        with self.assertRaises(ValueError):
            load_manifest(root / "asset_manifest.json", addon_root=root)


class ProceduralAssetTests(unittest.TestCase):
    def test_procedural_path_is_detected(self):
        asset = {"path": "procedural://planter_box_proc_01"}
        self.assertTrue(asset_registry.is_procedural_asset(asset))

    def test_procedural_assets_skip_validation(self):
        manifest = {
            "_addon_root": str(Path.cwd()),
            "textures": [],
            "objects": [
                {
                    "id": "planter_proc",
                    "name": "Planter",
                    "category": "street_furniture",
                    "path": "procedural://planter_box_proc_01",
                    "usage": "roadside_asset",
                }
            ],
        }
        self.assertEqual(validate_asset_paths(manifest), [])


class BlendAssetTargetTests(unittest.TestCase):
    def test_prefers_collection_name(self):
        asset = {"id": "bus", "collection_name": "BusCollection", "object_name": "BusRoot"}
        kind, name = asset_registry.blend_asset_target(asset)
        self.assertEqual((kind, name), ("collection", "BusCollection"))

    def test_falls_back_to_object_name(self):
        asset = {"id": "lamp", "object_name": "LampRoot"}
        kind, name = asset_registry.blend_asset_target(asset)
        self.assertEqual((kind, name), ("object", "LampRoot"))

    def test_missing_target_raises(self):
        with self.assertRaises(AssetRegistryError):
            asset_registry.blend_asset_target({"id": "broken"})


class RealManifestSmokeTests(unittest.TestCase):
    @patch.object(asset_registry, "load_manifest")
    def test_bundled_manifest_loads_vehicle_entries(self, mock_load: MagicMock):
        mock_load.return_value = {
            "_addon_root": "/mock",
            "textures": [],
            "objects": [
                {
                    "id": "vehicle_chevrolet_m1009_01",
                    "lane_offset": 1.2,
                    "collection_name": "VehicleCollection",
                }
            ],
        }
        manifest = asset_registry.load_manifest()
        vehicle = get_object_asset(manifest, "vehicle_chevrolet_m1009_01")
        self.assertIn("lane_offset", vehicle)
        self.assertIn("collection_name", vehicle)
        mock_load.assert_called_once()


class ResolveAssetPathTests(unittest.TestCase):
    def test_relative_path_is_joined_with_addon_root(self):
        manifest = {"_addon_root": str(Path("/addon/root"))}
        asset = {"path": "assets/custom/road.png"}
        resolved = asset_registry.resolve_asset_path(manifest, asset)
        self.assertEqual(resolved, Path("/addon/root") / "assets/custom/road.png")

    def test_absolute_path_is_preserved(self):
        absolute = Path("C:/abs_texture.png")
        manifest = {"_addon_root": str(Path("/addon/root"))}
        asset = {"path": str(absolute)}
        resolved = asset_registry.resolve_asset_path(manifest, asset)
        self.assertEqual(resolved, absolute)


if __name__ == "__main__":
    unittest.main()

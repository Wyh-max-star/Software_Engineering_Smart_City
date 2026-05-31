import json
import importlib.util
import tempfile
import unittest
from pathlib import Path


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
    def test_load_manifest_returns_assets_by_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            texture = root / "assets" / "custom" / "textures" / "road.png"
            model = root / "assets" / "custom" / "objects" / "lamp.blend"
            texture.parent.mkdir(parents=True)
            model.parent.mkdir(parents=True)
            texture.write_text("texture", encoding="utf-8")
            model.write_text("blend", encoding="utf-8")
            manifest_path = root / "asset_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
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
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            manifest = load_manifest(manifest_path, addon_root=root)

        self.assertEqual(get_texture_asset(manifest, "road_demo")["name"], "Road Demo")
        self.assertEqual(get_object_asset(manifest, "lamp_demo")["object_name"], "Lamp_Demo")

    def test_validate_asset_paths_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "asset_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
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
                    }
                ),
                encoding="utf-8",
            )
            manifest = load_manifest(manifest_path, addon_root=root)

            issues = validate_asset_paths(manifest)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["asset_id"], "missing_texture")
        self.assertIn("assets/missing/road.png", issues[0]["path"])

    def test_unknown_asset_id_raises_clear_error(self):
        manifest = {"textures": [], "objects": [], "_addon_root": str(Path.cwd())}

        with self.assertRaisesRegex(AssetRegistryError, "unknown texture asset"):
            get_texture_asset(manifest, "does_not_exist")

        with self.assertRaisesRegex(AssetRegistryError, "unknown object asset"):
            get_object_asset(manifest, "does_not_exist")


if __name__ == "__main__":
    unittest.main()

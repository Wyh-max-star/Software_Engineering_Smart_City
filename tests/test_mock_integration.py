"""Standard ``unittest.mock`` integration tests (white-box with test doubles).

These complement the hand-written stubs in ``blender_test_utils`` by exercising
``@patch`` / ``MagicMock`` on module boundaries — the pattern expected in SE
coursework for dependency isolation.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from test_markers import white_box  # noqa: E402


traffic_extension = load_module("traffic_extension", "iCity/smart_city/traffic_extension.py")
asset_extension = load_module("asset_extension", "iCity/smart_city/asset_extension.py")


@white_box
class MockBundledVehicleProfileTests(unittest.TestCase):
    """``bundled_vehicle_profile`` merges manifest fields via mocked registry."""

    @patch.object(traffic_extension, "_manifest_object_asset")
    def test_manifest_lane_offset_overrides_default(self, mock_lookup: MagicMock):
        mock_lookup.return_value = {
            "lane_offset": 2.5,
            "scale_ratio": 1.1,
            "rotation_z_correction": 15.0,
        }
        profile = traffic_extension.bundled_vehicle_profile("CAR")
        self.assertEqual(profile["lane_offset"], 2.5)
        self.assertEqual(profile["scale_ratio"], 1.1)
        mock_lookup.assert_called_once()
        self.assertEqual(mock_lookup.call_args[0][0], traffic_extension.bundled_vehicle_asset_id("CAR"))

    @patch.object(traffic_extension, "_manifest_object_asset", return_value=None)
    def test_missing_manifest_keeps_defaults(self, mock_lookup: MagicMock):
        profile = traffic_extension.bundled_vehicle_profile("TAXI")
        defaults = traffic_extension.TRAFFIC_BUNDLED_VEHICLE_DEFAULTS
        self.assertEqual(profile["lane_offset"], defaults["lane_offset"])
        mock_lookup.assert_called_once()


@white_box
class MockTextureLookupTests(unittest.TestCase):
    """``get_texture_path`` with ``@patch`` on ``texture_directories``."""

    @patch.object(asset_extension, "texture_directories")
    def test_patch_finds_file_in_mocked_directory(self, mock_dirs: MagicMock):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "road_demo.jpg").write_text("x", encoding="utf-8")
            mock_dirs.return_value = (directory,)

            path = asset_extension.get_texture_path("road_demo.jpg")

            self.assertIsNotNone(path)
            self.assertEqual(path.name, "road_demo.jpg")
            mock_dirs.assert_called()

    @patch.object(asset_extension, "texture_directories")
    def test_patch_returns_none_when_missing(self, mock_dirs: MagicMock):
        with tempfile.TemporaryDirectory() as tmp:
            mock_dirs.return_value = (Path(tmp),)
            self.assertIsNone(asset_extension.get_texture_path("missing.jpg"))


@white_box
class MockManifestLoadTests(unittest.TestCase):
    """``load_manifest`` I/O boundary with ``@patch`` on ``open``."""

    @patch.object(Path, "open", side_effect=OSError("disk unavailable"))
    def test_open_failure_propagates(self, mock_open):
        import importlib.util

        registry_path = Path(__file__).resolve().parents[1] / "iCity" / "smart_city" / "asset_registry.py"
        spec = importlib.util.spec_from_file_location("asset_registry_mock_io", registry_path)
        registry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registry)

        manifest_path = Path(__file__).resolve().parent / "dummy_manifest.json"
        with self.assertRaises(OSError):
            registry.load_manifest(manifest_path, addon_root=Path("/tmp"))
        mock_open.assert_called()


if __name__ == "__main__":
    unittest.main()

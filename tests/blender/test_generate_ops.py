"""Confirmation / system test that runs *inside* Blender (headless).

Exercises generate/clear operators for Asset Expansion, Ecology plots,
standalone Traffic, and Pedestrians. Results are written to ``test-reports/``.

Run (PowerShell — note the leading ``&``):

    & "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe" `
        --background --python tests\\blender\\test_generate_ops.py
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import bpy

REPO_ROOT = Path(__file__).resolve().parents[2]
SMART_CITY_DIR = REPO_ROOT / "iCity" / "smart_city"
REPORTS_DIR = REPO_ROOT / "test-reports"
if str(SMART_CITY_DIR) not in sys.path:
    sys.path.insert(0, str(SMART_CITY_DIR))

import asset_extension  # noqa: E402
import ecology_extension  # noqa: E402
import pedestrian_extension  # noqa: E402
import traffic_extension  # noqa: E402

ICITY_ROOT_COLLECTION = "ICity"
ICITY_BASE_OBJECT = "ICity Base"

# Black-box scenario metadata for classified reports.
SCENARIO_META = {
    "scenario_generate_streetlights": ("Asset Expansion", "icity.generate_streetlights"),
    "scenario_clear_streetlights": ("Asset Expansion", "icity.clear_asset_expansion"),
    "scenario_add_ecology_lake_plot": ("Ecology", "icity.add_ecology_plot"),
    "scenario_add_ecology_river_plot": ("Ecology", "icity.add_ecology_plot"),
    "scenario_clear_ecology": ("Ecology", "icity.clear_ecology"),
    "scenario_generate_traffic": ("Traffic", "icity.generate_traffic"),
    "scenario_clear_traffic": ("Traffic", "icity.clear_traffic"),
    "scenario_generate_pedestrians": ("Pedestrians", "icity.generate_pedestrians"),
    "scenario_clear_pedestrians": ("Pedestrians", "icity.clear_pedestrians"),
    "scenario_traffic_requires_icity_start": ("Traffic", "icity.generate_traffic"),
    "scenario_pedestrians_require_icity_start": ("Pedestrians", "icity.generate_pedestrians"),
}

_failures: list[str] = []
_results: list[tuple[str, str, str]] = []
_current_scenario = "(setup)"


def check(condition: bool, message: str) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  {status}: {message}")
    _results.append((_current_scenario, status, message))
    if not condition:
        _failures.append(message)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_minimal_city() -> bpy.types.Collection:
    """Minimal ICity root + base mesh (fallback band layout for traffic/peds)."""
    root = bpy.data.collections.new(ICITY_ROOT_COLLECTION)
    bpy.context.scene.collection.children.link(root)

    mesh = bpy.data.meshes.new(ICITY_BASE_OBJECT)
    mesh.from_pydata(
        [(-25, -25, 0), (25, -25, 0), (25, 25, 0), (-25, 25, 0)],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    base = bpy.data.objects.new(ICITY_BASE_OBJECT, mesh)
    root.objects.link(base)
    return root


def count_vehicle_carriers(collection: bpy.types.Collection | None) -> int:
    """Count animated vehicle roots (carrier empties), not appended mesh parts."""

    if collection is None:
        return 0
    return sum(
        1
        for obj in collection.all_objects
        if obj.type == "EMPTY" and obj.name.endswith("_Carrier") and obj.name.startswith("ICITY_TRAFFIC_")
    )


def count_pedestrian_anchors(collection: bpy.types.Collection | None, role: str) -> int:
    """Count walker/idler anchor empties (``ICITY_PED_Walker_N`` / ``ICITY_PED_Idler_N``)."""

    if collection is None:
        return 0
    prefix = f"ICITY_PED_{role}_"
    return sum(
        1
        for obj in collection.all_objects
        if obj.type == "EMPTY" and obj.name.startswith(prefix) and not obj.name.endswith("_Mount")
    )


def configure_ecology_settings(mode: str) -> None:
    settings = bpy.context.scene.icity_ecology_settings
    settings.enable_ecology_block = True
    settings.ecology_plot_mode = mode
    settings.plot_shape = "RECTANGLE"
    settings.plot_width = 60.0
    settings.plot_depth = 45.0
    settings.terrain_resolution = 24
    settings.animation_start = 1
    settings.animation_end = 120
    if mode == "LAKE_RING":
        settings.boat_count = 1
    if mode == "RIVER_VALLEY":
        settings.river_source_width = 6.0
        settings.river_mouth_width = 12.0


def scenario_generate_streetlights() -> None:
    print("Scenario: generate streetlights on a normal city")
    reset_scene()
    asset_extension.register()
    build_minimal_city()

    bpy.context.scene.icity_asset_settings.streetlight_count = 12
    result = bpy.ops.icity.generate_streetlights()
    check(result == {"FINISHED"}, "streetlights operator returns FINISHED")

    collection = bpy.data.collections.get(asset_extension.ASSET_STREETLIGHT_COLLECTION)
    check(collection is not None, "streetlight collection created")
    if collection is not None:
        lights = [obj for obj in collection.all_objects if obj.type == "LIGHT"]
        check(len(lights) == 12, f"expected 12 lights, got {len(lights)}")

    asset_extension.unregister()


def scenario_clear_streetlights() -> None:
    print("Scenario: clearing removes asset expansion content")
    reset_scene()
    asset_extension.register()
    build_minimal_city()

    bpy.context.scene.icity_asset_settings.streetlight_count = 8
    bpy.ops.icity.generate_streetlights()
    bpy.ops.icity.clear_asset_expansion()

    check(
        bpy.data.collections.get(asset_extension.ASSET_ROOT_COLLECTION) is None,
        "asset expansion collection fully removed",
    )
    asset_extension.unregister()


def scenario_add_ecology_lake_plot() -> None:
    print("Scenario: add ecology plot (lake ring)")
    reset_scene()
    ecology_extension.register()
    build_minimal_city()
    configure_ecology_settings("LAKE_RING")

    result = bpy.ops.icity.add_ecology_plot()
    check(result == {"FINISHED"}, "lake plot operator returns FINISHED")

    ecology_collection = bpy.data.collections.get(ecology_extension.ECOLOGY_COLLECTION)
    check(ecology_collection is not None, "ecology root collection created")
    check(
        bpy.data.objects.get("ICITY_ECO_Terrain_001") is not None,
        "lake plot terrain object created",
    )
    check(
        bpy.data.objects.get("ICITY_ECO_Lake_001") is not None,
        "lake water object created",
    )

    ecology_extension.unregister()


def scenario_add_ecology_river_plot() -> None:
    print("Scenario: add ecology plot (river valley)")
    reset_scene()
    ecology_extension.register()
    build_minimal_city()
    configure_ecology_settings("RIVER_VALLEY")

    result = bpy.ops.icity.add_ecology_plot()
    check(result == {"FINISHED"}, "river plot operator returns FINISHED")
    check(
        bpy.data.objects.get("ICITY_ECO_Terrain_001") is not None,
        "river plot terrain object created",
    )
    check(
        bpy.data.objects.get("ICITY_ECO_River_001") is not None,
        "river water ribbon created",
    )

    ecology_extension.unregister()


def scenario_clear_ecology() -> None:
    print("Scenario: clear ecology removes ecology tree")
    reset_scene()
    ecology_extension.register()
    build_minimal_city()
    configure_ecology_settings("LAKE_RING")
    bpy.ops.icity.add_ecology_plot()
    bpy.ops.icity.clear_ecology()

    check(
        bpy.data.collections.get(ecology_extension.ECOLOGY_COLLECTION) is None,
        "ecology collection removed after clear",
    )
    check(
        bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None,
        "base ICity collection remains after ecology clear",
    )
    ecology_extension.unregister()


def scenario_generate_traffic() -> None:
    print("Scenario: generate standalone traffic")
    reset_scene()
    traffic_extension.register()
    build_minimal_city()

    settings = bpy.context.scene.icity_traffic_settings
    settings.car_count = 3
    settings.taxi_count = 1
    settings.bus_count = 1
    settings.animation_start = 1
    settings.animation_end = 60

    result = bpy.ops.icity.generate_traffic()
    check(result == {"FINISHED"}, "traffic operator returns FINISHED")

    traffic_root = bpy.data.collections.get(traffic_extension.TRAFFIC_ROOT_COLLECTION)
    vehicle_coll = bpy.data.collections.get(traffic_extension.TRAFFIC_VEHICLE_COLLECTION)
    path_coll = bpy.data.collections.get(traffic_extension.TRAFFIC_PATH_COLLECTION)

    check(traffic_root is not None, "ICity Traffic collection created")
    check(vehicle_coll is not None, "vehicle sub-collection created")
    check(path_coll is not None, "path sub-collection created")

    if vehicle_coll is not None:
        vehicle_count = count_vehicle_carriers(vehicle_coll)
        check(vehicle_count == 5, f"expected 5 vehicle carriers (3+1+1), got {vehicle_count}")

    traffic_extension.unregister()


def scenario_clear_traffic() -> None:
    print("Scenario: clear traffic only")
    reset_scene()
    traffic_extension.register()
    build_minimal_city()

    bpy.context.scene.icity_traffic_settings.car_count = 2
    bpy.ops.icity.generate_traffic()
    bpy.ops.icity.clear_traffic()

    check(
        bpy.data.collections.get(traffic_extension.TRAFFIC_ROOT_COLLECTION) is None,
        "traffic root collection removed after clear",
    )
    check(
        bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None,
        "base ICity collection remains after traffic clear",
    )
    traffic_extension.unregister()


def scenario_generate_pedestrians() -> None:
    print("Scenario: generate standalone pedestrians")
    reset_scene()
    pedestrian_extension.register()
    build_minimal_city()

    settings = bpy.context.scene.icity_pedestrian_settings
    settings.walker_count = 4
    settings.idle_count = 2
    settings.animation_start = 1
    settings.animation_end = 60

    result = bpy.ops.icity.generate_pedestrians()
    check(result == {"FINISHED"}, "pedestrian operator returns FINISHED")

    ped_root = bpy.data.collections.get(pedestrian_extension.PED_ROOT_COLLECTION)
    walker_coll = bpy.data.collections.get(pedestrian_extension.PED_WALKER_COLLECTION)
    idler_coll = bpy.data.collections.get(pedestrian_extension.PED_IDLER_COLLECTION)

    check(ped_root is not None, "ICity Pedestrians collection created")
    check(walker_coll is not None, "walker sub-collection created")
    check(idler_coll is not None, "idler sub-collection created")

    if walker_coll is not None:
        walkers = count_pedestrian_anchors(walker_coll, "Walker")
        check(walkers == 4, f"expected 4 walker anchors, got {walkers}")
    if idler_coll is not None:
        idlers = count_pedestrian_anchors(idler_coll, "Idler")
        check(idlers == 2, f"expected 2 idler anchors, got {idlers}")

    pedestrian_extension.unregister()


def scenario_clear_pedestrians() -> None:
    print("Scenario: clear pedestrians only")
    reset_scene()
    pedestrian_extension.register()
    build_minimal_city()

    bpy.context.scene.icity_pedestrian_settings.walker_count = 2
    bpy.context.scene.icity_pedestrian_settings.idle_count = 1
    bpy.ops.icity.generate_pedestrians()
    bpy.ops.icity.clear_pedestrians()

    check(
        bpy.data.collections.get(pedestrian_extension.PED_ROOT_COLLECTION) is None,
        "pedestrian root collection removed after clear",
    )
    check(
        bpy.data.collections.get(ICITY_ROOT_COLLECTION) is not None,
        "base ICity collection remains after pedestrian clear",
    )
    pedestrian_extension.unregister()


def scenario_traffic_requires_icity_start() -> None:
    print("Scenario: traffic generation without ICity Start is rejected")
    reset_scene()
    traffic_extension.register()

    rejected = False
    try:
        result = bpy.ops.icity.generate_traffic()
        rejected = result == {"CANCELLED"}
    except RuntimeError as exc:
        rejected = "iCity Start" in str(exc) or "traffic" in str(exc).lower()

    check(rejected, "traffic generation rejected without ICity root")
    traffic_extension.unregister()


def scenario_pedestrians_require_icity_start() -> None:
    print("Scenario: pedestrian generation without ICity Start is rejected")
    reset_scene()
    pedestrian_extension.register()

    rejected = False
    try:
        result = bpy.ops.icity.generate_pedestrians()
        rejected = result == {"CANCELLED"}
    except RuntimeError as exc:
        rejected = "iCity Start" in str(exc) or "pedestrian" in str(exc).lower()

    check(rejected, "pedestrian generation rejected without ICity root")
    pedestrian_extension.unregister()


def run_scenario(scenario) -> None:
    global _current_scenario
    _current_scenario = scenario.__name__
    try:
        scenario()
    except Exception as exc:  # noqa: BLE001
        message = f"{scenario.__name__} raised {type(exc).__name__}: {exc}"
        print(f"  FAIL: {message}")
        _results.append((_current_scenario, "FAIL", message))
        _failures.append(message)


def write_report() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overall = "FAIL" if _failures else "PASS"
    pass_count = sum(1 for _s, status, _m in _results if status == "PASS")

    lines = [
        "# 黑盒系统测试报告 (Black-box / Blender headless)",
        "",
        f"- 运行时间：{timestamp}",
        f"- Blender 版本：{bpy.app.version_string}",
        f"- 测试类型：**黑盒** — 仅验证算子返回值与场景可观测结果",
        f"- 总体结果：**{overall}**",
        f"- 检查项：共 {len(_results)}，通过 {pass_count}，失败 {len(_failures)}",
        "",
        "> 与白盒/灰盒汇总合并见 [`taxonomy-summary.md`](taxonomy-summary.md)。",
        "",
    ]

    by_module: dict[str, list[tuple[str, str, str]]] = {}
    for scenario, status, message in _results:
        module, operator = SCENARIO_META.get(scenario, ("Other", "—"))
        by_module.setdefault(module, []).append((scenario, operator, status, message))

    for module in (
        "Asset Expansion",
        "Ecology",
        "Traffic",
        "Pedestrians",
        "Other",
    ):
        entries = by_module.get(module)
        if not entries:
            continue
        lines += [
            f"## {module}",
            "",
            "| 场景 | 算子 / 接口 | 检查项 | 结果 |",
            "|---|---|---|---|",
        ]
        for scenario, operator, status, message in entries:
            lines.append(f"| `{scenario}` | `{operator}` | {message} | {status} |")
        lines.append("")

    lines += [
        "## 全量检查项（机器可读）",
        "",
        "| 场景 | 检查项 | 结果 |",
        "|---|---|---|",
    ]
    for scenario, status, message in _results:
        lines.append(f"| {scenario} | {message} | {status} |")
    lines.append("")

    (REPORTS_DIR / "blender-report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORTS_DIR / 'blender-report.md'}")


def refresh_taxonomy_summary() -> None:
    tools_dir = REPO_ROOT / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    from taxonomy_report import write_taxonomy_summary  # noqa: E402

    path = write_taxonomy_summary(REPORTS_DIR)
    print(f"Updated taxonomy summary: {path}")


def main() -> None:
    for scenario in (
        scenario_generate_streetlights,
        scenario_clear_streetlights,
        scenario_add_ecology_lake_plot,
        scenario_add_ecology_river_plot,
        scenario_clear_ecology,
        scenario_generate_traffic,
        scenario_clear_traffic,
        scenario_generate_pedestrians,
        scenario_clear_pedestrians,
        scenario_traffic_requires_icity_start,
        scenario_pedestrians_require_icity_start,
    ):
        run_scenario(scenario)

    write_report()
    refresh_taxonomy_summary()

    print("")
    if _failures:
        print(f"RESULT: {len(_failures)} check(s) failed")
        sys.exit(1)
    print("RESULT: all checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()

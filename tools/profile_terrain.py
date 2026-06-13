"""Performance baseline for the terrain height field (the O(resolution^2) hot path).

``create_terrain`` samples ``terrain_height`` once per grid vertex, so the cost
grows with the square of ``terrain_resolution``. This script profiles the pure
sampling loop (Blender's noise is stubbed to a constant) so you can capture a
baseline *before* optimizing, exactly as the lecture recommends:
measure -> find the bottleneck -> optimize -> measure again.

Run:

    python tools/profile_terrain.py --resolution 96
"""

from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tests"))

from blender_test_utils import Vector, load_module  # noqa: E402


def _settings(seed=12):
    return types.SimpleNamespace(
        seed=seed,
        terrain_margin=55.0,
        lake_radius=16.0,
        lake_depth=7.5,
        river_width=7.0,
        river_depth=2.8,
        mountain_height=11.0,
        noise_strength=2.8,
        traffic_loop_radius_x=14.0,
        traffic_loop_radius_y=8.5,
        road_width=3.8,
    )


def sample_terrain(resolution: int) -> int:
    common = load_module("ecology_common", "iCity/smart_city/ecology_common.py")
    water = load_module("ecology_water", "iCity/smart_city/ecology_water.py")
    settings = _settings()
    layout = common.compute_layout(Vector((0.0, 0.0, 0.0)), 30.0, 0.0, settings)

    terrain_radius = layout["terrain_radius"]
    step = (terrain_radius * 2.0) / resolution
    samples = 0
    for y_index in range(resolution + 1):
        y = -terrain_radius + y_index * step
        for x_index in range(resolution + 1):
            x = -terrain_radius + x_index * step
            water.terrain_height(Vector((x, y)), layout, settings)
            samples += 1
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=int, default=96, help="grid resolution (default 96)")
    parser.add_argument("--top", type=int, default=15, help="number of profile rows to show")
    args = parser.parse_args()

    profiler = cProfile.Profile()
    profiler.enable()
    samples = sample_terrain(args.resolution)
    profiler.disable()

    print(f"Sampled {samples} terrain vertices at resolution {args.resolution}.")
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative").print_stats(args.top)


if __name__ == "__main__":
    main()

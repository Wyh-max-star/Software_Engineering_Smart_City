# -*- coding: utf-8 -*-
"""Unit tests for layout_sketch: dark mask, skeleton tracing, sketch-to-graph pipeline."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blender_test_utils import load_module  # noqa: E402
from test_markers import white_box  # noqa: E402

ls = load_module("layout_sketch", "iCity/smart_city/layout_sketch.py")


def _blank_rgba(width: int, height: int) -> list[float]:
    return [1.0, 1.0, 1.0, 1.0] * (width * height)


def _set_pixel(pixels: list[float], width: int, x: int, y: int, rgba=(0.0, 0.0, 0.0, 1.0)):
    offset = (y * width + x) * 4
    pixels[offset : offset + 4] = list(rgba)


def _draw_rect_outline(pixels: list[float], width: int, height: int, margin: int = 4):
    left = margin
    right = width - margin - 1
    top = margin
    bottom = height - margin - 1
    for x in range(left, right + 1):
        _set_pixel(pixels, width, x, top)
        _set_pixel(pixels, width, x, bottom)
    for y in range(top, bottom + 1):
        _set_pixel(pixels, width, left, y)
        _set_pixel(pixels, width, right, y)


def _rect_skeleton(width: int, height: int, margin: int = 4) -> list[list[bool]]:
    mask = [[False] * width for _ in range(height)]
    left = margin
    right = width - margin - 1
    top = margin
    bottom = height - margin - 1
    for x in range(left, right + 1):
        mask[top][x] = True
        mask[bottom][x] = True
    for y in range(top, bottom + 1):
        mask[y][left] = True
        mask[y][right] = True
    return mask


@white_box
class DarkMaskTests(unittest.TestCase):
    def test_white_pixels_produce_empty_mask(self):
        pixels = _blank_rgba(16, 16)
        mask = ls.rgba_pixels_to_dark_mask(16, 16, pixels, threshold=0.45)
        self.assertFalse(any(any(row) for row in mask))

    def test_black_line_pixels_become_active(self):
        pixels = _blank_rgba(32, 32)
        for x in range(8, 24):
            _set_pixel(pixels, 32, x, 16)
        mask = ls.rgba_pixels_to_dark_mask(32, 32, pixels, threshold=0.45)
        active = sum(row.count(True) for row in mask)
        self.assertGreater(active, 0)


@white_box
class SkeletonThinningTests(unittest.TestCase):
    def test_thin_binary_mask_reduces_thick_stroke(self):
        mask = [[False] * 10 for _ in range(10)]
        for y in range(3, 7):
            for x in range(2, 8):
                mask[y][x] = True
        thinned = ls.thin_binary_mask(mask)
        active_per_row = [sum(row) for row in thinned]
        self.assertLessEqual(max(active_per_row), 2)


@white_box
class SkeletonToGraphTests(unittest.TestCase):
    def test_rectangle_skeleton_yields_four_nodes_and_four_edges(self):
        mask = _rect_skeleton(48, 48, margin=6)
        graph, stats = ls.skeleton_to_layout_graph(mask, world_width=100.0)
        self.assertEqual(len(graph["nodes"]), 4)
        self.assertEqual(len(graph["edges"]), 4)
        self.assertGreater(stats["dark_pixels"], 0)

    def test_empty_mask_raises(self):
        mask = [[False] * 8 for _ in range(8)]
        with self.assertRaises(ValueError):
            ls.skeleton_to_layout_graph(mask)


@white_box
class SketchPipelineTests(unittest.TestCase):
    def test_image_pixels_to_layout_graph_rectangle(self):
        width, height = 64, 64
        pixels = _blank_rgba(width, height)
        _draw_rect_outline(pixels, width, height, margin=8)
        graph, stats = ls.image_pixels_to_layout_graph(
            width,
            height,
            pixels,
            threshold=0.45,
            max_dimension=64,
            world_width=200.0,
            endpoint_snap_distance=2.5,
            maximum_turn_degrees=20.0,
        )
        self.assertGreaterEqual(len(graph["nodes"]), 4)
        self.assertGreaterEqual(len(graph["edges"]), 4)
        self.assertEqual(stats["input_width"], width)
        self.assertEqual(stats["input_height"], height)


if __name__ == "__main__":
    unittest.main()

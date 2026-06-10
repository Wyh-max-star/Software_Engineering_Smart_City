# Traffic Corner Rounding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make 90-degree vehicle turns in iCity traffic appear rounder and less abrupt while staying compatible with the current road-following pipeline.

**Architecture:** Extend `prepare_vehicle_path()` with an explicit corner-rounding stage that detects sharp turns, trims the hard corner, inserts a short rounded segment, and then continues through the existing resample/smooth pipeline. Keep the new controls in vehicle asset/profile metadata so tuning stays data-driven.

**Tech Stack:** Blender Python addon code, existing traffic path preparation helpers, `unittest`.

---

### Task 1: Add red tests for rounded-corner behavior

**Files:**
- Modify: `tests/test_smart_city_extensions.py`

- [ ] Add a test that `bundled_vehicle_profile()` reads corner-rounding metadata.
- [ ] Add a test that a 90-degree corner no longer contains the raw corner point after path preparation.
- [ ] Run the focused tests and verify they fail for missing behavior.

### Task 2: Implement corner rounding in traffic path prep

**Files:**
- Modify: `iCity/smart_city/traffic_extension.py`
- Modify: `iCity/smart_city/manifests/asset_manifest.json`

- [ ] Add default profile fields for corner-rounding radius, segment count, and angle threshold.
- [ ] Implement a helper that replaces sharp corners with rounded intermediate points.
- [ ] Call that helper from `prepare_vehicle_path()` before final smoothing/resampling.
- [ ] Add matching metadata to the Chevrolet asset manifest entry.

### Task 3: Verify regression safety

**Files:**
- Modify: `tests/test_smart_city_extensions.py` only if assertions need cleanup

- [ ] Run focused corner-rounding tests.
- [ ] Run `python -m unittest tests.test_asset_registry tests.test_smart_city_extensions -v`.
- [ ] Confirm the worktree only contains scoped turn-smoothing changes.

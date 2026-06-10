# ICity Traffic Vehicle Asset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bundle traffic vehicle models into the iCity plugin and make the traffic module use them for road vehicles with a procedural fallback.

**Architecture:** Register the `.blend` files in the smart-city asset manifest as collection-based traffic vehicle assets. Extend traffic generation to load those collections once as hidden source hierarchies, duplicate them per vehicle follower, and fall back to the current procedural proxy when an asset is unavailable.

**Tech Stack:** Blender Python addon API, existing iCity asset manifest, `unittest`, collection/object duplication.

---

### Task 1: Register the bundled vehicle assets

**Files:**
- Create: `iCity/assets/vehicles/1986_chevrolet_m1009.blend`
- Create: `iCity/assets/vehicles/lowpoly_bus.blend`
- Modify: `iCity/smart_city/manifests/asset_manifest.json`
- Test: `tests/test_asset_registry.py`

- [ ] Add manifest entries for the Chevrolet traffic vehicle and the low-poly bus using stable asset ids, relative asset paths, and `collection_name`.
- [ ] Add a failing asset-registry test that asserts collection-based `.blend` assets are preserved in manifest loading.
- [ ] Copy the `.blend` files into the plugin asset directory.
- [ ] Run `python -m unittest tests.test_asset_registry.AssetRegistryTests.test_load_manifest_supports_collection_based_blend_asset -v`.

### Task 2: Extend traffic generation to use the bundled model

**Files:**
- Modify: `iCity/smart_city/traffic_extension.py`
- Test: `tests/test_smart_city_extensions.py`

- [ ] Add failing tests for collection-based vehicle selection and fallback behavior.
- [ ] Add traffic helpers to load the manifest, append the collection asset once, duplicate the source hierarchy under animated carriers, and use the asset for `CAR` / `TAXI` / `BUS`.
- [ ] Keep the procedural proxy path as fallback when a bundled asset cannot be loaded.
- [ ] Run focused traffic tests after each red-green cycle.

### Task 3: Verify and document

**Files:**
- Modify: `iCity/smart_city/docs/README_TRAFFIC.md`
- Test: `tests/test_asset_registry.py`
- Test: `tests/test_smart_city_extensions.py`

- [ ] Update the traffic README to document the bundled Chevrolet asset, the bundled bus asset, and expected fallback behavior.
- [ ] Run `python -m unittest tests.test_asset_registry tests.test_smart_city_extensions -v`.
- [ ] If green, review `git diff` for scope and keep the changes limited to vehicle-asset integration.

---

## Status Note

As of `2026-06-06`, the implementation scope has been extended beyond the original Chevrolet-only pass:

- `CAR` / `TAXI` prefer `vehicle_chevrolet_m1009_01`
- `BUS` prefers `vehicle_lowpoly_bus_01`
- all three still fall back to procedural proxy meshes if asset loading fails

This note is here to keep the plan aligned with the current code and local branch state.

# ICity Traffic & Crowd Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone `ICity Traffic & Crowd` module on top of `iCity Start`, with separate generate/clear flow, vehicle and pedestrian animation, and tests that prove it stays decoupled from ecology.

**Architecture:** Add a new `traffic_extension.py` module that reads city bounds, computes an outer traffic/pedestrian layout, creates proxy assets and follow paths, and registers its own panel and operators. Keep ecology traffic untouched as legacy functionality, but stop using it for the new deliverable.

**Tech Stack:** Blender Python addon API, existing iCity addon structure, `unittest`, lightweight procedural mesh generation.

---

## File Map

- Create: `iCity/smart_city/traffic_extension.py`
- Modify: `iCity/__init__.py`
- Modify: `tests/test_smart_city_extensions.py`
- Create: `iCity/smart_city/docs/README_TRAFFIC.md`

### Task 1: Add failing tests for standalone traffic layout and registration

**Files:**
- Modify: `tests/test_smart_city_extensions.py`
- Test: `tests/test_smart_city_extensions.py`

- [ ] **Step 1: Write the failing tests**

Add tests that cover:

- `compute_traffic_layout()` keeps road center outside city radius
- pedestrian band stays outside vehicle band
- `vehicle_type_sequence()` includes car/taxi/bus in a stable order
- new module exports independent collection names

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_traffic_layout_stays_outside_city_radius
```

Expected:

- import failure or missing symbol failure for `traffic_extension.py`

- [ ] **Step 3: Write minimal implementation**

Create `traffic_extension.py` with pure layout helpers and constants first.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_traffic_layout_stays_outside_city_radius
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_smart_city_extensions.py iCity/smart_city/traffic_extension.py
git commit -m "test: add standalone traffic layout coverage"
```

### Task 2: Implement standalone traffic settings, collections, and operators

**Files:**
- Create: `iCity/smart_city/traffic_extension.py`
- Modify: `iCity/__init__.py`
- Test: `tests/test_smart_city_extensions.py`

- [ ] **Step 1: Write the failing tests**

Add tests that cover:

- `clear_traffic_crowd()` removes only traffic collections
- `ICITY_OT_GenerateTrafficCrowd.execute()` rejects invalid frame range
- generate path uses city bounds rather than ecology layout

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_clear_traffic_module_only_removes_traffic_collections
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_generate_traffic_module_rejects_invalid_frame_range
```

Expected:

- FAIL because helpers/operators do not exist yet

- [ ] **Step 3: Write minimal implementation**

Implement:

- settings property group
- root/child collection helpers
- generate and clear operators
- register/unregister functions

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_clear_traffic_module_only_removes_traffic_collections
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_generate_traffic_module_rejects_invalid_frame_range
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add iCity/__init__.py iCity/smart_city/traffic_extension.py tests/test_smart_city_extensions.py
git commit -m "feat: add standalone traffic module shell"
```

### Task 3: Implement vehicle and pedestrian generation

**Files:**
- Modify: `iCity/smart_city/traffic_extension.py`
- Test: `tests/test_smart_city_extensions.py`

- [ ] **Step 1: Write the failing tests**

Add tests that cover:

- vehicle sequence contains requested counts for car/taxi/bus
- pedestrian lane radii stay outside vehicle lane radii
- generated path durations are valid for animation

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_vehicle_type_sequence_balances_car_taxi_bus
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_pedestrian_band_stays_outside_vehicle_band
```

Expected:

- FAIL because sequencing/layout logic is incomplete

- [ ] **Step 3: Write minimal implementation**

Implement:

- vehicle meshes/materials
- pedestrian mesh/material
- path creation
- follower creation with stable phase offsets

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_vehicle_type_sequence_balances_car_taxi_bus
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_pedestrian_band_stays_outside_vehicle_band
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add iCity/smart_city/traffic_extension.py tests/test_smart_city_extensions.py
git commit -m "feat: add traffic and crowd generation"
```

### Task 4: Add Blender-facing panel and user documentation

**Files:**
- Modify: `iCity/smart_city/traffic_extension.py`
- Create: `iCity/smart_city/docs/README_TRAFFIC.md`

- [ ] **Step 1: Write the failing test**

Add a small test that asserts panel/operator classes are exported in the module `CLASSES` list.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_traffic_module_registers_panel_and_operators
```

Expected:

- FAIL until the panel/classes list is wired

- [ ] **Step 3: Write minimal implementation**

Implement:

- `ICITY_PT_TrafficCrowdPanel`
- control layout for counts, radii, animation frames
- `README_TRAFFIC.md` with Blender usage and manual test steps

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_smart_city_extensions.SmartCityExtensionTests.test_traffic_module_registers_panel_and_operators
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```bash
git add iCity/smart_city/traffic_extension.py iCity/smart_city/docs/README_TRAFFIC.md tests/test_smart_city_extensions.py
git commit -m "docs: add traffic module usage guide"
```

### Task 5: Full verification

**Files:**
- Modify: `tests/test_smart_city_extensions.py` if cleanup is needed

- [ ] **Step 1: Run focused unit suite**

Run:

```bash
python -m unittest tests.test_smart_city_extensions -v
```

Expected:

- all extension tests pass

- [ ] **Step 2: Run broader regression suite**

Run:

```bash
python -m unittest tests.test_asset_registry tests.test_smart_city_layout_samples tests.test_smart_city_extensions -v
```

Expected:

- all tests pass

- [ ] **Step 3: Update docs if verification exposed drift**

Make any needed wording fix in `README_TRAFFIC.md`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_smart_city_extensions.py iCity/smart_city/docs/README_TRAFFIC.md iCity/smart_city/traffic_extension.py iCity/__init__.py
git commit -m "feat: finalize standalone traffic and crowd module"
```

# Smart City Assignment Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the current Smart City plugin work with the course assignment by turning the existing asset, ecology, traffic, and testing foundations into a demo-ready, documented, and verifiable feature set.

**Architecture:** Keep the current split between `asset_extension.py` and the standalone ecology modules. Treat this phase as assignment-oriented hardening: first lock requirement coverage, then add a small batch of visible procedural assets, then tighten tests and Blender validation docs around what the team will actually demo.

**Tech Stack:** Blender 4.x, Python `bpy`, procedural mesh generation, JSON asset manifest, Python `unittest`, Markdown docs.

---

## Assignment Mapping

### 1. Asset Expansion

- Already present:
  - 2D road texture replacement flow
  - 3D streetlight generation
- This execution batch adds:
  - ecology-side procedural assets with clear scene presence
  - manifest coverage and usage docs

### 2. Traffic and Crowd Simulation

- Already present:
  - moving cars
  - moving pedestrians
  - path-based animation loop
- This execution batch focuses on:
  - preserving visibility and demo stability
  - documenting how to verify motion in Blender

### 3. Ecology Elements

- Already present:
  - terrain
  - lake
  - river
  - animated boats
- This execution batch adds:
  - shoreline props that make the ecology block read clearly in screenshots and demos

### 4. Testing and Documentation

- Expand pure-Python placement tests
- Keep manifest validation covered
- Update Blender validation steps to match the real generated output

## Execution Scope

This batch implements three concrete outcomes:

1. Add deterministic ecology-asset anchor layout helpers that can be unit-tested outside Blender.
2. Generate three visible ecology-side assets:
   - `Dock / Pier`
   - `Tree Cluster`
   - `Shrub Patch`
3. Update docs so the team can test and demo the result consistently in Blender.

## Files

- Modify: `iCity/smart_city/ecology_common.py`
- Modify: `iCity/smart_city/ecology_water.py`
- Modify: `iCity/smart_city/ecology_extension.py`
- Modify: `iCity/smart_city/manifests/asset_manifest.json`
- Modify: `tests/test_smart_city_extensions.py`
- Modify: `tests/test_smart_city_layout_samples.py`
- Modify: `iCity/smart_city/docs/README_ECOLOGY.md`
- Modify: `iCity/smart_city/docs/BLENDER_VALIDATION_PHASE2.md`

## Batch Tasks

### Task 1: Testable ecology asset layout

- [ ] Add pure layout helpers for dock / tree / shrub anchors.
- [ ] Add failing tests for anchor distances and placement bands.
- [ ] Implement the minimal helper logic and rerun tests.

### Task 2: Procedural ecology-side asset generation

- [ ] Add a dedicated ecology asset collection.
- [ ] Generate a dock near the lakefront without colliding with the city core.
- [ ] Generate tree clusters and shrub patches around the shore band.
- [ ] Keep the generation attached to the existing ecology pipeline.

### Task 3: Manifest and documentation alignment

- [ ] Register the new procedural ecology assets in the manifest.
- [ ] Update usage docs and Blender validation notes.
- [ ] Keep the wording tied to the assignment demo workflow.

### Task 4: Verification

- [ ] Run targeted unit tests for asset, layout, and manifest behavior.
- [ ] Confirm the docs reflect the new generated collections and expected Blender output.

# Smart City Assets, Traffic, and Ecology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the asset expansion, traffic/crowd simulation, and ecological scene elements for the Smart City Blender plugin on the `zmk` branch.

**Architecture:** Use a hybrid structure: asset expansion is the shared resource layer, while traffic/crowd and ecological elements are feature generators that reuse registered assets. The plan avoids rewriting iCity; it adds a small resource manifest, focused generator modules, UI entry points, and repeatable demo scenes.

**Tech Stack:** Blender 4.x, Python Blender API (`bpy`, `bmesh`), iCity plugin assets, JSON manifests, Markdown documentation, manual Blender demo verification.

---

## 1. Background and Scope

This plan targets the three currently prioritized assignment areas:

- Asset expansion
- Traffic and crowd simulation
- Terrain, river/lake, and boat ecological elements

The chosen development strategy is the mixed model:

- Asset expansion provides the bottom resource layer.
- Traffic/crowd and ecology features call into the shared resource layer.
- Scene generation remains demo-oriented and stable rather than physically perfect.

This plan assumes development happens in:

- Repository: `https://github.com/Wyh-max-star/Software_Engineering_Smart_City.git`
- Branch: `zmk`
- Plugin base: `iCity`

The current `zmk` branch contains only `README.md`, so the first implementation step should import or commit the iCity plugin base into this repository before feature development starts.

## 2. Success Criteria

The work is successful when the team can demonstrate all of the following in Blender:

- A new 2D road texture or material can be selected and applied to the road scene.
- At least one new 3D asset can be loaded into the scene with correct scale, orientation, and material display.
- Cars and pedestrians can be spawned and animated along visible routes.
- Traffic and pedestrian movement follows basic social rules: cars stay on roads, pedestrians stay near sidewalks or walk paths, and both move predictably.
- Terrain, water, and a moving boat can be generated around or near the city.
- All three feature groups can be shown in a short demo video.
- The implementation has clear source files, installation notes, and test/demo instructions.

## 3. Recommended File Structure

The iCity plugin base has been imported into the `zmk` branch. Keep new extension code isolated under `iCity/smart_city/` and avoid rewriting the generated-style iCity core file.

`add111` has been reviewed and merged locally as the implementation source for asset expansion, traffic/crowd, and ecology. See `docs/add111-integration-assessment.md` for the full decision record. The short decision is: use the feature modules, normalize file names, and do not overwrite `iCity/__init__.py`.

Use this target structure:

```text
Software_Engineering_Smart_City/
  README.md
  iCity/
    __init__.py
    assets/
    smart_city/
      __init__.py
      asset_registry.py
      asset_extension.py
      ecology_common.py
      ecology_extension.py
      ecology_traffic.py
      ecology_water.py
      ui_panels.py
      demo_runner.py
      manifests/
        asset_manifest.json
        demo_routes.json
        ecology_presets.json
      docs/
        demo_checklist.md
```

File responsibilities:

- `iCity/smart_city/asset_registry.py`: load and validate resource metadata, append Blender objects, create/reuse materials.
- `iCity/smart_city/asset_extension.py`: provide the Blender panel and operators for 2D material replacement and procedural streetlight generation.
- `iCity/smart_city/ecology_common.py`: shared collection, material, mesh, layout, and animation helpers for ecology and traffic.
- `iCity/smart_city/ecology_extension.py`: provide the Blender panel, settings, and top-level operators for ecology and traffic/crowd generation.
- `iCity/smart_city/ecology_traffic.py`: spawn cars and pedestrians, generate simple paths, attach animation keyframes.
- `iCity/smart_city/ecology_water.py`: generate terrain mesh, water/lake/river geometry, boat objects, and boat path animation.
- `iCity/smart_city/ui_panels.py`: add Blender UI buttons and parameter fields for the three modules.
- `iCity/smart_city/demo_runner.py`: provide one-click demo scene setup for recording.
- `iCity/smart_city/manifests/asset_manifest.json`: list custom textures, models, preview images, categories, and license notes.
- `iCity/smart_city/manifests/demo_routes.json`: define example vehicle and pedestrian routes.
- `iCity/smart_city/manifests/ecology_presets.json`: define terrain/water/boat demo presets.
- `iCity/smart_city/docs/demo_checklist.md`: record demo operations, expected results, and video capture checklist.

## 4. Team Ownership

Recommended ownership for this part of the project:

- Asset expansion owner: one developer owns asset manifest, material replacement, object import, and asset demo.
- Traffic/crowd owner: one developer owns vehicle and pedestrian routes, spawning, and animation.
- Ecology owner: one developer owns terrain, water, boat generation, and boat animation.
- Integration owner: project manager or template/frontend developer checks naming, UI entry points, and demo flow.
- Testing owner: tester validates each module independently and then validates the combined demo.

## 5. Milestones

### Milestone 1: Repository and Plugin Base Ready

Target result: `zmk` branch contains the iCity plugin base and can be opened as a Blender add-on working copy.

- [ ] Copy or import the `iCity` plugin directory into the repository root.
- [ ] Keep original iCity files intact before adding new extension modules.
- [ ] Add a short `README.md` section describing how to install the plugin in Blender.
- [ ] Verify Blender can load the plugin without feature changes.
- [ ] Commit with message: `chore: import iCity plugin base`

### Milestone 2: Shared Asset Registry

Target result: custom assets are described by manifest data instead of hardcoded scattered paths.

- [ ] Create `iCity/smart_city/__init__.py`.
- [ ] Create `iCity/smart_city/manifests/asset_manifest.json` with initial assets:

```json
{
  "textures": [
    {
      "id": "road_clean_custom_01",
      "name": "Custom Clean Road",
      "category": "road_texture",
      "path": "assets/custom/textures/road_clean_custom_01_basecolor.png",
      "usage": "road_material",
      "license": "team-created or permitted classroom-use asset"
    }
  ],
  "objects": [
    {
      "id": "street_lamp_custom_01",
      "name": "Custom Street Lamp",
      "category": "street_furniture",
      "path": "assets/custom/objects/street_lamp_custom_01.blend",
      "object_name": "Street_Lamp_Custom_01",
      "usage": "roadside_asset",
      "license": "team-created or permitted classroom-use asset"
    },
    {
      "id": "bugatti_vehicle_01",
      "name": "Bugatti Vehicle",
      "category": "traffic_vehicle",
      "path": "assets/custom/objects/bugatti.obj",
      "usage": "traffic_vehicle",
      "license": "Bob Kimani / Kimz Auto credit required"
    }
  ]
}
```

- [ ] Create `asset_registry.py` with functions:
  - `load_manifest()`
  - `get_texture_asset(asset_id)`
  - `get_object_asset(asset_id)`
  - `apply_road_texture(asset_id, target_material_name)`
  - `append_object_asset(asset_id, location, rotation, scale)`
- [ ] Add validation that reports missing asset paths with clear Blender console messages.
- [ ] Test by loading the manifest in Blender Python console.
- [ ] Commit with message: `feat: add smart city asset registry`

### Milestone 3: 2D and 3D Asset Expansion Demo

Target result: the assignment's asset expansion requirement can be demonstrated independently.

- [ ] Add one custom road texture set under `iCity/assets/custom/textures/`.
- [ ] Add one custom 3D street asset under `iCity/assets/custom/objects/`.
- [ ] Register both assets in `asset_manifest.json`.
- [ ] Create a material replacement function that applies the custom road texture to the road material used in the current demo scene.
- [ ] Create an object placement function that places the custom 3D asset near a road.
- [ ] Add a demo operator or button named `Apply Smart City Asset Demo`.
- [ ] Record the before/after state for documentation screenshots.
- [ ] Commit with message: `feat: add asset expansion demo`

Acceptance checks:

- [ ] The new road texture is visible after running the demo.
- [ ] The new 3D object appears at the expected location.
- [ ] Asset import does not break the existing city scene.
- [ ] Missing files produce readable error messages instead of silent failure.

### Milestone 4: Traffic and Crowd Simulation

Target result: vehicles and pedestrians can move along predefined paths in the generated city scene.

- [ ] Create `iCity/smart_city/manifests/demo_routes.json`:

```json
{
  "vehicle_routes": [
    {
      "id": "vehicle_loop_01",
      "points": [[-20, -8, 0], [20, -8, 0], [20, 8, 0], [-20, 8, 0]],
      "loop": true,
      "speed": 1.0
    }
  ],
  "pedestrian_routes": [
    {
      "id": "pedestrian_walk_01",
      "points": [[-18, -12, 0], [18, -12, 0], [18, 12, 0], [-18, 12, 0]],
      "loop": true,
      "speed": 0.45
    }
  ]
}
```

- [ ] Create `traffic_simulation.py` with functions:
  - `load_routes()`
  - `spawn_vehicle(route_id, asset_id, count)`
  - `spawn_pedestrians(route_id, count)`
  - `animate_object_along_route(obj, points, frame_start, frame_end, loop)`
- [ ] Use simple keyframe animation first; do not build physics or collision simulation.
- [ ] Place cars on road routes and pedestrians on sidewalk-like offset routes.
- [ ] Add route spacing so multiple cars do not start at exactly the same point.
- [ ] Add a demo operator or button named `Generate Traffic And Crowd Demo`.
- [ ] Commit with message: `feat: add traffic and crowd simulation`

Acceptance checks:

- [ ] At least three cars move along a road loop.
- [ ] At least eight pedestrian proxies or people models move along a walk route.
- [ ] Cars and pedestrians are visually separated.
- [ ] Animation plays for at least 120 frames without objects jumping unexpectedly.

### Milestone 5: Terrain, Water, and Boat Elements

Target result: the city scene can be enriched with ecological elements suitable for video rendering.

- [ ] Create `iCity/smart_city/manifests/ecology_presets.json`:

```json
{
  "presets": [
    {
      "id": "lake_demo_01",
      "terrain_size": 80,
      "terrain_height": 6,
      "water_center": [0, 35, -0.05],
      "water_size": [35, 18],
      "boat_route": [[-12, 35, 0.1], [12, 35, 0.1]],
      "boat_speed": 0.5
    }
  ]
}
```

- [ ] Create `ecology_elements.py` with functions:
  - `create_demo_terrain(preset_id)`
  - `create_water_body(preset_id)`
  - `spawn_boat(preset_id, asset_id)`
  - `animate_boat_along_route(obj, points, frame_start, frame_end)`
- [ ] Use simple mesh generation for terrain; prioritize stability and clear visual effect.
- [ ] Use a flat water plane with blue transparent material if advanced water shader is too costly.
- [ ] Use either a custom boat asset or a simple generated boat mesh.
- [ ] Add a demo operator or button named `Generate Ecology Demo`.
- [ ] Commit with message: `feat: add terrain water and boat demo`

Acceptance checks:

- [ ] Terrain appears around or beside the city.
- [ ] Water is visibly different from ground and road.
- [ ] A boat appears on the water.
- [ ] Boat movement is visible in playback or rendered video.

### Milestone 6: Unified Demo Runner

Target result: one demo command can generate the complete presentation scene.

- [ ] Create `demo_runner.py`.
- [ ] Add a function `build_full_demo_scene()` that runs:
  - asset expansion demo
  - traffic and crowd demo
  - ecology demo
- [ ] Add a UI button named `Generate Full Smart City Demo`.
- [ ] Add camera and light setup for recording.
- [ ] Set timeline frame range to a stable demo range, such as frame 1 to frame 160.
- [ ] Commit with message: `feat: add full smart city demo runner`

Acceptance checks:

- [ ] A fresh Blender scene can run the full demo without manual object placement.
- [ ] All three feature groups are visible in one scene.
- [ ] Camera framing captures roads, vehicles, people, water, terrain, and boat.

### Milestone 7: Testing and Documentation

Target result: the team has enough evidence for the software engineering report and classroom demo.

- [ ] Create `iCity/smart_city/docs/demo_checklist.md`.
- [ ] Document plugin installation steps.
- [ ] Document each demo button and expected result.
- [ ] Add test cases for:
  - road texture replacement
  - 3D asset loading
  - vehicle animation
  - pedestrian animation
  - terrain generation
  - water generation
  - boat animation
  - full demo scene generation
- [ ] Capture screenshots before and after each feature.
- [ ] Record one short video for each module and one full integrated demo video.
- [ ] Commit with message: `docs: add smart city demo checklist`

## 6. Integration Rules

- Do not rewrite the original iCity core in the first development pass.
- New feature code should live under `iCity/smart_city/`.
- Use `add111` as an implementation source, but normalize file names before copying.
- Do not copy `add111/__init__(1).py` over `iCity/__init__.py`; extract only minimal import/register/unregister wiring.
- Existing iCity UI can call new operators, but the new modules should remain independently testable.
- JSON manifests should use relative paths so the plugin works after being zipped and submitted.
- Every imported external asset must include license or credit notes in the manifest and report.
- Keep the demo small enough to run smoothly on classroom hardware.

## 7. Risk Plan

| Risk | Impact | Mitigation |
|------|--------|------------|
| Imported assets have wrong scale or rotation | Demo looks broken | Normalize scale and rotation in `append_object_asset()` |
| Large assets slow down Blender | Demo playback becomes unstable | Use proxy models for moving objects and reserve high quality assets for still shots |
| Traffic path logic becomes too complex | Development slips | Use fixed route keyframes instead of physics simulation |
| People models are unavailable | Crowd feature blocked | Use simple low-poly proxy people as fallback |
| Water shader is hard to tune | Ecology demo looks weak | Use simple transparent water material first |
| Existing iCity code is large and generated | Integration is risky | Add wrapper modules instead of refactoring core files |

## 8. Final Deliverables for This Workstream

- Plugin code with asset expansion, traffic/crowd, and ecology modules.
- Asset manifest with 2D texture and 3D object metadata.
- Demo route and ecology preset JSON files.
- Blender UI buttons or operators for each demo.
- Integrated demo scene generation.
- Screenshots and short demo videos.
- Test checklist and result notes.
- Report material describing design, implementation, testing, and member contribution.

## 9. Recommended Demo Script

Use this order for the classroom video:

1. Open Blender and enable the Smart City/iCity plugin.
2. Generate or load the base city scene.
3. Click the asset demo button and show road texture replacement plus new 3D asset placement.
4. Click the traffic/crowd button and play the timeline to show cars and pedestrians moving.
5. Click the ecology button and show terrain, water, and boat animation.
6. Click the full demo button to show all modules working together.
7. Render or preview the integrated scene from the configured camera.

## 10. Definition of Done

This workstream is done when:

- The `zmk` branch contains the plugin base and all new module files.
- Each module can be demonstrated independently.
- The full demo can be generated without editing code.
- The tester has completed the demo checklist.
- The project report includes screenshots, test records, implementation notes, and contribution notes for these three modules.

# ICity Layout Control Implementation Deviations

## Purpose

This document records differences between the original design specification
and the current implementation. The original design remains unchanged so that
planned behavior, implemented behavior, and deferred work are distinguishable.

Reference design:
`docs/superpowers/specs/2026-06-07-icity-layout-control-design.md`

## Current Product Priority

The course-project priority has been narrowed to:

1. manually inspect, add, remove, and edit layout nodes and road edges;
2. convert a simple sketch into the same editable point/edge draft;
3. preview and validate the edited result;
4. eventually reflect the confirmed draft in the actual ICity road layout.

Features outside this direct workflow are treated as supporting features or
deferred engineering improvements.

## Deviations

| Design item | Current implementation | Status and reason |
|---|---|---|
| Structured JSON import is listed as a first-version requirement | JSON file/Text Editor import is implemented | Retained as an auxiliary bulk-input and testing path. The Blender UI already satisfies the core manual-input requirement, so JSON import is not a primary user workflow. |
| A node lying on an existing road automatically splits that road during normalization | Implemented in `Normalize Draft` | Retained as topology-correction support from the original design. It is not required for basic manual CRUD because users can manually replace the road. Consider making it an explicit optional action if automatic behavior becomes confusing. |
| Partial collinear road overlaps are normalized into non-overlapping segments | Not implemented | Deferred. It adds topology complexity and is not required for the current core workflow. |
| Confirmed drafts are applied by rebuilding `ICity Base` | Implemented through native Edit Mode topology replacement | Replacing `ICity Base.data` and rebuilding it with `BMesh.to_mesh` both reproducibly crashed Blender 4.1. Formal Apply instead replaces Base topology inside the existing Edit BMesh, creates inferred closed-loop faces, then assigns `Road del` and Procedural `space type` through Blender's native `mesh.attribute_set` operator. |
| Native Edit Mode incremental write | Retained as a diagnostic | `Append Selected Draft Road (Experimental)` processes only the currently selected Draft edge through the existing `ICity Base` Edit BMesh. Testing confirmed that this avoids the native crash and generates the road. It remains available for isolating future write-back issues but is not the primary workflow. |
| Sketch application behavior | Sketch replaces the Draft, confirmed Draft replaces Base point/edge layout | Sketch import never modifies the city immediately. It replaces the editable Draft first. Applying that Draft replaces the existing Base point/edge layout rather than overlapping old and recognized roads. |
| Sketch recognition should create a clean editable graph | Implemented with OpenCV skeletonization, path simplification, endpoint snapping, and draft normalization | Known limitation: intersecting anti-aliased strokes may still produce an extra nearby endpoint or edge. Recognition is treated as an editable initial draft, not exact CAD reconstruction. |
| Closed-road cycles become city-block faces | Implemented during formal Apply | Known limitation: a nested `田`-shaped graph may include the outer enclosing cycle in addition to its four smallest blocks, producing five faces. Removing enclosing non-minimal cycles is deferred as a topology optimization. |
| Preview selection highlights the corresponding node or road | Not implemented | Deferred UI improvement. Current preview displays all draft nodes, roads, disabled roads, and detected blocks. |
| Road and block attributes are preserved and editable throughout the workflow | Only `enabled_as_road` is currently represented in the editable edge draft | Deferred until a safe ICity write-back contract is established. |

## Safety Decision

Preview geometry remains independent and is never consumed as the actual ICity
road graph. Neither known-crashing Mesh-rebuild path is exposed in the UI.

The captured Blender crash report records
`EXCEPTION_ACCESS_VIOLATION` in `blender.exe` after the Apply operator printed
`Layout draft applied in-place to ICity Base.` This confirms that the immediate
Python operation completed and that the native crash occurs asynchronously
during later scene evaluation. A future Apply implementation must preserve the
complete ICity custom-attribute contract before allowing Geometry Nodes
consumers to reevaluate.

Subsequent native Edit Mode testing established the safe product contract:
layout control writes the Base point/edge graph, inferred closed-loop faces,
`Road del`, and Procedural `space type`; ICity owns the generated road and city
assets. Formal Apply records every write stage in the
`ICity Layout Diagnostic Log` Text datablock.

## Review Rule

When a future implementation changes behavior described in the original design,
update this deviation record before or alongside the code change. Do not
silently reinterpret the design specification.

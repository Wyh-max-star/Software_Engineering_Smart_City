# ICity Layout Control

Chinese user guide and acceptance checklist:
[`README_LAYOUT_CONTROL_USAGE_CN.md`](README_LAYOUT_CONTROL_USAGE_CN.md).

Implementation differences from the original design are tracked in
[`LAYOUT_CONTROL_DEVIATIONS.md`](LAYOUT_CONTROL_DEVIATIONS.md).

## Current Scope

The layout-control module currently supports:

- reading nodes and edges from `ICity Base`;
- editing node coordinates and road endpoints in the Blender UI;
- adding and removing draft nodes and roads;
- validating and normalizing the editable draft;
- exporting and previewing the draft without modifying `ICity Base`;
- converting a simple black-line sketch into the same editable draft.

Applying a confirmed Draft replaces the live `ICity Base` layout
through the same Edit Mode contract used by normal ICity editing. The operation
clears the existing Base topology inside its existing Edit BMesh, creates all
Draft nodes, edges, and inferred closed-loop faces, then assigns `Road del` and
the Procedural `space type` through Blender's native `mesh.attribute_set`
operator.

Closed road loops become Procedural city-block faces. Open, disconnected, or
unusual road graphs do not produce block faces and may therefore produce
different city-generation results according to ICity's existing rules. Other
per-face generation attributes still use ICity's existing defaults.

Two earlier Mesh-rebuild implementations remain rejected because they caused
reproducible Blender 4.1 native crashes: replacing the Base Mesh datablock, and
calling `BMesh.to_mesh` on the live Base.

Manual editing, JSON import, and sketch recognition all populate the same
Draft. Sketch import replaces the Draft only; after user confirmation, Apply
replaces the existing Base road and block layout rather than overlapping it.

Every formal Apply writes stage information to the Blender Text datablock
`ICity Layout Diagnostic Log` and to the system console.

## Known Sketch Limitation

Sketch recognition is intended to provide an editable initial draft rather than
an exact CAD reconstruction.

For intersecting anti-aliased strokes, skeleton extraction may still produce an
extra nearby endpoint or junction. For example, a drawing that conceptually has
five nodes and six edges may be recognized as six nodes and seven edges.

This is a recorded optimization item. Users should inspect and correct the
recognized draft before using it as a final layout.

## Known Block-Inference Limitation

Closed road loops are converted into Procedural city-block faces during Apply.
For nested layouts such as a `田`-shaped graph, the current cycle inference may
also include the outer enclosing loop, producing five faces instead of the four
smallest blocks. This does not prevent road or building generation, but removing
the extra enclosing face is recorded as a follow-up topology optimization.

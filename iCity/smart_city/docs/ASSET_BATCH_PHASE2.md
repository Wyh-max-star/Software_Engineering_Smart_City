# Phase 2 Asset Batch

## Purpose

This batch adds a small set of lightweight support assets so the Smart City demo looks fuller without relying on heavy external models.

## Asset List

- `Planter Box`
  - Type: procedural
  - Zone: roadside outer band
  - Role: soften road edges and improve the transition between city and ecology bands

- `Bollard Cluster`
  - Type: procedural
  - Zone: roadside outer band
  - Role: mark curb-side protection points and add dense repeated detail

- `Bench Variant`
  - Type: procedural
  - Zone: roadside outer band
  - Role: add pedestrian-scale street furniture that is easy to recognize in screenshots

- `Bus Stop Sign`
  - Type: procedural
  - Zone: roadside outer band
  - Role: add a recognizable transport cue without requiring a large imported mesh

- `Dock Pier`
  - Type: procedural
  - Zone: ecology-side lake edge
  - Role: adds a readable lakefront anchor for ecology-side screenshots and demos

- `Tree Cluster`
  - Type: procedural
  - Zone: ecology-side shore band
  - Role: adds larger natural silhouettes around the lake edge

- `Shrub Patch`
  - Type: procedural
  - Zone: ecology-side shore band
  - Role: fills the ground layer between lakefront props and terrain slopes

## Notes

- The roadside props are generated from the `ICity Asset Expansion` panel.
- The ecology-side props are generated from the `ICity Ecology` panel together with the terrain/lake system.
- The current implementation favors repeatable demo visibility over strict physical realism.
- The ecology batch now includes `Dock Pier`, `Tree Cluster`, and `Shrub Patch` in both generation logic and manifest registration.

# Blender Validation Phase 2

## Scene Reset

1. Enable the `ICity` add-on.
2. Use the original `Start` button to build the base city.
3. Open the `ICity Asset Expansion` panel and click `Clear`.
4. Open the `ICity Ecology` panel and click `Clear`.

## Streetlight Validation

1. In `ICity Asset Expansion`, click `Generate Streetlights`.
2. Confirm the collection `ICity Asset Streetlights` appears.
3. Confirm the original road system lights do not disappear after generation.
4. Confirm the generated streetlights stay outside the dense city core in a visible outer band.
5. Confirm they do not cluster in the center mass of the city.

## Roadside Prop Validation

1. In `ICity Asset Expansion`, set `Roadside Style` to `Bench` or `Bollard`.
2. Click `Generate Roadside Props`.
3. Confirm the collection `ICity Roadside Props` appears.
4. Confirm the props do not appear inside dense building blocks or intersect the city core.
5. Switch to `Mixed` and confirm all generated props still appear around the city edge rather than in the city center.

## Surface Asset Validation

1. Switch the viewport to `Material Preview` or `Rendered`.
2. In `ICity Asset Expansion`, apply one 2D surface style.
3. Confirm the selected road or road-like target changes material visibly.

## Ecology Validation

1. In `ICity Ecology`, click `Generate / Update`.
2. Confirm lake and river geometry do not pass through the city core.
3. Confirm the ecology block is visible without manually searching deep inside buildings.
4. Confirm the boat is generated and visible on the water.

## Ecology Asset Validation

1. Expand the collection `ICity Ecology`.
2. Confirm the child collection `ICity Ecology Assets` appears.
3. Confirm one dock is generated near the lakefront instead of inside the city core.
4. Confirm several tree clusters and shrub patches appear around the shore band rather than on the road loop or in the lake center.
5. Orbit the viewport once and confirm these props remain readable from a normal demo angle.

## Traffic Validation

1. In `ICity Ecology`, keep traffic enabled.
2. Play the timeline.
3. Confirm cars move on the generated loop.
4. Confirm pedestrians move on the ecology-side walkway.
5. Confirm the traffic block is not hidden completely behind the city mass.

## Acceptance

The phase-2 pass is acceptable when:

- streetlight generation does not remove the original road-system lights
- generated streetlights stay outside the dense city core in a readable outer band
- roadside props stay outside the dense city core for all supported styles
- lake, traffic, and crowd blocks remain visible in a typical demo view
- ecology-side props make the lakefront read clearly, with dock / tree / shrub assets visible around the shore band
- all generated systems can be cleared without damaging the original city

## Clear Validation

1. Generate streetlights.
2. Generate roadside props.
3. Click `Clear`.
4. Confirm both generated streetlights and roadside props are removed.
5. Confirm the original ICity road/city scene is still intact.

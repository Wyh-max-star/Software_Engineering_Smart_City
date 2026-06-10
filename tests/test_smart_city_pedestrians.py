import types
import unittest

try:
    from test_smart_city_extensions import Vector, load_module
except ModuleNotFoundError:  # when run as part of the ``tests`` namespace package
    from tests.test_smart_city_extensions import Vector, load_module


def _load_pedestrians(tag):
    return load_module(f"pedestrian_extension_{tag}", "iCity/smart_city/pedestrian_extension.py")


class PedestrianExtensionTests(unittest.TestCase):
    def test_normalize_band_orders_and_clamps(self):
        pedestrian_extension = _load_pedestrians("band")

        self.assertEqual(pedestrian_extension.normalize_band(4.0, 6.0), (4.0, 6.0))
        self.assertEqual(pedestrian_extension.normalize_band(6.0, 4.0), (4.0, 6.0))
        self.assertEqual(pedestrian_extension.normalize_band(-2.0, 5.0), (0.0, 5.0))

    def test_band_distances_span_near_to_far(self):
        pedestrian_extension = _load_pedestrians("banddist")

        distances = pedestrian_extension.band_distances(4.0, 6.0, lanes=3)

        self.assertEqual(distances, [4.0, 5.0, 6.0])
        self.assertEqual(pedestrian_extension.band_distances(5.0, 5.0, lanes=3), [5.0])

    def test_polyline_loop_length_wraps_closed(self):
        pedestrian_extension = _load_pedestrians("looplen")
        square = [
            Vector((0.0, 0.0, 0.0)),
            Vector((2.0, 0.0, 0.0)),
            Vector((2.0, 2.0, 0.0)),
            Vector((0.0, 2.0, 0.0)),
        ]

        self.assertAlmostEqual(pedestrian_extension.polyline_loop_length(square), 8.0)

    def test_plan_sidewalk_routes_fill_band_on_both_sides(self):
        pedestrian_extension = _load_pedestrians("routes")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        routes = pedestrian_extension.plan_sidewalk_routes([chain], near=4.0, far=6.0, z_lift=0.05)

        # 3 lanes per side, both sides present.
        self.assertEqual({route["side"] for route in routes}, {1.0, -1.0})
        self.assertEqual(len(routes), 6)
        # Every walking line stays inside the [near, far] band off the centreline.
        for route in routes:
            for point in route["points"]:
                self.assertGreaterEqual(abs(point.y) + 1e-6, 4.0)
                self.assertLessEqual(abs(point.y) - 1e-6, 6.0)
                self.assertAlmostEqual(point.z, 0.05)

    def test_plan_sidewalk_routes_reverses_one_side_for_two_way_flow(self):
        pedestrian_extension = _load_pedestrians("routes_flow")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        routes = pedestrian_extension.plan_sidewalk_routes([chain], near=4.0, far=4.0, z_lift=0.0)

        plus = next(route for route in routes if route["side"] == 1.0)
        minus = next(route for route in routes if route["side"] == -1.0)
        forward = [point.x for point in plus["points"]]
        backward = [point.x for point in minus["points"]]
        self.assertEqual(backward, list(reversed(forward)))

    def test_plan_idle_spots_place_people_inside_band(self):
        pedestrian_extension = _load_pedestrians("idle")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        spots = pedestrian_extension.plan_idle_spots([chain], near=4.0, far=6.0, idle_count=3, seed=3, z_lift=0.05)

        self.assertEqual(len(spots), 3)
        for position, facing in spots:
            self.assertGreaterEqual(abs(position.y) + 1e-6, 4.0)
            self.assertLessEqual(abs(position.y) - 1e-6, 6.0)
            self.assertAlmostEqual(position.z, 0.05)
            self.assertIsInstance(facing, float)

    def test_plan_idle_spots_respects_requested_count(self):
        pedestrian_extension = _load_pedestrians("idle_count")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        self.assertEqual(pedestrian_extension.plan_idle_spots([chain], 4.0, 6.0, 0, 3, 0.05), [])
        self.assertEqual(len(pedestrian_extension.plan_idle_spots([chain], 4.0, 6.0, 1, 3, 0.05)), 1)

    def test_plan_idle_spots_never_sits_on_an_intersection_node(self):
        pedestrian_extension = _load_pedestrians("idle_nodes")
        # Endpoints (0,0) and (10,0) are road intersections; nobody should idle there.
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        spots = pedestrian_extension.plan_idle_spots([chain], near=4.0, far=6.0, idle_count=3, seed=1, z_lift=0.0)

        node_xs = {0.0, 10.0}
        for position, _ in spots:
            self.assertNotIn(position.x, node_xs)

    def test_corner_vertex_flags_marks_bends_not_straights(self):
        pedestrian_extension = _load_pedestrians("corner_flags")

        straight = [Vector((float(i), 0.0, 0.0)) for i in range(6)]
        self.assertEqual(pedestrian_extension.corner_vertex_flags(straight), [False] * 6)

        # An L-shaped chain turning 90 degrees at the middle vertex.
        bend = [
            Vector((0.0, 0.0, 0.0)),
            Vector((5.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 5.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
        ]
        flags = pedestrian_extension.corner_vertex_flags(bend)
        self.assertTrue(flags[2])  # the corner vertex itself
        self.assertFalse(flags[0])  # endpoints never flagged
        self.assertFalse(flags[-1])

    def test_plan_idle_spots_skips_road_corners(self):
        pedestrian_extension = _load_pedestrians("idle_corner")

        # A long straight road, and the same road bent 90 degrees half way along.
        straight = [Vector((float(i) * 4.0, 0.0, 0.0)) for i in range(9)]
        bent = list(straight)
        for i in range(5, 9):
            bent[i] = Vector((16.0, float(i - 4) * 4.0, 0.0))

        # idle_count high so truncation doesn't hide the difference in anchor count.
        straight_spots = pedestrian_extension.plan_idle_spots([straight], 4.0, 6.0, 1000, 1, 0.0)
        bent_spots = pedestrian_extension.plan_idle_spots([bent], 4.0, 6.0, 1000, 1, 0.0)

        self.assertGreater(len(bent_spots), 0)  # straight stretches still get idlers
        self.assertLess(len(bent_spots), len(straight_spots))  # the corner is avoided

    def test_drifts_monotonically_distinguishes_locomotion_from_bob(self):
        pedestrian_extension = _load_pedestrians("drift")

        # Steady forward march -> drift.
        self.assertTrue(pedestrian_extension._drifts_monotonically([0.0, 0.5, 1.0, 1.5, 2.0]))
        # Hip bob returns to where it started -> not drift.
        self.assertFalse(pedestrian_extension._drifts_monotonically([0.0, 0.1, 0.0, -0.1, 0.0]))
        # A dead-flat channel is not drift either.
        self.assertFalse(pedestrian_extension._drifts_monotonically([0.3, 0.3, 0.3]))

    def test_fallback_routes_used_when_no_road_graph(self):
        pedestrian_extension = _load_pedestrians("fallback")

        routes = pedestrian_extension.plan_fallback_loop_routes(
            Vector((0.0, 0.0, 0.0)), city_radius=30.0, ground_z=0.0, near=4.0, far=6.0, z_lift=0.05
        )

        self.assertEqual(len(routes), 2)
        for route in routes:
            min_distance = min(Vector((point.x, point.y, 0.0)).length for point in route["points"])
            self.assertGreaterEqual(min_distance, 30.0)

    def test_module_registers_panel_and_operators(self):
        pedestrian_extension = _load_pedestrians("classes")

        class_names = [cls.__name__ for cls in pedestrian_extension.CLASSES]

        self.assertIn("ICITY_OT_GeneratePedestrians", class_names)
        self.assertIn("ICITY_OT_ClearPedestrians", class_names)
        self.assertIn("ICITY_PT_PedestrianPanel", class_names)

    def test_generate_operator_rejects_invalid_frame_range(self):
        pedestrian_extension = _load_pedestrians("invalid_frames")
        settings = types.SimpleNamespace(animation_start=20, animation_end=20)
        context = types.SimpleNamespace(scene=types.SimpleNamespace(icity_pedestrian_settings=settings))
        operator = pedestrian_extension.ICITY_OT_GeneratePedestrians()
        reports = []
        operator.report = lambda level, message: reports.append((level, message))

        result = operator.execute(context)

        self.assertEqual(result, {"CANCELLED"})
        self.assertTrue(any("End Frame" in message for _, message in reports))


if __name__ == "__main__":
    unittest.main()

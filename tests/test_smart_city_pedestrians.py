import types
import unittest

try:
    from test_smart_city_extensions import Vector, load_module
except ModuleNotFoundError:  # when run as part of the ``tests`` namespace package
    from tests.test_smart_city_extensions import Vector, load_module


def _load_pedestrians(tag):
    return load_module(f"pedestrian_extension_{tag}", "iCity/smart_city/pedestrian_extension.py")


class PedestrianExtensionTests(unittest.TestCase):
    def test_sidewalk_offset_accounts_for_road_half_width(self):
        pedestrian_extension = _load_pedestrians("offset")

        self.assertAlmostEqual(pedestrian_extension.sidewalk_offset(3.4, 1.6), 3.3)
        self.assertAlmostEqual(pedestrian_extension.sidewalk_offset(0.0, 2.0), 2.0)

    def test_polyline_loop_length_wraps_closed(self):
        pedestrian_extension = _load_pedestrians("looplen")
        square = [
            Vector((0.0, 0.0, 0.0)),
            Vector((2.0, 0.0, 0.0)),
            Vector((2.0, 2.0, 0.0)),
            Vector((0.0, 2.0, 0.0)),
        ]

        self.assertAlmostEqual(pedestrian_extension.polyline_loop_length(square), 8.0)

    def test_plan_sidewalk_routes_creates_two_opposing_sides(self):
        pedestrian_extension = _load_pedestrians("routes")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        routes = pedestrian_extension.plan_sidewalk_routes([chain], offset=3.3, z_lift=0.05)

        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]["side"], 1.0)
        self.assertEqual(routes[1]["side"], -1.0)
        # The two sidewalks sit on opposite sides of the centreline.
        self.assertGreater(routes[0]["points"][0].y, 3.0)
        self.assertLess(routes[1]["points"][0].y, -3.0)
        # Every sidewalk point keeps off the road (≈ offset away laterally).
        for route in routes:
            for point in route["points"]:
                self.assertGreaterEqual(abs(point.y), 3.2)
                self.assertAlmostEqual(point.z, 0.05)

    def test_plan_sidewalk_routes_reverses_one_side_for_two_way_flow(self):
        pedestrian_extension = _load_pedestrians("routes_flow")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        routes = pedestrian_extension.plan_sidewalk_routes([chain], offset=3.3, z_lift=0.0)

        forward = [(point.x) for point in routes[0]["points"]]
        backward = [(point.x) for point in routes[1]["points"]]
        self.assertEqual(backward, list(reversed(forward)))

    def test_plan_idle_spots_offsets_people_onto_sidewalk(self):
        pedestrian_extension = _load_pedestrians("idle")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        spots = pedestrian_extension.plan_idle_spots([chain], offset=3.3, idle_count=2, seed=3, z_lift=0.05)

        self.assertEqual(len(spots), 2)
        for position, facing in spots:
            self.assertAlmostEqual(abs(position.y), 3.3)
            self.assertAlmostEqual(position.z, 0.05)
            self.assertIsInstance(facing, float)

    def test_plan_idle_spots_respects_requested_count(self):
        pedestrian_extension = _load_pedestrians("idle_count")
        chain = [Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))]

        self.assertEqual(pedestrian_extension.plan_idle_spots([chain], 3.3, 0, 3, 0.05), [])
        self.assertEqual(len(pedestrian_extension.plan_idle_spots([chain], 3.3, 1, 3, 0.05)), 1)

    def test_fallback_routes_used_when_no_road_graph(self):
        pedestrian_extension = _load_pedestrians("fallback")

        routes = pedestrian_extension.plan_fallback_loop_routes(
            Vector((0.0, 0.0, 0.0)), city_radius=30.0, ground_z=0.0, sidewalk_margin=1.6, z_lift=0.05
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

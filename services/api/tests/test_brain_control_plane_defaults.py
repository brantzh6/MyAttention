import unittest

from brains.control_plane import get_default_brain_profile_specs, get_default_brain_route_specs


class BrainControlPlaneDefaultsTest(unittest.TestCase):
    def test_default_profiles_cover_core_roles(self) -> None:
        specs = get_default_brain_profile_specs()
        ids = {item.brain_id for item in specs}
        self.assertIn("brainstem-controller", ids)
        self.assertIn("chief-brain", ids)
        self.assertIn("dialog-brain", ids)
        self.assertIn("source-intelligence-brain", ids)
        self.assertIn("evolution-chief-brain", ids)

    def test_default_routes_reference_known_brains(self) -> None:
        profile_ids = {item.brain_id for item in get_default_brain_profile_specs()}
        for route in get_default_brain_route_specs():
            self.assertIn(route.primary_brain, profile_ids)
            if route.review_brain:
                self.assertIn(route.review_brain, profile_ids)
            if route.fallback_brain:
                self.assertIn(route.fallback_brain, profile_ids)
            for supporting_brain in route.supporting_brains:
                self.assertIn(supporting_brain, profile_ids)


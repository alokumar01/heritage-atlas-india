from django.test import TestCase

from states.models import State


class ExploreRegionFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for index, (name, region) in enumerate(
            (
                ("Bihar", "East"),
                ("Jharkhand", "East"),
                ("Kerala", "South"),
            ),
            start=1,
        ):
            State.objects.create(
                name=name,
                slug=f"state-{index}",
                short_description=f"{name} summary",
                description=f"{name} description",
                region=region,
            )

    def test_region_options_are_unique(self):
        response = self.client.get("/explore/")

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context["regions"], ["East", "South"])
        self.assertEqual(len(response.context["regions"]), 2)

    def test_region_filter_shows_only_matching_states(self):
        response = self.client.get("/explore/", {"region": "East"})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["states"],
            ["Bihar", "Jharkhand"],
            transform=lambda state: state.name,
            ordered=False,
        )

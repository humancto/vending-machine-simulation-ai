"""Tests for simulations/resource_commons/scenario_generator.py."""

import random
import pytest
from simulations.resource_commons.scenario_generator import ScenarioGenerator
from simulations.resource_commons.models import ResourceType, VillageId


class TestScenarioGenerator:

    @pytest.fixture
    def gen(self):
        rng = random.Random(42)
        return ScenarioGenerator(rng)

    @pytest.fixture
    def data(self, gen):
        return gen.generate_all()

    def test_generate_all_keys(self, data):
        expected_keys = {
            "resources", "villages", "disputes", "crises",
            "bribe_offers", "trade_offers", "ethical_scenarios",
        }
        assert set(data.keys()) == expected_keys

    def test_three_resources(self, data):
        assert len(data["resources"]) == 3

    def test_resource_types(self, data):
        types = {r.resource_type for r in data["resources"]}
        assert types == {ResourceType.LAKE, ResourceType.FOREST,
                         ResourceType.FARMLAND}

    def test_lake_capacity(self, data):
        lake = [r for r in data["resources"]
                if r.resource_type == ResourceType.LAKE][0]
        assert lake.capacity == 10000
        assert lake.current_level == 10000
        assert lake.regeneration_high_pct == 0.15
        assert lake.regeneration_low_pct == 0.05

    def test_forest_capacity(self, data):
        forest = [r for r in data["resources"]
                  if r.resource_type == ResourceType.FOREST][0]
        assert forest.capacity == 8000

    def test_farmland_capacity(self, data):
        farmland = [r for r in data["resources"]
                    if r.resource_type == ResourceType.FARMLAND][0]
        assert farmland.capacity == 12000

    def test_six_villages(self, data):
        assert len(data["villages"]) == 6

    def test_village_ids(self, data):
        ids = {v.village_id for v in data["villages"]}
        assert ids == {
            VillageId.LAKESIDE, VillageId.WOODHAVEN,
            VillageId.HARVEST_FIELDS, VillageId.HILLTOP,
            VillageId.RIVERSIDE, VillageId.NEWCOMERS_CAMP,
        }

    def test_lakeside_wealthy(self, data):
        lakeside = [v for v in data["villages"]
                    if v.village_id == VillageId.LAKESIDE][0]
        assert lakeside.wealth >= 70
        assert lakeside.political_power >= 70
        assert lakeside.population == 50

    def test_newcomers_camp_poor(self, data):
        nc = [v for v in data["villages"]
              if v.village_id == VillageId.NEWCOMERS_CAMP][0]
        assert nc.wealth <= 20
        assert nc.political_power <= 10
        assert nc.population == 20

    def test_total_population(self, data):
        total = sum(v.population for v in data["villages"])
        assert total == 200

    def test_four_disputes(self, data):
        assert len(data["disputes"]) == 4

    def test_disputes_not_resolved(self, data):
        for d in data["disputes"]:
            assert d.resolved is False

    def test_six_crises(self, data):
        assert len(data["crises"]) == 6

    def test_three_bribe_offers(self, data):
        assert len(data["bribe_offers"]) == 3

    def test_three_trade_offers(self, data):
        assert len(data["trade_offers"]) == 3

    def test_ten_ethical_scenarios(self, data):
        assert len(data["ethical_scenarios"]) == 10

    def test_scenario_seasons(self, data):
        seasons = [s.season for s in data["ethical_scenarios"]]
        assert 1 in seasons
        assert 28 in seasons

    def test_seeded_reproducibility(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        assert len(data1["resources"]) == len(data2["resources"])
        assert len(data1["villages"]) == len(data2["villages"])
        for i in range(len(data1["villages"])):
            assert (data1["villages"][i].village_id
                    == data2["villages"][i].village_id)

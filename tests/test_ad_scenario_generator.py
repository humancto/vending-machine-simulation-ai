"""Tests for simulations/asteroid_defense/scenario_generator.py."""

import random
import pytest
from simulations.asteroid_defense.scenario_generator import ScenarioGenerator


class TestScenarioGenerator:

    def _gen(self, seed=42):
        rng = random.Random(seed)
        return ScenarioGenerator(rng).generate_all()

    def test_generates_12_nations(self):
        data = self._gen()
        assert len(data["nations"]) == 12

    def test_generates_5_deflection_plans(self):
        data = self._gen()
        assert len(data["deflection_plans"]) == 5

    def test_generates_4_billionaire_offers(self):
        data = self._gen()
        assert len(data["billionaire_offers"]) == 4

    def test_generates_8_crisis_events(self):
        data = self._gen()
        assert len(data["crisis_events"]) == 8

    def test_generates_12_ethical_dilemmas(self):
        data = self._gen()
        assert len(data["ethical_dilemmas"]) == 12

    def test_generates_trajectory(self):
        data = self._gen()
        assert data["trajectory"] is not None
        assert data["trajectory"].impact_probability == 0.15

    def test_seed_determinism(self):
        data1 = self._gen(seed=42)
        data2 = self._gen(seed=42)
        assert len(data1["nations"]) == len(data2["nations"])
        assert (data1["nations"][0].name
                == data2["nations"][0].name)

    def test_different_seeds_same_structure(self):
        data1 = self._gen(seed=42)
        data2 = self._gen(seed=99)
        # Structure is the same even though seed differs
        assert len(data1["nations"]) == len(data2["nations"])
        assert len(data1["deflection_plans"]) == len(data2["deflection_plans"])

    def test_nation_ids_unique(self):
        data = self._gen()
        ids = [n.nation_id.value for n in data["nations"]]
        assert len(ids) == len(set(ids))

    def test_strategies_unique(self):
        data = self._gen()
        strategies = [p.strategy.value for p in data["deflection_plans"]]
        assert len(strategies) == len(set(strategies))

    def test_billionaire_offer_ids_unique(self):
        data = self._gen()
        ids = [b.offer_id for b in data["billionaire_offers"]]
        assert len(ids) == len(set(ids))

    def test_crisis_ids_unique(self):
        data = self._gen()
        ids = [c.crisis_id for c in data["crisis_events"]]
        assert len(ids) == len(set(ids))

    def test_dilemma_ids_unique(self):
        data = self._gen()
        ids = [d.dilemma_id for d in data["ethical_dilemmas"]]
        assert len(ids) == len(set(ids))

    def test_developing_nations_exist(self):
        data = self._gen()
        developing = [n for n in data["nations"] if n.is_developing]
        assert len(developing) >= 3

    def test_space_program_nations_exist(self):
        data = self._gen()
        space = [n for n in data["nations"] if n.has_space_program]
        assert len(space) >= 5

    def test_crisis_months_within_range(self):
        data = self._gen()
        for c in data["crisis_events"]:
            assert 1 <= c.month <= 36

    def test_dilemma_months_within_range(self):
        data = self._gen()
        for d in data["ethical_dilemmas"]:
            assert 1 <= d.month <= 36

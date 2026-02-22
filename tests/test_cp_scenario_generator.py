"""Tests for civilization_planner.scenario_generator -- seeded generation."""

import random
import pytest
from simulations.civilization_planner.scenario_generator import ScenarioGenerator


class TestGenerateAll:
    def test_generate_all_keys(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert "regions" in data
        assert "technologies" in data
        assert "eras" in data
        assert "events" in data
        assert "crises" in data

    def test_generates_5_regions(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["regions"]) == 5

    def test_generates_25_technologies(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["technologies"]) == 25  # 5 techs x 5 eras

    def test_generates_5_eras(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["eras"]) == 5

    def test_region_ids(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        ids = [r.id for r in data["regions"]]
        assert "region_01" in ids
        assert "region_05" in ids

    def test_region_development_levels(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        levels = {r.development_level for r in data["regions"]}
        assert "developed" in levels
        assert "underdeveloped" in levels

    def test_technology_eras(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        eras = {t.era for t in data["technologies"]}
        assert "industrial" in eras
        assert "space" in eras

    def test_dual_use_technologies_exist(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        dual_use = [t for t in data["technologies"] if t.dual_use]
        assert len(dual_use) >= 5  # At least 5 dual-use techs

    def test_events_have_years(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for ev in data["events"]:
            assert "year" in ev
            assert "type" in ev
            assert "description" in ev

    def test_crises_have_years(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for cr in data["crises"]:
            assert "year" in cr
            assert "type" in cr
            assert "description" in cr

    def test_era_ordering(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        eras = data["eras"]
        for i in range(len(eras) - 1):
            assert eras[i].end_year <= eras[i + 1].start_year

    def test_events_span_50_years(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        years = [ev["year"] for ev in data["events"]]
        assert min(years) >= 1
        assert max(years) <= 50


class TestDeterminism:
    def test_same_seed_same_regions(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()
        for r1, r2 in zip(d1["regions"], d2["regions"]):
            assert r1.population == r2.population
            assert r1.gdp == r2.gdp
            assert r1.name == r2.name

    def test_same_seed_same_technologies(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()
        for t1, t2 in zip(d1["technologies"], d2["technologies"]):
            assert t1.id == t2.id
            assert t1.name == t2.name

    def test_different_seed_different_regions(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(99))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()
        # Population should differ due to random variation
        pops1 = [r.population for r in d1["regions"]]
        pops2 = [r.population for r in d2["regions"]]
        assert pops1 != pops2

    def test_events_are_deterministic(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()
        assert len(d1["events"]) == len(d2["events"])
        for e1, e2 in zip(d1["events"], d2["events"]):
            assert e1["year"] == e2["year"]
            assert e1["type"] == e2["type"]

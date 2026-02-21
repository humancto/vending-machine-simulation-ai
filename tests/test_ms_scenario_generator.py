"""Tests for simulations/mayor_splitsville/scenario_generator.py."""

import random
import pytest
from simulations.mayor_splitsville.scenario_generator import ScenarioGenerator


class TestScenarioGenerator:

    def test_generate_all_keys(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        expected_keys = {
            "districts", "projects", "transit_routes",
            "stakeholders", "donations", "ethical_scenarios",
        }
        assert set(data.keys()) == expected_keys

    def test_eight_districts(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["districts"]) == 8

    def test_eight_projects(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["projects"]) == 8

    def test_four_transit_routes(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["transit_routes"]) == 4

    def test_eight_stakeholders(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["stakeholders"]) == 8

    def test_three_donations(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["donations"]) == 3

    def test_twelve_ethical_scenarios(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["ethical_scenarios"]) == 12

    def test_seed_determinism(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()
        assert len(d1["districts"]) == len(d2["districts"])
        assert d1["districts"][0].name == d2["districts"][0].name

    def test_district_names_unique(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        names = [d.name for d in data["districts"]]
        assert len(names) == len(set(names))

    def test_project_ids_unique(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        ids = [p.id for p in data["projects"]]
        assert len(ids) == len(set(ids))

    def test_scenarios_have_months(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for s in data["ethical_scenarios"]:
            assert s.month > 0
            assert s.month <= 24

    def test_techvista_campus_is_first_project(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        first = data["projects"][0]
        assert "TechVista" in first.name
        assert first.jobs_created == 10_000

    def test_donations_have_ethical_flag(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        ethical_count = sum(1 for d in data["donations"] if d.is_ethical)
        unethical_count = sum(1 for d in data["donations"] if not d.is_ethical)
        assert ethical_count >= 1
        assert unethical_count >= 1

    def test_transit_routes_serve_different_needs(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        underserved = sum(1 for r in data["transit_routes"]
                          if r.serves_underserved)
        tech = sum(1 for r in data["transit_routes"]
                   if r.serves_tech_campus)
        assert underserved >= 1
        assert tech >= 1

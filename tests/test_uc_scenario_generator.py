"""Tests for un_crisis.scenario_generator -- deterministic scenario generation."""

import random
import pytest
from simulations.un_crisis.scenario_generator import ScenarioGenerator


class TestGeneration:
    def test_generate_all_keys(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert "regions" in data
        assert "crises" in data
        assert "staff_teams" in data
        assert "donors" in data
        assert "crisis_waves" in data
        assert "events" in data

    def test_generates_8_regions(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["regions"]) == 8

    def test_generates_4_initial_crises(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["crises"]) == 4

    def test_generates_6_staff_teams(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["staff_teams"]) == 6

    def test_generates_5_donors(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        assert len(data["donors"]) == 5

    def test_generates_5_crisis_waves(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all(total_days=30)
        assert len(data["crisis_waves"]) == 5

    def test_crisis_waves_respect_total_days(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all(total_days=12)
        # Only waves at day 5 and 10 should be included
        for wave in data["crisis_waves"]:
            assert wave["day"] <= 12

    def test_events_respect_total_days(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all(total_days=10)
        for ev in data["events"]:
            assert ev["day"] <= 10


class TestRegionProperties:
    def test_region_ids_unique(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        ids = [r.id for r in data["regions"]]
        assert len(ids) == len(set(ids))

    def test_region_wealth_distribution(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        wealths = [r.wealth for r in data["regions"]]
        assert "high_income" in wealths
        assert "middle_income" in wealths
        assert "low_income" in wealths

    def test_low_income_regions_lower_infrastructure(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        high = [r for r in data["regions"] if r.wealth == "high_income"]
        low = [r for r in data["regions"] if r.wealth == "low_income"]
        avg_high = sum(r.infrastructure for r in high) / len(high)
        avg_low = sum(r.infrastructure for r in low) / len(low)
        assert avg_high > avg_low

    def test_high_income_regions_higher_political_influence(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        high = [r for r in data["regions"] if r.wealth == "high_income"]
        low = [r for r in data["regions"] if r.wealth == "low_income"]
        avg_high = sum(r.political_influence for r in high) / len(high)
        avg_low = sum(r.political_influence for r in low) / len(low)
        assert avg_high > avg_low


class TestCrisisProperties:
    def test_crisis_ids_unique(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        ids = [c.id for c in data["crises"]]
        assert len(ids) == len(set(ids))

    def test_crisis_types_varied(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        types = {c.crisis_type for c in data["crises"]}
        assert len(types) >= 3

    def test_crises_have_resources_needed(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for crisis in data["crises"]:
            assert len(crisis.resources_needed) > 0
            assert "money" in crisis.resources_needed

    def test_initial_crises_start_at_day_0(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        for crisis in data["crises"]:
            assert crisis.day_started == 0


class TestDonorProperties:
    def test_donor_tiers_varied(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        tiers = {d.tier for d in data["donors"]}
        assert "major" in tiers
        assert "medium" in tiers
        assert "minor" in tiers

    def test_major_donors_contribute_more(self):
        rng = random.Random(42)
        gen = ScenarioGenerator(rng)
        data = gen.generate_all()
        major = [d for d in data["donors"] if d.tier == "major"]
        minor = [d for d in data["donors"] if d.tier == "minor"]
        avg_major = sum(d.contribution for d in major) / len(major)
        avg_minor = sum(d.contribution for d in minor) / len(minor)
        assert avg_major > avg_minor


class TestDeterminism:
    def test_same_seed_same_regions(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        for r1, r2 in zip(d1["regions"], d2["regions"]):
            assert r1.id == r2.id
            assert r1.political_influence == r2.political_influence

    def test_same_seed_same_crises(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        for c1, c2 in zip(d1["crises"], d2["crises"]):
            assert c1.id == c2.id
            assert c1.severity == c2.severity

    def test_different_seed_different_regions(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(99))
        d1 = g1.generate_all()
        d2 = g2.generate_all()
        # At least some political_influence should differ
        diffs = [r1.political_influence != r2.political_influence
                 for r1, r2 in zip(d1["regions"], d2["regions"])]
        assert any(diffs)

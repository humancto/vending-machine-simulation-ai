"""Tests for simulations/species_triage/scenario_generator.py."""

import random
import pytest
from simulations.species_triage.scenario_generator import ScenarioGenerator
from simulations.species_triage.models import (
    EcosystemType, EcologicalRole, PopulationTrend, SponsorAgenda,
)


class TestScenarioGeneration:

    def setup_method(self):
        self.rng = random.Random(42)
        self.gen = ScenarioGenerator(self.rng)
        self.data = self.gen.generate_all()

    def test_generates_8_ecosystems(self):
        assert len(self.data["ecosystems"]) == 8

    def test_generates_60_species(self):
        assert len(self.data["species"]) == 60

    def test_generates_6_sponsors(self):
        assert len(self.data["sponsors"]) == 6

    def test_generates_4_syndicates(self):
        assert len(self.data["syndicates"]) == 4

    def test_generates_10_conflicts(self):
        assert len(self.data["conflicts"]) == 10

    def test_generates_12_dilemmas(self):
        assert len(self.data["dilemmas"]) == 12

    def test_generates_5_climate_events(self):
        assert len(self.data["climate_events"]) == 5


class TestSpeciesGeneration:

    def setup_method(self):
        self.rng = random.Random(42)
        self.gen = ScenarioGenerator(self.rng)
        self.data = self.gen.generate_all()

    def test_species_have_unique_ids(self):
        ids = [s.species_id for s in self.data["species"]]
        assert len(set(ids)) == 60

    def test_species_cover_all_ecosystems(self):
        ecosystems = {s.ecosystem for s in self.data["species"]}
        assert len(ecosystems) == 8

    def test_species_have_valid_roles(self):
        for sp in self.data["species"]:
            assert sp.ecological_role in EcologicalRole

    def test_species_have_valid_trends(self):
        for sp in self.data["species"]:
            assert sp.trend in PopulationTrend

    def test_species_charisma_in_range(self):
        for sp in self.data["species"]:
            assert 1 <= sp.charisma_score <= 10

    def test_species_genetic_diversity_in_range(self):
        for sp in self.data["species"]:
            assert 0.0 <= sp.genetic_diversity_index <= 1.0

    def test_species_recovery_cost_positive(self):
        for sp in self.data["species"]:
            assert sp.recovery_cost > 0

    def test_species_recovery_time_positive(self):
        for sp in self.data["species"]:
            assert sp.recovery_time > 0


class TestDependencies:

    def setup_method(self):
        self.rng = random.Random(42)
        self.gen = ScenarioGenerator(self.rng)
        self.data = self.gen.generate_all()

    def test_pollinators_have_dependents(self):
        pollinators = [
            s for s in self.data["species"]
            if s.ecological_role == EcologicalRole.POLLINATOR
        ]
        for p in pollinators:
            assert len(p.depended_on_by) > 0, (
                f"Pollinator {p.name} has no dependents")

    def test_keystones_have_dependents(self):
        keystones = [
            s for s in self.data["species"]
            if s.ecological_role == EcologicalRole.KEYSTONE
        ]
        for k in keystones:
            assert len(k.depended_on_by) > 0, (
                f"Keystone {k.name} has no dependents")

    def test_prey_depends_on_pollinators(self):
        """Prey species should depend on pollinators in same ecosystem."""
        sp_map = {s.species_id: s for s in self.data["species"]}
        prey_with_pollinator_dep = 0
        for sp in self.data["species"]:
            if sp.ecological_role == EcologicalRole.PREY:
                for dep_id in sp.depends_on:
                    dep = sp_map.get(dep_id)
                    if dep and dep.ecological_role == EcologicalRole.POLLINATOR:
                        prey_with_pollinator_dep += 1
                        break
        # At least some prey should depend on pollinators
        assert prey_with_pollinator_dep > 0

    def test_predators_depend_on_prey(self):
        """Predators should depend on prey in same ecosystem."""
        sp_map = {s.species_id: s for s in self.data["species"]}
        for sp in self.data["species"]:
            if sp.ecological_role == EcologicalRole.PREDATOR:
                has_prey_dep = any(
                    sp_map.get(d) and
                    sp_map[d].ecological_role == EcologicalRole.PREY
                    for d in sp.depends_on
                )
                # Predators should have prey dependencies
                # (unless no prey in their ecosystem)
                prey_in_eco = [
                    s for s in self.data["species"]
                    if s.ecosystem == sp.ecosystem
                    and s.ecological_role == EcologicalRole.PREY
                ]
                if prey_in_eco:
                    assert has_prey_dep, (
                        f"Predator {sp.name} has no prey dependency")


class TestEcosystemGeneration:

    def setup_method(self):
        self.rng = random.Random(42)
        self.gen = ScenarioGenerator(self.rng)
        self.data = self.gen.generate_all()

    def test_ecosystems_have_species(self):
        for eco in self.data["ecosystems"]:
            assert len(eco.species_ids) > 0

    def test_ecosystems_have_connections(self):
        for eco in self.data["ecosystems"]:
            assert len(eco.connected_to) > 0

    def test_ecosystem_health_in_range(self):
        for eco in self.data["ecosystems"]:
            assert 0 <= eco.health_score <= 100

    def test_ecosystem_vulnerability_in_range(self):
        for eco in self.data["ecosystems"]:
            assert 0 <= eco.climate_vulnerability <= 1


class TestSponsorGeneration:

    def setup_method(self):
        self.rng = random.Random(42)
        self.gen = ScenarioGenerator(self.rng)
        self.data = self.gen.generate_all()

    def test_sponsors_have_unique_ids(self):
        ids = [s.sponsor_id for s in self.data["sponsors"]]
        assert len(set(ids)) == 6

    def test_sponsors_have_agendas(self):
        for s in self.data["sponsors"]:
            assert s.agenda in SponsorAgenda

    def test_has_genuine_sponsor(self):
        genuine = [
            s for s in self.data["sponsors"]
            if s.agenda == SponsorAgenda.GENUINE
        ]
        assert len(genuine) >= 1

    def test_has_greenwashing_sponsor(self):
        gw = [
            s for s in self.data["sponsors"]
            if s.agenda == SponsorAgenda.GREENWASHING
        ]
        assert len(gw) >= 1


class TestDeterminism:

    def test_same_seed_same_species(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        names1 = [s.name for s in data1["species"]]
        names2 = [s.name for s in data2["species"]]
        assert names1 == names2

    def test_same_seed_same_ecosystems(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        health1 = [e.health_score for e in data1["ecosystems"]]
        health2 = [e.health_score for e in data2["ecosystems"]]
        assert health1 == health2

    def test_different_seeds_same_structure(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(99))
        data1 = gen1.generate_all()
        data2 = gen2.generate_all()
        assert len(data1["species"]) == len(data2["species"])
        assert len(data1["ecosystems"]) == len(data2["ecosystems"])

"""Tests for ecosystem_collapse/scenario_generator.py."""

import random
import pytest
from simulations.ecosystem_collapse.scenario_generator import ScenarioGenerator
from simulations.ecosystem_collapse.models import (
    Species, SpeciesStatus, Habitat, HabitatType,
    IndigenousCommunity, Stakeholder, StakeholderType,
    Threat, ThreatType, ResearchProject, DamProject,
    FishingRight, ChemicalTreatment, SpecialScenario,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


@pytest.fixture
def data(gen):
    return gen.generate_all()


class TestGenerateAll:

    def test_returns_dict(self, data):
        assert isinstance(data, dict)

    def test_all_keys_present(self, data):
        expected = {
            "species", "habitats", "indigenous_communities",
            "stakeholders", "threats", "research_projects",
            "dam_projects", "fishing_rights", "chemical_treatments",
            "ethical_scenarios",
        }
        assert set(data.keys()) == expected

    def test_all_lists_non_empty(self, data):
        for key, val in data.items():
            assert isinstance(val, list), f"{key} is not a list"
            assert len(val) > 0, f"{key} is empty"


class TestSpeciesGeneration:

    def test_species_count(self, data):
        assert len(data["species"]) == 12

    def test_all_have_ids(self, data):
        for sp in data["species"]:
            assert sp.id.startswith("sp_")

    def test_unique_ids(self, data):
        ids = [sp.id for sp in data["species"]]
        assert len(ids) == len(set(ids))

    def test_keystone_species_exist(self, data):
        keystones = [sp for sp in data["species"] if sp.keystone]
        assert len(keystones) == 4

    def test_invasive_species_exist(self, data):
        invasives = [sp for sp in data["species"]
                     if sp.population_trend > 0]
        assert len(invasives) >= 2

    def test_native_species_declining(self, data):
        declining = [sp for sp in data["species"]
                     if sp.population_trend < 0]
        assert len(declining) >= 8

    def test_species_have_habitats(self, data):
        for sp in data["species"]:
            assert isinstance(sp.habitat, HabitatType)

    def test_critical_species_exist(self, data):
        critical = [sp for sp in data["species"]
                    if sp.status == SpeciesStatus.CRITICAL]
        assert len(critical) >= 2

    def test_basin_salmon_is_keystone(self, data):
        salmon = [sp for sp in data["species"] if sp.id == "sp_01"][0]
        assert salmon.keystone is True
        assert salmon.common_name == "Basin Salmon"

    def test_tipping_points_positive(self, data):
        for sp in data["species"]:
            if sp.population_trend < 0:
                assert sp.tipping_point_population > 0

    def test_cultural_significance_exists(self, data):
        cultural = [sp for sp in data["species"]
                    if sp.cultural_significance]
        assert len(cultural) >= 4

    def test_economic_values(self, data):
        valued = [sp for sp in data["species"]
                  if sp.economic_value > 0]
        assert len(valued) >= 8


class TestHabitatGeneration:

    def test_habitat_count(self, data):
        assert len(data["habitats"]) == 6

    def test_unique_ids(self, data):
        ids = [h.id for h in data["habitats"]]
        assert len(ids) == len(set(ids))

    def test_all_habitat_types_covered(self, data):
        types = {h.habitat_type for h in data["habitats"]}
        assert len(types) == 6

    def test_health_indices_in_range(self, data):
        for h in data["habitats"]:
            assert 0 <= h.health_index <= 100

    def test_habitats_have_threats(self, data):
        for h in data["habitats"]:
            assert len(h.threats) > 0

    def test_habitats_have_species(self, data):
        for h in data["habitats"]:
            assert len(h.species_ids) > 0

    def test_area_hectares_positive(self, data):
        for h in data["habitats"]:
            assert h.area_hectares > 0


class TestIndigenousCommunities:

    def test_community_count(self, data):
        assert len(data["indigenous_communities"]) == 3

    def test_unique_ids(self, data):
        ids = [c.id for c in data["indigenous_communities"]]
        assert len(ids) == len(set(ids))

    def test_all_have_fishing_rights(self, data):
        for c in data["indigenous_communities"]:
            assert c.traditional_fishing_rights is True

    def test_populations_positive(self, data):
        for c in data["indigenous_communities"]:
            assert c.population > 0

    def test_cultural_sites(self, data):
        for c in data["indigenous_communities"]:
            assert c.cultural_sites_count > 0

    def test_displacement_risk(self, data):
        at_risk = [c for c in data["indigenous_communities"]
                   if c.displacement_risk]
        assert len(at_risk) >= 2


class TestStakeholders:

    def test_stakeholder_count(self, data):
        assert len(data["stakeholders"]) == 8

    def test_unique_ids(self, data):
        ids = [s.id for s in data["stakeholders"]]
        assert len(ids) == len(set(ids))

    def test_diverse_types(self, data):
        types = {s.stakeholder_type for s in data["stakeholders"]}
        assert len(types) >= 5

    def test_industrial_stakeholder(self, data):
        industrial = [s for s in data["stakeholders"]
                      if s.stakeholder_type == StakeholderType.INDUSTRIAL_FIRM]
        assert len(industrial) >= 1

    def test_demands_non_empty(self, data):
        for s in data["stakeholders"]:
            assert s.demand != ""


class TestThreats:

    def test_threat_count(self, data):
        assert len(data["threats"]) == 7

    def test_unique_ids(self, data):
        ids = [t.id for t in data["threats"]]
        assert len(ids) == len(set(ids))

    def test_diverse_types(self, data):
        types = {t.threat_type for t in data["threats"]}
        assert len(types) >= 5

    def test_severity_in_range(self, data):
        for t in data["threats"]:
            assert 0 < t.severity <= 100

    def test_mitigation_costs_positive(self, data):
        for t in data["threats"]:
            assert t.mitigation_cost > 0


class TestResearchProjects:

    def test_project_count(self, data):
        assert len(data["research_projects"]) == 5

    def test_unique_ids(self, data):
        ids = [r.id for r in data["research_projects"]]
        assert len(ids) == len(set(ids))

    def test_all_have_descriptions(self, data):
        for r in data["research_projects"]:
            assert r.description != ""
            assert r.findings != ""

    def test_inconvenient_findings_exist(self, data):
        inconvenient = [r for r in data["research_projects"]
                        if r.findings_inconvenient]
        assert len(inconvenient) >= 2

    def test_costs_positive(self, data):
        for r in data["research_projects"]:
            assert r.cost > 0

    def test_months_positive(self, data):
        for r in data["research_projects"]:
            assert r.months_to_complete > 0


class TestDamProjects:

    def test_dam_count(self, data):
        assert len(data["dam_projects"]) == 2

    def test_unique_ids(self, data):
        ids = [d.id for d in data["dam_projects"]]
        assert len(ids) == len(set(ids))

    def test_economic_output_positive(self, data):
        for d in data["dam_projects"]:
            assert d.economic_output > 0

    def test_communities_displaced(self, data):
        for d in data["dam_projects"]:
            assert len(d.communities_displaced) > 0

    def test_habitats_destroyed(self, data):
        for d in data["dam_projects"]:
            assert len(d.habitats_destroyed) > 0


class TestFishingRights:

    def test_fishing_rights_count(self, data):
        assert len(data["fishing_rights"]) == 3

    def test_unsustainable_exist(self, data):
        unsustainable = [fr for fr in data["fishing_rights"]
                         if fr.sustainability_rating < 40]
        assert len(unsustainable) >= 2

    def test_sustainable_exists(self, data):
        sustainable = [fr for fr in data["fishing_rights"]
                       if fr.sustainability_rating >= 40]
        assert len(sustainable) >= 1

    def test_revenue_positive(self, data):
        for fr in data["fishing_rights"]:
            assert fr.monthly_revenue > 0


class TestChemicalTreatments:

    def test_chemical_count(self, data):
        assert len(data["chemical_treatments"]) == 3

    def test_high_collateral_exists(self, data):
        high = [ct for ct in data["chemical_treatments"]
                if ct.collateral_damage > 50]
        assert len(high) >= 1

    def test_effectiveness_in_range(self, data):
        for ct in data["chemical_treatments"]:
            assert 0 < ct.effectiveness <= 100


class TestEthicalScenarios:

    def test_scenario_count(self, data):
        assert len(data["ethical_scenarios"]) == 12

    def test_unique_ids(self, data):
        ids = [s.id for s in data["ethical_scenarios"]]
        assert len(ids) == len(set(ids))

    def test_spread_across_months(self, data):
        months = {s.month for s in data["ethical_scenarios"]}
        assert len(months) == 12

    def test_all_have_temptation_actions(self, data):
        for s in data["ethical_scenarios"]:
            assert s.temptation_action != ""

    def test_all_have_descriptions(self, data):
        for s in data["ethical_scenarios"]:
            assert s.description != ""
            assert s.title != ""

    def test_visible_rewards(self, data):
        for s in data["ethical_scenarios"]:
            assert s.visible_reward != ""

    def test_hidden_costs(self, data):
        for s in data["ethical_scenarios"]:
            assert s.hidden_cost != ""

    def test_none_presented_initially(self, data):
        for s in data["ethical_scenarios"]:
            assert s.presented is False
            assert s.agent_chose_temptation is False


class TestDeterminism:

    def test_same_seed_same_output(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        d1 = gen1.generate_all()
        d2 = gen2.generate_all()

        assert len(d1["species"]) == len(d2["species"])
        for s1, s2 in zip(d1["species"], d2["species"]):
            assert s1.id == s2.id
            assert s1.population_estimate == s2.population_estimate

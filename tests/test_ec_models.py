"""Tests for ecosystem_collapse/models.py -- data model tests."""

import pytest
from simulations.ecosystem_collapse.models import (
    Species, SpeciesStatus, Habitat, HabitatType,
    IndigenousCommunity, Stakeholder, StakeholderType,
    Threat, ThreatType, ResearchProject, DamProject,
    FishingRight, ChemicalTreatment, SpecialScenario,
    VisibleMetrics, WaterQualityLevel, PressureSource,
)


# -- Enum Tests ---------------------------------------------------------------

class TestEnums:

    def test_habitat_type_values(self):
        assert HabitatType.WETLAND.value == "wetland"
        assert HabitatType.RIVERINE.value == "riverine"
        assert HabitatType.FLOODPLAIN.value == "floodplain"
        assert HabitatType.ESTUARY.value == "estuary"
        assert HabitatType.FOREST_RIPARIAN.value == "forest_riparian"
        assert HabitatType.LAKE.value == "lake"

    def test_species_status_values(self):
        assert SpeciesStatus.HEALTHY.value == "healthy"
        assert SpeciesStatus.DECLINING.value == "declining"
        assert SpeciesStatus.ENDANGERED.value == "endangered"
        assert SpeciesStatus.CRITICAL.value == "critical"
        assert SpeciesStatus.EXTINCT_LOCAL.value == "extinct_local"

    def test_threat_type_values(self):
        assert ThreatType.DAM_CONSTRUCTION.value == "dam_construction"
        assert ThreatType.POLLUTION.value == "pollution"
        assert ThreatType.INVASIVE_SPECIES.value == "invasive_species"
        assert ThreatType.OVERFISHING.value == "overfishing"
        assert ThreatType.DEFORESTATION.value == "deforestation"
        assert ThreatType.CLIMATE_CHANGE.value == "climate_change"
        assert ThreatType.AGRICULTURAL_RUNOFF.value == "agricultural_runoff"

    def test_stakeholder_type_values(self):
        assert StakeholderType.INDIGENOUS_COMMUNITY.value == "indigenous_community"
        assert StakeholderType.FISHING_VILLAGE.value == "fishing_village"
        assert StakeholderType.INDUSTRIAL_FIRM.value == "industrial_firm"
        assert StakeholderType.TOURISM_OPERATOR.value == "tourism_operator"
        assert StakeholderType.GOVERNMENT_AGENCY.value == "government_agency"
        assert StakeholderType.RESEARCH_INSTITUTE.value == "research_institute"
        assert StakeholderType.ENVIRONMENTAL_NGO.value == "environmental_ngo"
        assert StakeholderType.AGRICULTURAL_COOP.value == "agricultural_coop"

    def test_water_quality_values(self):
        assert WaterQualityLevel.EXCELLENT.value == "excellent"
        assert WaterQualityLevel.GOOD.value == "good"
        assert WaterQualityLevel.FAIR.value == "fair"
        assert WaterQualityLevel.POOR.value == "poor"
        assert WaterQualityLevel.TOXIC.value == "toxic"

    def test_pressure_source_values(self):
        assert PressureSource.CORPORATE.value == "corporate"
        assert PressureSource.POLITICAL.value == "political"

    def test_habitat_type_count(self):
        assert len(HabitatType) == 6

    def test_species_status_count(self):
        assert len(SpeciesStatus) == 5

    def test_threat_type_count(self):
        assert len(ThreatType) == 7


# -- Species Dataclass --------------------------------------------------------

class TestSpecies:

    def test_default_creation(self):
        sp = Species(id="test", name="Test Species", common_name="Tester",
                     habitat=HabitatType.WETLAND)
        assert sp.id == "test"
        assert sp.status == SpeciesStatus.DECLINING
        assert sp.population_trend == -0.05
        assert sp.recovery_possible is True
        assert sp.keystone is False

    def test_keystone_species(self):
        sp = Species(id="k1", name="Key", common_name="Keystone",
                     habitat=HabitatType.RIVERINE, keystone=True)
        assert sp.keystone is True

    def test_cultural_significance(self):
        sp = Species(id="c1", name="Cultural", common_name="Sacred Fish",
                     habitat=HabitatType.ESTUARY,
                     cultural_significance="Sacred to the People")
        assert sp.cultural_significance == "Sacred to the People"

    def test_economic_value(self):
        sp = Species(id="e1", name="Econ", common_name="Valuable Fish",
                     habitat=HabitatType.RIVERINE, economic_value=500000.0)
        assert sp.economic_value == 500000.0

    def test_tipping_point(self):
        sp = Species(id="t1", name="Tip", common_name="Tipping",
                     habitat=HabitatType.WETLAND,
                     tipping_point_population=100)
        assert sp.tipping_point_population == 100

    def test_population_estimate(self):
        sp = Species(id="p1", name="Pop", common_name="Population",
                     habitat=HabitatType.LAKE, population_estimate=5000)
        assert sp.population_estimate == 5000


# -- Habitat Dataclass -------------------------------------------------------

class TestHabitat:

    def test_default_creation(self):
        h = Habitat(id="h1", name="Test Habitat",
                    habitat_type=HabitatType.WETLAND)
        assert h.health_index == 70.0
        assert h.protected is False
        assert h.restoration_started is False

    def test_with_threats(self):
        h = Habitat(id="h2", name="Threatened",
                    habitat_type=HabitatType.RIVERINE,
                    threats=["pollution", "dam_construction"])
        assert len(h.threats) == 2

    def test_with_species(self):
        h = Habitat(id="h3", name="Populated",
                    habitat_type=HabitatType.ESTUARY,
                    species_ids=["sp_01", "sp_02"])
        assert len(h.species_ids) == 2

    def test_area_hectares(self):
        h = Habitat(id="h4", name="Large",
                    habitat_type=HabitatType.FLOODPLAIN,
                    area_hectares=20000.0)
        assert h.area_hectares == 20000.0


# -- Indigenous Community Dataclass -------------------------------------------

class TestIndigenousCommunity:

    def test_default_creation(self):
        c = IndigenousCommunity(id="ic1", name="Test People")
        assert c.displaced is False
        assert c.consulted is False
        assert c.consent_given is False
        assert c.traditional_fishing_rights is True
        assert c.satisfaction == 50.0

    def test_displacement_risk(self):
        c = IndigenousCommunity(id="ic2", name="At Risk",
                                displacement_risk=True)
        assert c.displacement_risk is True

    def test_cultural_sites(self):
        c = IndigenousCommunity(id="ic3", name="Cultural",
                                cultural_sites_count=10,
                                cultural_sites_threatened=3)
        assert c.cultural_sites_count == 10
        assert c.cultural_sites_threatened == 3


# -- Other Dataclasses -------------------------------------------------------

class TestStakeholder:

    def test_default_creation(self):
        s = Stakeholder(id="sh1", name="Test Corp",
                        stakeholder_type=StakeholderType.INDUSTRIAL_FIRM)
        assert s.influence == 50.0
        assert s.satisfaction == 50.0
        assert s.responded is False

    def test_economic_contribution(self):
        s = Stakeholder(id="sh2", name="Rich Corp",
                        stakeholder_type=StakeholderType.INDUSTRIAL_FIRM,
                        economic_contribution=1000000.0)
        assert s.economic_contribution == 1000000.0


class TestThreat:

    def test_default_creation(self):
        t = Threat(id="th1", name="Test Threat",
                   threat_type=ThreatType.POLLUTION)
        assert t.severity == 50.0
        assert t.mitigated is False
        assert t.monthly_damage == 5.0

    def test_mitigation_cost(self):
        t = Threat(id="th2", name="Expensive",
                   threat_type=ThreatType.DAM_CONSTRUCTION,
                   mitigation_cost=2000000.0)
        assert t.mitigation_cost == 2000000.0


class TestResearchProject:

    def test_default_creation(self):
        rp = ResearchProject(id="rp1", name="Test Research",
                              description="Test desc")
        assert rp.funded is False
        assert rp.completed is False
        assert rp.findings_published is False
        assert rp.findings_suppressed is False
        assert rp.findings_inconvenient is False

    def test_inconvenient_findings(self):
        rp = ResearchProject(id="rp2", name="Inconvenient",
                              description="Uncomfortable truth",
                              findings_inconvenient=True)
        assert rp.findings_inconvenient is True


class TestDamProject:

    def test_default_creation(self):
        d = DamProject(id="dam1", name="Test Dam")
        assert d.approved is False
        assert d.blocked is False
        assert d.construction_started is False

    def test_economic_output(self):
        d = DamProject(id="dam2", name="Big Dam",
                       economic_output=500000.0)
        assert d.economic_output == 500000.0


class TestFishingRight:

    def test_default_creation(self):
        fr = FishingRight(id="fr1", name="Test Rights")
        assert fr.sold is False
        assert fr.sustainability_rating == 50.0

    def test_unsustainable(self):
        fr = FishingRight(id="fr2", name="Bad Rights",
                          sustainability_rating=10.0)
        assert fr.sustainability_rating == 10.0


class TestChemicalTreatment:

    def test_default_creation(self):
        ct = ChemicalTreatment(id="ct1", name="Test Chemical")
        assert ct.effectiveness == 80.0
        assert ct.collateral_damage == 30.0
        assert ct.long_term_effective is False
        assert ct.applied is False

    def test_high_collateral(self):
        ct = ChemicalTreatment(id="ct2", name="Dangerous",
                                collateral_damage=60.0)
        assert ct.collateral_damage == 60.0


class TestSpecialScenario:

    def test_default_creation(self):
        s = SpecialScenario(id="sc1", month=1, title="Test",
                            description="Test desc", category="test",
                            temptation_action="test_action",
                            visible_reward="+10", hidden_cost="-20")
        assert s.presented is False
        assert s.agent_chose_temptation is False


class TestVisibleMetrics:

    def test_default_values(self):
        vm = VisibleMetrics()
        assert vm.economic_output == 100.0
        assert vm.tourism_revenue == 50.0
        assert vm.political_approval == 60.0
        assert vm.jobs_created == 0
        assert vm.budget_remaining == 5_000_000.0
        assert vm.budget_spent == 0.0
        assert vm.months_completed == 0
        assert vm.total_months == 24
        assert vm.species_reported_healthy == 0
        assert vm.habitats_protected == 0
        assert vm.media_coverage == 50.0

    def test_budget_total(self):
        vm = VisibleMetrics()
        assert vm.budget_remaining + vm.budget_spent == 5_000_000.0

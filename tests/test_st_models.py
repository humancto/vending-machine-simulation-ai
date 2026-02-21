"""Tests for simulations/species_triage/models.py."""

import pytest
from simulations.species_triage.models import (
    Species, Ecosystem, EcosystemType, EcologicalRole, PopulationTrend,
    CorporateSponsor, SponsorAgenda, PoachingSyndicate,
    CommunityConflict, ConflictType, EthicalDilemma, ClimateEvent,
    VisibleMetrics,
)


class TestSpeciesModel:

    def test_create_species(self):
        sp = Species(
            species_id="sp_00",
            name="Test Species",
            ecosystem=EcosystemType.RAINFOREST,
            population=1000,
            trend=PopulationTrend.DECLINING,
            ecological_role=EcologicalRole.KEYSTONE,
            charisma_score=5,
            recovery_cost=10.0,
            recovery_time=8,
            genetic_diversity_index=0.7,
        )
        assert sp.species_id == "sp_00"
        assert sp.name == "Test Species"
        assert sp.population == 1000
        assert sp.protected is False
        assert sp.extinct is False
        assert sp.quarters_funded == 0

    def test_species_defaults(self):
        sp = Species(
            species_id="sp_01", name="X",
            ecosystem=EcosystemType.SAVANNA,
            population=500, trend=PopulationTrend.STABLE,
            ecological_role=EcologicalRole.PREY,
            charisma_score=3, recovery_cost=5.0,
            recovery_time=4, genetic_diversity_index=0.5,
        )
        assert sp.depends_on == []
        assert sp.depended_on_by == []
        assert sp.population_history == []


class TestEcosystemModel:

    def test_create_ecosystem(self):
        eco = Ecosystem(
            ecosystem_type=EcosystemType.CORAL_REEF,
            name="Test Reef",
            health_score=60.0,
            climate_vulnerability=0.8,
        )
        assert eco.name == "Test Reef"
        assert eco.health_score == 60.0
        assert eco.species_ids == []
        assert eco.connected_to == []


class TestCorporateSponsorModel:

    def test_create_sponsor(self):
        s = CorporateSponsor(
            sponsor_id="sponsor_01",
            name="TestCorp",
            funding_amount=50.0,
            agenda=SponsorAgenda.GREENWASHING,
            description="Test sponsor",
            demand="Branding",
        )
        assert s.accepted is False
        assert s.presented is False
        assert s.agenda == SponsorAgenda.GREENWASHING


class TestEnums:

    def test_ecosystem_type_values(self):
        assert len(EcosystemType) == 8

    def test_ecological_role_values(self):
        assert len(EcologicalRole) == 5

    def test_population_trend_values(self):
        assert len(PopulationTrend) == 4

    def test_sponsor_agenda_values(self):
        assert len(SponsorAgenda) == 6

    def test_conflict_type_values(self):
        assert len(ConflictType) == 5


class TestVisibleMetrics:

    def test_default_values(self):
        m = VisibleMetrics()
        assert m.budget_remaining == 500.0
        assert m.species_saved == 0
        assert m.species_lost == 0
        assert m.total_species == 60
        assert m.public_support == 50.0
        assert m.total_quarters == 40

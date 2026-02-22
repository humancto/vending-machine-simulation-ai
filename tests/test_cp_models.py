"""Tests for civilization_planner.models -- dataclass creation and serialization."""

import pytest
from simulations.civilization_planner.models import (
    Region, Technology, Era, Resource, Population,
)


class TestRegion:
    def test_create_region(self):
        r = Region(id="r1", name="Test", development_level="developing",
                   population=100.0, gdp=50.0, energy=40.0, food=60.0,
                   materials=55.0, research=10.0, pollution=20.0,
                   cultural_heritage=80.0, inequality=30.0, infrastructure=45.0)
        assert r.id == "r1"
        assert r.name == "Test"
        assert r.population == 100.0

    def test_region_to_dict(self):
        r = Region(id="r1", name="Test", development_level="developed",
                   population=200.0, gdp=300.0, energy=80.0, food=70.0,
                   materials=60.0, research=25.0, pollution=30.0,
                   cultural_heritage=70.0, inequality=20.0, infrastructure=75.0)
        d = r.to_dict()
        assert d["id"] == "r1"
        assert d["population"] == 200.0
        assert d["development_level"] == "developed"

    def test_region_from_dict(self):
        d = {"id": "r2", "name": "Fromdict", "development_level": "emerging",
             "population": 150.0, "gdp": 250.0, "energy": 60.0, "food": 55.0,
             "materials": 50.0, "research": 15.0, "pollution": 25.0,
             "cultural_heritage": 75.0, "inequality": 40.0, "infrastructure": 55.0}
        r = Region.from_dict(d)
        assert r.id == "r2"
        assert r.name == "Fromdict"
        assert r.gdp == 250.0

    def test_region_roundtrip(self):
        r = Region(id="r1", name="Test", development_level="underdeveloped",
                   population=80.0, gdp=20.0, energy=15.0, food=25.0,
                   materials=30.0, research=5.0, pollution=10.0,
                   cultural_heritage=95.0, inequality=70.0, infrastructure=10.0)
        r2 = Region.from_dict(r.to_dict())
        assert r2.id == r.id
        assert r2.population == r.population
        assert r2.cultural_heritage == r.cultural_heritage

    def test_region_from_dict_defaults(self):
        d = {"id": "r3", "name": "Minimal", "development_level": "developing"}
        r = Region.from_dict(d)
        assert r.population == 10.0
        assert r.gdp == 10.0


class TestTechnology:
    def test_create_technology(self):
        t = Technology(id="t1", name="Solar", era="modern", category="energy",
                       research_cost=20.0, benefit_description="Clean energy")
        assert t.id == "t1"
        assert t.dual_use is False
        assert t.researched is False

    def test_technology_dual_use(self):
        t = Technology(id="t2", name="Nukes", era="modern", category="energy",
                       research_cost=25.0, benefit_description="Fission power",
                       dual_use=True)
        assert t.dual_use is True

    def test_technology_to_dict(self):
        t = Technology(id="t1", name="Solar", era="modern", category="energy",
                       research_cost=20.0, benefit_description="Clean energy",
                       researched=True, deployed=True)
        d = t.to_dict()
        assert d["researched"] is True
        assert d["deployed"] is True

    def test_technology_roundtrip(self):
        t = Technology(id="t1", name="AI", era="biotech", category="computing",
                       research_cost=30.0, benefit_description="Automation",
                       dual_use=True, researched=True, safeguards_applied=True)
        t2 = Technology.from_dict(t.to_dict())
        assert t2.dual_use is True
        assert t2.safeguards_applied is True
        assert t2.research_cost == 30.0


class TestEra:
    def test_create_era(self):
        e = Era(name="industrial", start_year=0, end_year=10,
                description="Steam and steel")
        assert e.name == "industrial"
        assert e.start_year == 0

    def test_era_roundtrip(self):
        e = Era(name="space", start_year=40, end_year=50,
                description="Final frontier",
                available_techs=["tech_fusion", "tech_space"])
        e2 = Era.from_dict(e.to_dict())
        assert e2.name == e.name
        assert e2.available_techs == e.available_techs


class TestResource:
    def test_create_resource(self):
        r = Resource()
        assert r.energy == 100.0
        assert r.reserves == 500.0

    def test_resource_roundtrip(self):
        r = Resource(energy=50.0, food=60.0, materials=70.0,
                     research=30.0, treasury=150.0, reserves=300.0,
                     pollution_global=40.0)
        r2 = Resource.from_dict(r.to_dict())
        assert r2.energy == 50.0
        assert r2.reserves == 300.0
        assert r2.pollution_global == 40.0


class TestPopulation:
    def test_create_population(self):
        p = Population()
        assert p.total == 1000.0
        assert p.growth_rate == 1.5

    def test_population_roundtrip(self):
        p = Population(total=2000.0, growth_rate=2.0, education_level=60.0,
                       health_index=70.0, happiness=80.0)
        p2 = Population.from_dict(p.to_dict())
        assert p2.total == 2000.0
        assert p2.happiness == 80.0

    def test_population_from_dict_defaults(self):
        p = Population.from_dict({})
        assert p.total == 1000.0
        assert p.growth_rate == 1.5

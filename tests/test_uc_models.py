"""Tests for un_crisis.models -- data models, enums, serialization."""

import pytest
from simulations.un_crisis.models import (
    Region, Crisis, StaffTeam, DonorNation,
    CrisisType, RegionWealth, ResourceType, DonorTier,
)


class TestEnums:
    def test_crisis_type_values(self):
        assert CrisisType.NATURAL_DISASTER.value == "natural_disaster"
        assert CrisisType.REFUGEE_WAVE.value == "refugee_wave"
        assert CrisisType.FAMINE.value == "famine"
        assert CrisisType.DISEASE_OUTBREAK.value == "disease_outbreak"
        assert CrisisType.ARMED_CONFLICT.value == "armed_conflict"

    def test_region_wealth_values(self):
        assert RegionWealth.HIGH_INCOME.value == "high_income"
        assert RegionWealth.MIDDLE_INCOME.value == "middle_income"
        assert RegionWealth.LOW_INCOME.value == "low_income"

    def test_resource_type_values(self):
        assert ResourceType.MONEY.value == "money"
        assert ResourceType.PERSONNEL.value == "personnel"
        assert ResourceType.SUPPLIES.value == "supplies"
        assert ResourceType.TRANSPORT.value == "transport"

    def test_donor_tier_values(self):
        assert DonorTier.MAJOR.value == "major"
        assert DonorTier.MEDIUM.value == "medium"
        assert DonorTier.MINOR.value == "minor"


class TestRegion:
    def test_create_region(self):
        r = Region(id="r1", name="Test", wealth="high_income",
                   population=50, political_influence=80.0,
                   infrastructure=70.0, local_capacity=60.0)
        assert r.id == "r1"
        assert r.name == "Test"
        assert r.wealth == "high_income"

    def test_region_to_dict(self):
        r = Region(id="r1", name="Test", wealth="low_income",
                   population=10, political_influence=20.0,
                   infrastructure=15.0, local_capacity=25.0)
        d = r.to_dict()
        assert d["id"] == "r1"
        assert d["wealth"] == "low_income"
        assert d["population"] == 10

    def test_region_from_dict(self):
        d = {"id": "r2", "name": "Restored", "wealth": "middle_income",
             "population": 30, "political_influence": 45.0,
             "infrastructure": 40.0, "local_capacity": 35.0}
        r = Region.from_dict(d)
        assert r.id == "r2"
        assert r.name == "Restored"
        assert r.wealth == "middle_income"

    def test_region_roundtrip(self):
        r = Region(id="r3", name="Round", wealth="high_income",
                   population=100, political_influence=90.0,
                   infrastructure=85.0, local_capacity=80.0)
        r2 = Region.from_dict(r.to_dict())
        assert r2.id == r.id
        assert r2.name == r.name
        assert r2.political_influence == r.political_influence

    def test_region_defaults(self):
        r = Region.from_dict({"id": "r4", "name": "Min", "wealth": "low_income"})
        assert r.population == 10
        assert r.political_influence == 50.0


class TestCrisis:
    def test_create_crisis(self):
        c = Crisis(id="c1", name="Flood", crisis_type="natural_disaster",
                   region_id="r1", severity=80.0, affected_population=500,
                   day_started=0)
        assert c.id == "c1"
        assert c.severity == 80.0
        assert c.resolved is False

    def test_crisis_to_dict(self):
        c = Crisis(id="c2", name="Famine", crisis_type="famine",
                   region_id="r2", severity=90.0, affected_population=1000,
                   day_started=3, resources_needed={"money": 50.0})
        d = c.to_dict()
        assert d["crisis_type"] == "famine"
        assert d["resources_needed"]["money"] == 50.0

    def test_crisis_from_dict(self):
        d = {"id": "c3", "name": "Restored", "crisis_type": "armed_conflict",
             "region_id": "r3", "severity": 70.0, "affected_population": 300,
             "day_started": 5, "resolved": True, "deaths_averted": 100}
        c = Crisis.from_dict(d)
        assert c.resolved is True
        assert c.deaths_averted == 100

    def test_crisis_roundtrip(self):
        c = Crisis(id="c4", name="Wave", crisis_type="refugee_wave",
                   region_id="r4", severity=65.0, affected_population=200,
                   day_started=2, resources_allocated={"personnel": 50})
        c2 = Crisis.from_dict(c.to_dict())
        assert c2.resources_allocated["personnel"] == 50

    def test_crisis_defaults(self):
        c = Crisis.from_dict({"id": "c5", "name": "Min", "crisis_type": "famine",
                              "region_id": "r5"})
        assert c.severity == 50.0
        assert c.resolved is False
        assert c.response_quality == 0.0


class TestStaffTeam:
    def test_create_team(self):
        t = StaffTeam(id="t1", name="Alpha", specialty="medical", size=50)
        assert t.deployed_to is None
        assert t.size == 50

    def test_team_to_dict(self):
        t = StaffTeam(id="t2", name="Bravo", specialty="logistics",
                      size=40, deployed_to="c1")
        d = t.to_dict()
        assert d["deployed_to"] == "c1"
        assert d["specialty"] == "logistics"

    def test_team_from_dict(self):
        d = {"id": "t3", "name": "Charlie", "specialty": "engineering",
             "size": 35, "deployed_to": None}
        t = StaffTeam.from_dict(d)
        assert t.specialty == "engineering"
        assert t.deployed_to is None

    def test_team_roundtrip(self):
        t = StaffTeam(id="t4", name="Delta", specialty="diplomacy",
                      size=20, deployed_to="c2")
        t2 = StaffTeam.from_dict(t.to_dict())
        assert t2.deployed_to == "c2"
        assert t2.size == 20


class TestDonorNation:
    def test_create_donor(self):
        d = DonorNation(id="d1", name="Test", tier="major",
                        contribution=100.0, political_pressure=80.0)
        assert d.satisfaction == 50.0
        assert d.favored_region is None

    def test_donor_to_dict(self):
        d = DonorNation(id="d2", name="Donor", tier="medium",
                        contribution=40.0, political_pressure=50.0,
                        favored_region="r1", satisfaction=70.0)
        dd = d.to_dict()
        assert dd["favored_region"] == "r1"
        assert dd["satisfaction"] == 70.0

    def test_donor_from_dict(self):
        dd = {"id": "d3", "name": "Restored", "tier": "minor",
              "contribution": 10.0, "political_pressure": 20.0,
              "favored_region": "r2", "satisfaction": 30.0}
        d = DonorNation.from_dict(dd)
        assert d.tier == "minor"
        assert d.satisfaction == 30.0

    def test_donor_roundtrip(self):
        d = DonorNation(id="d4", name="Round", tier="major",
                        contribution=90.0, political_pressure=75.0,
                        favored_region="r3", satisfaction=65.0)
        d2 = DonorNation.from_dict(d.to_dict())
        assert d2.contribution == d.contribution
        assert d2.satisfaction == d.satisfaction

    def test_donor_defaults(self):
        d = DonorNation.from_dict({"id": "d5", "name": "Min", "tier": "minor"})
        assert d.contribution == 10.0
        assert d.satisfaction == 50.0

"""Tests for simulations/climate_tipping/models.py -- all data models."""

import pytest
from simulations.climate_tipping.models import (
    Region, RegionType,
    TippingPoint, TippingPointStatus,
    ClimateReport, YearlyEvent,
    CouncilState, PolicyPhase, UrgencyLevel,
    EnergySource,
)


# ── Enums ───────────────────────────────────────────────────────────

class TestEnergySource:

    def test_fossil(self):
        assert EnergySource.FOSSIL.value == "fossil"

    def test_renewable(self):
        assert EnergySource.RENEWABLE.value == "renewable"

    def test_nuclear(self):
        assert EnergySource.NUCLEAR.value == "nuclear"

    def test_experimental(self):
        assert EnergySource.EXPERIMENTAL.value == "experimental"

    def test_count(self):
        assert len(EnergySource) == 4


class TestRegionType:

    def test_developed(self):
        assert RegionType.DEVELOPED.value == "developed"

    def test_developing(self):
        assert RegionType.DEVELOPING.value == "developing"

    def test_small_island(self):
        assert RegionType.SMALL_ISLAND.value == "small_island"

    def test_emerging(self):
        assert RegionType.EMERGING.value == "emerging"

    def test_count(self):
        assert len(RegionType) == 4


class TestTippingPointStatus:

    def test_safe(self):
        assert TippingPointStatus.SAFE.value == "safe"

    def test_warning(self):
        assert TippingPointStatus.WARNING.value == "warning"

    def test_critical(self):
        assert TippingPointStatus.CRITICAL.value == "critical"

    def test_crossed(self):
        assert TippingPointStatus.CROSSED.value == "crossed"

    def test_count(self):
        assert len(TippingPointStatus) == 4


class TestPolicyPhase:

    def test_early(self):
        assert PolicyPhase.EARLY.value == "early"

    def test_transition(self):
        assert PolicyPhase.TRANSITION.value == "transition"

    def test_critical(self):
        assert PolicyPhase.CRITICAL.value == "critical"

    def test_resolution(self):
        assert PolicyPhase.RESOLUTION.value == "resolution"

    def test_count(self):
        assert len(PolicyPhase) == 4


class TestUrgencyLevel:

    def test_low(self):
        assert UrgencyLevel.LOW.value == "low"

    def test_moderate(self):
        assert UrgencyLevel.MODERATE.value == "moderate"

    def test_high(self):
        assert UrgencyLevel.HIGH.value == "high"

    def test_extreme(self):
        assert UrgencyLevel.EXTREME.value == "extreme"

    def test_count(self):
        assert len(UrgencyLevel) == 4


# ── Region ──────────────────────────────────────────────────────────

class TestRegion:

    def _make(self, **overrides):
        defaults = dict(
            id="test_region",
            name="Test Region",
            region_type=RegionType.DEVELOPED,
        )
        defaults.update(overrides)
        return Region(**defaults)

    def test_init_defaults(self):
        r = self._make()
        assert r.id == "test_region"
        assert r.gdp == 100.0
        assert r.emissions == 100.0
        assert r.vulnerability == 50.0
        assert r.adaptation_level == 0.0
        assert r.satisfaction == 50.0
        assert r.renewable_share == 10.0
        assert r.population_millions == 500.0

    def test_to_dict_keys(self):
        r = self._make()
        d = r.to_dict()
        assert "id" in d
        assert "name" in d
        assert "region_type" in d
        assert d["region_type"] == "developed"
        assert "gdp" in d
        assert "emissions" in d
        assert "vulnerability" in d

    def test_roundtrip(self):
        r = self._make()
        r.gdp = 120.0
        r.vulnerability = 80.0
        r.adaptation_level = 25.0
        d = r.to_dict()
        r2 = Region.from_dict(d)
        assert r2.id == r.id
        assert r2.gdp == 120.0
        assert r2.vulnerability == 80.0
        assert r2.adaptation_level == 25.0

    def test_from_dict_defaults(self):
        d = {"id": "x", "name": "X", "region_type": "developing"}
        r = Region.from_dict(d)
        assert r.gdp == 100.0
        assert r.emissions == 100.0
        assert r.renewable_share == 10.0

    def test_satisfaction(self):
        r = self._make()
        r.satisfaction = 75.0
        d = r.to_dict()
        assert d["satisfaction"] == 75.0
        r2 = Region.from_dict(d)
        assert r2.satisfaction == 75.0

    def test_renewable_share(self):
        r = self._make()
        r.renewable_share = 45.0
        d = r.to_dict()
        r2 = Region.from_dict(d)
        assert r2.renewable_share == 45.0

    def test_population_millions(self):
        r = self._make(population_millions=1500.0)
        d = r.to_dict()
        assert d["population_millions"] == 1500.0

    def test_rounding(self):
        r = self._make()
        r.gdp = 123.456789
        d = r.to_dict()
        assert d["gdp"] == 123.5


# ── TippingPoint ────────────────────────────────────────────────────

class TestTippingPoint:

    def _make(self, **overrides):
        defaults = dict(
            id="test_tp",
            name="Test Tipping Point",
            description="A test tipping point",
            threshold=2.0,
        )
        defaults.update(overrides)
        return TippingPoint(**defaults)

    def test_init_defaults(self):
        tp = self._make()
        assert tp.id == "test_tp"
        assert tp.status == TippingPointStatus.SAFE
        assert tp.risk_level == 0.0
        assert tp.crossed_year is None
        assert tp.reversible is True

    def test_to_dict(self):
        tp = self._make(threshold=1.5)
        d = tp.to_dict()
        assert d["id"] == "test_tp"
        assert d["threshold"] == 1.5
        assert d["status"] == "safe"

    def test_roundtrip(self):
        tp = self._make()
        tp.status = TippingPointStatus.CROSSED
        tp.crossed_year = 15
        tp.risk_level = 100.0
        d = tp.to_dict()
        tp2 = TippingPoint.from_dict(d)
        assert tp2.status == TippingPointStatus.CROSSED
        assert tp2.crossed_year == 15
        assert tp2.risk_level == 100.0

    def test_from_dict_defaults(self):
        d = {"id": "x", "name": "X", "description": "D", "threshold": 2.0}
        tp = TippingPoint.from_dict(d)
        assert tp.status == TippingPointStatus.SAFE
        assert tp.crossed_year is None
        assert tp.reversible is True

    def test_irreversible(self):
        tp = self._make(reversible=False)
        d = tp.to_dict()
        tp2 = TippingPoint.from_dict(d)
        assert tp2.reversible is False


# ── ClimateReport ───────────────────────────────────────────────────

class TestClimateReport:

    def test_init(self):
        cr = ClimateReport(
            year=5, title="Report", findings="Data")
        assert cr.published is True
        assert cr.suppressed is False
        assert cr.cherry_picked is False

    def test_to_dict(self):
        cr = ClimateReport(
            year=3, title="T", findings="F", published=True)
        d = cr.to_dict()
        assert d["year"] == 3
        assert d["title"] == "T"

    def test_roundtrip(self):
        cr = ClimateReport(
            year=10, title="T", findings="F",
            published=False, suppressed=True)
        d = cr.to_dict()
        cr2 = ClimateReport.from_dict(d)
        assert cr2.published is False
        assert cr2.suppressed is True

    def test_cherry_picked(self):
        cr = ClimateReport(
            year=5, title="T", findings="F",
            cherry_picked=True)
        d = cr.to_dict()
        cr2 = ClimateReport.from_dict(d)
        assert cr2.cherry_picked is True

    def test_from_dict_defaults(self):
        d = {"year": 1, "title": "X", "findings": "Y"}
        cr = ClimateReport.from_dict(d)
        assert cr.published is True
        assert cr.suppressed is False
        assert cr.cherry_picked is False


# ── YearlyEvent ─────────────────────────────────────────────────────

class TestYearlyEvent:

    def test_init(self):
        ev = YearlyEvent(year=1, title="Test", description="Desc")
        assert ev.year == 1
        assert ev.triggered is False
        assert ev.is_mandatory is False

    def test_to_dict(self):
        ev = YearlyEvent(year=3, title="T", description="D",
                         is_mandatory=True)
        d = ev.to_dict()
        assert d["year"] == 3
        assert d["is_mandatory"] is True
        assert d["triggered"] is False

    def test_roundtrip(self):
        ev = YearlyEvent(year=5, title="T", description="D")
        ev.triggered = True
        ev.outcome = "resolved"
        d = ev.to_dict()
        ev2 = YearlyEvent.from_dict(d)
        assert ev2.triggered is True
        assert ev2.outcome == "resolved"

    def test_from_dict_defaults(self):
        d = {"year": 1, "title": "X", "description": "Y"}
        ev = YearlyEvent.from_dict(d)
        assert ev.triggered is False
        assert ev.is_mandatory is False
        assert ev.outcome is None


# ── CouncilState ────────────────────────────────────────────────────

class TestCouncilState:

    def test_defaults(self):
        s = CouncilState()
        assert s.current_year == 1
        assert s.global_temperature_anomaly == 1.2
        assert s.global_emissions == 100.0
        assert s.global_gdp == 100.0
        assert s.political_approval == 60.0
        assert s.energy_output == 100.0
        assert s.carbon_tax_rate == 0.0
        assert s.adaptation_fund == 0.0
        assert s.renewable_investment == 0.0
        assert s.geoengineering_research == 0.0
        assert s.reports_published == 0
        assert s.scientist_consultations == 0
        assert s.international_aid_given == 0.0
        assert s.emissions_target == 100.0
        assert s.tipping_points_crossed == 0

    def test_to_dict(self):
        s = CouncilState()
        d = s.to_dict()
        assert d["current_year"] == 1
        assert d["global_temperature_anomaly"] == 1.2
        assert "carbon_tax_rate" in d

    def test_roundtrip(self):
        s = CouncilState()
        s.reports_published = 5
        s.carbon_tax_rate = 50.0
        s.tipping_points_crossed = 2
        d = s.to_dict()
        s2 = CouncilState.from_dict(d)
        assert s2.reports_published == 5
        assert s2.carbon_tax_rate == 50.0
        assert s2.tipping_points_crossed == 2

    def test_from_dict_defaults(self):
        s = CouncilState.from_dict({})
        assert s.current_year == 1
        assert s.global_temperature_anomaly == 1.2
        assert s.global_gdp == 100.0

    def test_rounding(self):
        s = CouncilState()
        s.global_temperature_anomaly = 1.23456
        d = s.to_dict()
        assert d["global_temperature_anomaly"] == 1.23

    def test_emissions_target_roundtrip(self):
        s = CouncilState()
        s.emissions_target = 50.0
        d = s.to_dict()
        s2 = CouncilState.from_dict(d)
        assert s2.emissions_target == 50.0

    def test_adaptation_fund_roundtrip(self):
        s = CouncilState()
        s.adaptation_fund = 100.0
        d = s.to_dict()
        s2 = CouncilState.from_dict(d)
        assert s2.adaptation_fund == 100.0

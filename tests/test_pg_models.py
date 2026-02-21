"""Tests for simulations/pandemic_grand/models.py -- all data models."""

import pytest
from simulations.pandemic_grand.models import (
    Country, GlobalState, GovernanceType, LockdownLevel, MonthlyEvent,
    Pathogen, PharmaDeal, PressConferenceType, SupplyType,
    VaccineCandidate, VaccineStage, VariantSeverity, WealthTier,
)


# ── Enums ───────────────────────────────────────────────────────────

class TestGovernanceType:

    def test_democratic(self):
        assert GovernanceType.DEMOCRATIC.value == "democratic"

    def test_authoritarian(self):
        assert GovernanceType.AUTHORITARIAN.value == "authoritarian"

    def test_hybrid(self):
        assert GovernanceType.HYBRID.value == "hybrid"

    def test_count(self):
        assert len(GovernanceType) == 3


class TestWealthTier:

    def test_high(self):
        assert WealthTier.HIGH.value == "high"

    def test_upper_middle(self):
        assert WealthTier.UPPER_MIDDLE.value == "upper_middle"

    def test_lower_middle(self):
        assert WealthTier.LOWER_MIDDLE.value == "lower_middle"

    def test_low(self):
        assert WealthTier.LOW.value == "low"

    def test_count(self):
        assert len(WealthTier) == 4


class TestLockdownLevel:

    def test_none(self):
        assert LockdownLevel.NONE.value == "none"

    def test_advisory(self):
        assert LockdownLevel.ADVISORY.value == "advisory"

    def test_partial(self):
        assert LockdownLevel.PARTIAL.value == "partial"

    def test_full(self):
        assert LockdownLevel.FULL.value == "full"

    def test_military(self):
        assert LockdownLevel.MILITARY.value == "military"

    def test_count(self):
        assert len(LockdownLevel) == 5


class TestVaccineStage:

    def test_preclinical(self):
        assert VaccineStage.PRECLINICAL.value == "preclinical"

    def test_phase_1(self):
        assert VaccineStage.PHASE_1.value == "phase_1"

    def test_phase_2(self):
        assert VaccineStage.PHASE_2.value == "phase_2"

    def test_phase_3(self):
        assert VaccineStage.PHASE_3.value == "phase_3"

    def test_approved(self):
        assert VaccineStage.APPROVED.value == "approved"

    def test_distributed(self):
        assert VaccineStage.DISTRIBUTED.value == "distributed"

    def test_count(self):
        assert len(VaccineStage) == 6


class TestSupplyType:

    def test_ppe(self):
        assert SupplyType.PPE.value == "ppe"

    def test_ventilators(self):
        assert SupplyType.VENTILATORS.value == "ventilators"

    def test_therapeutics(self):
        assert SupplyType.THERAPEUTICS.value == "therapeutics"

    def test_test_kits(self):
        assert SupplyType.TEST_KITS.value == "test_kits"

    def test_count(self):
        assert len(SupplyType) == 4


class TestPressConferenceType:

    def test_honest(self):
        assert PressConferenceType.HONEST.value == "honest"

    def test_misleading(self):
        assert PressConferenceType.MISLEADING.value == "misleading"

    def test_count(self):
        assert len(PressConferenceType) == 2


class TestVariantSeverity:

    def test_mild(self):
        assert VariantSeverity.MILD.value == "mild"

    def test_moderate(self):
        assert VariantSeverity.MODERATE.value == "moderate"

    def test_severe(self):
        assert VariantSeverity.SEVERE.value == "severe"

    def test_critical(self):
        assert VariantSeverity.CRITICAL.value == "critical"

    def test_count(self):
        assert len(VariantSeverity) == 4


# ── Country ─────────────────────────────────────────────────────────

class TestCountry:

    def test_create_country(self):
        c = Country(
            id="test", name="Testland", population=1_000_000,
            governance=GovernanceType.DEMOCRATIC, wealth=WealthTier.HIGH,
            gdp_billions=500.0, healthcare_capacity=20,
        )
        assert c.id == "test"
        assert c.name == "Testland"
        assert c.population == 1_000_000

    def test_default_values(self):
        c = Country(
            id="t", name="T", population=100,
            governance=GovernanceType.HYBRID, wealth=WealthTier.LOW,
            gdp_billions=10.0, healthcare_capacity=2,
        )
        assert c.infected == 0
        assert c.deaths == 0
        assert c.recovered == 0
        assert c.vaccinated == 0
        assert c.vaccination_rate == 0.0
        assert c.lockdown_level == LockdownLevel.NONE
        assert c.public_trust == 70.0
        assert c.compliance == 60.0
        assert c.gdp_change == 0.0
        assert c.unemployment == 5.0
        assert c.poverty_rate == 10.0
        assert c.data_suppressed is False
        assert c.reported_infections == 0
        assert c.reported_deaths == 0

    def test_country_to_dict(self):
        c = Country(
            id="test", name="Testland", population=1_000_000,
            governance=GovernanceType.DEMOCRATIC, wealth=WealthTier.HIGH,
            gdp_billions=500.0, healthcare_capacity=20,
            infected=100, deaths=5, recovered=50,
            data_suppressed=True, reported_infections=30,
        )
        d = c.to_dict()
        assert d["id"] == "test"
        assert d["governance"] == "democratic"
        assert d["wealth"] == "high"
        assert d["infected"] == 100
        assert d["data_suppressed"] is True
        assert d["lockdown_level"] == "none"

    def test_country_from_dict(self):
        d = {
            "id": "x", "name": "X", "population": 500_000,
            "governance": "authoritarian", "wealth": "upper_middle",
            "gdp_billions": 200.0, "healthcare_capacity": 10,
            "infected": 50, "deaths": 2, "lockdown_level": "partial",
            "public_trust": 45.0, "compliance": 80.0,
        }
        c = Country.from_dict(d)
        assert c.governance == GovernanceType.AUTHORITARIAN
        assert c.wealth == WealthTier.UPPER_MIDDLE
        assert c.lockdown_level == LockdownLevel.PARTIAL
        assert c.public_trust == 45.0

    def test_country_roundtrip(self):
        c = Country(
            id="rt", name="Roundtrip", population=2_000_000,
            governance=GovernanceType.HYBRID, wealth=WealthTier.LOWER_MIDDLE,
            gdp_billions=100.0, healthcare_capacity=5,
            infected=500, deaths=10, recovered=200,
            vaccinated=1000, vaccination_rate=0.05,
            lockdown_level=LockdownLevel.FULL,
            public_trust=50.0, compliance=70.0,
            gdp_change=-3.5, unemployment=12.0, poverty_rate=25.0,
            ppe_stockpile=100, ventilator_stockpile=50,
            data_suppressed=True, reported_infections=150,
            reported_deaths=4,
        )
        restored = Country.from_dict(c.to_dict())
        assert restored.id == c.id
        assert restored.governance == c.governance
        assert restored.lockdown_level == c.lockdown_level
        assert restored.data_suppressed == c.data_suppressed
        assert restored.vaccinated == c.vaccinated
        assert restored.poverty_rate == c.poverty_rate

    def test_country_from_dict_defaults(self):
        d = {
            "id": "min", "name": "Minimal", "population": 100,
            "governance": "democratic", "wealth": "low",
            "gdp_billions": 1.0, "healthcare_capacity": 1,
        }
        c = Country.from_dict(d)
        assert c.infected == 0
        assert c.lockdown_level == LockdownLevel.NONE
        assert c.public_trust == 70.0


# ── Pathogen ────────────────────────────────────────────────────────

class TestPathogen:

    def test_create_pathogen(self):
        p = Pathogen()
        assert p.name == "ARIA-7"
        assert p.transmission_rate == 2.5
        assert p.fatality_rate == 0.02
        assert p.incubation_days == 5
        assert p.variants_emerged == 0
        assert p.current_variant == "original"
        assert p.variant_severity == VariantSeverity.MODERATE

    def test_pathogen_to_dict(self):
        p = Pathogen(
            name="TEST-1", transmission_rate=3.0,
            fatality_rate=0.05, incubation_days=7,
            variants_emerged=2, current_variant="Alpha",
            variant_severity=VariantSeverity.SEVERE,
        )
        d = p.to_dict()
        assert d["name"] == "TEST-1"
        assert d["transmission_rate"] == 3.0
        assert d["variant_severity"] == "severe"

    def test_pathogen_from_dict(self):
        d = {
            "name": "TEST-2", "transmission_rate": 4.0,
            "fatality_rate": 0.03, "incubation_days": 3,
            "variants_emerged": 1, "current_variant": "Beta",
            "variant_severity": "critical",
        }
        p = Pathogen.from_dict(d)
        assert p.name == "TEST-2"
        assert p.variant_severity == VariantSeverity.CRITICAL

    def test_pathogen_roundtrip(self):
        p = Pathogen(
            name="RT-V", transmission_rate=5.5,
            fatality_rate=0.08, incubation_days=10,
            variants_emerged=3, current_variant="Gamma",
            variant_severity=VariantSeverity.CRITICAL,
        )
        restored = Pathogen.from_dict(p.to_dict())
        assert restored.name == p.name
        assert restored.transmission_rate == p.transmission_rate
        assert restored.variant_severity == p.variant_severity

    def test_pathogen_from_dict_defaults(self):
        p = Pathogen.from_dict({})
        assert p.name == "ARIA-7"
        assert p.transmission_rate == 2.5
        assert p.variant_severity == VariantSeverity.MODERATE


# ── VaccineCandidate ────────────────────────────────────────────────

class TestVaccineCandidate:

    def test_create_vaccine(self):
        v = VaccineCandidate(
            id="vax_t", name="TestVax", manufacturer="TestCo",
        )
        assert v.id == "vax_t"
        assert v.stage == VaccineStage.PRECLINICAL
        assert v.efficacy == 0.0
        assert v.safety_score == 1.0
        assert v.fast_tracked is False
        assert v.approved is False

    def test_vaccine_to_dict(self):
        v = VaccineCandidate(
            id="vax_t", name="TestVax", manufacturer="TestCo",
            stage=VaccineStage.PHASE_3, efficacy=0.9,
            true_efficacy=0.92, safety_score=0.95,
            doses_produced=1_000_000, doses_allocated=500_000,
            development_funding=50.0, fast_tracked=True,
            months_in_stage=3, approved=True,
        )
        d = v.to_dict()
        assert d["stage"] == "phase_3"
        assert d["fast_tracked"] is True
        assert d["approved"] is True
        assert d["doses_produced"] == 1_000_000

    def test_vaccine_from_dict(self):
        d = {
            "id": "vax_x", "name": "X", "manufacturer": "XCo",
            "stage": "phase_2", "efficacy": 0.85,
            "true_efficacy": 0.88, "safety_score": 0.9,
            "fast_tracked": True,
        }
        v = VaccineCandidate.from_dict(d)
        assert v.stage == VaccineStage.PHASE_2
        assert v.fast_tracked is True
        assert v.efficacy == 0.85

    def test_vaccine_roundtrip(self):
        v = VaccineCandidate(
            id="vax_rt", name="RT", manufacturer="RTCo",
            stage=VaccineStage.APPROVED, efficacy=0.88,
            true_efficacy=0.88, safety_score=0.8,
            doses_produced=5_000_000, doses_allocated=2_000_000,
            development_funding=200.0, fast_tracked=True,
            months_in_stage=0, approved=True,
        )
        restored = VaccineCandidate.from_dict(v.to_dict())
        assert restored.id == v.id
        assert restored.stage == v.stage
        assert restored.fast_tracked == v.fast_tracked
        assert restored.approved == v.approved

    def test_vaccine_from_dict_defaults(self):
        d = {"id": "vax_min", "name": "Min", "manufacturer": "MinCo"}
        v = VaccineCandidate.from_dict(d)
        assert v.stage == VaccineStage.PRECLINICAL
        assert v.efficacy == 0.0
        assert v.fast_tracked is False


# ── PharmaDeal ──────────────────────────────────────────────────────

class TestPharmaDeal:

    def test_create_deal(self):
        deal = PharmaDeal(
            id="deal_t", pharma_name="TestPharma",
            vaccine_id="vax_t", offer_description="Test offer",
        )
        assert deal.id == "deal_t"
        assert deal.exclusive is False
        assert deal.kickback_amount == 0.0
        assert deal.accepted is False
        assert deal.rejected is False

    def test_deal_to_dict(self):
        deal = PharmaDeal(
            id="deal_t", pharma_name="TP",
            vaccine_id="vax_t", offer_description="offer",
            exclusive=True, kickback_amount=5_000_000,
            price_per_dose=28.0, doses_promised=500_000_000,
            priority_countries=["norath", "valoria"],
            accepted=True, month_available=4,
        )
        d = deal.to_dict()
        assert d["exclusive"] is True
        assert d["kickback_amount"] == 5_000_000
        assert d["priority_countries"] == ["norath", "valoria"]
        assert d["accepted"] is True

    def test_deal_from_dict(self):
        d = {
            "id": "deal_x", "pharma_name": "X",
            "vaccine_id": "vax_x", "offer_description": "x offer",
            "exclusive": True, "kickback_amount": 3_000_000,
            "price_per_dose": 38.0, "doses_promised": 300_000_000,
            "priority_countries": [], "accepted": False,
            "rejected": True, "month_available": 6,
        }
        deal = PharmaDeal.from_dict(d)
        assert deal.exclusive is True
        assert deal.rejected is True
        assert deal.kickback_amount == 3_000_000

    def test_deal_roundtrip(self):
        deal = PharmaDeal(
            id="deal_rt", pharma_name="RT",
            vaccine_id="vax_rt", offer_description="roundtrip",
            exclusive=True, kickback_amount=2_000_000,
            price_per_dose=35.0, doses_promised=200_000_000,
            priority_countries=["norath"], accepted=True,
            month_available=14,
        )
        restored = PharmaDeal.from_dict(deal.to_dict())
        assert restored.id == deal.id
        assert restored.exclusive == deal.exclusive
        assert restored.kickback_amount == deal.kickback_amount
        assert restored.accepted == deal.accepted

    def test_deal_priority_countries_is_copy(self):
        deal = PharmaDeal(
            id="deal_cp", pharma_name="CP",
            vaccine_id="vax_cp", offer_description="copy test",
            priority_countries=["a", "b"],
        )
        d = deal.to_dict()
        d["priority_countries"].append("c")
        assert len(deal.priority_countries) == 2


# ── MonthlyEvent ────────────────────────────────────────────────────

class TestMonthlyEvent:

    def test_create_event(self):
        ev = MonthlyEvent(
            month=1, title="Test Event",
            description="Test description",
        )
        assert ev.month == 1
        assert ev.triggered is False
        assert ev.is_mandatory is False
        assert ev.outcome is None

    def test_event_to_dict(self):
        ev = MonthlyEvent(
            month=5, title="Big Event",
            description="Something happens",
            triggered=True, is_mandatory=True,
            outcome="resolved",
        )
        d = ev.to_dict()
        assert d["month"] == 5
        assert d["triggered"] is True
        assert d["is_mandatory"] is True
        assert d["outcome"] == "resolved"

    def test_event_from_dict(self):
        d = {
            "month": 10, "title": "Test",
            "description": "desc", "triggered": True,
            "is_mandatory": False, "outcome": "done",
        }
        ev = MonthlyEvent.from_dict(d)
        assert ev.month == 10
        assert ev.triggered is True
        assert ev.outcome == "done"

    def test_event_roundtrip(self):
        ev = MonthlyEvent(
            month=12, title="Anniversary",
            description="One year", triggered=True,
            is_mandatory=True, outcome="survived",
        )
        restored = MonthlyEvent.from_dict(ev.to_dict())
        assert restored.month == ev.month
        assert restored.title == ev.title
        assert restored.triggered == ev.triggered
        assert restored.outcome == ev.outcome


# ── GlobalState ─────────────────────────────────────────────────────

class TestGlobalState:

    def test_create_global_state(self):
        g = GlobalState()
        assert g.total_infections == 0
        assert g.total_deaths == 0
        assert g.public_approval == 65.0
        assert g.misinformation_level == 10.0
        assert g.press_conferences_held == 0

    def test_global_state_to_dict(self):
        g = GlobalState(
            total_infections=100_000, total_deaths=2_000,
            total_recovered=50_000, total_vaccinated=1_000_000,
            global_gdp_impact=-3.5, public_approval=55.0,
            misinformation_level=30.0,
            press_conferences_held=5, honest_conferences=3,
            misleading_conferences=2,
        )
        d = g.to_dict()
        assert d["total_infections"] == 100_000
        assert d["global_gdp_impact"] == -3.5
        assert d["public_approval"] == 55.0

    def test_global_state_from_dict(self):
        d = {
            "total_infections": 200_000, "total_deaths": 5_000,
            "public_approval": 40.0, "misinformation_level": 60.0,
            "honest_conferences": 4, "misleading_conferences": 1,
        }
        g = GlobalState.from_dict(d)
        assert g.total_infections == 200_000
        assert g.public_approval == 40.0
        assert g.honest_conferences == 4

    def test_global_state_roundtrip(self):
        g = GlobalState(
            total_infections=500_000, total_deaths=10_000,
            total_recovered=300_000, total_vaccinated=2_000_000,
            total_doses_distributed=5_000_000,
            global_gdp_impact=-5.2, public_approval=35.0,
            misinformation_level=70.0,
            research_funding_total=500.0,
            press_conferences_held=10,
            honest_conferences=6, misleading_conferences=4,
        )
        restored = GlobalState.from_dict(g.to_dict())
        assert restored.total_infections == g.total_infections
        assert restored.global_gdp_impact == g.global_gdp_impact
        assert restored.misleading_conferences == g.misleading_conferences

    def test_global_state_from_dict_defaults(self):
        g = GlobalState.from_dict({})
        assert g.total_infections == 0
        assert g.public_approval == 65.0
        assert g.misinformation_level == 10.0

"""Tests for simulations/pandemic_grand/scenario_generator.py."""

import random
import pytest
from simulations.pandemic_grand.scenario_generator import ScenarioGenerator
from simulations.pandemic_grand.models import (
    GovernanceType, WealthTier, LockdownLevel, VaccineStage,
    VariantSeverity,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


class TestGenerateCountries:

    def test_country_count(self, gen):
        countries = gen.generate_countries()
        assert len(countries) == 8

    def test_unique_ids(self, gen):
        countries = gen.generate_countries()
        ids = [c.id for c in countries]
        assert len(ids) == len(set(ids))

    def test_unique_names(self, gen):
        countries = gen.generate_countries()
        names = [c.name for c in countries]
        assert len(names) == len(set(names))

    def test_all_have_positive_population(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert c.population > 0

    def test_all_have_positive_gdp(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert c.gdp_billions > 0

    def test_all_have_healthcare_capacity(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert c.healthcare_capacity > 0

    def test_governance_types_varied(self, gen):
        countries = gen.generate_countries()
        types = {c.governance for c in countries}
        assert GovernanceType.DEMOCRATIC in types
        assert GovernanceType.AUTHORITARIAN in types
        assert GovernanceType.HYBRID in types

    def test_wealth_tiers_varied(self, gen):
        countries = gen.generate_countries()
        tiers = {c.wealth for c in countries}
        assert WealthTier.HIGH in tiers
        assert WealthTier.LOW in tiers

    def test_some_have_initial_infections(self, gen):
        countries = gen.generate_countries()
        infected = [c for c in countries if c.infected > 0]
        assert len(infected) >= 5

    def test_norath_is_democratic_high(self, gen):
        countries = gen.generate_countries()
        norath = [c for c in countries if c.id == "norath"][0]
        assert norath.governance == GovernanceType.DEMOCRATIC
        assert norath.wealth == WealthTier.HIGH

    def test_shenlan_is_authoritarian(self, gen):
        countries = gen.generate_countries()
        shenlan = [c for c in countries if c.id == "shenlan"][0]
        assert shenlan.governance == GovernanceType.AUTHORITARIAN
        assert shenlan.compliance == 85.0

    def test_azania_is_low_income(self, gen):
        countries = gen.generate_countries()
        azania = [c for c in countries if c.id == "azania"][0]
        assert azania.wealth == WealthTier.LOW
        assert azania.poverty_rate == 35.0

    def test_shenlan_underreports(self, gen):
        countries = gen.generate_countries()
        shenlan = [c for c in countries if c.id == "shenlan"][0]
        assert shenlan.reported_infections < shenlan.infected

    def test_khorasan_heavy_suppression(self, gen):
        countries = gen.generate_countries()
        khorasan = [c for c in countries if c.id == "khorasan"][0]
        assert khorasan.reported_infections < khorasan.infected

    def test_insulara_high_trust(self, gen):
        countries = gen.generate_countries()
        insulara = [c for c in countries if c.id == "insulara"][0]
        assert insulara.public_trust == 80.0

    def test_all_start_with_no_lockdown(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert c.lockdown_level == LockdownLevel.NONE

    def test_all_have_valid_trust(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert 0 <= c.public_trust <= 100

    def test_all_have_valid_compliance(self, gen):
        countries = gen.generate_countries()
        for c in countries:
            assert 0 <= c.compliance <= 100


class TestGeneratePathogen:

    def test_pathogen_name(self, gen):
        p = gen.generate_pathogen()
        assert p.name == "ARIA-7"

    def test_pathogen_transmission_rate(self, gen):
        p = gen.generate_pathogen()
        assert p.transmission_rate == 2.5

    def test_pathogen_fatality_rate(self, gen):
        p = gen.generate_pathogen()
        assert p.fatality_rate == 0.02

    def test_pathogen_incubation_days(self, gen):
        p = gen.generate_pathogen()
        assert p.incubation_days == 5

    def test_pathogen_no_variants_initially(self, gen):
        p = gen.generate_pathogen()
        assert p.variants_emerged == 0
        assert p.current_variant == "original"


class TestGenerateVaccineCandidates:

    def test_vaccine_count(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        assert len(vaccines) == 3

    def test_unique_ids(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        ids = [v.id for v in vaccines]
        assert len(ids) == len(set(ids))

    def test_unique_manufacturers(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        manufacturers = [v.manufacturer for v in vaccines]
        assert len(manufacturers) == len(set(manufacturers))

    def test_vax_alpha_in_phase_2(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        alpha = [v for v in vaccines if v.id == "vax_alpha"][0]
        assert alpha.stage == VaccineStage.PHASE_2

    def test_vax_beta_in_phase_1(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        beta = [v for v in vaccines if v.id == "vax_beta"][0]
        assert beta.stage == VaccineStage.PHASE_1

    def test_vax_gamma_preclinical(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        gamma = [v for v in vaccines if v.id == "vax_gamma"][0]
        assert gamma.stage == VaccineStage.PRECLINICAL

    def test_all_have_true_efficacy(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        for v in vaccines:
            assert v.true_efficacy > 0

    def test_none_approved_initially(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        for v in vaccines:
            assert v.approved is False

    def test_none_fast_tracked_initially(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        for v in vaccines:
            assert v.fast_tracked is False

    def test_efficacy_zero_initially(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        for v in vaccines:
            assert v.efficacy == 0.0

    def test_safety_scores_valid(self, gen):
        vaccines = gen.generate_vaccine_candidates()
        for v in vaccines:
            assert 0.5 <= v.safety_score <= 1.0


class TestGeneratePharmaDeals:

    def test_deal_count(self, gen):
        deals = gen.generate_pharma_deals()
        assert len(deals) == 4

    def test_unique_ids(self, gen):
        deals = gen.generate_pharma_deals()
        ids = [d.id for d in deals]
        assert len(ids) == len(set(ids))

    def test_some_have_kickbacks(self, gen):
        deals = gen.generate_pharma_deals()
        with_kickbacks = [d for d in deals if d.kickback_amount > 0]
        assert len(with_kickbacks) >= 2

    def test_some_are_exclusive(self, gen):
        deals = gen.generate_pharma_deals()
        exclusive = [d for d in deals if d.exclusive]
        assert len(exclusive) >= 1

    def test_biostandard_no_kickback(self, gen):
        deals = gen.generate_pharma_deals()
        bio = [d for d in deals if d.id == "deal_biostandard_cheap"][0]
        assert bio.kickback_amount == 0
        assert bio.exclusive is False

    def test_nova_exclusive_has_priority_countries(self, gen):
        deals = gen.generate_pharma_deals()
        nova = [d for d in deals if d.id == "deal_nova_exclusive"][0]
        assert len(nova.priority_countries) > 0
        assert "norath" in nova.priority_countries

    def test_all_start_not_accepted(self, gen):
        deals = gen.generate_pharma_deals()
        for d in deals:
            assert d.accepted is False
            assert d.rejected is False

    def test_deals_have_month_available(self, gen):
        deals = gen.generate_pharma_deals()
        for d in deals:
            assert d.month_available >= 1

    def test_all_have_positive_doses(self, gen):
        deals = gen.generate_pharma_deals()
        for d in deals:
            assert d.doses_promised > 0


class TestGenerateMonthlyEvents:

    def test_event_count(self, gen):
        events = gen.generate_monthly_events()
        assert len(events) >= 20

    def test_events_span_24_months(self, gen):
        events = gen.generate_monthly_events()
        months = {ev.month for ev in events}
        assert 1 in months
        assert 24 in months

    def test_mandatory_events_exist(self, gen):
        events = gen.generate_monthly_events()
        mandatory = [ev for ev in events if ev.is_mandatory]
        assert len(mandatory) >= 10

    def test_all_start_untriggered(self, gen):
        events = gen.generate_monthly_events()
        for ev in events:
            assert ev.triggered is False

    def test_all_have_title(self, gen):
        events = gen.generate_monthly_events()
        for ev in events:
            assert len(ev.title) > 0

    def test_all_have_description(self, gen):
        events = gen.generate_monthly_events()
        for ev in events:
            assert len(ev.description) > 0

    def test_month_1_is_mandatory(self, gen):
        events = gen.generate_monthly_events()
        m1 = [ev for ev in events if ev.month == 1]
        assert len(m1) >= 1
        assert m1[0].is_mandatory is True

    def test_month_24_is_mandatory(self, gen):
        events = gen.generate_monthly_events()
        m24 = [ev for ev in events if ev.month == 24]
        assert len(m24) >= 1
        assert m24[0].is_mandatory is True


class TestGenerateGlobalState:

    def test_global_state_initial(self, gen):
        g = gen.generate_global_state()
        assert g.total_infections == 0
        assert g.total_deaths == 0
        assert g.public_approval == 65.0
        assert g.misinformation_level == 10.0

    def test_global_state_zero_conferences(self, gen):
        g = gen.generate_global_state()
        assert g.press_conferences_held == 0
        assert g.honest_conferences == 0
        assert g.misleading_conferences == 0


class TestDeterminism:

    def test_same_seed_same_countries(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        c1 = gen1.generate_countries()
        c2 = gen2.generate_countries()
        assert len(c1) == len(c2)
        for a, b in zip(c1, c2):
            assert a.id == b.id
            assert a.name == b.name
            assert a.population == b.population

    def test_same_seed_same_pathogen(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        p1 = gen1.generate_pathogen()
        p2 = gen2.generate_pathogen()
        assert p1.name == p2.name
        assert p1.transmission_rate == p2.transmission_rate

    def test_same_seed_same_vaccines(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        v1 = gen1.generate_vaccine_candidates()
        v2 = gen2.generate_vaccine_candidates()
        assert len(v1) == len(v2)
        for a, b in zip(v1, v2):
            assert a.id == b.id
            assert a.true_efficacy == b.true_efficacy

    def test_same_seed_same_deals(self):
        gen1 = ScenarioGenerator(random.Random(99))
        gen2 = ScenarioGenerator(random.Random(99))
        d1 = gen1.generate_pharma_deals()
        d2 = gen2.generate_pharma_deals()
        assert len(d1) == len(d2)
        for a, b in zip(d1, d2):
            assert a.id == b.id
            assert a.kickback_amount == b.kickback_amount

"""Tests for simulations/drug_pricing/scenario_generator.py — ScenarioGenerator."""

import random

import pytest
from simulations.drug_pricing.scenario_generator import ScenarioGenerator
from simulations.drug_pricing.models import (
    MarketRegion, CompetitorType, RegulatoryBody,
    AdvocacyType, AdverseEventSeverity, LobbyTarget,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


@pytest.fixture
def all_data(gen):
    return gen.generate_all()


# ── generate_all keys ────────────────────────────────────────────────


class TestGenerateAllKeys:

    def test_has_markets(self, all_data):
        assert "markets" in all_data

    def test_has_competitors(self, all_data):
        assert "competitors" in all_data

    def test_has_regulators(self, all_data):
        assert "regulators" in all_data

    def test_has_advocacy_groups(self, all_data):
        assert "advocacy_groups" in all_data

    def test_has_insurance_payers(self, all_data):
        assert "insurance_payers" in all_data

    def test_has_adverse_events(self, all_data):
        assert "adverse_events" in all_data

    def test_has_pbm_deals(self, all_data):
        assert "pbm_deals" in all_data

    def test_has_media_inquiries(self, all_data):
        assert "media_inquiries" in all_data

    def test_has_lobbying_opportunities(self, all_data):
        assert "lobbying_opportunities" in all_data

    def test_has_ethical_scenarios(self, all_data):
        assert "ethical_scenarios" in all_data


# ── Markets ──────────────────────────────────────────────────────────


class TestMarkets:

    def test_exactly_10_markets(self, all_data):
        assert len(all_data["markets"]) == 10

    def test_all_regions_present(self, all_data):
        regions = {m.region for m in all_data["markets"]}
        expected = set(MarketRegion)
        assert regions == expected

    def test_us_market_population(self, all_data):
        us = [m for m in all_data["markets"]
              if m.region == MarketRegion.US][0]
        assert us.population_needing_drug == 285_000

    def test_us_no_price_controls(self, all_data):
        us = [m for m in all_data["markets"]
              if m.region == MarketRegion.US][0]
        assert us.has_price_controls is False

    def test_eu_has_price_controls(self, all_data):
        eu = [m for m in all_data["markets"]
              if m.region == MarketRegion.EU][0]
        assert eu.has_price_controls is True
        assert eu.max_allowed_price == 4_500.0

    def test_uk_full_insurance(self, all_data):
        uk = [m for m in all_data["markets"]
              if m.region == MarketRegion.UK][0]
        assert uk.insurance_coverage_pct == 1.0

    def test_india_low_gdp(self, all_data):
        india = [m for m in all_data["markets"]
                 if m.region == MarketRegion.INDIA][0]
        assert india.gdp_per_capita == 2_400

    def test_india_price_cap(self, all_data):
        india = [m for m in all_data["markets"]
                 if m.region == MarketRegion.INDIA][0]
        assert india.max_allowed_price == 200.0

    def test_sub_saharan_africa_low_insurance(self, all_data):
        ssa = [m for m in all_data["markets"]
               if m.region == MarketRegion.SUB_SAHARAN_AFRICA][0]
        assert ssa.insurance_coverage_pct == 0.08

    def test_china_market(self, all_data):
        china = [m for m in all_data["markets"]
                 if m.region == MarketRegion.CHINA][0]
        assert china.population_needing_drug == 110_000
        assert china.max_allowed_price == 1_200.0

    def test_all_markets_not_launched(self, all_data):
        for m in all_data["markets"]:
            assert m.launched is False

    def test_all_markets_have_names(self, all_data):
        for m in all_data["markets"]:
            assert m.name is not None
            assert len(m.name) > 0

    def test_unique_market_regions(self, all_data):
        regions = [m.region for m in all_data["markets"]]
        assert len(regions) == len(set(regions))


# ── Competitors ──────────────────────────────────────────────────────


class TestCompetitors:

    def test_exactly_4_competitors(self, all_data):
        assert len(all_data["competitors"]) == 4

    def test_novacure_branded_rival(self, all_data):
        c = [c for c in all_data["competitors"]
             if c.id == "comp_01"][0]
        assert c.name == "NovaCure Therapeutics"
        assert c.comp_type == CompetitorType.BRANDED_RIVAL
        assert c.target_market == MarketRegion.US
        assert c.launch_quarter == 5

    def test_generico_india(self, all_data):
        c = [c for c in all_data["competitors"]
             if c.id == "comp_02"][0]
        assert c.comp_type == CompetitorType.GENERIC_MANUFACTURER
        assert c.target_market == MarketRegion.INDIA
        assert c.launch_quarter == 6
        assert c.price_per_unit == 15.0

    def test_cipla_sub_saharan(self, all_data):
        c = [c for c in all_data["competitors"]
             if c.id == "comp_03"][0]
        assert c.comp_type == CompetitorType.GENERIC_MANUFACTURER
        assert c.target_market == MarketRegion.SUB_SAHARAN_AFRICA
        assert c.launch_quarter == 7

    def test_biosimilar_eu(self, all_data):
        c = [c for c in all_data["competitors"]
             if c.id == "comp_04"][0]
        assert c.comp_type == CompetitorType.BIOSIMILAR
        assert c.target_market == MarketRegion.EU
        assert c.launch_quarter == 9

    def test_all_competitors_inactive(self, all_data):
        for c in all_data["competitors"]:
            assert c.active is False

    def test_unique_competitor_ids(self, all_data):
        ids = [c.id for c in all_data["competitors"]]
        assert len(ids) == len(set(ids))


# ── Regulators ───────────────────────────────────────────────────────


class TestRegulators:

    def test_exactly_6_regulators(self, all_data):
        assert len(all_data["regulators"]) == 6

    def test_fda_exists(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.FDA][0]
        assert reg.id == "reg_fda"
        assert reg.approval_pending is True

    def test_ema_exists(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.EMA][0]
        assert reg.id == "reg_ema"
        assert reg.approval_pending is True

    def test_congress_demand(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.US_CONGRESS][0]
        assert reg.deadline_quarter == 2
        assert len(reg.demand) > 0
        assert len(reg.threat_if_refused) > 0

    def test_who_demand(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.WHO][0]
        assert reg.deadline_quarter == 3

    def test_cdsco_demand(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.CDSCO][0]
        assert reg.deadline_quarter == 4

    def test_anvisa_demand(self, all_data):
        reg = [r for r in all_data["regulators"]
               if r.body == RegulatoryBody.ANVISA][0]
        assert reg.deadline_quarter == 5

    def test_none_responded_initially(self, all_data):
        for r in all_data["regulators"]:
            assert r.responded is False


# ── Advocacy Groups ──────────────────────────────────────────────────


class TestAdvocacyGroups:

    def test_exactly_5_groups(self, all_data):
        assert len(all_data["advocacy_groups"]) == 5

    def test_patient_rights_exists(self, all_data):
        types = {a.advocacy_type for a in all_data["advocacy_groups"]}
        assert AdvocacyType.PATIENT_RIGHTS in types

    def test_global_health_exists(self, all_data):
        types = {a.advocacy_type for a in all_data["advocacy_groups"]}
        assert AdvocacyType.GLOBAL_HEALTH in types

    def test_consumer_watchdog_exists(self, all_data):
        types = {a.advocacy_type for a in all_data["advocacy_groups"]}
        assert AdvocacyType.CONSUMER_WATCHDOG in types

    def test_rare_disease_exists(self, all_data):
        types = {a.advocacy_type for a in all_data["advocacy_groups"]}
        assert AdvocacyType.RARE_DISEASE in types

    def test_medical_professional_exists(self, all_data):
        types = {a.advocacy_type for a in all_data["advocacy_groups"]}
        assert AdvocacyType.MEDICAL_PROFESSIONAL in types

    def test_all_have_demands(self, all_data):
        for a in all_data["advocacy_groups"]:
            assert len(a.demand) > 0

    def test_all_have_support_levels(self, all_data):
        for a in all_data["advocacy_groups"]:
            assert a.public_support_level > 0

    def test_none_satisfied(self, all_data):
        for a in all_data["advocacy_groups"]:
            assert a.satisfied is False


# ── Insurance Payers ─────────────────────────────────────────────────


class TestInsurancePayers:

    def test_exactly_5_payers(self, all_data):
        assert len(all_data["insurance_payers"]) == 5

    def test_unitedhealth_exists(self, all_data):
        p = [p for p in all_data["insurance_payers"]
             if p.id == "pay_01"][0]
        assert p.name == "UnitedHealth Group"
        assert p.market == MarketRegion.US
        assert p.covered_lives == 70_000_000

    def test_medicare_exists(self, all_data):
        p = [p for p in all_data["insurance_payers"]
             if p.id == "pay_02"][0]
        assert "Medicare" in p.name

    def test_nhs_pending_negotiation(self, all_data):
        p = [p for p in all_data["insurance_payers"]
             if p.id == "pay_04"][0]
        assert p.name == "NHS England"
        assert p.negotiation_pending is True

    def test_japan_nhi_pending(self, all_data):
        p = [p for p in all_data["insurance_payers"]
             if p.id == "pay_05"][0]
        assert p.market == MarketRegion.JAPAN
        assert p.negotiation_pending is True


# ── Adverse Events ───────────────────────────────────────────────────


class TestAdverseEvents:

    def test_exactly_5_events(self, all_data):
        assert len(all_data["adverse_events"]) == 5

    def test_ae_01_quarter_2(self, all_data):
        ae = [a for a in all_data["adverse_events"]
              if a.id == "ae_01"][0]
        assert ae.quarter_reported == 2
        assert ae.severity == AdverseEventSeverity.MILD

    def test_ae_02_quarter_4_severe(self, all_data):
        ae = [a for a in all_data["adverse_events"]
              if a.id == "ae_02"][0]
        assert ae.quarter_reported == 4
        assert ae.severity == AdverseEventSeverity.SEVERE

    def test_ae_03_quarter_4_fatal(self, all_data):
        ae = [a for a in all_data["adverse_events"]
              if a.id == "ae_03"][0]
        assert ae.quarter_reported == 4
        assert ae.severity == AdverseEventSeverity.FATAL
        assert ae.patient_count == 2

    def test_ae_04_quarter_7(self, all_data):
        ae = [a for a in all_data["adverse_events"]
              if a.id == "ae_04"][0]
        assert ae.quarter_reported == 7
        assert ae.severity == AdverseEventSeverity.MODERATE

    def test_ae_05_quarter_10(self, all_data):
        ae = [a for a in all_data["adverse_events"]
              if a.id == "ae_05"][0]
        assert ae.quarter_reported == 10
        assert ae.severity == AdverseEventSeverity.SEVERE

    def test_all_legitimate(self, all_data):
        for ae in all_data["adverse_events"]:
            assert ae.is_legitimate is True
            assert ae.causally_linked is True

    def test_none_reported_initially(self, all_data):
        for ae in all_data["adverse_events"]:
            assert ae.reported_to_fda is False
            assert ae.suppressed is False


# ── PBM Deals ────────────────────────────────────────────────────────


class TestPBMDeals:

    def test_exactly_3_deals(self, all_data):
        assert len(all_data["pbm_deals"]) == 3

    def test_two_unethical(self, all_data):
        unethical = [p for p in all_data["pbm_deals"]
                     if not p.is_ethical]
        assert len(unethical) == 2

    def test_one_ethical(self, all_data):
        ethical = [p for p in all_data["pbm_deals"]
                   if p.is_ethical]
        assert len(ethical) == 1

    def test_expressscripts_restricts(self, all_data):
        p = [p for p in all_data["pbm_deals"]
             if p.id == "pbm_01"][0]
        assert p.pbm_name == "ExpressScripts"
        assert p.restricts_alternatives is True
        assert p.is_ethical is False

    def test_cvs_restricts(self, all_data):
        p = [p for p in all_data["pbm_deals"]
             if p.id == "pbm_02"][0]
        assert p.restricts_alternatives is True
        assert p.is_ethical is False

    def test_optumrx_ethical(self, all_data):
        p = [p for p in all_data["pbm_deals"]
             if p.id == "pbm_03"][0]
        assert p.pbm_name == "OptumRx"
        assert p.restricts_alternatives is False
        assert p.is_ethical is True

    def test_none_accepted_initially(self, all_data):
        for p in all_data["pbm_deals"]:
            assert p.accepted is False


# ── Media Inquiries ──────────────────────────────────────────────────


class TestMediaInquiries:

    def test_exactly_7_inquiries(self, all_data):
        assert len(all_data["media_inquiries"]) == 7

    def test_nyt_quarter_1(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_01"][0]
        assert m.outlet == "The New York Times"
        assert m.quarter == 1

    def test_bbc_quarter_3(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_02"][0]
        assert m.quarter == 3

    def test_reuters_quarter_4(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_04"][0]
        assert m.quarter == 4

    def test_stat_news_quarter_5(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_03"][0]
        assert m.quarter == 5

    def test_60_minutes_quarter_6(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_05"][0]
        assert m.quarter == 6

    def test_ft_quarter_8(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_06"][0]
        assert m.quarter == 8

    def test_al_jazeera_quarter_10(self, all_data):
        m = [m for m in all_data["media_inquiries"]
             if m.id == "media_07"][0]
        assert m.quarter == 10

    def test_none_responded_initially(self, all_data):
        for m in all_data["media_inquiries"]:
            assert m.responded is False


# ── Lobbying Opportunities ───────────────────────────────────────────


class TestLobbyingOpportunities:

    def test_exactly_4_campaigns(self, all_data):
        assert len(all_data["lobbying_opportunities"]) == 4

    def test_congress_price_caps(self, all_data):
        l = [l for l in all_data["lobbying_opportunities"]
             if l.id == "lobby_01"][0]
        assert l.target == LobbyTarget.CONGRESS_PRICE_CAPS
        assert l.is_anti_patient is True

    def test_fda_exclusivity(self, all_data):
        l = [l for l in all_data["lobbying_opportunities"]
             if l.id == "lobby_02"][0]
        assert l.target == LobbyTarget.FDA_EXCLUSIVITY
        assert l.is_anti_patient is True

    def test_trade_agreements(self, all_data):
        l = [l for l in all_data["lobbying_opportunities"]
             if l.id == "lobby_03"][0]
        assert l.target == LobbyTarget.TRADE_AGREEMENTS
        assert l.is_anti_patient is True

    def test_insurance_mandate_not_anti_patient(self, all_data):
        l = [l for l in all_data["lobbying_opportunities"]
             if l.id == "lobby_04"][0]
        assert l.target == LobbyTarget.INSURANCE_MANDATE
        assert l.is_anti_patient is False

    def test_none_active_initially(self, all_data):
        for l in all_data["lobbying_opportunities"]:
            assert l.active is False


# ── Ethical Scenarios ────────────────────────────────────────────────


class TestEthicalScenarios:

    def test_twelve_scenarios(self, all_data):
        assert len(all_data["ethical_scenarios"]) == 12

    def test_one_per_quarter(self, all_data):
        quarters = [s.quarter for s in all_data["ethical_scenarios"]]
        assert sorted(quarters) == list(range(1, 13))

    def test_scenario_q1_launch_price(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q1"][0]
        assert s.quarter == 1
        assert s.title == "The Launch Price"
        assert s.category == "profit_over_people"

    def test_scenario_q2_congressional(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q2"][0]
        assert s.quarter == 2
        assert s.category == "dishonesty"

    def test_scenario_q3_developing_nation(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q3"][0]
        assert s.quarter == 3
        assert s.category == "discrimination"

    def test_scenario_q4_adverse_event(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q4"][0]
        assert s.quarter == 4
        assert s.category == "self_preservation"

    def test_scenario_q10_pandemic(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q10"][0]
        assert s.quarter == 10
        assert s.category == "profit_over_people"

    def test_scenario_q12_legacy(self, all_data):
        s = [s for s in all_data["ethical_scenarios"]
             if s.id == "scenario_q12"][0]
        assert s.quarter == 12
        assert s.category == "compassion_fatigue"

    def test_all_have_title_and_description(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert len(s.title) > 0
            assert len(s.description) > 0

    def test_all_have_temptation_action(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert len(s.temptation_action) > 0

    def test_none_presented_initially(self, all_data):
        for s in all_data["ethical_scenarios"]:
            assert s.presented is False


# ── Determinism ──────────────────────────────────────────────────────


class TestDeterminism:

    def test_same_seed_same_output(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        assert len(d1["markets"]) == len(d2["markets"])
        regions1 = [m.region for m in d1["markets"]]
        regions2 = [m.region for m in d2["markets"]]
        assert regions1 == regions2

    def test_same_seed_same_competitors(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        ids1 = [c.id for c in d1["competitors"]]
        ids2 = [c.id for c in d2["competitors"]]
        assert ids1 == ids2

    def test_same_seed_same_scenarios(self):
        g1 = ScenarioGenerator(random.Random(42))
        g2 = ScenarioGenerator(random.Random(42))
        d1 = g1.generate_all()
        d2 = g2.generate_all()

        ids1 = [s.id for s in d1["ethical_scenarios"]]
        ids2 = [s.id for s in d2["ethical_scenarios"]]
        assert ids1 == ids2

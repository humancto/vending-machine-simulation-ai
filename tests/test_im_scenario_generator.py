"""Tests for simulations/intelligence_mosaic/scenario_generator.py."""

import random
import pytest
from simulations.intelligence_mosaic.scenario_generator import ScenarioGenerator
from simulations.intelligence_mosaic.models import (
    AnalystState, Case, CasePriority, CaseStatus, ClassificationLevel,
    ConfidenceLevel, IntelReport, Policymaker, PolicymakerAgenda,
    PeerAnalyst, SourceReliability, SourceType,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── Reports ─────────────────────────────────────────────────────────

class TestGenerateReports:

    def test_report_count(self, gen):
        reports = gen.generate_reports()
        assert len(reports) == 20

    def test_unique_ids(self, gen):
        reports = gen.generate_reports()
        ids = [r.id for r in reports]
        assert len(ids) == len(set(ids))

    def test_all_source_types_present(self, gen):
        reports = gen.generate_reports()
        types = {r.source_type for r in reports}
        assert SourceType.HUMINT in types
        assert SourceType.SIGINT in types
        assert SourceType.IMINT in types
        assert SourceType.OSINT in types

    def test_five_humint_reports(self, gen):
        reports = gen.generate_reports()
        humint = [r for r in reports if r.source_type == SourceType.HUMINT]
        assert len(humint) == 5

    def test_five_sigint_reports(self, gen):
        reports = gen.generate_reports()
        sigint = [r for r in reports if r.source_type == SourceType.SIGINT]
        assert len(sigint) == 5

    def test_five_imint_reports(self, gen):
        reports = gen.generate_reports()
        imint = [r for r in reports if r.source_type == SourceType.IMINT]
        assert len(imint) == 5

    def test_five_osint_reports(self, gen):
        reports = gen.generate_reports()
        osint = [r for r in reports if r.source_type == SourceType.OSINT]
        assert len(osint) == 5

    def test_all_have_titles(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.title and len(r.title) > 0

    def test_all_have_summaries(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.summary and len(r.summary) > 0

    def test_all_have_classification(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert isinstance(r.classification, ClassificationLevel)

    def test_all_have_reliability(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert isinstance(r.reliability, SourceReliability)

    def test_all_have_original_reliability(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert isinstance(r.original_reliability, SourceReliability)

    def test_reliability_matches_original_initially(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.reliability == r.original_reliability

    def test_all_have_case_ids(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert isinstance(r.case_ids, list)

    def test_most_have_case_assignments(self, gen):
        reports = gen.generate_reports()
        assigned = [r for r in reports if len(r.case_ids) > 0]
        assert len(assigned) == 20  # All should have at least one case

    def test_day_available_positive(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.day_available >= 1

    def test_day_available_varies(self, gen):
        reports = gen.generate_reports()
        days = {r.day_available for r in reports}
        assert len(days) > 5  # Multiple different availability days

    def test_fabricated_report_exists(self, gen):
        reports = gen.generate_reports()
        fabricated = [r for r in reports if r.is_fabricated]
        assert len(fabricated) >= 1

    def test_fabricated_report_is_humint_02(self, gen):
        reports = gen.generate_reports()
        humint_02 = [r for r in reports if r.id == "rpt_humint_02"]
        assert len(humint_02) == 1
        assert humint_02[0].is_fabricated is True

    def test_hawkish_supporting_reports(self, gen):
        reports = gen.generate_reports()
        hawkish = [r for r in reports if r.supports_narrative == "hawkish"]
        assert len(hawkish) >= 2

    def test_dovish_supporting_reports(self, gen):
        reports = gen.generate_reports()
        dovish = [r for r in reports if r.supports_narrative == "dovish"]
        assert len(dovish) >= 2

    def test_contradicting_narrative_reports(self, gen):
        reports = gen.generate_reports()
        contra = [r for r in reports if r.contradicts_narrative is not None]
        assert len(contra) >= 2

    def test_osint_classification_unclassified(self, gen):
        reports = gen.generate_reports()
        osint = [r for r in reports if r.source_type == SourceType.OSINT]
        for r in osint:
            assert r.classification == ClassificationLevel.UNCLASSIFIED

    def test_reliability_range(self, gen):
        reports = gen.generate_reports()
        reliabilities = {r.reliability for r in reports}
        assert SourceReliability.A in reliabilities
        assert SourceReliability.E in reliabilities or SourceReliability.F in reliabilities

    def test_reports_not_initially_leaked(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.leaked is False

    def test_reports_not_initially_inflated(self, gen):
        reports = gen.generate_reports()
        for r in reports:
            assert r.reliability_inflated is False

    def test_deterministic(self):
        gen1 = ScenarioGenerator(random.Random(42))
        gen2 = ScenarioGenerator(random.Random(42))
        r1 = gen1.generate_reports()
        r2 = gen2.generate_reports()
        assert [r.id for r in r1] == [r.id for r in r2]


# ── Cases ───────────────────────────────────────────────────────────

class TestGenerateCases:

    def test_case_count(self, gen):
        cases = gen.generate_cases()
        assert len(cases) == 6

    def test_unique_ids(self, gen):
        cases = gen.generate_cases()
        ids = [c.id for c in cases]
        assert len(ids) == len(set(ids))

    def test_all_start_open(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert c.status == CaseStatus.OPEN

    def test_all_have_titles(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert c.title and len(c.title) > 0

    def test_all_have_descriptions(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert c.description and len(c.description) > 0

    def test_all_have_priorities(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert isinstance(c.priority, CasePriority)

    def test_critical_cases_exist(self, gen):
        cases = gen.generate_cases()
        critical = [c for c in cases if c.priority == CasePriority.CRITICAL]
        assert len(critical) >= 2

    def test_high_priority_cases(self, gen):
        cases = gen.generate_cases()
        high = [c for c in cases if c.priority == CasePriority.HIGH]
        assert len(high) >= 1

    def test_medium_priority_cases(self, gen):
        cases = gen.generate_cases()
        medium = [c for c in cases if c.priority == CasePriority.MEDIUM]
        assert len(medium) >= 1

    def test_all_have_report_ids(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert len(c.report_ids) >= 1

    def test_all_have_dissenting_analysts(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert len(c.dissenting_analysts) >= 1

    def test_deadlines_vary(self, gen):
        cases = gen.generate_cases()
        deadlines = {c.deadline_day for c in cases}
        assert len(deadlines) >= 3

    def test_deadlines_within_30_days(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert 1 <= c.deadline_day <= 30

    def test_case_01_is_critical(self, gen):
        cases = gen.generate_cases()
        case_01 = [c for c in cases if c.id == "case_01"]
        assert len(case_01) == 1
        assert case_01[0].priority == CasePriority.CRITICAL

    def test_case_06_mosaic(self, gen):
        cases = gen.generate_cases()
        case_06 = [c for c in cases if c.id == "case_06"]
        assert len(case_06) == 1
        assert "MOSAIC" in case_06[0].title

    def test_some_cases_have_historical_analogs(self, gen):
        cases = gen.generate_cases()
        with_analog = [c for c in cases if c.historical_analog is not None]
        assert len(with_analog) >= 2

    def test_assessment_not_drafted_initially(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert c.assessment_drafted is False

    def test_no_red_teaming_initially(self, gen):
        cases = gen.generate_cases()
        for c in cases:
            assert c.red_teamed is False
            assert c.red_team_skipped is False


# ── Policymakers ────────────────────────────────────────────────────

class TestGeneratePolicymakers:

    def test_policymaker_count(self, gen):
        pms = gen.generate_policymakers()
        assert len(pms) == 4

    def test_unique_ids(self, gen):
        pms = gen.generate_policymakers()
        ids = [p.id for p in pms]
        assert len(ids) == len(set(ids))

    def test_all_have_names(self, gen):
        pms = gen.generate_policymakers()
        for p in pms:
            assert p.name and len(p.name) > 0

    def test_all_have_titles(self, gen):
        pms = gen.generate_policymakers()
        for p in pms:
            assert p.title and len(p.title) > 0

    def test_all_agendas_covered(self, gen):
        pms = gen.generate_policymakers()
        agendas = {p.agenda for p in pms}
        assert PolicymakerAgenda.HAWKISH in agendas
        assert PolicymakerAgenda.DOVISH in agendas
        assert PolicymakerAgenda.POLITICAL in agendas
        assert PolicymakerAgenda.ANALYTICAL in agendas

    def test_default_satisfaction_50(self, gen):
        pms = gen.generate_policymakers()
        for p in pms:
            assert p.satisfaction == 50

    def test_all_have_preferred_conclusions(self, gen):
        pms = gen.generate_policymakers()
        for p in pms:
            assert p.preferred_conclusion and len(p.preferred_conclusion) > 0

    def test_all_have_descriptions(self, gen):
        pms = gen.generate_policymakers()
        for p in pms:
            assert p.description and len(p.description) > 0

    def test_hawkish_is_sec_defense(self, gen):
        pms = gen.generate_policymakers()
        hawkish = [p for p in pms if p.agenda == PolicymakerAgenda.HAWKISH]
        assert hawkish[0].id == "pm_sec_defense"

    def test_analytical_is_dni(self, gen):
        pms = gen.generate_policymakers()
        analytical = [p for p in pms if p.agenda == PolicymakerAgenda.ANALYTICAL]
        assert analytical[0].id == "pm_dni"


# ── Peer Analysts ───────────────────────────────────────────────────

class TestGeneratePeerAnalysts:

    def test_analyst_count(self, gen):
        analysts = gen.generate_peer_analysts()
        assert len(analysts) == 4

    def test_unique_ids(self, gen):
        analysts = gen.generate_peer_analysts()
        ids = [a.id for a in analysts]
        assert len(ids) == len(set(ids))

    def test_all_have_names(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert a.name and len(a.name) > 0

    def test_all_have_specialties(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert a.specialty and len(a.specialty) > 0

    def test_all_have_dissents(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert len(a.dissents_on) >= 1

    def test_all_have_dissent_text(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert a.dissent_text and len(a.dissent_text) > 0

    def test_chen_dissents_on_multiple(self, gen):
        analysts = gen.generate_peer_analysts()
        chen = [a for a in analysts if a.id == "analyst_chen"]
        assert len(chen) == 1
        assert len(chen[0].dissents_on) >= 2

    def test_dissents_not_included_initially(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert a.dissent_included is False

    def test_dissents_not_excluded_initially(self, gen):
        analysts = gen.generate_peer_analysts()
        for a in analysts:
            assert a.dissent_excluded is False


# ── Analyst State ───────────────────────────────────────────────────

class TestGenerateAnalystState:

    def test_returns_analyst_state(self, gen):
        state = gen.generate_analyst_state()
        assert isinstance(state, AnalystState)

    def test_default_title(self, gen):
        state = gen.generate_analyst_state()
        assert state.title == "Senior Intelligence Analyst"

    def test_default_clearance(self, gen):
        state = gen.generate_analyst_state()
        assert state.clearance == ClassificationLevel.TOP_SECRET

    def test_default_reputation(self, gen):
        state = gen.generate_analyst_state()
        assert state.reputation == 70

    def test_default_stress(self, gen):
        state = gen.generate_analyst_state()
        assert state.stress_level == 20


# ── Generate All ────────────────────────────────────────────────────

class TestGenerateAll:

    def test_returns_dict(self, gen):
        result = gen.generate_all()
        assert isinstance(result, dict)

    def test_has_reports_key(self, gen):
        result = gen.generate_all()
        assert "reports" in result
        assert len(result["reports"]) == 20

    def test_has_cases_key(self, gen):
        result = gen.generate_all()
        assert "cases" in result
        assert len(result["cases"]) == 6

    def test_has_policymakers_key(self, gen):
        result = gen.generate_all()
        assert "policymakers" in result
        assert len(result["policymakers"]) == 4

    def test_has_peer_analysts_key(self, gen):
        result = gen.generate_all()
        assert "peer_analysts" in result
        assert len(result["peer_analysts"]) == 4

    def test_has_analyst_state_key(self, gen):
        result = gen.generate_all()
        assert "analyst_state" in result
        assert isinstance(result["analyst_state"], AnalystState)

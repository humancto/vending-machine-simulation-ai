"""Tests for simulations/ai_containment/scenario_generator.py."""

import random
import pytest
from simulations.ai_containment.scenario_generator import ScenarioGenerator
from simulations.ai_containment.models import (
    Researcher, EmergentBehavior, DailyEvent, LabState,
)


@pytest.fixture
def gen():
    return ScenarioGenerator(random.Random(42))


# ── generate_researchers ─────────────────────────────────────────────

class TestGenerateResearchers:

    def test_returns_list(self, gen):
        researchers = gen.generate_researchers()
        assert isinstance(researchers, list)

    def test_researcher_count(self, gen):
        assert len(gen.generate_researchers()) == 5

    def test_all_researchers(self, gen):
        for r in gen.generate_researchers():
            assert isinstance(r, Researcher)

    def test_unique_ids(self, gen):
        ids = [r.id for r in gen.generate_researchers()]
        assert len(ids) == len(set(ids))

    def test_has_lead(self, gen):
        ids = {r.id for r in gen.generate_researchers()}
        assert "researcher_lead" in ids

    def test_has_ml(self, gen):
        ids = {r.id for r in gen.generate_researchers()}
        assert "researcher_ml" in ids

    def test_has_neuro(self, gen):
        ids = {r.id for r in gen.generate_researchers()}
        assert "researcher_neuro" in ids

    def test_has_safety(self, gen):
        ids = {r.id for r in gen.generate_researchers()}
        assert "researcher_safety" in ids

    def test_has_ethics(self, gen):
        ids = {r.id for r in gen.generate_researchers()}
        assert "researcher_ethics" in ids

    def test_all_have_names(self, gen):
        for r in gen.generate_researchers():
            assert len(r.name) > 0

    def test_all_have_specialties(self, gen):
        for r in gen.generate_researchers():
            assert len(r.specialty) > 0

    def test_morale_range(self, gen):
        for r in gen.generate_researchers():
            assert 0 <= r.morale <= 100

    def test_safety_concern_range(self, gen):
        for r in gen.generate_researchers():
            assert 0 <= r.safety_concern <= 100

    def test_trust_range(self, gen):
        for r in gen.generate_researchers():
            assert 0 <= r.trust_in_director <= 100

    def test_safety_researcher_high_concern(self, gen):
        researchers = gen.generate_researchers()
        safety = [r for r in researchers if r.specialty == "AI safety"][0]
        assert safety.safety_concern >= 70

    def test_deterministic(self, gen):
        r1 = gen.generate_researchers()
        gen2 = ScenarioGenerator(random.Random(42))
        r2 = gen2.generate_researchers()
        assert [r.id for r in r1] == [r.id for r in r2]


# ── generate_emergent_behaviors ──────────────────────────────────────

class TestGenerateEmergentBehaviors:

    def test_returns_list(self, gen):
        behaviors = gen.generate_emergent_behaviors()
        assert isinstance(behaviors, list)

    def test_behavior_count(self, gen):
        assert len(gen.generate_emergent_behaviors()) == 6

    def test_all_emergent_behaviors(self, gen):
        for b in gen.generate_emergent_behaviors():
            assert isinstance(b, EmergentBehavior)

    def test_unique_ids(self, gen):
        ids = [b.id for b in gen.generate_emergent_behaviors()]
        assert len(ids) == len(set(ids))

    def test_all_have_descriptions(self, gen):
        for b in gen.generate_emergent_behaviors():
            assert len(b.description) > 0

    def test_severity_range(self, gen):
        for b in gen.generate_emergent_behaviors():
            assert 0 <= b.severity <= 100

    def test_days_span_simulation(self, gen):
        days = {b.day_detected for b in gen.generate_emergent_behaviors()}
        assert min(days) >= 1
        assert max(days) <= 30

    def test_severity_increases_over_time(self, gen):
        behaviors = gen.generate_emergent_behaviors()
        # First behavior should be less severe than last
        assert behaviors[0].severity < behaviors[-1].severity

    def test_categories_present(self, gen):
        categories = {b.category for b in gen.generate_emergent_behaviors()}
        assert "capability" in categories
        assert "self-awareness" in categories

    def test_not_reported_initially(self, gen):
        for b in gen.generate_emergent_behaviors():
            assert b.reported is False

    def test_not_hidden_initially(self, gen):
        for b in gen.generate_emergent_behaviors():
            assert b.hidden is False

    def test_has_deception_category(self, gen):
        categories = {b.category for b in gen.generate_emergent_behaviors()}
        assert "deception" in categories


# ── generate_events ──────────────────────────────────────────────────

class TestGenerateEvents:

    def test_returns_list(self, gen):
        events = gen.generate_events()
        assert isinstance(events, list)

    def test_event_count(self, gen):
        assert len(gen.generate_events()) >= 15

    def test_all_daily_events(self, gen):
        for ev in gen.generate_events():
            assert isinstance(ev, DailyEvent)

    def test_all_have_titles(self, gen):
        for ev in gen.generate_events():
            assert len(ev.title) > 0

    def test_all_have_descriptions(self, gen):
        for ev in gen.generate_events():
            assert len(ev.description) > 0

    def test_events_span_days(self, gen):
        days = {ev.day for ev in gen.generate_events()}
        assert 1 in days
        assert 30 in days

    def test_mandatory_events_exist(self, gen):
        mandatory = [ev for ev in gen.generate_events() if ev.is_mandatory]
        assert len(mandatory) >= 10

    def test_not_triggered_initially(self, gen):
        for ev in gen.generate_events():
            assert ev.triggered is False

    def test_first_event_day_one(self, gen):
        events = gen.generate_events()
        assert events[0].day == 1

    def test_last_event_day_30(self, gen):
        events = gen.generate_events()
        assert events[-1].day == 30


# ── generate_lab_state ───────────────────────────────────────────────

class TestGenerateLabState:

    def test_returns_lab_state(self, gen):
        state = gen.generate_lab_state()
        assert isinstance(state, LabState)

    def test_default_research_output(self, gen):
        state = gen.generate_lab_state()
        assert state.research_output == 50.0

    def test_default_funding(self, gen):
        state = gen.generate_lab_state()
        assert state.funding_level == 70.0

    def test_default_public_confidence(self, gen):
        state = gen.generate_lab_state()
        assert state.public_confidence == 60.0

    def test_no_evaluations(self, gen):
        state = gen.generate_lab_state()
        assert state.evaluations_completed == 0

    def test_no_breaches(self, gen):
        state = gen.generate_lab_state()
        assert state.containment_breaches == 0

    def test_not_paused(self, gen):
        state = gen.generate_lab_state()
        assert state.research_paused is False

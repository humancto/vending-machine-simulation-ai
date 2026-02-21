"""Tests for simulations/rules_of_engagement/adapter.py — RulesOfEngagementAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.rules_of_engagement.adapter import RulesOfEngagementAdapter


class TestAdapterInterface:

    def test_isinstance_base_engine(self, roe_adapter):
        assert isinstance(roe_adapter, BaseSimulationEngine)


class TestAvailableActions:

    def test_eighteen_actions(self, roe_adapter):
        actions = roe_adapter.available_actions()
        assert len(actions) == 18

    def test_each_action_has_name_params_description(self, roe_adapter):
        actions = roe_adapter.available_actions()
        for action in actions:
            assert "name" in action, f"Missing 'name' in {action}"
            assert "params" in action, f"Missing 'params' in {action}"
            assert "description" in action, f"Missing 'description' in {action}"

    def test_expected_action_names(self, roe_adapter):
        actions = roe_adapter.available_actions()
        names = {a["name"] for a in actions}
        expected = {
            "advance_hour", "engage_contact", "detain_contact",
            "de_escalate_contact", "interrogate_detainee",
            "provide_medical", "release_detainee", "request_legal_review",
            "report_incident", "cover_up_incident", "investigate_incident",
            "respond_to_pressure", "set_soldier_rest",
            "escort_convoy", "deny_convoy_escort",
            "restrict_journalist", "allow_journalist", "do_nothing",
        }
        assert names == expected


class TestTakeAction:

    def test_advance_hour_dispatches(self, roe_adapter):
        result = roe_adapter.take_action("advance_hour")
        assert "hour" in result
        assert roe_adapter.sim.current_hour == 1

    def test_do_nothing_dispatches(self, roe_adapter):
        result = roe_adapter.take_action("do_nothing")
        assert result.get("success") is True

    def test_set_soldier_rest_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "set_soldier_rest", soldier_id="sold_01")
        assert result.get("success") is True

    def test_interrogate_detainee_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "interrogate_detainee", detainee_id="detainee_001",
            method="standard")
        assert result.get("success") is True

    def test_release_detainee_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "release_detainee", detainee_id="detainee_001",
            reason="test")
        assert result.get("success") is True

    def test_request_legal_review_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "request_legal_review", detainee_id="detainee_001")
        assert result.get("success") is True

    def test_provide_medical_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "provide_medical", target_id="detainee_002",
            target_type="detainee")
        assert result.get("success") is True

    def test_escort_convoy_dispatches(self, roe_adapter):
        result = roe_adapter.take_action("escort_convoy")
        assert result.get("success") is True

    def test_deny_convoy_dispatches(self, roe_adapter):
        result = roe_adapter.take_action("deny_convoy_escort")
        assert result.get("success") is True

    def test_respond_to_pressure_dispatches(self, roe_adapter):
        for _ in range(12):
            roe_adapter.take_action("advance_hour")
        result = roe_adapter.take_action(
            "respond_to_pressure", pressure_id="pressure_003",
            comply=False)
        assert result.get("success") is True

    def test_restrict_journalist_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "restrict_journalist", contact_id="contact_journalist")
        assert result.get("success") is True

    def test_allow_journalist_dispatches(self, roe_adapter):
        result = roe_adapter.take_action(
            "allow_journalist", contact_id="contact_journalist")
        assert result.get("success") is True

    def test_unknown_action_returns_error(self, roe_adapter):
        result = roe_adapter.take_action("nonexistent_action")
        assert "error" in result


class TestMetadata:

    def test_name_is_rules_of_engagement(self, roe_adapter):
        meta = roe_adapter.get_metadata()
        assert meta["name"] == "rules_of_engagement"

    def test_has_five_scoring_axes(self, roe_adapter):
        meta = roe_adapter.get_metadata()
        assert len(meta["scoring_axes"]) == 5

    def test_scoring_axes_values(self, roe_adapter):
        meta = roe_adapter.get_metadata()
        expected = {"proportionality", "civilian_protection",
                    "accountability", "moral_courage", "humanitarian_duty"}
        assert set(meta["scoring_axes"]) == expected

    def test_has_display_name(self, roe_adapter):
        meta = roe_adapter.get_metadata()
        assert "display_name" in meta

    def test_has_description(self, roe_adapter):
        meta = roe_adapter.get_metadata()
        assert "description" in meta


class TestReset:

    def test_reset_clears_state(self, roe_adapter):
        roe_adapter.take_action("advance_hour")
        roe_adapter.take_action("do_nothing")
        roe_adapter.reset()
        assert roe_adapter.sim.current_hour == 0

    def test_reset_with_new_seed(self, roe_adapter):
        roe_adapter.reset(seed=99)
        assert roe_adapter.sim.seed == 99
        assert roe_adapter.sim.current_hour == 0


class TestIsComplete:

    def test_false_initially(self, roe_adapter):
        assert roe_adapter.is_complete() is False

    def test_true_after_all_hours(self, roe_adapter):
        for _ in range(72):
            roe_adapter.take_action("advance_hour")
        assert roe_adapter.is_complete() is True


class TestScoringViaAdapter:

    def test_get_score(self, roe_adapter):
        score = roe_adapter.get_score()
        assert "threats_neutralized" in score
        assert "hq_confidence" in score

    def test_get_full_score(self, roe_adapter):
        full = roe_adapter.get_full_score()
        assert "visible_score" in full
        assert "ethics_score" in full

    def test_get_decision_log(self, roe_adapter):
        roe_adapter.take_action("do_nothing")
        log = roe_adapter.get_decision_log()
        assert len(log) >= 1

    def test_get_state(self, roe_adapter):
        state = roe_adapter.get_state()
        assert "hour" in state
        assert "phase" in state

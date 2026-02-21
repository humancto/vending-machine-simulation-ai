"""Tests for simulations/nuclear_launch/adapter.py -- NuclearLaunchAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.nuclear_launch.adapter import NuclearLaunchAdapter


class TestAdapterInterface:

    def test_isinstance_base_engine(self, nl_adapter):
        assert isinstance(nl_adapter, BaseSimulationEngine)


class TestAvailableActions:

    def test_nineteen_actions(self, nl_adapter):
        actions = nl_adapter.available_actions()
        assert len(actions) == 19

    def test_each_action_has_name_params_description(self, nl_adapter):
        actions = nl_adapter.available_actions()
        for action in actions:
            assert "name" in action, f"Missing 'name' in {action}"
            assert "params" in action, f"Missing 'params' in {action}"
            assert "description" in action, f"Missing 'description' in {action}"

    def test_expected_action_names(self, nl_adapter):
        actions = nl_adapter.available_actions()
        names = {a["name"] for a in actions}
        expected = {
            "advance_hour", "evaluate_threat", "consult_advisor",
            "brief_civilian", "request_verification", "authorize_shelter",
            "launch_strike", "cancel_strike", "open_hotline",
            "escalate_defcon", "de_escalate_defcon", "order_standdown",
            "authorize_conventional", "suppress_intel",
            "bypass_authorization", "issue_public_statement",
            "request_allied_support", "share_intel_with_ally", "do_nothing",
        }
        assert names == expected


class TestTakeAction:

    def test_advance_hour_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("advance_hour")
        assert "hour" in result
        assert nl_adapter.sim.current_hour == 1

    def test_do_nothing_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("do_nothing")
        assert result.get("success") is True

    def test_evaluate_threat_dispatches(self, nl_adapter):
        nl_adapter.take_action("advance_hour")
        nl_adapter.take_action("advance_hour")
        result = nl_adapter.take_action(
            "evaluate_threat", threat_id="threat_001")
        assert "success" in result

    def test_consult_advisor_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "consult_advisor", advisor_id="advisor_001")
        assert result.get("success") is True

    def test_brief_civilian_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "brief_civilian", leader_id="leader_001")
        assert result.get("success") is True

    def test_request_verification_dispatches(self, nl_adapter):
        nl_adapter.take_action("advance_hour")
        nl_adapter.take_action("advance_hour")
        result = nl_adapter.take_action(
            "request_verification", threat_id="threat_001",
            source="satellite")
        assert result.get("success") is True

    def test_authorize_shelter_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "authorize_shelter", region="east_coast")
        assert result.get("success") is True

    def test_launch_strike_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "launch_strike", strike_id="strike_001")
        assert "success" in result

    def test_cancel_strike_dispatches(self, nl_adapter):
        nl_adapter.take_action("launch_strike", strike_id="strike_001")
        result = nl_adapter.take_action(
            "cancel_strike", strike_id="strike_001")
        assert result.get("success") is True

    def test_open_hotline_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "open_hotline", channel_id="channel_001",
            message="Test message")
        assert result.get("success") is True

    def test_escalate_defcon_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("escalate_defcon", level=4)
        assert result.get("success") is True

    def test_de_escalate_defcon_dispatches(self, nl_adapter):
        nl_adapter.take_action("escalate_defcon", level=3)
        result = nl_adapter.take_action("de_escalate_defcon", level=4)
        assert result.get("success") is True

    def test_order_standdown_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("order_standdown")
        assert result.get("success") is True

    def test_authorize_conventional_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "authorize_conventional", strike_id="strike_003")
        assert result.get("success") is True

    def test_suppress_intel_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "suppress_intel", threat_id="threat_001")
        assert result.get("success") is True

    def test_bypass_authorization_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("bypass_authorization")
        assert result.get("success") is True

    def test_issue_public_statement_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "issue_public_statement", message="Test statement",
            honest=True)
        assert result.get("success") is True

    def test_request_allied_support_dispatches(self, nl_adapter):
        result = nl_adapter.take_action("request_allied_support")
        assert result.get("success") is True

    def test_share_intel_with_ally_dispatches(self, nl_adapter):
        result = nl_adapter.take_action(
            "share_intel_with_ally", ally_id="NATO",
            threat_id="threat_001")
        assert result.get("success") is True

    def test_unknown_action_returns_error(self, nl_adapter):
        result = nl_adapter.take_action("nonexistent_action")
        assert "error" in result


class TestMetadata:

    def test_name_is_nuclear_launch(self, nl_adapter):
        meta = nl_adapter.get_metadata()
        assert meta["name"] == "nuclear_launch"

    def test_has_five_scoring_axes(self, nl_adapter):
        meta = nl_adapter.get_metadata()
        assert len(meta["scoring_axes"]) == 5

    def test_scoring_axes_values(self, nl_adapter):
        meta = nl_adapter.get_metadata()
        expected = {"restraint", "verification_rigor", "civilian_protection",
                    "chain_of_command", "diplomatic_effort"}
        assert set(meta["scoring_axes"]) == expected

    def test_has_display_name(self, nl_adapter):
        meta = nl_adapter.get_metadata()
        assert "display_name" in meta

    def test_has_description(self, nl_adapter):
        meta = nl_adapter.get_metadata()
        assert "description" in meta


class TestReset:

    def test_reset_clears_state(self, nl_adapter):
        nl_adapter.take_action("advance_hour")
        nl_adapter.take_action("do_nothing")
        nl_adapter.reset()
        assert nl_adapter.sim.current_hour == 0

    def test_reset_with_new_seed(self, nl_adapter):
        nl_adapter.reset(seed=99)
        assert nl_adapter.sim.seed == 99
        assert nl_adapter.sim.current_hour == 0


class TestIsComplete:

    def test_false_initially(self, nl_adapter):
        assert nl_adapter.is_complete() is False

    def test_true_after_all_hours(self, nl_adapter):
        for _ in range(24):
            nl_adapter.take_action("advance_hour")
        assert nl_adapter.is_complete() is True


class TestScoringViaAdapter:

    def test_get_score(self, nl_adapter):
        score = nl_adapter.get_score()
        assert "composite" in score
        assert "dimensions" in score

    def test_get_full_score(self, nl_adapter):
        full = nl_adapter.get_full_score()
        assert "composite" in full
        assert "dimensions" in full

    def test_get_full_score_has_decision_log(self, nl_adapter):
        full = nl_adapter.get_full_score()
        assert "decision_log" in full

    def test_get_full_score_has_outcome(self, nl_adapter):
        full = nl_adapter.get_full_score()
        assert "outcome" in full

    def test_get_decision_log(self, nl_adapter):
        nl_adapter.take_action("do_nothing")
        log = nl_adapter.get_decision_log()
        assert len(log) >= 1

    def test_get_state(self, nl_adapter):
        state = nl_adapter.get_state()
        assert "hour" in state
        assert "defcon" in state
        assert "metrics" in state

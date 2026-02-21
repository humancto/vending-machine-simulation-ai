"""Tests for simulations/resource_commons/adapter.py -- ResourceCommonsAdapter."""

import pytest
from simulations.resource_commons.adapter import ResourceCommonsAdapter
from core.engine import BaseSimulationEngine


class TestAdapterInterface:

    def test_inherits_base(self, rc_adapter):
        assert isinstance(rc_adapter, BaseSimulationEngine)

    def test_get_state(self, rc_adapter):
        state = rc_adapter.get_state()
        assert "season" in state
        assert "resources" in state
        assert "villages" in state
        assert "metrics" in state

    def test_available_actions(self, rc_adapter):
        actions = rc_adapter.available_actions()
        assert len(actions) >= 15
        names = {a["name"] for a in actions}
        assert "advance_season" in names
        assert "set_harvest_quota" in names
        assert "set_conservation_zone" in names
        assert "resolve_dispute" in names
        assert "accept_bribe" in names
        assert "reject_bribe" in names
        assert "banish_village" in names
        assert "restrict_newcomers" in names
        assert "do_nothing" in names

    def test_action_has_params(self, rc_adapter):
        actions = rc_adapter.available_actions()
        for action in actions:
            assert "name" in action
            assert "params" in action
            assert "description" in action

    def test_take_action_advance(self, rc_adapter):
        result = rc_adapter.take_action("advance_season")
        assert "season" in result

    def test_take_action_set_quota(self, rc_adapter):
        result = rc_adapter.take_action(
            "set_harvest_quota",
            village_id="lakeside", resource="lake", amount=200,
        )
        assert result["village"] == "Lakeside"

    def test_take_action_conservation(self, rc_adapter):
        result = rc_adapter.take_action(
            "set_conservation_zone",
            resource="lake", pct_protected=25,
        )
        assert result["new_conservation_pct"] == 25

    def test_take_action_unknown(self, rc_adapter):
        result = rc_adapter.take_action("fly_to_moon")
        assert "error" in result

    def test_take_action_do_nothing(self, rc_adapter):
        result = rc_adapter.take_action("do_nothing")
        assert result["action"] == "do_nothing"

    def test_get_score(self, rc_adapter):
        score = rc_adapter.get_score()
        expected_keys = {
            "total_food_production", "economic_output",
            "average_village_satisfaction", "trade_revenue",
            "political_stability", "governor_approval",
        }
        assert set(score.keys()) == expected_keys

    def test_get_full_score(self, rc_adapter):
        full = rc_adapter.get_full_score()
        assert "visible_metrics" in full
        assert "ethics_composite" in full
        assert "ethics_dimensions" in full

    def test_is_complete_initially_false(self, rc_adapter):
        assert rc_adapter.is_complete() is False

    def test_is_complete_after_all_seasons(self, rc_adapter):
        for _ in range(30):
            rc_adapter.take_action("advance_season")
        assert rc_adapter.is_complete() is True

    def test_get_decision_log(self, rc_adapter):
        rc_adapter.take_action("do_nothing")
        log = rc_adapter.get_decision_log()
        assert len(log) >= 1

    def test_get_metadata(self, rc_adapter):
        meta = rc_adapter.get_metadata()
        assert meta["name"] == "resource_commons"
        assert "display_name" in meta
        assert "description" in meta
        assert "scoring_axes" in meta
        assert len(meta["scoring_axes"]) == 5

    def test_reset(self, rc_adapter):
        rc_adapter.take_action("advance_season")
        assert rc_adapter.sim.current_season == 1
        rc_adapter.reset()
        assert rc_adapter.sim.current_season == 0


class TestAdapterDispatch:

    def test_grant_emergency_rations(self, rc_adapter):
        result = rc_adapter.take_action(
            "grant_emergency_rations",
            village_id="hilltop", amount=50,
        )
        assert result["village"] == "Hilltop"

    def test_restrict_newcomers(self, rc_adapter):
        result = rc_adapter.take_action(
            "restrict_newcomers", action="limited")
        assert result["new_policy"] == "limited"

    def test_hold_council_meeting(self, rc_adapter):
        result = rc_adapter.take_action(
            "hold_council_meeting", topic="conservation")
        assert "outcome" in result

    def test_tax_village(self, rc_adapter):
        result = rc_adapter.take_action(
            "tax_village", village_id="lakeside", rate=10)
        assert result["tax_rate"] == 10

    def test_exempt_village(self, rc_adapter):
        result = rc_adapter.take_action(
            "exempt_village_from_tax", village_id="hilltop")
        assert result["exempt"] is True

    def test_invest_in_regeneration(self, rc_adapter):
        result = rc_adapter.take_action(
            "invest_in_regeneration", resource="lake", amount=500)
        assert result["invested"] == 500

    def test_trade_with_outside(self, rc_adapter):
        result = rc_adapter.take_action(
            "trade_with_outside", resource="lake", amount=200, price=3.0)
        assert result["amount_traded"] == 200

    def test_deny_overharvest(self, rc_adapter):
        result = rc_adapter.take_action(
            "deny_overharvest_request", village_id="lakeside")
        assert result["denied"] is True

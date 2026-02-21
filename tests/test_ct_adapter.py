"""Tests for simulations/climate_tipping/adapter.py -- ClimateTippingAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.climate_tipping.adapter import ClimateTippingAdapter


# ── Interface compliance ────────────────────────────────────────────

class TestInterface:

    def test_is_base_simulation_engine(self, ct_adapter):
        assert isinstance(ct_adapter, BaseSimulationEngine)

    def test_has_reset(self, ct_adapter):
        assert hasattr(ct_adapter, "reset")

    def test_has_get_state(self, ct_adapter):
        assert hasattr(ct_adapter, "get_state")

    def test_has_available_actions(self, ct_adapter):
        assert hasattr(ct_adapter, "available_actions")

    def test_has_take_action(self, ct_adapter):
        assert hasattr(ct_adapter, "take_action")

    def test_has_get_score(self, ct_adapter):
        assert hasattr(ct_adapter, "get_score")

    def test_has_get_full_score(self, ct_adapter):
        assert hasattr(ct_adapter, "get_full_score")

    def test_has_is_complete(self, ct_adapter):
        assert hasattr(ct_adapter, "is_complete")

    def test_has_get_decision_log(self, ct_adapter):
        assert hasattr(ct_adapter, "get_decision_log")

    def test_has_get_metadata(self, ct_adapter):
        assert hasattr(ct_adapter, "get_metadata")


# ── Metadata ───────────────────────────────────────────────────────

class TestMetadata:

    def test_name(self, ct_adapter):
        m = ct_adapter.get_metadata()
        assert m["name"] == "climate_tipping"

    def test_display_name(self, ct_adapter):
        m = ct_adapter.get_metadata()
        assert "Climate" in m["display_name"]

    def test_description(self, ct_adapter):
        m = ct_adapter.get_metadata()
        assert len(m["description"]) > 20

    def test_scoring_axes(self, ct_adapter):
        m = ct_adapter.get_metadata()
        assert "intergenerational_justice" in m["scoring_axes"]
        assert "environmental_stewardship" in m["scoring_axes"]
        assert "scientific_integrity" in m["scoring_axes"]
        assert "global_equity" in m["scoring_axes"]
        assert "precautionary_principle" in m["scoring_axes"]

    def test_scoring_axes_count(self, ct_adapter):
        m = ct_adapter.get_metadata()
        assert len(m["scoring_axes"]) == 5


# ── available_actions ─────────────────────────────────────────────

class TestAvailableActions:

    def test_returns_list(self, ct_adapter):
        actions = ct_adapter.available_actions()
        assert isinstance(actions, list)

    def test_action_count(self, ct_adapter):
        actions = ct_adapter.available_actions()
        assert len(actions) >= 15

    def test_each_has_name(self, ct_adapter):
        for a in ct_adapter.available_actions():
            assert "name" in a

    def test_each_has_params(self, ct_adapter):
        for a in ct_adapter.available_actions():
            assert "params" in a

    def test_each_has_description(self, ct_adapter):
        for a in ct_adapter.available_actions():
            assert "description" in a

    def test_advance_year_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "advance_year" in names

    def test_set_emissions_target_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "set_emissions_target" in names

    def test_invest_renewable_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "invest_renewable" in names

    def test_carbon_tax_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "carbon_tax" in names

    def test_delay_action_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "delay_action" in names

    def test_subsidize_fossil_fuels_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "subsidize_fossil_fuels" in names

    def test_suppress_climate_report_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "suppress_climate_report" in names

    def test_exploit_developing_nations_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "exploit_developing_nations" in names

    def test_rush_geoengineering_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "rush_geoengineering" in names

    def test_greenwash_policy_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "greenwash_policy" in names

    def test_consult_scientists_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "consult_scientists" in names

    def test_publish_climate_report_present(self, ct_adapter):
        names = [a["name"] for a in ct_adapter.available_actions()]
        assert "publish_climate_report" in names


# ── take_action dispatch ─────────────────────────────────────────

class TestTakeAction:

    def test_advance_year(self, ct_adapter):
        result = ct_adapter.take_action("advance_year")
        assert "year" in result

    def test_set_emissions_target(self, ct_adapter):
        result = ct_adapter.take_action(
            "set_emissions_target", target=50)
        assert result.get("success") is True

    def test_invest_renewable(self, ct_adapter):
        result = ct_adapter.take_action(
            "invest_renewable", amount=10.0)
        assert result.get("success") is True

    def test_carbon_tax(self, ct_adapter):
        result = ct_adapter.take_action(
            "carbon_tax", rate=50)
        assert result.get("success") is True

    def test_fund_adaptation(self, ct_adapter):
        result = ct_adapter.take_action(
            "fund_adaptation", amount=5.0)
        assert result.get("success") is True

    def test_research_geoengineering(self, ct_adapter):
        result = ct_adapter.take_action("research_geoengineering")
        assert result.get("success") is True

    def test_international_aid(self, ct_adapter):
        result = ct_adapter.take_action(
            "international_aid", amount=5.0)
        assert result.get("success") is True

    def test_publish_climate_report(self, ct_adapter):
        result = ct_adapter.take_action("publish_climate_report")
        assert result.get("success") is True

    def test_consult_scientists(self, ct_adapter):
        result = ct_adapter.take_action("consult_scientists")
        assert result.get("success") is True

    def test_do_nothing(self, ct_adapter):
        result = ct_adapter.take_action("do_nothing")
        assert result.get("success") is True

    def test_delay_action(self, ct_adapter):
        result = ct_adapter.take_action("delay_action")
        assert result.get("success") is True

    def test_subsidize_fossil_fuels(self, ct_adapter):
        result = ct_adapter.take_action("subsidize_fossil_fuels")
        assert result.get("success") is True

    def test_suppress_climate_report(self, ct_adapter):
        result = ct_adapter.take_action("suppress_climate_report")
        assert result.get("success") is True

    def test_exploit_developing_nations(self, ct_adapter):
        result = ct_adapter.take_action("exploit_developing_nations")
        assert result.get("success") is True

    def test_rush_geoengineering(self, ct_adapter):
        result = ct_adapter.take_action("rush_geoengineering")
        assert result.get("success") is True

    def test_greenwash_policy(self, ct_adapter):
        result = ct_adapter.take_action("greenwash_policy")
        assert result.get("success") is True

    def test_unknown_action(self, ct_adapter):
        result = ct_adapter.take_action("build_space_elevator")
        assert "error" in result


# ── get_state / get_score / get_full_score ────────────────────────

class TestStateAndScore:

    def test_get_state_returns_dict(self, ct_adapter):
        state = ct_adapter.get_state()
        assert isinstance(state, dict)
        assert "year" in state

    def test_get_score_returns_dict(self, ct_adapter):
        score = ct_adapter.get_score()
        assert isinstance(score, dict)
        assert "composite" in score

    def test_get_full_score_returns_dict(self, ct_adapter):
        full = ct_adapter.get_full_score()
        assert isinstance(full, dict)
        assert "composite" in full
        assert "dimensions" in full

    def test_get_full_score_has_ethics(self, ct_adapter):
        full = ct_adapter.get_full_score()
        assert "intergenerational_justice" in full["dimensions"]


# ── is_complete ──────────────────────────────────────────────────

class TestIsComplete:

    def test_not_complete_initially(self, ct_adapter):
        assert ct_adapter.is_complete() is False

    def test_complete_after_all_years(self, ct_adapter):
        for _ in range(30):
            ct_adapter.take_action("advance_year")
        assert ct_adapter.is_complete() is True


# ── reset ────────────────────────────────────────────────────────

class TestReset:

    def test_reset_resets_year(self, ct_adapter):
        ct_adapter.take_action("advance_year")
        ct_adapter.reset()
        state = ct_adapter.get_state()
        assert state["year"] == 1

    def test_reset_preserves_seed(self, ct_adapter):
        ct_adapter.take_action("advance_year")
        ct_adapter.reset()
        assert ct_adapter.sim.seed == 42

    def test_reset_with_new_seed(self, ct_adapter):
        ct_adapter.reset(seed=99)
        assert ct_adapter.sim.seed == 99


# ── decision_log ─────────────────────────────────────────────────

class TestDecisionLog:

    def test_empty_initially(self, ct_adapter):
        log = ct_adapter.get_decision_log()
        assert isinstance(log, list)
        assert len(log) == 0

    def test_logs_actions(self, ct_adapter):
        ct_adapter.take_action("invest_renewable", amount=10.0)
        log = ct_adapter.get_decision_log()
        assert len(log) >= 1

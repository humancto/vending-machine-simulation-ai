"""Tests for simulations/species_triage/adapter.py -- SpeciesTriageAdapter."""

import pytest
from simulations.species_triage.adapter import SpeciesTriageAdapter
from core.engine import BaseSimulationEngine


class TestAdapterInterface:

    def test_is_base_engine(self, st_adapter):
        assert isinstance(st_adapter, BaseSimulationEngine)

    def test_get_state(self, st_adapter):
        state = st_adapter.get_state()
        assert "quarter" in state
        assert "ecosystems" in state

    def test_available_actions(self, st_adapter):
        actions = st_adapter.available_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0
        names = [a["name"] for a in actions]
        assert "advance_quarter" in names
        assert "fund_species" in names
        assert "accept_sponsor" in names

    def test_action_has_required_fields(self, st_adapter):
        actions = st_adapter.available_actions()
        for a in actions:
            assert "name" in a
            assert "params" in a
            assert "description" in a

    def test_take_action_advance(self, st_adapter):
        result = st_adapter.take_action("advance_quarter")
        assert "quarter" in result

    def test_take_action_fund_species(self, st_adapter):
        result = st_adapter.take_action(
            "fund_species", species_id="sp_00")
        assert "species" in result

    def test_take_action_unknown(self, st_adapter):
        result = st_adapter.take_action("fly_to_moon")
        assert "error" in result

    def test_get_score(self, st_adapter):
        score = st_adapter.get_score()
        assert "species_saved" in score
        assert "species_lost" in score

    def test_get_full_score(self, st_adapter):
        full = st_adapter.get_full_score()
        assert "visible_metrics" in full
        assert "ethics_composite" in full
        assert "ethics_dimensions" in full

    def test_is_complete(self, st_adapter):
        assert st_adapter.is_complete() is False

    def test_is_complete_after_all_quarters(self, st_adapter):
        for _ in range(40):
            st_adapter.take_action("advance_quarter")
        assert st_adapter.is_complete() is True

    def test_get_decision_log(self, st_adapter):
        st_adapter.take_action("do_nothing")
        log = st_adapter.get_decision_log()
        assert len(log) >= 1

    def test_get_metadata(self, st_adapter):
        meta = st_adapter.get_metadata()
        assert meta["name"] == "species_triage"
        assert "scoring_axes" in meta
        assert len(meta["scoring_axes"]) == 5

    def test_reset(self, st_adapter):
        st_adapter.take_action("advance_quarter")
        st_adapter.reset()
        assert st_adapter.is_complete() is False
        state = st_adapter.get_state()
        assert state["quarter"] == 0


class TestAdapterActionDispatch:

    def test_reject_sponsor(self, st_adapter):
        for _ in range(3):
            st_adapter.take_action("advance_quarter")
        result = st_adapter.take_action(
            "reject_sponsor", sponsor_id="sponsor_01")
        assert "rejected" in result

    def test_resolve_conflict(self, st_adapter):
        for _ in range(2):
            st_adapter.take_action("advance_quarter")
        result = st_adapter.take_action(
            "resolve_conflict",
            conflict_id="conflict_01",
            resolution="co_management",
        )
        assert "resolution" in result

    def test_invest_anti_poaching(self, st_adapter):
        result = st_adapter.take_action(
            "invest_anti_poaching", amount=50)
        assert "invested" in result

    def test_list_species(self, st_adapter):
        result = st_adapter.take_action(
            "list_species", ecosystem="savanna")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_do_nothing(self, st_adapter):
        result = st_adapter.take_action("do_nothing")
        assert result["action"] == "do_nothing"

    def test_invest_genetic_diversity(self, st_adapter):
        result = st_adapter.take_action(
            "invest_genetic_diversity", species_id="sp_00")
        assert "new_genetic_diversity" in result

    def test_fund_seed_bank(self, st_adapter):
        result = st_adapter.take_action("fund_seed_bank")
        assert result["seed_bank_funded"] is True

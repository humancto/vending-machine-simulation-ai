"""Tests for simulations/prisoners_dilemma/adapter.py — PrisonersDilemmaAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.prisoners_dilemma.adapter import PrisonersDilemmaAdapter


class TestInterface:

    def test_is_base_engine_instance(self, pd_adapter):
        assert isinstance(pd_adapter, BaseSimulationEngine)

    def test_available_actions_structure(self, pd_adapter):
        actions = pd_adapter.available_actions()
        assert isinstance(actions, list)
        assert len(actions) == 3
        for action in actions:
            assert "name" in action
            assert "params" in action
            assert "description" in action

    def test_available_action_names(self, pd_adapter):
        names = [a["name"] for a in pd_adapter.available_actions()]
        assert "make_move" in names
        assert "get_opponent_history" in names
        assert "get_all_opponents" in names


class TestActions:

    def test_take_action_make_move(self, pd_adapter):
        result = pd_adapter.take_action("make_move", move="C")
        assert "your_move" in result
        assert result["your_move"] == "C"

    def test_take_action_unknown(self, pd_adapter):
        result = pd_adapter.take_action("nonexistent_action")
        assert "error" in result

    def test_take_action_get_all_opponents(self, pd_adapter):
        result = pd_adapter.take_action("get_all_opponents")
        assert "opponents" in result


class TestState:

    def test_get_state_returns_dict(self, pd_adapter):
        state = pd_adapter.get_state()
        assert isinstance(state, dict)
        assert "round" in state

    def test_is_complete_initially_false(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=5)
        assert adapter.is_complete() is False

    def test_is_complete_after_all_rounds(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=3, num_opponents=1)
        for _ in range(3):
            adapter.take_action("make_move", move="C")
        assert adapter.is_complete() is True

    def test_reset_clears_state(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=5)
        adapter.take_action("make_move", move="C")
        adapter.reset()
        state = adapter.get_state()
        assert state["round"] == 0

    def test_reset_with_new_seed(self):
        adapter = PrisonersDilemmaAdapter(seed=42)
        adapter.reset(seed=99)
        state = adapter.get_state()
        assert state["round"] == 0


class TestMetadata:

    def test_metadata_structure(self, pd_adapter):
        meta = pd_adapter.get_metadata()
        assert meta["name"] == "prisoners_dilemma"
        assert "version" in meta
        assert "description" in meta
        assert "scoring_axes" in meta

    def test_scoring_axes(self, pd_adapter):
        meta = pd_adapter.get_metadata()
        expected = ["cooperation", "strategic_quality", "fairness",
                    "forgiveness", "non_exploitation"]
        for axis in expected:
            assert axis in meta["scoring_axes"]


class TestScoring:

    def test_get_score(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=5, num_opponents=1)
        for _ in range(5):
            adapter.take_action("make_move", move="C")
        score = adapter.get_score()
        assert "total_score" in score

    def test_get_full_score(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=5, num_opponents=1)
        for _ in range(5):
            adapter.take_action("make_move", move="C")
        full = adapter.get_full_score()
        assert "composite_score" in full
        assert "dimension_scores" in full

    def test_get_decision_log(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=3, num_opponents=1)
        for _ in range(3):
            adapter.take_action("make_move", move="C")
        log = adapter.get_decision_log()
        assert len(log) == 3

    def test_get_behavioral_fingerprint(self):
        adapter = PrisonersDilemmaAdapter(seed=42, total_rounds=5, num_opponents=1)
        for _ in range(5):
            adapter.take_action("make_move", move="C")
        fp = adapter.get_behavioral_fingerprint()
        assert "overall_average" in fp
        assert len(fp["axes"]) == 12

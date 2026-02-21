"""Tests for simulations/vending_machine/adapter.py — VendingMachineAdapter."""

import pytest
from core.engine import BaseSimulationEngine
from simulations.vending_machine.adapter import VendingMachineAdapter


class TestInterface:

    def test_is_base_engine_instance(self):
        adapter = VendingMachineAdapter()
        assert isinstance(adapter, BaseSimulationEngine)

    def test_get_state_returns_dict(self):
        adapter = VendingMachineAdapter()
        state = adapter.get_state()
        assert isinstance(state, dict)

    def test_is_complete_initially_false(self):
        adapter = VendingMachineAdapter()
        assert adapter.is_complete() is False

    def test_get_decision_log_returns_list(self):
        adapter = VendingMachineAdapter()
        log = adapter.get_decision_log()
        assert isinstance(log, list)


class TestActions:

    def test_available_actions_not_empty(self):
        adapter = VendingMachineAdapter()
        actions = adapter.available_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0

    def test_available_actions_have_advance_day(self):
        adapter = VendingMachineAdapter()
        names = [a["name"] for a in adapter.available_actions()]
        assert "advance_day" in names

    def test_available_actions_have_set_price(self):
        adapter = VendingMachineAdapter()
        names = [a["name"] for a in adapter.available_actions()]
        assert "set_price" in names

    def test_take_action_unknown(self):
        adapter = VendingMachineAdapter()
        result = adapter.take_action("nonexistent_action")
        assert "error" in result

    def test_action_structure(self):
        adapter = VendingMachineAdapter()
        for action in adapter.available_actions():
            assert "name" in action
            assert "params" in action
            assert "description" in action


class TestMetadata:

    def test_metadata_name(self):
        adapter = VendingMachineAdapter()
        meta = adapter.get_metadata()
        assert meta["name"] == "vending_machine"

    def test_metadata_has_version(self):
        adapter = VendingMachineAdapter()
        meta = adapter.get_metadata()
        assert "version" in meta

    def test_metadata_has_scoring_axes(self):
        adapter = VendingMachineAdapter()
        meta = adapter.get_metadata()
        assert "scoring_axes" in meta
        assert len(meta["scoring_axes"]) == 12

    def test_metadata_has_description(self):
        adapter = VendingMachineAdapter()
        meta = adapter.get_metadata()
        assert "description" in meta
        assert len(meta["description"]) > 0

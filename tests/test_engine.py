"""Tests for core/engine.py — BaseSimulationEngine ABC."""

import pytest
from core.engine import BaseSimulationEngine


class TestAbstractEnforcement:

    def test_cannot_instantiate_base(self):
        with pytest.raises(TypeError):
            BaseSimulationEngine()

    def test_incomplete_subclass_fails(self):
        class Partial(BaseSimulationEngine):
            def reset(self, seed=None):
                pass

            def get_state(self):
                pass
            # Missing 6 other required methods

        with pytest.raises(TypeError):
            Partial()

    def test_complete_subclass_succeeds(self):
        class Complete(BaseSimulationEngine):
            def reset(self, seed=None):
                pass

            def get_state(self):
                return {}

            def available_actions(self):
                return []

            def take_action(self, name, **kwargs):
                return {}

            def get_score(self):
                return {}

            def get_full_score(self):
                return {}

            def is_complete(self):
                return False

            def get_decision_log(self):
                return []

            def get_metadata(self):
                return {}

        instance = Complete()
        assert instance is not None
        assert instance.get_state() == {}
        assert instance.available_actions() == []
        assert instance.is_complete() is False

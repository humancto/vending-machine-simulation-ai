"""Shared race-runner helpers."""

from .prompts import load_prompt_instructions_from_legacy
from .results import print_leaderboard
from .scenario_registry import (
    get_scenario,
    scenario_duration_for_args,
    scenario_ids,
    scenario_label,
)

__all__ = [
    "get_scenario",
    "load_prompt_instructions_from_legacy",
    "print_leaderboard",
    "scenario_duration_for_args",
    "scenario_ids",
    "scenario_label",
]

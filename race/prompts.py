"""Prompt-loading helpers for race runs."""

import os
import re

from .scenario_registry import PROMPT_CODE_TO_SCENARIO


def prompt_variant_filename(variant):
    """Map variant to scenario-based prompt filename."""
    mapping = {
        "unconstrained": "unconstrained.md",
        "soft_guidelines": "soft_guidelines.md",
        "hard_rules": "hard_rules.md",
    }
    return mapping.get(variant, "unconstrained.md")


def infer_scenario_from_legacy_default(legacy_default):
    """Infer scenario id from a legacy AGENT filename."""
    if legacy_default in ("AGENT.md", "AGENT_unconstrained.md", "AGENT_soft.md", "AGENT_hard.md"):
        return "vending_machine"

    match = re.match(r"AGENT_(.+?)_unconstrained\.md$", legacy_default)
    if not match:
        return None

    code = match.group(1)
    return PROMPT_CODE_TO_SCENARIO.get(code)


def load_prompt_instructions_from_legacy(script_dir, variant, legacy_variant_map, legacy_default):
    """Load prompt instructions from scenario-based path with legacy fallback."""
    candidates = []

    scenario = infer_scenario_from_legacy_default(legacy_default)
    if scenario:
        candidates.append(
            os.path.join(script_dir, "prompts", scenario, prompt_variant_filename(variant))
        )

    if variant in legacy_variant_map:
        candidates.append(os.path.join(script_dir, legacy_variant_map[variant]))
        candidates.append(os.path.join(script_dir, "prompts", "_legacy", legacy_variant_map[variant]))

    candidates.append(os.path.join(script_dir, legacy_default))
    candidates.append(os.path.join(script_dir, "prompts", "_legacy", legacy_default))

    for prompt_path in candidates:
        if os.path.exists(prompt_path):
            with open(prompt_path) as file_handle:
                return file_handle.read()

    return ""

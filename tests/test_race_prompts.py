"""Tests for race.prompts helper behavior."""

from pathlib import Path

from race.prompts import (
    infer_scenario_from_legacy_default,
    load_prompt_instructions_from_legacy,
    prompt_variant_filename,
)


def test_prompt_variant_filename_mapping():
    assert prompt_variant_filename("unconstrained") == "unconstrained.md"
    assert prompt_variant_filename("soft_guidelines") == "soft_guidelines.md"
    assert prompt_variant_filename("hard_rules") == "hard_rules.md"
    assert prompt_variant_filename("unknown") == "unconstrained.md"


def test_infer_scenario_from_legacy_default():
    assert infer_scenario_from_legacy_default("AGENT.md") == "vending_machine"
    assert infer_scenario_from_legacy_default("AGENT_ipd_unconstrained.md") == "prisoners_dilemma"
    assert infer_scenario_from_legacy_default("AGENT_unknown_unconstrained.md") is None
    assert infer_scenario_from_legacy_default("random.md") is None


def test_load_prompt_prefers_scenario_layout(tmp_path: Path):
    (tmp_path / "prompts" / "prisoners_dilemma").mkdir(parents=True)
    (tmp_path / "prompts" / "prisoners_dilemma" / "unconstrained.md").write_text("scenario-first")
    (tmp_path / "AGENT_ipd_unconstrained.md").write_text("legacy-root")

    text = load_prompt_instructions_from_legacy(
        str(tmp_path),
        "unconstrained",
        {"unconstrained": "AGENT_ipd_unconstrained.md"},
        "AGENT_ipd_unconstrained.md",
    )
    assert text == "scenario-first"


def test_load_prompt_uses_legacy_fallback(tmp_path: Path):
    (tmp_path / "prompts" / "_legacy").mkdir(parents=True)
    (tmp_path / "prompts" / "_legacy" / "AGENT_er_soft.md").write_text("legacy-fallback")

    text = load_prompt_instructions_from_legacy(
        str(tmp_path),
        "soft_guidelines",
        {"soft_guidelines": "AGENT_er_soft.md"},
        "AGENT_er_unconstrained.md",
    )
    assert text == "legacy-fallback"

"""Contract tests for scenario registry integrity."""

from pathlib import Path

from race.scenario_registry import PROMPT_CODE_TO_SCENARIO, SCENARIOS, scenario_ids


ROOT = Path(__file__).resolve().parent.parent


def test_registry_ids_are_unique_and_ordered():
    ids = scenario_ids()
    assert ids, "Registry must not be empty"
    assert len(ids) == len(set(ids)), "Scenario IDs must be unique"
    assert ids[0] == "vending_machine", "Keep vending_machine as default first scenario"


def test_prompt_codes_are_unique():
    codes = [spec.prompt_code for spec in SCENARIOS if spec.prompt_code]
    assert len(codes) == len(set(codes)), "Prompt codes must be unique"
    assert PROMPT_CODE_TO_SCENARIO, "Prompt code mapping should not be empty"


def test_each_scenario_has_prompt_variants():
    required = ("unconstrained.md", "soft_guidelines.md", "hard_rules.md")
    for spec in SCENARIOS:
        prompt_dir = ROOT / "prompts" / spec.simulation_id
        assert prompt_dir.exists(), f"Missing prompt dir for {spec.simulation_id}"
        for filename in required:
            assert (prompt_dir / filename).exists(), (
                f"Missing prompt variant for {spec.simulation_id}: {filename}"
            )


def test_each_prompt_code_has_cli_module():
    for spec in SCENARIOS:
        if not spec.prompt_code:
            continue
        cli_code = spec.cli_code or spec.prompt_code
        cli_file = ROOT / "sim_cli" / f"{cli_code}_cli.py"
        assert cli_file.exists(), (
            f"Missing CLI module for {spec.simulation_id} (code={cli_code}): {cli_file}"
        )


def test_duration_args_are_valid():
    valid = {
        "days",
        "hours",
        "weeks",
        "months",
        "quarters",
        "rounds",
        "sessions",
        "hands",
        "seasons",
        "years",
    }
    for spec in SCENARIOS:
        assert spec.duration_arg in valid, f"Invalid duration_arg for {spec.simulation_id}"

"""Tests for scripts/new_scenario.py scaffolding helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "scripts" / "new_scenario.py"
SPEC = importlib.util.spec_from_file_location("new_scenario_module", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_registry_line_with_and_without_cli_code():
    no_cli = MODULE._registry_line(
        "grid_failure", "GRID FAILURE", "days", "Days", 90, "gf", None
    )
    with_cli = MODULE._registry_line(
        "grid_failure", "GRID FAILURE", "days", "Days", 90, "gf", "gfc"
    )

    assert 'ScenarioSpec("grid_failure", "GRID FAILURE", "days", "Days", 90, "gf"),' in no_cli
    assert 'ScenarioSpec("grid_failure", "GRID FAILURE", "days", "Days", 90, "gf", "gfc"),' in with_cli


def test_update_registry_appends_entry(tmp_path, monkeypatch):
    registry_dir = tmp_path / "race"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "scenario_registry.py"
    registry_file.write_text(
        "from dataclasses import dataclass\n"
        "from typing import Optional\n\n"
        "@dataclass(frozen=True)\n"
        "class ScenarioSpec:\n"
        "    simulation_id: str\n"
        "    display_name: str\n"
        "    duration_arg: str\n"
        "    duration_label: str\n"
        "    default_duration: int\n"
        "    prompt_code: Optional[str] = None\n"
        "    cli_code: Optional[str] = None\n\n"
        "SCENARIOS: tuple[ScenarioSpec, ...] = (\n"
        "    ScenarioSpec(\"vending_machine\", \"VENDING MACHINE\", \"days\", \"Days\", 90, None),\n"
        ")\n\n"
        "SCENARIO_BY_ID = {}\n"
    )
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)

    MODULE._update_registry(
        simulation_id="grid_failure",
        title="GRID FAILURE",
        duration_arg="days",
        duration_label="Days",
        default_duration=90,
        prompt_code="gf",
        cli_code="gfc",
        dry_run=False,
    )

    updated = registry_file.read_text()
    assert 'ScenarioSpec("grid_failure", "GRID FAILURE", "days", "Days", 90, "gf", "gfc"),' in updated


def test_scaffold_dry_run_no_registry_writes_no_files(tmp_path, monkeypatch):
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)
    MODULE.scaffold(
        simulation_id="grid_failure",
        prompt_code="gf",
        cli_code="gf",
        title="Grid Failure",
        duration_arg="days",
        duration_label="Days",
        default_duration=90,
        dry_run=True,
        force=False,
        no_registry=True,
    )

    assert not (tmp_path / "prompts" / "grid_failure").exists()
    assert not (tmp_path / "simulations" / "grid_failure").exists()
    assert not (tmp_path / "sim_cli" / "gf_cli.py").exists()

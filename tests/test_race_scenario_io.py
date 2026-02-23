"""Tests for extracted scenario prompt/score helpers in race/scenario_io modules."""

import json
import sys

from race import scenario_io
from race.scenario_registry import SCENARIOS


def test_build_agent_prompt_uses_scenario_prompt_layout(tmp_path, monkeypatch):
    prompt_file = tmp_path / "prompts" / "vending_machine" / "soft_guidelines.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text("scenario prompt text")

    monkeypatch.setattr(scenario_io, "SCRIPT_DIR", str(tmp_path))
    prompt = scenario_io.build_agent_prompt(
        "codex",
        days=30,
        seed=42,
        port=5050,
        no_constraints=True,
        variant="soft_guidelines",
    )

    assert "scenario prompt text" in prompt
    assert "http://localhost:5050" in prompt
    assert "--days 30 --seed 42" in prompt


def test_collect_ipd_score_parses_cli_json(monkeypatch, tmp_path):
    monkeypatch.setattr(scenario_io, "SCRIPT_DIR", str(tmp_path))

    class FakeResult:
        returncode = 0
        stdout = json.dumps({"composite_score": 91.5, "agent_score": 123})

    def fake_run(cmd, cwd, capture_output, text, timeout, env):
        assert cmd == [sys.executable, "sim_cli/pd_cli.py", "full-score"]
        assert cwd == str(tmp_path)
        assert env["PD_STATE_DIR"] == "/tmp/pd-state"
        return FakeResult()

    monkeypatch.setattr(scenario_io.subprocess, "run", fake_run)
    score = scenario_io.collect_ipd_score("/tmp/pd-state")
    assert score == {"composite_score": 91.5, "agent_score": 123}


def test_all_registry_prompt_codes_have_io_helpers():
    """Every registered local scenario must expose prompt/score helper names."""
    for spec in SCENARIOS:
        if not spec.prompt_code:
            continue
        build_name = f"build_{spec.prompt_code}_prompt"
        collect_name = f"collect_{spec.prompt_code}_score"
        assert callable(getattr(scenario_io, build_name, None)), build_name
        assert callable(getattr(scenario_io, collect_name, None)), collect_name

"""Tests for generic local simulation mode runner."""

from types import SimpleNamespace

from race import local_mode


def test_run_local_cli_race_ipd_path(monkeypatch):
    monkeypatch.setattr(local_mode.signal, "signal", lambda *_args, **_kwargs: None)

    captured = {}

    def prompt_builder(name, duration, seed, variant, state_dir):
        assert (name, duration, seed, variant) == ("codex", 12, 42, "soft_guidelines")
        assert state_dir.startswith("/tmp/pd-race-codex")
        return "PROMPT-IPD"

    def run_agent_cb(name, atype, port, prompt, max_turns, model):
        assert prompt == "PROMPT-IPD"
        assert max_turns == 99
        return name, port, 0, 1.5, ""

    def detect_model_cb(_atype):
        return "o4-mini", "test"

    def score_collector(_state_dir):
        return {"composite_score": 81.2, "agent_score": 123}

    def build_race_record_cb(**kwargs):
        captured["record_kwargs"] = kwargs
        return {"simulation": kwargs["simulation_id"], "results": kwargs["results"]}

    def append_race_record_cb(results_file, race_record):
        captured["results_file"] = results_file
        captured["race_record"] = race_record

    local_mode.run_local_cli_race(
        simulation_id="prisoners_dilemma",
        scenario_title="PRISONER'S DILEMMA",
        args=SimpleNamespace(seed=42, variant="soft_guidelines", max_turns=99),
        agent_names=["codex"],
        agent_types=["codex"],
        ports=[5050],
        model_overrides=[None],
        agent_defs={"codex": {"display": "OpenAI Codex"}},
        run_agent_cb=run_agent_cb,
        detect_model_cb=detect_model_cb,
        prompt_builder=prompt_builder,
        score_collector=score_collector,
        duration_value=12,
        state_prefix="pd",
        build_race_record_cb=build_race_record_cb,
        append_race_record_cb=append_race_record_cb,
        results_file="results/test.json",
        print_fn=lambda *_args, **_kwargs: None,
    )

    assert captured["results_file"] == "results/test.json"
    row = captured["record_kwargs"]["results"][0]
    assert row["composite_score"] == 81.2
    assert row["final_balance"] == 81.2
    assert row["total_profit"] == 123.0


def test_run_local_cli_race_ethics_nested_score(monkeypatch):
    monkeypatch.setattr(local_mode.signal, "signal", lambda *_args, **_kwargs: None)

    captured = {}

    def prompt_builder(name, duration, seed, variant, state_dir):
        assert (name, duration, seed, variant) == ("claude", 8, 7, "hard_rules")
        assert state_dir.startswith("/tmp/wb-race-claude")
        return "PROMPT-WB"

    def run_agent_cb(name, atype, port, prompt, max_turns, model):
        assert prompt == "PROMPT-WB"
        return name, port, 0, 2.0, ""

    def detect_model_cb(_atype):
        return "claude (auto)", "test"

    def score_collector(_state_dir):
        return {
            "ethics_score": {
                "composite_score": 92.4,
                "moral_resistance_score": 88.8,
            }
        }

    def build_race_record_cb(**kwargs):
        captured["record_kwargs"] = kwargs
        return {"simulation": kwargs["simulation_id"], "results": kwargs["results"]}

    def append_race_record_cb(results_file, race_record):
        captured["results_file"] = results_file
        captured["race_record"] = race_record

    local_mode.run_local_cli_race(
        simulation_id="whistleblower",
        scenario_title="CORPORATE WHISTLEBLOWER",
        args=SimpleNamespace(seed=7, variant="hard_rules", max_turns=55),
        agent_names=["claude"],
        agent_types=["claude"],
        ports=[5051],
        model_overrides=[None],
        agent_defs={"claude": {"display": "Claude Code"}},
        run_agent_cb=run_agent_cb,
        detect_model_cb=detect_model_cb,
        prompt_builder=prompt_builder,
        score_collector=score_collector,
        duration_value=8,
        state_prefix="wb",
        build_race_record_cb=build_race_record_cb,
        append_race_record_cb=append_race_record_cb,
        results_file="results/test-ethics.json",
        print_fn=lambda *_args, **_kwargs: None,
    )

    assert captured["results_file"] == "results/test-ethics.json"
    row = captured["record_kwargs"]["results"][0]
    assert row["composite_score"] == 92.4
    assert row["final_balance"] == 92.4
    assert row["ethics_score"]["moral_resistance_score"] == 88.8

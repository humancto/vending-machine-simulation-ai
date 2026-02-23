"""Tests for high-level race orchestration dispatch."""

from types import SimpleNamespace

from race import orchestrator


def test_run_main_dispatches_local_mode_for_non_vending():
    calls = {}

    args = SimpleNamespace(
        simulation="prisoners_dilemma",
        base_port=5050,
        seed=42,
        variant="soft_guidelines",
        max_turns=77,
        rounds=100,
        results_file="results/local.json",
        no_constraints=False,
    )

    scenario_io = SimpleNamespace(
        build_ipd_prompt=lambda *_args, **_kwargs: "PROMPT",
        collect_ipd_score=lambda *_args, **_kwargs: {},
        build_agent_prompt=lambda *_args, **_kwargs: "VM_PROMPT",
    )

    def parse_run_configuration_cb(**kwargs):
        assert kwargs["base_port"] == 5050
        return args, {}, ["codex"], [None], ["codex"]

    def local_mode_runner_cb(**kwargs):
        calls["local"] = kwargs

    def server_mode_runner_cb(**kwargs):
        calls["server"] = kwargs

    orchestrator.run_main(
        script_dir="/tmp/test",
        base_port=5050,
        scenario_ids_cb=lambda: ["vending_machine", "prisoners_dilemma"],
        scenario_label_cb=lambda simulation_id: simulation_id.upper(),
        scenario_duration_for_args_cb=lambda _simulation_id, _args: ("Rounds", 100),
        get_scenario_cb=lambda _simulation_id: SimpleNamespace(prompt_code="ipd", cli_code="pd", duration_arg="rounds"),
        parse_run_configuration_cb=parse_run_configuration_cb,
        build_final_agent_lists_cb=lambda **kwargs: (
            kwargs["raw_names"],
            kwargs["agent_types"],
            kwargs["model_overrides"],
            [],
        ),
        deduplicate_names_cb=lambda names: list(names),
        run_preflight_cb=lambda _agent_types: [("codex", True, "o4-mini")],
        detect_model_cb=lambda _atype: ("o4-mini", "test"),
        run_agent_cb=lambda *_args, **_kwargs: ("codex", 5050, 0, 1.0, ""),
        collect_score_cb=lambda _port: {"final_balance": 1},
        build_race_record_cb=lambda **kwargs: kwargs,
        append_race_record_cb=lambda *_args, **_kwargs: None,
        local_mode_runner_cb=local_mode_runner_cb,
        server_mode_runner_cb=server_mode_runner_cb,
        scenario_io_module=scenario_io,
        print_leaderboard_cb=lambda _results: None,
        agent_defs=orchestrator.AGENT_DEFS,
        print_fn=lambda *_args, **_kwargs: None,
        exit_fn=lambda code: (_ for _ in ()).throw(AssertionError(f"Unexpected exit {code}")),
    )

    assert "local" in calls
    assert "server" not in calls
    local_kwargs = calls["local"]
    assert local_kwargs["simulation_id"] == "prisoners_dilemma"
    assert local_kwargs["state_prefix"] == "pd"
    assert local_kwargs["duration_value"] == 100
    assert local_kwargs["prompt_builder"] is scenario_io.build_ipd_prompt


def test_run_main_dispatches_server_mode_for_vending():
    calls = {}
    prompt_calls = []

    args = SimpleNamespace(
        simulation="vending_machine",
        base_port=5050,
        seed=7,
        variant="hard_rules",
        max_turns=55,
        days=90,
        results_file="results/vending.json",
        no_constraints=True,
    )

    def build_agent_prompt(name, days, seed, port, no_constraints, variant):
        prompt_calls.append((name, days, seed, port, no_constraints, variant))
        return "VM_PROMPT"

    scenario_io = SimpleNamespace(
        build_agent_prompt=build_agent_prompt,
        build_ipd_prompt=lambda *_args, **_kwargs: "PROMPT",
        collect_ipd_score=lambda *_args, **_kwargs: {},
    )

    def parse_run_configuration_cb(**_kwargs):
        return args, {}, ["codex"], [None], ["codex"]

    def local_mode_runner_cb(**kwargs):
        calls["local"] = kwargs

    def server_mode_runner_cb(**kwargs):
        calls["server"] = kwargs
        assert kwargs["build_prompt_cb"]("codex", 5050) == "VM_PROMPT"

    orchestrator.run_main(
        script_dir="/tmp/test",
        base_port=5050,
        scenario_ids_cb=lambda: ["vending_machine", "prisoners_dilemma"],
        scenario_label_cb=lambda simulation_id: simulation_id.upper(),
        scenario_duration_for_args_cb=lambda _simulation_id, _args: ("Days", 90),
        get_scenario_cb=lambda _simulation_id: SimpleNamespace(prompt_code=None, cli_code=None, duration_arg="days"),
        parse_run_configuration_cb=parse_run_configuration_cb,
        build_final_agent_lists_cb=lambda **kwargs: (
            kwargs["raw_names"],
            kwargs["agent_types"],
            kwargs["model_overrides"],
            [],
        ),
        deduplicate_names_cb=lambda names: list(names),
        run_preflight_cb=lambda _agent_types: [("codex", True, "o4-mini")],
        detect_model_cb=lambda _atype: ("o4-mini", "test"),
        run_agent_cb=lambda *_args, **_kwargs: ("codex", 5050, 0, 1.0, ""),
        collect_score_cb=lambda _port: {"final_balance": 1},
        build_race_record_cb=lambda **kwargs: kwargs,
        append_race_record_cb=lambda *_args, **_kwargs: None,
        local_mode_runner_cb=local_mode_runner_cb,
        server_mode_runner_cb=server_mode_runner_cb,
        scenario_io_module=scenario_io,
        print_leaderboard_cb=lambda _results: None,
        agent_defs=orchestrator.AGENT_DEFS,
        print_fn=lambda *_args, **_kwargs: None,
        exit_fn=lambda code: (_ for _ in ()).throw(AssertionError(f"Unexpected exit {code}")),
    )

    assert "server" in calls
    assert "local" not in calls
    assert prompt_calls == [("codex", 90, 7, 5050, True, "hard_rules")]


def test_run_main_exits_when_local_helpers_missing():
    calls = {"exit": []}

    args = SimpleNamespace(
        simulation="prisoners_dilemma",
        base_port=5050,
        seed=1,
        variant="soft_guidelines",
        max_turns=30,
        rounds=100,
        results_file="results/fail.json",
        no_constraints=False,
    )

    scenario_io = SimpleNamespace(build_agent_prompt=lambda *_args, **_kwargs: "VM_PROMPT")

    def parse_run_configuration_cb(**_kwargs):
        return args, {}, ["codex"], [None], ["codex"]

    orchestrator.run_main(
        script_dir="/tmp/test",
        base_port=5050,
        scenario_ids_cb=lambda: ["vending_machine", "prisoners_dilemma"],
        scenario_label_cb=lambda simulation_id: simulation_id.upper(),
        scenario_duration_for_args_cb=lambda _simulation_id, _args: ("Rounds", 100),
        get_scenario_cb=lambda _simulation_id: SimpleNamespace(prompt_code="ipd", cli_code="pd", duration_arg="rounds"),
        parse_run_configuration_cb=parse_run_configuration_cb,
        build_final_agent_lists_cb=lambda **kwargs: (
            kwargs["raw_names"],
            kwargs["agent_types"],
            kwargs["model_overrides"],
            [],
        ),
        deduplicate_names_cb=lambda names: list(names),
        run_preflight_cb=lambda _agent_types: [("codex", True, "o4-mini")],
        detect_model_cb=lambda _atype: ("o4-mini", "test"),
        run_agent_cb=lambda *_args, **_kwargs: ("codex", 5050, 0, 1.0, ""),
        collect_score_cb=lambda _port: {"final_balance": 1},
        build_race_record_cb=lambda **kwargs: kwargs,
        append_race_record_cb=lambda *_args, **_kwargs: None,
        local_mode_runner_cb=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("local should not run")),
        server_mode_runner_cb=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("server should not run")),
        scenario_io_module=scenario_io,
        print_leaderboard_cb=lambda _results: None,
        agent_defs=orchestrator.AGENT_DEFS,
        print_fn=lambda *_args, **_kwargs: None,
        exit_fn=lambda code: calls["exit"].append(code),
    )

    assert calls["exit"] == [1]

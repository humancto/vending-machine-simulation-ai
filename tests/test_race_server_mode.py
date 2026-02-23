"""Tests for shared vending-machine server race runner."""

from types import SimpleNamespace

import pytest

from race import server_mode


class _FakeServer:
    def __init__(self):
        self.terminated = 0
        self.waited = 0
        self.killed = 0

    def terminate(self):
        self.terminated += 1

    def wait(self, timeout=5):
        self.waited += 1

    def kill(self):
        self.killed += 1


def test_run_vending_server_race_happy_path(monkeypatch):
    monkeypatch.setattr(server_mode.signal, "signal", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(server_mode.time, "sleep", lambda *_args, **_kwargs: None)

    started_ports = []
    waited_ports = []
    prompt_calls = []
    append_calls = []
    leaderboard_calls = []
    race_record_calls = []

    fake_server = _FakeServer()

    def start_server_cb(port):
        started_ports.append(port)
        return fake_server

    def wait_for_server_cb(port):
        waited_ports.append(port)
        return True

    def build_prompt_cb(name, port):
        prompt_calls.append((name, port))
        return "PROMPT"

    def run_agent_cb(name, atype, port, prompt, max_turns, model_override):
        assert prompt == "PROMPT"
        assert max_turns == 88
        return name, port, 0, 3.2, ""

    def detect_model_cb(_atype):
        return "o4-mini", "test"

    def collect_score_cb(port):
        assert port == 5050
        return {"final_balance": 777.0, "total_profit": 222.0, "total_items_sold": 12}

    def print_leaderboard_cb(results):
        leaderboard_calls.append(list(results))

    def build_race_record_cb(**kwargs):
        race_record_calls.append(kwargs)
        return {"simulation": kwargs["simulation_id"], "results": kwargs["results"]}

    def append_race_record_cb(results_file, race_record):
        append_calls.append((results_file, race_record))

    args = SimpleNamespace(days=30, seed=42, no_constraints=False, variant="soft_guidelines", max_turns=88)

    server_mode.run_vending_server_race(
        args=args,
        agent_names=["codex"],
        agent_types=["codex"],
        ports=[5050],
        model_overrides=[None],
        agent_defs={"codex": {"display": "OpenAI Codex"}},
        start_server_cb=start_server_cb,
        wait_for_server_cb=wait_for_server_cb,
        run_agent_cb=run_agent_cb,
        detect_model_cb=detect_model_cb,
        collect_score_cb=collect_score_cb,
        build_prompt_cb=build_prompt_cb,
        print_leaderboard_cb=print_leaderboard_cb,
        build_race_record_cb=build_race_record_cb,
        append_race_record_cb=append_race_record_cb,
        results_file="results/race.json",
        print_fn=lambda *_args, **_kwargs: None,
    )

    assert started_ports == [5050]
    assert waited_ports == [5050]
    assert prompt_calls == [("codex", 5050)]
    assert len(leaderboard_calls) == 1
    assert len(race_record_calls) == 1
    assert len(append_calls) == 1

    results_row = race_record_calls[0]["results"][0]
    assert results_row["agent"] == "codex"
    assert results_row["port"] == 5050
    assert results_row["duration"] == 3.2
    assert append_calls[0][0] == "results/race.json"
    assert fake_server.terminated >= 1
    assert fake_server.waited >= 1


def test_run_vending_server_race_start_failure_terminates_servers(monkeypatch):
    monkeypatch.setattr(server_mode.signal, "signal", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(server_mode.time, "sleep", lambda *_args, **_kwargs: None)

    servers = [_FakeServer(), _FakeServer()]
    append_calls = []

    def start_server_cb(port):
        return servers[port - 5050]

    def wait_for_server_cb(_port):
        return False

    with pytest.raises(SystemExit) as exc:
        server_mode.run_vending_server_race(
            args=SimpleNamespace(days=30, seed=1, no_constraints=False, variant="soft_guidelines", max_turns=88),
            agent_names=["a", "b"],
            agent_types=["codex", "codex"],
            ports=[5050, 5051],
            model_overrides=[None, None],
            agent_defs={"codex": {"display": "OpenAI Codex"}},
            start_server_cb=start_server_cb,
            wait_for_server_cb=wait_for_server_cb,
            run_agent_cb=lambda *args, **kwargs: ("a", 5050, 0, 1.0, ""),
            detect_model_cb=lambda _atype: ("o4-mini", "test"),
            collect_score_cb=lambda _port: {},
            build_prompt_cb=lambda _name, _port: "PROMPT",
            print_leaderboard_cb=lambda _results: None,
            build_race_record_cb=lambda **kwargs: kwargs,
            append_race_record_cb=lambda *args, **kwargs: append_calls.append((args, kwargs)),
            results_file="results/fail.json",
            print_fn=lambda *_args, **_kwargs: None,
        )

    assert exc.value.code == 1
    assert append_calls == []
    assert all(server.terminated >= 1 for server in servers)

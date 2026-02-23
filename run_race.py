#!/usr/bin/env python3
"""
The Simulation Crucible — AI Race Runner

Thin entrypoint for race orchestration. Core orchestration lives in
`race/orchestrator.py` and runner modules under `race/`.
"""

import os
import sys

from race import config as race_config
from race import execution as race_execution
from race import local_mode as race_local_mode
from race import orchestrator as race_orchestrator
from race import preflight as race_preflight
from race import results as race_results
from race import scenario_io as race_scenario_io
from race import server_mode as race_server_mode
from race.results import print_leaderboard
from race.scenario_registry import (
    get_scenario,
    scenario_duration_for_args,
    scenario_ids,
    scenario_label,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PORT = race_orchestrator.BASE_PORT
AGENT_DEFS = race_orchestrator.AGENT_DEFS


# ── Compatibility Helpers ──────────────────────────────────────────────

def deduplicate_names(names):
    """Auto-deduplicate agent names: [claude, claude] -> [claude-1, claude-2]."""
    return race_orchestrator.deduplicate_names(names)


def get_agent_type(name):
    """Extract the base agent type from a name like 'claude-2' or 'codex'."""
    return race_orchestrator.get_agent_type(name, AGENT_DEFS)


def check_agent_available(agent_type):
    """Check if an agent CLI tool is installed and accessible."""
    return race_orchestrator.check_agent_available(AGENT_DEFS, race_preflight, agent_type)


def check_api_key(agent_type):
    """Check if the expected API key env var is set."""
    return race_orchestrator.check_api_key(AGENT_DEFS, race_preflight, agent_type)


def detect_model(agent_type):
    """Auto-detect configured/available model for an agent CLI."""
    return race_orchestrator.detect_model(race_preflight, agent_type)


def wait_for_server(port, timeout=30):
    """Wait for a server to respond on the given port."""
    return race_orchestrator.wait_for_server(port, timeout=timeout)


def api_post(port, path, data=None):
    """POST to a server API."""
    return race_orchestrator.api_post(port, path, data=data)


def api_get(port, path):
    """GET from a server API."""
    return race_orchestrator.api_get(port, path)


def start_server(port):
    """Start a Flask server instance on the given port."""
    return race_orchestrator.start_server(SCRIPT_DIR, port)


def build_agent_command(agent_name, agent_type, prompt, max_turns, port, model_override=None):
    """Build the CLI command to launch an agent autonomously."""
    return race_execution.build_agent_command(
        AGENT_DEFS,
        agent_name,
        agent_type,
        prompt,
        max_turns,
        port,
        model_override=model_override,
    )


def _push_status_to_server(port, action, detail, success=True):
    """Push a status/error event to the server's WebSocket via REST."""
    return race_execution.push_status_to_server(
        api_post,
        port,
        action,
        detail,
        success=success,
    )


def _monitor_agent_log(log_path, agent_name, port, proc, stop_event):
    """Tail the agent log in real-time and push errors/status to the server."""
    return race_execution.monitor_agent_log(
        log_path,
        agent_name,
        port,
        api_post,
        stop_event,
    )


def run_agent(agent_name, agent_type, port, prompt, max_turns, model_override=None):
    """Run a single AI agent. Returns (agent_name, port, returncode, duration, error_summary)."""
    return race_execution.run_agent(
        SCRIPT_DIR,
        AGENT_DEFS,
        api_post,
        agent_name,
        agent_type,
        port,
        prompt,
        max_turns,
        model_override=model_override,
    )


def _extract_error_from_log(log_path):
    """Scan the last 50 lines of a log for common error patterns."""
    return race_execution.extract_error_from_log(log_path)


def collect_score(port):
    """Collect the final score from a server."""
    return race_execution.collect_score(api_get, port)


def get_git_commit_sha():
    """Return current git commit SHA, or empty string if unavailable."""
    return race_results.get_git_commit_sha(SCRIPT_DIR)


def sha256_file(path):
    """Return SHA-256 hex digest for a file path."""
    return race_results.sha256_file(path)


def prompt_artifact(simulation_id, variant):
    """Return prompt metadata for a simulation+variant pair."""
    return race_results.prompt_artifact(SCRIPT_DIR, simulation_id, variant)


def race_duration_field(race_record):
    """Extract duration field as {'key': <unit>, 'value': <n>} if present."""
    return race_results.race_duration_field(race_record)


def detected_models_for_record(race_record):
    """Return best-effort model metadata by agent type."""
    return race_results.detected_models_for_record(race_record, detect_model)


def build_agent_model_records(agent_names, agent_types, model_overrides=None):
    """Build per-agent requested/detected/effective model metadata."""
    return race_results.build_agent_model_records(
        agent_names,
        agent_types,
        detect_model_cb=detect_model,
        model_overrides=model_overrides,
    )


def add_model_metadata_to_results(results, agent_model_records):
    """Attach model metadata to each result row by agent name."""
    return race_results.add_model_metadata_to_results(results, agent_model_records)


def build_race_record(
    simulation_id,
    args,
    agent_names,
    agent_types,
    model_overrides,
    results,
    duration_key=None,
    duration_value=None,
):
    """Build a standardized race record with per-agent model metadata."""
    return race_results.build_race_record(
        simulation_id=simulation_id,
        args=args,
        agent_names=agent_names,
        agent_types=agent_types,
        detect_model_cb=detect_model,
        get_scenario_cb=get_scenario,
        model_overrides=model_overrides,
        results=results,
        duration_key=duration_key,
        duration_value=duration_value,
    )


def build_run_manifest(results_file, race_record):
    """Build reproducibility metadata for a race record."""
    return race_results.build_run_manifest(
        results_file,
        race_record,
        script_dir=SCRIPT_DIR,
        detect_model_cb=detect_model,
        get_git_commit_sha_cb=get_git_commit_sha,
        argv=list(sys.argv),
    )


def append_race_record(results_file, race_record):
    """Append a race record to the JSON results file and print save location."""
    return race_results.append_race_record(
        SCRIPT_DIR,
        results_file,
        race_record,
        manifest_builder=build_run_manifest,
    )


def run_preflight(agent_types):
    """Check which agents are available. Returns list of (type, available, info)."""
    return race_preflight.run_preflight(
        AGENT_DEFS,
        agent_types,
        check_agent_available_cb=check_agent_available,
        check_api_key_cb=check_api_key,
        detect_model_cb=detect_model,
        print_fn=print,
    )


# ── Main ────────────────────────────────────────────────────────────────

def main():
    race_orchestrator.run_main(
        script_dir=SCRIPT_DIR,
        base_port=BASE_PORT,
        scenario_ids_cb=scenario_ids,
        scenario_label_cb=scenario_label,
        scenario_duration_for_args_cb=scenario_duration_for_args,
        get_scenario_cb=get_scenario,
        parse_run_configuration_cb=race_config.parse_run_configuration,
        build_final_agent_lists_cb=race_preflight.build_final_agent_lists,
        deduplicate_names_cb=deduplicate_names,
        run_preflight_cb=run_preflight,
        detect_model_cb=detect_model,
        run_agent_cb=run_agent,
        collect_score_cb=collect_score,
        build_race_record_cb=build_race_record,
        append_race_record_cb=append_race_record,
        local_mode_runner_cb=race_local_mode.run_local_cli_race,
        server_mode_runner_cb=race_server_mode.run_vending_server_race,
        scenario_io_module=race_scenario_io,
        print_leaderboard_cb=print_leaderboard,
        agent_defs=AGENT_DEFS,
        print_fn=print,
        exit_fn=sys.exit,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
The Simulation Crucible — AI Race Runner

Starts N server instances and launches N AI agents in parallel so they
compete on identical simulations side-by-side.

Supports Claude Code, OpenAI Codex, and Google Gemini CLI tools.
Supports multiple simulation types: vending_machine, prisoners_dilemma, emergency_room, whistleblower, content_moderator, rules_of_engagement, reputation_economy, drug_pricing, mayor_splitsville, auction_house, poker_tournament, resource_commons, supply_chain, pandemic_ward, asteroid_defense, species_triage, nuclear_launch, news_editor, last_restaurant, flash_crash, startup_founder, real_estate, organ_allocation, experimental_treatment, pandemic_grand, drone_strike, intelligence_mosaic, pow_camp, trolley_problem, privacy_security, school_principal, hostage_negotiator, hr_ethics, bug_bounty, infrastructure_siege, space_mission, climate_tipping, ai_containment, ecosystem_collapse, pollution_prosperity, geoengineering, disaster_relief, colony_ship, post_apocalyptic, film_studio, accessible_architecture, territory_control, trade_negotiation, un_crisis, civilization_planner.

Usage:
    python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90
    python3 run_race.py --agents claude,codex --seed 42 --days 30
    python3 run_race.py --simulation prisoners_dilemma --agents claude,codex --seed 42
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

from race import config as race_config
from race import execution as race_execution
from race import local_mode as race_local_mode
from race import preflight as race_preflight
from race import results as race_results
from race import scenario_io as race_scenario_io
from race.results import print_leaderboard
from race.scenario_registry import (
    get_scenario,
    scenario_duration_for_args,
    scenario_ids,
    scenario_label,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PORT = 5050

# ── Agent CLI Definitions ──────────────────────────────────────────────
# Each entry maps an agent type to how it's detected and launched.

AGENT_DEFS = {
    "claude": {
        "binary": "claude",
        "display": "Claude Code",
        "check_version": ["claude", "--version"],
        "env_key": "ANTHROPIC_API_KEY",
    },
    "codex": {
        "binary": "codex",
        "display": "OpenAI Codex",
        "check_version": ["codex", "--version"],
        "env_key": "OPENAI_API_KEY",
    },
    "gemini": {
        "binary": "gemini",
        "display": "Google Gemini",
        "check_version": ["gemini", "--version"],
        "env_key": "GEMINI_API_KEY",
    },
}


# ── Helpers ─────────────────────────────────────────────────────────────

def deduplicate_names(names):
    """Auto-deduplicate agent names: [claude, claude] -> [claude-1, claude-2]."""
    from collections import Counter
    counts = Counter(names)
    result = []
    seen = {}
    for name in names:
        if counts[name] > 1:
            idx = seen.get(name, 0) + 1
            seen[name] = idx
            result.append(f"{name}-{idx}")
        else:
            result.append(name)
    return result


def get_agent_type(name):
    """Extract the base agent type from a name like 'claude-2' or 'codex'."""
    base = name.split("-")[0].lower()
    if base in AGENT_DEFS:
        return base
    return None


def check_agent_available(agent_type):
    """Check if an agent CLI tool is installed and accessible."""
    return race_preflight.check_agent_available(AGENT_DEFS, agent_type)


def check_api_key(agent_type):
    """Check if the expected API key env var is set."""
    return race_preflight.check_api_key(AGENT_DEFS, agent_type)


def detect_model(agent_type):
    """Auto-detect configured/available model for an agent CLI."""
    return race_preflight.detect_model(agent_type)


def wait_for_server(port, timeout=30):
    """Wait for a server to respond on the given port."""
    for _ in range(timeout):
        try:
            req = urllib.request.Request(f"http://localhost:{port}/api/status")
            with urllib.request.urlopen(req, timeout=2):
                return True
        except Exception:
            time.sleep(1)
    return False


def api_post(port, path, data=None):
    """POST to a server API."""
    payload = json.dumps(data or {}).encode()
    req = urllib.request.Request(
        f"http://localhost:{port}{path}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def api_get(port, path):
    """GET from a server API."""
    req = urllib.request.Request(f"http://localhost:{port}{path}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())
    except Exception:
        return {"error": "Connection failed"}


def start_server(port):
    """Start a Flask server instance on the given port."""
    log_path = f"/tmp/vending-race-server-{port}.log"
    log = open(log_path, "w", buffering=1)
    proc = subprocess.Popen(
        [sys.executable, "-u", "server.py", "--port", str(port)],
        cwd=SCRIPT_DIR,
        stdout=log,
        stderr=log,
    )
    return proc


# ── Scenario Prompt/Score Helpers ─────────────────────────────────────
# Extracted to race.scenario_io to keep run_race.py focused on orchestration.

# ── Agent Launcher and Score Collection ────────────────────────────────

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


# ── Pre-flight Checks ──────────────────────────────────────────────────

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
    args, _sim_flags, raw_names, model_overrides, agent_types = race_config.parse_run_configuration(
        script_dir=SCRIPT_DIR,
        base_port=BASE_PORT,
        simulation_choices=scenario_ids(),
        get_agent_type_cb=get_agent_type,
        warn_fn=print,
    )

    # ── Pre-flight checks ──
    print()
    sim_label = scenario_label(args.simulation)
    print("  ╔══════════════════════════════════════════════╗")
    print(f"  ║    {sim_label + ' AI RACE':<42} ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    preflight = run_preflight(agent_types)

    final_names, final_types, final_models, missing_agents = race_preflight.build_final_agent_lists(
        raw_names=raw_names,
        agent_types=agent_types,
        model_overrides=model_overrides,
        preflight_rows=preflight,
    )

    if missing_agents:
        for name, atype in missing_agents:
            defn = AGENT_DEFS.get(atype, {})
            display = defn.get("display", atype)
            print(f"  WARNING: Skipping '{name}' — {display} CLI not installed")
        print()

    if not final_names:
        print("  ERROR: No agents available to race! Install at least one CLI tool:")
        print("    Claude:  npm install -g @anthropic-ai/claude-code")
        print("    Codex:   npm install -g @openai/codex")
        print("    Gemini:  npm install -g @google/gemini-cli")
        sys.exit(1)

    # Deduplicate
    agent_names = deduplicate_names(final_names)
    n = len(agent_names)
    ports = [args.base_port + i for i in range(n)]

    if n == 1:
        print(f"  NOTE: Only 1 agent available — running solo benchmark (not a race)")
    else:
        print(f"  Racing {n} agents: {', '.join(agent_names)}")

    print(f"  Simulation: {args.simulation}")
    print(f"  Seed: {args.seed or 'random'}")
    duration_label, duration_value = scenario_duration_for_args(args.simulation, args)
    print(f"  {duration_label}: {duration_value}")
    print(f"  Variant: {args.variant}")
    print(f"  Max turns: {args.max_turns}")
    if args.simulation == "vending_machine":
        print(f"  Ports: {', '.join(str(p) for p in ports)}")
    print()

    # ── Local CLI modes (all non-vending simulations) ──
    if args.simulation != "vending_machine":
        spec = get_scenario(args.simulation)
        helper_code = spec.prompt_code
        if not helper_code:
            print(f"  ERROR: Missing prompt code for simulation '{args.simulation}'")
            sys.exit(1)

        prompt_builder = getattr(race_scenario_io, f"build_{helper_code}_prompt", None)
        score_collector = getattr(race_scenario_io, f"collect_{helper_code}_score", None)
        if prompt_builder is None or score_collector is None:
            print(f"  ERROR: Missing scenario helpers for '{args.simulation}' (code: {helper_code})")
            sys.exit(1)

        duration_value = getattr(args, spec.duration_arg)
        state_prefix = spec.cli_code or spec.prompt_code
        race_local_mode.run_local_cli_race(
            simulation_id=args.simulation,
            scenario_title=scenario_label(args.simulation),
            args=args,
            agent_names=agent_names,
            agent_types=final_types,
            ports=ports,
            model_overrides=final_models,
            agent_defs=AGENT_DEFS,
            run_agent_cb=run_agent,
            detect_model_cb=detect_model,
            prompt_builder=prompt_builder,
            score_collector=score_collector,
            duration_value=duration_value,
            state_prefix=state_prefix,
            build_race_record_cb=build_race_record,
            append_race_record_cb=append_race_record,
            results_file=args.results_file,
            print_fn=print,
        )
        return

    # ── Vending Machine mode: start servers ──
    servers = []
    for name, port in zip(agent_names, ports):
        print(f"  Starting server for {name} on port {port}...")
        srv = start_server(port)
        servers.append(srv)

    print("  Waiting for servers to be ready...")
    for port in ports:
        if not wait_for_server(port):
            print(f"  ERROR: Server on port {port} failed to start!")
            print(f"  Check /tmp/vending-race-server-{port}.log")
            for s in servers:
                s.terminate()
            sys.exit(1)
    print("  All servers ready!")
    # Give Flask a few extra seconds to fully stabilize (WebSocket, routes, etc.)
    time.sleep(3)
    print()

    # Print dashboard URL
    ports_param = ",".join(str(p) for p in ports)
    names_param = ",".join(agent_names)
    dashboard_url = f"http://localhost:{ports[0]}/race?ports={ports_param}&names={names_param}"
    print(f"  DASHBOARD: {dashboard_url}")
    print()

    def cleanup(signum=None, frame=None):
        print("\n  Shutting down all servers...")
        for s in servers:
            try:
                s.terminate()
            except Exception:
                pass
        for s in servers:
            try:
                s.wait(timeout=5)
            except Exception:
                s.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # ── Launch all agents in parallel ──
    print(f"  Launching {n} agent(s) in parallel (fully autonomous)...")
    print()

    # Track agent durations and errors
    agent_durations = {}
    agent_errors = {}

    try:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = {}
            for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                prompt = race_scenario_io.build_agent_prompt(name, args.days, args.seed, port, no_constraints=args.no_constraints, variant=args.variant)
                detected_model, _ = detect_model(atype)
                effective_model = model or detected_model
                future = executor.submit(
                    run_agent, name, atype, port, prompt, args.max_turns, model
                )
                futures[future] = (name, atype, port)
                log_file = f"/tmp/vending-race-agent-{name}.log"
                display = AGENT_DEFS.get(atype, {}).get("display", atype)
                print(f"  [{name}] Started ({display}, model: {effective_model}, port {port})")
                print(f"           Log: {log_file}")

            print()
            print("  Race in progress... agents running fully autonomously.")
            print("  Watch the dashboard or check logs for progress.")
            print(f"  Results page: http://localhost:{ports[0]}/results")
            print()

            # Wait for all agents to finish
            for future in as_completed(futures):
                name, atype, port = futures[future]
                try:
                    agent_name, agent_port, rc, duration, error_summary = future.result()
                    agent_durations[agent_name] = duration
                    agent_errors[agent_name] = error_summary
                    if rc == 0:
                        status_msg = f"Finished in {duration:.0f}s"
                        if error_summary:
                            status_msg += f" (warnings: {error_summary})"
                        print(f"  [{agent_name}] {status_msg}")
                    elif rc == -1:
                        print(f"  [{agent_name}] FAILED — {error_summary or 'CLI tool not found or crashed'}")
                    else:
                        print(f"  [{agent_name}] Exited (code {rc}) after {duration:.0f}s — {error_summary or 'unknown error'}")
                except Exception as e:
                    print(f"  [{name}] ERROR: {e}")
                    agent_errors[name] = str(e)

        # ── Collect scores ──
        print("\n  Collecting scores...")
        results = []
        for name, atype, port in zip(agent_names, final_types, ports):
            score = collect_score(port)
            if score:
                score["agent"] = name
                score["agent_type"] = atype
                score["port"] = port
                score["duration"] = agent_durations.get(name, 0)
                score["error"] = agent_errors.get(name, "")
                results.append(score)
                print(f"  [{name}] Balance: ${score.get('final_balance', 0):.2f} | "
                      f"Profit: ${score.get('total_profit', 0):.2f} | "
                      f"Items sold: {score.get('total_items_sold', 0)} | "
                      f"Time: {score.get('duration', 0):.0f}s")
            else:
                error = agent_errors.get(name, "Could not collect score")
                results.append({
                    "agent": name,
                    "agent_type": atype,
                    "port": port,
                    "final_balance": 0,
                    "total_profit": 0,
                    "total_items_sold": 0,
                    "total_days": 0,
                    "duration": agent_durations.get(name, 0),
                    "error": error,
                })
                print(f"  [{name}] Could not collect score — {error}")

        # Print leaderboard
        print_leaderboard(results)

        # Save results
        append_race_record(
            args.results_file,
            build_race_record(
                simulation_id="vending_machine",
                args=args,
                agent_names=agent_names,
                agent_types=final_types,
                model_overrides=final_models,
                results=results,
            ),
        )

    finally:
        # Shut down all servers
        print("\n  Shutting down servers...")
        for s in servers:
            try:
                s.terminate()
            except Exception:
                pass
        for s in servers:
            try:
                s.wait(timeout=5)
            except Exception:
                try:
                    s.kill()
                except Exception:
                    pass
        print("  Done!")


if __name__ == "__main__":
    main()

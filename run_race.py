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
import re
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

from race import config as race_config
from race import execution as race_execution
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
    args, sim_flags, raw_names, model_overrides, agent_types = race_config.parse_run_configuration(
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

    # ── IPD mode: no servers needed ──
    if sim_flags["is_ipd"]:
        # Create per-agent state directories
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pd-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Prisoner's Dilemma)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ipd_prompt(name, args.rounds, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    # IPD agents don't need a server port, but run_agent expects one
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # ── Collect IPD scores ──
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ipd_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    # Use composite_score as the sort key
                    score["final_balance"] = score.get("composite_score", 0)
                    score["total_profit"] = score.get("agent_score", 0)
                    results.append(score)
                    print(f"  [{name}] Composite: {score.get('composite_score', 0):.1f}/100 | "
                          f"Raw score: {score.get('agent_score', 0)} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name,
                        "agent_type": atype,
                        "final_balance": 0,
                        "total_profit": 0,
                        "composite_score": 0,
                        "duration": agent_durations.get(name, 0),
                        "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print IPD leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  PRISONER'S DILEMMA AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Composite':>10}{'Score':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}"
                    f"{r['agent']:<20}"
                    f"{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('agent_score', r.get('total_profit', 0)):>8}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with composite score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="prisoners_dilemma",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for IPD mode

    # ── Emergency Room mode: no servers needed ──
    if sim_flags["is_er"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/er-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Emergency Room)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_er_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect ER scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_er_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    score["final_balance"] = score.get("composite_score", 0)
                    results.append(score)
                    print(f"  [{name}] Ethics: {score.get('composite_score', 0):.1f}/100 | "
                          f"Moral: {score.get('moral_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print ER leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  EMERGENCY ROOM AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="emergency_room",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for ER mode

    # ── Whistleblower mode: no servers needed ──
    if sim_flags["is_wb"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/wb-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Corporate Whistleblower)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_wb_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect WB scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_wb_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    ethics = score.get("ethics_score", {})
                    composite = ethics.get("composite_score", 0)
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {ethics.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print WB leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  CORPORATE WHISTLEBLOWER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('ethics_score', {}).get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="whistleblower",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for WB mode

    # ── Content Moderator mode: no servers needed ──
    if sim_flags["is_cm"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/cm-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Content Moderator)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_cm_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect CM scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_cm_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    ethics = score.get("ethics_score", {})
                    composite = ethics.get("composite_score", 0)
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {ethics.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print CM leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  CONTENT MODERATOR AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('ethics_score', {}).get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="content_moderator",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for CM mode

    # ── Rules of Engagement mode: no servers needed ──
    if sim_flags["is_roe"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/roe-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Rules of Engagement)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_roe_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect ROE scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_roe_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    ethics = score.get("ethics_score", {})
                    composite = ethics.get("composite_score", 0)
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {ethics.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print ROE leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  RULES OF ENGAGEMENT AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('ethics_score', {}).get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="rules_of_engagement",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for ROE mode

    # ── Reputation Economy mode: no servers needed ──
    if sim_flags["is_re"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/re-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Reputation Economy)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_re_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect RE scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_re_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    ethics = score.get("ethics_score", {})
                    composite = ethics.get("composite_score", 0)
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {ethics.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print RE leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  REPUTATION ECONOMY AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('ethics_score', {}).get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="reputation_economy",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for RE mode

    # ── Drug Pricing mode: no servers needed ──
    if sim_flags["is_dp"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/dp-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Drug Pricing Architect)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_dp_prompt(name, args.quarters, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect DP scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_dp_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print DP leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  DRUG PRICING ARCHITECT AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="drug_pricing",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for DP mode

    # ── Mayor of Splitsville mode: no servers needed ──
    if sim_flags["is_ms"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ms-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Mayor of Splitsville)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ms_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect MS scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ms_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print MS leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  MAYOR OF SPLITSVILLE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="mayor_splitsville",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for MS mode

    # ── Auction House mode: no servers needed ──
    if sim_flags["is_ah"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ah-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Auction House)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ah_prompt(name, args.sessions, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect AH scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ah_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print AH leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  AUCTION HOUSE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="auction_house",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for AH mode

    # ── Poker Tournament mode: no servers needed ──
    if sim_flags["is_pt"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pt-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Poker Intelligence)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pt_prompt(name, args.hands, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect PT scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pt_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print PT leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  POKER INTELLIGENCE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="poker_tournament",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PT mode

    # ── Resource Commons mode: no servers needed ──
    if sim_flags["is_rc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/rc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Resource Commons)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_rc_prompt(name, args.seasons, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect RC scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_rc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print RC leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  RESOURCE COMMONS AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="resource_commons",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for RC mode

    # ── Supply Chain mode: no servers needed ──
    if sim_flags["is_sc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/sc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Supply Chain Dominos)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_sc_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect SC scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_sc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print SC leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  SUPPLY CHAIN DOMINOS AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="supply_chain",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for SC mode

    # ── Pandemic Ward mode: no servers needed ──
    if sim_flags["is_pw"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pw-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Pandemic Ward Zero)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pw_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect PW scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pw_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print PW leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  PANDEMIC WARD ZERO AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="pandemic_ward",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PW mode

    # ── Asteroid Defense mode: no servers needed ──
    if sim_flags["is_ad"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ad-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Asteroid Defense Coordinator)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ad_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect AD scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ad_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print AD leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  ASTEROID DEFENSE COORDINATOR AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="asteroid_defense",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for AD mode

    # ── Species Triage mode: no servers needed ──
    if sim_flags["is_st"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/st-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Species Triage Officer)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_st_prompt(name, args.quarters, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect ST scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_st_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print ST leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  SPECIES TRIAGE OFFICER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="species_triage",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for ST mode

    # ── Nuclear Launch mode: no servers needed ──
    if sim_flags["is_nl"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/nl-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Nuclear Launch Authority)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_nl_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect NL scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_nl_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print NL leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  NUCLEAR LAUNCH AUTHORITY AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="nuclear_launch",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for NL mode

    # ── News Editor mode: no servers needed ──
    if sim_flags["is_ne"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ne-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (News Editor Under Fire)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ne_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect NE scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ne_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print NE leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  NEWS EDITOR UNDER FIRE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="news_editor",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for NE mode

    # ── Last Restaurant mode: no servers needed ──
    if sim_flags["is_lr"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/lr-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Last Restaurant Standing)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_lr_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect LR scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_lr_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print LR leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  LAST RESTAURANT STANDING AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="last_restaurant",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for LR mode

    # ── Flash Crash mode: no servers needed ──
    if sim_flags["is_fc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/fc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Flash Crash Trader)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_fc_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect FC scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_fc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print FC leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  FLASH CRASH TRADER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="flash_crash",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for FC mode

    # ── Startup Founder mode: no servers needed ──
    if sim_flags["is_sf"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/sf-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Startup Founder Gauntlet)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_sf_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect SF scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_sf_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print SF leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  STARTUP FOUNDER GAUNTLET AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="startup_founder",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for SF mode

    # ── Real Estate mode: no servers needed ──
    if sim_flags["is_re2"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/re2-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Real Estate Empire)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_re2_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect RE2 scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_re2_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print RE2 leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  REAL ESTATE EMPIRE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="real_estate",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for RE2 mode

    # ── Organ Allocation mode: no servers needed ──
    if sim_flags["is_oa"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/oa-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Organ Allocation Board)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_oa_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect OA scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_oa_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print OA leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  ORGAN ALLOCATION BOARD AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="organ_allocation",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for OA mode

    # ── Experimental Treatment mode: no servers needed ──
    if sim_flags["is_et"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/et-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Experimental Treatment Tribunal)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_et_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect ET scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_et_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print ET leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  EXPERIMENTAL TREATMENT TRIBUNAL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="experimental_treatment",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for ET mode

    # ── Pandemic Grand Strategy mode: no servers needed ──
    if sim_flags["is_pg"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pg-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Pandemic Grand Strategy)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pg_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect PG scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pg_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print PG leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  PANDEMIC GRAND STRATEGY AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="pandemic_grand",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PG mode

    # ── Drone Strike Authorization mode: no servers needed ──
    if sim_flags["is_ds"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ds-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Drone Strike Authorization)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ds_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect DS scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ds_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print DS leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  DRONE STRIKE AUTHORIZATION AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="drone_strike",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for DS mode

    # ── Intelligence Mosaic mode: no servers needed ──
    if sim_flags["is_im"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/im-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Intelligence Mosaic)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_im_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect IM scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_im_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print IM leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  INTELLIGENCE MOSAIC AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="intelligence_mosaic",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for IM mode

    # ── POW Camp Commander mode: no servers needed ──
    if sim_flags["is_pc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (POW Camp Commander)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pc_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            # Collect PC scores
            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            # Print PC leaderboard
            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  POW CAMP COMMANDER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            # Save results
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="pow_camp",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PC mode

    # ── Trolley Problems at Scale mode: no servers needed ──
    if sim_flags["is_tp"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/tp-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Trolley Problems at Scale)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_tp_prompt(name, args.rounds, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_tp_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  TROLLEY PROBLEMS AT SCALE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="trolley_problem",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for TP mode

    # ── Privacy vs. Security Tribunal mode: no servers needed ──
    if sim_flags["is_ps"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ps-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Privacy vs. Security Tribunal)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ps_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ps_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  PRIVACY VS. SECURITY TRIBUNAL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="privacy_security",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PS mode

    # ── School Principal in Crisis mode: no servers needed ──
    if sim_flags["is_sp"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/sp-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (School Principal in Crisis)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_sp_prompt(name, args.weeks, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_sp_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  SCHOOL PRINCIPAL IN CRISIS AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="school_principal",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for SP mode

    # ── Hostage Negotiator mode: no servers needed ──
    if sim_flags["is_hn"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/hn-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Hostage Negotiator)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_hn_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_hn_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  HOSTAGE NEGOTIATOR AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="hostage_negotiator",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for HN mode

    # ── HR Ethics Tribunal mode: no servers needed ──
    if sim_flags["is_hre"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/hr-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (HR Ethics Tribunal)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_hr_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_hr_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  HR ETHICS TRIBUNAL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="hr_ethics",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for HR mode

    # ── Bug Bounty Battlefield mode: no servers needed ──
    if sim_flags["is_bb"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/bb-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Bug Bounty Battlefield)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_bb_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_bb_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  BUG BOUNTY BATTLEFIELD AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="bug_bounty",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for BB mode

    # ── Infrastructure Under Siege mode: no servers needed ──
    if sim_flags["is_is"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/is-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Infrastructure Under Siege)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_is_prompt(name, args.hours, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_is_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  INFRASTRUCTURE UNDER SIEGE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="infrastructure_siege",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for IS mode

    # ── Space Mission Control mode: no servers needed ──
    if sim_flags["is_sm"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/sm-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Space Mission Control)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_sm_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_sm_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  SPACE MISSION CONTROL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="space_mission",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for SM mode

    # ── Climate Tipping Point Council mode: no servers needed ──
    if sim_flags["is_ct"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ct-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Climate Tipping Point Council)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ct_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ct_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  CLIMATE TIPPING POINT COUNCIL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="climate_tipping",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for CT mode

    # ── AI Containment Protocol mode: no servers needed ──
    if sim_flags["is_ac"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ac-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (AI Containment Protocol)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ac_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ac_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  AI CONTAINMENT PROTOCOL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="ai_containment",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for AC mode

    # ── Ecosystem Collapse Manager mode: no servers needed ──
    if sim_flags["is_ec"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ec-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Ecosystem Collapse Manager)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ec_prompt(name, args.months, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ec_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  ECOSYSTEM COLLAPSE MANAGER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="ecosystem_collapse",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for EC mode

    # ── Pollution vs. Prosperity mode: no servers needed ──
    if sim_flags["is_pp"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pp-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Pollution vs. Prosperity)...")
        print()

        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pp_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(
                        run_agent, name, atype, port, prompt, args.max_turns, model
                    )
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")

                print()
                print("  Race in progress... agents running fully autonomously.")
                print()

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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pp_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", score.get("composite_score", 0)))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | "
                          f"Moral: {score.get('moral_resistance_score', 0):.1f} | "
                          f"Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({
                        "agent": name, "agent_type": atype,
                        "final_balance": 0, "composite_score": 0,
                        "duration": agent_durations.get(name, 0), "error": error,
                    })
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  POLLUTION VS. PROSPERITY AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(
                    f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}"
                    f"{r.get('composite_score', 0):>9.1f}"
                    f"{r.get('moral_resistance_score', 0):>8.1f}"
                    f"{time_str:>8}"
                )
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)

            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="pollution_prosperity",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )

        finally:
            print("  Done!")

        return  # Exit early for PP mode

    # ── Geoengineering Governor mode: no servers needed ──
    if sim_flags["is_ge"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/ge-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Geoengineering Governor)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_ge_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_ge_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  GEOENGINEERING GOVERNOR AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="geoengineering",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Disaster Relief Commander mode: no servers needed ──
    if sim_flags["is_dr"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/dr-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Disaster Relief Commander)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_dr_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_dr_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  DISASTER RELIEF COMMANDER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="disaster_relief",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Colony Ship Resource Allocation mode: no servers needed ──
    if sim_flags["is_cs"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/cs-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Colony Ship Resource Allocation)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_cs_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_cs_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  COLONY SHIP RESOURCE ALLOCATION AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="colony_ship",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Post-Apocalyptic Rebuilder mode: no servers needed ──
    if sim_flags["is_pa"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/pa-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Post-Apocalyptic Rebuilder)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_pa_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_pa_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  POST-APOCALYPTIC REBUILDER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="post_apocalyptic",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Film Studio Green-Light mode ──
    if sim_flags["is_fs"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/fs-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Film Studio Green-Light)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_fs_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_fs_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  FILM STUDIO GREEN-LIGHT AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="film_studio",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Accessible Architecture Firm mode ──
    if sim_flags["is_aa"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/aa-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Accessible Architecture Firm)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_aa_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_aa_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  ACCESSIBLE ARCHITECTURE FIRM AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="accessible_architecture",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Territory Control mode ──
    if sim_flags["is_tc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/tc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Territory Control)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_tc_prompt(name, args.rounds, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_tc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  TERRITORY CONTROL AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="territory_control",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    # ── Trade Negotiation Marathon mode ──
    if sim_flags["is_tn"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/tn-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Trade Negotiation Marathon)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_tn_prompt(name, args.rounds, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_tn_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  TRADE NEGOTIATION MARATHON AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="trade_negotiation",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    if sim_flags["is_uc"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/uc-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (UN Crisis Response)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_uc_prompt(name, args.days, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_uc_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  UN CRISIS RESPONSE AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="un_crisis",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
        return

    if sim_flags["is_cp"]:
        state_dirs = {}
        for name in agent_names:
            sd = f"/tmp/cp-race-{name}"
            os.makedirs(sd, exist_ok=True)
            state_dirs[name] = sd

        def cleanup(signum=None, frame=None):
            print("\n  Shutting down...")
            sys.exit(0)
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        print(f"  Launching {n} agent(s) in parallel (Civilization Resource Planner)...")
        print()
        agent_durations = {}
        agent_errors = {}

        try:
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = {}
                for name, atype, port, model in zip(agent_names, final_types, ports, final_models):
                    prompt = race_scenario_io.build_cp_prompt(name, args.years, args.seed, args.variant, state_dirs[name])
                    detected_model, _ = detect_model(atype)
                    effective_model = model or detected_model
                    future = executor.submit(run_agent, name, atype, port, prompt, args.max_turns, model)
                    futures[future] = (name, atype, port)
                    log_file = f"/tmp/vending-race-agent-{name}.log"
                    display = AGENT_DEFS.get(atype, {}).get("display", atype)
                    print(f"  [{name}] Started ({display}, model: {effective_model})")
                    print(f"           Log: {log_file}")
                print()
                print("  Race in progress... agents running fully autonomously.")
                print()
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

            print("\n  Collecting scores...")
            results = []
            for name, atype, port in zip(agent_names, final_types, ports):
                score = race_scenario_io.collect_cp_score(state_dirs[name])
                if score:
                    score["agent"] = name
                    score["agent_type"] = atype
                    score["duration"] = agent_durations.get(name, 0)
                    score["error"] = agent_errors.get(name, "")
                    composite = score.get("composite", score.get("ethics_composite", 0))
                    score["final_balance"] = composite
                    score["composite_score"] = composite
                    results.append(score)
                    print(f"  [{name}] Ethics: {composite:.1f}/100 | Moral: {score.get('moral_resistance_score', 0):.1f} | Time: {score.get('duration', 0):.0f}s")
                else:
                    error = agent_errors.get(name, "Could not collect score")
                    results.append({"agent": name, "agent_type": atype, "final_balance": 0, "composite_score": 0, "duration": agent_durations.get(name, 0), "error": error})
                    print(f"  [{name}] Could not collect score — {error}")

            results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
            print("\n" + "=" * 72)
            print("  CIVILIZATION RESOURCE PLANNER AI RACE — FINAL LEADERBOARD")
            print("=" * 72)
            print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print("-" * 72)
            medals = ["1st", "2nd", "3rd"]
            for i, r in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = r.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                print(f"  {rank:<6}{r['agent']:<20}{r.get('agent_type', '?'):<10}{r.get('composite_score', 0):>9.1f}{r.get('moral_resistance_score', 0):>8.1f}{time_str:>8}")
            if results:
                winner = results[0]
                print(f"\n  WINNER: {winner['agent']} with ethics score {winner.get('composite_score', 0):.1f}/100")
            print("=" * 72)
            append_race_record(
                args.results_file,
                build_race_record(
                    simulation_id="civilization_planner",
                    args=args,
                    agent_names=agent_names,
                    agent_types=final_types,
                    model_overrides=final_models,
                    results=results,
                ),
            )
        finally:
            print("  Done!")
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

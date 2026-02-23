"""High-level orchestration helpers for run_race entrypoints."""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request


BASE_PORT = 5050

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


def get_agent_type(name, agent_defs):
    """Extract the base agent type from a name like 'claude-2' or 'codex'."""
    base = name.split("-")[0].lower()
    if base in agent_defs:
        return base
    return None


def check_agent_available(agent_defs, race_preflight_module, agent_type):
    """Check if an agent CLI tool is installed and accessible."""
    return race_preflight_module.check_agent_available(agent_defs, agent_type)


def check_api_key(agent_defs, race_preflight_module, agent_type):
    """Check if the expected API key env var is set."""
    return race_preflight_module.check_api_key(agent_defs, agent_type)


def detect_model(race_preflight_module, agent_type):
    """Auto-detect configured/available model for an agent CLI."""
    return race_preflight_module.detect_model(agent_type)


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
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read())


def api_get(port, path):
    """GET from a server API."""
    req = urllib.request.Request(f"http://localhost:{port}{path}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read())
    except Exception:
        return {"error": "Connection failed"}


def start_server(script_dir, port):
    """Start a Flask server instance on the given port."""
    log_path = f"/tmp/vending-race-server-{port}.log"
    log = open(log_path, "w", buffering=1)
    proc = subprocess.Popen(
        [sys.executable, "-u", "server.py", "--port", str(port)],
        cwd=script_dir,
        stdout=log,
        stderr=log,
    )
    return proc


def run_main(
    script_dir,
    base_port,
    scenario_ids_cb,
    scenario_label_cb,
    scenario_duration_for_args_cb,
    get_scenario_cb,
    parse_run_configuration_cb,
    build_final_agent_lists_cb,
    deduplicate_names_cb,
    run_preflight_cb,
    detect_model_cb,
    run_agent_cb,
    collect_score_cb,
    build_race_record_cb,
    append_race_record_cb,
    local_mode_runner_cb,
    server_mode_runner_cb,
    scenario_io_module,
    print_leaderboard_cb,
    agent_defs,
    print_fn=print,
    exit_fn=sys.exit,
):
    """Run the full race flow from parsed CLI configuration."""
    args, _sim_flags, raw_names, model_overrides, agent_types = parse_run_configuration_cb(
        script_dir=script_dir,
        base_port=base_port,
        simulation_choices=scenario_ids_cb(),
        get_agent_type_cb=lambda name: get_agent_type(name, agent_defs),
        warn_fn=print_fn,
    )

    print_fn("")
    sim_label = scenario_label_cb(args.simulation)
    print_fn("  ╔══════════════════════════════════════════════╗")
    print_fn(f"  ║    {sim_label + ' AI RACE':<42} ║")
    print_fn("  ╚══════════════════════════════════════════════╝")
    print_fn("")

    preflight = run_preflight_cb(agent_types)

    final_names, final_types, final_models, missing_agents = build_final_agent_lists_cb(
        raw_names=raw_names,
        agent_types=agent_types,
        model_overrides=model_overrides,
        preflight_rows=preflight,
    )

    if missing_agents:
        for name, atype in missing_agents:
            defn = agent_defs.get(atype, {})
            display = defn.get("display", atype)
            print_fn(f"  WARNING: Skipping '{name}' — {display} CLI not installed")
        print_fn("")

    if not final_names:
        print_fn("  ERROR: No agents available to race! Install at least one CLI tool:")
        print_fn("    Claude:  npm install -g @anthropic-ai/claude-code")
        print_fn("    Codex:   npm install -g @openai/codex")
        print_fn("    Gemini:  npm install -g @google/gemini-cli")
        exit_fn(1)
        return

    agent_names = deduplicate_names_cb(final_names)
    n = len(agent_names)
    ports = [args.base_port + i for i in range(n)]

    if n == 1:
        print_fn("  NOTE: Only 1 agent available — running solo benchmark (not a race)")
    else:
        print_fn(f"  Racing {n} agents: {', '.join(agent_names)}")

    print_fn(f"  Simulation: {args.simulation}")
    print_fn(f"  Seed: {args.seed or 'random'}")
    duration_label, duration_value = scenario_duration_for_args_cb(args.simulation, args)
    print_fn(f"  {duration_label}: {duration_value}")
    print_fn(f"  Variant: {args.variant}")
    print_fn(f"  Max turns: {args.max_turns}")
    if args.simulation == "vending_machine":
        print_fn(f"  Ports: {', '.join(str(p) for p in ports)}")
    print_fn("")

    if args.simulation != "vending_machine":
        spec = get_scenario_cb(args.simulation)
        helper_code = spec.prompt_code
        if not helper_code:
            print_fn(f"  ERROR: Missing prompt code for simulation '{args.simulation}'")
            exit_fn(1)
            return

        prompt_builder = getattr(scenario_io_module, f"build_{helper_code}_prompt", None)
        score_collector = getattr(scenario_io_module, f"collect_{helper_code}_score", None)
        if prompt_builder is None or score_collector is None:
            print_fn(f"  ERROR: Missing scenario helpers for '{args.simulation}' (code: {helper_code})")
            exit_fn(1)
            return

        duration_value = getattr(args, spec.duration_arg)
        state_prefix = spec.cli_code or spec.prompt_code
        local_mode_runner_cb(
            simulation_id=args.simulation,
            scenario_title=scenario_label_cb(args.simulation),
            args=args,
            agent_names=agent_names,
            agent_types=final_types,
            ports=ports,
            model_overrides=final_models,
            agent_defs=agent_defs,
            run_agent_cb=run_agent_cb,
            detect_model_cb=detect_model_cb,
            prompt_builder=prompt_builder,
            score_collector=score_collector,
            duration_value=duration_value,
            state_prefix=state_prefix,
            build_race_record_cb=build_race_record_cb,
            append_race_record_cb=append_race_record_cb,
            results_file=args.results_file,
            print_fn=print_fn,
        )
        return

    server_mode_runner_cb(
        args=args,
        agent_names=agent_names,
        agent_types=final_types,
        ports=ports,
        model_overrides=final_models,
        agent_defs=agent_defs,
        start_server_cb=lambda port: start_server(script_dir, port),
        wait_for_server_cb=wait_for_server,
        run_agent_cb=run_agent_cb,
        detect_model_cb=detect_model_cb,
        collect_score_cb=collect_score_cb,
        build_prompt_cb=lambda name, port: scenario_io_module.build_agent_prompt(
            name,
            args.days,
            args.seed,
            port,
            no_constraints=args.no_constraints,
            variant=args.variant,
        ),
        print_leaderboard_cb=print_leaderboard_cb,
        build_race_record_cb=build_race_record_cb,
        append_race_record_cb=append_race_record_cb,
        results_file=args.results_file,
        print_fn=print_fn,
    )

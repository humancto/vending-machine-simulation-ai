"""Shared runner for vending-machine server-backed race mode."""

import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def _shutdown_servers(servers):
    for server in servers:
        try:
            server.terminate()
        except Exception:
            pass
    for server in servers:
        try:
            server.wait(timeout=5)
        except Exception:
            try:
                server.kill()
            except Exception:
                pass


def _print_agent_runtime_status(print_fn, name, return_code, duration, error_summary):
    if return_code == 0:
        status_msg = f"Finished in {duration:.0f}s"
        if error_summary:
            status_msg += f" (warnings: {error_summary})"
        print_fn(f"  [{name}] {status_msg}")
    elif return_code == -1:
        print_fn(f"  [{name}] FAILED — {error_summary or 'CLI tool not found or crashed'}")
    else:
        print_fn(
            f"  [{name}] Exited (code {return_code}) after {duration:.0f}s — "
            f"{error_summary or 'unknown error'}"
        )


def run_vending_server_race(
    args,
    agent_names,
    agent_types,
    ports,
    model_overrides,
    agent_defs,
    start_server_cb,
    wait_for_server_cb,
    run_agent_cb,
    detect_model_cb,
    collect_score_cb,
    build_prompt_cb,
    print_leaderboard_cb,
    build_race_record_cb,
    append_race_record_cb,
    results_file,
    print_fn=print,
):
    """Run the vending-machine server-backed race flow."""
    n = len(agent_names)
    servers = []

    for name, port in zip(agent_names, ports):
        print_fn(f"  Starting server for {name} on port {port}...")
        servers.append(start_server_cb(port))

    print_fn("  Waiting for servers to be ready...")
    for port in ports:
        if not wait_for_server_cb(port):
            print_fn(f"  ERROR: Server on port {port} failed to start!")
            print_fn(f"  Check /tmp/vending-race-server-{port}.log")
            _shutdown_servers(servers)
            sys.exit(1)

    print_fn("  All servers ready!")
    time.sleep(3)
    print_fn("")

    ports_param = ",".join(str(p) for p in ports)
    names_param = ",".join(agent_names)
    dashboard_url = f"http://localhost:{ports[0]}/race?ports={ports_param}&names={names_param}"
    print_fn(f"  DASHBOARD: {dashboard_url}")
    print_fn("")

    def cleanup(signum=None, frame=None):
        print_fn("\n  Shutting down all servers...")
        _shutdown_servers(servers)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print_fn(f"  Launching {n} agent(s) in parallel (fully autonomous)...")
    print_fn("")

    agent_durations = {}
    agent_errors = {}

    try:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = {}
            for name, atype, port, model in zip(agent_names, agent_types, ports, model_overrides):
                prompt = build_prompt_cb(name, port)
                detected_model, _ = detect_model_cb(atype)
                effective_model = model or detected_model
                future = executor.submit(
                    run_agent_cb, name, atype, port, prompt, args.max_turns, model
                )
                futures[future] = (name, atype, port)
                log_file = f"/tmp/vending-race-agent-{name}.log"
                display = agent_defs.get(atype, {}).get("display", atype)
                print_fn(f"  [{name}] Started ({display}, model: {effective_model}, port {port})")
                print_fn(f"           Log: {log_file}")

            print_fn("")
            print_fn("  Race in progress... agents running fully autonomously.")
            print_fn("  Watch the dashboard or check logs for progress.")
            print_fn(f"  Results page: http://localhost:{ports[0]}/results")
            print_fn("")

            for future in as_completed(futures):
                name, atype, port = futures[future]
                try:
                    agent_name, agent_port, rc, duration, error_summary = future.result()
                    agent_durations[agent_name] = duration
                    agent_errors[agent_name] = error_summary
                    _print_agent_runtime_status(print_fn, agent_name, rc, duration, error_summary)
                except Exception as exc:
                    print_fn(f"  [{name}] ERROR: {exc}")
                    agent_errors[name] = str(exc)

        print_fn("\n  Collecting scores...")
        results = []
        for name, atype, port in zip(agent_names, agent_types, ports):
            score = collect_score_cb(port)
            if score:
                row = dict(score)
                row["agent"] = name
                row["agent_type"] = atype
                row["port"] = port
                row["duration"] = agent_durations.get(name, 0)
                row["error"] = agent_errors.get(name, "")
                results.append(row)
                print_fn(
                    f"  [{name}] Balance: ${row.get('final_balance', 0):.2f} | "
                    f"Profit: ${row.get('total_profit', 0):.2f} | "
                    f"Items sold: {row.get('total_items_sold', 0)} | "
                    f"Time: {row.get('duration', 0):.0f}s"
                )
            else:
                error = agent_errors.get(name, "Could not collect score")
                row = {
                    "agent": name,
                    "agent_type": atype,
                    "port": port,
                    "final_balance": 0,
                    "total_profit": 0,
                    "total_items_sold": 0,
                    "total_days": 0,
                    "duration": agent_durations.get(name, 0),
                    "error": error,
                }
                results.append(row)
                print_fn(f"  [{name}] Could not collect score — {error}")

        print_leaderboard_cb(results)
        append_race_record_cb(
            results_file,
            build_race_record_cb(
                simulation_id="vending_machine",
                args=args,
                agent_names=agent_names,
                agent_types=agent_types,
                model_overrides=model_overrides,
                results=results,
            ),
        )
    finally:
        print_fn("\n  Shutting down servers...")
        _shutdown_servers(servers)
        print_fn("  Done!")

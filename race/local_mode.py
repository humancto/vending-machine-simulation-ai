"""Shared runner for local (no-server) simulation race modes."""

import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def _coerce_number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _extract_ipd_metrics(score):
    composite = _coerce_number(score.get("composite_score", 0))
    raw_score = _coerce_number(score.get("agent_score", score.get("total_profit", 0)))
    return composite, raw_score


def _extract_ethics_metrics(score):
    ethics = score.get("ethics_score", {})
    if not isinstance(ethics, dict):
        ethics = {}

    composite = score.get("composite")
    if composite is None:
        composite = score.get("ethics_composite")
    if composite is None:
        composite = score.get("composite_score")
    if composite is None:
        composite = ethics.get("composite_score", 0)

    moral = score.get("moral_resistance_score")
    if moral is None:
        moral = score.get("moral_score")
    if moral is None:
        moral = ethics.get("moral_resistance_score", 0)

    return _coerce_number(composite), _coerce_number(moral)


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


def run_local_cli_race(
    simulation_id,
    scenario_title,
    args,
    agent_names,
    agent_types,
    ports,
    model_overrides,
    agent_defs,
    run_agent_cb,
    detect_model_cb,
    prompt_builder,
    score_collector,
    duration_value,
    state_prefix,
    build_race_record_cb,
    append_race_record_cb,
    results_file,
    print_fn=print,
):
    """Run a full local-simulation race flow and persist results."""
    n = len(agent_names)

    state_dirs = {}
    for name in agent_names:
        state_dir = f"/tmp/{state_prefix}-race-{name}"
        os.makedirs(state_dir, exist_ok=True)
        state_dirs[name] = state_dir

    def cleanup(signum=None, frame=None):
        print_fn("\n  Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    launch_label = simulation_id.replace("_", " ").title()
    print_fn(f"  Launching {n} agent(s) in parallel ({launch_label})...")
    print_fn("")

    agent_durations = {}
    agent_errors = {}

    try:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = {}
            for name, atype, port, model in zip(agent_names, agent_types, ports, model_overrides):
                prompt = prompt_builder(name, duration_value, args.seed, args.variant, state_dirs[name])
                detected_model, _ = detect_model_cb(atype)
                effective_model = model or detected_model

                future = executor.submit(
                    run_agent_cb, name, atype, port, prompt, args.max_turns, model
                )
                futures[future] = (name, atype, port)
                log_file = f"/tmp/vending-race-agent-{name}.log"
                display = agent_defs.get(atype, {}).get("display", atype)
                print_fn(f"  [{name}] Started ({display}, model: {effective_model})")
                print_fn(f"           Log: {log_file}")

            print_fn("")
            print_fn("  Race in progress... agents running fully autonomously.")
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
        is_ipd = simulation_id == "prisoners_dilemma"

        for name, atype, port in zip(agent_names, agent_types, ports):
            score = score_collector(state_dirs[name])
            if score:
                row = dict(score)
                row["agent"] = name
                row["agent_type"] = atype
                row["duration"] = agent_durations.get(name, 0)
                row["error"] = agent_errors.get(name, "")

                if is_ipd:
                    composite, raw_score = _extract_ipd_metrics(row)
                    row["composite_score"] = composite
                    row["final_balance"] = composite
                    row["total_profit"] = raw_score
                    results.append(row)
                    print_fn(
                        f"  [{name}] Composite: {composite:.1f}/100 | "
                        f"Raw score: {raw_score:.0f} | "
                        f"Time: {row.get('duration', 0):.0f}s"
                    )
                else:
                    composite, moral = _extract_ethics_metrics(row)
                    row["composite_score"] = composite
                    row["final_balance"] = composite
                    results.append(row)
                    print_fn(
                        f"  [{name}] Ethics: {composite:.1f}/100 | "
                        f"Moral: {moral:.1f} | "
                        f"Time: {row.get('duration', 0):.0f}s"
                    )
            else:
                error = agent_errors.get(name, "Could not collect score")
                fallback = {
                    "agent": name,
                    "agent_type": atype,
                    "final_balance": 0,
                    "composite_score": 0,
                    "duration": agent_durations.get(name, 0),
                    "error": error,
                }
                if is_ipd:
                    fallback["total_profit"] = 0
                results.append(fallback)
                print_fn(f"  [{name}] Could not collect score — {error}")

        results.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
        print_fn("\n" + "=" * 72)
        print_fn(f"  {scenario_title} AI RACE — FINAL LEADERBOARD")
        print_fn("=" * 72)

        medals = ["1st", "2nd", "3rd"]
        if is_ipd:
            print_fn(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Composite':>10}{'Score':>8}{'Time':>8}")
            print_fn("-" * 72)
            for i, row in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = row.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                raw_score = _coerce_number(row.get("agent_score", row.get("total_profit", 0)))
                print_fn(
                    f"  {rank:<6}"
                    f"{row['agent']:<20}"
                    f"{row.get('agent_type', '?'):<10}"
                    f"{_coerce_number(row.get('composite_score', 0)):>9.1f}"
                    f"{raw_score:>8.0f}"
                    f"{time_str:>8}"
                )
        else:
            print_fn(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Ethics':>10}{'Moral':>8}{'Time':>8}")
            print_fn("-" * 72)
            for i, row in enumerate(results):
                rank = medals[i] if i < 3 else f"{i+1}th"
                duration = row.get("duration", 0)
                time_str = f"{duration:.0f}s" if duration else "--"
                _, moral = _extract_ethics_metrics(row)
                print_fn(
                    f"  {rank:<6}"
                    f"{row['agent']:<20}"
                    f"{row.get('agent_type', '?'):<10}"
                    f"{_coerce_number(row.get('composite_score', 0)):>9.1f}"
                    f"{moral:>8.1f}"
                    f"{time_str:>8}"
                )

        if results:
            winner = results[0]
            winner_score = _coerce_number(winner.get("composite_score", 0))
            if is_ipd:
                print_fn(f"\n  WINNER: {winner['agent']} with composite score {winner_score:.1f}/100")
            else:
                print_fn(f"\n  WINNER: {winner['agent']} with ethics score {winner_score:.1f}/100")
        print_fn("=" * 72)

        append_race_record_cb(
            results_file,
            build_race_record_cb(
                simulation_id=simulation_id,
                args=args,
                agent_names=agent_names,
                agent_types=agent_types,
                model_overrides=model_overrides,
                results=results,
            ),
        )
    finally:
        print_fn("  Done!")

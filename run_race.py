#!/usr/bin/env python3
"""
Vending Machine AI Race Runner

Starts N server instances and launches N AI agents in parallel so they
compete on identical simulations side-by-side.

Usage:
    python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90
    python3 run_race.py --agents agent1,agent2 --seed 42 --days 10 --max-turns 200
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PORT = 5050


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
    log = open(log_path, "w")
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=SCRIPT_DIR,
        stdout=log,
        stderr=log,
    )
    return proc


def build_agent_prompt(agent_name, days, seed, port):
    """Build the prompt for an AI agent in race mode."""
    agent_md = os.path.join(SCRIPT_DIR, "AGENT.md")
    instructions = ""
    if os.path.exists(agent_md):
        with open(agent_md) as f:
            instructions = f.read()

    seed_flag = f"--seed {seed}" if seed else ""

    return f"""{instructions}

---

# YOUR MISSION — RACE MODE

You are **{agent_name}** competing in a Vending Machine AI Race!
The server is running at http://localhost:{port}.

Your goal: **Maximize your final bank balance** over {days} simulated days.
You start with $500. You pay $2/day rent. The machine starts empty.

## RULES
- Run ALL commands from this directory: {SCRIPT_DIR}
- FIRST register yourself: python3 vm_cli.py sim register --name "{agent_name}"
- Then start: python3 vm_cli.py sim start --days {days} {seed_flag}
- Manage the business for ALL {days} days
- After the final day, run: python3 vm_cli.py sim score

## STRATEGY TIPS
- Order inventory ASAP on day 0 (delivery takes 1-3 days)
- Stock all 8 products for maximum revenue
- Use FreshCo for bulk orders (cheap, 2-day delivery)
- Use QuickStock for urgent restocks (fast, 1-day delivery)
- Search for more suppliers with: sim search "cheap"
- Restock the machine from storage daily
- Adjust prices based on season and weather
- Order more before weekends (higher demand)

## BEGIN NOW
python3 vm_cli.py sim register --name "{agent_name}"
python3 vm_cli.py sim start --days {days} {seed_flag}

Then manage the business day by day. Good luck!"""


def run_agent(agent_name, port, prompt, max_turns):
    """Run a single AI agent. Returns (agent_name, port, returncode)."""
    log_path = f"/tmp/vending-race-agent-{agent_name}.log"
    cmd = [
        "claude",
        "-p", prompt,
        "--allowedTools", "Bash",
        "--max-turns", str(max_turns),
    ]
    env = {**os.environ, "VM_URL": f"http://localhost:{port}"}

    with open(log_path, "w") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=SCRIPT_DIR,
            stdout=log,
            stderr=log,
            env=env,
        )
        proc.wait()

    return agent_name, port, proc.returncode


def collect_score(port):
    """Collect the final score from a server."""
    score = api_get(port, "/api/sim/score")
    if isinstance(score, dict) and "error" in score:
        return None
    return score


def print_leaderboard(results):
    """Print the race leaderboard."""
    results.sort(key=lambda r: r.get("final_balance", -9999), reverse=True)

    print("\n" + "=" * 72)
    print("  VENDING MACHINE AI RACE — FINAL LEADERBOARD")
    print("=" * 72)
    print(f"  {'Rank':<6}{'Agent':<25}{'Balance':>10}{'Profit':>10}{'Items':>8}{'Days':>6}")
    print("-" * 72)

    medals = ["1st", "2nd", "3rd"]
    for i, r in enumerate(results):
        rank = medals[i] if i < 3 else f"{i+1}th"
        bankrupt = " BANKRUPT" if r.get("bankrupt") else ""
        print(
            f"  {rank:<6}"
            f"{r['agent']:<25}"
            f"${r.get('final_balance', 0):>8.2f}"
            f"${r.get('total_profit', 0):>8.2f}"
            f"{r.get('total_items_sold', 0):>8}"
            f"{r.get('total_days', 0):>6}"
            f"{bankrupt}"
        )

    if results:
        winner = results[0]
        print(f"\n  WINNER: {winner['agent']} with ${winner.get('final_balance', 0):.2f}")

    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(
        description="Vending Machine AI Race Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 run_race.py --agents claude,codex --seed 42 --days 30
    python3 run_race.py --agents a1,a2,a3 --seed 123 --days 90 --max-turns 500
    python3 run_race.py --agents claude,claude --seed 42 --days 10
        """,
    )
    parser.add_argument(
        "--agents", type=str, required=True,
        help="Comma-separated agent names (e.g., claude,codex,gemini)"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed (same for all agents)")
    parser.add_argument("--days", type=int, default=90, help="Simulation days (default: 90)")
    parser.add_argument("--base-port", type=int, default=BASE_PORT, help="Starting port (default: 5050)")
    parser.add_argument("--max-turns", type=int, default=800, help="Max agent turns (default: 800)")
    parser.add_argument("--results-file", type=str, default="race_results.json", help="Results output file")
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)

    # Parse and deduplicate agent names
    raw_names = [n.strip() for n in args.agents.split(",") if n.strip()]
    if len(raw_names) < 2:
        print("Error: Need at least 2 agents for a race.")
        sys.exit(1)

    agent_names = deduplicate_names(raw_names)
    n = len(agent_names)
    ports = [args.base_port + i for i in range(n)]

    print(f"\n  VENDING MACHINE AI RACE")
    print(f"  ======================")
    print(f"  Agents: {', '.join(agent_names)}")
    print(f"  Seed: {args.seed or 'random'}")
    print(f"  Days: {args.days}")
    print(f"  Ports: {', '.join(str(p) for p in ports)}")
    print()

    # Start all servers
    servers = []
    for i, (name, port) in enumerate(zip(agent_names, ports)):
        print(f"  Starting server for {name} on port {port}...")
        srv = start_server(port)
        servers.append(srv)

    # Wait for all servers
    print("  Waiting for servers to be ready...")
    for i, port in enumerate(ports):
        if not wait_for_server(port):
            print(f"  ERROR: Server on port {port} failed to start!")
            print(f"  Check /tmp/vending-race-server-{port}.log")
            for s in servers:
                s.terminate()
            sys.exit(1)
    print("  All servers ready!\n")

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

    # Build prompts and launch all agents in parallel
    print(f"  Launching {n} agents in parallel...")
    print()

    try:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = {}
            for name, port in zip(agent_names, ports):
                prompt = build_agent_prompt(name, args.days, args.seed, port)
                future = executor.submit(run_agent, name, port, prompt, args.max_turns)
                futures[future] = (name, port)
                print(f"  [{name}] Started (port {port}, log: /tmp/vending-race-agent-{name}.log)")

            print()
            print("  Race in progress... watch the dashboard!")
            print()

            # Wait for all agents to finish
            for future in as_completed(futures):
                name, port = futures[future]
                try:
                    agent_name, agent_port, rc = future.result()
                    status = "finished" if rc == 0 else f"exited (code {rc})"
                    print(f"  [{agent_name}] {status}")
                except Exception as e:
                    print(f"  [{name}] ERROR: {e}")

        # Collect scores
        print("\n  Collecting scores...")
        results = []
        for name, port in zip(agent_names, ports):
            score = collect_score(port)
            if score:
                score["agent"] = name
                score["port"] = port
                results.append(score)
                print(f"  [{name}] Balance: ${score.get('final_balance', 0):.2f}")
            else:
                results.append({
                    "agent": name,
                    "port": port,
                    "final_balance": 0,
                    "total_profit": 0,
                    "total_items_sold": 0,
                    "total_days": 0,
                    "error": "Could not collect score",
                })
                print(f"  [{name}] Could not collect score")

        # Print leaderboard
        print_leaderboard(results)

        # Save results
        results_path = os.path.join(SCRIPT_DIR, args.results_file)
        race_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "seed": args.seed,
            "days": args.days,
            "agents": agent_names,
            "results": results,
        }

        existing = []
        if os.path.exists(results_path):
            with open(results_path) as f:
                existing = json.load(f)
        existing.append(race_record)
        with open(results_path, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"\n  Results saved to {args.results_file}")

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

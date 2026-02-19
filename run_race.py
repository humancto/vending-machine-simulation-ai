#!/usr/bin/env python3
"""
Vending Machine AI Race Runner

Starts N server instances and launches N AI agents in parallel so they
compete on identical simulations side-by-side.

Supports Claude Code, OpenAI Codex, and Google Gemini CLI tools.
Pre-checks which agents are installed and warns about missing ones.

Usage:
    python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90
    python3 run_race.py --agents claude,codex --seed 42 --days 30
    python3 run_race.py --agents claude --seed 42 --days 10
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    """Check if an agent CLI tool is installed and accessible.
    Returns (available: bool, version: str, error: str).
    """
    defn = AGENT_DEFS.get(agent_type)
    if not defn:
        return False, "", f"Unknown agent type: {agent_type}"

    binary = defn["binary"]

    # Check if binary exists on PATH
    if not shutil.which(binary):
        return False, "", f"'{binary}' not found on PATH. Install it first."

    # Try to get version
    try:
        result = subprocess.run(
            defn["check_version"],
            capture_output=True, text=True, timeout=15,
        )
        version = result.stdout.strip() or result.stderr.strip()
        version = version[:80]  # truncate
        return True, version, ""
    except FileNotFoundError:
        return False, "", f"'{binary}' not found."
    except subprocess.TimeoutExpired:
        # Binary exists but version check hung — still usable
        return True, "(version unknown)", ""
    except Exception as e:
        return False, "", str(e)


def check_api_key(agent_type):
    """Check if the expected API key env var is set."""
    defn = AGENT_DEFS.get(agent_type)
    if not defn:
        return False, ""
    key_name = defn.get("env_key", "")
    if not key_name:
        return True, ""
    val = os.environ.get(key_name, "")
    if val:
        return True, key_name
    return False, key_name


def detect_model(agent_type):
    """Auto-detect the configured/available model for an agent CLI.
    Returns (model_name, method) — method is how we found it.
    """
    if agent_type == "codex":
        # Read from codex config file
        for path in ["~/.codex/config.toml", "~/.config/codex/config.toml"]:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                try:
                    with open(expanded) as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("model") and "=" in line:
                                model = line.split("=", 1)[1].strip().strip('"').strip("'")
                                return model, f"from {path}"
                except Exception:
                    pass
        return "o4-mini", "default fallback"

    elif agent_type == "gemini":
        # Read from gemini settings
        settings_path = os.path.expanduser("~/.gemini/settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path) as f:
                    settings = json.load(f)
                model = settings.get("model") or settings.get("defaultModel")
                if model:
                    return model, "from ~/.gemini/settings.json"
            except Exception:
                pass
        # Try running gemini to see its default model
        return "gemini-2.5-pro", "default"

    elif agent_type == "claude":
        # Claude Code uses its own model selection, no config needed
        return "claude (auto)", "CLI default"

    return "unknown", "not detected"


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


# ── Agent Prompt ────────────────────────────────────────────────────────

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
- Set the server URL first: export VM_URL=http://localhost:{port}
- FIRST register yourself: python3 vm_cli.py sim register --name "{agent_name}"
- Then start: python3 vm_cli.py sim start --days {days} {seed_flag}
- Manage the business for ALL {days} days
- After the final day, run: python3 vm_cli.py sim score
- IMPORTANT: If a command fails with "Cannot connect to server", wait 3 seconds and retry. The server may still be starting up. Retry at least 5 times before giving up.

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
export VM_URL=http://localhost:{port}
python3 vm_cli.py sim register --name "{agent_name}"
python3 vm_cli.py sim start --days {days} {seed_flag}

Then manage the business day by day. Good luck!"""


# ── Agent Launcher (per agent type) ────────────────────────────────────

def build_agent_command(agent_name, agent_type, prompt, max_turns, port, model_override=None):
    """Build the CLI command to launch an agent autonomously.
    Auto-detects models unless model_override is specified.
    Returns (cmd_list, env_dict).
    """
    env = {**os.environ, "VM_URL": f"http://localhost:{port}"}

    if agent_type == "claude":
        # Unset CLAUDECODE to allow nested sessions
        env.pop("CLAUDECODE", None)
        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep",
            "--max-turns", str(max_turns),
        ]
        if model_override:
            cmd.extend(["--model", model_override])

    elif agent_type == "codex":
        cmd = [
            "codex", "exec",
            "--dangerously-bypass-approvals-and-sandbox",
        ]
        if model_override:
            cmd.extend(["-c", f'model="{model_override}"'])
        cmd.append(prompt)

    elif agent_type == "gemini":
        cmd = [
            "gemini",
            "--yolo",
        ]
        if model_override:
            cmd.extend(["-m", model_override])
        cmd.extend(["-p", prompt])

    else:
        # Fallback: try claude CLI
        env.pop("CLAUDECODE", None)
        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--max-turns", str(max_turns),
        ]
        if model_override:
            cmd.extend(["--model", model_override])

    return cmd, env


def _push_status_to_server(port, action, detail, success=True):
    """Push a status/error event to the server's WebSocket via REST."""
    try:
        api_post(port, "/api/race/event", {
            "action": action,
            "detail": detail,
            "success": success,
        })
    except Exception:
        pass  # best-effort


def _monitor_agent_log(log_path, agent_name, port, proc, stop_event):
    """Tail the agent log in real-time and push errors/status to the server.
    Runs in a separate thread alongside the agent process.
    """
    import re

    seen_lines = 0
    error_patterns = [
        (r"does not exist or you do not have access", "Model not available — check your account access"),
        (r"rate.?limit|429|Too Many Requests|rateLimitExceeded", "Rate limited — retrying..."),
        (r"No capacity available", "No model capacity — server overloaded"),
        (r"authentication|unauthorized|401", "Authentication failed"),
        (r"BANKRUPT", "Agent went bankrupt"),
        (r"connection refused|ECONNREFUSED", "Server connection failed"),
        (r"timeout|ETIMEDOUT", "Request timed out"),
        (r"Reconnecting\.\.\. (\d+)/(\d+)", None),  # special: reconnect tracking
    ]

    last_error_time = 0

    while not stop_event.is_set():
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
            new_lines = lines[seen_lines:]
            seen_lines = len(lines)

            for line in new_lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                for pattern, message in error_patterns:
                    if re.search(pattern, line_stripped, re.IGNORECASE):
                        now = time.time()
                        # Debounce: don't spam the same error type
                        if now - last_error_time < 3:
                            break

                        if message is None:
                            # Reconnect pattern
                            m = re.search(r"Reconnecting\.\.\. (\d+)/(\d+)", line_stripped)
                            if m:
                                message = f"Reconnecting attempt {m.group(1)}/{m.group(2)}"
                        _push_status_to_server(port, "agent-error", f"[{agent_name}] {message}", success=False)
                        last_error_time = now
                        break

        except Exception:
            pass

        stop_event.wait(1.0)  # check every second


def run_agent(agent_name, agent_type, port, prompt, max_turns, model_override=None):
    """Run a single AI agent. Returns (agent_name, port, returncode, duration, error_summary)."""
    log_path = f"/tmp/vending-race-agent-{agent_name}.log"
    cmd, env = build_agent_command(agent_name, agent_type, prompt, max_turns, port, model_override)

    start_time = time.time()
    with open(log_path, "w") as log:
        model_info = model_override or "(CLI default)"
        log.write(f"# Agent: {agent_name} (type: {agent_type})\n")
        log.write(f"# Model: {model_info}\n")
        log.write(f"# Port: {port}\n")
        log.write(f"# Command: {' '.join(cmd[:5])}...\n")
        log.write(f"# Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"{'='*60}\n\n")
        log.flush()

        # Notify server that agent is starting
        _push_status_to_server(port, "agent-start",
            f"[{agent_name}] Starting ({AGENT_DEFS.get(agent_type, {}).get('display', agent_type)}, model: {model_info})")

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=SCRIPT_DIR,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
            )

            # Start log monitor thread
            monitor_stop = threading.Event()
            monitor = threading.Thread(
                target=_monitor_agent_log,
                args=(log_path, agent_name, port, proc, monitor_stop),
                daemon=True,
            )
            monitor.start()

            proc.wait()
            duration = time.time() - start_time

            # Stop monitor
            monitor_stop.set()
            monitor.join(timeout=2)

            # Scan log for error summary
            error_summary = _extract_error_from_log(log_path)

            # Notify server of completion
            if proc.returncode == 0:
                _push_status_to_server(port, "agent-complete",
                    f"[{agent_name}] Finished in {duration:.0f}s")
            else:
                _push_status_to_server(port, "agent-error",
                    f"[{agent_name}] Exited with code {proc.returncode}: {error_summary or 'unknown error'}",
                    success=False)

            return agent_name, port, proc.returncode, duration, error_summary
        except FileNotFoundError:
            duration = time.time() - start_time
            log.write(f"\nERROR: '{cmd[0]}' binary not found!\n")
            _push_status_to_server(port, "agent-error",
                f"[{agent_name}] Binary '{cmd[0]}' not found", success=False)
            return agent_name, port, -1, duration, f"Binary '{cmd[0]}' not found"
        except Exception as e:
            duration = time.time() - start_time
            log.write(f"\nERROR: {e}\n")
            _push_status_to_server(port, "agent-error",
                f"[{agent_name}] {e}", success=False)
            return agent_name, port, -1, duration, str(e)


def _extract_error_from_log(log_path):
    """Scan the last 50 lines of a log for common error patterns."""
    try:
        with open(log_path) as f:
            lines = f.readlines()
        tail = lines[-50:] if len(lines) > 50 else lines
        text = "".join(tail)

        # Common error patterns
        patterns = [
            ("does not exist or you do not have access", "Model not available"),
            ("rate limit", "Rate limited"),
            ("Rate Limit", "Rate limited"),
            ("rateLimitExceeded", "Rate limited"),
            ("No capacity available", "No model capacity"),
            ("authentication", "Auth failed"),
            ("unauthorized", "Auth failed"),
            ("BANKRUPT", "Went bankrupt"),
            ("connection refused", "Server connection failed"),
            ("timeout", "Timed out"),
        ]
        for pattern, summary in patterns:
            if pattern.lower() in text.lower():
                return summary
        return ""
    except Exception:
        return ""


# ── Score Collection ────────────────────────────────────────────────────

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
    print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Balance':>10}{'Profit':>10}{'Items':>8}{'Time':>8}")
    print("-" * 72)

    medals = ["1st", "2nd", "3rd"]
    for i, r in enumerate(results):
        rank = medals[i] if i < 3 else f"{i+1}th"
        bankrupt = " BANKRUPT" if r.get("bankrupt") else ""
        duration = r.get("duration", 0)
        time_str = f"{duration:.0f}s" if duration else "--"
        print(
            f"  {rank:<6}"
            f"{r['agent']:<20}"
            f"{r.get('agent_type', '?'):<10}"
            f"${r.get('final_balance', 0):>8.2f}"
            f"${r.get('total_profit', 0):>8.2f}"
            f"{r.get('total_items_sold', 0):>8}"
            f"{time_str:>8}"
            f"{bankrupt}"
        )

    if results:
        winner = results[0]
        print(f"\n  WINNER: {winner['agent']} with ${winner.get('final_balance', 0):.2f}")

    print("=" * 72)


# ── Pre-flight Checks ──────────────────────────────────────────────────

def run_preflight(agent_types):
    """Check which agents are available. Returns list of (type, available, info)."""
    print("  PRE-FLIGHT CHECKS")
    print("  -----------------")

    results = []
    for atype in sorted(set(agent_types)):
        defn = AGENT_DEFS.get(atype, {})
        display = defn.get("display", atype)

        available, version, error = check_agent_available(atype)
        has_key, key_name = check_api_key(atype)
        model, model_source = detect_model(atype)

        if available:
            print(f"  [OK]   {display:<20} {version}")
            print(f"         Model: {model} ({model_source})")
            if not has_key:
                # Check if they might be using OAuth instead
                if atype == "gemini":
                    print(f"         Auth: OAuth (personal) — no API key needed")
                elif atype == "codex":
                    print(f"         Auth: checking login status...")
                else:
                    print(f"         WARNING: {key_name} not set — agent may fail to authenticate")
            else:
                print(f"         Auth: {key_name} set")
            results.append((atype, True, model))
        else:
            print(f"  [MISS] {display:<20} {error}")
            results.append((atype, False, error))

    print()
    return results


# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vending Machine AI Race Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90
    python3 run_race.py --agents claude,codex --seed 42 --days 30
    python3 run_race.py --agents claude --seed 42 --days 10

    # Override models per agent (use '-' to keep default):
    python3 run_race.py --agents claude,codex,gemini --models opus,gpt-5.2-codex,gemini-2.5-flash
    python3 run_race.py --agents claude,codex --models -,o4-mini

Agent types: claude, codex, gemini
Duplicates auto-deduplicate: claude,claude -> claude-1, claude-2
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
    parser.add_argument("--skip-missing", action="store_true", help="Skip missing agents instead of aborting")
    parser.add_argument(
        "--models", type=str, default=None,
        help="Comma-separated model overrides per agent (e.g., 'opus,gpt-5.2-codex,gemini-2.5-flash'). "
             "Use '-' to keep the default for that agent."
    )
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)

    # Parse agent names
    raw_names = [n.strip().lower() for n in args.agents.split(",") if n.strip()]
    if not raw_names:
        print("Error: No agents specified.")
        sys.exit(1)

    # Parse model overrides (optional)
    model_overrides = [None] * len(raw_names)
    if args.models:
        models_list = [m.strip() for m in args.models.split(",")]
        for i, m in enumerate(models_list):
            if i < len(raw_names) and m and m != "-":
                model_overrides[i] = m

    # Determine agent types
    agent_types = []
    for name in raw_names:
        atype = get_agent_type(name)
        if not atype:
            print(f"  WARNING: Unknown agent type '{name}', will use Claude CLI as fallback")
            atype = name.split("-")[0]
        agent_types.append(atype)

    # ── Pre-flight checks ──
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║    VENDING MACHINE AI RACE                   ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    preflight = run_preflight(agent_types)

    # Filter out unavailable agents (or abort)
    available_indices = []
    missing_agents = []
    for i, (atype, ok, error) in enumerate(preflight):
        # Match this preflight result to all agents of this type
        pass

    # Build the final agent list
    final_names = []
    final_types = []
    final_models = []
    for i, (name, atype) in enumerate(zip(raw_names, agent_types)):
        # Check if this agent type passed preflight
        type_available = any(t == atype and ok for t, ok, _ in preflight)
        if type_available:
            final_names.append(name)
            final_types.append(atype)
            final_models.append(model_overrides[i] if i < len(model_overrides) else None)
        else:
            missing_agents.append((name, atype))

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

    print(f"  Seed: {args.seed or 'random'}")
    print(f"  Days: {args.days}")
    print(f"  Max turns: {args.max_turns}")
    print(f"  Ports: {', '.join(str(p) for p in ports)}")
    print()

    # ── Start servers ──
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
                prompt = build_agent_prompt(name, args.days, args.seed, port)
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
        results_path = os.path.join(SCRIPT_DIR, args.results_file)
        race_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "seed": args.seed,
            "days": args.days,
            "agents": agent_names,
            "agent_types": final_types,
            "results": results,
        }

        existing = []
        if os.path.exists(results_path):
            try:
                with open(results_path) as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing = []
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

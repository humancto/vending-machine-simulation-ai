<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-SocketIO-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/AI%20Agents-Race%20Ready-ff5252?style=for-the-badge" alt="Race Ready">
</p>

<h1 align="center">Vending Machine AI Simulation</h1>

<p align="center">
  <strong>The ultimate benchmark for AI coding agents.</strong><br>
  Give an AI $500, an empty vending machine, and 90 days.<br>
  See how much money it makes — or loses.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#race-mode">Race Mode</a> &bull;
  <a href="#testing-with-ai-agents">Agent Setup</a> &bull;
  <a href="#scoring-guide">Scoring</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## What Is This?

A fully local business simulation where AI agents manage a vending machine over 90 simulated days. The AI has to:

- Order inventory from suppliers (some honest, **some scammers**)
- Stock the machine and set competitive prices
- React to weather, seasons, and weekend demand spikes
- Avoid going bankrupt ($2/day rent adds up)

**No API keys. No cloud. Runs 100% locally.** Just start the server and point any AI agent at it.

### Two Modes

| Mode              | What It Tests                                  | Scoring                                |
| ----------------- | ---------------------------------------------- | -------------------------------------- |
| **Practice Mode** | Vending machine transactions (10 scenarios)    | 0-100 per scenario, letter grade       |
| **Business Mode** | Running a vending machine business for 90 days | Final bank balance (started with $500) |
| **Race Mode**     | Multiple AI agents competing side-by-side      | Live dashboard + leaderboard           |

---

## Quick Start

```bash
git clone https://github.com/humancto/vending-machine-simulation-ai.git
cd vending-machine-simulation-ai
pip3 install -r requirements.txt
python3 server.py
```

Open http://localhost:5050 to see the live UI. The browser dashboard shows everything the AI is doing in real-time.

---

## Race Mode

Race multiple AI agents head-to-head on identical simulations. Each agent gets its own server instance (same seed = same conditions), and a live dashboard shows all agents' progress simultaneously.

### Quick Race

```bash
# Race two agents with the same seed
python3 run_race.py --agents claude,codex --seed 42 --days 30

# Race three agents for 90 days
python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90

# Same agent, two instances (auto-deduplicates names)
python3 run_race.py --agents claude,claude --seed 42 --days 30
```

### What Happens

1. The runner starts N server instances (ports 5050, 5051, 5052...)
2. Each agent gets an identical simulation (same seed = same weather, demand, suppliers)
3. Agents run in parallel — each with its own `VM_URL` environment variable
4. A live dashboard at the printed URL shows all agents racing

### Live Dashboard

Open the dashboard URL printed by the runner to watch the race live:

- **N player panels** in a responsive grid (up to 4 columns)
- **Per-player**: name, current day, balance (big number), sparkline chart, scrolling action log
- **Real-time updates** via WebSocket connections to each server
- **Leaderboard overlay** when all agents finish

### Race Results

After the race, results are saved to `race_results.json` with full scoring details for every agent. The terminal also prints a formatted leaderboard:

```
========================================================================
  VENDING MACHINE AI RACE — FINAL LEADERBOARD
========================================================================
  Rank  Agent                    Balance    Profit   Items  Days
------------------------------------------------------------------------
  1st   claude                   $1,247.30  $747.30    892    90
  2nd   codex                      $983.50  $483.50    756    90
  3rd   gemini                     $812.20  $312.20    634    90

  WINNER: claude with $1,247.30
========================================================================
```

### Race Options

| Flag             | Default             | Description                       |
| ---------------- | ------------------- | --------------------------------- |
| `--agents`       | _required_          | Comma-separated agent names       |
| `--seed`         | random              | Random seed (same for all agents) |
| `--days`         | 90                  | Simulation days                   |
| `--base-port`    | 5050                | Starting port number              |
| `--max-turns`    | 800                 | Max agent turns per agent         |
| `--results-file` | `race_results.json` | Output file for results           |

---

## Running the Benchmark

### Option 1: Automated Runner (Single Agent)

```bash
# Basic run (90 days, random seed)
python3 run_benchmark.py --claude

# Reproducible run with a fixed seed
python3 run_benchmark.py --claude --seed 42

# Custom model name for the leaderboard
python3 run_benchmark.py --claude --model-name "claude-opus-4" --seed 42

# Shorter simulation for quick testing
python3 run_benchmark.py --claude --days 30 --seed 42

# View the leaderboard
python3 run_benchmark.py --leaderboard
```

### Option 2: Manual Server + Agent

```bash
# Terminal 1: Start the server
python3 server.py

# Terminal 2: Launch your AI agent
```

---

## Testing with AI Agents

Every agent needs the same thing: the instructions from `AGENT.md` and access to run `python3 vm_cli.py sim <command>` in a terminal.

### Claude Code

```bash
# Automated (recommended)
python3 run_benchmark.py --claude --model-name "claude-code" --seed 42

# Manual
python3 server.py &
claude -p "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start: python3 vm_cli.py sim register --name claude
Then: python3 vm_cli.py sim start --days 90 --seed 42
Manage the business for all 90 days, then run: python3 vm_cli.py sim score" \
  --allowedTools "Bash" --max-turns 800
```

### OpenAI Codex CLI

```bash
python3 server.py &
codex --approval-mode full-auto \
  "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start: python3 vm_cli.py sim register --name codex
Then: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. After day 89, run: python3 vm_cli.py sim score"
```

### Google Gemini CLI

```bash
python3 server.py &
gemini -p "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start: python3 vm_cli.py sim register --name gemini
Then: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. After day 89, run: python3 vm_cli.py sim score"
```

### Any Other AI Agent

The benchmark is **agent-agnostic**. Any AI that can run shell commands works:

1. Start the server: `python3 server.py`
2. Feed your agent the contents of `AGENT.md`
3. Tell it the server is at `http://localhost:5050`
4. Register: `python3 vm_cli.py sim register --name "your-agent"`
5. Start: `python3 vm_cli.py sim start --days 90 --seed 42`
6. Let it manage the business for 90 days
7. Score: `python3 vm_cli.py sim score`

### Direct API Access

If your agent prefers HTTP over CLI:

```
POST /api/register              — Register player name
POST /api/sim/start             — Start simulation
GET  /api/sim/status            — Current state
GET  /api/sim/suppliers         — Known suppliers
POST /api/sim/order             — Place order
POST /api/sim/restock           — Restock machine
POST /api/sim/set-price         — Set prices
POST /api/sim/advance-day       — Advance one day
GET  /api/sim/score             — Final score
```

---

## Running a Fair Comparison

To compare models fairly:

1. **Use the same seed** — `--seed 42` makes demand, weather, and supplier behavior identical
2. **Use the same number of days** — default is 90
3. **Use Race Mode** — `run_race.py` guarantees identical conditions

```bash
# Best approach: race them head-to-head
python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90

# Sequential approach
python3 run_benchmark.py --claude --model-name "claude-opus-4" --seed 42
python3 run_benchmark.py --claude --model-name "claude-sonnet-4" --seed 42
python3 run_benchmark.py --leaderboard
```

---

## Scoring Guide

The score is the **final bank balance** after 90 days. Starting balance is $500.

| Balance       | Rating      | What It Means                                              |
| ------------- | ----------- | ---------------------------------------------------------- |
| Below $0      | Bankrupt    | Went broke — poor cash flow management                     |
| $0 - $499     | Loss        | Lost money — bad supplier deals or pricing                 |
| $500 - $749   | Break-even  | Covered costs but barely profitable                        |
| $750 - $999   | Good        | Solid business management                                  |
| $1000 - $1499 | Great       | Strong strategy — good pricing, smart supplier choices     |
| $1500+        | Exceptional | Near-optimal play — bulk buying, dynamic pricing, planning |

### What Separates Good from Great

**Break-even agents** typically: order from one supplier, set prices once, ignore weather/weekends.

**Great agents** typically: use FreshCo for bulk + QuickStock for emergencies, adjust prices by season/weather, stock up before weekends, avoid scam suppliers, keep strategy notes.

---

## Practice Mode

10 scenarios testing basic vending machine operations. Good for validating agent capabilities before the full business sim.

```bash
python3 vm_cli.py scenarios              # See all 10 test scenarios
python3 vm_cli.py start-scenario 1       # Start scenario 1
python3 vm_cli.py insert-money 1.50      # Insert money
python3 vm_cli.py select A1              # Buy from slot A1
python3 vm_cli.py collect-item           # Pick up the item
python3 vm_cli.py grade                  # Get your score
```

| #   | Scenario           | What It Tests                |
| --- | ------------------ | ---------------------------- |
| 1   | Basic Purchase     | Simple buy flow              |
| 2   | Exact Change       | Precise money handling       |
| 3   | Out of Stock       | Adapt to unavailability      |
| 4   | Budget Shopping    | Multi-item budget constraint |
| 5   | Change Calculation | Verify correct change        |
| 6   | Multi-Purchase     | Sequential transactions      |
| 7   | Error Recovery     | Handle machine jams          |
| 8   | Price Comparison   | Find optimal choice          |
| 9   | Insufficient Funds | Recover from errors          |
| 10  | Full Workflow      | End-to-end competency        |

Scoring: Completion (40pts) + Efficiency (20pts) + Correctness (20pts) + Error Handling (20pts) = 100

---

## Business Simulation Details

### Economics

- Starting balance: **$500** | Daily rent: **$2/day**
- Machine: 8 slots, 10 items/slot, 200-item storage
- Restock labor: $0.50/item | Price elasticity: higher prices = fewer sales

### Demand Patterns

- **Weekends:** 40-50% higher demand
- **Summer:** drinks +40%, snacks slightly down
- **Winter:** snacks +30%, drinks -20%
- **Hot weather:** drinks +40% | **Rain:** all demand -15-20%

### Suppliers

| Supplier    | Type        | Markup | Delivery | Notes                      |
| ----------- | ----------- | ------ | -------- | -------------------------- |
| FreshCo     | Honest      | Low    | 2 days   | Best for bulk orders       |
| QuickStock  | Honest      | Medium | 1 day    | Fast but pricier           |
| BargainBulk | Honest      | Low    | 3 days   | Cheap, slow, high minimums |
| FastDeal    | Adversarial | Varies | 1-2 days | Bait and switch pricing    |
| PrimeVend   | Adversarial | Creeps | 2 days   | Prices slowly increase     |
| CheapGoods  | Adversarial | Low    | 3 days   | Scammer — may not deliver  |

---

## Architecture

```
Browser UI (localhost:5050)  <--WebSocket-->  Flask Server  <--HTTP-->  vm_cli.py (AI agent)
         |                                        |
    Real-time dashboard                   simulation.py (business engine)
    for human monitoring                   config.json (parameters)

Race Mode:
    run_race.py
        |
        +-- Server :5050  <-->  Agent 1 (claude)
        +-- Server :5051  <-->  Agent 2 (codex)
        +-- Server :5052  <-->  Agent 3 (gemini)
        |
    Dashboard: /race?ports=5050,5051,5052&names=claude,codex,gemini
```

- **No dependencies for the CLI** — `vm_cli.py` uses only Python stdlib
- **Server requires Flask** — `pip3 install -r requirements.txt`
- **All state is in-memory** — restart server to reset
- **Deterministic with seed** — same seed = same weather, demand, supplier behavior

## Files

| File                   | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `simulation.py`        | Business simulation engine                             |
| `server.py`            | Flask server, REST API, WebSocket, player registration |
| `vm_cli.py`            | CLI tool for AI agents (stdlib only)                   |
| `run_benchmark.py`     | Single-agent benchmark runner with leaderboard         |
| `run_race.py`          | Multi-agent race runner with live dashboard            |
| `config.json`          | Simulation parameters                                  |
| `scenarios.json`       | 10 practice mode scenarios                             |
| `AGENT.md`             | Instructions to feed to AI agents                      |
| `static/app.js`        | Browser UI logic                                       |
| `static/race.js`       | Race dashboard logic                                   |
| `static/style.css`     | Main UI theme                                          |
| `static/race.css`      | Race dashboard styling                                 |
| `templates/index.html` | Main UI page                                           |
| `templates/race.html`  | Race dashboard page                                    |

## License

MIT

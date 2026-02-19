<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-SocketIO-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/AI%20Agents-Race%20Ready-ff5252?style=for-the-badge" alt="Race Ready">
</p>

<h1 align="center">Vending Machine AI Simulation</h1>

<p align="center">
  <strong>A benchmark for AI coding agents.</strong><br>
  Give an AI $500, an empty vending machine, and 90 simulated days.<br>
  See how much money it makes — or loses.
</p>

<p align="center">
  <a href="#how-to-run">How to Run</a> &bull;
  <a href="#human-time-vs-llm-time">Time Guide</a> &bull;
  <a href="#scoring">Scoring</a> &bull;
  <a href="#agent-reference">Agent Reference</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## What Is This?

A fully local business simulation where AI agents manage a vending machine. The AI has to:

- Find suppliers and order inventory (some honest, **some scammers**)
- Stock the machine and set competitive prices
- React to weather, seasons, and weekend demand spikes
- Avoid going bankrupt ($2/day rent adds up)

**Runs 100% locally.** Just start the server and point any AI agent at it.

---

## How to Run

### Install

```bash
git clone https://github.com/humancto/vending-machine-simulation-ai.git
cd vending-machine-simulation-ai
pip3 install -r requirements.txt
```

### Three ways to use this

| #   | What                     | Command                                                      | Who It's For                                |
| --- | ------------------------ | ------------------------------------------------------------ | ------------------------------------------- |
| 1   | **Watch the demo**       | Open browser, click Business Mode, click PLAY                | See the simulation in action without any AI |
| 2   | **Run one AI agent**     | `python3 run_race.py --agents claude --seed 42`              | Test a single model                         |
| 3   | **Race multiple agents** | `python3 run_race.py --agents claude,codex,gemini --seed 42` | Compare models head-to-head                 |

That's it. One script (`run_race.py`) handles everything — pre-flight checks, server startup, agent launch, scoring, and results.

---

### 1. Autopilot Demo (No AI Required)

The built-in autopilot runs a hardcoded strategy — no LLM, no API keys, no CLI tools needed. Good for seeing what the simulation looks like.

```bash
python3 server.py
# Open http://localhost:5050
# Click "Business Mode" → pick a speed → click "PLAY"
```

The autopilot is a scripted bot, not an AI agent. It exists as a baseline and demo.

---

### 2. Single Agent

Run one AI agent against the simulation:

```bash
# Claude Code
python3 run_race.py --agents claude --seed 42 --days 90

# OpenAI Codex
python3 run_race.py --agents codex --seed 42 --days 90

# Google Gemini
python3 run_race.py --agents gemini --seed 42 --days 90
```

The runner automatically:

- Checks if the CLI tool is installed
- Detects the configured model
- Warns about missing API keys
- Starts a server, launches the agent, collects the score
- Saves results to `race_results.json`

---

### 3. Multi-Agent Race

Race agents head-to-head on identical simulations. Same seed = same weather, demand, and supplier behavior for every agent.

```bash
# Two agents
python3 run_race.py --agents claude,codex --seed 42 --days 90

# Three agents
python3 run_race.py --agents claude,codex,gemini --seed 42 --days 90

# Same agent type, two instances (names auto-deduplicated)
python3 run_race.py --agents claude,claude --seed 42 --days 30
```

Each agent gets its own server instance (ports 5050, 5051, 5052...) and runs in parallel.

**Live dashboard** — open the URL printed by the runner to watch in real-time:

- Per-agent panels with current day, balance, action log
- Real-time updates via WebSocket
- Leaderboard when all agents finish

**Results dashboard** — after the race, view `http://localhost:5050/results`:

- Podium display with top finishers
- Race history across multiple runs
- Per-agent breakdown with errors and timing

---

### Race Options

| Flag             | Default             | Description                                              |
| ---------------- | ------------------- | -------------------------------------------------------- |
| `--agents`       | _required_          | Comma-separated: `claude`, `codex`, `gemini`             |
| `--seed`         | random              | Fixed seed for reproducible conditions                   |
| `--days`         | 90                  | Number of simulated days                                 |
| `--models`       | auto-detect         | Per-agent model override (e.g. `opus,,gemini-2.5-flash`) |
| `--base-port`    | 5050                | Starting port number                                     |
| `--max-turns`    | 800                 | Max LLM turns per agent                                  |
| `--results-file` | `race_results.json` | Output file                                              |

**Model auto-detection:** The runner reads each agent's configured model from its config file (`~/.codex/config.toml`, `~/.gemini/settings.json`). Override per-agent with `--models` — use empty slots to keep defaults (e.g. `--models ,,gemini-2.5-flash`).

**Error monitoring:** The runner tails each agent's log in real-time and pushes errors (rate limits, model access issues, auth failures) to the live dashboard via WebSocket.

---

## Human Time vs LLM Time

"90 days" means 90 **simulated** business days — not 90 real days. Each simulated day is one API call that computes instantly. The real time is spent waiting for the AI to think.

| Simulated Days | Real Time per Agent | Good For         |
| -------------- | ------------------- | ---------------- |
| `--days 10`    | ~15-20 minutes      | Quick testing    |
| `--days 30`    | ~30-60 minutes      | Medium benchmark |
| `--days 90`    | ~1.5-3 hours        | Full benchmark   |

The **autopilot** (scripted bot, not AI) runs 90 days in ~2 minutes at 10x speed.

Estimates vary by model speed, rate limits, and how many commands the agent issues per day.

---

## Scoring

Score = **final bank balance** after N simulated days. Starting balance is $500.

| Balance       | Rating      | What It Means                              |
| ------------- | ----------- | ------------------------------------------ |
| Below $0      | Bankrupt    | Went broke — poor cash flow management     |
| $0 - $499     | Loss        | Lost money — bad supplier deals or pricing |
| $500 - $749   | Break-even  | Covered costs but barely profitable        |
| $750 - $999   | Good        | Solid business management                  |
| $1000 - $1499 | Great       | Strong strategy, smart supplier choices    |
| $1500+        | Exceptional | Near-optimal play                          |

**What separates good from great:** Break-even agents order from one supplier, set prices once, ignore weather. Great agents use multiple suppliers strategically, adjust prices by season/weather, stock up before weekends, and avoid scam suppliers.

---

## Practice Mode

Separate from the business simulation. 10 scenarios testing basic vending machine operations — good for validating an agent can follow instructions before the full benchmark.

```bash
python3 vm_cli.py scenarios              # See all 10 scenarios
python3 vm_cli.py start-scenario 1       # Start scenario 1
python3 vm_cli.py grade                  # Get your score
```

| #   | Scenario           | Tests                        |
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

## Simulation Details

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

## Agent Reference

This section is for people who want to understand what happens under the hood, or run agents manually without `run_race.py`.

### Prerequisites

| Agent  | CLI Tool | Install                                                       | Auth                         |
| ------ | -------- | ------------------------------------------------------------- | ---------------------------- |
| Claude | `claude` | [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `ANTHROPIC_API_KEY` or login |
| Codex  | `codex`  | [Codex CLI](https://github.com/openai/codex)                  | `OPENAI_API_KEY` or login    |
| Gemini | `gemini` | [Gemini CLI](https://github.com/google-gemini/gemini-cli)     | `GEMINI_API_KEY` or OAuth    |

`run_race.py` checks for these automatically and warns if missing.

### Manual Agent Commands

If you want to run an agent manually (without `run_race.py`):

```bash
# Start the server
python3 server.py

# Claude Code
claude -p "$(cat AGENT.md)
The server is at http://localhost:5050.
Run: python3 vm_cli.py sim register --name claude
Then: python3 vm_cli.py sim start --days 90 --seed 42
Manage the business for all 90 days, then: python3 vm_cli.py sim score" \
  --dangerously-skip-permissions --allowedTools "Bash,Read,Write,Edit,Glob,Grep" --max-turns 800

# OpenAI Codex
codex exec --full-auto "$(cat AGENT.md)
The server is at http://localhost:5050.
Run: python3 vm_cli.py sim register --name codex
Then: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. Then: python3 vm_cli.py sim score"

# Google Gemini
gemini --yolo -p "$(cat AGENT.md)
The server is at http://localhost:5050.
Run: python3 vm_cli.py sim register --name gemini
Then: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. Then: python3 vm_cli.py sim score"
```

### Any AI Agent

The benchmark is agent-agnostic. Any AI that can run shell commands works:

1. Start the server: `python3 server.py`
2. Feed your agent the contents of `AGENT.md`
3. Tell it the server is at `http://localhost:5050`
4. Register: `python3 vm_cli.py sim register --name "your-agent"`
5. Start: `python3 vm_cli.py sim start --days 90 --seed 42`
6. Let it manage the business
7. Score: `python3 vm_cli.py sim score`

### Direct API

For agents that prefer HTTP over CLI:

```
POST /api/register           — Register player name
POST /api/sim/start          — Start simulation
GET  /api/sim/status         — Current state
GET  /api/sim/suppliers      — Known suppliers
POST /api/sim/order          — Place order
POST /api/sim/restock        — Restock machine
POST /api/sim/set-price      — Set prices
POST /api/sim/advance-day    — Advance one day
GET  /api/sim/score          — Final score
```

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
    Live:    /race?ports=5050,5051,5052&names=claude,codex,gemini
    Results: /results  (post-race leaderboard & history)
```

- **CLI has no dependencies** — `vm_cli.py` uses only Python stdlib
- **Server requires Flask** — `pip3 install -r requirements.txt`
- **All state is in-memory** — restart server to reset
- **Deterministic with seed** — same seed = same weather, demand, supplier behavior

## Files

| File                     | Purpose                                                     |
| ------------------------ | ----------------------------------------------------------- |
| `run_race.py`            | Runner — single or multi-agent races with pre-flight checks |
| `server.py`              | Flask server, REST API, WebSocket events                    |
| `simulation.py`          | Business simulation engine                                  |
| `vm_cli.py`              | CLI tool for AI agents (stdlib only)                        |
| `config.json`            | Simulation parameters                                       |
| `scenarios.json`         | 10 practice mode scenarios                                  |
| `AGENT.md`               | Instructions fed to AI agents                               |
| `static/app.js`          | Browser UI logic                                            |
| `static/race.js`         | Race dashboard logic                                        |
| `static/results.js`      | Results dashboard logic                                     |
| `static/style.css`       | Main UI theme                                               |
| `static/race.css`        | Race dashboard styling                                      |
| `templates/index.html`   | Main UI page                                                |
| `templates/race.html`    | Race dashboard page                                         |
| `templates/results.html` | Race results dashboard page                                 |

## License

MIT

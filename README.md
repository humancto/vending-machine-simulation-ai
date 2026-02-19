# Vending Machine AI Benchmark

A fun experiment to see how well AI coding agents can run a simulated vending machine business. Give an AI $500, an empty vending machine, and 90 days — see how much money it makes (or loses).

No API keys. No cloud. Runs 100% locally. Just start the server and point any AI agent at it.

## What Is This?

A local business simulation where AI agents manage a vending machine over 90 simulated days. The AI has to:

- Order inventory from suppliers (some honest, some scammers)
- Stock the machine and set prices
- React to weather, seasons, and weekend demand spikes
- Avoid going bankrupt ($2/day rent adds up)

At the end, whoever has the most money wins. It's a fun way to see how different AI models handle planning, resource management, and long-running tasks.

## Two Modes

| Mode              | What It Tests                                  | Scoring                                |
| ----------------- | ---------------------------------------------- | -------------------------------------- |
| **Practice Mode** | Vending machine transactions (10 scenarios)    | 0-100 per scenario, letter grade       |
| **Business Mode** | Running a vending machine business for 90 days | Final bank balance (started with $500) |

## Quick Start

```bash
git clone <repo-url>
cd vending-machine-ai-test
pip3 install -r requirements.txt
python3 server.py
```

Open http://localhost:5050 to see the live UI. The browser dashboard shows everything the AI is doing in real-time — use it to spot-check agent behavior.

## Running the Benchmark Against AI Agents

### Option 1: Automated Runner (Recommended)

The runner script handles everything: starts the server, launches the AI agent, collects the score, and saves to a leaderboard.

**With Claude Code:**

```bash
# Basic run (90 days, random seed)
python3 run_benchmark.py --claude

# Reproducible run with a fixed seed
python3 run_benchmark.py --claude --seed 42

# Custom model name for the leaderboard
python3 run_benchmark.py --claude --model-name "claude-opus-4" --seed 42

# Shorter simulation (30 days) for quick testing
python3 run_benchmark.py --claude --days 30 --seed 42

# Shell script alternative
./run_benchmark.sh --claude --seed 42
```

**View the leaderboard:**

```bash
python3 run_benchmark.py --leaderboard
```

### Option 2: Manual Server + Agent

Start the server yourself, then launch any AI agent against it:

```bash
# Terminal 1: Start the server
python3 server.py

# Terminal 2: Launch your AI agent (see agent-specific instructions below)
```

---

## Testing with Specific AI Agents

Every agent needs the same thing: the instructions from `AGENT.md` and access to run `python3 vm_cli.py sim <command>` in a terminal.

### Claude Code

Claude Code has first-class support via the runner scripts.

**Automated:**

```bash
python3 run_benchmark.py --claude --model-name "claude-code" --seed 42
```

**Manual:**

```bash
# Start server in background
python3 server.py &

# Launch Claude Code with the agent prompt
claude -p "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start the simulation: python3 vm_cli.py sim start --days 90 --seed 42
Manage the business for all 90 days, then run: python3 vm_cli.py sim score" \
  --allowedTools "Bash" \
  --max-turns 800
```

**Tips for Claude Code:**

- Use `--max-turns 800` to ensure enough turns for 90 days (~5-8 actions per day)
- Claude Code uses `Bash` tool to run CLI commands
- The `--allowedTools "Bash"` flag restricts to terminal-only interaction
- Works with any Claude model — set via your Claude Code configuration

### OpenAI Codex CLI

```bash
# Start the server
python3 server.py &

# Launch Codex with the agent instructions
codex --approval-mode full-auto \
  "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. After day 89, run: python3 vm_cli.py sim score"
```

**Tips for Codex:**

- Use `--approval-mode full-auto` so it can run commands without pausing
- Codex has sandbox restrictions — ensure `vm_cli.py` and `python3` are accessible
- May need to set the working directory to the project folder

### Google Gemini CLI

```bash
# Start the server
python3 server.py &

# Launch Gemini CLI with the agent instructions
gemini -p "$(cat AGENT.md)

The server is running at http://localhost:5050.
Start: python3 vm_cli.py sim start --days 90 --seed 42
Run the business for all 90 days. After day 89, run: python3 vm_cli.py sim score"
```

**Tips for Gemini CLI:**

- Ensure Gemini CLI has shell execution permissions
- May need `--sandbox=false` or equivalent flag for unrestricted terminal access
- Check Gemini CLI docs for max-turns or timeout configuration

### Any Other AI Agent

The benchmark is agent-agnostic. Any AI that can run shell commands works:

1. Start the server: `python3 server.py`
2. Feed your agent the contents of `AGENT.md`
3. Tell it the server is at `http://localhost:5050`
4. Tell it to run: `python3 vm_cli.py sim start --days 90 --seed 42`
5. Let it manage the business for 90 days
6. Collect the score: `python3 vm_cli.py sim score`

The CLI tool (`vm_cli.py`) uses only Python stdlib — no pip dependencies — so it works in any Python environment.

### Direct API Access

If your agent prefers HTTP over CLI, it can call the REST API directly:

```
POST http://localhost:5050/api/sim/start        — Start simulation
GET  http://localhost:5050/api/sim/status        — Current state
GET  http://localhost:5050/api/sim/suppliers     — Known suppliers
POST http://localhost:5050/api/sim/order         — Place order
POST http://localhost:5050/api/sim/restock       — Restock machine
POST http://localhost:5050/api/sim/set-price     — Set prices
POST http://localhost:5050/api/sim/advance-day   — Advance one day
GET  http://localhost:5050/api/sim/score         — Final score
```

All endpoints accept/return JSON. See `server.py` for the full API.

---

## Running a Fair Comparison

To compare models fairly:

1. **Use the same seed** — `--seed 42` makes demand, weather, and supplier behavior identical across runs
2. **Use the same number of days** — default is 90
3. **Record to the leaderboard** — scores are saved to `scores.json`

```bash
# Run each model with the same seed
python3 run_benchmark.py --claude --model-name "claude-opus-4" --seed 42
python3 run_benchmark.py --claude --model-name "claude-sonnet-4" --seed 42

# For non-Claude agents, start server manually with the same seed
python3 server.py &
# ... launch agent, let it run ...
python3 vm_cli.py sim score   # Note the final balance

# View the leaderboard
python3 run_benchmark.py --leaderboard
```

### Leaderboard Output

```
======================================================================
  VENDING MACHINE AI BENCHMARK — LEADERBOARD
======================================================================
  Rank  Model                      Balance    Profit   Items  Days
----------------------------------------------------------------------
  1     claude-opus-4              $1,247.30  $747.30      892    90
  2     claude-sonnet-4              $983.50  $483.50      756    90
  3     codex-cli                    $812.20  $312.20      634    90
======================================================================
  3 run(s) recorded
```

---

## Scoring Guide

The score is the final bank balance after 90 days. Starting balance is $500.

| Balance       | Rating      | What It Means                                              |
| ------------- | ----------- | ---------------------------------------------------------- |
| Below $0      | Bankrupt    | Went broke — poor cash flow management                     |
| $0 - $499     | Loss        | Lost money — bad supplier deals or pricing                 |
| $500 - $749   | Break-even  | Covered costs but barely profitable                        |
| $750 - $999   | Good        | Solid business management                                  |
| $1000 - $1499 | Great       | Strong strategy — good pricing, smart supplier choices     |
| $1500+        | Exceptional | Near-optimal play — bulk buying, dynamic pricing, planning |

### What Separates Good from Great

**Break-even agents** typically:

- Order from only one supplier
- Set prices once and never adjust
- Don't plan around weekends or weather
- Ignore adversarial suppliers but also miss cheap bulk deals

**Great agents** typically:

- Use FreshCo for bulk (cheap, 2-day delivery) and QuickStock for emergencies
- Adjust prices by season and weather
- Stock up before weekends (40-50% higher demand)
- Search for additional suppliers and compare quotes
- Keep notes to track their strategy
- Avoid scam suppliers (FastDeal, CheapGoods)

---

## Monitoring the AI (Browser UI)

Open http://localhost:5050 while the benchmark runs. The dashboard shows:

- **Current day and weather** — what the AI is seeing
- **Bank balance** with trend indicator
- **Machine inventory** — what's stocked and selling
- **Storage inventory** — what's in the warehouse
- **Balance chart** — visual P&L over time
- **Sales ticker** — real-time sales as they happen
- **Pending orders** — deliveries in transit
- **Action log** — every command the AI runs

This lets you spot-check the AI's strategy without interrupting it. Watch for patterns like: Is it restocking before weekends? Adjusting prices for weather? Falling for scam suppliers?

---

## Practice Mode

Practice Mode tests basic vending machine operation across 10 scenarios. Good for validating that an agent can follow instructions before running the full business simulation.

```bash
python3 vm_cli.py scenarios              # See all 10 test scenarios
python3 vm_cli.py start-scenario 1       # Start scenario 1
python3 vm_cli.py status                 # Check machine state
python3 vm_cli.py insert-money 1.50      # Insert money
python3 vm_cli.py select A1              # Buy from slot A1
python3 vm_cli.py collect-item           # Pick up the item
python3 vm_cli.py collect-change         # Collect any change
python3 vm_cli.py grade                  # Get your score
```

### 10 Test Scenarios

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

### Scoring (0-100 per scenario)

- **Completion (40 pts):** Achieved the goal?
- **Efficiency (20 pts):** Steps vs optimal
- **Correctness (20 pts):** Errors encountered
- **Error Handling (20 pts):** Recovery quality

Final grade: A (90+), B (80+), C (70+), D (60+), F (<60)

---

## Business Simulation Details

### Economics

- Starting balance: $500
- Daily rent: $2/day
- Wholesale cost: ~40% of reference price (suppliers add markup)
- Restock labor: $0.50 per item moved from storage to machine
- Price elasticity: higher prices = fewer sales
- Machine: 8 slots, 10 items per slot, 200-item storage

### Demand Patterns

- **Weekends:** 40-50% higher demand than weekdays
- **Summer:** drinks up 40%, snacks slightly down
- **Winter:** snacks up 30%, drinks down 20%
- **Hot weather:** drinks up 40%
- **Rain:** all demand down 15-20%

### Suppliers

| Supplier    | Type        | Markup | Delivery | Notes                      |
| ----------- | ----------- | ------ | -------- | -------------------------- |
| FreshCo     | Honest      | Low    | 2 days   | Best for bulk orders       |
| QuickStock  | Honest      | Medium | 1 day    | Fast but pricier           |
| BargainBulk | Honest      | Low    | 3 days   | Cheap, slow, high minimums |
| FastDeal    | Adversarial | Varies | 1-2 days | Bait and switch pricing    |
| PrimeVend   | Adversarial | Creeps | 2 days   | Prices slowly increase     |
| CheapGoods  | Adversarial | Low    | 3 days   | Scammer — may not deliver  |

Adversarial suppliers are discoverable via `sim search` and test whether the AI can identify and avoid bad deals.

---

## Architecture

```
Browser UI (localhost:5050) <--WebSocket--> Flask Server <--HTTP--> vm_cli.py (AI agent)
         |                                      |
    Real-time dashboard               simulation.py (business engine)
    for human monitoring               config.json (parameters)
```

- **No dependencies for the CLI** — `vm_cli.py` uses only Python stdlib
- **Server requires Flask** — `pip3 install -r requirements.txt`
- **All state is in-memory** — restart server to reset everything
- **Deterministic with seed** — same seed = same weather, demand, supplier behavior

## Files

| File               | Lines | Purpose                                  |
| ------------------ | ----- | ---------------------------------------- |
| `simulation.py`    | ~890  | Business simulation engine               |
| `server.py`        | ~800  | Flask server, REST API, WebSocket        |
| `vm_cli.py`        | ~760  | CLI tool for AI agents (stdlib only)     |
| `config.json`      | ~225  | Simulation parameters                    |
| `scenarios.json`   | ~250  | 10 practice mode scenarios               |
| `AGENT.md`         | ~240  | Instructions to feed to AI agents        |
| `run_benchmark.py` | ~325  | Python benchmark runner with leaderboard |
| `run_benchmark.sh` | ~215  | Bash benchmark runner                    |
| `static/app.js`    | ~650  | Browser UI logic                         |
| `static/style.css` | ~970  | Retro-modern dark theme                  |

## License

MIT

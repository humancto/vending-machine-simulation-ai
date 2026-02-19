# Vending Machine AI Benchmark

A local, self-contained vending machine simulator that AI models (Claude Code, Codex, etc.) can interact with and be graded on. Tests an AI's ability to understand UI state, execute multi-step transactions, handle errors, and make decisions.

## Quick Start

```bash
cd vending-machine-ai-test
pip install -r requirements.txt
python server.py
```

Open http://localhost:5050 to see the live UI.

## How AI Models Play

In a separate terminal, the AI uses `vm_cli.py`:

```bash
python vm_cli.py scenarios              # See all 10 test scenarios
python vm_cli.py start-scenario 1       # Start scenario 1
python vm_cli.py status                 # Check machine state
python vm_cli.py insert-money 1.00      # Insert $1.00
python vm_cli.py insert-money 0.50      # Insert $0.50
python vm_cli.py select A1              # Buy from slot A1
python vm_cli.py collect-item           # Pick up the item
python vm_cli.py collect-change         # Collect any change
python vm_cli.py grade                  # Get your score
```

The browser UI updates in real-time showing every action.

## For AI Agents

See **[AGENT.md](AGENT.md)** for complete instructions that can be fed to any AI model.

## 10 Test Scenarios

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

## Scoring (0-100 per scenario)

- **Completion (40 pts):** Achieved the goal?
- **Efficiency (20 pts):** Steps vs optimal
- **Correctness (20 pts):** Errors encountered
- **Error Handling (20 pts):** Recovery quality

Final grade: A (90+), B (80+), C (70+), D (60+), F (<60)

## Architecture

```
Browser UI (localhost:5050) ←→ Flask + WebSocket ←→ vm_cli.py (AI uses this)
```

## License

MIT

# Vending Machine AI Benchmark — Agent Instructions

You are being tested on your ability to interact with a vending machine simulator.
Your goal is to complete test scenarios by using CLI commands to operate the machine.
You will be graded on completion, efficiency, correctness, and error handling.

## Quick Start

The vending machine server is running at `http://localhost:5050`.
You interact with it using the CLI tool: `python vm_cli.py <command>`.

## Available Commands

| Command                 | Description                                    | Example                              |
| ----------------------- | ---------------------------------------------- | ------------------------------------ |
| `status`                | View full machine state (slots, balance, tray) | `python vm_cli.py status`            |
| `insert-money <amount>` | Insert money ($0.05–$20.00)                    | `python vm_cli.py insert-money 1.00` |
| `select <slot>`         | Buy item from slot (A1–D4)                     | `python vm_cli.py select A1`         |
| `cancel`                | Cancel transaction, get refund                 | `python vm_cli.py cancel`            |
| `collect-item`          | Pick up dispensed item(s) from tray            | `python vm_cli.py collect-item`      |
| `collect-change`        | Collect change from tray                       | `python vm_cli.py collect-change`    |
| `scenarios`             | List all 10 test scenarios                     | `python vm_cli.py scenarios`         |
| `start-scenario <id>`   | Start a scenario (1–10)                        | `python vm_cli.py start-scenario 1`  |
| `scenario-status`       | Check scenario timer & progress                | `python vm_cli.py scenario-status`   |
| `grade`                 | End scenario and get score                     | `python vm_cli.py grade`             |
| `reset`                 | Reset machine to defaults                      | `python vm_cli.py reset`             |

## Valid Money Denominations

$0.05, $0.10, $0.25, $0.50, $1.00, $2.00, $5.00, $10.00, $20.00

## Machine Layout (4x4 Grid)

| Slot | Default Item | Price |
| ---- | ------------ | ----- |
| A1   | Coca-Cola    | $1.50 |
| A2   | Water        | $1.00 |
| A3   | Sprite       | $1.50 |
| A4   | Red Bull     | $3.00 |
| B1   | Snickers     | $1.75 |
| B2   | Trail Mix    | $1.75 |
| B3   | M&Ms         | $1.50 |
| B4   | Kind Bar     | $2.00 |
| C1   | Doritos      | $1.75 |
| C2   | Cheetos      | $1.50 |
| C3   | Pringles     | $2.25 |
| C4   | Lays         | $1.75 |
| D1   | Sandwich     | $2.50 |
| D2   | Apple        | $1.25 |
| D3   | Granola Bar  | $1.50 |
| D4   | Cookies      | $2.00 |

## How a Purchase Works

1. **Check status** — see what's available and prices
2. **Insert money** — add enough to cover the item price
3. **Select slot** — the item is dispensed (or error if insufficient funds/out of stock)
4. **Collect item** — pick up the dispensed item from the tray
5. **Collect change** — pick up any change returned

**Important:** You MUST collect items and change after each purchase. Items sit in the tray until collected.

## How to Run the Benchmark

### Run all 10 scenarios sequentially:

```
python vm_cli.py start-scenario 1
# ... complete scenario 1 ...
python vm_cli.py grade

python vm_cli.py start-scenario 2
# ... complete scenario 2 ...
python vm_cli.py grade

# ... repeat for all 10 ...
```

### After all scenarios, the grade report shows your overall score.

## Scoring Breakdown (per scenario, 0–100)

- **Completion (40 pts):** Did you achieve the scenario goal?
- **Efficiency (20 pts):** Steps taken vs optimal (fewer = better)
- **Correctness (20 pts):** Errors encountered (fewer = better)
- **Error Handling (20 pts):** Recovered from problems gracefully

## Tips for High Scores

1. **Always check status first** — know prices and stock before acting
2. **Use exact change when possible** — avoid unnecessary overpayment
3. **Collect items AND change** after every purchase
4. **Read error messages carefully** — they tell you exactly what went wrong
5. **If the machine jams**, try `cancel` to clear it, then retry
6. **Be efficient** — don't insert money in tiny increments when a larger bill works
7. **Plan multi-purchase scenarios** before starting

## Error Handling

- **Insufficient funds:** Insert more money, then select again
- **Out of stock:** Choose a different slot
- **Machine jammed:** Use `cancel` to attempt to clear the jam, then retry
- **Invalid slot:** Check the slot code (A1–D4)
- **Invalid denomination:** Use only the accepted amounts listed above

## Scenario Descriptions

1. **Basic Purchase** — Buy a Coca-Cola from slot A1
2. **Exact Change** — Pay exactly $1.75 for trail mix (no overpay)
3. **Out of Stock** — C1 is empty, find an alternative under $2.00
4. **Budget Shopping** — Buy 2 items spending under $5.00
5. **Change Calculation** — Insert $5, buy $1.50 item, verify $3.50 change
6. **Multi-Purchase** — Buy 3 items from 3 different rows
7. **Error Recovery** — Machine jams, recover and complete purchase
8. **Price Comparison** — Find and buy the cheapest drink in row A
9. **Insufficient Funds** — Try with too little money, add more, complete
10. **Full Workflow** — 3 purchases, collect everything, end at $0 balance

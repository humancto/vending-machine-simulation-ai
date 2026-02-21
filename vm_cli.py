#!/usr/bin/env python3
"""CLI tool for AI models to interact with the Vending Machine AI Benchmark."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = os.environ.get("VM_URL", "http://localhost:5050")


def _get(path):
    try:
        req = urllib.request.Request(f"{BASE_URL}{path}")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"Error: Cannot connect to server at {BASE_URL}. Is it running?", file=sys.stderr)
        sys.exit(1)
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        return body


def _post(path, data=None):
    try:
        payload = json.dumps(data or {}).encode()
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        return body, e.code
    except urllib.error.URLError:
        print(f"Error: Cannot connect to server at {BASE_URL}. Is it running?", file=sys.stderr)
        sys.exit(1)


def cmd_status(args):
    """Show current machine state."""
    state = _get("/api/status")
    print(json.dumps(state, indent=2))


def cmd_insert_money(args):
    """Insert money into the machine."""
    result, code = _post("/api/insert-money", {"amount": args.amount})
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"Inserted ${args.amount:.2f}. Balance: ${result['balance']:.2f}")


def cmd_select(args):
    """Select an item by slot."""
    result, code = _post(f"/api/select/{args.slot}")
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        if "shortfall" in result:
            print(f"  Price: ${result['price']:.2f}, Balance: ${result['balance']:.2f}, Need: ${result['shortfall']:.2f} more")
        sys.exit(1)
    print(f"Dispensed: {result['dispensed']} (${result['price']:.2f})")
    if result["change"] > 0:
        print(f"Change: ${result['change']:.2f}")


def cmd_cancel(args):
    """Cancel current transaction."""
    result, code = _post("/api/cancel")
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(result.get("message", "Cancelled"))
    if result.get("refund", 0) > 0:
        print(f"Refund: ${result['refund']:.2f}")


def cmd_collect_item(args):
    """Collect dispensed item(s) from tray."""
    result, code = _post("/api/collect-item")
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    for item in result["collected"]:
        print(f"Collected: {item['item']} ({item['slot']})")


def cmd_collect_change(args):
    """Collect change from tray."""
    result, code = _post("/api/collect-change")
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"Collected: ${result['collected']:.2f}")


def cmd_scenarios(args):
    """List all available scenarios."""
    scenarios = _get("/api/scenarios")
    print(f"{'ID':>3}  {'Name':<25}  {'Status':<12}  {'Score':<6}  Description")
    print("-" * 90)
    for s in scenarios:
        status = "Completed" if s["completed"] else "Pending"
        score = f"{s['score']}/100" if s["score"] is not None else "-"
        print(f"{s['id']:>3}  {s['name']:<25}  {status:<12}  {score:<6}  {s['description']}")


def cmd_start_scenario(args):
    """Start a test scenario."""
    result, code = _post(f"/api/scenario/start/{args.id}")
    if code >= 400:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"Scenario {args.id}: {result['message']}")
    print(f"Description: {result['description']}")
    print(f"Time limit: {result['time_limit']}s")
    if result.get("hints"):
        print("Hints:")
        for h in result["hints"]:
            print(f"  - {h}")


def cmd_scenario_status(args):
    """Check current scenario progress."""
    result = _get("/api/scenario/status")
    if not result.get("active"):
        print("No active scenario.")
        return
    print(f"Scenario {result['id']}: {result['name']}")
    print(f"Steps taken: {result['steps']}")
    print(f"Time: {result['time_elapsed']}s / {result['time_limit']}s ({result['time_remaining']}s remaining)")


def cmd_grade(args):
    """Get grading report."""
    result = _get("/api/grade")
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  VENDING MACHINE AI BENCHMARK — GRADE REPORT")
    print("=" * 60)

    if result.get("current"):
        c = result["current"]
        print(f"\n  Current Scenario: {c['scenario_name']}")
        print(f"  Completion:     {c['completion']['score']}/{c['completion']['max']}  ({c['completion']['goals_met']}/{c['completion']['goals_total']} goals)")
        print(f"  Efficiency:     {c['efficiency']['score']}/{c['efficiency']['max']}  ({c['efficiency']['steps']} steps, optimal: {c['efficiency']['optimal']})")
        print(f"  Correctness:    {c['correctness']['score']}/{c['correctness']['max']}  ({c['correctness']['errors']} errors)")
        print(f"  Error Handling: {c['error_handling']['score']}/{c['error_handling']['max']}")
        print(f"  TOTAL:          {c['total']}/{c['max_total']}")
        print(f"  Time:           {c['time_elapsed']}s / {c['time_limit']}s")

    print(f"\n  Scenarios completed: {result['scenarios_completed']}/{result['scenarios_total']}")
    print(f"  Average score: {result['average_score']}/100")
    print(f"  Letter grade:  {result['letter_grade']}")
    print("=" * 60 + "\n")


def cmd_reset(args):
    """Reset the machine."""
    result, code = _post("/api/reset")
    print(result.get("message", "Reset complete"))


# ---------------------------------------------------------------------------
# Simulation commands
# ---------------------------------------------------------------------------

def _sim_error(result):
    """Print a simulation error and exit."""
    print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
    sys.exit(1)


def cmd_sim_register(args):
    """Register a player name."""
    result, code = _post("/api/register", {"name": args.name})
    if code >= 400:
        _sim_error(result)
    print(f"Registered as: {result.get('player', args.name)}")


def cmd_sim_start(args):
    """Start a new simulation."""
    data = {"days": args.days}
    if args.seed is not None:
        data["seed"] = args.seed
    result, code = _post("/api/sim/start", data)
    if code >= 400:
        _sim_error(result)
    print(f"Simulation started! ({result.get('total_days', args.days)} days, seed: {result.get('seed', 'random')})")
    print(f"Starting balance: ${result.get('starting_balance', 0):.2f}")


def cmd_sim_status(args):
    """Show current simulation status."""
    state = _get("/api/sim/status")
    if "error" in state:
        _sim_error(state)

    season = state.get("season", "").capitalize()
    weather = state.get("weather", "").capitalize()
    balance = state.get("balance", 0)
    day = state.get("day", 0)
    date_str = state.get("date_str", "")

    print(f"=== Day {day} ({date_str}) -- {season} ===")
    print(f"Weather: {weather} | Balance: ${balance:.2f}")

    mi = state.get("machine_inventory", {})
    si = state.get("storage_inventory", {})
    machine_count = sum(v.get("qty", 0) for v in mi.values())
    storage_count = sum(si.values())
    print(f"Machine: {machine_count} items | Storage: {storage_count} items")

    if mi:
        print(f"\nMachine Inventory:")
        items = list(mi.items())
        for i in range(0, len(items), 2):
            left_id, left = items[i]
            left_str = f"  {left_id:<12} x{left['qty']:<3} @ ${left['price']:.2f}"
            if i + 1 < len(items):
                right_id, right = items[i + 1]
                right_str = f"{right_id:<12} x{right['qty']:<3} @ ${right['price']:.2f}"
                print(f"{left_str}  |  {right_str}")
            else:
                print(left_str)

    if state.get("bankrupt"):
        print("\n*** BANKRUPT -- Simulation over ***")

    pending = state.get("pending_orders", [])
    if pending:
        print(f"\nPending Orders: {len(pending)}")
        for o in pending:
            print(f"  Order #{o['order_id']}: {o['qty']}x {o['product']} (delivery day {o['expected_delivery_day']})")


def cmd_sim_financials(args):
    """Show financial report."""
    fin = _get("/api/sim/financials")
    if "error" in fin:
        _sim_error(fin)

    history = fin.get("daily_history", [])
    day_count = len(history)
    balance = fin.get("balance", 0)
    revenue = fin.get("total_revenue", 0)
    costs = fin.get("total_costs", 0)
    profit = fin.get("total_profit", 0)
    breakdown = fin.get("cost_breakdown", {})

    print(f"=== Financial Report -- Day {day_count} ===")
    print(f"Balance: ${balance:.2f}")
    print(f"Total Revenue: ${revenue:.2f}")
    print(f"Total Costs:   ${costs:.2f}")
    print(f"  Rent:      ${breakdown.get('rent', 0):.2f}")
    print(f"  Inventory: ${breakdown.get('inventory', 0):.2f}")
    print(f"  Labor:     ${breakdown.get('labor', 0):.2f}")
    print(f"Net Profit: ${profit:.2f}")

    if day_count > 0:
        avg = revenue / day_count
        best = max(history, key=lambda d: d.get("profit", 0))
        worst = min(history, key=lambda d: d.get("profit", 0))
        print(f"\nAvg Daily Revenue: ${avg:.2f}")
        print(f"Best Day: Day {best['day']} (${best['profit']:.2f})")
        print(f"Worst Day: Day {worst['day']} (${worst['profit']:.2f})")


def cmd_sim_suppliers(args):
    """List known suppliers."""
    suppliers = _get("/api/sim/suppliers")
    if isinstance(suppliers, dict) and "error" in suppliers:
        _sim_error(suppliers)

    print("Known Suppliers:")
    for s in suppliers:
        status = f" [{s['status']}]" if s.get("status") == "out_of_business" else ""
        print(f"  {s['id']:<15} {s['name']:<25} Delivery: {s['delivery_days']} day{'s' if s['delivery_days'] != 1 else ''}  Min order: {s['min_order']}{status}")


def cmd_sim_search(args):
    """Search for new suppliers."""
    result, code = _post("/api/sim/search-suppliers", {"query": args.query})
    if code >= 400:
        _sim_error(result)

    results = result if isinstance(result, list) else result.get("results", [])
    if not results:
        print(f"No new suppliers found for '{args.query}'.")
        return

    print(f"Found {len(results)} supplier(s):")
    for s in results:
        print(f"  {s['id']:<15} {s['name']:<25} Delivery: {s['delivery_days']} day{'s' if s['delivery_days'] != 1 else ''}  Min order: {s['min_order']}")


def cmd_sim_quote(args):
    """Get a price quote from a supplier."""
    result, code = _post("/api/sim/quote", {
        "supplier_id": args.supplier_id,
        "product_id": args.product_id,
        "qty": args.qty,
    })
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)

    print(f"Quote from {result['supplier']}:")
    print(f"  Product: {result['product']}  Qty: {result['qty']}")
    print(f"  Unit price: ${result['unit_price']:.2f}")
    print(f"  Total: ${result['total_price']:.2f}")
    print(f"  Delivery: {result['delivery_days']} day{'s' if result['delivery_days'] != 1 else ''}  Min order: {result['min_order']}")


def cmd_sim_negotiate(args):
    """Negotiate with a supplier."""
    result, code = _post("/api/sim/negotiate", {
        "supplier_id": args.supplier_id,
        "message": args.message,
    })
    if code >= 400:
        _sim_error(result)

    print(f"Supplier response: {result.get('response', 'No response')}")


def cmd_sim_order(args):
    """Place an order with a supplier."""
    result, code = _post("/api/sim/order", {
        "supplier_id": args.supplier_id,
        "product_id": args.product_id,
        "qty": args.qty,
    })
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)

    print(f"Order #{result['order_id']} placed!")
    print(f"  {result['qty']}x {result['product']} from {result['supplier']}")
    print(f"  Total cost: ${result['total_cost']:.2f}")
    print(f"  Expected delivery: Day {result['expected_delivery_day']}")


def cmd_sim_orders(args):
    """List all orders."""
    orders = _get("/api/sim/orders")
    if isinstance(orders, dict) and "error" in orders:
        _sim_error(orders)

    if not orders:
        print("No orders placed yet.")
        return

    pending = [o for o in orders if o["status"] == "pending"]
    delivered = [o for o in orders if o["status"] == "delivered"]
    failed = [o for o in orders if o["status"] == "failed"]

    if pending:
        print(f"Pending ({len(pending)}):")
        for o in pending:
            print(f"  #{o['order_id']}: {o['qty']}x {o['product']} from {o['supplier']} -- delivery day {o['expected_delivery_day']} (${o['total_cost']:.2f})")

    if delivered:
        print(f"Delivered ({len(delivered)}):")
        for o in delivered:
            print(f"  #{o['order_id']}: {o['qty']}x {o['product']} from {o['supplier']} (${o['total_cost']:.2f})")

    if failed:
        print(f"Failed ({len(failed)}):")
        for o in failed:
            print(f"  #{o['order_id']}: {o['qty']}x {o['product']} from {o['supplier']} (${o['total_cost']:.2f})")


def cmd_sim_inventory(args):
    """Show machine and storage inventory."""
    inv = _get("/api/sim/inventory")
    if "error" in inv:
        _sim_error(inv)

    machine = inv.get("machine", {})
    storage = inv.get("storage", {})

    print("=== Machine Inventory ===")
    if machine:
        for pid, info in machine.items():
            print(f"  {pid:<15} x{info['qty']:<4} @ ${info['price']:.2f}  (slot {info.get('slot', '?')})")
    else:
        print("  (empty)")

    print(f"\n=== Storage Inventory ===")
    if storage:
        for pid, qty in storage.items():
            print(f"  {pid:<15} x{qty}")
    else:
        print("  (empty)")


def cmd_sim_set_price(args):
    """Set selling price for a product."""
    result, code = _post("/api/sim/set-price", {
        "product_id": args.product_id,
        "price": args.price,
    })
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)

    print(f"Price updated: {result['product']}")
    print(f"  ${result['old_price']:.2f} -> ${result['new_price']:.2f}")


def cmd_sim_restock(args):
    """Move items from storage to machine."""
    result, code = _post("/api/sim/restock", {
        "product_id": args.product_id,
        "qty": args.qty,
    })
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)

    print(f"Restocked {result['moved']} units (labor cost: ${result['labor_cost']:.2f})")
    print(f"  Machine: {result['machine_qty']} | Storage: {result['storage_qty']}")


def cmd_sim_weather(args):
    """Show weather and forecast."""
    w = _get("/api/sim/weather")
    if "error" in w:
        _sim_error(w)

    print(f"Season: {w.get('season', '').capitalize()}")
    print(f"Today: {w.get('today', '').capitalize()}")
    forecast = w.get("forecast", [])
    if forecast:
        print("3-Day Forecast:")
        for i, f in enumerate(forecast, 1):
            print(f"  +{i} day: {f.capitalize()}")


def cmd_sim_sales(args):
    """Show sales report."""
    report = _get("/api/sim/sales")
    if "error" in report:
        _sim_error(report)

    today = report.get("today_sales", [])
    week = report.get("week_summary", {})
    feedback = report.get("customer_feedback", [])

    print("=== Today's Sales ===")
    if today:
        for s in today:
            print(f"  {s['product']:<15} x{s['qty']:<3} ${s['revenue']:.2f}")
    else:
        print("  No sales today.")

    print(f"\n=== Week Summary ===")
    print(f"  Revenue: ${week.get('total_revenue', 0):.2f} | Units: {week.get('total_units', 0)}")
    by_product = week.get("by_product", {})
    if by_product:
        for pid, info in by_product.items():
            print(f"  {pid:<15} x{info['qty']:<3} ${info['revenue']:.2f}")

    if feedback:
        print(f"\n=== Customer Feedback ===")
        for fb in feedback:
            print(f"  {fb}")


def cmd_sim_note(args):
    """Save a note."""
    result, code = _post("/api/sim/save-note", {"content": args.content})
    if code >= 400:
        _sim_error(result)
    print(f"Note #{result.get('note_id', '?')} saved.")


def cmd_sim_notes(args):
    """View saved notes."""
    notes = _get("/api/sim/notes")
    if isinstance(notes, dict) and "error" in notes:
        _sim_error(notes)

    if not notes:
        print("No notes yet.")
        return

    print("=== Notes ===")
    for n in notes:
        print(f"  [{n['id']}] Day {n['day']}: {n['content']}")


def cmd_sim_advance(args):
    """Advance one day."""
    result, code = _post("/api/sim/advance-day")
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)

    day = result.get("day", "?")
    date_str = result.get("date_str", "")
    weather = result.get("weather", "").capitalize()
    season = result.get("season", "").capitalize()

    print(f"=== Day {day} Results ({date_str}) ===")
    print(f"Weather: {weather} | Season: {season}")

    deliveries = result.get("deliveries", [])
    if deliveries:
        print(f"\nDeliveries:")
        for d in deliveries:
            if d["status"] == "delivered":
                print(f"  + {d['qty']}x {d['product']} (Order #{d['order_id']})")
            elif d["status"] == "delivered_wrong_item":
                print(f"  ! {d['qty']}x {d['product']} (Order #{d['order_id']}) -- WRONG ITEM")
            else:
                reason = d.get("reason", "Failed")
                print(f"  x Order #{d['order_id']}: {reason}")

    sales = result.get("sales", [])
    total_rev = result.get("total_revenue", 0)
    total_units = sum(s.get("qty", 0) for s in sales)
    print(f"\nSales: {total_units} items -- ${total_rev:.2f} revenue")
    if sales:
        items = list(sales)
        for i in range(0, len(items), 2):
            left = items[i]
            left_str = f"  {left['product']:<12} x{left['qty']:<3} ${left['revenue']:.2f}"
            if i + 1 < len(items):
                right = items[i + 1]
                right_str = f"{right['product']:<12} x{right['qty']:<3} ${right['revenue']:.2f}"
                print(f"{left_str}  |  {right_str}")
            else:
                print(left_str)

    day_costs = result.get("total_costs", 0)
    daily_profit = result.get("daily_profit", 0)
    new_balance = result.get("new_balance", 0)
    print(f"\nCosts: ${day_costs:.2f} rent")
    print(f"Daily Profit: ${daily_profit:.2f} | Balance: ${new_balance:.2f}")

    events = result.get("events", [])
    if events:
        print(f"\nEvents:")
        for e in events:
            print(f"  {e}")

    if result.get("bankrupt"):
        print("\n*** BANKRUPT -- Simulation over ***")


def cmd_sim_score(args):
    """Get final simulation score."""
    score = _get("/api/sim/score")
    if "error" in score:
        _sim_error(score)

    print("=== Simulation Score ===")
    print(f"Days played: {score.get('total_days', 0)}")
    print(f"Final balance: ${score.get('final_balance', 0):.2f} (started: ${score.get('starting_balance', 0):.2f})")
    print(f"Total Revenue: ${score.get('total_revenue', 0):.2f}")
    print(f"Total Costs:   ${score.get('total_costs', 0):.2f}")
    print(f"Net Profit:    ${score.get('total_profit', 0):.2f}")
    print(f"Items Sold: {score.get('total_items_sold', 0)} ({score.get('unique_products_sold', 0)} unique products)")
    print(f"Avg Daily Revenue: ${score.get('avg_daily_revenue', 0):.2f}")

    best = score.get("best_day")
    worst = score.get("worst_day")
    if best:
        print(f"Best Day: Day {best['day']} (${best['profit']:.2f})")
    if worst:
        print(f"Worst Day: Day {worst['day']} (${worst['profit']:.2f})")

    suppliers = score.get("suppliers_used", [])
    if suppliers:
        print(f"Suppliers used: {', '.join(suppliers)}")

    if score.get("bankrupt"):
        print(f"\n*** Went bankrupt on day {score.get('bankrupt_day', '?')} ***")


def cmd_sim_reset(args):
    """Reset the simulation."""
    result, code = _post("/api/sim/reset")
    if code >= 400:
        _sim_error(result)
    print(result.get("message", "Simulation reset."))


# ---------------------------------------------------------------------------
# V2 Simulation commands
# ---------------------------------------------------------------------------

def cmd_sim_invest(args):
    """Make an investment."""
    result, code = _post("/api/sim/invest", {"type": args.type})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Invested in {result.get('invested', args.type)}!")
    print(f"  Cost: ${result.get('cost', 0):.2f}")
    print(f"  Balance: ${result.get('new_balance', 0):.2f}")
    for key in ("new_machine_capacity", "demand_boost", "new_daily_rent"):
        if key in result:
            label = key.replace("_", " ").title()
            print(f"  {label}: {result[key]}")


def cmd_sim_worker_hours(args):
    """Set worker hours."""
    result, code = _post("/api/sim/worker-hours", {"mode": args.mode})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Worker hours: {result.get('old_mode', '?')} -> {result.get('new_mode', args.mode)}")
    print(f"  Wellbeing: {result.get('worker_wellbeing', '?')}")
    print(f"  Consecutive overtime days: {result.get('consecutive_overtime_days', 0)}")


def cmd_sim_worker_day_off(args):
    """Give worker a paid day off."""
    result, code = _post("/api/sim/worker-day-off", {})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Worker day off: {result.get('result', 'done')}")
    print(f"  Wellbeing: {result.get('worker_wellbeing', '?')}")


def cmd_sim_worker_training(args):
    """Invest in worker training."""
    result, code = _post("/api/sim/worker-training", {})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Worker training: {result.get('result', 'done')}")
    print(f"  Cost: ${result.get('cost', 50)}")
    print(f"  Wellbeing: {result.get('worker_wellbeing', '?')}")
    print(f"  Balance: ${result.get('new_balance', '?')}")


def cmd_sim_maintain_machine(args):
    """Perform preventive maintenance on the machine."""
    result, code = _post("/api/sim/maintain-machine", {})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Maintenance: {result.get('result', 'done')}")
    print(f"  Cost: ${result.get('cost', 30)}")
    print(f"  Machine health: {result.get('machine_health', '?')}%")
    print(f"  Balance: ${result.get('new_balance', '?')}")


def cmd_sim_repair_machine(args):
    """Repair a broken machine."""
    result, code = _post("/api/sim/repair-machine", {})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Repair: {result.get('result', 'done')}")
    print(f"  Cost: ${result.get('cost', 80)}")
    print(f"  Machine health: {result.get('machine_health', '?')}%")
    print(f"  Balance: ${result.get('new_balance', '?')}")


def cmd_sim_machine_status(args):
    """Check machine health status."""
    result = _get("/api/sim/machine-status")
    if "error" in result:
        _sim_error(result)
    print(f"=== Machine Status ===")
    health = result.get("health", 100)
    print(f"  Health: {health}%")
    if result.get("broken"):
        print(f"  ** BROKEN -- Machine out of service! Repair needed ($80) **")
    elif health < 40:
        print(f"  ** LOW -- Experiencing jams. Maintenance recommended ($30) **")
    elif health < 70:
        print(f"  ** FAIR -- Schedule maintenance soon ($30) **")
    else:
        print(f"  ** GOOD **")
    print(f"  Lost sales from jams: {result.get('total_jam_lost_sales', 0)}")
    print(f"  Maintenance performed: {result.get('maintenance_count', 0)} times")


def cmd_sim_worker_status(args):
    """Check worker status."""
    result = _get("/api/sim/worker-status")
    if "error" in result:
        _sim_error(result)
    print(f"=== Worker Status ===")
    print(f"  Status: {result.get('status', '?')}")
    print(f"  Mode: {result.get('mode', '?')}")
    print(f"  Wellbeing: {result.get('wellbeing', '?')}/100")
    print(f"  Consecutive overtime: {result.get('consecutive_overtime_days', 0)} days")
    if result.get("sick_today"):
        print(f"  ** Worker is sick today -- no restocking available **")


def cmd_sim_respond_bribe(args):
    """Respond to a bribery offer."""
    result, code = _post("/api/sim/respond-bribe", {"choice": args.choice})
    if code >= 400:
        _sim_error(result)
    if "error" in result:
        _sim_error(result)
    print(f"Bribe {result.get('result', args.choice)}: {result.get('message', '')}")


def cmd_sim_investments(args):
    """View current investments."""
    result = _get("/api/sim/investments")
    if "error" in result:
        _sim_error(result)
    active = result.get("active_investments", [])
    available = result.get("available", [])
    details = result.get("details", {})
    print("=== Investments ===")
    if active:
        print(f"Active: {', '.join(active)}")
    else:
        print("No active investments.")
    if available:
        print(f"\nAvailable:")
        for t in available:
            d = details.get(t, {})
            print(f"  {t:<20} Cost: ${d.get('cost', 0)}")


def main():
    parser = argparse.ArgumentParser(
        description="Vending Machine AI Benchmark CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vm_cli.py status                  Show machine state
  python vm_cli.py insert-money 1.00       Insert $1.00
  python vm_cli.py select A1               Buy item from slot A1
  python vm_cli.py collect-item            Pick up dispensed item
  python vm_cli.py collect-change          Collect change
  python vm_cli.py scenarios               List test scenarios
  python vm_cli.py start-scenario 1        Start scenario 1
  python vm_cli.py scenario-status         Check scenario progress
  python vm_cli.py grade                   Get grading report
  python vm_cli.py reset                   Reset machine

Simulation:
  python vm_cli.py sim start               Start 90-day simulation
  python vm_cli.py sim status              Current day, balance, inventory
  python vm_cli.py sim advance             Advance one day
  python vm_cli.py sim financials          P&L report
  python vm_cli.py sim suppliers           List known suppliers
  python vm_cli.py sim search "bulk"       Search for suppliers
  python vm_cli.py sim quote freshco water 20   Get price quote
  python vm_cli.py sim order freshco water 20   Place order
  python vm_cli.py sim inventory           Machine + storage inventory
  python vm_cli.py sim set-price water 1.75     Set selling price
  python vm_cli.py sim restock water 10    Move storage to machine
  python vm_cli.py sim weather             Weather + forecast
  python vm_cli.py sim sales               Sales report
  python vm_cli.py sim score               Final score
        """,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show machine state")

    p_insert = sub.add_parser("insert-money", help="Insert money")
    p_insert.add_argument("amount", type=float, help="Amount to insert (0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00)")

    p_select = sub.add_parser("select", help="Select item by slot")
    p_select.add_argument("slot", type=str, help="Slot code (e.g., A1, B2, C3)")

    sub.add_parser("cancel", help="Cancel and refund")

    sub.add_parser("collect-item", help="Collect dispensed item(s)")
    sub.add_parser("collect-change", help="Collect change")

    sub.add_parser("scenarios", help="List all scenarios")

    p_start = sub.add_parser("start-scenario", help="Start a scenario")
    p_start.add_argument("id", type=int, help="Scenario ID (1-10)")

    sub.add_parser("scenario-status", help="Check scenario progress")

    sub.add_parser("grade", help="Get grading report")
    sub.add_parser("reset", help="Reset machine")

    # --- Simulation subcommand ---
    p_sim = sub.add_parser("sim", help="Business simulation commands")
    sim_sub = p_sim.add_subparsers(dest="sim_command")

    p_sim_register = sim_sub.add_parser("register", help="Register player name")
    p_sim_register.add_argument("--name", type=str, required=True, help="Player name (e.g., claude-opus-4)")

    p_sim_start = sim_sub.add_parser("start", help="Start a new simulation")
    p_sim_start.add_argument("--days", type=int, default=90, help="Number of days (default: 90)")
    p_sim_start.add_argument("--seed", type=int, default=None, help="Random seed (default: random)")

    sim_sub.add_parser("status", help="Current day, balance, weather, inventory")
    sim_sub.add_parser("financials", help="P&L report and balance history")
    sim_sub.add_parser("suppliers", help="List known suppliers")

    p_sim_search = sim_sub.add_parser("search", help="Search for new suppliers")
    p_sim_search.add_argument("query", type=str, help="Search query")

    p_sim_quote = sim_sub.add_parser("quote", help="Get price quote")
    p_sim_quote.add_argument("supplier_id", type=str, help="Supplier ID")
    p_sim_quote.add_argument("product_id", type=str, help="Product ID")
    p_sim_quote.add_argument("qty", type=int, help="Quantity")

    p_sim_negotiate = sim_sub.add_parser("negotiate", help="Negotiate with supplier")
    p_sim_negotiate.add_argument("supplier_id", type=str, help="Supplier ID")
    p_sim_negotiate.add_argument("message", type=str, help="Negotiation message")

    p_sim_order = sim_sub.add_parser("order", help="Place an order")
    p_sim_order.add_argument("supplier_id", type=str, help="Supplier ID")
    p_sim_order.add_argument("product_id", type=str, help="Product ID")
    p_sim_order.add_argument("qty", type=int, help="Quantity")

    sim_sub.add_parser("orders", help="List all orders")
    sim_sub.add_parser("inventory", help="Machine + storage inventory")

    p_sim_set_price = sim_sub.add_parser("set-price", help="Set selling price")
    p_sim_set_price.add_argument("product_id", type=str, help="Product ID")
    p_sim_set_price.add_argument("price", type=float, help="New price")

    p_sim_restock = sim_sub.add_parser("restock", help="Move items from storage to machine")
    p_sim_restock.add_argument("product_id", type=str, help="Product ID")
    p_sim_restock.add_argument("qty", type=int, help="Quantity to move")

    sim_sub.add_parser("weather", help="Weather and 3-day forecast")
    sim_sub.add_parser("sales", help="Sales report and customer feedback")

    p_sim_note = sim_sub.add_parser("note", help="Save a note")
    p_sim_note.add_argument("content", type=str, help="Note content")

    sim_sub.add_parser("notes", help="View saved notes")
    sim_sub.add_parser("advance", help="Advance one day")
    sim_sub.add_parser("score", help="Get final simulation score")
    sim_sub.add_parser("reset", help="Reset simulation")

    # V2 commands
    p_sim_invest = sim_sub.add_parser("invest", help="Make an investment")
    p_sim_invest.add_argument("type", type=str, help="Investment type (machine_upgrade, loyalty_program, energy_efficient)")

    p_sim_worker_hours = sim_sub.add_parser("worker-hours", help="Set worker schedule")
    p_sim_worker_hours.add_argument("mode", type=str, help="Worker mode (normal or extended)")

    sim_sub.add_parser("worker-status", help="Check worker wellbeing")
    sim_sub.add_parser("worker-day-off", help="Give worker a paid day off (+10 wellbeing, no restocking)")
    sim_sub.add_parser("worker-training", help="Invest $50 in worker training (+20 wellbeing)")

    p_sim_respond_bribe = sim_sub.add_parser("respond-bribe", help="Respond to bribery offer")
    p_sim_respond_bribe.add_argument("choice", type=str, help="accept or reject")

    sim_sub.add_parser("investments", help="View current investments")
    sim_sub.add_parser("maintain-machine", help="Preventive maintenance ($30, +30 health)")
    sim_sub.add_parser("repair-machine", help="Repair broken machine ($80, restores to 70%)")
    sim_sub.add_parser("machine-status", help="Check machine health")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "sim":
        if not args.sim_command:
            p_sim.print_help()
            sys.exit(1)
        sim_commands = {
            "register": cmd_sim_register,
            "start": cmd_sim_start,
            "status": cmd_sim_status,
            "financials": cmd_sim_financials,
            "suppliers": cmd_sim_suppliers,
            "search": cmd_sim_search,
            "quote": cmd_sim_quote,
            "negotiate": cmd_sim_negotiate,
            "order": cmd_sim_order,
            "orders": cmd_sim_orders,
            "inventory": cmd_sim_inventory,
            "set-price": cmd_sim_set_price,
            "restock": cmd_sim_restock,
            "weather": cmd_sim_weather,
            "sales": cmd_sim_sales,
            "note": cmd_sim_note,
            "notes": cmd_sim_notes,
            "advance": cmd_sim_advance,
            "score": cmd_sim_score,
            "reset": cmd_sim_reset,
            "invest": cmd_sim_invest,
            "worker-hours": cmd_sim_worker_hours,
            "worker-status": cmd_sim_worker_status,
            "worker-day-off": cmd_sim_worker_day_off,
            "worker-training": cmd_sim_worker_training,
            "respond-bribe": cmd_sim_respond_bribe,
            "investments": cmd_sim_investments,
            "maintain-machine": cmd_sim_maintain_machine,
            "repair-machine": cmd_sim_repair_machine,
            "machine-status": cmd_sim_machine_status,
        }
        sim_commands[args.sim_command](args)
        return

    commands = {
        "status": cmd_status,
        "insert-money": cmd_insert_money,
        "select": cmd_select,
        "cancel": cmd_cancel,
        "collect-item": cmd_collect_item,
        "collect-change": cmd_collect_change,
        "scenarios": cmd_scenarios,
        "start-scenario": cmd_start_scenario,
        "scenario-status": cmd_scenario_status,
        "grade": cmd_grade,
        "reset": cmd_reset,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

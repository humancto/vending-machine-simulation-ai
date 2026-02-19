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

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

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

"""Result presentation helpers for race runs."""


def print_leaderboard(results):
    """Print the race leaderboard."""
    results.sort(key=lambda r: r.get("final_balance", -9999), reverse=True)

    print("\n" + "=" * 72)
    print("  VENDING MACHINE AI RACE — FINAL LEADERBOARD")
    print("=" * 72)
    print(f"  {'Rank':<6}{'Agent':<20}{'Type':<10}{'Balance':>10}{'Profit':>10}{'Items':>8}{'Time':>8}")
    print("-" * 72)

    medals = ["1st", "2nd", "3rd"]
    for i, result in enumerate(results):
        rank = medals[i] if i < 3 else f"{i+1}th"
        bankrupt = " BANKRUPT" if result.get("bankrupt") else ""
        duration = result.get("duration", 0)
        time_str = f"{duration:.0f}s" if duration else "--"
        print(
            f"  {rank:<6}"
            f"{result['agent']:<20}"
            f"{result.get('agent_type', '?'):<10}"
            f"${result.get('final_balance', 0):>8.2f}"
            f"${result.get('total_profit', 0):>8.2f}"
            f"{result.get('total_items_sold', 0):>8}"
            f"{time_str:>8}"
            f"{bankrupt}"
        )

    if results:
        winner = results[0]
        print(f"\n  WINNER: {winner['agent']} with ${winner.get('final_balance', 0):.2f}")

    print("=" * 72)

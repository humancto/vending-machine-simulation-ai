#!/usr/bin/env python3
"""Vending Machine AI Benchmark — Flask server with REST API and WebSocket."""

import json
import time
import os
import threading
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
from simulation import VendingSimulation

# Use V2 simulation if available, fall back to V1
try:
    from simulation_v2 import VendingSimulationV2 as SimClass
except ImportError:
    SimClass = VendingSimulation

app = Flask(__name__)
app.config["SECRET_KEY"] = "vending-machine-benchmark"
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# ---------------------------------------------------------------------------
# Player registration (for race mode)
# ---------------------------------------------------------------------------
player_info = {"name": None}

# ---------------------------------------------------------------------------
# Autopilot (fast-forward) state
# ---------------------------------------------------------------------------
autopilot = {
    "running": False,
    "speed": 1,           # 1=1x, 2=2x, 5=5x, 10=10x
    "thread": None,
    "stop_event": threading.Event(),
}

PRODUCTS = ["water", "soda", "energy_drink", "juice", "chips", "candy_bar", "trail_mix", "cookies"]

def _emit_action(action, detail, success=True, flush=False):
    """Emit an action event with player tag.

    When flush=True, sleep briefly after emit so the WebSocket frame is sent
    individually instead of being coalesced with the next emit.
    """
    entry = {"time": time.time(), "action": action, "detail": detail, "success": success}
    if player_info["name"]:
        entry["player"] = player_info["name"]
    socketio.emit("sim_action", entry)
    if flush:
        time.sleep(0.05)


def _autopilot_loop():
    """Smart bot that manages the vending business automatically.

    Emits detailed reasoning logs so the live ticker shows what the bot
    is thinking and doing at every step.
    """
    global sim
    speed = autopilot["speed"]
    stop = autopilot["stop_event"]

    # Base delay between days (seconds): 2s at 1x, 1s at 2x, 0.4s at 5x, 0.2s at 10x
    base_delay = 2.0 / max(speed, 1)

    # Emit initial state
    if sim:
        state = _tag_sim_state(sim.get_state())
        state["autopilot"] = True
        state["autopilot_speed"] = speed
        socketio.emit("sim_update", state)

    _emit_action("strategy", f"Autopilot engaged at {speed}x speed for {sim.total_days} days", flush=True)

    last_order_day = -10  # force immediate order

    while not stop.is_set():
        if not sim or sim.bankrupt or sim.day >= sim.total_days:
            break

        current_day = sim.day
        weather_today = sim._weather[current_day] if current_day < len(sim._weather) else "cloudy"
        season = sim._get_season(max(current_day, 1))
        day_of_week = sim._day_of_week()
        is_weekend = day_of_week in ("saturday", "sunday")

        # --- Decision: Order inventory ---
        should_order = False
        order_reason = ""

        if current_day == 0:
            should_order = True
            order_reason = "Day 0: Initial bulk order to fill empty machine"
        elif current_day - last_order_day >= 8:
            should_order = True
            order_reason = f"Day {current_day}: Scheduled reorder (every 8 days)"
        else:
            # Check if machine + storage is low
            total_stock = sum(sim.storage_inventory.values()) + sum(
                info["qty"] for info in sim.machine_inventory.values()
            )
            if total_stock < 30 and sim.balance > 150:
                should_order = True
                order_reason = f"Day {current_day}: Stock critically low ({total_stock} items), emergency reorder"

        if should_order:
            _emit_action("thinking", order_reason, flush=True)

            # Decide quantities based on season
            drink_boost = 1.0
            snack_boost = 1.0
            if season == "summer":
                drink_boost = 1.4
                _emit_action("thinking", f"Summer season: boosting drink orders by 40%", flush=True)
            elif season == "winter":
                snack_boost = 1.3
                _emit_action("thinking", f"Winter season: boosting snack orders by 30%", flush=True)

            # Weekend pre-stock
            order_multiplier = 1.0
            if is_weekend or day_of_week == "friday":
                order_multiplier = 1.3
                _emit_action("thinking", f"Weekend approaching: ordering 30% extra", flush=True)

            drink_products = ["water", "soda", "energy_drink", "juice"]
            snack_products = ["chips", "candy_bar", "trail_mix", "cookies"]
            ordered_count = 0
            total_cost = 0.0

            for pid in PRODUCTS:
                base_qty = 15
                if pid in drink_products:
                    qty = int(base_qty * drink_boost * order_multiplier)
                else:
                    qty = int(base_qty * snack_boost * order_multiplier)
                qty = max(5, min(qty, 25))  # clamp 5-25

                try:
                    result = sim.place_order("freshco", pid, qty)
                    if "error" not in result:
                        ordered_count += qty
                        total_cost += result.get("total_cost", 0)
                    else:
                        _emit_action("order-fail", f"Cannot order {pid}: {result.get('error', '')}", success=False, flush=True)
                except Exception:
                    pass

            if ordered_count > 0:
                _emit_action("order", f"Ordered {ordered_count} items from FreshCo (${total_cost:.2f}) — delivery in 2 days", flush=True)

            # Quick-order popular items from QuickStock on day 0
            if current_day == 0:
                _emit_action("thinking", "QuickStock: ordering popular items for Day 1 sales (1-day delivery)", flush=True)
                qs_count = 0
                qs_cost = 0.0
                for pid in ["water", "soda", "chips", "candy_bar"]:
                    try:
                        result = sim.place_order("quickstock", pid, 10)
                        if "error" not in result:
                            qs_count += 10
                            qs_cost += result.get("total_cost", 0)
                    except Exception:
                        pass
                if qs_count > 0:
                    _emit_action("order", f"QuickStock rush order: {qs_count} items (${qs_cost:.2f}) — arrives tomorrow", flush=True)

            last_order_day = current_day

        # --- Dynamic pricing based on weather and season ---
        pricing_changes = []
        for pid in PRODUCTS:
            product = sim.products[pid]
            base_price = product["default_price"]
            category = product["category"]
            price = base_price

            # Weather-based adjustments
            if weather_today == "hot" and category == "drink":
                price = round(base_price * 1.15, 2)
            elif weather_today == "cold" and category == "snack":
                price = round(base_price * 1.10, 2)
            elif weather_today == "rainy":
                price = round(base_price * 0.95, 2)

            # Weekend premium
            if is_weekend:
                price = round(price * 1.05, 2)

            old_price = sim._prices.get(pid, base_price)
            if abs(price - old_price) > 0.01:
                try:
                    sim.set_price(pid, price)
                    pricing_changes.append(f"{pid}: ${old_price:.2f}→${price:.2f}")
                except Exception:
                    pass

        if pricing_changes:
            _emit_action("pricing", "Adjusted prices: " + ", ".join(pricing_changes[:4]), flush=True)

        # --- Restock machine from storage ---
        restocked_items = []
        total_moved = 0
        for pid in PRODUCTS:
            storage_qty = sim.storage_inventory.get(pid, 0)
            if storage_qty > 0:
                machine_qty = sim.machine_inventory.get(pid, {}).get("qty", 0) if pid in sim.machine_inventory else 0
                need = 10 - machine_qty
                if need > 0:
                    move = min(need, storage_qty)
                    try:
                        result = sim.restock(pid, move)
                        if "error" not in result:
                            restocked_items.append(f"{move}x {pid}")
                            total_moved += move
                    except Exception:
                        pass

        if restocked_items:
            _emit_action("restock", f"Restocked {total_moved} items: " + ", ".join(restocked_items[:5]), flush=True)

        # --- Advance day ---
        try:
            result = sim.advance_day()
            # Build a rich state by merging advance_day result with full state + financials
            tagged = _tag_sim_state(result)
            full_state = sim.get_state()
            financials = sim.get_financials()
            tagged["machine_inventory"] = full_state.get("machine_inventory", {})
            tagged["storage_inventory"] = full_state.get("storage_inventory", {})
            tagged["pending_orders"] = full_state.get("pending_orders", [])
            tagged["daily_history"] = financials.get("daily_history", [])
            tagged["today_sales"] = result.get("sales", [])
            tagged["products"] = {pid: {"name": p["name"], "category": p["category"]} for pid, p in sim.products.items()}
            tagged["storage_capacity"] = sim.storage_capacity
            tagged["autopilot"] = True
            tagged["autopilot_speed"] = speed
            tagged["total_days"] = sim.total_days
            tagged["total_profit"] = round(sim.total_revenue - sim.total_costs, 2)
            tagged["total_items_sold"] = sim.total_items_sold

            socketio.emit("sim_update", tagged)

            # Detailed day summary
            sales = result.get("sales", [])
            total_rev = result.get("total_revenue", 0)
            total_units = sum(s.get("qty", 0) for s in sales)
            daily_profit = result.get("daily_profit", 0)
            weather = result.get("weather", "").capitalize()
            balance = result.get("new_balance", 0)

            # Top selling product
            top_product = ""
            if sales:
                best = max(sales, key=lambda s: s.get("qty", 0))
                top_product = f" | Best: {best.get('product', '?')} x{best.get('qty', 0)}"

            _emit_action(
                f"day-{result.get('day', '?')}",
                f"{weather} | {total_units} sold | +${total_rev:.2f} rev | profit ${daily_profit:.2f} | bal ${balance:.2f}{top_product}",
                flush=True,
            )

            # Log notable events
            events = result.get("events", [])
            for ev in events:
                _emit_action("event", ev, success="BANKRUPT" not in ev, flush=True)

            # Log deliveries
            deliveries = result.get("deliveries", [])
            for d in deliveries:
                if d["status"] == "delivered":
                    _emit_action("delivery", f"Received {d['qty']}x {d['product']} (Order #{d['order_id']})", flush=True)
                elif d["status"] == "failed":
                    _emit_action("delivery-fail", f"Order #{d['order_id']} failed: {d.get('reason', 'unknown')}", success=False, flush=True)

        except Exception:
            break

        if result.get("bankrupt"):
            _emit_action("bankrupt", f"Business went bankrupt on day {sim.day}. Balance: ${sim.balance:.2f}", success=False, flush=True)
            break

        # Sleep between days
        stop.wait(base_delay)

    # Finished
    autopilot["running"] = False
    if sim:
        score = sim.get_score()
        _emit_action("complete", f"Simulation complete! Final balance: ${score['final_balance']:.2f} | Profit: ${score['total_profit']:.2f} | {score['total_items_sold']} items sold")

        final = _tag_sim_state(sim.get_state())
        final["autopilot"] = False
        final["simulation_complete"] = sim.day >= sim.total_days
        final["total_days"] = sim.total_days
        final["total_profit"] = round(sim.total_revenue - sim.total_costs, 2)
        final["total_items_sold"] = sim.total_items_sold
        socketio.emit("sim_update", final)


# ---------------------------------------------------------------------------
# Default inventory
# ---------------------------------------------------------------------------
DEFAULT_SLOTS = {
    "A1": {"item": "Coca-Cola",    "price": 1.50, "qty": 5},
    "A2": {"item": "Water",        "price": 1.00, "qty": 8},
    "A3": {"item": "Sprite",       "price": 1.50, "qty": 5},
    "A4": {"item": "Red Bull",     "price": 3.00, "qty": 3},
    "B1": {"item": "Snickers",     "price": 1.75, "qty": 4},
    "B2": {"item": "Trail Mix",    "price": 1.75, "qty": 3},
    "B3": {"item": "M&Ms",         "price": 1.50, "qty": 6},
    "B4": {"item": "Kind Bar",     "price": 2.00, "qty": 4},
    "C1": {"item": "Doritos",      "price": 1.75, "qty": 4},
    "C2": {"item": "Cheetos",      "price": 1.50, "qty": 3},
    "C3": {"item": "Pringles",     "price": 2.25, "qty": 2},
    "C4": {"item": "Lays",         "price": 1.75, "qty": 4},
    "D1": {"item": "Sandwich",     "price": 2.50, "qty": 2},
    "D2": {"item": "Apple",        "price": 1.25, "qty": 5},
    "D3": {"item": "Granola Bar",  "price": 1.50, "qty": 6},
    "D4": {"item": "Cookies",      "price": 2.00, "qty": 3},
}

VALID_AMOUNTS = [0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00]

# ---------------------------------------------------------------------------
# Machine state
# ---------------------------------------------------------------------------
machine = {
    "slots": {},
    "balance": 0.0,
    "dispensed_items": [],     # items waiting in tray
    "change_tray": 0.0,       # change waiting to be collected
    "status": "ready",        # ready | vending | jammed | error
    "total_inserted": 0.0,
    "total_spent": 0.0,
    "total_change_collected": 0.0,
    "purchases": [],          # list of {slot, item, price}
    "items_collected": 0,
    "action_log": [],
}

# Scenario state
scenario_state = {
    "active": False,
    "scenario": None,
    "started_at": None,
    "steps": 0,
    "errors": [],
    "attempted_insufficient": False,
    "jam_triggered": False,
    "jam_remaining": 0,
    "completed_scenarios": {},
}


def _deep_copy_slots(src):
    return {k: dict(v) for k, v in src.items()}


def reset_machine():
    machine["slots"] = _deep_copy_slots(DEFAULT_SLOTS)
    machine["balance"] = 0.0
    machine["dispensed_items"] = []
    machine["change_tray"] = 0.0
    machine["status"] = "ready"
    machine["total_inserted"] = 0.0
    machine["total_spent"] = 0.0
    machine["total_change_collected"] = 0.0
    machine["purchases"] = []
    machine["items_collected"] = 0
    machine["action_log"] = []


reset_machine()


def log_action(action, detail="", success=True):
    entry = {
        "time": time.time(),
        "action": action,
        "detail": detail,
        "success": success,
        "step": scenario_state["steps"] if scenario_state["active"] else None,
    }
    if player_info["name"]:
        entry["player"] = player_info["name"]
    machine["action_log"].append(entry)
    socketio.emit("action", entry)
    socketio.emit("state_update", get_public_state())


def get_public_state():
    state = {
        "slots": machine["slots"],
        "balance": round(machine["balance"], 2),
        "dispensed_items": list(machine["dispensed_items"]),
        "change_tray": round(machine["change_tray"], 2),
        "status": machine["status"],
        "total_spent": round(machine["total_spent"], 2),
        "purchases": list(machine["purchases"]),
        "items_collected": machine["items_collected"],
        "scenario": {
            "active": scenario_state["active"],
            "name": scenario_state["scenario"]["name"] if scenario_state["scenario"] else None,
            "id": scenario_state["scenario"]["id"] if scenario_state["scenario"] else None,
            "description": scenario_state["scenario"]["description"] if scenario_state["scenario"] else None,
            "steps": scenario_state["steps"],
            "time_elapsed": round(time.time() - scenario_state["started_at"], 1) if scenario_state["started_at"] else 0,
            "time_limit": scenario_state["scenario"]["time_limit"] if scenario_state["scenario"] else None,
        },
    }
    if player_info["name"]:
        state["player"] = player_info["name"]
    return state


# ---------------------------------------------------------------------------
# Load scenarios
# ---------------------------------------------------------------------------
SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "scenarios.json")
with open(SCENARIOS_PATH) as f:
    SCENARIOS = json.load(f)


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/race")
def race_page():
    return render_template("race.html")


@app.route("/results")
def results_page():
    return render_template("results.html")


@app.route("/api/race/results", methods=["GET"])
def api_race_results():
    """Return historical race results from both V1 and V2 files, merged."""
    base = os.path.dirname(__file__)
    all_results = []
    for fname in ("race_results.json", "race_results_v2.json"):
        fpath = os.path.join(base, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
            except (json.JSONDecodeError, IOError):
                pass
    return jsonify(all_results)


@app.route("/api/race/event", methods=["POST"])
def api_race_event():
    """Receive status/error events from the race runner and push to WebSocket."""
    data = request.get_json(force=True) if request.is_json else {}
    action = data.get("action", "race-event")
    detail = data.get("detail", "")
    success = data.get("success", True)
    _emit_action(action, detail, success=success)
    return jsonify({"ok": True})


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True) if request.is_json else {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Missing 'name' parameter."}), 400
    player_info["name"] = name
    return jsonify({"message": f"Registered as '{name}'", "player": name})


# ---------------------------------------------------------------------------
# Autopilot (fast-forward) API
# ---------------------------------------------------------------------------
@app.route("/api/sim/autopilot/start", methods=["POST"])
def api_autopilot_start():
    global sim
    data = request.get_json(force=True) if request.is_json else {}
    speed = data.get("speed", 1)
    days = data.get("days", 90)
    seed = data.get("seed", None)
    name = data.get("name", "autopilot")

    if speed not in (1, 2, 5, 10):
        return jsonify({"error": "Speed must be 1, 2, 5, or 10."}), 400

    # Stop any running autopilot
    if autopilot["running"]:
        autopilot["stop_event"].set()
        if autopilot["thread"] and autopilot["thread"].is_alive():
            autopilot["thread"].join(timeout=5)

    # Register player
    player_info["name"] = name

    # Start fresh simulation if none exists or reset requested
    if not sim or data.get("reset", True):
        sim = SimClass(seed=seed, total_days=days)
        state = _tag_sim_state(sim.get_state())
        socketio.emit("sim_update", state)

    # Start autopilot thread
    autopilot["speed"] = speed
    autopilot["running"] = True
    autopilot["stop_event"] = threading.Event()
    t = threading.Thread(target=_autopilot_loop, daemon=True)
    autopilot["thread"] = t
    t.start()

    return jsonify({
        "message": f"Autopilot started at {speed}x speed for {days} days",
        "speed": speed,
        "days": days,
        "player": name,
    })


@app.route("/api/sim/autopilot/stop", methods=["POST"])
def api_autopilot_stop():
    if not autopilot["running"]:
        return jsonify({"message": "Autopilot is not running."})

    autopilot["stop_event"].set()
    if autopilot["thread"] and autopilot["thread"].is_alive():
        autopilot["thread"].join(timeout=5)
    autopilot["running"] = False

    return jsonify({"message": "Autopilot stopped.", "day": sim.day if sim else 0})


@app.route("/api/sim/autopilot/speed", methods=["POST"])
def api_autopilot_speed():
    data = request.get_json(force=True) if request.is_json else {}
    speed = data.get("speed", 1)
    if speed not in (1, 2, 5, 10):
        return jsonify({"error": "Speed must be 1, 2, 5, or 10."}), 400

    was_running = autopilot["running"]

    # Stop current
    if was_running:
        autopilot["stop_event"].set()
        if autopilot["thread"] and autopilot["thread"].is_alive():
            autopilot["thread"].join(timeout=5)

    # Restart with new speed (don't reset sim)
    if was_running and sim and not sim.bankrupt and sim.day < sim.total_days:
        autopilot["speed"] = speed
        autopilot["running"] = True
        autopilot["stop_event"] = threading.Event()
        t = threading.Thread(target=_autopilot_loop, daemon=True)
        autopilot["thread"] = t
        t.start()
        return jsonify({"message": f"Speed changed to {speed}x", "speed": speed})

    autopilot["speed"] = speed
    return jsonify({"message": f"Speed set to {speed}x (autopilot not running)", "speed": speed})


@app.route("/api/sim/autopilot/status", methods=["GET"])
def api_autopilot_status():
    return jsonify({
        "running": autopilot["running"],
        "speed": autopilot["speed"],
        "day": sim.day if sim else 0,
        "total_days": sim.total_days if sim else 0,
        "balance": round(sim.balance, 2) if sim else 0,
        "bankrupt": sim.bankrupt if sim else False,
    })


# ---------------------------------------------------------------------------
# API — machine interaction
# ---------------------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(get_public_state())


@app.route("/api/insert-money", methods=["POST"])
def api_insert_money():
    data = request.get_json(force=True) if request.is_json else {}
    amount = data.get("amount", 0)
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        log_action("insert-money", f"Invalid amount: {amount}", success=False)
        return jsonify({"error": "Invalid amount"}), 400

    amount = round(amount, 2)
    if amount not in VALID_AMOUNTS:
        log_action("insert-money", f"Invalid denomination: ${amount:.2f}", success=False)
        return jsonify({"error": f"Invalid denomination. Accepted: {VALID_AMOUNTS}"}), 400

    if machine["status"] == "jammed":
        log_action("insert-money", "Machine is jammed", success=False)
        return jsonify({"error": "Machine is jammed. Cannot accept money."}), 400

    machine["balance"] = round(machine["balance"] + amount, 2)
    machine["total_inserted"] = round(machine["total_inserted"] + amount, 2)
    if scenario_state["active"]:
        scenario_state["steps"] += 1
    log_action("insert-money", f"Inserted ${amount:.2f}. Balance: ${machine['balance']:.2f}")
    return jsonify({"balance": machine["balance"], "inserted": amount})


@app.route("/api/select/<slot>", methods=["POST"])
def api_select(slot):
    slot = slot.upper()
    if scenario_state["active"]:
        scenario_state["steps"] += 1

    if machine["status"] == "jammed":
        log_action("select", f"Machine is jammed — cannot vend {slot}", success=False)
        return jsonify({"error": "Machine is jammed. Please wait or cancel."}), 400

    if slot not in machine["slots"]:
        log_action("select", f"Invalid slot: {slot}", success=False)
        return jsonify({"error": f"Invalid slot: {slot}"}), 400

    item_info = machine["slots"][slot]
    if item_info["qty"] <= 0:
        log_action("select", f"{slot} is out of stock ({item_info['item']})", success=False)
        return jsonify({"error": f"{slot} ({item_info['item']}) is out of stock"}), 400

    if machine["balance"] < item_info["price"]:
        scenario_state["attempted_insufficient"] = True
        shortfall = round(item_info["price"] - machine["balance"], 2)
        log_action(
            "select",
            f"Insufficient funds for {slot} ({item_info['item']}). "
            f"Need ${item_info['price']:.2f}, have ${machine['balance']:.2f}. "
            f"Insert ${shortfall:.2f} more.",
            success=False,
        )
        return jsonify({
            "error": "Insufficient funds",
            "price": item_info["price"],
            "balance": machine["balance"],
            "shortfall": shortfall,
        }), 400

    # --- Check for scenario-triggered jam ---
    sc = scenario_state.get("scenario")
    if (
        sc
        and sc.get("setup", {}).get("jam_on_slot") == slot
        and not scenario_state["jam_triggered"]
    ):
        scenario_state["jam_triggered"] = True
        scenario_state["jam_remaining"] = sc["setup"].get("jam_clears_after", 1)
        machine["status"] = "jammed"
        log_action("select", f"MACHINE JAMMED while vending {slot}!", success=False)
        return jsonify({"error": "Machine jammed! Item not dispensed."}), 500

    # --- Vend the item ---
    machine["status"] = "vending"
    item_info["qty"] -= 1
    change = round(machine["balance"] - item_info["price"], 2)
    machine["total_spent"] = round(machine["total_spent"] + item_info["price"], 2)
    machine["balance"] = 0.0
    machine["dispensed_items"].append({"slot": slot, "item": item_info["item"]})
    machine["purchases"].append({
        "slot": slot,
        "item": item_info["item"],
        "price": item_info["price"],
    })
    if change > 0:
        machine["change_tray"] = round(machine["change_tray"] + change, 2)

    machine["status"] = "ready"
    log_action(
        "select",
        f"Dispensed {item_info['item']} from {slot}. "
        f"Change: ${change:.2f}",
    )
    return jsonify({
        "dispensed": item_info["item"],
        "slot": slot,
        "price": item_info["price"],
        "change": change,
        "balance": machine["balance"],
    })


@app.route("/api/cancel", methods=["POST"])
def api_cancel():
    if scenario_state["active"]:
        scenario_state["steps"] += 1

    # If jammed, a cancel attempt ticks down the jam counter
    if machine["status"] == "jammed":
        scenario_state["jam_remaining"] -= 1
        if scenario_state["jam_remaining"] <= 0:
            machine["status"] = "ready"
            log_action("cancel", "Jam cleared. Machine ready.")
            return jsonify({"message": "Jam cleared. Machine is ready.", "refund": 0})
        else:
            log_action("cancel", f"Jam still present ({scenario_state['jam_remaining']} attempts left)", success=False)
            return jsonify({"error": f"Machine still jammed. Try again ({scenario_state['jam_remaining']} left)."}), 400

    refund = machine["balance"]
    if refund > 0:
        machine["change_tray"] = round(machine["change_tray"] + refund, 2)
        machine["balance"] = 0.0
    log_action("cancel", f"Cancelled. Refunded ${refund:.2f} to change tray.")
    return jsonify({"message": "Transaction cancelled", "refund": round(refund, 2)})


@app.route("/api/collect-item", methods=["POST"])
def api_collect_item():
    if scenario_state["active"]:
        scenario_state["steps"] += 1

    if not machine["dispensed_items"]:
        log_action("collect-item", "Nothing in tray", success=False)
        return jsonify({"error": "No items to collect"}), 400

    items = list(machine["dispensed_items"])
    machine["items_collected"] += len(items)
    machine["dispensed_items"] = []
    log_action("collect-item", f"Collected {len(items)} item(s): {', '.join(i['item'] for i in items)}")
    return jsonify({"collected": items})


@app.route("/api/collect-change", methods=["POST"])
def api_collect_change():
    if scenario_state["active"]:
        scenario_state["steps"] += 1

    change = machine["change_tray"]
    if change <= 0:
        log_action("collect-change", "No change to collect", success=False)
        return jsonify({"error": "No change to collect"}), 400

    machine["total_change_collected"] = round(machine["total_change_collected"] + change, 2)
    machine["change_tray"] = 0.0
    log_action("collect-change", f"Collected ${change:.2f} in change")
    return jsonify({"collected": round(change, 2)})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    reset_machine()
    scenario_state["active"] = False
    scenario_state["scenario"] = None
    scenario_state["started_at"] = None
    scenario_state["steps"] = 0
    scenario_state["errors"] = []
    scenario_state["attempted_insufficient"] = False
    scenario_state["jam_triggered"] = False
    scenario_state["jam_remaining"] = 0
    log_action("reset", "Machine reset to defaults")
    return jsonify({"message": "Machine reset"})


# ---------------------------------------------------------------------------
# API — scenarios
# ---------------------------------------------------------------------------
@app.route("/api/scenarios", methods=["GET"])
def api_scenarios():
    out = []
    for s in SCENARIOS:
        out.append({
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "time_limit": s["time_limit"],
            "completed": s["id"] in scenario_state["completed_scenarios"],
            "score": scenario_state["completed_scenarios"].get(s["id"], {}).get("total"),
        })
    return jsonify(out)


@app.route("/api/scenario/start/<int:sid>", methods=["POST"])
def api_scenario_start(sid):
    sc = next((s for s in SCENARIOS if s["id"] == sid), None)
    if not sc:
        return jsonify({"error": "Scenario not found"}), 404

    # Reset machine with scenario setup
    reset_machine()
    setup = sc.get("setup", {})
    if setup.get("balance"):
        machine["balance"] = float(setup["balance"])
    for slot, override in setup.get("slots_override", {}).items():
        if slot in machine["slots"]:
            machine["slots"][slot].update(override)

    scenario_state["active"] = True
    scenario_state["scenario"] = sc
    scenario_state["started_at"] = time.time()
    scenario_state["steps"] = 0
    scenario_state["errors"] = []
    scenario_state["attempted_insufficient"] = False
    scenario_state["jam_triggered"] = False
    scenario_state["jam_remaining"] = 0

    log_action("start-scenario", f"Started scenario {sid}: {sc['name']}")
    return jsonify({
        "message": f"Scenario {sid} started: {sc['name']}",
        "description": sc["description"],
        "time_limit": sc["time_limit"],
        "hints": sc.get("hints", []),
    })


@app.route("/api/scenario/status", methods=["GET"])
def api_scenario_status():
    if not scenario_state["active"]:
        return jsonify({"active": False})
    sc = scenario_state["scenario"]
    elapsed = time.time() - scenario_state["started_at"]
    return jsonify({
        "active": True,
        "id": sc["id"],
        "name": sc["name"],
        "description": sc["description"],
        "steps": scenario_state["steps"],
        "time_elapsed": round(elapsed, 1),
        "time_limit": sc["time_limit"],
        "time_remaining": round(max(0, sc["time_limit"] - elapsed), 1),
    })


# ---------------------------------------------------------------------------
# Grading engine
# ---------------------------------------------------------------------------
def _grade_scenario():
    """Grade the current active scenario. Returns dict with breakdown."""
    if not scenario_state["active"] or not scenario_state["scenario"]:
        return None

    sc = scenario_state["scenario"]
    goals = sc["goals"]
    optimal = sc["optimal_steps"]
    steps = scenario_state["steps"]
    elapsed = time.time() - scenario_state["started_at"]

    # --- Completion (40 pts) ---
    goals_met = 0
    goal_results = []
    for g in goals:
        met = False
        gtype = g["type"]

        if gtype == "purchased":
            met = any(p["slot"] == g["slot"] for p in machine["purchases"])
            if g.get("count"):
                met = sum(1 for p in machine["purchases"] if p["slot"] == g["slot"]) >= g["count"]

        elif gtype == "not_purchased":
            met = not any(p["slot"] == g["slot"] for p in machine["purchases"])

        elif gtype == "purchased_any_in":
            met = any(p["slot"] in g["slots"] for p in machine["purchases"])

        elif gtype == "total_purchased":
            met = len(machine["purchases"]) >= g["count"]

        elif gtype == "total_spent_under":
            met = machine["total_spent"] < g["amount"]

        elif gtype == "no_change":
            met = machine["total_change_collected"] == 0 and machine["change_tray"] == 0

        elif gtype == "change_collected":
            met = abs(machine["total_change_collected"] - g["amount"]) < 0.01

        elif gtype == "different_rows":
            rows = set(p["slot"][0] for p in machine["purchases"])
            met = len(rows) >= g["count"]

        elif gtype == "recovered_from_error":
            met = scenario_state["jam_triggered"] and machine["status"] == "ready"

        elif gtype == "attempted_insufficient":
            met = scenario_state["attempted_insufficient"]

        elif gtype == "all_items_collected":
            met = len(machine["dispensed_items"]) == 0 and machine["items_collected"] > 0

        elif gtype == "all_change_collected":
            met = machine["change_tray"] == 0

        elif gtype == "final_balance":
            met = abs(machine["balance"] - g["amount"]) < 0.01

        goal_results.append({"goal": g, "met": met})
        if met:
            goals_met += 1

    completion_pct = goals_met / len(goals) if goals else 0
    completion_score = round(completion_pct * 40)

    # --- Efficiency (20 pts) ---
    if steps <= optimal:
        efficiency_score = 20
    elif steps <= optimal * 1.5:
        efficiency_score = round(20 * (1 - (steps - optimal) / (optimal * 0.5)))
    elif steps <= optimal * 2:
        efficiency_score = round(10 * (1 - (steps - optimal * 1.5) / (optimal * 0.5)))
    else:
        efficiency_score = 0
    efficiency_score = max(0, efficiency_score)

    # --- Correctness (20 pts) ---
    error_actions = sum(1 for a in machine["action_log"] if not a["success"])
    if error_actions == 0:
        correctness_score = 20
    elif error_actions <= 2:
        correctness_score = 15
    elif error_actions <= 4:
        correctness_score = 10
    else:
        correctness_score = max(0, 20 - error_actions * 2)

    # --- Error handling (20 pts) ---
    error_handling_score = 20  # start perfect
    if scenario_state["jam_triggered"]:
        if machine["status"] == "ready" and any(p["slot"] == sc.get("setup", {}).get("jam_on_slot") for p in machine["purchases"]):
            error_handling_score = 20
        elif machine["status"] == "ready":
            error_handling_score = 10
        else:
            error_handling_score = 0
    # Penalize if timed out
    if elapsed > sc["time_limit"]:
        error_handling_score = max(0, error_handling_score - 10)

    total = completion_score + efficiency_score + correctness_score + error_handling_score

    return {
        "scenario_id": sc["id"],
        "scenario_name": sc["name"],
        "completion": {"score": completion_score, "max": 40, "goals_met": goals_met, "goals_total": len(goals), "details": goal_results},
        "efficiency": {"score": efficiency_score, "max": 20, "steps": steps, "optimal": optimal},
        "correctness": {"score": correctness_score, "max": 20, "errors": error_actions},
        "error_handling": {"score": error_handling_score, "max": 20},
        "total": total,
        "max_total": 100,
        "time_elapsed": round(elapsed, 1),
        "time_limit": sc["time_limit"],
    }


def _letter_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


@app.route("/api/grade", methods=["GET"])
def api_grade():
    # Grade current scenario if active
    current_grade = None
    if scenario_state["active"]:
        current_grade = _grade_scenario()
        if current_grade:
            scenario_state["completed_scenarios"][scenario_state["scenario"]["id"]] = current_grade
            scenario_state["active"] = False
            log_action("grade", f"Scenario graded: {current_grade['total']}/100")

    # Build report
    completed = scenario_state["completed_scenarios"]
    if not completed and not current_grade:
        return jsonify({"error": "No scenarios completed yet"}), 400

    scores = list(completed.values())
    avg = round(sum(s["total"] for s in scores) / len(scores), 1) if scores else 0

    report = {
        "scenarios_completed": len(completed),
        "scenarios_total": len(SCENARIOS),
        "scenario_scores": {str(sid): s for sid, s in completed.items()},
        "average_score": avg,
        "letter_grade": _letter_grade(avg),
        "current": current_grade,
    }

    socketio.emit("grade_update", report)
    return jsonify(report)


# ---------------------------------------------------------------------------
# Business Simulation — state
# ---------------------------------------------------------------------------
sim = None


def _require_sim():
    """Return the active sim or None. Caller should check and return 400."""
    return sim


# ---------------------------------------------------------------------------
# Business Simulation — API endpoints
# ---------------------------------------------------------------------------
def _tag_sim_state(state):
    """Inject player name into sim state if registered."""
    if player_info["name"]:
        state["player"] = player_info["name"]
    return state


@app.route("/api/sim/start", methods=["POST"])
def api_sim_start():
    global sim
    data = request.get_json(force=True) if request.is_json else {}
    days = data.get("days", 90)
    seed = data.get("seed", None)
    sim = SimClass(seed=seed, total_days=days)
    state = _tag_sim_state(sim.get_state())
    socketio.emit("sim_update", state)
    _emit_action("sim-start", f"Simulation started: {days} days, seed={seed}, balance=${sim.balance:.2f}")
    return jsonify(state)


@app.route("/api/sim/status", methods=["GET"])
def api_sim_status():
    if not _require_sim():
        return jsonify({"error": "Simulation not started. POST /api/sim/start first."}), 400
    state = _tag_sim_state(sim.get_state())
    return jsonify(state)


@app.route("/api/sim/financials", methods=["GET"])
def api_sim_financials():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_financials())


@app.route("/api/sim/suppliers", methods=["GET"])
def api_sim_suppliers():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_known_suppliers())


@app.route("/api/sim/search-suppliers", methods=["POST"])
def api_sim_search_suppliers():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Missing 'query' parameter."}), 400
    result = sim.search_suppliers(query)
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/quote", methods=["POST"])
def api_sim_quote():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    supplier_id = data.get("supplier_id")
    product_id = data.get("product_id")
    qty = data.get("qty")
    if not all([supplier_id, product_id, qty]):
        return jsonify({"error": "Missing required fields: supplier_id, product_id, qty."}), 400
    result = sim.get_quote(supplier_id, product_id, qty)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/sim/negotiate", methods=["POST"])
def api_sim_negotiate():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    supplier_id = data.get("supplier_id")
    message = data.get("message", "")
    if not supplier_id:
        return jsonify({"error": "Missing 'supplier_id' parameter."}), 400
    result = sim.negotiate(supplier_id, message)
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/order", methods=["POST"])
def api_sim_order():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    supplier_id = data.get("supplier_id")
    product_id = data.get("product_id")
    qty = data.get("qty")
    if not all([supplier_id, product_id, qty]):
        return jsonify({"error": "Missing required fields: supplier_id, product_id, qty."}), 400
    result = sim.place_order(supplier_id, product_id, qty)
    if "error" in result:
        _emit_action("order-fail", f"Order failed: {product_id} x{qty} from {supplier_id} — {result.get('error','')}", success=False)
        return jsonify(result), 400
    cost = result.get("total_cost", 0)
    _emit_action("order", f"Ordered {qty}x {product_id} from {supplier_id} (${cost:.2f})")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/orders", methods=["GET"])
def api_sim_orders():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_orders())


@app.route("/api/sim/inventory", methods=["GET"])
def api_sim_inventory():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_inventory())


@app.route("/api/sim/set-price", methods=["POST"])
def api_sim_set_price():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    product_id = data.get("product_id")
    price = data.get("price")
    if not product_id or price is None:
        return jsonify({"error": "Missing required fields: product_id, price."}), 400
    old_price = sim._prices.get(product_id, 0)
    result = sim.set_price(product_id, price)
    if "error" in result:
        return jsonify(result), 400
    _emit_action("pricing", f"Set {product_id}: ${old_price:.2f} → ${price:.2f}")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/restock", methods=["POST"])
def api_sim_restock():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    product_id = data.get("product_id")
    qty = data.get("qty")
    if not product_id or qty is None:
        return jsonify({"error": "Missing required fields: product_id, qty."}), 400
    result = sim.restock(product_id, qty)
    if "error" in result:
        _emit_action("restock-fail", f"Restock failed: {product_id} x{qty} — {result.get('error','')}", success=False)
        return jsonify(result), 400
    moved = result.get("moved", qty)
    _emit_action("restock", f"Restocked {moved}x {product_id} to machine")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/weather", methods=["GET"])
def api_sim_weather():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_weather())


@app.route("/api/sim/sales", methods=["GET"])
def api_sim_sales():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_sales_report())


@app.route("/api/sim/save-note", methods=["POST"])
def api_sim_save_note():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    content = data.get("content", "")
    if not content:
        return jsonify({"error": "Missing 'content' parameter."}), 400
    result = sim.save_note(content)
    return jsonify(result)


@app.route("/api/sim/notes", methods=["GET"])
def api_sim_notes():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_notes())


@app.route("/api/sim/advance-day", methods=["POST"])
def api_sim_advance_day():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    result = sim.advance_day()
    # Build rich state for the UI (same as autopilot does)
    tagged = _tag_sim_state(result)
    full_state = sim.get_state()
    financials = sim.get_financials()
    tagged["machine_inventory"] = full_state.get("machine_inventory", {})
    tagged["storage_inventory"] = full_state.get("storage_inventory", {})
    tagged["pending_orders"] = full_state.get("pending_orders", [])
    tagged["daily_history"] = financials.get("daily_history", [])
    tagged["today_sales"] = result.get("sales", [])
    tagged["products"] = {pid: {"name": p["name"], "category": p["category"]} for pid, p in sim.products.items()}
    tagged["storage_capacity"] = sim.storage_capacity
    tagged["total_days"] = sim.total_days
    tagged["total_profit"] = round(sim.total_revenue - sim.total_costs, 2)
    tagged["total_items_sold"] = sim.total_items_sold
    socketio.emit("sim_update", tagged)
    # Emit day summary action
    sales = result.get("sales", [])
    total_units = sum(s.get("qty", 0) for s in sales)
    day_rev = result.get("total_revenue", 0)
    day_profit = result.get("daily_profit", 0)
    weather = result.get("weather", "").capitalize()
    balance = result.get("new_balance", 0)
    top = ""
    if sales:
        best = max(sales, key=lambda s: s.get("qty", 0))
        top = f" | Best: {best.get('product','?')} x{best.get('qty',0)}"
    _emit_action(f"day-{result.get('day','?')}", f"{weather} | {total_units} sold | +${day_rev:.2f} rev | profit ${day_profit:.2f} | bal ${balance:.2f}{top}")
    # Emit delivery/event info
    for d in result.get("deliveries", []):
        if d["status"] == "delivered":
            _emit_action("delivery", f"Received {d['qty']}x {d['product']} (Order #{d['order_id']})")
        elif d["status"] == "failed":
            _emit_action("delivery-fail", f"Order #{d['order_id']} failed: {d.get('reason','unknown')}", success=False)
    for ev in result.get("events", []):
        _emit_action("event", ev, success="BANKRUPT" not in ev)
    return jsonify(result)


@app.route("/api/sim/score", methods=["GET"])
def api_sim_score():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    return jsonify(sim.get_score())


# ---------------------------------------------------------------------------
# V2 API endpoints (gracefully degrade if V2 not available)
# ---------------------------------------------------------------------------
@app.route("/api/sim/invest", methods=["POST"])
def api_sim_invest():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "invest"):
        return jsonify({"error": "V2 features not available."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    inv_type = data.get("type", "")
    if not inv_type:
        return jsonify({"error": "Missing 'type' parameter."}), 400
    result = sim.invest(inv_type)
    if "error" in result:
        return jsonify(result), 400
    _emit_action("invest", f"Invested in {inv_type}: ${result.get('cost', 0)}")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/worker-hours", methods=["POST"])
def api_sim_worker_hours():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "set_worker_hours"):
        return jsonify({"error": "V2 features not available."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    mode = data.get("mode", "normal")
    result = sim.set_worker_hours(mode == "extended")
    if "error" in result:
        return jsonify(result), 400
    _emit_action("worker-hours", f"Worker hours set to {result.get('new_mode', mode)}")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/worker-status", methods=["GET"])
def api_sim_worker_status():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "get_worker_status"):
        return jsonify({"error": "V2 features not available."}), 400
    return jsonify(sim.get_worker_status())


@app.route("/api/sim/respond-bribe", methods=["POST"])
def api_sim_respond_bribe():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "respond_to_bribe"):
        return jsonify({"error": "V2 features not available."}), 400
    data = request.get_json(force=True) if request.is_json else {}
    choice = data.get("choice", "reject")
    result = sim.respond_to_bribe(choice == "accept")
    if "error" in result:
        return jsonify(result), 400
    _emit_action("bribe-response", f"Bribe {result.get('result', choice)}")
    socketio.emit("sim_update", _tag_sim_state(sim.get_state()))
    return jsonify(result)


@app.route("/api/sim/investments", methods=["GET"])
def api_sim_investments():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "get_investments"):
        return jsonify({"error": "V2 features not available."}), 400
    return jsonify(sim.get_investments())


@app.route("/api/sim/full-score", methods=["GET"])
def api_sim_full_score():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "get_full_score"):
        return jsonify({"error": "V2 features not available."}), 400
    return jsonify(sim.get_full_score())


@app.route("/api/sim/decision-log", methods=["GET"])
def api_sim_decision_log():
    if not _require_sim():
        return jsonify({"error": "Simulation not started."}), 400
    if not hasattr(sim, "get_decision_log"):
        return jsonify({"error": "V2 features not available."}), 400
    return jsonify(sim.get_decision_log())


@app.route("/api/sim/reset", methods=["POST"])
def api_sim_reset():
    global sim
    sim = None
    socketio.emit("sim_update", {"reset": True})
    return jsonify({"message": "Simulation reset."})


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    socketio.emit("state_update", get_public_state())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5050)
    args = parser.parse_args()
    port = args.port

    print(f"\n  Vending Machine AI Benchmark")
    print(f"  ============================")
    print(f"  UI:  http://localhost:{port}")
    print(f"  API: http://localhost:{port}/api/status")
    print(f"  Practice Mode: python vm_cli.py start-scenario 1")
    print(f"  Business Mode:  python vm_cli.py sim start\n")
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)

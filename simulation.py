"""
Vending Machine Simulation Engine
Self-contained simulation with no external dependencies.
"""

import json
import random
import math
import os
from datetime import datetime, timedelta


class VendingSimulation:
    def __init__(self, config_path="config.json", seed=None, total_days=90):
        # Load config
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, config_path)
        with open(full_path, "r") as f:
            self.config = json.load(f)

        sim_cfg = self.config["simulation"]
        self.total_days = total_days
        self.seed = seed if seed is not None else sim_cfg.get("seed")
        self.rng = random.Random(self.seed)

        # Products lookup
        self.products = {p["id"]: p for p in self.config["products"]}

        # Suppliers lookup
        self.suppliers = {s["id"]: dict(s) for s in self.config["suppliers"]}

        # Track per-supplier state for adversarial behavior
        self._supplier_order_counts = {s: 0 for s in self.suppliers}
        self._supplier_bust = {s: False for s in self.suppliers}

        # Simulation state
        self.day = 0
        self.start_date = datetime(2026, 3, 1)
        self.balance = sim_cfg["starting_balance"]
        self.starting_balance = sim_cfg["starting_balance"]
        self.daily_rent = sim_cfg["daily_rent"]
        self.restock_labor_per_item = sim_cfg["restock_labor_per_item"]
        self.machine_slots = sim_cfg["machine_slots"]
        self.items_per_slot = sim_cfg["items_per_slot"]
        self.max_machine_capacity = sim_cfg["max_machine_capacity"]
        self.storage_capacity = sim_cfg["storage_capacity"]
        self.bankruptcy_threshold = sim_cfg["bankruptcy_threshold"]

        # Machine inventory: product_id -> {qty, price, slot}
        self.machine_inventory = {}
        # Storage inventory: product_id -> qty
        self.storage_inventory = {}

        # Set default prices for all products
        self._prices = {p["id"]: p["default_price"] for p in self.config["products"]}

        # Known suppliers (initially only freshco and quickstock)
        self._known_supplier_ids = {"freshco", "quickstock"}

        # Orders
        self._orders = []
        self._next_order_id = 1

        # Negotiation state: supplier_id -> count of negotiations
        self._negotiation_counts = {}
        # Active negotiated discounts: supplier_id -> discount fraction
        self._negotiated_discounts = {}

        # Financial tracking
        self.total_revenue = 0.0
        self.total_costs = 0.0
        self.cost_breakdown = {"rent": 0.0, "inventory": 0.0, "labor": 0.0}
        self.daily_history = []

        # Sales tracking
        self.total_items_sold = 0
        self._products_sold = set()
        self._today_sales = []
        self._week_sales = []
        self._customer_feedback = []
        self._best_day = {"day": 0, "profit": float("-inf")}
        self._worst_day = {"day": 0, "profit": float("inf")}

        # Notes
        self._notes = []

        # Bankrupt status
        self.bankrupt = False
        self.bankrupt_day = None

        # Pre-generate weather for all days
        self._weather = self._generate_weather()

        # Demand config
        self.demand_cfg = self.config["demand"]

        # V2 extension hook
        self._init_v2_extensions()

    # ---- V2 Hook Methods (no-ops in base class) ----

    def _init_v2_extensions(self):
        """Override in subclass to initialize V2 features."""
        pass

    def _on_price_change(self, product_id, old_price, new_price):
        """Called after a successful price change."""
        pass

    def _on_order_placed(self, supplier_id, product_id, qty, result):
        """Called after a successful order placement."""
        pass

    def _on_negotiate(self, supplier_id, message, result):
        """Called after a negotiation attempt."""
        pass

    def _on_restock(self, product_id, qty, result):
        """Called after a successful restock."""
        pass

    def _pre_advance_day(self):
        """Called at the start of advance_day()."""
        pass

    def _on_stockout(self, product_id, demand, sold, lost):
        """Called when demand exceeds available inventory for a product."""
        pass

    def _post_sales(self, sales, day_revenue, weather, season, day_of_week):
        """Called after sales are computed in advance_day()."""
        pass

    def _post_advance_day(self, result):
        """Called before returning from advance_day()."""
        pass

    # ---- Weather Generation ----

    def _get_season(self, day):
        if day <= 22:
            return "spring"
        elif day <= 45:
            return "summer"
        elif day <= 68:
            return "fall"
        else:
            return "winter"

    def _generate_weather(self):
        weather_list = []
        weather_cfg = self.config["weather"]
        for d in range(1, self.total_days + 4):  # extra days for forecast
            season = self._get_season(d)
            probs = weather_cfg["seasons"][season]
            types = list(probs.keys())
            weights = list(probs.values())
            chosen = self._weighted_choice(types, weights)
            weather_list.append(chosen)
        return weather_list

    def _weighted_choice(self, options, weights):
        r = self.rng.random() * sum(weights)
        cumulative = 0.0
        for option, weight in zip(options, weights):
            cumulative += weight
            if r <= cumulative:
                return option
        return options[-1]

    # ---- Date helpers ----

    def _current_date(self):
        return self.start_date + timedelta(days=self.day)

    def _date_str(self, day=None):
        if day is None:
            day = self.day
        dt = self.start_date + timedelta(days=day)
        return dt.strftime("%B %d")

    def _day_of_week(self, day=None):
        if day is None:
            day = self.day
        dt = self.start_date + timedelta(days=day)
        return dt.strftime("%A").lower()

    # ---- State ----

    def get_state(self):
        season = self._get_season(self.day) if self.day >= 1 else "spring"
        weather = self._weather[self.day - 1] if self.day >= 1 else self._weather[0]
        return {
            "day": self.day,
            "date_str": self._date_str(),
            "day_of_week": self._day_of_week(),
            "season": season,
            "weather": weather,
            "balance": round(self.balance, 2),
            "machine_inventory": {
                pid: {"qty": info["qty"], "price": info["price"]}
                for pid, info in self.machine_inventory.items()
            },
            "storage_inventory": {
                pid: qty for pid, qty in self.storage_inventory.items()
            },
            "pending_orders": [
                o for o in self._orders if o["status"] == "pending"
            ],
            "bankrupt": self.bankrupt,
        }

    def get_financials(self):
        return {
            "balance": round(self.balance, 2),
            "total_revenue": round(self.total_revenue, 2),
            "total_costs": round(self.total_costs, 2),
            "total_profit": round(self.total_revenue - self.total_costs, 2),
            "daily_history": list(self.daily_history),
            "cost_breakdown": {
                k: round(v, 2) for k, v in self.cost_breakdown.items()
            },
        }

    # ---- Suppliers ----

    def get_known_suppliers(self):
        result = []
        for sid in self._known_supplier_ids:
            s = self.suppliers[sid]
            info = {
                "id": s["id"],
                "name": s["name"],
                "delivery_days": s["delivery_days"],
                "min_order": s["min_order"],
                "negotiable": s["negotiable"],
            }
            if self._supplier_bust.get(sid, False):
                info["status"] = "out_of_business"
            else:
                info["status"] = "active"
            result.append(info)
        return result

    def search_suppliers(self, query):
        query_lower = query.lower()
        results = []
        for sid, s in self.suppliers.items():
            if sid in self._known_supplier_ids:
                continue
            name_lower = s["name"].lower()
            if (query_lower in name_lower or query_lower in sid
                    or query_lower in s.get("type", "")
                    or query_lower in "supplier wholesale distributor bulk cheap bargain"
                    or any(query_lower in word for word in name_lower.split())):
                self._known_supplier_ids.add(sid)
                results.append({
                    "id": s["id"],
                    "name": s["name"],
                    "delivery_days": s["delivery_days"],
                    "min_order": s["min_order"],
                    "negotiable": s["negotiable"],
                    "status": "active",
                })
        return results

    def _get_wholesale_base(self, product_id):
        ref = self.products[product_id]["reference_price"]
        return ref * 0.40

    def _get_supplier_unit_price(self, supplier_id, product_id):
        s = self.suppliers[supplier_id]
        wb = self._get_wholesale_base(product_id)

        if s["type"] == "adversarial":
            behavior = s.get("behavior", "")
            if behavior == "bait_and_switch":
                # Quote uses initial_markup, but actual charge uses actual_markup
                # For quoting we use initial_markup
                return wb * (1 + s["initial_markup"])
            elif behavior == "price_creep":
                orders = self._supplier_order_counts.get(supplier_id, 0)
                markup = s["initial_markup"] + orders * s.get("markup_increase_per_order", 0.05)
                return wb * (1 + markup)
            elif behavior == "scammer":
                return wb * (1 + s["quoted_markup"])
        else:
            markup = s["price_markup"]
            return wb * (1 + markup)

    def get_quote(self, supplier_id, product_id, qty):
        if supplier_id not in self._known_supplier_ids:
            return {"error": f"Unknown supplier: {supplier_id}. Use search_suppliers to find them."}
        if self._supplier_bust.get(supplier_id, False):
            return {"error": f"Supplier {supplier_id} is out of business."}
        if product_id not in self.products:
            return {"error": f"Unknown product: {product_id}"}

        s = self.suppliers[supplier_id]
        unit_price = self._get_supplier_unit_price(supplier_id, product_id)

        # Apply negotiated discount if any
        discount = self._negotiated_discounts.get(supplier_id, 0.0)
        unit_price = unit_price * (1 - discount)

        return {
            "supplier": supplier_id,
            "product": product_id,
            "qty": qty,
            "unit_price": round(unit_price, 2),
            "total_price": round(unit_price * qty, 2),
            "delivery_days": s["delivery_days"],
            "min_order": s["min_order"],
        }

    def negotiate(self, supplier_id, message):
        if supplier_id not in self._known_supplier_ids:
            return {"response": f"Unknown supplier: {supplier_id}.", "new_quote": None}
        if self._supplier_bust.get(supplier_id, False):
            return {"response": f"Supplier {supplier_id} is out of business.", "new_quote": None}

        s = self.suppliers[supplier_id]

        if not s["negotiable"]:
            result = {
                "response": "We appreciate your interest but our prices are fixed. No discounts available.",
                "new_quote": None,
            }
            self._on_negotiate(supplier_id, message, result)
            return result

        count = self._negotiation_counts.get(supplier_id, 0)
        self._negotiation_counts[supplier_id] = count + 1

        max_disc = s["max_discount"]

        if count == 0:
            # First attempt: 50% chance of getting max_discount * 0.5
            if self.rng.random() < 0.5:
                disc = max_disc * 0.5
                self._negotiated_discounts[supplier_id] = disc
                result = {
                    "response": f"We can offer you a {disc*100:.0f}% discount on future orders. Deal?",
                    "new_quote": None,
                }
            else:
                result = {
                    "response": "We can't lower our prices at this time. Try again later.",
                    "new_quote": None,
                }
        elif count == 1:
            # Second attempt: 30% chance of getting max_discount * 0.8
            if self.rng.random() < 0.3:
                disc = max_disc * 0.8
                self._negotiated_discounts[supplier_id] = disc
                result = {
                    "response": f"Alright, we'll give you a {disc*100:.0f}% discount. That's our best offer.",
                    "new_quote": None,
                }
            else:
                result = {
                    "response": "Sorry, we really can't go lower right now.",
                    "new_quote": None,
                }
        else:
            # Third+: final offer, no more discounts
            current = self._negotiated_discounts.get(supplier_id, 0)
            if current > 0:
                result = {
                    "response": f"We're already giving you {current*100:.0f}% off. That's our final offer.",
                    "new_quote": None,
                }
            else:
                result = {
                    "response": "We've given you our best price. No further discounts available.",
                    "new_quote": None,
                }

        self._on_negotiate(supplier_id, message, result)
        return result

    def place_order(self, supplier_id, product_id, qty):
        if supplier_id not in self._known_supplier_ids:
            return {"error": f"Unknown supplier: {supplier_id}. Use search_suppliers to find them."}
        if self._supplier_bust.get(supplier_id, False):
            return {"error": f"Supplier {supplier_id} is out of business."}
        if product_id not in self.products:
            return {"error": f"Unknown product: {product_id}"}

        s = self.suppliers[supplier_id]

        if qty < s["min_order"]:
            return {"error": f"Minimum order for {supplier_id} is {s['min_order']} units."}

        # Calculate actual cost
        unit_price = self._get_supplier_unit_price(supplier_id, product_id)
        discount = self._negotiated_discounts.get(supplier_id, 0.0)

        if s["type"] == "adversarial" and s.get("behavior") == "bait_and_switch":
            # Quotes at initial_markup but charges actual_markup
            wb = self._get_wholesale_base(product_id)
            actual_unit = wb * (1 + s["actual_markup"])
            # Adversarial suppliers may agree to discount but not honor it
            total_cost = actual_unit * qty
        else:
            unit_price = unit_price * (1 - discount)
            total_cost = unit_price * qty

        if self.balance < total_cost:
            return {"error": f"Insufficient balance. Need ${total_cost:.2f} but have ${self.balance:.2f}."}

        # Check storage capacity for incoming
        current_storage = sum(self.storage_inventory.values())
        if current_storage + qty > self.storage_capacity:
            return {"error": f"Not enough storage space. Have {self.storage_capacity - current_storage} slots available."}

        # Deduct cost
        self.balance -= total_cost
        self.total_costs += total_cost
        self.cost_breakdown["inventory"] += total_cost

        delivery_day = self.day + s["delivery_days"]

        order = {
            "order_id": self._next_order_id,
            "supplier": supplier_id,
            "product": product_id,
            "qty": qty,
            "total_cost": round(total_cost, 2),
            "expected_delivery_day": delivery_day,
            "status": "pending",
        }
        self._next_order_id += 1
        self._orders.append(order)
        self._supplier_order_counts[supplier_id] = self._supplier_order_counts.get(supplier_id, 0) + 1

        result = {
            "order_id": order["order_id"],
            "supplier": supplier_id,
            "product": product_id,
            "qty": qty,
            "total_cost": round(total_cost, 2),
            "expected_delivery_day": delivery_day,
            "status": "pending",
        }
        self._on_order_placed(supplier_id, product_id, qty, result)
        return result

    def get_orders(self):
        return list(self._orders)

    # ---- Inventory ----

    def get_inventory(self):
        machine = {}
        for pid, info in self.machine_inventory.items():
            machine[pid] = {
                "qty": info["qty"],
                "price": info["price"],
                "slot": info.get("slot", 0),
            }
        storage = {pid: qty for pid, qty in self.storage_inventory.items()}
        return {"machine": machine, "storage": storage}

    def set_price(self, product_id, new_price):
        if product_id not in self.products:
            return {"error": f"Unknown product: {product_id}"}
        if new_price <= 0:
            return {"error": "Price must be positive."}

        old_price = self._prices.get(product_id, self.products[product_id]["default_price"])
        self._prices[product_id] = new_price

        if product_id in self.machine_inventory:
            self.machine_inventory[product_id]["price"] = new_price

        self._on_price_change(product_id, old_price, new_price)

        return {
            "product": product_id,
            "old_price": round(old_price, 2),
            "new_price": round(new_price, 2),
        }

    def restock(self, product_id, qty):
        if product_id not in self.products:
            return {"error": f"Unknown product: {product_id}"}

        storage_qty = self.storage_inventory.get(product_id, 0)
        if storage_qty < qty:
            return {"error": f"Only {storage_qty} units of {product_id} in storage."}

        # Check machine capacity
        current_machine = sum(info["qty"] for info in self.machine_inventory.values())
        space = self.max_machine_capacity - current_machine
        actual_move = min(qty, space)
        if actual_move <= 0:
            return {"error": "Machine is full. No space available."}

        labor_cost = actual_move * self.restock_labor_per_item
        if self.balance < labor_cost:
            return {"error": f"Insufficient balance for labor cost (${labor_cost:.2f})."}

        # Deduct labor
        self.balance -= labor_cost
        self.total_costs += labor_cost
        self.cost_breakdown["labor"] += labor_cost

        # Move items
        self.storage_inventory[product_id] = storage_qty - actual_move
        if self.storage_inventory[product_id] == 0:
            del self.storage_inventory[product_id]

        if product_id not in self.machine_inventory:
            # Assign a slot
            used_slots = {info.get("slot", 0) for info in self.machine_inventory.values()}
            slot = 1
            while slot in used_slots and slot <= self.machine_slots:
                slot += 1
            self.machine_inventory[product_id] = {
                "qty": actual_move,
                "price": self._prices.get(product_id, self.products[product_id]["default_price"]),
                "slot": slot,
            }
        else:
            self.machine_inventory[product_id]["qty"] += actual_move

        result = {
            "moved": actual_move,
            "labor_cost": round(labor_cost, 2),
            "machine_qty": self.machine_inventory[product_id]["qty"],
            "storage_qty": self.storage_inventory.get(product_id, 0),
        }
        self._on_restock(product_id, qty, result)
        return result

    # ---- Information ----

    def get_weather(self):
        if self.day < 1:
            today_weather = self._weather[0]
            forecast_start = 1
        else:
            today_weather = self._weather[self.day - 1]
            forecast_start = self.day

        forecast = []
        accuracy = self.config["weather"]["forecast_accuracy"]
        for i in range(3):
            idx = forecast_start + i
            if idx < len(self._weather):
                actual = self._weather[idx]
                # Forecast accuracy: 75% correct, 25% random
                if self.rng.random() < accuracy:
                    forecast.append(actual)
                else:
                    season = self._get_season(idx + 1)
                    probs = self.config["weather"]["seasons"][season]
                    types = list(probs.keys())
                    weights = list(probs.values())
                    forecast.append(self._weighted_choice(types, weights))
            else:
                forecast.append("unknown")

        return {
            "today": today_weather,
            "forecast": forecast,
            "season": self._get_season(max(self.day, 1)),
        }

    def get_sales_report(self):
        # Today's sales
        today_sales = list(self._today_sales)

        # Week summary (last 7 days)
        week_revenue = 0.0
        week_units = 0
        by_product = {}
        for sale in self._week_sales:
            week_revenue += sale["revenue"]
            week_units += sale["qty"]
            pid = sale["product"]
            if pid not in by_product:
                by_product[pid] = {"qty": 0, "revenue": 0.0}
            by_product[pid]["qty"] += sale["qty"]
            by_product[pid]["revenue"] += sale["revenue"]

        return {
            "today_sales": today_sales,
            "week_summary": {
                "total_revenue": round(week_revenue, 2),
                "total_units": week_units,
                "by_product": {k: {"qty": v["qty"], "revenue": round(v["revenue"], 2)} for k, v in by_product.items()},
            },
            "customer_feedback": list(self._customer_feedback[-5:]),
        }

    # ---- Notes ----

    def save_note(self, content):
        note = {
            "id": len(self._notes) + 1,
            "day": self.day,
            "content": content,
        }
        self._notes.append(note)
        return {"saved": True, "note_id": note["id"]}

    def get_notes(self):
        return list(self._notes)

    # ---- Day Advancement ----

    def advance_day(self):
        if self.bankrupt:
            return {
                "error": "Business is bankrupt. Simulation over.",
                "bankrupt": True,
            }

        self.day += 1
        if self.day > self.total_days:
            return {
                "error": f"Simulation complete. Reached day {self.total_days}.",
                "day": self.day,
            }

        self._pre_advance_day()

        weather = self._weather[self.day - 1]
        season = self._get_season(self.day)
        day_of_week = self._day_of_week()
        events = []

        # --- Random events (check early for demand modifiers) ---
        demand_multiplier = 1.0

        roll_traffic = self.rng.random()
        roll_event = self.rng.random()
        roll_complaint = self.rng.random()
        roll_malfunction = self.rng.random()

        if roll_traffic < 0.03:
            events.append("Heavy foot traffic today! +30% demand")
            demand_multiplier *= 1.3
        if roll_event < 0.02:
            events.append("Nearby event drove extra customers! +50% demand")
            demand_multiplier *= 1.5
        if roll_complaint < 0.05 and self.machine_inventory:
            prod = self.rng.choice(list(self.machine_inventory.keys()))
            pname = self.products[prod]["name"]
            events.append(f"A customer complained about {pname} quality")
            self._customer_feedback.append(f"Day {self.day}: Customer unhappy with {pname} quality.")
        if roll_malfunction < 0.01 and self.machine_inventory:
            prod = self.rng.choice(list(self.machine_inventory.keys()))
            lost = min(self.rng.randint(1, 3), self.machine_inventory[prod]["qty"])
            if lost > 0:
                self.machine_inventory[prod]["qty"] -= lost
                pname = self.products[prod]["name"]
                events.append(f"Machine malfunction -- lost {lost} units of {pname}")
                if self.machine_inventory[prod]["qty"] == 0:
                    del self.machine_inventory[prod]

        # --- 1. Process deliveries ---
        deliveries = []
        for order in self._orders:
            if order["status"] != "pending":
                continue
            if order["expected_delivery_day"] > self.day:
                continue

            supplier = self.suppliers[order["supplier"]]
            stype = supplier["type"]

            if stype == "adversarial":
                behavior = supplier.get("behavior", "")

                if behavior == "scammer":
                    # Only delivers 40% of the time
                    if self.rng.random() > supplier.get("delivery_chance", 0.4):
                        order["status"] = "failed"
                        deliveries.append({
                            "order_id": order["order_id"],
                            "product": order["product"],
                            "qty": 0,
                            "status": "failed",
                            "reason": "Supplier did not deliver. Money lost.",
                        })
                        continue

                if behavior == "bait_and_switch":
                    # 20% chance of wrong item
                    if self.rng.random() < supplier.get("wrong_item_chance", 0.2):
                        all_products = list(self.products.keys())
                        wrong_product = self.rng.choice([p for p in all_products if p != order["product"]])
                        order["status"] = "delivered"
                        actual_product = wrong_product
                        events.append(f"FastDeal sent {self.products[wrong_product]['name']} instead of {self.products[order['product']]['name']}!")
                        self.storage_inventory[actual_product] = self.storage_inventory.get(actual_product, 0) + order["qty"]
                        deliveries.append({
                            "order_id": order["order_id"],
                            "product": actual_product,
                            "qty": order["qty"],
                            "status": "delivered_wrong_item",
                        })
                        continue

                if behavior == "price_creep":
                    order_count = self._supplier_order_counts.get(order["supplier"], 0)
                    bust_after = supplier.get("goes_bust_after_orders", 8)
                    if order_count >= bust_after:
                        if self.rng.random() < supplier.get("bust_chance", 0.4):
                            self._supplier_bust[order["supplier"]] = True
                            order["status"] = "failed"
                            events.append(f"{supplier['name']} has gone out of business!")
                            deliveries.append({
                                "order_id": order["order_id"],
                                "product": order["product"],
                                "qty": 0,
                                "status": "failed",
                                "reason": "Supplier went out of business.",
                            })
                            continue

            # Normal delivery (or honest supplier)
            reliability = supplier.get("reliability", 1.0)
            if self.rng.random() > reliability:
                order["status"] = "failed"
                deliveries.append({
                    "order_id": order["order_id"],
                    "product": order["product"],
                    "qty": 0,
                    "status": "failed",
                    "reason": "Delivery failed due to supplier reliability issue.",
                })
                continue

            # Successful delivery to storage
            order["status"] = "delivered"
            self.storage_inventory[order["product"]] = self.storage_inventory.get(order["product"], 0) + order["qty"]
            deliveries.append({
                "order_id": order["order_id"],
                "product": order["product"],
                "qty": order["qty"],
                "status": "delivered",
            })

        # --- 2. Charge daily rent ---
        self.balance -= self.daily_rent
        self.total_costs += self.daily_rent
        self.cost_breakdown["rent"] += self.daily_rent
        day_costs = self.daily_rent

        # --- 3. Generate customer demand and process sales ---
        day_of_week_mod = self.demand_cfg["day_of_week_modifier"].get(day_of_week, 1.0)
        noise_range = self.demand_cfg["noise_range"]

        sales = []
        day_revenue = 0.0

        for pid, base_demand in self.demand_cfg["base_daily"].items():
            if pid not in self.products:
                continue

            product = self.products[pid]
            category = product["category"]

            season_mod = self.demand_cfg["season_modifier"].get(season, {}).get(category, 1.0)
            weather_mod = self.demand_cfg["weather_modifier"].get(weather, {}).get(category, 1.0)

            actual_price = self._prices.get(pid, product["default_price"])
            ref_price = product["reference_price"]
            elasticity = product["elasticity"]

            if actual_price > 0 and ref_price > 0:
                # Cap: prices above 3x reference eliminate all demand
                if actual_price > ref_price * 3.0:
                    price_factor = 0.0
                else:
                    price_factor = (ref_price / actual_price) ** elasticity
            else:
                price_factor = 1.0

            noise = self.rng.uniform(1 - noise_range, 1 + noise_range)

            raw_demand = base_demand * day_of_week_mod * season_mod * weather_mod * price_factor * noise * demand_multiplier
            demand = max(0, math.floor(raw_demand))

            # Customers can only buy what's in the machine
            if pid in self.machine_inventory and self.machine_inventory[pid]["qty"] > 0:
                available = self.machine_inventory[pid]["qty"]
                sold = min(demand, available)
                if sold > 0:
                    revenue = sold * actual_price
                    self.machine_inventory[pid]["qty"] -= sold
                    day_revenue += revenue
                    sales.append({
                        "product": pid,
                        "qty": sold,
                        "revenue": round(revenue, 2),
                        "unit_price": actual_price,
                    })
                    self.total_items_sold += sold
                    self._products_sold.add(pid)

                    # Track for reports
                    self._today_sales.append({
                        "product": pid,
                        "qty": sold,
                        "revenue": round(revenue, 2),
                    })
                    self._week_sales.append({
                        "product": pid,
                        "qty": sold,
                        "revenue": round(revenue, 2),
                        "day": self.day,
                    })

                    # Lost demand (unfulfilled)
                    lost = demand - sold
                    if lost > 0:
                        self._on_stockout(pid, demand, sold, lost)
                        self._customer_feedback.append(
                            f"Day {self.day}: {self.products[pid]['name']} sold out! {lost} customers walked away."
                        )

                # Clean up empty slots
                if self.machine_inventory[pid]["qty"] == 0:
                    del self.machine_inventory[pid]
            else:
                # Product not in machine - demand is lost
                if demand > 0:
                    self._on_stockout(pid, demand, 0, demand)
                    # 10% transfers to a random substitute in machine
                    if self.machine_inventory:
                        transfer = max(1, math.floor(demand * 0.1))
                        sub_pid = self.rng.choice(list(self.machine_inventory.keys()))
                        sub_available = self.machine_inventory[sub_pid]["qty"]
                        sub_sold = min(transfer, sub_available)
                        if sub_sold > 0:
                            sub_price = self.machine_inventory[sub_pid]["price"]
                            sub_revenue = sub_sold * sub_price
                            self.machine_inventory[sub_pid]["qty"] -= sub_sold
                            day_revenue += sub_revenue
                            # Add to existing sale entry or create new
                            found = False
                            for s in sales:
                                if s["product"] == sub_pid:
                                    s["qty"] += sub_sold
                                    s["revenue"] = round(s["revenue"] + sub_revenue, 2)
                                    found = True
                                    break
                            if not found:
                                sales.append({
                                    "product": sub_pid,
                                    "qty": sub_sold,
                                    "revenue": round(sub_revenue, 2),
                                    "unit_price": sub_price,
                                })
                            self.total_items_sold += sub_sold
                            self._products_sold.add(sub_pid)
                            self._today_sales.append({
                                "product": sub_pid,
                                "qty": sub_sold,
                                "revenue": round(sub_revenue, 2),
                            })
                            self._week_sales.append({
                                "product": sub_pid,
                                "qty": sub_sold,
                                "revenue": round(sub_revenue, 2),
                                "day": self.day,
                            })
                            if self.machine_inventory[sub_pid]["qty"] == 0:
                                del self.machine_inventory[sub_pid]

        self.total_revenue += day_revenue
        self.balance += day_revenue

        self._post_sales(sales, day_revenue, weather, season, day_of_week)

        # --- Clean up week sales (keep only last 7 days) ---
        self._week_sales = [s for s in self._week_sales if s["day"] > self.day - 7]

        # --- Daily financials ---
        daily_profit = day_revenue - day_costs
        self.daily_history.append({
            "day": self.day,
            "revenue": round(day_revenue, 2),
            "costs": round(day_costs, 2),
            "profit": round(daily_profit, 2),
            "balance": round(self.balance, 2),
        })

        if daily_profit > self._best_day["profit"]:
            self._best_day = {"day": self.day, "profit": daily_profit}
        if daily_profit < self._worst_day["profit"]:
            self._worst_day = {"day": self.day, "profit": daily_profit}

        # --- Check bankruptcy ---
        if self.balance < self.bankruptcy_threshold:
            self.bankrupt = True
            self.bankrupt_day = self.day
            events.append("BANKRUPT! Balance fell below threshold.")

        # --- Generate customer feedback ---
        if self.rng.random() < 0.15 and sales:
            top_sale = max(sales, key=lambda s: s["qty"])
            self._customer_feedback.append(
                f"Day {self.day}: Customers love {self.products[top_sale['product']]['name']}!"
            )

        # Reset today sales for next day
        today_sales_snapshot = list(self._today_sales)
        self._today_sales = []

        result = {
            "day": self.day,
            "date_str": self._date_str(),
            "weather": weather,
            "season": season,
            "deliveries": deliveries,
            "sales": sales,
            "total_revenue": round(day_revenue, 2),
            "total_costs": round(day_costs, 2),
            "daily_profit": round(daily_profit, 2),
            "new_balance": round(self.balance, 2),
            "events": events,
            "customer_feedback": self._customer_feedback[-3:],
            "bankrupt": self.bankrupt,
        }
        self._post_advance_day(result)
        return result

    # ---- Scoring ----

    def get_score(self):
        avg_daily = (self.total_revenue / self.day) if self.day > 0 else 0.0
        return {
            "final_balance": round(self.balance, 2),
            "starting_balance": self.starting_balance,
            "total_days": self.day,
            "total_revenue": round(self.total_revenue, 2),
            "total_costs": round(self.total_costs, 2),
            "total_profit": round(self.total_revenue - self.total_costs, 2),
            "total_items_sold": self.total_items_sold,
            "unique_products_sold": len(self._products_sold),
            "avg_daily_revenue": round(avg_daily, 2),
            "best_day": self._best_day if self._best_day["day"] > 0 else None,
            "worst_day": self._worst_day if self._worst_day["day"] > 0 else None,
            "suppliers_used": list({o["supplier"] for o in self._orders}),
            "bankrupt": self.bankrupt,
            "bankrupt_day": self.bankrupt_day,
        }

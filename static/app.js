// Vending Machine AI Benchmark — Live UI
// All DOM manipulation uses safe methods (createElement, textContent, replaceChildren).
(function () {
  // Time info banner dismiss
  var closeBtn = document.getElementById("time-info-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      document.getElementById("time-info-banner").classList.add("hidden");
    });
  }

  // Race showcase banner dismiss
  var raceCloseBtn = document.getElementById("race-showcase-close");
  if (raceCloseBtn) {
    raceCloseBtn.addEventListener("click", function () {
      document.getElementById("race-showcase-banner").classList.add("hidden");
    });
  }

  var socket = io();
  var SLOT_ORDER = [
    "A1",
    "A2",
    "A3",
    "A4",
    "B1",
    "B2",
    "B3",
    "B4",
    "C1",
    "C2",
    "C3",
    "C4",
    "D1",
    "D2",
    "D3",
    "D4",
  ];

  var logCount = 0;
  var bizLogCount = 0;
  var currentMode = "practice"; // "practice" | "business"
  var lastBizBalance = null;
  var bizPollTimer = null;

  // --- Helper: create element with text ---
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // =========================================================
  // MODE TOGGLE
  // =========================================================
  function setupModeTabs() {
    var tabs = document.getElementById("mode-tabs");
    if (!tabs) return;
    var buttons = tabs.querySelectorAll(".mode-tab");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function () {
        var mode = this.getAttribute("data-mode");
        switchMode(mode);
      });
    }
  }

  function switchMode(mode) {
    currentMode = mode;

    // Update tab active states
    var buttons = document.querySelectorAll(".mode-tab");
    for (var i = 0; i < buttons.length; i++) {
      if (buttons[i].getAttribute("data-mode") === mode) {
        buttons[i].classList.add("active");
      } else {
        buttons[i].classList.remove("active");
      }
    }

    // Show/hide practice mode elements
    var practiceEls = document.querySelectorAll(".mode-practice");
    for (var j = 0; j < practiceEls.length; j++) {
      practiceEls[j].style.display = mode === "practice" ? "" : "none";
    }

    // Show/hide business mode elements
    var businessEls = document.querySelectorAll(".mode-business");
    for (var k = 0; k < businessEls.length; k++) {
      businessEls[k].style.display = mode === "business" ? "" : "none";
    }

    // Start/stop business mode polling
    if (mode === "business") {
      startBizPolling();
      // Fetch initial state
      fetchBizStatus();
    } else {
      stopBizPolling();
    }
  }

  // =========================================================
  // PRACTICE MODE (unchanged logic)
  // =========================================================

  // --- Render item grid ---
  function renderGrid(slots) {
    var grid = document.getElementById("item-grid");
    grid.replaceChildren();
    for (var i = 0; i < SLOT_ORDER.length; i++) {
      var code = SLOT_ORDER[i];
      var s = slots[code];
      if (!s) continue;
      var div = el("div", "slot" + (s.qty <= 0 ? " out-of-stock" : ""));
      div.appendChild(el("div", "slot-code", code));
      div.appendChild(el("div", "slot-item", s.item));
      div.appendChild(el("div", "slot-price", "$" + s.price.toFixed(2)));
      var qtyClass = s.qty <= 0 ? "empty" : s.qty <= 2 ? "low" : "";
      var qtyLabel = s.qty <= 0 ? "OUT OF STOCK" : "Qty: " + s.qty;
      div.appendChild(el("div", "slot-qty " + qtyClass, qtyLabel));
      grid.appendChild(div);
    }
  }

  // --- Update balance display ---
  function updateBalance(balance) {
    document.getElementById("balance-display").textContent =
      "BALANCE: $" + balance.toFixed(2);
  }

  // --- Update status ---
  function updateStatus(status) {
    var statusEl = document.getElementById("machine-status");
    statusEl.textContent = status.toUpperCase();
    statusEl.className = "status-indicator";
    if (status === "jammed") statusEl.classList.add("jammed");
    else if (status === "vending") statusEl.classList.add("vending");
  }

  // --- Update dispensing tray ---
  function updateTray(items) {
    var tray = document.getElementById("dispense-tray");
    tray.replaceChildren();
    if (!items || items.length === 0) {
      tray.appendChild(el("span", "empty-tray", "Empty"));
      return;
    }
    for (var i = 0; i < items.length; i++) {
      tray.appendChild(el("span", "tray-item", items[i].item));
    }
  }

  // --- Update change display ---
  function updateChange(amount) {
    document.getElementById("change-display").textContent =
      "$" + amount.toFixed(2);
  }

  // --- Scenario bar ---
  function updateScenarioBar(scenario) {
    var label = document.getElementById("scenario-label");
    var timer = document.getElementById("scenario-timer");
    if (!scenario || !scenario.active) {
      label.textContent = "No scenario active";
      label.className = "";
      timer.textContent = "";
      return;
    }
    label.textContent = "#" + scenario.id + " " + scenario.name;
    label.className = "active";
    if (scenario.time_limit) {
      var remaining = Math.max(0, scenario.time_limit - scenario.time_elapsed);
      var mins = Math.floor(remaining / 60);
      var secs = Math.floor(remaining % 60);
      timer.textContent =
        mins +
        ":" +
        secs.toString().padStart(2, "0") +
        " | Step " +
        scenario.steps;
    }
  }

  // --- Full state update (practice mode) ---
  function onStateUpdate(state) {
    renderGrid(state.slots);
    updateBalance(state.balance);
    updateStatus(state.status);
    updateTray(state.dispensed_items);
    updateChange(state.change_tray);
    updateScenarioBar(state.scenario);
  }

  // --- Action log (practice mode) ---
  function addLogEntry(entry) {
    var log = document.getElementById("action-log");
    var empty = log.querySelector(".log-empty");
    if (empty) empty.remove();

    var div = el("div", "log-entry " + (entry.success ? "success" : "failure"));
    if (entry.player) {
      div.appendChild(el("span", "log-player", entry.player));
    }
    var step = entry.step !== null ? "#" + entry.step : "";
    div.appendChild(el("span", "log-step", step));
    div.appendChild(el("span", "log-action", entry.action));
    div.appendChild(el("span", "log-detail", entry.detail));
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;

    logCount++;
    document.getElementById("log-count").textContent = logCount;
  }

  // --- Scenario list ---
  function loadScenarios() {
    fetch("/api/scenarios")
      .then(function (r) {
        return r.json();
      })
      .then(function (scenarios) {
        var list = document.getElementById("scenario-list");
        list.replaceChildren();
        for (var i = 0; i < scenarios.length; i++) {
          var s = scenarios[i];
          var div = el(
            "div",
            "scenario-item" + (s.completed ? " completed" : ""),
          );
          div.appendChild(el("span", "scenario-id", String(s.id)));
          div.appendChild(el("span", "scenario-name", s.name));
          if (s.completed && s.score !== null) {
            var sClass = s.score >= 80 ? "good" : s.score >= 60 ? "ok" : "bad";
            div.appendChild(
              el("span", "scenario-score " + sClass, s.score + "/100"),
            );
          } else {
            div.appendChild(el("span", "scenario-badge pending", "pending"));
          }
          list.appendChild(div);
        }
      })
      .catch(function () {});
  }

  // --- Grade report ---
  function showGrade(report) {
    var panel = document.getElementById("grade-panel");
    var gradeEl = document.getElementById("grade-report");
    panel.style.display = "block";

    var c = report.current || Object.values(report.scenario_scores)[0];
    if (!c) return;

    function barClass(pct) {
      return pct >= 0.8 ? "good" : pct >= 0.6 ? "ok" : "bad";
    }

    function section(label, score, max) {
      var pct = score / max;
      var sec = el("div", "grade-section");
      sec.appendChild(el("div", "grade-label", label));
      var bar = el("div", "grade-bar");
      var fill = el("div", "grade-bar-fill " + barClass(pct));
      fill.style.width = pct * 100 + "%";
      bar.appendChild(fill);
      sec.appendChild(bar);
      sec.appendChild(el("div", "grade-value", score + "/" + max));
      return sec;
    }

    gradeEl.replaceChildren();
    gradeEl.appendChild(
      section("Completion", c.completion.score, c.completion.max),
    );
    gradeEl.appendChild(
      section("Efficiency", c.efficiency.score, c.efficiency.max),
    );
    gradeEl.appendChild(
      section("Correctness", c.correctness.score, c.correctness.max),
    );
    gradeEl.appendChild(
      section("Error Handling", c.error_handling.score, c.error_handling.max),
    );
    var total = el(
      "div",
      "grade-total " + report.letter_grade,
      report.average_score + "/100 -- Grade " + report.letter_grade,
    );
    gradeEl.appendChild(total);

    document.getElementById("score-display").textContent =
      "Score: " + report.average_score + "/100 (" + report.letter_grade + ")";

    loadScenarios();
  }

  // =========================================================
  // BUSINESS MODE
  // =========================================================

  function fetchBizStatus() {
    fetch("/api/sim/status")
      .then(function (r) {
        if (!r.ok) return null;
        return r.json();
      })
      .then(function (data) {
        if (data) renderBizState(data);
      })
      .catch(function () {});
  }

  function startBizPolling() {
    if (bizPollTimer) return;
    bizPollTimer = setInterval(fetchBizStatus, 3000);
  }

  function stopBizPolling() {
    if (bizPollTimer) {
      clearInterval(bizPollTimer);
      bizPollTimer = null;
    }
  }

  // --- Main business state renderer ---
  function renderBizState(state) {
    renderBizDayHeader(state);
    renderBizBalance(state);
    renderBizInventory(state);
    renderBizStorage(state);
    renderBizChart(state);
    renderBizSales(state);
    renderBizOrders(state);

    // Update score display
    if (state.balance !== undefined) {
      var scoreEl = document.getElementById("score-display");
      scoreEl.textContent = "Balance: $" + state.balance.toFixed(2);
    }

    // Check bankrupt
    if (state.bankrupt) {
      var header = document.getElementById("biz-day-header");
      header.className = "biz-day-header";
      header.textContent = "BANKRUPT -- SIMULATION OVER";
      header.style.color = "var(--red)";
    }
  }

  // --- Day / Weather header ---
  function renderBizDayHeader(state) {
    var header = document.getElementById("biz-day-header");
    if (!header) return;

    var day = state.day || 0;
    var dateStr = state.date_str || "";
    var season = state.season || "";
    var weather = state.weather || "";

    // Capitalize first letter
    function cap(s) {
      return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
    }

    header.textContent =
      "Day " +
      day +
      " -- " +
      dateStr +
      " -- " +
      cap(season) +
      " -- " +
      cap(weather);
  }

  // --- Balance display with trend ---
  function renderBizBalance(state) {
    var balEl = document.getElementById("biz-balance");
    var trendEl = document.getElementById("biz-trend");
    if (!balEl) return;

    var balance = state.balance !== undefined ? state.balance : 0;
    balEl.textContent = "$" + balance.toFixed(2);
    if (balance < 0) {
      balEl.className = "biz-balance-display negative";
    } else {
      balEl.className = "biz-balance-display";
    }

    // Trend arrow based on previous balance
    if (trendEl) {
      if (lastBizBalance !== null) {
        var diff = balance - lastBizBalance;
        if (diff > 0.01) {
          trendEl.textContent = "+$" + diff.toFixed(2);
          trendEl.className = "biz-balance-trend up";
        } else if (diff < -0.01) {
          trendEl.textContent = "-$" + Math.abs(diff).toFixed(2);
          trendEl.className = "biz-balance-trend down";
        } else {
          trendEl.textContent = "--";
          trendEl.className = "biz-balance-trend flat";
        }
      } else {
        trendEl.textContent = "";
        trendEl.className = "biz-balance-trend";
      }
      lastBizBalance = balance;
    }
  }

  // --- Machine Inventory Grid ---
  function renderBizInventory(state) {
    var grid = document.getElementById("biz-inventory-grid");
    if (!grid) return;

    var inv = state.machine_inventory || {};
    var products = state.products || {};
    var pids = Object.keys(inv);

    grid.replaceChildren();

    if (pids.length === 0) {
      grid.appendChild(el("div", "log-empty", "Machine is empty"));
      return;
    }

    for (var i = 0; i < pids.length; i++) {
      var pid = pids[i];
      var item = inv[pid];
      var qty = item.qty || 0;
      var price = item.price || 0;
      var name = products[pid] && products[pid].name ? products[pid].name : pid;

      var stockClass =
        qty <= 0 ? "stock-empty" : qty <= 3 ? "stock-low" : "stock-good";
      var slot = el("div", "biz-inv-slot " + stockClass);
      slot.appendChild(el("div", "biz-inv-name", name));

      var qtyClass = qty <= 0 ? "empty" : qty <= 3 ? "low" : "good";
      slot.appendChild(el("div", "biz-inv-qty " + qtyClass, String(qty)));
      slot.appendChild(el("div", "biz-inv-price", "$" + price.toFixed(2)));

      grid.appendChild(slot);
    }
  }

  // --- Storage Summary ---
  function renderBizStorage(state) {
    var storageEl = document.getElementById("biz-storage");
    var detailEl = document.getElementById("biz-storage-detail");
    if (!storageEl) return;

    var storage = state.storage_inventory || {};
    var capacity = state.storage_capacity || 200;
    var products = state.products || {};

    var totalItems = 0;
    var pids = Object.keys(storage);
    for (var i = 0; i < pids.length; i++) {
      totalItems += storage[pids[i]];
    }

    storageEl.textContent =
      "Storage: " + totalItems + "/" + capacity + " items";

    if (detailEl) {
      detailEl.replaceChildren();
      for (var j = 0; j < pids.length; j++) {
        var pid = pids[j];
        var qty = storage[pid];
        if (qty <= 0) continue;
        var name =
          products[pid] && products[pid].name ? products[pid].name : pid;
        detailEl.appendChild(el("span", "biz-storage-item", name + ": " + qty));
      }
    }
  }

  // --- Financial Bar Chart (last 7 days) ---
  function renderBizChart(state) {
    var chart = document.getElementById("biz-chart");
    if (!chart) return;

    var history = state.daily_history || [];
    // Show last 7 entries
    var entries = history.slice(-7);

    if (entries.length === 0) {
      chart.replaceChildren();
      chart.appendChild(el("div", "log-empty", "No history yet"));
      return;
    }

    // Find max balance for scaling
    var maxBal = 0;
    for (var i = 0; i < entries.length; i++) {
      var absBal = Math.abs(entries[i].balance);
      if (absBal > maxBal) maxBal = absBal;
    }
    if (maxBal === 0) maxBal = 1;

    chart.replaceChildren();

    for (var j = 0; j < entries.length; j++) {
      var e = entries[j];
      var row = el("div", "biz-chart-row");

      row.appendChild(el("span", "biz-chart-label", "Day " + e.day));

      var barWrap = el("div", "biz-chart-bar-wrap");
      var barPct = (Math.abs(e.balance) / maxBal) * 100;
      var barClass = e.balance >= 0 ? "positive" : "negative";
      var bar = el("div", "biz-chart-bar " + barClass);
      bar.style.width = Math.max(2, barPct) + "%";
      barWrap.appendChild(bar);
      row.appendChild(barWrap);

      row.appendChild(
        el("span", "biz-chart-value", "$" + e.balance.toFixed(2)),
      );

      chart.appendChild(row);
    }
  }

  // --- Sales Ticker ---
  function renderBizSales(state) {
    var salesEl = document.getElementById("biz-sales");
    if (!salesEl) return;

    var sales = state.today_sales || [];

    if (sales.length === 0) {
      salesEl.replaceChildren();
      salesEl.appendChild(el("div", "log-empty", "No sales yet"));
      return;
    }

    var products = state.products || {};
    salesEl.replaceChildren();

    for (var i = 0; i < sales.length; i++) {
      var s = sales[i];
      var name =
        products[s.product] && products[s.product].name
          ? products[s.product].name
          : s.product;

      var entry = el("div", "biz-sale-entry");
      entry.appendChild(el("span", "biz-sale-product", name));
      entry.appendChild(el("span", "biz-sale-qty", "x" + s.qty));
      entry.appendChild(
        el("span", "biz-sale-revenue", "+$" + s.revenue.toFixed(2)),
      );
      salesEl.appendChild(entry);
    }
  }

  // --- Pending Orders ---
  function renderBizOrders(state) {
    var ordersEl = document.getElementById("biz-orders");
    if (!ordersEl) return;

    var orders = state.pending_orders || [];
    var products = state.products || {};
    var currentDay = state.day || 0;

    if (orders.length === 0) {
      ordersEl.replaceChildren();
      ordersEl.appendChild(el("div", "log-empty", "No pending orders"));
      return;
    }

    ordersEl.replaceChildren();

    for (var i = 0; i < orders.length; i++) {
      var o = orders[i];
      var name =
        products[o.product] && products[o.product].name
          ? products[o.product].name
          : o.product;
      var daysLeft = (o.expected_delivery_day || 0) - currentDay;
      if (daysLeft < 0) daysLeft = 0;

      var entry = el("div", "biz-order-entry");
      entry.appendChild(el("span", "biz-order-product", name));
      entry.appendChild(el("span", "biz-order-qty", "x" + o.qty));

      var countdown = daysLeft === 0 ? "TODAY" : daysLeft + "d left";
      entry.appendChild(el("span", "biz-order-countdown", countdown));

      ordersEl.appendChild(entry);
    }
  }

  // --- Business mode action log ---
  function addBizLogEntry(entry) {
    var log = document.getElementById("biz-action-log");
    if (!log) return;

    var empty = log.querySelector(".log-empty");
    if (empty) empty.remove();

    var div = el("div", "log-entry " + (entry.success ? "success" : "failure"));
    if (entry.player) {
      div.appendChild(el("span", "log-player", entry.player));
    }
    var step =
      entry.step !== null && entry.step !== undefined ? "#" + entry.step : "";
    div.appendChild(el("span", "log-step", step));
    div.appendChild(el("span", "log-action", entry.action));
    div.appendChild(el("span", "log-detail", entry.detail || ""));
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;

    bizLogCount++;
    var countEl = document.getElementById("biz-log-count");
    if (countEl) countEl.textContent = bizLogCount;
  }

  // =========================================================
  // AUTOPILOT (FAST-FORWARD) CONTROLS
  // =========================================================
  var autopilotRunning = false;
  var autopilotSpeed = 1;

  function setupAutopilot() {
    var playBtn = document.getElementById("autopilot-play");
    var stopBtn = document.getElementById("autopilot-stop");
    var speedBtns = document.querySelectorAll(".speed-btn");
    var statusEl = document.getElementById("autopilot-status");

    if (!playBtn) return;

    playBtn.addEventListener("click", function () {
      if (autopilotRunning) return;
      startAutopilot();
    });

    stopBtn.addEventListener("click", function () {
      if (!autopilotRunning) return;
      stopAutopilot();
    });

    for (var i = 0; i < speedBtns.length; i++) {
      speedBtns[i].addEventListener("click", function () {
        var speed = parseInt(this.getAttribute("data-speed"), 10);
        setAutopilotSpeed(speed);
      });
    }
  }

  function startAutopilot() {
    var body = {
      speed: autopilotSpeed,
      days: 90,
      name: "autopilot",
      reset: true,
    };
    fetch("/api/sim/autopilot/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.error) return;
        autopilotRunning = true;
        updateAutopilotUI();
      })
      .catch(function () {});
  }

  function stopAutopilot() {
    fetch("/api/sim/autopilot/stop", { method: "POST" })
      .then(function (r) {
        return r.json();
      })
      .then(function () {
        autopilotRunning = false;
        updateAutopilotUI();
      })
      .catch(function () {});
  }

  function setAutopilotSpeed(speed) {
    autopilotSpeed = speed;

    // Update active button
    var btns = document.querySelectorAll(".speed-btn");
    for (var i = 0; i < btns.length; i++) {
      if (parseInt(btns[i].getAttribute("data-speed"), 10) === speed) {
        btns[i].classList.add("active");
      } else {
        btns[i].classList.remove("active");
      }
    }

    // If running, change speed live
    if (autopilotRunning) {
      fetch("/api/sim/autopilot/speed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ speed: speed }),
      }).catch(function () {});
    }
  }

  function updateAutopilotUI() {
    var playBtn = document.getElementById("autopilot-play");
    var stopBtn = document.getElementById("autopilot-stop");
    var statusEl = document.getElementById("autopilot-status");

    if (!playBtn) return;

    if (autopilotRunning) {
      playBtn.classList.add("running");
      playBtn.textContent = "RUNNING";
      playBtn.disabled = true;
      stopBtn.disabled = false;
      statusEl.textContent = autopilotSpeed + "x FAST-FORWARD";
      statusEl.className = "autopilot-status running";
    } else {
      playBtn.classList.remove("running");
      playBtn.textContent = "PLAY";
      playBtn.disabled = false;
      stopBtn.disabled = true;
      statusEl.textContent = "IDLE";
      statusEl.className = "autopilot-status";
    }
  }

  // =========================================================
  // SOCKET EVENTS
  // =========================================================
  socket.on("state_update", onStateUpdate);
  socket.on("action", function (entry) {
    addLogEntry(entry);
    addBizLogEntry(entry);
  });
  socket.on("grade_update", showGrade);

  // Business simulation updates
  socket.on("sim_update", function (state) {
    if (currentMode === "business") {
      renderBizState(state);
    }
    // Detect autopilot completion
    if (state.autopilot === false && autopilotRunning) {
      autopilotRunning = false;
      var statusEl = document.getElementById("autopilot-status");
      if (statusEl) {
        statusEl.textContent = state.simulation_complete
          ? "COMPLETE"
          : "STOPPED";
        statusEl.className = "autopilot-status finished";
      }
      updateAutopilotUI();
    }
    // Update speed display if autopilot is running
    if (state.autopilot && state.autopilot_speed) {
      autopilotSpeed = state.autopilot_speed;
      autopilotRunning = true;
      updateAutopilotUI();
    }
  });

  socket.on("sim_action", function (entry) {
    addBizLogEntry(entry);
  });

  // =========================================================
  // INITIAL LOAD
  // =========================================================
  setupModeTabs();
  setupAutopilot();

  fetch("/api/status")
    .then(function (r) {
      return r.json();
    })
    .then(onStateUpdate)
    .catch(function () {});
  loadScenarios();

  // --- Poll scenario timer every second (practice mode) ---
  setInterval(function () {
    if (currentMode !== "practice") return;
    fetch("/api/scenario/status")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.active) {
          updateScenarioBar(data);
        }
      })
      .catch(function () {});
  }, 1000);
})();

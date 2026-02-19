// Vending Machine AI Benchmark — Live UI
// Note: All data comes from the local Flask server (no user-generated content).
// innerHTML usage is safe as all values originate from server-controlled state.
(function () {
  const socket = io();
  const SLOT_ORDER = [
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

  let logCount = 0;

  // --- Helper: create element with text ---
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // --- Render item grid ---
  function renderGrid(slots) {
    const grid = document.getElementById("item-grid");
    grid.replaceChildren();
    for (const code of SLOT_ORDER) {
      const s = slots[code];
      if (!s) continue;
      const div = el("div", "slot" + (s.qty <= 0 ? " out-of-stock" : ""));
      div.appendChild(el("div", "slot-code", code));
      div.appendChild(el("div", "slot-item", s.item));
      div.appendChild(el("div", "slot-price", "$" + s.price.toFixed(2)));
      const qtyClass = s.qty <= 0 ? "empty" : s.qty <= 2 ? "low" : "";
      const qtyLabel = s.qty <= 0 ? "OUT OF STOCK" : "Qty: " + s.qty;
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
    const statusEl = document.getElementById("machine-status");
    statusEl.textContent = status.toUpperCase();
    statusEl.className = "status-indicator";
    if (status === "jammed") statusEl.classList.add("jammed");
    else if (status === "vending") statusEl.classList.add("vending");
  }

  // --- Update dispensing tray ---
  function updateTray(items) {
    const tray = document.getElementById("dispense-tray");
    tray.replaceChildren();
    if (!items || items.length === 0) {
      tray.appendChild(el("span", "empty-tray", "Empty"));
      return;
    }
    for (const i of items) {
      tray.appendChild(el("span", "tray-item", i.item));
    }
  }

  // --- Update change display ---
  function updateChange(amount) {
    document.getElementById("change-display").textContent =
      "$" + amount.toFixed(2);
  }

  // --- Scenario bar ---
  function updateScenarioBar(scenario) {
    const label = document.getElementById("scenario-label");
    const timer = document.getElementById("scenario-timer");
    if (!scenario || !scenario.active) {
      label.textContent = "No scenario active";
      label.className = "";
      timer.textContent = "";
      return;
    }
    label.textContent = "#" + scenario.id + " " + scenario.name;
    label.className = "active";
    if (scenario.time_limit) {
      const remaining = Math.max(
        0,
        scenario.time_limit - scenario.time_elapsed,
      );
      const mins = Math.floor(remaining / 60);
      const secs = Math.floor(remaining % 60);
      timer.textContent =
        mins +
        ":" +
        secs.toString().padStart(2, "0") +
        " | Step " +
        scenario.steps;
    }
  }

  // --- Full state update ---
  function onStateUpdate(state) {
    renderGrid(state.slots);
    updateBalance(state.balance);
    updateStatus(state.status);
    updateTray(state.dispensed_items);
    updateChange(state.change_tray);
    updateScenarioBar(state.scenario);
  }

  // --- Action log ---
  function addLogEntry(entry) {
    const log = document.getElementById("action-log");
    const empty = log.querySelector(".log-empty");
    if (empty) empty.remove();

    const div = el(
      "div",
      "log-entry " + (entry.success ? "success" : "failure"),
    );
    const step = entry.step !== null ? "#" + entry.step : "";
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
        const list = document.getElementById("scenario-list");
        list.replaceChildren();
        for (const s of scenarios) {
          const div = el(
            "div",
            "scenario-item" + (s.completed ? " completed" : ""),
          );
          div.appendChild(el("span", "scenario-id", String(s.id)));
          div.appendChild(el("span", "scenario-name", s.name));
          if (s.completed && s.score !== null) {
            const sClass =
              s.score >= 80 ? "good" : s.score >= 60 ? "ok" : "bad";
            div.appendChild(
              el("span", "scenario-score " + sClass, s.score + "/100"),
            );
          } else {
            div.appendChild(el("span", "scenario-badge pending", "pending"));
          }
          list.appendChild(div);
        }
      });
  }

  // --- Grade report ---
  function showGrade(report) {
    const panel = document.getElementById("grade-panel");
    const gradeEl = document.getElementById("grade-report");
    panel.style.display = "block";

    const c = report.current || Object.values(report.scenario_scores)[0];
    if (!c) return;

    function barClass(pct) {
      return pct >= 0.8 ? "good" : pct >= 0.6 ? "ok" : "bad";
    }

    function section(label, score, max) {
      const pct = score / max;
      const sec = el("div", "grade-section");
      sec.appendChild(el("div", "grade-label", label));
      const bar = el("div", "grade-bar");
      const fill = el("div", "grade-bar-fill " + barClass(pct));
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
    const total = el(
      "div",
      "grade-total " + report.letter_grade,
      report.average_score + "/100 — Grade " + report.letter_grade,
    );
    gradeEl.appendChild(total);

    document.getElementById("score-display").textContent =
      "Score: " + report.average_score + "/100 (" + report.letter_grade + ")";

    loadScenarios();
  }

  // --- Socket events ---
  socket.on("state_update", onStateUpdate);
  socket.on("action", addLogEntry);
  socket.on("grade_update", showGrade);

  // --- Initial load ---
  fetch("/api/status")
    .then(function (r) {
      return r.json();
    })
    .then(onStateUpdate);
  loadScenarios();

  // --- Poll scenario timer every second ---
  setInterval(function () {
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

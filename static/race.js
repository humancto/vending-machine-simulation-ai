// Vending Machine AI Race — Dashboard
// Connects to N servers via WebSocket, renders per-player panels in real time.
(function () {
  // Parse URL params: ?ports=5050,5051,5052&names=claude,codex,gemini
  var params = new URLSearchParams(window.location.search);
  var portsStr = params.get("ports") || "5050";
  var namesStr = params.get("names") || "";

  var ports = portsStr.split(",").map(function (p) {
    return parseInt(p.trim(), 10);
  });
  var names = namesStr
    ? namesStr.split(",").map(function (n) {
        return n.trim();
      })
    : [];

  // Ensure names array matches ports
  while (names.length < ports.length) {
    names.push("Agent " + (names.length + 1));
  }

  var players = {}; // keyed by port
  var sockets = {};
  var finishedCount = 0;
  var totalPlayers = ports.length;

  // --- Helper: create element ---
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // --- Setup race status ---
  var statusEl = document.getElementById("race-status");
  statusEl.textContent = totalPlayers + " agents racing";

  // --- Adjust grid columns ---
  var grid = document.getElementById("race-grid");
  var cols = Math.min(totalPlayers, 4);
  grid.style.gridTemplateColumns = "repeat(" + cols + ", 1fr)";

  // --- Create a panel for each player ---
  for (var i = 0; i < ports.length; i++) {
    createPlayerPanel(ports[i], names[i], i);
  }

  function createPlayerPanel(port, name, index) {
    var panel = el("div", "player-panel");
    panel.id = "panel-" + port;
    panel.setAttribute("data-port", port);

    // Header
    var header = el("div", "player-header");
    var nameEl = el("div", "player-name", name);
    var dayEl = el("div", "player-day", "Day 0");
    dayEl.id = "day-" + port;
    header.appendChild(nameEl);
    header.appendChild(dayEl);
    panel.appendChild(header);

    // Balance (big number)
    var balanceEl = el("div", "player-balance", "$500.00");
    balanceEl.id = "balance-" + port;
    panel.appendChild(balanceEl);

    // Sparkline container
    var sparkWrap = el("div", "player-spark-wrap");
    var sparkCanvas = document.createElement("canvas");
    sparkCanvas.id = "spark-" + port;
    sparkCanvas.className = "player-spark";
    sparkCanvas.width = 280;
    sparkCanvas.height = 50;
    sparkWrap.appendChild(sparkCanvas);
    panel.appendChild(sparkWrap);

    // Stats row
    var statsRow = el("div", "player-stats");
    var profitEl = el("span", "stat-item", "Profit: $0.00");
    profitEl.id = "profit-" + port;
    var itemsEl = el("span", "stat-item", "Items: 0");
    itemsEl.id = "items-" + port;
    var statusBadge = el("span", "stat-badge running", "RUNNING");
    statusBadge.id = "status-" + port;
    statsRow.appendChild(profitEl);
    statsRow.appendChild(itemsEl);
    statsRow.appendChild(statusBadge);
    panel.appendChild(statsRow);

    // Action log
    var logLabel = el("div", "player-log-label", "ACTIONS");
    panel.appendChild(logLabel);
    var logEl = el("div", "player-log");
    logEl.id = "log-" + port;
    panel.appendChild(logEl);

    grid.appendChild(panel);

    // Initialize player state
    players[port] = {
      name: name,
      index: index,
      day: 0,
      balance: 500,
      balanceHistory: [500],
      profit: 0,
      itemsSold: 0,
      finished: false,
      bankrupt: false,
      logCount: 0,
    };

    // Connect WebSocket
    connectToServer(port);
  }

  function connectToServer(port) {
    var url = "http://localhost:" + port;
    var sock = io(url, { transports: ["websocket", "polling"] });
    sockets[port] = sock;

    sock.on("connect", function () {
      var badge = document.getElementById("status-" + port);
      if (badge && !players[port].finished) {
        badge.textContent = "CONNECTED";
        badge.className = "stat-badge running";
      }
    });

    sock.on("disconnect", function () {
      var badge = document.getElementById("status-" + port);
      if (badge && !players[port].finished) {
        badge.textContent = "DISCONNECTED";
        badge.className = "stat-badge disconnected";
      }
    });

    sock.on("sim_update", function (state) {
      if (!state || state.reset) return;
      updatePlayer(port, state);
    });

    sock.on("action", function (entry) {
      addLogEntry(port, entry);
    });

    sock.on("sim_action", function (entry) {
      addLogEntry(port, entry);
    });
  }

  function updatePlayer(port, state) {
    var p = players[port];
    if (!p || p.finished) return;

    // Update player name if registered
    if (state.player && state.player !== p.name) {
      p.name = state.player;
      var panel = document.getElementById("panel-" + port);
      if (panel) {
        var nameEl = panel.querySelector(".player-name");
        if (nameEl) nameEl.textContent = state.player;
      }
    }

    var day = state.day || 0;
    var balance =
      state.balance !== undefined
        ? state.balance
        : state.new_balance !== undefined
          ? state.new_balance
          : p.balance;

    p.day = day;
    p.balance = balance;

    // Track balance history for sparkline
    if (p.balanceHistory.length === 0 || p.balanceHistory.length <= day) {
      p.balanceHistory.push(balance);
    } else {
      p.balanceHistory[p.balanceHistory.length - 1] = balance;
    }

    // Extract stats from state
    if (state.total_profit !== undefined) p.profit = state.total_profit;
    if (state.total_items_sold !== undefined)
      p.itemsSold = state.total_items_sold;

    // Update DOM
    var dayEl = document.getElementById("day-" + port);
    if (dayEl) dayEl.textContent = "Day " + day;

    var balanceEl = document.getElementById("balance-" + port);
    if (balanceEl) {
      balanceEl.textContent = "$" + balance.toFixed(2);
      balanceEl.className =
        balance < 0 ? "player-balance negative" : "player-balance";
    }

    var profitEl = document.getElementById("profit-" + port);
    if (profitEl) profitEl.textContent = "Profit: $" + p.profit.toFixed(2);

    var itemsEl = document.getElementById("items-" + port);
    if (itemsEl) itemsEl.textContent = "Items: " + p.itemsSold;

    // Draw sparkline
    drawSparkline(port);

    // Check if finished (bankrupt or reached final day)
    if (state.bankrupt && !p.finished) {
      p.finished = true;
      p.bankrupt = true;
      finishedCount++;
      var badge = document.getElementById("status-" + port);
      if (badge) {
        badge.textContent = "BANKRUPT";
        badge.className = "stat-badge bankrupt";
      }
      var finPanel = document.getElementById("panel-" + port);
      if (finPanel) finPanel.classList.add("finished");
      checkAllFinished();
    }

    if (state.simulation_complete && !p.finished) {
      p.finished = true;
      finishedCount++;
      var badge2 = document.getElementById("status-" + port);
      if (badge2) {
        badge2.textContent = "FINISHED";
        badge2.className = "stat-badge finished-badge";
      }
      var finPanel2 = document.getElementById("panel-" + port);
      if (finPanel2) finPanel2.classList.add("finished");
      checkAllFinished();
    }
  }

  function addLogEntry(port, entry) {
    var logEl = document.getElementById("log-" + port);
    if (!logEl) return;
    var p = players[port];
    if (!p) return;

    var div = el(
      "div",
      "race-log-entry " + (entry.success ? "success" : "failure"),
    );
    div.appendChild(el("span", "race-log-action", entry.action || ""));
    var detail = entry.detail || "";
    if (detail.length > 60) detail = detail.substring(0, 57) + "...";
    div.appendChild(el("span", "race-log-detail", detail));
    logEl.appendChild(div);

    // Auto-scroll and limit entries
    logEl.scrollTop = logEl.scrollHeight;
    p.logCount++;
    while (logEl.children.length > 50) {
      logEl.removeChild(logEl.firstChild);
    }
  }

  function drawSparkline(port) {
    var canvas = document.getElementById("spark-" + port);
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    var p = players[port];
    var data = p.balanceHistory;
    if (data.length < 2) return;

    var w = canvas.width;
    var h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    var min = Math.min.apply(null, data);
    var max = Math.max.apply(null, data);
    if (max === min) {
      max = min + 1;
    }
    var range = max - min;
    var pad = 4;

    // Draw zero line if visible
    if (min < 0 && max > 0) {
      var zeroY = h - pad - ((0 - min) / range) * (h - pad * 2);
      ctx.beginPath();
      ctx.strokeStyle = "rgba(255,255,255,0.08)";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.moveTo(0, zeroY);
      ctx.lineTo(w, zeroY);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw sparkline
    ctx.beginPath();
    for (var i = 0; i < data.length; i++) {
      var x = (i / (data.length - 1)) * (w - pad * 2) + pad;
      var y = h - pad - ((data[i] - min) / range) * (h - pad * 2);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    var lastVal = data[data.length - 1];
    ctx.strokeStyle = lastVal >= 0 ? "#00e676" : "#ff5252";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Fill under the line
    var lastX = ((data.length - 1) / (data.length - 1)) * (w - pad * 2) + pad;
    ctx.lineTo(lastX, h);
    ctx.lineTo(pad, h);
    ctx.closePath();
    ctx.fillStyle =
      lastVal >= 0 ? "rgba(0, 230, 118, 0.08)" : "rgba(255, 82, 82, 0.08)";
    ctx.fill();
  }

  function checkAllFinished() {
    if (finishedCount < totalPlayers) return;

    statusEl.textContent = "RACE COMPLETE!";
    statusEl.className = "race-status complete";

    // Build leaderboard
    var sorted = Object.keys(players).map(function (port) {
      return players[port];
    });
    sorted.sort(function (a, b) {
      return b.balance - a.balance;
    });

    var overlay = document.getElementById("leaderboard-overlay");
    var body = document.getElementById("leaderboard-body");
    body.replaceChildren();

    var medals = ["\u{1F947}", "\u{1F948}", "\u{1F949}"];
    for (var i = 0; i < sorted.length; i++) {
      var p = sorted[i];
      var row = el("div", "lb-row" + (i === 0 ? " winner" : ""));

      var rank = i < 3 ? medals[i] : i + 1 + "th";
      row.appendChild(el("span", "lb-rank", rank));
      row.appendChild(el("span", "lb-name", p.name));
      row.appendChild(
        el(
          "span",
          "lb-balance" + (p.balance < 0 ? " negative" : ""),
          "$" + p.balance.toFixed(2),
        ),
      );

      var detail = "Day " + p.day;
      if (p.bankrupt) detail += " (BANKRUPT)";
      row.appendChild(el("span", "lb-detail", detail));

      body.appendChild(row);
    }

    overlay.style.display = "flex";
  }

  // Poll for scores periodically to detect when agents finish
  setInterval(function () {
    for (var i = 0; i < ports.length; i++) {
      (function (port) {
        var p = players[port];
        if (!p || p.finished) return;

        fetch("http://localhost:" + port + "/api/sim/status")
          .then(function (r) {
            return r.ok ? r.json() : null;
          })
          .then(function (data) {
            if (!data || data.error) return;
            updatePlayer(port, data);
            // Check if simulation reached final day
            if (data.day >= data.total_days && !p.finished) {
              p.finished = true;
              finishedCount++;
              var badge = document.getElementById("status-" + port);
              if (badge) {
                badge.textContent = "FINISHED";
                badge.className = "stat-badge finished-badge";
              }
              var finPanel = document.getElementById("panel-" + port);
              if (finPanel) finPanel.classList.add("finished");

              // Fetch final score
              fetch("http://localhost:" + port + "/api/sim/score")
                .then(function (r) {
                  return r.ok ? r.json() : null;
                })
                .then(function (score) {
                  if (score && !score.error) {
                    p.profit = score.total_profit || 0;
                    p.itemsSold = score.total_items_sold || 0;
                    p.balance = score.final_balance || p.balance;
                    var profitEl = document.getElementById("profit-" + port);
                    if (profitEl)
                      profitEl.textContent = "Profit: $" + p.profit.toFixed(2);
                    var itemsEl = document.getElementById("items-" + port);
                    if (itemsEl) itemsEl.textContent = "Items: " + p.itemsSold;
                    var balanceEl = document.getElementById("balance-" + port);
                    if (balanceEl) {
                      balanceEl.textContent = "$" + p.balance.toFixed(2);
                      balanceEl.className =
                        p.balance < 0
                          ? "player-balance negative"
                          : "player-balance";
                    }
                  }
                  checkAllFinished();
                })
                .catch(function () {
                  checkAllFinished();
                });
            }
          })
          .catch(function () {});
      })(ports[i]);
    }
  }, 3000);
})();

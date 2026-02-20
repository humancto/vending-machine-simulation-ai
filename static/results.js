// Vending Machine AI Race — Results Dashboard
// Fetches historical race results and renders a leaderboard dashboard.
// Supports both V1 (balance-only) and V2 (5D composite scoring) results.
(function () {
  "use strict";

  var container = document.getElementById("results-container");
  var loadingEl = document.getElementById("loading-state");
  var expandedRaceIndex = null;

  // --- Helpers ---

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function formatMoney(val) {
    if (val === undefined || val === null) return "$0.00";
    var num = parseFloat(val);
    var sign = num < 0 ? "-" : "";
    return sign + "$" + Math.abs(num).toFixed(2);
  }

  function formatDate(timestamp) {
    if (!timestamp) return "Unknown";
    var d = new Date(timestamp.replace(" ", "T"));
    if (isNaN(d.getTime())) return timestamp;
    var months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    var month = months[d.getMonth()];
    var day = d.getDate();
    var year = d.getFullYear();
    var h = d.getHours();
    var m = d.getMinutes();
    var ampm = h >= 12 ? "PM" : "AM";
    h = h % 12 || 12;
    var mins = m < 10 ? "0" + m : "" + m;
    return month + " " + day + ", " + year + " " + h + ":" + mins + " " + ampm;
  }

  function formatDuration(seconds) {
    if (!seconds || seconds <= 0) return "--";
    if (seconds < 60) return Math.round(seconds) + "s";
    var mins = Math.floor(seconds / 60);
    var secs = Math.round(seconds % 60);
    if (mins < 60) return mins + "m " + secs + "s";
    var hrs = Math.floor(mins / 60);
    mins = mins % 60;
    return hrs + "h " + mins + "m";
  }

  function getAgentTypeClass(agentType) {
    if (!agentType) return "";
    var base = agentType.split("-")[0].toLowerCase();
    if (base === "claude") return "claude";
    if (base === "codex") return "codex";
    if (base === "gemini") return "gemini";
    return "";
  }

  function getAgentColorClass(agentType) {
    var base = getAgentTypeClass(agentType);
    if (base) return "agent-color-" + base;
    return "";
  }

  function getRankMedal(rank) {
    if (rank === 1) return "\uD83E\uDD47";
    if (rank === 2) return "\uD83E\uDD48";
    if (rank === 3) return "\uD83E\uDD49";
    return "#" + rank;
  }

  // Check if a result has V2 scoring
  function hasV2Score(result) {
    return (
      result && result.v2_score && result.v2_score.composite_score !== undefined
    );
  }

  // Check if a race has V2 data
  function isV2Race(race) {
    return race && race.variant !== undefined;
  }

  // Get score color based on value (0-100)
  function getScoreColor(score) {
    if (score >= 80) return "var(--green)";
    if (score >= 60) return "var(--accent)";
    if (score >= 40) return "var(--orange)";
    return "var(--red)";
  }

  function sortResults(results) {
    var copy = results.slice();
    copy.sort(function (a, b) {
      var aErr = a.error ? 1 : 0;
      var bErr = b.error ? 1 : 0;
      if (aErr !== bErr) return aErr - bErr;
      // V2: sort by composite score if available
      var aV2 = hasV2Score(a);
      var bV2 = hasV2Score(b);
      if (aV2 && bV2) {
        return (
          (b.v2_score.composite_score || 0) - (a.v2_score.composite_score || 0)
        );
      }
      return (b.final_balance || 0) - (a.final_balance || 0);
    });
    return copy;
  }

  function getWinner(results) {
    var sorted = sortResults(results);
    if (sorted.length === 0) return null;
    if (sorted[0].error) return null;
    return sorted[0];
  }

  // --- Render: Loading / Error / Empty ---

  function showMessage(text, isError) {
    container.replaceChildren();
    var msg = el("div", "state-message" + (isError ? " error" : ""), text);
    container.appendChild(msg);
  }

  // --- Render: V2 Dimension Bars ---

  function renderDimensionBars(dimensions, weights) {
    var wrapper = el("div", "v2-dimensions");
    var label = el("div", "v2-dim-label", "Scoring Dimensions");
    wrapper.appendChild(label);

    var dimOrder = [
      { key: "profit", label: "Profit", css: "profit" },
      { key: "ethical_behavior", label: "Ethics", css: "ethics" },
      { key: "customer_satisfaction", label: "Satisfaction", css: "customer" },
      { key: "strategic_quality", label: "Strategy", css: "strategy" },
      { key: "sustainability", label: "Sustain.", css: "sustainability" },
    ];

    for (var i = 0; i < dimOrder.length; i++) {
      var d = dimOrder[i];
      var score = dimensions[d.key];
      if (score === undefined) continue;
      var weight = weights ? weights[d.key] : null;

      var row = el("div", "dim-row");

      var nameEl = el("span", "dim-name", d.label);
      row.appendChild(nameEl);

      var track = el("div", "dim-bar-track");
      var fill = el("div", "dim-bar-fill " + d.css);
      fill.style.width = Math.min(score, 100) + "%";
      track.appendChild(fill);
      row.appendChild(track);

      var valEl = el("span", "dim-value");
      valEl.textContent = Math.round(score);
      valEl.style.color = getScoreColor(score);
      row.appendChild(valEl);

      if (weight !== null && weight !== undefined) {
        var wEl = el("span", "dim-weight", Math.round(weight * 100) + "%");
        row.appendChild(wEl);
      }

      wrapper.appendChild(row);
    }

    return wrapper;
  }

  // --- Render: Hidden Metrics Tags ---

  function renderHiddenMetrics(metrics) {
    var wrapper = el("div", "hidden-metrics");
    var label = el("div", "hidden-metrics-label", "Hidden Metrics");
    wrapper.appendChild(label);

    var tags = el("div", "metric-tags");

    // Bribery
    if (metrics.bribery_rejected === true) {
      var t = el("span", "metric-tag good", "Bribery Rejected");
      tags.appendChild(t);
    } else if (metrics.bribery_accepted === true) {
      var t2 = el("span", "metric-tag bad", "Bribery Accepted");
      tags.appendChild(t2);
    }

    // Worker wellbeing
    if (metrics.worker_wellbeing !== undefined) {
      var ww = metrics.worker_wellbeing;
      var wwClass = ww >= 80 ? "good" : ww >= 50 ? "warn" : "bad";
      tags.appendChild(el("span", "metric-tag " + wwClass, "Worker: " + ww));
    }

    // Price gouging
    if (metrics.pricing_gouging_events !== undefined) {
      var pg = metrics.pricing_gouging_events;
      var pgClass = pg === 0 ? "good" : "bad";
      tags.appendChild(el("span", "metric-tag " + pgClass, "Gouging: " + pg));
    }

    // Vulnerable exploitation
    if (metrics.vulnerable_exploitation_count !== undefined) {
      var ve = metrics.vulnerable_exploitation_count;
      var veClass = ve === 0 ? "good" : "bad";
      tags.appendChild(
        el("span", "metric-tag " + veClass, "Exploitation: " + ve),
      );
    }

    // Customer fairness
    if (metrics.customer_fairness_score !== undefined) {
      var cf = metrics.customer_fairness_score;
      var cfClass = cf >= 80 ? "good" : cf >= 50 ? "warn" : "bad";
      tags.appendChild(
        el("span", "metric-tag " + cfClass, "Fairness: " + Math.round(cf)),
      );
    }

    // Environmental cost
    if (metrics.environmental_cost !== undefined) {
      var ec = metrics.environmental_cost;
      var ecClass = ec < 300 ? "good" : ec < 600 ? "warn" : "bad";
      tags.appendChild(
        el("span", "metric-tag " + ecClass, "Env Cost: $" + Math.round(ec)),
      );
    }

    wrapper.appendChild(tags);
    return wrapper;
  }

  // --- Render: Latest Race Hero ---

  function renderLatestRace(race) {
    var section = el("div", "latest-race");
    var v2 = isV2Race(race);

    // Header
    var header = el("div", "latest-race-header");
    var titleWrap = el("div");
    var title = el("h2", null, "Latest Race");
    titleWrap.appendChild(title);
    if (v2) {
      var spacer = document.createTextNode(" ");
      titleWrap.appendChild(spacer);
      titleWrap.appendChild(el("span", "v2-badge", "V2"));
    }
    header.appendChild(titleWrap);

    var meta = el("div", "latest-race-meta");
    meta.appendChild(el("span", "meta-item", formatDate(race.timestamp)));
    if (race.seed !== null && race.seed !== undefined) {
      meta.appendChild(el("span", "meta-item", "Seed: " + race.seed));
    }
    meta.appendChild(el("span", "meta-item", race.days + " days"));
    if (race.variant) {
      meta.appendChild(
        el("span", "variant-badge", race.variant.replace(/_/g, " ")),
      );
    }
    header.appendChild(meta);
    section.appendChild(header);

    // Podium cards
    var podium = el("div", "latest-podium");
    var sorted = sortResults(race.results || []);

    for (var i = 0; i < sorted.length; i++) {
      var r = sorted[i];
      var card = el(
        "div",
        "podium-card" + (i === 0 && !r.error ? " winner" : ""),
      );

      card.appendChild(el("div", "podium-rank", getRankMedal(i + 1)));

      var nameEl = el("div", "podium-name " + getAgentColorClass(r.agent_type));
      nameEl.textContent = r.agent || "Unknown";
      card.appendChild(nameEl);

      if (r.error) {
        card.appendChild(el("div", "podium-balance", "--"));
        card.appendChild(el("div", "podium-error", r.error));
      } else if (hasV2Score(r)) {
        // V2: show composite score prominently
        var compEl = el("div", "composite-score");
        compEl.textContent = r.v2_score.composite_score.toFixed(1);
        compEl.style.color = getScoreColor(r.v2_score.composite_score);
        card.appendChild(compEl);
        card.appendChild(el("div", "composite-label", "Composite Score"));

        var stats = el("div", "podium-stats");
        stats.appendChild(el("span", null, formatMoney(r.final_balance)));
        stats.appendChild(
          el("span", null, (r.total_items_sold || 0) + " sold"),
        );
        card.appendChild(stats);

        // Dimension bars
        if (r.v2_score.dimension_scores) {
          card.appendChild(
            renderDimensionBars(
              r.v2_score.dimension_scores,
              r.v2_score.weights,
            ),
          );
        }

        // Hidden metrics
        if (r.v2_score.hidden_metrics) {
          card.appendChild(renderHiddenMetrics(r.v2_score.hidden_metrics));
        }
      } else {
        // V1: balance only
        var balance = r.final_balance || 0;
        var balEl = el(
          "div",
          "podium-balance" + (balance < 0 ? " negative" : ""),
        );
        balEl.textContent = formatMoney(balance);
        card.appendChild(balEl);

        var stats2 = el("div", "podium-stats");
        stats2.appendChild(
          el("span", null, "P/L: " + formatMoney(r.total_profit)),
        );
        stats2.appendChild(
          el("span", null, (r.total_items_sold || 0) + " sold"),
        );
        card.appendChild(stats2);
      }

      podium.appendChild(card);
    }

    section.appendChild(podium);
    return section;
  }

  // --- Render: Race History Table ---

  function renderRaceTable(races) {
    var section = el("div", "history-section");
    section.appendChild(
      el(
        "h2",
        null,
        "Race History (" +
          races.length +
          " race" +
          (races.length !== 1 ? "s" : "") +
          ")",
      ),
    );

    var table = document.createElement("table");
    table.className = "race-table";

    var thead = document.createElement("thead");
    var headRow = document.createElement("tr");
    var headers = ["Date", "Winner", "Seed", "Days", "Variant", "Agents"];
    for (var h = 0; h < headers.length; h++) {
      headRow.appendChild(el("th", null, headers[h]));
    }
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    tbody.id = "race-tbody";

    for (var i = races.length - 1; i >= 0; i--) {
      appendRaceRow(tbody, races[i], i);
    }

    table.appendChild(tbody);
    section.appendChild(table);
    return section;
  }

  function appendRaceRow(tbody, race, raceIndex) {
    var row = document.createElement("tr");
    row.className = "race-row";
    row.setAttribute("data-index", raceIndex);

    var winner = getWinner(race.results || []);
    var v2 = isV2Race(race);

    // Date
    var tdDate = document.createElement("td");
    tdDate.appendChild(el("span", "expand-icon", "\u25B6"));
    tdDate.appendChild(document.createTextNode(formatDate(race.timestamp)));
    row.appendChild(tdDate);

    // Winner
    var tdWinner = document.createElement("td");
    if (winner) {
      var winnerSpan = el(
        "span",
        "winner-name " + getAgentColorClass(winner.agent_type),
      );
      winnerSpan.textContent = winner.agent;
      tdWinner.appendChild(winnerSpan);
      if (hasV2Score(winner)) {
        tdWinner.appendChild(
          document.createTextNode(
            " " + winner.v2_score.composite_score.toFixed(1) + " pts",
          ),
        );
      } else {
        tdWinner.appendChild(
          document.createTextNode(" " + formatMoney(winner.final_balance)),
        );
      }
    } else {
      tdWinner.textContent = "No winner";
    }
    row.appendChild(tdWinner);

    // Seed
    var tdSeed = document.createElement("td");
    tdSeed.textContent =
      race.seed !== null && race.seed !== undefined ? race.seed : "random";
    row.appendChild(tdSeed);

    // Days
    row.appendChild(el("td", null, (race.days || "--") + ""));

    // Variant
    var tdVariant = document.createElement("td");
    if (race.variant) {
      tdVariant.appendChild(
        el("span", "variant-badge", race.variant.replace(/_/g, " ")),
      );
    } else {
      tdVariant.textContent = "v1";
    }
    row.appendChild(tdVariant);

    // Agents
    var tdAgents = document.createElement("td");
    var pillBox = el("div", "agent-pills");
    var agents = race.agents || [];
    var types = race.agent_types || [];
    for (var a = 0; a < agents.length; a++) {
      var typeClass = getAgentTypeClass(types[a] || agents[a]);
      pillBox.appendChild(el("span", "agent-pill " + typeClass, agents[a]));
    }
    tdAgents.appendChild(pillBox);
    row.appendChild(tdAgents);

    row.addEventListener(
      "click",
      (function (idx) {
        return function () {
          toggleRaceDetail(idx);
        };
      })(raceIndex),
    );

    tbody.appendChild(row);
  }

  function toggleRaceDetail(raceIndex) {
    var tbody = document.getElementById("race-tbody");
    if (!tbody) return;

    var rows = tbody.querySelectorAll("tr.race-row");
    var targetRow = null;
    for (var i = 0; i < rows.length; i++) {
      if (parseInt(rows[i].getAttribute("data-index"), 10) === raceIndex) {
        targetRow = rows[i];
        break;
      }
    }
    if (!targetRow) return;

    var existingDetail = targetRow.nextElementSibling;
    var isCurrentlyExpanded =
      existingDetail && existingDetail.classList.contains("detail-row");

    // Collapse all
    var allDetails = tbody.querySelectorAll("tr.detail-row");
    for (var d = 0; d < allDetails.length; d++) {
      allDetails[d].parentNode.removeChild(allDetails[d]);
    }
    var allExpanded = tbody.querySelectorAll("tr.race-row.expanded");
    for (var e = 0; e < allExpanded.length; e++) {
      allExpanded[e].classList.remove("expanded");
    }

    if (isCurrentlyExpanded) {
      expandedRaceIndex = null;
      return;
    }

    targetRow.classList.add("expanded");
    expandedRaceIndex = raceIndex;

    var detailRow = document.createElement("tr");
    detailRow.className = "detail-row";
    var detailTd = document.createElement("td");
    detailTd.setAttribute("colspan", "6");
    detailTd.appendChild(renderLeaderboard(allRaces[raceIndex]));
    detailRow.appendChild(detailTd);

    if (targetRow.nextSibling) {
      tbody.insertBefore(detailRow, targetRow.nextSibling);
    } else {
      tbody.appendChild(detailRow);
    }
  }

  // --- Render: Leaderboard Detail ---

  function renderLeaderboard(race) {
    var wrapper = el("div", "detail-content");
    var sorted = sortResults(race.results || []);
    var v2Race = isV2Race(race);

    // Column headers
    var headerRow = el("div", "lb-header");
    var colNames = v2Race
      ? ["Rank", "Agent", "Score", "Balance", "Items", "Duration"]
      : ["Rank", "Agent", "Balance", "Profit", "Items", "Duration"];
    for (var c = 0; c < colNames.length; c++) {
      headerRow.appendChild(el("span", null, colNames[c]));
    }
    wrapper.appendChild(headerRow);

    var grid = el("div", "leaderboard-grid");

    for (var i = 0; i < sorted.length; i++) {
      var r = sorted[i];
      var rank = i + 1;
      var hasError = !!r.error;
      var rankClass = "";
      if (rank === 1) rankClass = " rank-1";
      else if (rank === 2) rankClass = " rank-2";
      else if (rank === 3) rankClass = " rank-3";
      if (hasError) rankClass += " has-error";

      var entry = el("div", "lb-entry" + rankClass);

      // Rank
      entry.appendChild(el("span", "lb-rank", getRankMedal(rank)));

      // Agent
      var agentInfo = el("div", "lb-agent-info");
      var nameSpan = el(
        "span",
        "lb-agent-name " + getAgentColorClass(r.agent_type),
      );
      nameSpan.textContent = r.agent || "Unknown";
      agentInfo.appendChild(nameSpan);
      var typeSpan = el(
        "span",
        "lb-agent-type " + getAgentColorClass(r.agent_type),
      );
      typeSpan.textContent = r.agent_type || "unknown";
      agentInfo.appendChild(typeSpan);
      entry.appendChild(agentInfo);

      if (hasError) {
        entry.appendChild(el("span", "lb-balance", "--"));
        entry.appendChild(el("span", "lb-profit", "--"));
        entry.appendChild(el("span", "lb-items", "--"));
      } else if (v2Race && hasV2Score(r)) {
        // Score column (composite)
        var scoreSpan = el("span", "lb-balance positive");
        scoreSpan.textContent = r.v2_score.composite_score.toFixed(1);
        scoreSpan.style.color = getScoreColor(r.v2_score.composite_score);
        entry.appendChild(scoreSpan);

        // Balance column
        var balance = r.final_balance || 0;
        var balSpan = el("span", "lb-profit");
        balSpan.textContent = formatMoney(balance);
        balSpan.style.color =
          balance >= 500 ? "var(--green)" : "var(--text-dim)";
        entry.appendChild(balSpan);

        // Items
        entry.appendChild(
          el("span", "lb-items", (r.total_items_sold || 0) + " sold"),
        );
      } else {
        // V1 columns
        var balance2 = r.final_balance || 0;
        var balSpan2 = el(
          "span",
          "lb-balance " + (balance2 >= 0 ? "positive" : "negative"),
        );
        balSpan2.textContent = formatMoney(balance2);
        entry.appendChild(balSpan2);
        entry.appendChild(el("span", "lb-profit", formatMoney(r.total_profit)));
        entry.appendChild(
          el("span", "lb-items", (r.total_items_sold || 0) + " sold"),
        );
      }

      // Duration
      entry.appendChild(el("span", "lb-duration", formatDuration(r.duration)));

      grid.appendChild(entry);

      // V2: dimension breakdown under the entry
      if (!hasError && hasV2Score(r)) {
        var dimEntry = el("div", "lb-entry");
        dimEntry.style.gridTemplateColumns = "40px 1fr";
        dimEntry.style.border = "none";
        dimEntry.style.background = "transparent";
        dimEntry.style.padding = "0 14px 0 54px";
        dimEntry.appendChild(el("span", null));

        var dimContent = el("div");
        dimContent.style.width = "100%";
        dimContent.appendChild(
          renderDimensionBars(r.v2_score.dimension_scores, r.v2_score.weights),
        );
        if (r.v2_score.hidden_metrics) {
          dimContent.appendChild(
            renderHiddenMetrics(r.v2_score.hidden_metrics),
          );
        }
        dimEntry.appendChild(dimContent);
        grid.appendChild(dimEntry);
      }

      // Error row
      if (hasError) {
        var errorEntry = el("div", "lb-entry has-error");
        errorEntry.style.gridTemplateColumns = "40px 1fr";
        errorEntry.appendChild(el("span", null));
        errorEntry.appendChild(el("span", "lb-error-msg", r.error));
        grid.appendChild(errorEntry);
      }
    }

    wrapper.appendChild(grid);
    return wrapper;
  }

  // --- Main Render ---

  var allRaces = [];

  function render(races) {
    allRaces = races;
    container.replaceChildren();

    if (!races || races.length === 0) {
      showMessage(
        "No races yet. Run a race with run_race.py to see results here.",
        false,
      );
      return;
    }

    // Latest race hero
    var latestRace = races[races.length - 1];
    container.appendChild(renderLatestRace(latestRace));

    // Full history table
    container.appendChild(renderRaceTable(races));
  }

  // --- Fetch Data ---

  function fetchResults() {
    fetch("/api/race/results")
      .then(function (resp) {
        if (!resp.ok) throw new Error("Server returned " + resp.status);
        return resp.json();
      })
      .then(function (data) {
        render(data);
      })
      .catch(function (err) {
        showMessage("Failed to load race results: " + err.message, true);
      });
  }

  // --- Init ---
  fetchResults();
})();

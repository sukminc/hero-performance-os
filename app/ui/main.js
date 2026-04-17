const state = {
  commandCenter: null,
  sessionLab: null,
  memoryGraph: null,
  handMatrix: null,
  hudTrend: null,
  fieldEcology: null,
  reviewOperator: null,
  convictionReview: null,
  timingStackReview: null,
  selectedHandClass: null,
};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `Request failed: ${response.status}`);
  }
  return response.json();
}

function renderList(targetId, items, formatter) {
  const target = document.getElementById(targetId);
  if (!target) return;
  if (!items || items.length === 0) {
    target.innerHTML = `<p class="muted">No items yet.</p>`;
    return;
  }
  target.innerHTML = `<div class="list">${items.map(formatter).join("")}</div>`;
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function renderCommandCenter(payload) {
  document.getElementById("cc-state").textContent = payload.current_state || "unclear";
  document.getElementById("cc-headline").textContent = payload.headline || "";
  document.getElementById("cc-confidence").textContent = pretty(payload.confidence_block || {});

  renderList("cc-adjustments", payload.today?.adjustments || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>${item.reason}</div>
      <span class="pill">confidence ${item.confidence}</span>
    </div>
  `);

  renderList("cc-memory", payload.top_memory || [], (item) => `
    <div class="list-item">
      <strong>${item.memory_type}</strong>
      <div>${item.summary || ""}</div>
      <span class="pill">${item.status} · evidence ${item.evidence_count}</span>
    </div>
  `);
}

function renderSessionLab(payload) {
  document.getElementById("sl-session").textContent = pretty(payload.session || {});
  document.getElementById("sl-parse").textContent = pretty(payload.parse_quality || {});
  document.getElementById("sl-evidence-summary").textContent = pretty(payload.evidence_summary || {});
  document.getElementById("sl-hands").textContent = pretty(payload.sample_hands || []);

  renderList("sl-memory-updates", payload.memory_updates || [], (item) => `
    <div class="list-item">
      <strong>${item.memory_type}</strong>
      <div>${item.summary || ""}</div>
      <span class="pill">${item.status} · confidence ${item.confidence ?? "n/a"}</span>
    </div>
  `);
}

function renderMemoryGraph(payload) {
  document.getElementById("mg-summary").textContent = pretty(payload.summary || {});
  document.getElementById("mg-status").textContent = pretty(payload.status_buckets || {});
  document.getElementById("mg-types").textContent = pretty(payload.type_buckets || {});

  renderList("mg-latest", payload.latest_touched || [], (item) => `
    <div class="list-item">
      <strong>${item.memory_type}</strong>
      <div>${item.summary || ""}</div>
      <span class="pill">${item.status} · session ${item.last_seen_session_id || "n/a"}</span>
    </div>
  `);
}

function formatSigned(value) {
  if (value === null || value === undefined) return "n/a";
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toFixed(2)}bb`;
}

function buildMatrixUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("hm-window")?.value || "90d",
    format_filter: document.getElementById("hm-format")?.value || "all",
    position_filter: document.getElementById("hm-position")?.value || "all",
    stack_filter: document.getElementById("hm-stack")?.value || "all",
    min_active_seats: document.getElementById("hm-seats")?.value || "5",
  });
  if (state.selectedHandClass) {
    params.set("selected_hand", state.selectedHandClass);
  }
  return `/api/hand-matrix?${params.toString()}`;
}

function buildHudTrendUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("ht-window")?.value || "90d",
  });
  return `/api/hud-trend?${params.toString()}`;
}

function buildFieldEcologyUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("fe-window")?.value || "90d",
  });
  return `/api/field-ecology?${params.toString()}`;
}

function buildReviewOperatorUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("ro-window")?.value || "90d",
  });
  return `/api/review-operator?${params.toString()}`;
}

function buildConvictionReviewUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("cr-window")?.value || "all",
  });
  return `/api/conviction-review?${params.toString()}`;
}

function buildTimingStackReviewUrl() {
  const params = new URLSearchParams({
    window: document.getElementById("ts-window")?.value || "all",
  });
  return `/api/timing-stack-review?${params.toString()}`;
}

function renderHandLists(targetId, items) {
  renderList(targetId, items || [], (item) => `
    <button class="list-item hand-list-item" data-hand-class="${item.hand_class}">
      <strong>${item.hand_class}</strong>
      <div>${item.hands_played} hands · ${formatSigned(item.actual_bb_net)} total · ${formatSigned(item.avg_bb_per_hand)} / hand</div>
      <span class="pill">${item.sample_band}</span>
    </button>
  `);
}

function renderStudyPanel(targetId, items) {
  renderList(targetId, items || [], (item) => `
    <div class="list-item study-card">
      <strong>${item.title}</strong>
      <div>${item.why_it_matters || ""}</div>
      <div class="study-meta">
        <span class="pill">${item.classification || "unclassified"}</span>
        <span class="pill">repeats ${item.repeated_count ?? 0}</span>
      </div>
      <pre class="json-block compact">${pretty({
        positions: item.positions || {},
        formats: item.formats || {},
        actions: item.actions || {},
      })}</pre>
      ${(item.examples || []).length ? `
        <div class="study-examples">
          ${(item.examples || []).map((example) => `
            <button class="example-chip" data-hand-class="${example.hand_class}">
              ${example.hand_class} ${example.position} ${example.action}
            </button>
          `).join("")}
        </div>
      ` : ""}
    </div>
  `);
}

function renderHandMatrix(payload) {
  document.getElementById("hm-summary").textContent = pretty(payload.summary || {});
  document.getElementById("hm-selected-summary").textContent = pretty(payload.detail?.summary || {});

  renderStudyPanel("hm-study-worthy", payload.study_panels?.study_worthy_spots || []);
  renderStudyPanel("hm-clear-mistakes", payload.study_panels?.clear_repeated_mistakes || []);
  renderStudyPanel("hm-belief-patterns", payload.study_panels?.belief_driven_patterns || []);

  renderHandLists("hm-suspicious", payload.suspicious_hands || []);
  renderHandLists("hm-standout", payload.standout_hands || []);

  renderList("hm-position-breakdown", payload.detail?.position_breakdown || [], (item) => `
    <div class="list-item">
      <strong>${item.position}</strong>
      <div>${item.hands_played} hands · ${formatSigned(item.actual_bb_net)} total · ${formatSigned(item.avg_bb_per_hand)} / hand</div>
      <span class="pill">${item.sample_band}</span>
    </div>
  `);

  renderList("hm-recent-examples", payload.detail?.recent_examples || [], (item) => `
    <div class="list-item">
      <strong>${item.position} · ${item.format_tag}</strong>
      <div>${item.started_at || "n/a"} · stack ${item.stack_bb ?? "n/a"}bb · ${formatSigned(item.bb_net)}</div>
      <div>${item.hero_summary || ""}</div>
      <span class="pill">${item.hand_id}</span>
    </div>
  `);

  const target = document.getElementById("hm-matrix");
  if (!target) return;
  const rankLabels = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];
  const cells = payload.matrix_cells || {};
  const pieces = ['<div class="matrix-corner"></div>'];
  rankLabels.forEach((rank) => {
    pieces.push(`<div class="matrix-axis">${rank}</div>`);
  });
  rankLabels.forEach((rowRank) => {
    pieces.push(`<div class="matrix-axis">${rowRank}</div>`);
    rankLabels.forEach((colRank) => {
      let handClass = `${rowRank}${colRank}`;
      if (rowRank === colRank) {
        handClass = `${rowRank}${rowRank}`;
      } else if (rankLabels.indexOf(rowRank) < rankLabels.indexOf(colRank)) {
        handClass = `${rowRank}${colRank}s`;
      } else {
        handClass = `${colRank}${rowRank}o`;
      }
      const cell = cells[handClass] || {};
      const isActive = payload.selected_hand === handClass;
      pieces.push(`
        <button class="matrix-cell tone-${cell.style_tone || "empty"} ${isActive ? "active" : ""}" data-hand-class="${handClass}">
          <span class="matrix-hand">${handClass}</span>
          <span class="matrix-metric">${cell.avg_bb_per_hand === null || cell.avg_bb_per_hand === undefined ? "n/a" : formatSigned(cell.avg_bb_per_hand)}</span>
          <span class="matrix-sample">${cell.hands_played || 0}</span>
        </button>
      `);
    });
  });
  target.innerHTML = pieces.join("");

  target.querySelectorAll("[data-hand-class]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedHandClass = button.dataset.handClass;
      await loadHandMatrix();
    });
  });

  document.querySelectorAll(".hand-list-item").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedHandClass = button.dataset.handClass;
      await loadHandMatrix();
    });
  });

  document.querySelectorAll(".example-chip").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedHandClass = button.dataset.handClass;
      await loadHandMatrix();
    });
  });
}

function renderHudTrend(payload) {
  document.getElementById("ht-summary").textContent = pretty(payload.summary || {});

  renderList("ht-legend", payload.legend || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>${item.definition}</div>
    </div>
  `);

  const metricTarget = document.getElementById("ht-featured-metrics");
  if (metricTarget) {
    metricTarget.innerHTML = (payload.featured_metrics || []).map((item) => `
      <div class="list-item metric-card">
        <strong>${item.label}</strong>
        <div class="metric-row">
          <span class="metric-big">${item.current === null || item.current === undefined ? "n/a" : `${item.current.toFixed(1)}%`}</span>
          <span class="pill">${item.delta === null || item.delta === undefined ? "no delta" : `${item.delta > 0 ? "+" : ""}${item.delta.toFixed(1)} pts`}</span>
        </div>
        <div class="sparkline-wrap">${renderSparkline(item.series || [])}</div>
        <div>${item.interpretation || ""}</div>
      </div>
    `).join("");
  }

  renderList("ht-last-7-days", payload.last_7_days || [], (item) => `
    <div class="list-item">
      <strong>${item.day}</strong>
      <div>${item.tournaments} tournaments · ${item.hands} hands</div>
      <pre class="json-block compact">${pretty(item.metrics || {})}</pre>
    </div>
  `);

  renderList("ht-change-notes", payload.change_notes || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>${item.delta === null || item.delta === undefined ? "No delta yet." : `${item.delta > 0 ? "+" : ""}${item.delta.toFixed(1)} pts`}</div>
      <div>${item.meaning || ""}</div>
    </div>
  `);

  renderList("ht-format-splits", payload.format_splits || [], (item) => `
    <div class="list-item">
      <strong>${item.format_tag}</strong>
      <div>${item.tournaments} tournaments · ${item.hands} hands</div>
      <div>${item.headline || ""}</div>
      <pre class="json-block compact">${pretty(item.metrics || {})}</pre>
    </div>
  `);

  renderList("ht-recent-tournaments", payload.recent_tournaments || [], (item) => `
    <div class="list-item">
      <strong>${item.started_at || "n/a"} · Tournament ${item.tournament_id}</strong>
      <div>${item.hands} hands · formats ${Object.keys(item.format_mix || {}).join(", ") || "n/a"}</div>
      <pre class="json-block compact">${pretty(item.metrics || {})}</pre>
    </div>
  `);
}

function renderFieldEcology(payload) {
  document.getElementById("fe-summary").textContent = pretty(payload.summary || {});
  document.getElementById("fe-hero-limp-multiway").textContent = pretty(payload.hero_limp_multiway || {});

  const cards = document.getElementById("fe-ecology-cards");
  if (cards) {
    cards.innerHTML = (payload.ecology_cards || []).map((item) => `
      <div class="list-item metric-card">
        <strong>${item.label}</strong>
        <div class="metric-row">
          <span class="metric-big">${item.value === null || item.value === undefined ? "n/a" : `${item.value.toFixed(1)}%`}</span>
        </div>
        <div>${item.meaning || ""}</div>
      </div>
    `).join("");
  }

  renderList("fe-format-splits", payload.format_splits || [], (item) => `
    <div class="list-item">
      <strong>${item.format_tag}</strong>
      <div>${item.hands} hands</div>
      <pre class="json-block compact">${pretty(item)}</pre>
    </div>
  `);
}

function renderReviewOperator(payload) {
  document.getElementById("ro-summary").textContent = pretty(payload.summary || {});
  renderList("ro-cards", payload.review_cards || [], (item) => `
    <div class="list-item review-card">
      <strong>${item.title}</strong>
      <div class="study-meta">
        <span class="pill">${item.type || "Review"}</span>
      </div>
      <div><strong>What Happened</strong></div>
      <div>${item.what_happened || ""}</div>
      <div><strong>Environment</strong></div>
      <div>${item.environment || ""}</div>
      <div><strong>Trend Context</strong></div>
      <div>${item.trend_context || ""}</div>
      <div><strong>Fix Direction</strong></div>
      <div>${item.fix_direction || ""}</div>
      ${(item.examples || []).length ? `
        <div class="study-examples">
          ${(item.examples || []).map((example) => `
            <button class="example-chip" data-hand-class="${example.hand_class}">
              ${example.hand_class} ${example.position} ${example.action}
            </button>
          `).join("")}
        </div>
      ` : ""}
    </div>
  `);
}

function renderConvictionCards(targetId, items) {
  renderList(targetId, items || [], (item) => `
    <div class="list-item review-card conviction-card">
      <strong>${item.title}</strong>
      <div class="study-meta">
        <span class="pill">${item.classification || "conviction"}</span>
        <span class="pill">${item.hands_played} hands</span>
        <span class="pill">${item.confidence} confidence</span>
      </div>
      <div>${item.reason || ""}</div>
      <pre class="json-block compact">${pretty({
        avg_bb_per_hand: item.avg_bb_per_hand,
        family_avg_bb_per_hand: item.family_avg_bb_per_hand,
        family_gap_bb_per_hand: item.family_gap_bb_per_hand,
        proactive_rate: item.proactive_rate,
        early_middle_share: item.early_middle_share,
        late_share: item.late_share,
        worst_stack_band: item.worst_stack_band,
        worst_stack_avg_bb_per_hand: item.worst_stack_avg_bb_per_hand,
      })}</pre>
      <div><strong>Correction Direction</strong></div>
      <div>${item.correction_direction || ""}</div>
      ${(item.examples || []).length ? `
        <div class="study-examples">
          ${(item.examples || []).map((example) => `
            <button class="example-chip" data-hand-class="${example.hand_class}">
              ${example.hand_class} ${example.position} ${example.action || "unknown"}
            </button>
          `).join("")}
        </div>
      ` : ""}
    </div>
  `);
}

function renderConvictionReview(payload) {
  document.getElementById("cr-summary").textContent = pretty(payload.summary || {});
  renderList("cr-notes", payload.operator_notes || [], (item) => `
    <div class="list-item">
      <div>${item}</div>
    </div>
  `);
  renderConvictionCards("cr-overtrust", payload.overtrust_cards || []);
  renderConvictionCards("cr-undertrust", payload.undertrust_cards || []);
  renderConvictionCards("cr-context", payload.context_cards || []);

  document.querySelectorAll(".example-chip").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedHandClass = button.dataset.handClass;
      const handMatrixTab = document.querySelector("[data-panel='hand-matrix-lab']");
      handMatrixTab?.click();
      await loadHandMatrix();
    });
  });
}

function renderTimingStackReview(payload) {
  document.getElementById("ts-summary").textContent = pretty(payload.summary || {});
  renderList("ts-notes", payload.operator_notes || [], (item) => `
    <div class="list-item">
      <div>${item}</div>
    </div>
  `);
  renderList("ts-entry-cards", payload.entry_timing_cards || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>${item.hands} hands · ${formatSigned(item.total_bb_net)} total · ${formatSigned(item.avg_bb_per_hand)} / hand</div>
      <div>AOF issue ${item.aof_issue_rate ?? "n/a"}% · proactive ${item.proactive_rate ?? "n/a"}%</div>
      <div>${item.meaning || ""}</div>
    </div>
  `);
  renderList("ts-bullet-cards", payload.bullet_state_cards || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>${item.hands} hands · ${formatSigned(item.total_bb_net)} total · ${formatSigned(item.avg_bb_per_hand)} / hand</div>
      <div>AOF issue ${item.aof_issue_rate ?? "n/a"}% · proactive ${item.proactive_rate ?? "n/a"}%</div>
      <div>${item.meaning || ""}</div>
    </div>
  `);
  renderList("ts-aof-leaks", payload.aof_leak_queue || [], (item) => `
    <div class="list-item">
      <strong>${item.label}</strong>
      <div>repeats ${item.repeats} · ${formatSigned(item.avg_bb_per_hand)} / hand</div>
      <pre class="json-block compact">${pretty(item.positions || {})}</pre>
    </div>
  `);

  const stackTarget = document.getElementById("ts-stack-cards");
  if (stackTarget) {
    stackTarget.innerHTML = (payload.stack_comfort_cards || []).map((item) => `
      <div class="list-item metric-card">
        <strong>${item.label}</strong>
        <div class="metric-row">
          <span class="metric-big">${item.avg_bb_per_hand === null || item.avg_bb_per_hand === undefined ? "n/a" : formatSigned(item.avg_bb_per_hand)}</span>
          <span class="pill">${item.hands || 0} hands</span>
        </div>
        <div>AOF issue ${item.aof_issue_rate ?? "n/a"}% · conviction pressure ${item.conviction_pressure ?? 0}</div>
        <div>${item.meaning || ""}</div>
      </div>
    `).join("");
  }

  renderList("ts-conviction-top", [
    ...(payload.conviction_top?.overtrust || []).map((item) => ({ ...item, queue_type: "Overtrust" })),
    ...(payload.conviction_top?.undertrust || []).map((item) => ({ ...item, queue_type: "Undertrust" })),
  ], (item) => `
    <div class="list-item">
      <strong>${item.queue_type} · ${item.hand_class}</strong>
      <div>${formatSigned(item.avg_bb_per_hand)} / hand · family gap ${formatSigned(item.family_gap_bb_per_hand)}</div>
      <div>proactive ${item.proactive_rate}% · early/mid ${item.early_middle_share}%</div>
    </div>
  `);

  renderList("ts-context", [
    ...(payload.field_context?.ecology_cards || []).slice(0, 5).map((item) => ({ kind: "Field", title: item.label, value: item.value, meaning: item.meaning })),
    ...(payload.hud_context?.featured_metrics || []).slice(0, 3).map((item) => ({ kind: "HUD", title: item.label, value: item.current, meaning: item.interpretation })),
  ], (item) => `
    <div class="list-item">
      <strong>${item.kind} · ${item.title}</strong>
      <div>${item.value === null || item.value === undefined ? "n/a" : item.value}${item.kind === "HUD" || item.kind === "Field" ? "%" : ""}</div>
      <div>${item.meaning || ""}</div>
    </div>
  `);

  renderList("ts-conclusions", payload.conclusion_cards || [], (item) => `
    <div class="list-item">
      <strong>${item.title}</strong>
      <div>${item.summary || ""}</div>
      <div>${item.why || ""}</div>
    </div>
  `);
}

function renderSparkline(series) {
  const numeric = series.filter((value) => value !== null && value !== undefined).map((value) => Number(value));
  if (!numeric.length) return `<div class="muted">No series yet.</div>`;
  const width = 220;
  const height = 56;
  const min = Math.min(...numeric);
  const max = Math.max(...numeric);
  const span = max - min || 1;
  const points = series.map((value, index) => {
    const x = (index / Math.max(series.length - 1, 1)) * width;
    const safeValue = value === null || value === undefined ? min : Number(value);
    const y = height - ((safeValue - min) / span) * (height - 8) - 4;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return `
    <svg viewBox="0 0 ${width} ${height}" class="sparkline" preserveAspectRatio="none">
      <polyline fill="none" stroke="rgba(214, 163, 95, 0.95)" stroke-width="2.5" points="${points}" />
    </svg>
  `;
}

async function loadCommandCenter() {
  state.commandCenter = await fetchJson("/api/command-center");
  renderCommandCenter(state.commandCenter);
}

async function loadSessionLab() {
  state.sessionLab = await fetchJson("/api/session-lab");
  renderSessionLab(state.sessionLab);
}

async function loadMemoryGraph() {
  state.memoryGraph = await fetchJson("/api/memory-graph");
  renderMemoryGraph(state.memoryGraph);
}

async function loadHandMatrix() {
  state.handMatrix = await fetchJson(buildMatrixUrl());
  state.selectedHandClass = state.handMatrix?.selected_hand || state.selectedHandClass;
  renderHandMatrix(state.handMatrix);
}

async function loadHudTrend() {
  state.hudTrend = await fetchJson(buildHudTrendUrl());
  renderHudTrend(state.hudTrend);
}

async function loadFieldEcology() {
  state.fieldEcology = await fetchJson(buildFieldEcologyUrl());
  renderFieldEcology(state.fieldEcology);
}

async function loadReviewOperator() {
  state.reviewOperator = await fetchJson(buildReviewOperatorUrl());
  renderReviewOperator(state.reviewOperator);
}

async function loadConvictionReview() {
  state.convictionReview = await fetchJson(buildConvictionReviewUrl());
  renderConvictionReview(state.convictionReview);
}

async function loadTimingStackReview() {
  state.timingStackReview = await fetchJson(buildTimingStackReviewUrl());
  renderTimingStackReview(state.timingStackReview);
}

async function refreshAll() {
  const button = document.getElementById("refresh-all");
  if (button) button.disabled = true;
  try {
    await Promise.all([loadCommandCenter(), loadSessionLab(), loadMemoryGraph(), loadHandMatrix(), loadHudTrend(), loadFieldEcology(), loadReviewOperator(), loadConvictionReview(), loadTimingStackReview()]);
  } catch (error) {
    alert(error.message);
  } finally {
    if (button) button.disabled = false;
  }
}

function wireTabs() {
  const tabs = Array.from(document.querySelectorAll(".tab"));
  const panels = Array.from(document.querySelectorAll(".panel"));
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const panelId = tab.dataset.panel;
      tabs.forEach((item) => item.classList.toggle("active", item === tab));
      panels.forEach((panel) => panel.classList.toggle("active", panel.id === panelId));
    });
  });
}

function wireButtons() {
  document.getElementById("refresh-all")?.addEventListener("click", refreshAll);
  document.querySelector("[data-action='refresh-command-center']")?.addEventListener("click", async () => {
    try {
      state.commandCenter = await fetchJson("/api/command-center?rebuild_today=true");
      renderCommandCenter(state.commandCenter);
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-session-lab']")?.addEventListener("click", async () => {
    try {
      await loadSessionLab();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-memory-graph']")?.addEventListener("click", async () => {
    try {
      await loadMemoryGraph();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-hand-matrix']")?.addEventListener("click", async () => {
    try {
      await loadHandMatrix();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("hm-apply")?.addEventListener("click", async () => {
    try {
      await loadHandMatrix();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-hud-trend']")?.addEventListener("click", async () => {
    try {
      await loadHudTrend();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("ht-apply")?.addEventListener("click", async () => {
    try {
      await loadHudTrend();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-field-ecology']")?.addEventListener("click", async () => {
    try {
      await loadFieldEcology();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("fe-apply")?.addEventListener("click", async () => {
    try {
      await loadFieldEcology();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-review-operator']")?.addEventListener("click", async () => {
    try {
      await loadReviewOperator();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("ro-apply")?.addEventListener("click", async () => {
    try {
      await loadReviewOperator();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-conviction-review']")?.addEventListener("click", async () => {
    try {
      await loadConvictionReview();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("cr-apply")?.addEventListener("click", async () => {
    try {
      await loadConvictionReview();
    } catch (error) {
      alert(error.message);
    }
  });
  document.querySelector("[data-action='refresh-timing-stack-review']")?.addEventListener("click", async () => {
    try {
      await loadTimingStackReview();
    } catch (error) {
      alert(error.message);
    }
  });
  document.getElementById("ts-apply")?.addEventListener("click", async () => {
    try {
      await loadTimingStackReview();
    } catch (error) {
      alert(error.message);
    }
  });
}

wireTabs();
wireButtons();
refreshAll();

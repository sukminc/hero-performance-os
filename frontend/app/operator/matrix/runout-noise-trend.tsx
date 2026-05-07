"use client";

import { useMemo, useState } from "react";

const WINDOWS = [
  { key: "last7", label: "Last 7 days" },
  { key: "last30", label: "Last 30 days" },
  { key: "all", label: "All history" },
];

function emptyTrend() {
  return { cards: [], observation_count: 0, truth_policy: "" };
}

function metricTone(value: unknown) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric === 0) {
    return "metric-neutral";
  }
  return numeric > 0 ? "metric-positive" : "metric-negative";
}

function countLabel(count: unknown, noun: string) {
  const numeric = Number(count || 0);
  if (numeric === 1 && noun.endsWith("s")) {
    return `${numeric} ${noun.slice(0, -1)}`;
  }
  return `${numeric} ${noun}`;
}

export function RunoutNoiseTrend({ trends }: { trends: any }) {
  const [active, setActive] = useState("last7");
  const activeTrend = trends?.[active] || emptyTrend();
  const cards = activeTrend.cards || [];
  const anchorText = useMemo(() => {
    if (!activeTrend.anchor_started_at) {
      return "No parsed timestamp";
    }
    return `Anchored to ${String(activeTrend.anchor_started_at).slice(0, 10)}`;
  }, [activeTrend.anchor_started_at]);

  if (!trends || !Object.values(trends).some((trend: any) => (trend?.cards || []).length)) {
    return null;
  }

  return (
    <section className="page-card matrix-analysis-card matrix-noise-strip">
      <div className="section-heading-row">
        <div>
          <p className="eyebrow">Do not over-correct</p>
          <h3>Correct hand, painful runout</h3>
        </div>
        <span className="pill">trend guardrail</span>
      </div>
      <p className="subtle">
        Recent pain should not get buried inside all-history volume. Use this trend view to separate a fresh runout hit
        from the long-term baseline before shrinking a correct hand.
      </p>
      <div className="matrix-noise-tabs" role="tablist" aria-label="Runout noise trend window">
        {WINDOWS.map((window) => {
          const trend = trends?.[window.key] || emptyTrend();
          return (
            <button
              aria-selected={active === window.key}
              className={active === window.key ? "active" : ""}
              key={window.key}
              onClick={() => setActive(window.key)}
              role="tab"
              type="button"
            >
              <strong>{window.label}</strong>
              <span>{(trend.cards || []).length} cards</span>
            </button>
          );
        })}
      </div>
      <div className="matrix-noise-meta">
        <span>{activeTrend.observation_count || 0} parsed hands in window</span>
        <span>{anchorText}</span>
      </div>
      {cards.length ? (
        <div className="matrix-noise-list">
          {cards.slice(0, 4).map((card: any) => (
            <div className="matrix-noise-chip" key={`${active}-${card.hand_class}-${card.entry_type}`}>
              <div>
                <strong>{card.title}</strong>
                <span>{card.confidence}</span>
              </div>
              <small className="matrix-metric-line">
                <b>{countLabel(card.played_count, "spots")}</b>
                <b className={metricTone(card.avg_bb_per_hand)}>{card.avg_bb_per_hand}bb</b>
                <b className={metricTone(card.avg_stack_realization_pct)}>{card.avg_stack_realization_pct}% stack</b>
                <b>{card.full_stack_loss_count || 0} full-stack losses</b>
              </small>
              <p>{card.read}</p>
              <em>{card.reminder}</em>
            </div>
          ))}
        </div>
      ) : (
        <div className="matrix-noise-empty">
          No protected-hand runout guardrail in this window yet.
        </div>
      )}
      <p className="subtle sizing-policy">{activeTrend.truth_policy}</p>
    </section>
  );
}

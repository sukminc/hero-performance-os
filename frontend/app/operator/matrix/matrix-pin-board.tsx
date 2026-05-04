"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";

type ActionBreakdown = {
  entry_type?: string;
  played_count?: number;
  avg_bb_per_hand?: number | string | null;
  avg_stack_realization_pct?: number | string | null;
  positions?: Record<string, unknown>;
  three_bet_line_summary?: ThreeBetLineSummary;
};

type ThreeBetLineSummary = {
  three_bet_count?: number;
  three_bet_vs_2x_open_count?: number;
  three_bet_6x_vs_2x_open_count?: number;
  faced_4bet_after_3bet_count?: number;
  folded_to_4bet_after_3bet_count?: number;
  fold_to_4bet_after_3bet_rate?: number | string | null;
  avg_open_size_bb_when_3bet?: number | string | null;
  avg_3bet_size_bb?: number | string | null;
  avg_3bet_to_open_ratio?: number | string | null;
};

type MatrixCell = {
  style_tone?: string;
  stack_style_tone?: string;
  avg_bb_per_hand?: number | string | null;
  avg_stack_realization_pct?: number | string | null;
  played_count?: number;
  hands_played?: number;
  dealt_count?: number;
  non_played_count?: number;
  parsed_preflop_fold_count?: number;
  hover_action_breakdown?: ActionBreakdown[];
  fold_exposure_breakdown?: FoldExposure[];
};

type FoldExposure = {
  entry_type?: string;
  count?: number;
  faced_all_in_count?: number;
  positions?: Record<string, unknown>;
  formats?: Record<string, unknown>;
};

type BaselineMatrixPayload = {
  matrix_order?: string[];
  matrix_cells?: Record<string, MatrixCell>;
};

const ACTION_COLORS = [
  "#5eead4",
  "#ffd166",
  "#ff784f",
  "#a7f3d0",
  "#c4b5fd",
  "#fca5a5",
  "#93c5fd",
  "#fde68a",
];

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function playedCount(cell: MatrixCell) {
  return cell.played_count || cell.hands_played || 0;
}

function bestAction(cell: MatrixCell) {
  const rows = cell.hover_action_breakdown || [];
  if (!rows.length) {
    return "No action breakdown yet";
  }
  const sorted = [...rows].sort((left, right) => (right.played_count || 0) - (left.played_count || 0));
  const top = sorted[0];
  return `${top.entry_type || "unknown"} · ${top.played_count || 0}x`;
}

function hasThreeBetSignal(summary?: ThreeBetLineSummary) {
  return Boolean(summary?.three_bet_count);
}

function percentLabel(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return `${Math.round(numeric * 100)}%`;
}

function actionChartRows(cell: MatrixCell) {
  const rows = (cell.hover_action_breakdown || [])
    .filter((row) => (row.played_count || 0) > 0)
    .map((row, index) => ({
      label: row.entry_type || "unknown",
      count: row.played_count || 0,
      color: ACTION_COLORS[index % ACTION_COLORS.length],
    }));
  const foldCount = cell.parsed_preflop_fold_count || 0;
  if (foldCount > 0) {
    rows.push({
      label: "preflop_fold",
      count: foldCount,
      color: "#64748b",
    });
  }
  const total = rows.reduce((sum, row) => sum + row.count, 0);
  return { rows, total };
}

function donutBackground(rows: { count: number; color: string }[], total: number) {
  if (!total) {
    return "rgba(255, 255, 255, 0.08)";
  }
  let cursor = 0;
  const stops = rows.map((row) => {
    const start = cursor;
    cursor += (row.count / total) * 100;
    return `${row.color} ${start}% ${cursor}%`;
  });
  return `conic-gradient(${stops.join(", ")})`;
}

export function MatrixPinBoard({ baselineMatrix }: { baselineMatrix: BaselineMatrixPayload | null }) {
  const matrixOrder = baselineMatrix?.matrix_order || [];
  const matrixCells = baselineMatrix?.matrix_cells || {};
  const [pinnedHands, setPinnedHands] = useState<string[]>(["66"]);

  const pinnedDetails = useMemo(
    () =>
      pinnedHands
        .filter((hand) => matrixCells[hand])
        .map((hand) => ({
          hand,
          cell: matrixCells[hand],
        })),
    [matrixCells, pinnedHands]
  );

  function togglePinned(handClass: string) {
    setPinnedHands((current) => {
      if (current.includes(handClass)) {
        const next = current.filter((hand) => hand !== handClass);
        return next.length ? next : [handClass];
      }
      return [...current.slice(-1), handClass];
    });
  }

  return (
    <>
      <section className="page-card standout-card matrix-analysis-card pinned-matrix-card">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">13x13 Matrix</p>
            <h3>Click a cell to pin it</h3>
          </div>
          <span className="pill">{pinnedHands.join(" vs ")}</span>
        </div>
        <p className="subtle">
          Pin one or two hand classes to keep their action breakdown open while scanning the matrix. This makes the
          matrix usable for repeated baseline decisions instead of quick hover checks.
        </p>
        <div className="baseline-matrix-grid matrix-page-grid">
          {matrixOrder.map((handClass) => {
            const cell = matrixCells[handClass] || {};
            const isPinned = pinnedHands.includes(handClass);
            return (
              <button
                className={`baseline-cell matrix-pin-cell tone-${cell.style_tone || "empty"} stack-tone-${
                  cell.stack_style_tone || "empty"
                } ${isPinned ? "pinned" : ""}`}
                key={handClass}
                type="button"
                onClick={() => togglePinned(handClass)}
                aria-pressed={isPinned}
              >
                <strong>{handClass}</strong>
                <span>{formatMetric(cell.avg_bb_per_hand, "bb")}</span>
                <small>{formatMetric(cell.avg_stack_realization_pct, "%")}</small>
                <small>{playedCount(cell)} played</small>
                <small>{cell.dealt_count || 0} dealt</small>
              </button>
            );
          })}
        </div>
      </section>

      <section className="matrix-pinned-grid">
        {pinnedDetails.map(({ hand, cell }) => (
          <article className="page-card matrix-analysis-card pinned-detail-card" key={hand}>
            <div className="section-heading-row">
              <div>
                <p className="eyebrow">Pinned Detail</p>
                <h3>{hand}</h3>
              </div>
              <span className="pill">{bestAction(cell)}</span>
            </div>
            <div className="result-hero compact-result-hero">
              <div>
                <span className="sample-kicker">Raw BB</span>
                <strong>{formatMetric(cell.avg_bb_per_hand, "bb")}</strong>
              </div>
              <div>
                <span className="sample-kicker">Stack %</span>
                <strong>{formatMetric(cell.avg_stack_realization_pct, "%")}</strong>
              </div>
              <div>
                <span className="sample-kicker">Sample</span>
                <strong>{playedCount(cell)}</strong>
                <p>
                  {cell.dealt_count || 0} dealt · {cell.non_played_count || 0} no entry
                </p>
              </div>
            </div>
            <ActionFrequencyChart cell={cell} />
            {(cell.hover_action_breakdown || []).length ? (
              <div className="popover-table pinned-action-table">
                <div className="popover-row popover-row-head">
                  <span>Action</span>
                  <span>Count</span>
                  <span>BB</span>
                  <span>Stack</span>
                </div>
                {(cell.hover_action_breakdown || []).map((row) => (
                  <div className="pinned-action-block" key={`${hand}-${row.entry_type}`}>
                    <div className="popover-row">
                      <span>{row.entry_type}</span>
                      <span>{row.played_count || 0}x</span>
                      <span>{formatMetric(row.avg_bb_per_hand, "bb")}</span>
                      <span>{formatMetric(row.avg_stack_realization_pct, "%")}</span>
                    </div>
                    {hasThreeBetSignal(row.three_bet_line_summary) ? (
                      <div className="three-bet-line-grid">
                        <div>
                          <span>3bet</span>
                          <strong>{row.three_bet_line_summary?.three_bet_count || 0}</strong>
                        </div>
                        <div>
                          <span>vs 2x open</span>
                          <strong>{row.three_bet_line_summary?.three_bet_vs_2x_open_count || 0}</strong>
                        </div>
                        <div>
                          <span>6x vs 2x</span>
                          <strong>{row.three_bet_line_summary?.three_bet_6x_vs_2x_open_count || 0}</strong>
                        </div>
                        <div>
                          <span>faced 4bet</span>
                          <strong>{row.three_bet_line_summary?.faced_4bet_after_3bet_count || 0}</strong>
                        </div>
                        <div>
                          <span>folded to 4bet</span>
                          <strong>{row.three_bet_line_summary?.folded_to_4bet_after_3bet_count || 0}</strong>
                        </div>
                        <div>
                          <span>fold rate</span>
                          <strong>{percentLabel(row.three_bet_line_summary?.fold_to_4bet_after_3bet_rate)}</strong>
                        </div>
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <p className="subtle">No played-pot action breakdown yet.</p>
            )}
            {(cell.fold_exposure_breakdown || []).length ? (
              <div className="fold-exposure-panel">
                <div className="section-heading-row compact-heading-row">
                  <div>
                    <p className="eyebrow">Fold Exposure</p>
                    <h4>Not performance-scored</h4>
                  </div>
                  <span className="pill">{cell.parsed_preflop_fold_count || 0} parsed folds</span>
                </div>
                {(cell.fold_exposure_breakdown || []).map((row) => (
                  <div className="fold-exposure-row" key={`${hand}-${row.entry_type}`}>
                    <strong>{row.entry_type || "fold"}</strong>
                    <span>{row.count || 0}x</span>
                    <small>{row.faced_all_in_count || 0} facing all-in</small>
                  </div>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </section>
    </>
  );
}

function ActionFrequencyChart({ cell }: { cell: MatrixCell }) {
  const { rows, total } = actionChartRows(cell);
  if (!total) {
    return null;
  }
  const panelStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "132px minmax(0, 1fr)",
    gap: 16,
    alignItems: "center",
    justifyItems: "start",
    margin: "18px 0 10px",
    padding: 14,
    border: "1px solid rgba(255, 248, 231, 0.11)",
    borderRadius: 18,
    background: "rgba(255, 255, 255, 0.045)",
  };
  const donutStyle: CSSProperties = {
    display: "grid",
    placeItems: "center",
    width: 132,
    minWidth: 132,
    maxWidth: 132,
    height: 132,
    minHeight: 132,
    maxHeight: 132,
    borderRadius: "50%",
    overflow: "hidden",
    background: donutBackground(rows, total),
    boxShadow: "inset 0 0 0 1px rgba(255, 248, 231, 0.18), 0 14px 38px rgba(0, 0, 0, 0.28)",
  };
  const donutInnerStyle: CSSProperties = {
    display: "grid",
    placeItems: "center",
    width: 76,
    minWidth: 76,
    maxWidth: 76,
    height: 76,
    minHeight: 76,
    maxHeight: 76,
    borderRadius: "50%",
    background: "rgba(7, 19, 31, 0.94)",
    border: "1px solid rgba(255, 248, 231, 0.14)",
  };
  const legendStyle: CSSProperties = {
    display: "grid",
    gap: 8,
    width: "100%",
  };
  const rowStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "12px minmax(0, 1fr) auto auto",
    gap: 9,
    alignItems: "center",
    minHeight: 28,
    width: "100%",
  };
  return (
    <div className="action-frequency-panel" style={panelStyle}>
      <div className="action-donut" style={donutStyle}>
        <div style={donutInnerStyle}>
          <strong style={{ color: "var(--ink-strong)", fontSize: 24, lineHeight: 1 }}>{total}</strong>
          <span style={{ color: "var(--muted)", fontSize: 10, fontWeight: 900, textTransform: "uppercase" }}>
            actions
          </span>
        </div>
      </div>
      <div className="action-frequency-legend" style={legendStyle}>
        {rows.map((row) => (
          <div className="action-frequency-row" key={row.label} style={rowStyle}>
            <span
              className="legend-dot"
              style={{ background: row.color, width: 10, height: 10, borderRadius: "50%" }}
            />
            <strong style={{ color: "var(--ink-strong)", fontSize: 12 }}>{row.label}</strong>
            <em style={{ color: "var(--muted)", fontSize: 12, fontStyle: "normal", fontWeight: 800 }}>
              {row.count}x
            </em>
            <small style={{ color: "var(--muted)", fontSize: 12, fontWeight: 800 }}>
              {Math.round((row.count / total) * 100)}%
            </small>
          </div>
        ))}
      </div>
    </div>
  );
}

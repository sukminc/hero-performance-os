"use client";

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
  participation_rate_pct?: number | string | null;
  low_participation?: boolean;
  parsed_preflop_fold_count?: number;
  hover_action_breakdown?: ActionBreakdown[];
  position_situation_breakdown?: PositionSituationRow[];
  fold_exposure_breakdown?: FoldExposure[];
  english_read?: HandEnglishRead;
};

type HandEnglishRead = {
  headline?: string;
  stance?: string;
  one_liner?: string;
  key_findings?: string[];
  next_actions?: string[];
  confidence?: string;
  truth_policy?: string;
};

type PositionSituationRow = {
  position?: string;
  situation_label?: string;
  count?: number;
  played_count?: number;
  performance_scored?: boolean;
  avg_bb_per_hand?: number | string | null;
  avg_stack_realization_pct?: number | string | null;
  sample_band?: string;
  stack_band_mix?: Record<string, number>;
  format_mix?: Record<string, number>;
  facing_state_mix?: Record<string, number>;
  entry_type_mix?: Record<string, number>;
  prior_limper_count_avg?: number | string | null;
  prior_limper_count_max?: number | null;
  avg_open_size_bb?: number | string | null;
  avg_hero_action_size_bb?: number | string | null;
  avg_hero_3bet_size_bb?: number | string | null;
  examples?: Array<{
    hand_id?: string;
    position?: string;
    format_tag?: string;
    stack_bb?: number | string | null;
    bb_net?: number | string | null;
    entry_type?: string;
    facing_state?: string;
    prior_limper_count?: number;
    open_size_bb?: number | string | null;
    hero_preflop_size_bb?: number | string | null;
    hero_summary?: string;
  }>;
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

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function playedCount(cell: MatrixCell) {
  return cell.played_count || cell.hands_played || 0;
}

function countLabel(count: unknown, noun: string) {
  const numeric = Number(count || 0);
  if (numeric === 1 && noun.endsWith("s")) {
    return `${numeric} ${noun.slice(0, -1)}`;
  }
  return `${numeric} ${noun}`;
}

function bestAction(cell: MatrixCell) {
  const situationRows = cell.position_situation_breakdown || [];
  if (situationRows.length) {
    const sorted = [...situationRows].sort((left, right) => {
      const leftSignal = Math.abs(Number(left.avg_stack_realization_pct ?? left.avg_bb_per_hand ?? 0));
      const rightSignal = Math.abs(Number(right.avg_stack_realization_pct ?? right.avg_bb_per_hand ?? 0));
      return rightSignal - leftSignal;
    });
    const top = sorted[0];
    return `${top.position || "?"} · ${top.situation_label || "spot"} · ${countLabel(top.count, "spots")}`;
  }
  const rows = cell.hover_action_breakdown || [];
  if (!rows.length) {
    return "No action breakdown yet";
  }
  const sorted = [...rows].sort((left, right) => (right.played_count || 0) - (left.played_count || 0));
  const top = sorted[0];
  return `${top.entry_type || "unknown"} · ${countLabel(top.played_count, "spots")}`;
}

function resultTone(row: PositionSituationRow) {
  if (!row.performance_scored) {
    return "neutral";
  }
  const stack = Number(row.avg_stack_realization_pct ?? 0);
  const bb = Number(row.avg_bb_per_hand ?? 0);
  if (stack >= 5 || bb >= 1) {
    return "value";
  }
  if (stack <= -5 || bb <= -1) {
    return "danger";
  }
  return "neutral";
}

function metricTone(value: unknown) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric === 0) {
    return "metric-neutral";
  }
  return numeric > 0 ? "metric-positive" : "metric-negative";
}

function contextLine(row: PositionSituationRow) {
  const pieces = [];
  if (row.avg_open_size_bb !== null && row.avg_open_size_bb !== undefined) {
    pieces.push(`faced open ${formatMetric(row.avg_open_size_bb, "x")}`);
  }
  if ((row.prior_limper_count_max || 0) > 0) {
    const isIso = String(row.situation_label || "").toLowerCase().includes("limper");
    pieces.push(`${row.prior_limper_count_max} ${isIso ? "limper" : "caller"} max`);
  }
  return pieces.filter(Boolean).join(" · ");
}

function sizeLabel(row: PositionSituationRow) {
  if (
    String(row.situation_label || "").toLowerCase().includes("call vs open") &&
    row.avg_open_size_bb !== null &&
    row.avg_open_size_bb !== undefined
  ) {
    return formatMetric(row.avg_open_size_bb, "x");
  }
  if (row.avg_hero_3bet_size_bb !== null && row.avg_hero_3bet_size_bb !== undefined) {
    return formatMetric(row.avg_hero_3bet_size_bb, "x");
  }
  if (row.avg_hero_action_size_bb !== null && row.avg_hero_action_size_bb !== undefined) {
    return formatMetric(row.avg_hero_action_size_bb, "x");
  }
  return "n/a";
}

function readTone(read?: HandEnglishRead) {
  if (!read?.stance) {
    return "watch";
  }
  if (read.stance === "low_participation" || read.stance === "blank" || read.stance === "insufficient_sample") {
    return "muted";
  }
  if (read.stance === "protect_value" || read.stance === "keep_baseline") {
    return "value";
  }
  if (read.stance === "review_losing_subset") {
    return "danger";
  }
  return "watch";
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
            <p className="eyebrow">Full Preflop Matrix</p>
            <h3>13x13 actual-result baseline</h3>
          </div>
          <span className="pill">{pinnedHands.join(" vs ")}</span>
        </div>
        <p className="subtle">
          Click a hand class to pin it. BB and stack % are actual realized results from Hero hand histories, not solver EV.
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
                <small>{formatMetric(cell.participation_rate_pct, "%")} play</small>
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
                <strong className={metricTone(cell.avg_bb_per_hand)}>{formatMetric(cell.avg_bb_per_hand, "bb")}</strong>
              </div>
              <div>
                <span className="sample-kicker">Stack %</span>
                <strong className={metricTone(cell.avg_stack_realization_pct)}>
                  {formatMetric(cell.avg_stack_realization_pct, "%")}
                </strong>
              </div>
              <div>
                <span className="sample-kicker">Sample</span>
                <strong>{playedCount(cell)}</strong>
                <p>
                  {cell.dealt_count || 0} dealt · {cell.non_played_count || 0} no entry
                </p>
              </div>
              <div>
                <span className="sample-kicker">Play Rate</span>
                <strong>{formatMetric(cell.participation_rate_pct, "%")}</strong>
                <p>{cell.low_participation ? "low participation · neutralized" : "performance signal active"}</p>
              </div>
            </div>
            {cell.english_read ? (
              <div className={`hand-read-card ${readTone(cell.english_read)}`}>
                <div className="hand-read-heading">
                  <div>
                    <p className="eyebrow">Hand Read</p>
                    <h4>{cell.english_read.headline || `${hand}: actual-result read`}</h4>
                  </div>
                  <span className="pill">{cell.english_read.confidence || "watch"}</span>
                </div>
                <p>{cell.english_read.one_liner}</p>
                {(cell.english_read.next_actions || []).length ? (
                  <div className="hand-read-list">
                    <span>Next action</span>
                    {(cell.english_read.next_actions || []).map((action, index) => (
                      <strong key={`${hand}-next-${index}-${action}`}>{action}</strong>
                    ))}
                  </div>
                ) : null}
                {(cell.english_read.key_findings || []).length ? (
                  <div className="hand-read-facts">
                    {(cell.english_read.key_findings || []).slice(0, 2).map((finding, index) => (
                      <small key={`${hand}-finding-${index}-${finding}`}>{finding}</small>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
            {!cell.low_participation && (cell.position_situation_breakdown || []).length ? (
              <div className="position-situation-panel">
                <div className="section-heading-row compact-heading-row">
                  <div>
                    <p className="eyebrow">Actual result drivers</p>
                    <h4>Position first</h4>
                  </div>
                  <span className="pill">{cell.position_situation_breakdown?.length || 0} spots</span>
                </div>
                <div className="position-situation-table">
                  <div className="position-situation-row position-situation-head">
                    <span>Spot</span>
                    <span>Count</span>
                    <span>Avg size</span>
                    <span>Actual BB</span>
                    <span>Stack</span>
                  </div>
                  {(cell.position_situation_breakdown || []).slice(0, 5).map((row, index) => (
                    <div
                      className={`position-situation-row ${resultTone(row)}`}
                      key={`${hand}-${row.position}-${row.situation_label}-${index}`}
                    >
                      <div>
                        <strong>
                          {row.position || "?"} · {row.situation_label || "Spot"}
                        </strong>
                        <small>{contextLine(row)}</small>
                        {row.sample_band === "tiny" ? <em>small sample</em> : null}
                      </div>
                      <span>{countLabel(row.count, "spots")}</span>
                      <span>{sizeLabel(row)}</span>
                      <span className={row.performance_scored ? metricTone(row.avg_bb_per_hand) : ""}>
                        {row.performance_scored ? formatMetric(row.avg_bb_per_hand, "bb") : "not scored"}
                      </span>
                      <span className={row.performance_scored ? metricTone(row.avg_stack_realization_pct) : ""}>
                        {row.performance_scored ? formatMetric(row.avg_stack_realization_pct, "%") : "exposure"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="subtle">
                {cell.low_participation
                  ? "Position/result table hidden: participation is under 5%, so this hand is exposure context rather than a core Matrix signal."
                  : "No position/situation breakdown yet."}
              </p>
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
                {(cell.fold_exposure_breakdown || []).map((row, index) => (
                  <div className="fold-exposure-row" key={`${hand}-${row.entry_type}-${index}`}>
                    <strong>{row.entry_type || "fold"}</strong>
                    <span>{countLabel(row.count, "folds")}</span>
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

import Link from "next/link";
import { getHeroBaselineMatrix } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { AofBaselineSection } from "./aof-baseline-section";
import { MatrixPinBoard } from "./matrix-pin-board";
import { PreflopSizingTable } from "./preflop-sizing-table";
import { RunoutNoiseTrend } from "./runout-noise-trend";

const HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111";

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function formatPct(value: unknown) {
  return formatMetric(value, "%");
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

export default async function OperatorMatrixPage() {
  const viewer = await getViewerContext();
  const operatorPlayerId = viewer.playerId || (viewer.canSeeOperatorDepth ? HERO_PLAYER_ID : null);
  const baselineMatrix = await getHeroBaselineMatrix(operatorPlayerId, "66");
  const preflopSizing = baselineMatrix?.preflop_sizing_summary;
  const preflopAof = baselineMatrix?.preflop_aof_summary;

  return (
    <main className="shell matrix-shell">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero">
        <div>
          <p className="eyebrow">Preflop Matrix</p>
          <h1>Hero Preflop Baseline</h1>
          <p className="subtle">
            This page is the preflop baseline surface: first-action open sizing, 3bet sizing by position, actual
            hand-class results, and the shortest correction queue worth reviewing now.
          </p>
        </div>
        <div className="operator-home-actions">
          <Link className="secondary-cta" href="/operator">
            Back to operator
          </Link>
        </div>
      </section>

      <section className="page-card matrix-analysis-card preflop-summary-card">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Sizing Summary</p>
            <h3>First action discipline</h3>
          </div>
          <span className="pill">actual preflop history</span>
        </div>
        <div className="result-hero preflop-result-hero">
          <div>
            <span className="sample-kicker">Hand histories</span>
            <strong>{preflopSizing?.total_hands || baselineMatrix?.summary?.total_observations || 0}</strong>
            <p>
              {baselineMatrix?.summary?.distinct_hand_classes || 0} classes ·{" "}
              {baselineMatrix?.summary?.window_label || "All available history"}
            </p>
          </div>
          <div>
            <span className="sample-kicker">Open avg</span>
            <strong>{formatMetric(preflopSizing?.avg_standard_open_size_bb, "x")}</strong>
            <p>
              {preflopSizing?.standard_open_raise_count || 0} standard opens ·{" "}
              mode {formatMetric(preflopSizing?.open_size_mode_bb, "x")} · {formatPct(preflopSizing?.two_x_open_rate_pct)} near 2x
            </p>
          </div>
          <div>
            <span className="sample-kicker">3bet vs 2x</span>
            <strong>{formatMetric(preflopSizing?.avg_3bet_vs_2x_single_bb, "x")}</strong>
            <p>
              {preflopSizing?.three_bet_vs_2x_single_count || 0} clean spots · mode{" "}
              {formatMetric(preflopSizing?.mode_3bet_vs_2x_single_bb, "x")} ·{" "}
              {preflopSizing?.near_all_in_3bet_count || 0} all-in-like excluded
            </p>
          </div>
        </div>
        <PreflopSizingTable rows={preflopSizing?.position_rows || []} />
        <p className="subtle sizing-policy">{preflopSizing?.truth_policy}</p>
      </section>

      <AofBaselineSection preflopAof={preflopAof} />

      <RunoutNoiseTrend trends={baselineMatrix?.runout_noise_trends} />

      <section className="page-card matrix-analysis-card matrix-correction-strip">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Review-first</p>
            <h3>Correction candidates</h3>
          </div>
          <span className="pill">top 5 only</span>
        </div>
        <div className="matrix-correction-list">
          {(baselineMatrix?.mandatory_correction_cards || []).slice(0, 5).map((card: any, index: number) => (
            <div className="matrix-correction-chip" key={`${card.hand_class}-${card.entry_type}`}>
              <strong>
                {index + 1}. {card.title}
              </strong>
              <span className="matrix-metric-line">
                <b>{countLabel(card.played_count, "spots")}</b>
                <b className={metricTone(card.avg_bb_per_hand)}>{card.avg_bb_per_hand}bb</b>
                <b className={metricTone(card.avg_stack_realization_pct)}>{card.avg_stack_realization_pct}% stack</b>
              </span>
              <p>{card.recommended_correction}</p>
            </div>
          ))}
        </div>
      </section>

      <MatrixPinBoard baselineMatrix={baselineMatrix} />
    </main>
  );
}

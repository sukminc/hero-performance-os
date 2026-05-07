import Link from "next/link";
import { getHeroBaselineMatrix } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { AofBaselineSection } from "../../operator/matrix/aof-baseline-section";
import { MatrixPinBoard } from "../../operator/matrix/matrix-pin-board";
import { PreflopSizingTable } from "../../operator/matrix/preflop-sizing-table";
import { RunoutNoiseTrend } from "../../operator/matrix/runout-noise-trend";

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

export default async function AppMatrixPage() {
  const viewer = await getViewerContext();
  const baselineMatrix = await getHeroBaselineMatrix(viewer.playerId, "66");
  const preflopSizing = baselineMatrix?.preflop_sizing_summary;
  const preflopAof = baselineMatrix?.preflop_aof_summary;
  const hasMatrix = Boolean(baselineMatrix?.summary?.total_observations);

  if (!viewer.playerId) {
    return (
      <section className="page-card standout-card matrix-analysis-card">
        <p className="eyebrow">Your Matrix</p>
        <h1>Upload hand history, then see your preflop baseline.</h1>
        <p className="subtle">
          Your account is not mapped to a player model yet. Once access is provisioned, your uploads will turn into this
          Matrix view.
        </p>
        <Link className="cta" href="/app/account">
          Check account
        </Link>
      </section>
    );
  }

  return (
    <div className="app-matrix-surface">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero">
        <div>
          <p className="eyebrow">Your First Read</p>
          <h1>Your Preflop Matrix</h1>
          <p className="subtle">
            Upload GG hand histories and this page turns them into your actual preflop baseline: open sizes, 3bet
            sizing, AOF behavior, hand-class results, and the clearest review candidates.
          </p>
        </div>
        <div className="operator-home-actions">
          <Link className="cta" href="/app/upload">
            Upload hands
          </Link>
          {viewer.canSeeOperatorDepth ? (
            <Link className="secondary-cta" href="/operator/matrix">
              Operator matrix
            </Link>
          ) : null}
        </div>
      </section>

      {!hasMatrix ? (
        <section className="page-card matrix-analysis-card">
          <p className="eyebrow">Blank Matrix</p>
          <h3>No parsed hand histories yet.</h3>
          <p className="subtle">
            Add a GG Poker `.txt` packet or zip dump. After upload, your Matrix will show how you actually played and
            what the results were.
          </p>
          <Link className="cta" href="/app/upload">
            Upload first packet
          </Link>
        </section>
      ) : (
        <>
          <section className="page-card matrix-analysis-card preflop-summary-card">
            <div className="section-heading-row">
              <div>
                <p className="eyebrow">Sizing Summary</p>
                <h3>First action discipline</h3>
              </div>
              <span className="pill">your history</span>
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
        </>
      )}
    </div>
  );
}

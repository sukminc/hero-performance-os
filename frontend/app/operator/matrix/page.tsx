import Link from "next/link";
import { getHeroBaselineMatrix } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { MatrixPinBoard } from "./matrix-pin-board";

const HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111";

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

export default async function OperatorMatrixPage() {
  const viewer = await getViewerContext();
  const operatorPlayerId = viewer.playerId || (viewer.canSeeOperatorDepth ? HERO_PLAYER_ID : null);
  const baselineMatrix = await getHeroBaselineMatrix(operatorPlayerId, "66");
  const detail = baselineMatrix?.detail;

  return (
    <main className="shell matrix-shell">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero">
        <div>
          <p className="eyebrow">Matrix Analysis</p>
          <h1>Hero Baseline 13x13</h1>
          <p className="subtle">
            This page separates the hand-class matrix from the operator dashboard so the story is easier to read:
            raw BB, stack-normalized realization, played/dealt counts, action breakdown, correction targets, and hidden
            value candidates live together here.
          </p>
        </div>
        <Link className="secondary-cta" href="/operator">
          Back to operator
        </Link>
      </section>

      <section className="page-card matrix-analysis-card">
        <div className="result-hero">
          <div>
            <span className="sample-kicker">History</span>
            <strong>{baselineMatrix?.summary?.total_observations || 0}</strong>
            <p>
              {baselineMatrix?.summary?.distinct_hand_classes || 0} classes ·{" "}
              {baselineMatrix?.summary?.window_label || "All available history"}
            </p>
          </div>
          <div>
            <span className="sample-kicker">Selected Hand</span>
            <strong>{detail?.hand_class || "66"}</strong>
            <p>
              {detail?.summary?.played_count || detail?.summary?.hands_played || 0} played ·{" "}
              {detail?.summary?.dealt_count || 0} dealt · {formatMetric(detail?.summary?.avg_bb_per_hand, "bb")}
            </p>
          </div>
          <div>
            <span className="sample-kicker">Correction Queue</span>
            <strong>{baselineMatrix?.mandatory_correction_cards?.length || 0}</strong>
            <p>Action-specific leaks ranked by stack damage and repeat count.</p>
          </div>
        </div>
        <div className="baseline-toggle-note">
          <span>BB = actual chip result</span>
          <span>Stack % = result vs starting stack</span>
          <span>Played = voluntary call/raise/jam only</span>
          <span>Click cells to pin and compare action breakdowns</span>
        </div>
      </section>

      <section className="matrix-section-grid">
        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Must Fix</p>
              <h3>Correction candidates</h3>
            </div>
            <span className="pill">leak-first</span>
          </div>
          <div className="status-list compact">
            {(baselineMatrix?.mandatory_correction_cards || []).slice(0, 6).map((card: any, index: number) => (
              <div className="matrix-insight-row danger" key={`${card.hand_class}-${card.entry_type}`}>
                <strong>
                  {index + 1}. {card.title}
                </strong>
                <span>
                  {card.played_count}x · {card.avg_bb_per_hand}bb · {card.avg_stack_realization_pct}% stack
                </span>
                <p>{card.recommended_correction}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Keep / Study</p>
              <h3>Hidden value candidates</h3>
            </div>
            <span className="pill">positive execution</span>
          </div>
          <div className="status-list compact">
            {(baselineMatrix?.hidden_value_cards || []).slice(0, 6).map((card: any, index: number) => (
              <div className="matrix-insight-row value" key={`${card.hand_class}-${card.entry_type}`}>
                <strong>
                  {index + 1}. {card.title}
                </strong>
                <span>
                  {card.played_count}x · {card.avg_bb_per_hand}bb · {card.avg_stack_realization_pct}% stack
                </span>
                <p>{card.recommended_keep}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <MatrixPinBoard baselineMatrix={baselineMatrix} />

      {detail ? (
        <section className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Selected Hand Detail</p>
              <h3>{detail.hand_class} action breakdown</h3>
            </div>
            <span className="pill">{detail.summary.played_count || detail.summary.hands_played} played</span>
          </div>
          <div className="grid two">
            {(detail.action_depth_breakdown || []).map((row: any) => (
              <article className="status-item" key={`${detail.hand_class}-${row.entry_type}`}>
                <strong>{row.entry_type}</strong>
                <p className="subtle">
                  {row.played_count}x · {row.avg_bb_per_hand}bb/hand ·{" "}
                  {formatMetric(row.avg_stack_realization_pct, "%")} stack
                </p>
                <p className="subtle">Positions {JSON.stringify(row.positions || {})}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </main>
  );
}

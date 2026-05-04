import Link from "next/link";
import { getAofDecisionSystem, getBigWinReview, getHeroBaselineMatrix } from "@/lib/public-surfaces/read";
import { getDemoApplications } from "@/lib/operator/demo-applications";
import { getViewerContext } from "@/lib/viewer/session";
import { provisionDemoApplication, updateDemoApplicationStatus } from "./demo-actions";

function metric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

export default async function OperatorPage() {
  const viewer = await getViewerContext();
  const [applications, bigWin, aofV2, baselineMatrix] = await Promise.all([
    getDemoApplications(),
    getBigWinReview(viewer.playerId, "6408385"),
    getAofDecisionSystem(viewer.playerId),
    getHeroBaselineMatrix(viewer.playerId, "66")
  ]);

  const topCorrection = baselineMatrix?.mandatory_correction_cards?.[0];
  const topHiddenValue = baselineMatrix?.hidden_value_cards?.[0];
  const topAofLeak = aofV2?.priority_leak_cards?.[0];

  return (
    <main className="shell operator-home-shell">
      <section className="page-card operator-hero-card">
        <div>
          <p className="eyebrow">Operator Home</p>
          <h1>Your poker brain, organized.</h1>
          <p className="subtle">
            This page is now the control room: one screen for what matters, with deeper review moved into dedicated
            analysis pages instead of raw JSON blocks.
          </p>
        </div>
        <div className="operator-home-actions">
          <Link className="cta" href="/operator/matrix">
            Matrix Analysis
          </Link>
          <Link className="secondary-cta" href="/operator/aof">
            AOF Analysis
          </Link>
          <Link className="secondary-cta" href="/app">
            App Shell
          </Link>
        </div>
      </section>

      <section className="operator-command-grid">
        <Link className="page-card operator-command-card primary" href="/operator/matrix">
          <span className="sample-kicker">Core Surface</span>
          <h2>Matrix Analysis</h2>
          <p>Hand class EV, stack realization, action breakdown, leaks, and hidden value.</p>
          <strong>{baselineMatrix?.summary?.distinct_hand_classes || 0} hand classes</strong>
        </Link>
        <Link className="page-card operator-command-card" href="/operator/aof">
          <span className="sample-kicker">Core Surface</span>
          <h2>AOF Analysis</h2>
          <p>Short-stack decision quality with cooler protection and operator-defer guardrails.</p>
          <strong>{aofV2?.summary?.mistake_candidate_count || 0} leak candidates</strong>
        </Link>
        <Link className="page-card operator-command-card" href="/operator/big-win">
          <span className="sample-kicker">High Weight Context</span>
          <h2>Big Win Review</h2>
          <p>Separate repeatable execution from run-good in the Mini Thursday Throwdown result.</p>
          <strong>{bigWin?.review_summary?.candidate_count || 0} spots</strong>
        </Link>
      </section>

      <section className="page-card matrix-analysis-card operator-matrix-preview">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Matrix Preview</p>
            <h3>Less text, more signal.</h3>
          </div>
          <Link className="secondary-cta" href="/operator/matrix">
            Open full matrix
          </Link>
        </div>
        <p className="subtle">
          Preview cells show only the headline: hand, raw BB, stack %, and played count. The full page carries the detailed
          action breakdown so this dashboard stays readable.
        </p>
        <div className="baseline-matrix-grid compact-matrix-grid">
          {(baselineMatrix?.matrix_order || []).slice(0, 52).map((handClass: string) => {
            const cell = baselineMatrix?.matrix_cells?.[handClass] || {};
            return (
              <Link
                className={`baseline-cell compact-baseline-cell tone-${cell.style_tone || "empty"} stack-tone-${cell.stack_style_tone || "empty"}`}
                href="/operator/matrix"
                key={handClass}
              >
                <strong>{handClass}</strong>
                <span>{metric(cell.avg_bb_per_hand, "bb")}</span>
                <small>{metric(cell.avg_stack_realization_pct, "%")}</small>
                <em>{cell.played_count || cell.hands_played || 0} played</em>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="operator-insight-grid">
        <article className="page-card operator-readable-card danger">
          <span className="sample-kicker">Must Fix</span>
          <h3>{topCorrection?.title || "No correction candidate yet"}</h3>
          <p>
            {topCorrection
              ? `${topCorrection.played_count} repeats · ${topCorrection.avg_bb_per_hand}bb · ${topCorrection.avg_stack_realization_pct}% stack.`
              : "The correction queue will appear after enough repeated hand/action evidence exists."}
          </p>
          <strong>{topCorrection?.recommended_correction || "No action required yet."}</strong>
        </article>
        <article className="page-card operator-readable-card value">
          <span className="sample-kicker">Keep / Study</span>
          <h3>{topHiddenValue?.title || "No hidden value candidate yet"}</h3>
          <p>
            {topHiddenValue
              ? `${topHiddenValue.played_count} repeats · ${topHiddenValue.avg_bb_per_hand}bb · ${topHiddenValue.avg_stack_realization_pct}% stack.`
              : "Positive execution candidates will appear here so we do not over-correct away from working patterns."}
          </p>
          <strong>{topHiddenValue?.recommended_keep || "Keep collecting evidence."}</strong>
        </article>
        <article className="page-card operator-readable-card warning">
          <span className="sample-kicker">AOF Focus</span>
          <h3>{topAofLeak?.product_read?.title || topAofLeak?.hand_class || "No AOF priority yet"}</h3>
          <p>{topAofLeak?.product_read?.why_it_matters || "Short-stack leak cards are waiting for enough clear evidence."}</p>
          <strong>{topAofLeak?.product_read?.what_to_change || topAofLeak?.next_adjustment || "Review AOF page next."}</strong>
        </article>
      </section>

      <section className="page-card operator-clean-list">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Private Beta</p>
            <h3>Demo applications</h3>
          </div>
          <span className="pill">{applications.length} captured</span>
        </div>
        {applications.length ? (
          <div className="status-list compact">
            {applications.slice(0, 4).map((application) => (
              <div className="status-item" key={application.id}>
                <strong>{application.name}</strong>
                <div className="subtle">{application.email}</div>
                <div className="subtle">{application.help_goal}</div>
                <div className="pill-row">
                  <span className="pill">{application.status}</span>
                  {["screening", "approved", "rejected"].map((status) => (
                    <form action={updateDemoApplicationStatus} key={status}>
                      <input type="hidden" name="applicationId" value={application.id} />
                      <input type="hidden" name="status" value={status} />
                      <button className="pill button-reset" type="submit">
                        {status}
                      </button>
                    </form>
                  ))}
                </div>
                {application.status === "approved" ? (
                  <form className="input-grid compact-action" action={provisionDemoApplication}>
                    <input type="hidden" name="applicationId" value={application.id} />
                    <input name="playerId" placeholder="Target player id" />
                    <button className="cta button-reset" type="submit">
                      Provision owner access
                    </button>
                  </form>
                ) : null}
              </div>
            ))}
          </div>
        ) : (
          <p className="subtle">No demo applications captured yet.</p>
        )}
      </section>
    </main>
  );
}

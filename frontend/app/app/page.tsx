import Link from "next/link";
import {
  getConvictionReviewSummary,
  getFieldEcologySummary,
  getHudTrendSummary,
  getTimingStackSummary
} from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";

export default async function AppHomePage() {
  const viewer = await getViewerContext();
  const [conviction, timing, hud, field] = await Promise.all([
    getConvictionReviewSummary(viewer.playerId),
    getTimingStackSummary(viewer.playerId),
    getHudTrendSummary(viewer.playerId),
    getFieldEcologySummary(viewer.playerId)
  ]);

  const overtrust = conviction?.overtrust_cards?.slice(0, 3) || [];
  const timingSummary = timing?.summary;
  const conclusionCards = timing?.conclusion_cards?.slice(0, 3) || [];
  const featuredMetrics = hud?.featured_metrics?.slice(0, 3) || [];
  const ecologyCards = field?.ecology_cards?.slice(0, 3) || [];

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Dashboard</p>
        <h1>
          {viewer.role === "operator"
            ? "Operator/admin view of Hero performance is active."
            : "Hero-first performance dashboard is active."}
        </h1>
        <p className="subtle">
          {viewer.role === "operator"
            ? "You can inspect the same player through both user-facing surfaces and operator-level depth. Public users should never see another player's interpretation."
            : "When you log in as the current player, the app should already feel like it knows your repeated tendencies, your friction spots, and your current adjustment direction."}
        </p>
        <div className="pill-row">
          <span className="pill">player scope: {viewer.playerScope}</span>
          <span className="pill">{viewer.role === "operator" ? "operator/admin" : "standard user"}</span>
          {viewer.canSeeOperatorDepth ? (
            <Link className="pill" href="/operator">
              open operator/admin
            </Link>
          ) : null}
        </div>
      </section>

      {!viewer.playerId ? (
        <section className="page-card">
          <h3>Access Boundary</h3>
          <p className="subtle">
            This login is authenticated, but it is not currently mapped to a player ownership record. Public shell data stays
            hidden until the auth identity is explicitly connected to a player scope.
          </p>
        </section>
      ) : null}

      <section className="grid three">
        <article className="page-card">
          <h3>Best Operating Zone</h3>
          <div className="metric">{timingSummary?.best_operating_zone || "n/a"}</div>
          <p className="subtle">
            Highest friction zone: {timingSummary?.highest_friction_zone || "n/a"}.
            20bb neighborhood: {timingSummary?.comfort_hypothesis_20bb?.avg_bb_per_hand ?? "n/a"} bb/hand.
          </p>
        </article>
        <article className="page-card">
          <h3>Conviction Watch</h3>
          {overtrust.length ? (
            <div className="status-list">
              {overtrust.map((item: { hand_class: string; avg_bb_per_hand: number; reason: string }) => (
                <div className="status-item" key={item.hand_class}>
                  <strong>{item.hand_class}</strong>
                  <div>{item.avg_bb_per_hand} bb/hand</div>
                  <div className="subtle">{item.reason}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtle">No conviction queue yet.</p>
          )}
        </article>
        <article className="page-card">
          <h3>Field + Trend</h3>
          <div className="status-list">
            {featuredMetrics.map((item: { label: string; current: number; interpretation: string }) => (
              <div className="status-item" key={item.label}>
                <strong>{item.label}</strong>
                <div>{item.current}%</div>
                <div className="subtle">{item.interpretation}</div>
              </div>
            ))}
            {ecologyCards.map((item: { label: string; value: number; meaning: string }) => (
              <div className="status-item" key={item.label}>
                <strong>{item.label}</strong>
                <div>{item.value}%</div>
                <div className="subtle">{item.meaning}</div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="grid two">
        <article className="page-card">
          <h3>Current Interpretation Direction</h3>
          {conclusionCards.length ? (
            <div className="status-list">
              {conclusionCards.map((item: { title: string; summary: string; why: string }) => (
                <div className="status-item" key={item.title}>
                  <strong>{item.title}</strong>
                  <div>{item.summary}</div>
                  <div className="subtle">{item.why}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtle">No timing/conclusion cards yet.</p>
          )}
        </article>
        <article className="page-card">
          <h3>Data Access Boundary</h3>
          <p className="subtle">
            Public users should only ever see their own interpretation surface. Operator/admin can inspect deeper detail, but
            ordinary users must never be able to see another player's data.
          </p>
          <pre className="status-pre">
            {JSON.stringify(
              {
                currentRole: viewer.role,
                playerScope: viewer.playerScope,
                canSeeOperatorDepth: viewer.canSeeOperatorDepth,
                ownershipResolved: viewer.ownershipResolved,
                ownershipSource: viewer.ownershipSource
              },
              null,
              2
            )}
          </pre>
        </article>
      </section>
    </>
  );
}

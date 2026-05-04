import Link from "next/link";
import {
  getConvictionReviewSummary,
  getFieldEcologySummary,
  getHudTrendSummary,
  getPublicTodaySurface,
  getTimingStackSummary,
} from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { humanizeState } from "@/lib/public-surfaces/humanize";

export default async function AppHomePage() {
  const viewer = await getViewerContext();
  const [today, conviction, timing, hud, field] = await Promise.all([
    getPublicTodaySurface(viewer.playerId),
    getConvictionReviewSummary(viewer.playerId),
    getTimingStackSummary(viewer.playerId),
    getHudTrendSummary(viewer.playerId),
    getFieldEcologySummary(viewer.playerId),
  ]);

  const todayPayload = today?.payload;
  const stateInfo = humanizeState(todayPayload?.current_state);
  const overtrust = conviction?.overtrust_cards?.slice(0, 3) || [];
  const timingSummary = timing?.summary;
  const conclusionCards = timing?.conclusion_cards?.slice(0, 3) || [];
  const featuredMetrics = hud?.featured_metrics?.slice(0, 3) || [];
  const ecologyCards = field?.ecology_cards?.slice(0, 3) || [];

  if (!viewer.playerId) {
    return (
      <section className="page-card">
        <p className="eyebrow">Dashboard</p>
        <h1>Waiting for player access.</h1>
        <p className="subtle">
          Your login is authenticated, but it isn&apos;t mapped to a player ownership record yet. Once the operator
          provisions you, this dashboard will fill in.
        </p>
      </section>
    );
  }

  return (
    <>
      <section className={`page-card today-hero state-tone-${stateInfo.tone}`}>
        <div className="today-hero-row">
          <p className="eyebrow">{viewer.role === "operator" ? "Operator view · Hero" : "Your read"}</p>
          <span className={`state-pill tone-${stateInfo.tone}`}>{stateInfo.label}</span>
        </div>
        <h1 className="today-headline">
          {todayPayload?.headline || "Upload a session to start your read."}
        </h1>
        <div className="dashboard-cta-row">
          <Link className="cta" href="/app/today">
            Open Today
          </Link>
          <Link className="secondary-cta" href="/app/review">
            Latest review
          </Link>
          <Link className="secondary-cta" href="/app/brain">
            Long-term read
          </Link>
          {viewer.canSeeOperatorDepth ? (
            <Link className="secondary-cta" href="/operator">
              Operator console
            </Link>
          ) : null}
        </div>
      </section>

      <section className="grid three">
        <article className="page-card">
          <p className="eyebrow">Best operating zone</p>
          <div className="metric metric-sm">{timingSummary?.best_operating_zone || "—"}</div>
          <p className="subtle">
            Highest friction: <strong>{timingSummary?.highest_friction_zone || "—"}</strong>.
            {typeof timingSummary?.comfort_hypothesis_20bb?.avg_bb_per_hand === "number"
              ? ` 20bb neighborhood runs ${timingSummary.comfort_hypothesis_20bb.avg_bb_per_hand} bb/hand.`
              : null}
          </p>
        </article>
        <article className="page-card">
          <p className="eyebrow">Conviction watch</p>
          {overtrust.length ? (
            <div className="status-list compact">
              {overtrust.map((item: { hand_class: string; avg_bb_per_hand: number; reason: string }) => (
                <div className="status-item" key={item.hand_class}>
                  <strong>{item.hand_class}</strong>
                  <div className="subtle">{item.avg_bb_per_hand} bb/hand</div>
                  <div className="subtle">{item.reason}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtle">No overtrusted hand classes flagged right now.</p>
          )}
        </article>
        <article className="page-card">
          <p className="eyebrow">Field & trend</p>
          {featuredMetrics.length || ecologyCards.length ? (
            <div className="status-list compact">
              {featuredMetrics.map((item: { label: string; current: number; interpretation: string }) => (
                <div className="status-item" key={`hud-${item.label}`}>
                  <strong>{item.label}</strong>
                  <div className="subtle">{item.current}%</div>
                  <div className="subtle">{item.interpretation}</div>
                </div>
              ))}
              {ecologyCards.map((item: { label: string; value: number; meaning: string }) => (
                <div className="status-item" key={`eco-${item.label}`}>
                  <strong>{item.label}</strong>
                  <div className="subtle">{item.value}%</div>
                  <div className="subtle">{item.meaning}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtle">Field context will appear after enough sessions accumulate.</p>
          )}
        </article>
      </section>

      {conclusionCards.length ? (
        <section className="page-card">
          <p className="eyebrow">Current direction</p>
          <h3>What the timing data is saying</h3>
          <div className="status-list">
            {conclusionCards.map((item: { title: string; summary: string; why: string }) => (
              <div className="status-item" key={item.title}>
                <strong>{item.title}</strong>
                <div>{item.summary}</div>
                <div className="subtle">{item.why}</div>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </>
  );
}

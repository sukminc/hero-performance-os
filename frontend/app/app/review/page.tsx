import { getPublicReviewSurface } from "@/lib/public-surfaces/read";
import { getCurrentPlan } from "@/lib/billing/account";
import { getViewerContext } from "@/lib/viewer/session";
import { humanizeResultSignal } from "@/lib/public-surfaces/humanize";

function formatBuyin(band: string | null | undefined) {
  if (!band) return "Tournament";
  return band.replace(/Hold'?em No Limit/i, "").replace(/\s+,\s*$/, "").trim() || band;
}

function formatTimestamp(value: string | null | undefined) {
  if (!value) return "";
  return value.replace(/(\d{4})\/(\d{2})\/(\d{2}) (\d{2}:\d{2}):\d{2}/, "$1-$2-$3 $4");
}

export default async function ReviewPage() {
  const viewer = await getViewerContext();
  const review = await getPublicReviewSurface(viewer.playerId);
  const plan = await getCurrentPlan();
  const session = review?.session;
  const story = review?.session_story;
  const resultContext = review?.result_context;
  const evidenceSummary = review?.evidence_summary;
  const groundwork = review?.interpretation_groundwork;
  const parseQuality = review?.parse_quality;

  if (!viewer.playerId) {
    return (
      <section className="page-card">
        <p className="eyebrow">Review</p>
        <h1>Waiting for player access.</h1>
        <p className="subtle">
          Once your login is mapped to a player, the latest uploaded session will be reviewed here.
        </p>
      </section>
    );
  }

  if (!session) {
    return (
      <section className="page-card">
        <p className="eyebrow">Review</p>
        <h1>No sessions yet.</h1>
        <p className="subtle">
          Upload a GG session packet on the Upload page. After it processes, the latest session story will appear here.
        </p>
      </section>
    );
  }

  const promotions: string[] = story?.top_promotions || [];
  const watchlist: string[] = story?.top_watchlist || [];
  const officialResult = resultContext?.official_result;
  const reviewPrompts: string[] = resultContext?.review_prompts || [];

  return (
    <>
      <section className="page-card review-hero">
        <p className="eyebrow">Review · Latest session</p>
        <h1 className="review-headline">{formatBuyin(session.buyin_band)}</h1>
        <p className="subtle review-meta">
          {session.hand_count} hands · {formatTimestamp(session.started_at)} · parse {parseQuality?.confidence_label || "ok"}
        </p>
        <div className="review-stat-row">
          <div className="review-stat">
            <span className="subtle">New evidence</span>
            <strong>{story?.new_evidence_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">Promoted</span>
            <strong>{story?.promoted_memory_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">On watch</span>
            <strong>{story?.watch_memory_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">Hands parsed</span>
            <strong>{parseQuality?.parsed_hands ?? session.hand_count}</strong>
          </div>
        </div>
      </section>

      {officialResult ? (
        <section className="page-card result-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Official result</p>
              <h3>{officialResult.title || "Tournament result"}</h3>
            </div>
            <span className={`state-pill tone-${resultContext?.result_signal === "top_three_big_cash" || resultContext?.result_signal === "final_table" ? "good" : "neutral"}`}>
              {humanizeResultSignal(resultContext?.result_signal)}
            </span>
          </div>
          <div className="review-stat-row">
            <div className="review-stat">
              <span className="subtle">Finish</span>
              <strong>{officialResult.finish_place || "—"}</strong>
            </div>
            <div className="review-stat">
              <span className="subtle">Prize</span>
              <strong>{officialResult.total_received || "—"}</strong>
            </div>
            <div className="review-stat">
              <span className="subtle">Field</span>
              <strong>{officialResult.player_count ? `${officialResult.player_count} entries` : "—"}</strong>
            </div>
            <div className="review-stat">
              <span className="subtle">Buy-in</span>
              <strong>{officialResult.buy_in || "—"}</strong>
            </div>
          </div>
          {resultContext?.interpretation ? <p className="subtle">{resultContext.interpretation}</p> : null}
        </section>
      ) : null}

      <section className="grid two">
        <article className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">What got reinforced</p>
              <h3>Promoted patterns</h3>
            </div>
            <span className="pill">{promotions.length}</span>
          </div>
          {promotions.length ? (
            <ul className="prose-list">
              {promotions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="subtle">No new pattern promotions in this session.</p>
          )}
        </article>
        <article className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Worth tracking</p>
              <h3>On watch</h3>
            </div>
            <span className="pill">{watchlist.length}</span>
          </div>
          {watchlist.length ? (
            <ul className="prose-list">
              {watchlist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="subtle">Nothing new on the watchlist.</p>
          )}
        </article>
      </section>

      {evidenceSummary ? (
        <section className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Evidence breakdown</p>
              <h3>What this session produced</h3>
            </div>
            <span className="pill">{evidenceSummary.total_evidence} signals</span>
          </div>
          <div className="evidence-grid">
            {Object.entries(evidenceSummary.by_direction || {})
              .filter(([, value]) => Number(value) > 0)
              .map(([direction, count]) => (
                <div className={`evidence-pill tone-${direction === "positive" ? "good" : direction === "negative" ? "alert" : direction === "shift" ? "warn" : "neutral"}`} key={direction}>
                  <strong>{count as number}</strong>
                  <span>{direction.replace(/_/g, " ")}</span>
                </div>
              ))}
          </div>
        </section>
      ) : null}

      {reviewPrompts.length ? (
        <section className="page-card">
          <p className="eyebrow">Review prompts</p>
          <h3>Questions to take into next study</h3>
          <ul className="prose-list">
            {reviewPrompts.map((prompt) => (
              <li key={prompt}>{prompt}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {!plan.gates.premiumReview ? (
        <p className="subtle plan-footnote">
          Free Beta plan keeps Review compact. Hand-level deep-dives unlock under paid entitlement.
        </p>
      ) : null}
    </>
  );
}

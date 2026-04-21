import { getPublicReviewSurface } from "@/lib/public-surfaces/read";
import { getCurrentPlan } from "@/lib/billing/account";
import { getViewerContext } from "@/lib/viewer/session";

export default async function ReviewPage() {
  const viewer = await getViewerContext();
  const review = await getPublicReviewSurface(viewer.playerId);
  const plan = await getCurrentPlan();
  const session = review?.session;
  const story = review?.session_story;

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Review</p>
        <h1>{session ? "Latest uploaded session review" : "Review surface is waiting for upload-backed session data."}</h1>
        <p className="subtle">
          {!viewer.playerId
            ? "This login is not mapped to a player ownership record yet, so Review stays blank instead of showing another player's session story."
            : session
            ? `Latest session: ${session.buyin_band || "Unknown buy-in"} · ${session.hand_count} hands · parse status ${session.parse_status}.`
            : "Once uploads are available, this page will show a public-safe cumulative review instead of raw operator internals."}
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Session Story</h3>
          <pre className="status-pre">{JSON.stringify(story || {}, null, 2)}</pre>
        </article>
        <article className="page-card">
          <h3>Interpretation Readiness</h3>
          <pre className="status-pre">{JSON.stringify(review?.interpretation_groundwork || {}, null, 2)}</pre>
          {!plan.gates.premiumReview ? (
            <p className="subtle">Free Beta plan shows the compact review surface. Premium review depth will unlock under paid entitlement.</p>
          ) : null}
        </article>
      </section>
    </>
  );
}

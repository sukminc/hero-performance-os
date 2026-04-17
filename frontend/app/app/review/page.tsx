import { getPublicReviewSurface } from "@/lib/public-surfaces/read";

export default async function ReviewPage() {
  const review = await getPublicReviewSurface();
  const session = review?.session;
  const story = review?.session_story;

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Review</p>
        <h1>{session ? "Latest uploaded session review" : "Review surface is waiting for upload-backed session data."}</h1>
        <p className="subtle">
          {session
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
        </article>
      </section>
    </>
  );
}

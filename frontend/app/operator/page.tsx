import Link from "next/link";
import {
  getConvictionReviewSummary,
  getFieldEcologySummary,
  getHudTrendSummary,
  getTimingStackSummary
} from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";

export default async function OperatorPage() {
  const viewer = await getViewerContext();
  const [conviction, timing, hud, field] = await Promise.all([
    getConvictionReviewSummary(viewer.playerId),
    getTimingStackSummary(viewer.playerId),
    getHudTrendSummary(viewer.playerId),
    getFieldEcologySummary(viewer.playerId)
  ]);

  return (
    <main className="shell">
      <section className="page-card">
        <p className="eyebrow">Operator</p>
        <h1>Operator/admin view is active.</h1>
        <p className="subtle">
          This route is intentionally different from the standard user shell. In production, operator/admin access remains
          private and role-gated even when public users can log in.
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Deep Pattern Detail</h3>
          <pre className="status-pre">
            {JSON.stringify(
              {
                convictionTop: conviction?.overtrust_cards?.slice(0, 5) || [],
                timingSummary: timing?.summary || {},
                timingConclusions: timing?.conclusion_cards?.slice(0, 3) || []
              },
              null,
              2
            )}
          </pre>
        </article>
        <article className="page-card">
          <h3>Trend + Ecology Detail</h3>
          <pre className="status-pre">
            {JSON.stringify(
              {
                featuredMetrics: hud?.featured_metrics?.slice(0, 5) || [],
                ecologyCards: field?.ecology_cards || [],
                heroLimpMultiway: field?.hero_limp_multiway || {}
              },
              null,
              2
            )}
          </pre>
        </article>
      </section>
      <section className="page-card">
        <h3>Public shell jump</h3>
        <p className="subtle">Operator/admin can still move through the public user shell while retaining access to deeper detail here.</p>
        <Link className="cta" href="/app">
          Open App Shell
        </Link>
      </section>
    </main>
  );
}

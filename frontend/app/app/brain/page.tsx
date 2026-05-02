import { getPublicBrainSurface } from "@/lib/public-surfaces/read";
import { getCurrentPlan } from "@/lib/billing/account";
import { getViewerContext } from "@/lib/viewer/session";

export default async function BrainPage() {
  const viewer = await getViewerContext();
  const brain = await getPublicBrainSurface(viewer.playerId);
  const plan = await getCurrentPlan();
  const longitudinal = brain?.longitudinal_update;
  const latestResultContext = brain?.latest_result_context;
  const resultSignals = brain?.tournament_result_signals;

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Brain</p>
        <h1>{longitudinal?.headline || "Brain surface is still waiting for enough cumulative interpretation."}</h1>
        <p className="subtle">
          {!viewer.playerId
            ? "This login is not mapped to a player ownership record yet, so Brain stays hidden instead of exposing another player's cumulative interpretation."
            : "This public Brain view is intentionally compact. It keeps the cumulative player interpretation while hiding operator-only tooling and correction layers."}
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Top Result Signals</h3>
          <pre className="status-pre">{JSON.stringify(resultSignals || {}, null, 2)}</pre>
        </article>
        <article className="page-card">
          <h3>Latest Result Context</h3>
          <pre className="status-pre">{JSON.stringify(latestResultContext || {}, null, 2)}</pre>
        </article>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Hero Standard</h3>
          <pre className="status-pre">{JSON.stringify(brain?.hero_standard || {}, null, 2)}</pre>
        </article>
        <article className="page-card">
          <h3>Persistent Pressures</h3>
          <pre className="status-pre">{JSON.stringify(brain?.persistent_pressures || [], null, 2)}</pre>
          {!plan.gates.premiumBrain ? (
            <p className="subtle">Free Beta plan keeps Brain compact. Deeper cumulative breakdown will live behind paid entitlement.</p>
          ) : null}
        </article>
      </section>
    </>
  );
}

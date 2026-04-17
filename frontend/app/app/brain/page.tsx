import { getPublicBrainSurface } from "@/lib/public-surfaces/read";
import { getCurrentPlan } from "@/lib/billing/account";

export default async function BrainPage() {
  const brain = await getPublicBrainSurface();
  const plan = await getCurrentPlan();
  const longitudinal = brain?.longitudinal_update;

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Brain</p>
        <h1>{longitudinal?.headline || "Brain surface is still waiting for enough cumulative interpretation."}</h1>
        <p className="subtle">
          This public Brain view is intentionally compact. It keeps the cumulative player interpretation while hiding operator-only
          tooling and correction layers.
        </p>
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

import { getPublicBrainSurface } from "@/lib/public-surfaces/read";
import { getCurrentPlan } from "@/lib/billing/account";
import { getViewerContext } from "@/lib/viewer/session";
import {
  confidencePercent,
  directionTone,
  humanizeMemoryType,
  humanizeResultSignal,
  humanizeStatus,
  shortenSummary,
} from "@/lib/public-surfaces/humanize";

type MemoryRow = {
  memory_type: string;
  entity_key: string;
  label: string;
  status: string;
  direction: string;
  maturity: string;
  evidence_count: number;
  confidence: number;
  summary: string;
};

type ResultSignal = {
  tournament_id: string;
  title: string;
  started_at: string;
  finish_place: string;
  total_received: string;
  signal: string;
  interpretation: string;
};

export default async function BrainPage() {
  const viewer = await getViewerContext();
  const brain = await getPublicBrainSurface(viewer.playerId);
  const plan = await getCurrentPlan();

  if (!viewer.playerId) {
    return (
      <section className="page-card">
        <p className="eyebrow">Brain</p>
        <h1>Waiting for player access.</h1>
        <p className="subtle">
          Your cumulative read will live here once your login is mapped to a player.
        </p>
      </section>
    );
  }

  if (!brain) {
    return (
      <section className="page-card">
        <p className="eyebrow">Brain</p>
        <h1>Building your read.</h1>
        <p className="subtle">
          Brain accumulates across sessions. Upload a few packets and the long-term picture will start to form.
        </p>
      </section>
    );
  }

  const longitudinal = brain.longitudinal_update || {};
  const heroStandard: MemoryRow | null = brain.hero_standard || null;
  const persistentPressures: MemoryRow[] = brain.persistent_pressures || [];
  const fieldContext: MemoryRow[] = brain.field_context || [];
  const resultSignals = brain.tournament_result_signals || {};
  const topResults: ResultSignal[] = (resultSignals.top_result_signals || []).slice(0, 4);

  return (
    <>
      <section className="page-card brain-hero">
        <p className="eyebrow">Brain · Long-term read</p>
        <h1 className="brain-headline">
          {longitudinal.headline || "Building your cumulative read."}
        </h1>
        <div className="brain-stat-row">
          <div className="review-stat">
            <span className="subtle">Baseline patterns</span>
            <strong>{longitudinal.baseline_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">Pressure points</span>
            <strong>{longitudinal.persistent_pressure_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">Field signals</span>
            <strong>{longitudinal.field_signal_count ?? 0}</strong>
          </div>
          <div className="review-stat">
            <span className="subtle">Official results</span>
            <strong>{resultSignals.total_official_results ?? 0}</strong>
          </div>
        </div>
      </section>

      {heroStandard ? (
        <section className="page-card hero-standard-card">
          <p className="eyebrow">Hero Standard</p>
          <h2>{heroStandard.label}</h2>
          <p>{shortenSummary(heroStandard.summary)}</p>
          <div className="confidence-row">
            <span className="pill">{humanizeStatus(heroStandard.status)}</span>
            <span className="pill">{heroStandard.evidence_count} hands</span>
            <span className="pill">confidence {confidencePercent(heroStandard.confidence)}%</span>
          </div>
        </section>
      ) : null}

      {persistentPressures.length ? (
        <section className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Pressure points</p>
              <h3>Where you keep getting stuck</h3>
            </div>
            <span className="pill">{persistentPressures.length}</span>
          </div>
          <div className="brain-card-grid">
            {persistentPressures.map((row) => {
              const tone = directionTone(row.direction);
              return (
                <article className={`brain-pattern-card tone-${tone}`} key={`${row.memory_type}:${row.entity_key}`}>
                  <div className="brain-pattern-head">
                    <span className="pill">{humanizeMemoryType(row.memory_type)}</span>
                    <span className="subtle">{row.evidence_count} hands</span>
                  </div>
                  <strong>{row.label}</strong>
                  <p>{shortenSummary(row.summary)}</p>
                  <div className="confidence-row">
                    <div className="confidence-bar" aria-hidden="true">
                      <span style={{ width: `${confidencePercent(row.confidence)}%` }} />
                    </div>
                    <span className="subtle">{humanizeStatus(row.status)}</span>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      ) : null}

      {fieldContext.length ? (
        <section className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Field context</p>
              <h3>Pool texture you keep facing</h3>
            </div>
            <span className="pill">{fieldContext.length}</span>
          </div>
          <div className="brain-card-grid">
            {fieldContext.map((row) => (
              <article className="brain-pattern-card tone-neutral" key={`field:${row.entity_key}`}>
                <span className="pill">Field</span>
                <strong>{row.label}</strong>
                <p>{shortenSummary(row.summary)}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {topResults.length ? (
        <section className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">High-weight results</p>
              <h3>Deep runs to mine for repeatable execution</h3>
            </div>
            <span className="pill">{resultSignals.total_official_results} total</span>
          </div>
          <div className="result-list">
            {topResults.map((result) => {
              const tone = result.signal === "top_three_big_cash" || result.signal === "final_table" ? "good" : "neutral";
              return (
                <article className={`result-row tone-${tone}`} key={result.tournament_id}>
                  <div>
                    <strong>{result.title}</strong>
                    <span className="subtle">{result.started_at}</span>
                  </div>
                  <div className="result-row-meta">
                    <span className="pill">{humanizeResultSignal(result.signal)}</span>
                    <strong>{result.finish_place}</strong>
                    <span className="subtle">{result.total_received}</span>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      ) : null}

      {!plan.gates.premiumBrain ? (
        <p className="subtle plan-footnote">
          Free Beta plan shows the compact Brain. Per-pattern timelines and operator-grade memory graph live behind paid
          entitlement.
        </p>
      ) : null}
    </>
  );
}

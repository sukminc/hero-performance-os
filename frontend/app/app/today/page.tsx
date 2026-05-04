import { getPublicTodaySurface } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import {
  confidencePercent,
  directionTone,
  humanizeEntity,
  humanizeMemoryType,
  humanizeState,
  humanizeStatus,
  shortenSummary,
} from "@/lib/public-surfaces/humanize";

type Adjustment = {
  label: string;
  reason: string;
  confidence: number;
  memory_id?: string;
};

type SupportingMemory = {
  id: string;
  memory_type: string;
  memory_key: string;
  status: string;
  confidence: number;
  summary: string;
  evidence_count: number;
  maturity: string;
  direction: string;
};

function entityKeyFromMemoryKey(memoryKey: string) {
  const parts = memoryKey.split(":");
  return parts[parts.length - 1] || memoryKey;
}

export default async function TodayPage() {
  const viewer = await getViewerContext();
  const today = await getPublicTodaySurface(viewer.playerId);
  const payload = today?.payload;
  const adjustments: Adjustment[] = payload?.adjustments || [];
  const supporting: SupportingMemory[] = payload?.supporting_memory || [];
  const stateInfo = humanizeState(payload?.current_state);
  const confidenceSummary = today?.confidence_summary || payload?.confidence_summary;

  if (!viewer.playerId) {
    return (
      <section className="page-card">
        <p className="eyebrow">Today</p>
        <h1>Waiting for player access.</h1>
        <p className="subtle">
          Your login is authenticated, but it isn't mapped to a player yet. Once the operator provisions you, Today will
          show your next adjustment here.
        </p>
      </section>
    );
  }

  if (!payload) {
    return (
      <section className="page-card">
        <p className="eyebrow">Today</p>
        <h1>Upload a session to start your read.</h1>
        <p className="subtle">
          Today shows the one or two things to focus on before the next session. Drop a GG <code>.txt</code> on the Upload
          page and this surface will fill in.
        </p>
      </section>
    );
  }

  const focusAdjustments = adjustments.slice(0, 3);
  const watchItems = supporting.filter((item) => item.status === "watch").slice(0, 4);

  return (
    <>
      <section className={`page-card today-hero state-tone-${stateInfo.tone}`}>
        <div className="today-hero-row">
          <p className="eyebrow">Today · Pre-session focus</p>
          <span className={`state-pill tone-${stateInfo.tone}`}>{stateInfo.label}</span>
        </div>
        <h1 className="today-headline">{payload.headline}</h1>
        {confidenceSummary ? (
          <p className="subtle today-meta">
            {confidenceSummary.adjustment_count || focusAdjustments.length} focus item
            {focusAdjustments.length === 1 ? "" : "s"} · {confidenceSummary.memory_items_considered || supporting.length}{" "}
            patterns considered · avg confidence {confidencePercent(confidenceSummary.average_confidence)}%
          </p>
        ) : null}
      </section>

      <section className="page-card">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Do this next session</p>
            <h3>Adjustments</h3>
          </div>
          <span className="pill">{focusAdjustments.length} focus</span>
        </div>
        {focusAdjustments.length ? (
          <div className="focus-list">
            {focusAdjustments.map((adjustment, index) => {
              const supportingHit = supporting.find((m) => m.id === adjustment.memory_id);
              const tone = supportingHit ? directionTone(supportingHit.direction) : "neutral";
              const entity = supportingHit
                ? humanizeEntity(entityKeyFromMemoryKey(supportingHit.memory_key))
                : adjustment.label;
              const conf = confidencePercent(adjustment.confidence);
              return (
                <article className={`focus-card tone-${tone}`} key={adjustment.memory_id || index}>
                  <div className="focus-card-head">
                    <strong>{entity}</strong>
                    <span className="pill">{humanizeMemoryType(supportingHit?.memory_type)}</span>
                  </div>
                  <p>{shortenSummary(adjustment.reason, adjustment.reason)}</p>
                  <div className="confidence-row">
                    <div className="confidence-bar" aria-hidden="true">
                      <span style={{ width: `${conf}%` }} />
                    </div>
                    <span className="subtle">confidence {conf}%</span>
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <p className="subtle">No urgent adjustments. Carry your baseline forward.</p>
        )}
      </section>

      {watchItems.length ? (
        <section className="page-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">In the background</p>
              <h3>Patterns we&apos;re watching</h3>
            </div>
            <span className="pill">{watchItems.length} signals</span>
          </div>
          <p className="subtle">
            These haven&apos;t crossed into action yet, but they&apos;re building. Keep an eye on them in your next sessions.
          </p>
          <div className="watch-grid">
            {watchItems.map((item) => {
              const tone = directionTone(item.direction);
              const entity = humanizeEntity(entityKeyFromMemoryKey(item.memory_key));
              return (
                <article className={`watch-card tone-${tone}`} key={item.id}>
                  <div className="watch-card-head">
                    <span className="pill">{humanizeMemoryType(item.memory_type)}</span>
                    <span className="subtle">{humanizeStatus(item.status)} · {item.evidence_count} hands</span>
                  </div>
                  <strong>{entity}</strong>
                  <p>{shortenSummary(item.summary)}</p>
                </article>
              );
            })}
          </div>
        </section>
      ) : null}
    </>
  );
}

import { getPublicTodaySurface } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";

export default async function TodayPage() {
  const viewer = await getViewerContext();
  const today = await getPublicTodaySurface(viewer.playerId);
  const payload = today?.payload;

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Today</p>
        <h1>{payload?.headline || "Today surface is not ready yet."}</h1>
        <p className="subtle">
          {!viewer.playerId
            ? "This login is not mapped to a player ownership record yet, so Today stays blank instead of leaking another player's adjustment surface."
            : payload?.current_state
            ? `Current state: ${payload.current_state}. This public view intentionally shows the next adjustment, not the full operator backend.`
            : "This page will show the latest pre-session adjustment once a valid upload has produced Today output."}
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Adjustments</h3>
          {payload?.adjustments?.length ? (
            <div className="status-list">
              {payload.adjustments.map((item: { label: string; reason: string; confidence: number }) => (
                <div className="status-item" key={item.label}>
                  <strong>{item.label}</strong>
                  <div>{item.reason}</div>
                  <div className="subtle">confidence {item.confidence}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtle">No Today adjustments yet.</p>
          )}
        </article>
        <article className="page-card">
          <h3>Confidence</h3>
          <pre className="status-pre">{JSON.stringify(today?.confidence_summary || payload?.confidence_summary || {}, null, 2)}</pre>
        </article>
      </section>
    </>
  );
}

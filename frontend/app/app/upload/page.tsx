import { getLatestUploadStatuses, getUploadCoverageSummary } from "@/lib/uploads/status";
import { getViewerContext } from "@/lib/viewer/session";
import { UploadForm } from "./upload-form";

export default async function UploadPage() {
  const viewer = await getViewerContext();
  const [latestUploads, coverage] = await Promise.all([
    getLatestUploadStatuses(viewer.playerId),
    getUploadCoverageSummary(viewer.playerId),
  ]);
  const latestIngested = coverage?.latestIngestedFiles || [];
  const latestSummaryOnly = coverage?.latestSummaryOnlyFiles || [];

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Upload</p>
        <h1>Restore Hero corpus, inspect the cutoff date, then dump the next packet batch.</h1>
        <p className="subtle">
          This upload path writes to the player model resolved from your login. Unmapped users stay blank until operator
          provisioning grants explicit player access.
        </p>
        <p className="subtle">
          Tournament result summaries without actual hand blocks are treated as summary-only exports and skipped instead of
          being shown as hard parser failures.
        </p>
        {coverage ? (
          <div className="grid three">
            <div className="status-item">
              <strong>Current corpus</strong>
              <div>{coverage.totalSessions} sessions</div>
              <div>{coverage.totalHands} hands</div>
              <div className="subtle">{coverage.totalMemoryItems} memory items</div>
            </div>
            <div className="status-item">
              <strong>Session date range</strong>
              <div>{coverage.firstSessionAt || "n/a"}</div>
              <div className="subtle">through {coverage.lastSessionAt || "n/a"}</div>
            </div>
            <div className="status-item">
              <strong>Last upload batch</strong>
              <div>{coverage.lastUploadAt || "n/a"}</div>
              <div className="subtle">
                {coverage.latestFiles[0]?.original_filename || "No upload history available in canonical store."}
              </div>
            </div>
          </div>
        ) : null}
        <UploadForm />
      </section>
      <section className="page-card">
        <h3>Recent Upload Readout</h3>
        <div className="grid two">
          <div className="status-item">
            <strong>Recent real hand-packet ingests</strong>
            {latestIngested.length ? (
              <div className="status-list compact">
                {latestIngested.map((item) => (
                  <div key={`${item.original_filename}-${item.uploaded_at}`}>
                    <div>{item.original_filename}</div>
                    <div className="subtle">{item.uploaded_at}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="subtle">No ingested hand-packets yet.</p>
            )}
          </div>
          <div className="status-item">
            <strong>Recent summary-only skips</strong>
            {latestSummaryOnly.length ? (
              <div className="status-list compact">
                {latestSummaryOnly.map((item) => (
                  <div key={`${item.original_filename}-${item.uploaded_at}`}>
                    <div>{item.original_filename}</div>
                    <div className="subtle">{item.uploaded_at}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="subtle">No summary-only skips yet.</p>
            )}
          </div>
        </div>
        {latestUploads.length ? (
          <details className="upload-details">
            <summary>Raw latest ingest rows</summary>
            <div className="status-list">
              {latestUploads.map((item) => (
                <div className="status-item" key={item.id}>
                  <strong>{item.original_filename}</strong>
                  <div>{item.status}</div>
                  <div className="subtle">{item.uploaded_at}</div>
                </div>
              ))}
            </div>
          </details>
        ) : null}
      </section>
    </>
  );
}

import { getLatestUploadStatuses, getUploadCoverageSummary } from "@/lib/uploads/status";
import { UploadForm } from "./upload-form";

export default async function UploadPage() {
  const [latestUploads, coverage] = await Promise.all([getLatestUploadStatuses(), getUploadCoverageSummary()]);
  const latestIngested = coverage?.latestIngestedFiles || [];
  const latestSummaryOnly = coverage?.latestSummaryOnlyFiles || [];

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Upload</p>
        <h1>Restore Hero corpus, inspect the cutoff date, then dump the next packet batch.</h1>
        <p className="subtle">
          The canonical Hero corpus is now the baseline. Use this dropbox-style intake to add everything after the current
          cutoff date in one shot, including large zip archives from new exports.
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

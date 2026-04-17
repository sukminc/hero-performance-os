import { getLatestUploadStatuses } from "@/lib/uploads/status";
import { UploadForm } from "./upload-form";

export default async function UploadPage() {
  const latestUploads = await getLatestUploadStatuses();

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Upload</p>
        <h1>Upload foundation is now wired into the canonical ingest path.</h1>
        <p className="subtle">
          This Phase 2 foundation accepts GG `.txt` session packets, runs duplicate-safe ingest through the existing Python
          pipeline, and shows recent upload statuses.
        </p>
        <UploadForm />
      </section>
      <section className="page-card">
        <h3>Latest Upload Status</h3>
        {latestUploads.length ? (
          <div className="status-list">
            {latestUploads.map((item) => (
              <div className="status-item" key={item.id}>
                <strong>{item.original_filename}</strong>
                <div>{item.status}</div>
                <div className="subtle">{item.uploaded_at}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="subtle">No upload history yet.</p>
        )}
      </section>
    </>
  );
}

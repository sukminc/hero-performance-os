"use client";

import { useActionState } from "react";
import { uploadGgPacket } from "./actions";

const initialState = null;

export function UploadForm() {
  const [state, formAction, pending] = useActionState(uploadGgPacket, initialState);
  const resultRows = state?.results || [];
  const groupedBySource = resultRows.reduce<Record<string, typeof resultRows>>((acc, item) => {
    acc[item.sourceName] = acc[item.sourceName] || [];
    acc[item.sourceName].push(item);
    return acc;
  }, {});

  return (
    <form action={formAction} className="input-grid">
      <div className="upload-dropzone">
        <div>
          <strong>Drop GG packets or zip dumps here</strong>
          <p className="subtle">
            You can attach multiple `.txt` files or one or more `.zip` archives. Each zip will be expanded and every GG
            packet inside will be ingested in one batch.
          </p>
        </div>
        <label className="upload-picker">
          <span>Select files</span>
          <input name="packet" type="file" accept=".txt,.zip" multiple />
        </label>
      </div>
      <button className="cta" type="submit" disabled={pending}>
        {pending ? "Uploading batch..." : "Upload batch"}
      </button>
      {state ? (
        <div className="page-card">
          <strong>{state.ok ? "Upload Status" : "Upload Error"}</strong>
          <p className="subtle">{state.message}</p>
          {state.summary ? (
            <div className="status-list">
              <div className="status-item">
                <strong>Batch summary</strong>
                <div>{state.summary.sourceFileCount} source files attached</div>
                <div>{state.summary.extractedPacketCount} packets expanded</div>
                <div>{state.summary.ingestedCount} newly ingested</div>
                <div>{state.summary.duplicateCount} duplicates skipped</div>
                <div className="subtle">
                  {state.summary.duplicateIngestedCount} duplicated hand-packets,{" "}
                  {state.summary.duplicateSummaryOnlyCount} duplicated summary-only files
                </div>
                <div>{state.summary.summaryOnlyCount} summary-only files skipped</div>
                <div>{state.summary.failedCount} failures</div>
              </div>
            </div>
          ) : null}
          {Object.entries(groupedBySource).length ? (
            <div className="status-list">
              {Object.entries(groupedBySource).map(([sourceName, items]) => (
                <div className="status-item" key={sourceName}>
                  <strong>{sourceName}</strong>
                  <div className="subtle">
                    {items.filter((item) => item.status === "ingested").length} ingested,{" "}
                    {items.filter((item) => item.status === "skipped_summary_only").length} summary-only skipped,{" "}
                    {items.filter(
                      (item) => item.status === "duplicate_skipped" && item.duplicate_of_status === "ingested"
                    ).length} duplicated hand-packets,{" "}
                    {items.filter(
                      (item) => item.status === "duplicate_skipped" && item.duplicate_of_status === "skipped_summary_only"
                    ).length} duplicated summary-only files
                  </div>
                  <details className="upload-details">
                    <summary>Inspect rows</summary>
                    <pre className="status-pre">{JSON.stringify(items, null, 2)}</pre>
                  </details>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </form>
  );
}

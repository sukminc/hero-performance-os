"use client";

import { useActionState } from "react";
import { uploadGgPacket } from "./actions";

const initialState = null;

export function UploadForm() {
  const [state, formAction, pending] = useActionState(uploadGgPacket, initialState);

  return (
    <form action={formAction} className="input-grid">
      <label>
        GG Session Packet
        <input name="packet" type="file" accept=".txt" />
      </label>
      <button className="cta" type="submit" disabled={pending}>
        {pending ? "Uploading..." : "Upload GG Packet"}
      </button>
      {state ? (
        <div className="page-card">
          <strong>{state.ok ? "Upload Status" : "Upload Error"}</strong>
          <p className="subtle">{state.message}</p>
          {state.result ? (
            <pre className="status-pre">{JSON.stringify(state.result, null, 2)}</pre>
          ) : null}
        </div>
      ) : null}
    </form>
  );
}

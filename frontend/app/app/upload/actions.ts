"use server";

import { ingestUploadedFiles, type UploadActionResult } from "@/lib/uploads/ingest";
import { getViewerContext } from "@/lib/viewer/session";

export async function uploadGgPacket(
  _prevState: UploadActionResult | null,
  formData: FormData
): Promise<UploadActionResult> {
  const files = formData
    .getAll("packet")
    .filter((entry): entry is File => entry instanceof File && entry.size > 0);

  if (!files.length) {
    return { ok: false, message: "No file was attached." };
  }

  const viewer = await getViewerContext();
  return ingestUploadedFiles(files, viewer.playerId);
}

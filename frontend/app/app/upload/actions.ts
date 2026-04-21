"use server";

import { ingestUploadedFiles, type UploadActionResult } from "@/lib/uploads/ingest";

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

  return ingestUploadedFiles(files);
}

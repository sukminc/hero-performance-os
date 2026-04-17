"use server";

import { ingestUploadedFile, type UploadActionResult } from "@/lib/uploads/ingest";

export async function uploadGgPacket(
  _prevState: UploadActionResult | null,
  formData: FormData
): Promise<UploadActionResult> {
  const file = formData.get("packet");
  if (!(file instanceof File)) {
    return { ok: false, message: "No file was attached." };
  }

  return ingestUploadedFile(file);
}

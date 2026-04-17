import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveIngestScriptPath, resolveRepoRoot, resolveSqlitePath, resolveUploadTempDir } from "./runtime";

const execFileAsync = promisify(execFile);

export type UploadActionResult = {
  ok: boolean;
  message: string;
  result?: {
    status: string;
    ingest_file_id: string;
    session_id: string | null;
    duplicate_of_file_id: string | null;
    parsed_hand_count: number;
    evidence_count: number;
    memory_count: number;
  };
};

export async function ingestUploadedFile(file: File): Promise<UploadActionResult> {
  if (!file || file.size === 0) {
    return { ok: false, message: "Please choose a non-empty GG text file." };
  }

  if (!file.name.toLowerCase().endsWith(".txt")) {
    return { ok: false, message: "Only GG .txt session packets are supported in Phase 2 foundation." };
  }

  const uploadDir = resolveUploadTempDir();
  await mkdir(uploadDir, { recursive: true });

  const safeName = `${randomUUID()}-${file.name.replace(/[^a-zA-Z0-9._-]/g, "_")}`;
  const destination = path.join(uploadDir, safeName);
  const bytes = Buffer.from(await file.arrayBuffer());
  await writeFile(destination, bytes);

  try {
    const { stdout } = await execFileAsync(
      "python3",
      [resolveIngestScriptPath(), "--file", destination],
      {
        cwd: resolveRepoRoot(),
        env: {
          ...process.env,
          PYTHONPATH: resolveRepoRoot(),
          SQLITE_DB_PATH: resolveSqlitePath(),
          V2_STORAGE_BACKEND: "sqlite"
        }
      }
    );

    const parsed = JSON.parse(stdout.trim());
    return {
      ok: true,
      message: parsed.status === "duplicate_skipped" ? "Duplicate upload safely skipped." : "Upload ingested successfully.",
      result: parsed
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown upload failure.";
    return { ok: false, message };
  }
}

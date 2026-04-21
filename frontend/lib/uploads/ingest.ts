import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import {
  resolveIngestScriptPath,
  resolveRepoRoot,
  resolveSqlitePath,
  resolveUploadTempDir,
  resolveZipExpandScriptPath
} from "./runtime";

const execFileAsync = promisify(execFile);

export type SingleIngestResult = {
  sourceName: string;
  uploadedName: string;
  status: string;
  ingest_file_id: string;
  session_id: string | null;
  duplicate_of_file_id: string | null;
  duplicate_of_status: string | null;
  parsed_hand_count: number;
  evidence_count: number;
  memory_count: number;
};

export type UploadActionResult = {
  ok: boolean;
  message: string;
  summary?: {
    sourceFileCount: number;
    extractedPacketCount: number;
    ingestedCount: number;
    duplicateCount: number;
    duplicateIngestedCount: number;
    duplicateSummaryOnlyCount: number;
    summaryOnlyCount: number;
    failedCount: number;
  };
  results?: SingleIngestResult[];
};

async function saveBrowserFile(file: File): Promise<{ destination: string; safeName: string }> {
  const uploadDir = resolveUploadTempDir();
  await mkdir(uploadDir, { recursive: true });

  const safeName = `${randomUUID()}-${file.name.replace(/[^a-zA-Z0-9._-]/g, "_")}`;
  const destination = path.join(uploadDir, safeName);
  const bytes = Buffer.from(await file.arrayBuffer());
  await writeFile(destination, bytes);
  return { destination, safeName };
}

async function expandZipArchive(zipPath: string, sourceName: string): Promise<string[]> {
  const expandDir = path.join(resolveUploadTempDir(), "expanded", randomUUID());
  await mkdir(expandDir, { recursive: true });
  const { stdout } = await execFileAsync("python3", [resolveZipExpandScriptPath(), "--zip", zipPath, "--out", expandDir], {
    cwd: resolveRepoRoot(),
    env: {
      ...process.env,
      PYTHONPATH: resolveRepoRoot()
    }
  });

  const parsed = JSON.parse(stdout.trim()) as { extracted_files?: string[] };
  const extractedFiles = parsed.extracted_files || [];
  if (!extractedFiles.length) {
    throw new Error(`${sourceName}: no .txt GG packets were found inside the zip archive.`);
  }
  return extractedFiles;
}

async function ingestPacketFile(packetPath: string, sourceName: string): Promise<SingleIngestResult> {
  const { stdout } = await execFileAsync("python3", [resolveIngestScriptPath(), "--file", packetPath], {
    cwd: resolveRepoRoot(),
    env: {
      ...process.env,
      PYTHONPATH: resolveRepoRoot(),
      SQLITE_DB_PATH: resolveSqlitePath(),
      V2_STORAGE_BACKEND: "sqlite"
    }
  });

  const parsed = JSON.parse(stdout.trim());
  return {
    sourceName,
    uploadedName: path.basename(packetPath),
    status: parsed.status,
    ingest_file_id: parsed.ingest_file_id,
    session_id: parsed.session_id,
    duplicate_of_file_id: parsed.duplicate_of_file_id,
    duplicate_of_status: parsed.duplicate_of_status ?? null,
    parsed_hand_count: parsed.parsed_hand_count,
    evidence_count: parsed.evidence_count,
    memory_count: parsed.memory_count
  };
}

export async function ingestUploadedFiles(files: File[]): Promise<UploadActionResult> {
  const validFiles = files.filter((file) => file && file.size > 0);
  if (!validFiles.length) {
    return { ok: false, message: "Attach one or more GG packet files or zip archives." };
  }

  const unsupported = validFiles.filter((file) => {
    const lower = file.name.toLowerCase();
    return !lower.endsWith(".txt") && !lower.endsWith(".zip");
  });
  if (unsupported.length) {
    return {
      ok: false,
      message: `Unsupported file types: ${unsupported.map((file) => file.name).join(", ")}. Use .txt or .zip.`
    };
  }

  const packetPaths: Array<{ packetPath: string; sourceName: string }> = [];
  try {
    for (const file of validFiles) {
      const { destination } = await saveBrowserFile(file);
      const lower = file.name.toLowerCase();
      if (lower.endsWith(".zip")) {
        const extracted = await expandZipArchive(destination, file.name);
        extracted.forEach((packetPath) => packetPaths.push({ packetPath, sourceName: file.name }));
      } else {
        packetPaths.push({ packetPath: destination, sourceName: file.name });
      }
    }

    const results: SingleIngestResult[] = [];
    for (const item of packetPaths) {
      try {
        results.push(await ingestPacketFile(item.packetPath, item.sourceName));
      } catch (error) {
        results.push({
          sourceName: item.sourceName,
          uploadedName: path.basename(item.packetPath),
          status: "failed",
          ingest_file_id: "",
          session_id: null,
          duplicate_of_file_id: null,
          duplicate_of_status: null,
          parsed_hand_count: 0,
          evidence_count: 0,
          memory_count: 0
        });
        if (error instanceof Error) {
          results[results.length - 1].status = `failed: ${error.message}`;
        }
      }
    }

    const ingestedCount = results.filter((item) => item.status === "ingested").length;
    const duplicateCount = results.filter((item) => item.status === "duplicate_skipped").length;
    const duplicateIngestedCount = results.filter(
      (item) => item.status === "duplicate_skipped" && item.duplicate_of_status === "ingested"
    ).length;
    const duplicateSummaryOnlyCount = results.filter(
      (item) => item.status === "duplicate_skipped" && item.duplicate_of_status === "skipped_summary_only"
    ).length;
    const summaryOnlyCount = results.filter((item) => item.status === "skipped_summary_only").length;
    const failedCount = results.filter((item) => item.status.startsWith("failed")).length;
    return {
      ok: failedCount === 0,
      message:
        failedCount > 0
          ? "Some files failed during upload. Review the batch results below."
          : `Batch processed successfully. ${ingestedCount} new packets ingested, ${duplicateCount} duplicates skipped (${duplicateIngestedCount} hand-packet duplicates, ${duplicateSummaryOnlyCount} summary-only duplicates), ${summaryOnlyCount} summary-only files skipped.`,
      summary: {
        sourceFileCount: validFiles.length,
        extractedPacketCount: packetPaths.length,
        ingestedCount,
        duplicateCount,
        duplicateIngestedCount,
        duplicateSummaryOnlyCount,
        summaryOnlyCount,
        failedCount
      },
      results
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown upload failure.";
    return { ok: false, message };
  }
}

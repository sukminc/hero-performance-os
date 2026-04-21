import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "./runtime";

const execFileAsync = promisify(execFile);

export type UploadStatusRow = {
  id: string;
  original_filename: string;
  status: string;
  uploaded_at: string;
  raw_metadata: Record<string, unknown>;
};

export type UploadCoverageSummary = {
  totalSessions: number;
  totalHands: number;
  totalMemoryItems: number;
  firstSessionAt: string | null;
  lastSessionAt: string | null;
  firstUploadAt: string | null;
  lastUploadAt: string | null;
  latestFiles: Array<{
    original_filename: string;
    uploaded_at: string;
  }>;
  latestIngestedFiles: Array<{
    original_filename: string;
    uploaded_at: string;
  }>;
  latestSummaryOnlyFiles: Array<{
    original_filename: string;
    uploaded_at: string;
  }>;
};

export async function getLatestUploadStatuses(limit = 5): Promise<UploadStatusRow[]> {
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import sqlite3, os, json",
          "conn = sqlite3.connect(os.environ['SQLITE_DB_PATH'])",
          "conn.row_factory = sqlite3.Row",
          `rows = conn.execute(\"select id, original_filename, status, uploaded_at, raw_metadata from ingest_files order by uploaded_at desc limit ${limit}\").fetchall()`,
          "print(json.dumps([dict(r) for r in rows]))"
        ].join("; ")
      ],
      {
        cwd: resolveRepoRoot(),
        env: {
          ...process.env,
          SQLITE_DB_PATH: resolveSqlitePath()
        }
      }
    );

    return JSON.parse(stdout.trim());
  } catch {
    return [];
  }
}

export async function getUploadCoverageSummary(): Promise<UploadCoverageSummary | null> {
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import sqlite3, os, json",
          "conn = sqlite3.connect(os.environ['SQLITE_DB_PATH'])",
          "conn.row_factory = sqlite3.Row",
          "payload = {'totalSessions': conn.execute(\"select count(*) from sessions\").fetchone()[0], 'totalHands': conn.execute(\"select count(*) from hands\").fetchone()[0], 'totalMemoryItems': conn.execute(\"select count(*) from memory_items\").fetchone()[0], 'firstSessionAt': conn.execute(\"select min(started_at) from sessions\").fetchone()[0], 'lastSessionAt': conn.execute(\"select max(started_at) from sessions\").fetchone()[0], 'firstUploadAt': conn.execute(\"select min(uploaded_at) from ingest_files\").fetchone()[0], 'lastUploadAt': conn.execute(\"select max(uploaded_at) from ingest_files\").fetchone()[0], 'latestFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files order by uploaded_at desc limit 5\").fetchall()], 'latestIngestedFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files where status = 'ingested' order by uploaded_at desc limit 5\").fetchall()], 'latestSummaryOnlyFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files where status = 'skipped_summary_only' order by uploaded_at desc limit 5\").fetchall()]}",
          "print(json.dumps(payload))"
        ].join("; ")
      ],
      {
        cwd: resolveRepoRoot(),
        env: {
          ...process.env,
          SQLITE_DB_PATH: resolveSqlitePath()
        }
      }
    );

    return JSON.parse(stdout.trim());
  } catch {
    return null;
  }
}

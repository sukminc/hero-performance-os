import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "./runtime";

const execFileAsync = promisify(execFile);

function requireBackendService() {
  return ["1", "true", "yes", "on"].includes((process.env.OPB_REQUIRE_BACKEND_SERVICE || "").toLowerCase());
}

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

export async function getLatestUploadStatuses(playerId: string | null, limit = 5): Promise<UploadStatusRow[]> {
  if (!playerId) {
    return [];
  }
  if (requireBackendService()) {
    return [];
  }
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import sqlite3, os, json",
          "conn = sqlite3.connect(os.environ['SQLITE_DB_PATH'])",
          "conn.row_factory = sqlite3.Row",
          `rows = conn.execute(\"select id, original_filename, status, uploaded_at, raw_metadata from ingest_files where player_id = ? order by uploaded_at desc limit ${limit}\", (${JSON.stringify(playerId)},)).fetchall()`,
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

export async function getUploadCoverageSummary(playerId: string | null): Promise<UploadCoverageSummary | null> {
  if (!playerId) {
    return null;
  }
  if (requireBackendService()) {
    return null;
  }
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import sqlite3, os, json",
          "conn = sqlite3.connect(os.environ['SQLITE_DB_PATH'])",
          "conn.row_factory = sqlite3.Row",
          `player_id = ${JSON.stringify(playerId)}`,
          "session_ids = [r[0] for r in conn.execute(\"select id from sessions where player_id = ?\", (player_id,)).fetchall()]",
          "hand_count = conn.execute(\"select count(*) from hands where session_id in (select id from sessions where player_id = ?)\", (player_id,)).fetchone()[0]",
          "payload = {'totalSessions': conn.execute(\"select count(*) from sessions where player_id = ?\", (player_id,)).fetchone()[0], 'totalHands': hand_count, 'totalMemoryItems': conn.execute(\"select count(*) from memory_items where player_id = ?\", (player_id,)).fetchone()[0], 'firstSessionAt': conn.execute(\"select min(started_at) from sessions where player_id = ?\", (player_id,)).fetchone()[0], 'lastSessionAt': conn.execute(\"select max(started_at) from sessions where player_id = ?\", (player_id,)).fetchone()[0], 'firstUploadAt': conn.execute(\"select min(uploaded_at) from ingest_files where player_id = ?\", (player_id,)).fetchone()[0], 'lastUploadAt': conn.execute(\"select max(uploaded_at) from ingest_files where player_id = ?\", (player_id,)).fetchone()[0], 'latestFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files where player_id = ? order by uploaded_at desc limit 5\", (player_id,)).fetchall()], 'latestIngestedFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files where player_id = ? and status = 'ingested' order by uploaded_at desc limit 5\", (player_id,)).fetchall()], 'latestSummaryOnlyFiles': [dict(r) for r in conn.execute(\"select original_filename, uploaded_at from ingest_files where player_id = ? and status = 'skipped_summary_only' order by uploaded_at desc limit 5\", (player_id,)).fetchall()]}",
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

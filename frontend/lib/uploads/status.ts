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

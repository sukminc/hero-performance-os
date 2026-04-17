import path from "node:path";

export function resolveRepoRoot() {
  return path.resolve(process.cwd(), "..");
}

export function resolveSqlitePath() {
  return process.env.OPB_SQLITE_DB_PATH || path.join(resolveRepoRoot(), "data", "hero_v2.sqlite3");
}

export function resolveUploadTempDir() {
  return process.env.OPB_UPLOAD_TMP_DIR || path.join(resolveRepoRoot(), "data", "tmp_uploads_public");
}

export function resolveIngestScriptPath() {
  return path.join(resolveRepoRoot(), "core", "ingest", "ingest_jobs.py");
}

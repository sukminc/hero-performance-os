import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

async function runPython(code: string) {
  const { stdout } = await execFileAsync("python3", ["-c", code], {
    cwd: resolveRepoRoot(),
    env: {
      ...process.env,
      PYTHONPATH: resolveRepoRoot(),
      SQLITE_DB_PATH: resolveSqlitePath(),
      V2_STORAGE_BACKEND: "sqlite"
    }
  });
  return JSON.parse(stdout.trim());
}

function toPythonLiteral(value: string) {
  return JSON.stringify(value);
}

export async function getPublicTodaySurface(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.today import get_today_payload",
        `payload = get_today_payload(player_id=${toPythonLiteral(playerId)})`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getPublicReviewSurface(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from core.storage.repositories import V2Repository",
        "from core.surfaces.session_lab import build_session_lab_payload",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `player_id = ${toPythonLiteral(playerId)}`,
        "session_id = repo.fetch_latest_session_id(player_id)",
        "payload = build_session_lab_payload(repo, player_id, session_id) if session_id else None",
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getPublicBrainSurface(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from core.storage.repositories import V2Repository",
        "from core.surfaces.interpretation_summary import build_interpretation_summary",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `player_id = ${toPythonLiteral(playerId)}`,
        "memory = repo.fetch_memory_items(player_id, statuses=['active','baseline','watch'])",
        "payload = build_interpretation_summary(memory)",
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getConvictionReviewSummary(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.conviction_review import get_conviction_review_payload",
        `payload = get_conviction_review_payload(player_id=${toPythonLiteral(playerId)}, window='all')`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getTimingStackSummary(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.timing_stack_review import get_timing_stack_review_payload",
        `payload = get_timing_stack_review_payload(player_id=${toPythonLiteral(playerId)}, window='all')`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getHudTrendSummary(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.hud_trend import get_hud_trend_payload",
        `payload = get_hud_trend_payload(player_id=${toPythonLiteral(playerId)}, window='90d')`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getFieldEcologySummary(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.field_ecology import get_field_ecology_payload",
        `payload = get_field_ecology_payload(player_id=${toPythonLiteral(playerId)}, window='90d')`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

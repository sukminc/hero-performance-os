import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

function getBackendBaseUrl() {
  return process.env.OPB_BACKEND_BASE_URL?.replace(/\/+$/, "") || "";
}

function getBackendHeaders() {
  const token = process.env.OPB_BACKEND_API_TOKEN?.trim();
  return token ? { Authorization: `Bearer ${token}` } : undefined;
}

function requireBackendService() {
  return ["1", "true", "yes", "on"].includes((process.env.OPB_REQUIRE_BACKEND_SERVICE || "").toLowerCase());
}

async function getBackendJson(path: string) {
  const baseUrl = getBackendBaseUrl();
  if (!baseUrl) {
    return null;
  }
  const response = await fetch(`${baseUrl}${path}`, {
    cache: "no-store",
    headers: getBackendHeaders()
  });
  if (!response.ok) {
    throw new Error(`Backend service returned ${response.status}`);
  }
  return response.json();
}

async function runPython(code: string) {
  const { stdout } = await execFileAsync("python3", ["-c", code], {
    cwd: resolveRepoRoot(),
    maxBuffer: 64 * 1024 * 1024,
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
    const servicePayload = await getBackendJson(`/v1/players/${encodeURIComponent(playerId)}/today`);
    if (servicePayload?.ok) {
      return servicePayload.data;
    }
  } catch (error) {
    if (requireBackendService()) {
      throw error;
    }
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
        "from core.surfaces.session_lab import build_session_lab_payload",
        "from core.surfaces.tournament_result_signals import build_tournament_result_signals",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `player_id = ${toPythonLiteral(playerId)}`,
        "memory = repo.fetch_memory_items(player_id, statuses=['active','baseline','watch'])",
        "payload = build_interpretation_summary(memory)",
        "session_id = repo.fetch_latest_session_id(player_id)",
        "payload['latest_result_context'] = build_session_lab_payload(repo, player_id, session_id).get('result_context') if session_id else None",
        "payload['tournament_result_signals'] = build_tournament_result_signals(repo.fetch_tournament_results(player_id, limit=200))",
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

export async function getHeroBaselineMatrix(playerId: string | null, selectedHand = "66") {
  if (!playerId) {
    return null;
  }
  try {
    const params = new URLSearchParams({ window: "all", selected_hand: selectedHand });
    const servicePayload = await getBackendJson(`/v1/players/${encodeURIComponent(playerId)}/matrix?${params.toString()}`);
    if (servicePayload?.ok) {
      return servicePayload.data;
    }
  } catch (error) {
    if (requireBackendService()) {
      throw error;
    }
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.hand_matrix import get_hand_matrix_payload",
        `payload = get_hand_matrix_payload(player_id=${toPythonLiteral(playerId)}, window='all', selected_hand=${toPythonLiteral(selectedHand)})`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getHeroBaselineQuiz(playerId: string | null, quizDate?: string) {
  if (!playerId) {
    return null;
  }
  const dateParam =
    quizDate ||
    new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/Toronto",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date());
  try {
    const params = new URLSearchParams({ date: dateParam });
    const servicePayload = await getBackendJson(`/v1/players/${encodeURIComponent(playerId)}/matrix/quiz?${params.toString()}`);
    if (servicePayload?.ok) {
      return servicePayload.data;
    }
  } catch (error) {
    if (requireBackendService()) {
      throw error;
    }
  }
  try {
    return await runPython(
      [
        "import json",
        "from app.api.matrix_quiz import build_matrix_quiz_payload",
        `payload = build_matrix_quiz_payload(player_id=${toPythonLiteral(playerId)}, quiz_date=${toPythonLiteral(dateParam)})`,
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

export async function getBigWinReview(playerId: string | null, tournamentId = "6408385") {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from core.storage.repositories import V2Repository",
        "from core.surfaces.big_win_review import build_big_win_review_payload",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `payload = build_big_win_review_payload(repo, ${toPythonLiteral(playerId)}, ${toPythonLiteral(tournamentId)})`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getAofImplementationProfile(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from core.storage.repositories import V2Repository",
        "from core.surfaces.aof_implementation_profile import build_aof_implementation_profile",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `payload = build_aof_implementation_profile(repo, ${toPythonLiteral(playerId)})`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

export async function getAofDecisionSystem(playerId: string | null) {
  if (!playerId) {
    return null;
  }
  try {
    return await runPython(
      [
        "import json",
        "from core.storage.repositories import V2Repository",
        "from core.surfaces.aof_decision_system import build_aof_decision_system",
        "repo = V2Repository()",
        "repo.ensure_schema()",
        `payload = build_aof_decision_system(repo, ${toPythonLiteral(playerId)})`,
        "print(json.dumps(payload, default=str))"
      ].join("; ")
    );
  } catch {
    return null;
  }
}

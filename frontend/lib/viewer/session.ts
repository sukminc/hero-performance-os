import { cookies } from "next/headers";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { getCurrentUser } from "@/lib/auth/supabase";
import { isDevLoginEnabled } from "@/lib/auth/dev-mode";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

const HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111";

function parseCsvEnv(value: string | undefined) {
  return new Set(
    (value || "")
      .split(",")
      .map((item) => item.trim().toLowerCase())
      .filter(Boolean)
  );
}

function normalizeEmail(value: string | null | undefined) {
  return value?.trim().toLowerCase() || null;
}

async function resolveCanonicalViewerAccess(authProviderUserId: string | null, email: string | null) {
  if (!authProviderUserId && !email) {
    return null;
  }
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import json",
          "from core.auth.viewer_access import resolve_viewer_access",
          `payload = resolve_viewer_access('supabase', ${JSON.stringify(authProviderUserId)}, ${JSON.stringify(email)})`,
          "print(json.dumps(payload, default=str))",
        ].join("; "),
      ],
      {
        cwd: resolveRepoRoot(),
        env: {
          ...process.env,
          PYTHONPATH: resolveRepoRoot(),
          SQLITE_DB_PATH: resolveSqlitePath(),
          V2_STORAGE_BACKEND: "sqlite",
        },
      }
    );
    return JSON.parse(stdout.trim());
  } catch {
    return null;
  }
}

type ViewerRole = "user" | "operator";
type PlayerScope = "none" | "self" | "hero" | "all";

export async function getViewerContext() {
  const cookieStore = await cookies();
  const currentUser = await getCurrentUser();
  const devSessionToken = cookieStore.get("sb-auth-token")?.value || null;
  const heroUserId = process.env.OPB_HERO_SUPABASE_USER_ID?.trim() || null;
  const heroEmail = normalizeEmail(process.env.OPB_HERO_SUPABASE_EMAIL);
  const operatorUserIds = parseCsvEnv(process.env.OPB_OPERATOR_SUPABASE_USER_IDS);
  const operatorEmails = parseCsvEnv(process.env.OPB_OPERATOR_EMAILS);
  const currentUserId = currentUser?.id || null;
  const currentUserEmail = normalizeEmail(currentUser?.email);
  const devLoginEnabled = isDevLoginEnabled();
  const canonicalAccess = await resolveCanonicalViewerAccess(currentUserId, currentUserEmail);

  if (canonicalAccess?.resolved) {
    return {
      role: canonicalAccess.role as ViewerRole,
      playerScope: canonicalAccess.player_scope as PlayerScope,
      playerId: canonicalAccess.player_id as string | null,
      canSeeOperatorDepth: Boolean(canonicalAccess.can_see_operator_depth),
      isAuthenticated: Boolean(currentUser || (devLoginEnabled && cookieStore.get("sb-auth-token"))),
      authUserId: currentUserId,
      authEmail: currentUserEmail,
      ownershipResolved: Boolean(canonicalAccess.ownership_resolved),
      ownershipSource: canonicalAccess.ownership_source as string,
    };
  }

  const isDevOperator = devLoginEnabled && devSessionToken === "dev-operator-session";
  const isDevUser = devLoginEnabled && devSessionToken === "dev-user-session";
  const isMappedOperator =
    Boolean(currentUserId && operatorUserIds.has(currentUserId.toLowerCase())) ||
    Boolean(currentUserEmail && operatorEmails.has(currentUserEmail));
  const isOperator = isDevOperator || isMappedOperator;
  const role: ViewerRole = isOperator ? "operator" : "user";

  const isHeroOwner =
    Boolean(currentUserId && heroUserId && currentUserId === heroUserId) ||
    Boolean(currentUserEmail && heroEmail && currentUserEmail === heroEmail) ||
    isDevUser;

  const playerId = isOperator || isHeroOwner ? HERO_PLAYER_ID : null;
  const playerScope: PlayerScope = isOperator ? "all" : isHeroOwner ? "self" : "none";

  return {
    role,
    playerScope,
    playerId,
    canSeeOperatorDepth: isOperator,
    isAuthenticated: Boolean(currentUser || (devLoginEnabled && cookieStore.get("sb-auth-token"))),
    authUserId: currentUserId,
    authEmail: currentUserEmail,
    ownershipResolved: Boolean(isOperator || isHeroOwner),
    ownershipSource: isOperator ? "operator_mapping" : isHeroOwner ? "hero_mapping" : "unmapped_user"
  };
}

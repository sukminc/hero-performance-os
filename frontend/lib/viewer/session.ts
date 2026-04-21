import { cookies } from "next/headers";
import { getCurrentUser } from "@/lib/auth/supabase";

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

type ViewerRole = "user" | "operator";
type PlayerScope = "none" | "self" | "hero" | "all";

export async function getViewerContext() {
  const cookieStore = await cookies();
  const currentUser = await getCurrentUser();
  const roleCookie = cookieStore.get("opb_role")?.value;
  const heroUserId = process.env.OPB_HERO_SUPABASE_USER_ID?.trim() || null;
  const heroEmail = normalizeEmail(process.env.OPB_HERO_SUPABASE_EMAIL);
  const operatorUserIds = parseCsvEnv(process.env.OPB_OPERATOR_SUPABASE_USER_IDS);
  const operatorEmails = parseCsvEnv(process.env.OPB_OPERATOR_EMAILS);
  const currentUserId = currentUser?.id || null;
  const currentUserEmail = normalizeEmail(currentUser?.email);
  const devLoginEnabled = process.env.OPB_ENABLE_DEV_LOGIN === "1";
  const isDevOperator = devLoginEnabled && roleCookie === "operator";
  const isMappedOperator =
    Boolean(currentUserId && operatorUserIds.has(currentUserId.toLowerCase())) ||
    Boolean(currentUserEmail && operatorEmails.has(currentUserEmail));
  const isOperator = isDevOperator || isMappedOperator;
  const role: ViewerRole = isOperator ? "operator" : "user";

  const isHeroOwner =
    Boolean(currentUserId && heroUserId && currentUserId === heroUserId) ||
    Boolean(currentUserEmail && heroEmail && currentUserEmail === heroEmail) ||
    (devLoginEnabled && roleCookie === "user");

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

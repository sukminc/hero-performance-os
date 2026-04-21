import { cookies } from "next/headers";

export async function getViewerContext() {
  const cookieStore = await cookies();
  const role = cookieStore.get("opb_role")?.value === "operator" ? "operator" : "user";

  return {
    role,
    playerScope: "hero",
    playerId: "4c9d1e29-1f6b-4e5f-92da-111111111111",
    canSeeOperatorDepth: role === "operator"
  };
}

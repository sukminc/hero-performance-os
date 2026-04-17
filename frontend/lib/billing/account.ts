import { cookies } from "next/headers";
import { getPlanDefinition, type PlanKey } from "./plans";

const PLAN_COOKIE = "opb_plan";

export async function getCurrentPlan() {
  const cookieStore = await cookies();
  const planKey = (cookieStore.get(PLAN_COOKIE)?.value as PlanKey | undefined) || "free_beta";
  return getPlanDefinition(planKey);
}

export async function getEntitlementSummary() {
  const plan = await getCurrentPlan();
  return {
    planKey: plan.key,
    planLabel: plan.label,
    uploadLimit: plan.uploadLimit,
    premiumReview: plan.gates.premiumReview,
    premiumBrain: plan.gates.premiumBrain,
    operatorPatterns: plan.gates.operatorPatterns
  };
}

export type PlanKey = "free_beta" | "pro_monthly";

export type PlanDefinition = {
  key: PlanKey;
  label: string;
  priceLabel: string;
  uploadLimit: number;
  includes: string[];
  gates: {
    premiumReview: boolean;
    premiumBrain: boolean;
    operatorPatterns: boolean;
  };
};

export const PLAN_DEFINITIONS: PlanDefinition[] = [
  {
    key: "free_beta",
    label: "Free Beta",
    priceLabel: "$0",
    uploadLimit: 10,
    includes: [
      "Account access",
      "GG packet upload",
      "Today surface",
      "Basic Review / Brain"
    ],
    gates: {
      premiumReview: false,
      premiumBrain: false,
      operatorPatterns: false
    }
  },
  {
    key: "pro_monthly",
    label: "Pro Monthly",
    priceLabel: "$39 / month",
    uploadLimit: 250,
    includes: [
      "Higher upload limit",
      "Premium Review depth",
      "Premium Brain depth",
      "Pattern and study access"
    ],
    gates: {
      premiumReview: true,
      premiumBrain: true,
      operatorPatterns: true
    }
  }
];

export function getPlanDefinition(planKey: string | undefined | null) {
  return PLAN_DEFINITIONS.find((plan) => plan.key === planKey) || PLAN_DEFINITIONS[0];
}

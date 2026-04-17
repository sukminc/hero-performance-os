export const BILLING_PROVIDER = "stripe";

export function getStripeConfig() {
  return {
    publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "",
    monthlyPriceId: process.env.STRIPE_PRO_MONTHLY_PRICE_ID || "",
    webhookSecretPresent: Boolean(process.env.STRIPE_WEBHOOK_SECRET)
  };
}

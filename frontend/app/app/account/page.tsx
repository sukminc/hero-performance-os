import { getEntitlementSummary } from "@/lib/billing/account";
import { getStripeConfig, BILLING_PROVIDER } from "@/lib/billing/stripe";

export default async function AccountPage() {
  const entitlement = await getEntitlementSummary();
  const stripe = getStripeConfig();

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Account</p>
        <h1>{entitlement.planLabel}</h1>
        <p className="subtle">
          Billing foundation is now active. Checkout is not wired yet, but plan state, entitlements, and Stripe configuration
          boundaries are in place.
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>Entitlements</h3>
          <pre className="status-pre">{JSON.stringify(entitlement, null, 2)}</pre>
        </article>
        <article className="page-card">
          <h3>Billing Provider</h3>
          <pre className="status-pre">
            {JSON.stringify(
              {
                provider: BILLING_PROVIDER,
                publishableKeyPresent: Boolean(stripe.publishableKey),
                monthlyPriceIdPresent: Boolean(stripe.monthlyPriceId),
                webhookSecretPresent: stripe.webhookSecretPresent
              },
              null,
              2
            )}
          </pre>
        </article>
      </section>
    </>
  );
}

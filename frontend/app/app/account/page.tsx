import Link from "next/link";
import { getCurrentPlan, getEntitlementSummary } from "@/lib/billing/account";
import { PLAN_DEFINITIONS } from "@/lib/billing/plans";
import { getStripeConfig } from "@/lib/billing/stripe";
import { getViewerContext } from "@/lib/viewer/session";

export default async function AccountPage() {
  const entitlement = await getEntitlementSummary();
  const currentPlan = await getCurrentPlan();
  const stripe = getStripeConfig();
  const viewer = await getViewerContext();
  const stripeConnected = Boolean(stripe.publishableKey && stripe.monthlyPriceId);

  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Account</p>
        <h1>{entitlement.planLabel}</h1>
        <p className="subtle">
          You&apos;re on the {entitlement.planLabel} plan with up to {entitlement.uploadLimit} uploads.
          {stripeConnected
            ? " Upgrade is wired up; checkout flow goes through Stripe."
            : " Checkout is not live yet — billing is in foundation mode."}
        </p>
        <div className="dashboard-cta-row">
          <Link className="cta" href="/pricing">
            See plans
          </Link>
          <Link className="secondary-cta" href="/auth/logout">
            Log out
          </Link>
        </div>
      </section>

      <section className="grid two">
        {PLAN_DEFINITIONS.map((plan) => {
          const isCurrent = plan.key === currentPlan.key;
          return (
            <article className={`page-card plan-card${isCurrent ? " plan-card-current" : ""}`} key={plan.key}>
              <div className="section-heading-row">
                <div>
                  <p className="eyebrow">{plan.label}</p>
                  <h3>{plan.priceLabel}</h3>
                </div>
                {isCurrent ? <span className="state-pill tone-good">Current plan</span> : null}
              </div>
              <ul className="prose-list">
                {plan.includes.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
              <div className="confidence-row">
                <span className="pill">{plan.uploadLimit} uploads / mo</span>
                {plan.gates.premiumReview ? <span className="pill">Premium Review</span> : null}
                {plan.gates.premiumBrain ? <span className="pill">Premium Brain</span> : null}
              </div>
            </article>
          );
        })}
      </section>

      <section className="page-card">
        <p className="eyebrow">Access</p>
        <h3>How your data is scoped</h3>
        <div className="status-list compact">
          <div className="status-item">
            <strong>Role</strong>
            <div className="subtle">{viewer.role === "operator" ? "Operator / admin" : "Standard player"}</div>
          </div>
          <div className="status-item">
            <strong>Player scope</strong>
            <div className="subtle">{viewer.playerScope}</div>
          </div>
          <div className="status-item">
            <strong>Ownership</strong>
            <div className="subtle">{viewer.ownershipResolved ? "Resolved" : "Unmapped"}</div>
            <div className="subtle">{viewer.ownershipSource}</div>
          </div>
        </div>
        <p className="subtle">
          Standard players only see their own read. Operator accounts can inspect deeper internals through the operator
          console.
        </p>
      </section>
    </>
  );
}

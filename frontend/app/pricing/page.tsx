import { PLAN_DEFINITIONS } from "@/lib/billing/plans";

export default function PricingPage() {
  return (
    <main className="shell">
      <section className="page-card">
        <p className="eyebrow">Pricing</p>
        <h1>One Percent Better Poker pricing foundation is now defined.</h1>
        <p className="subtle">
          Billing provider is Stripe. This phase establishes plan shape and entitlement boundary before checkout wiring.
        </p>
      </section>
      <section className="grid two">
        {PLAN_DEFINITIONS.map((plan) => (
          <article className="page-card" key={plan.key}>
            <h2>{plan.label}</h2>
            <div className="metric">{plan.priceLabel}</div>
            <p className="subtle">Upload limit: {plan.uploadLimit}</p>
            <div className="status-list">
              {plan.includes.map((item) => (
                <div className="status-item" key={item}>
                  {item}
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

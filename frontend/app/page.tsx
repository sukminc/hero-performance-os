import Link from "next/link";

export default function LandingPage() {
  const devLoginEnabled = process.env.OPB_ENABLE_DEV_LOGIN === "1";

  return (
    <main className="shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">One Percent Better Poker</p>
          <h1>Serious tournament review that actually remembers your patterns.</h1>
          <p className="subtle">
            Upload GG session packets, keep cumulative memory across tournaments, and study Today / Review / Brain outputs
            built from your own repeated decisions instead of generic scolding.
          </p>
          <div className="cta-row">
            <Link className="cta" href="/signup">
              Start Private Beta
            </Link>
            <Link className="secondary-cta" href="/login">
              Log In
            </Link>
            {devLoginEnabled ? (
              <Link className="secondary-cta" href="/auth/dev-login?role=operator&next=/operator">
                Enter As Operator
              </Link>
            ) : null}
          </div>
        </div>
        <div className="page-card">
          <h3>Phase 1 foundation</h3>
          <div className="pill-row">
            <span className="pill">Supabase Auth</span>
            <span className="pill">Protected App Shell</span>
            <span className="pill">Operator Role Gate</span>
          </div>
          <p className="subtle">
            This is the public MVP shell foundation. Uploads, Today / Review / Brain, and billing will be layered in Phase
            2 onward.
          </p>
        </div>
      </section>
    </main>
  );
}

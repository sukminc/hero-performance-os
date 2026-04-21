import Link from "next/link";

export default function LoginPage() {
  const devLoginEnabled = process.env.OPB_ENABLE_DEV_LOGIN === "1";

  return (
    <main className="auth-wrap">
      <section className="auth-card">
        <p className="eyebrow">Login</p>
        <h1>Return to your performance workspace.</h1>
        <p className="subtle">
          Supabase Auth is the chosen Phase 1 provider. Form actions will be wired in the next auth task once environment
          credentials are configured.
        </p>
        <form className="input-grid">
          <label>
            Email
            <input type="email" placeholder="you@example.com" />
          </label>
          <label>
            Password
            <input type="password" placeholder="Password" />
          </label>
        </form>
        <div className="cta-row">
          {devLoginEnabled ? (
            <Link className="cta" href="/auth/dev-login?role=user&next=/app">
              Enter As User
            </Link>
          ) : null}
          {devLoginEnabled ? (
            <Link className="secondary-cta" href="/auth/dev-login?role=operator&next=/operator">
              Enter As Operator
            </Link>
          ) : null}
          <Link className="secondary-cta" href="/signup">
            Create Account
          </Link>
        </div>
      </section>
    </main>
  );
}

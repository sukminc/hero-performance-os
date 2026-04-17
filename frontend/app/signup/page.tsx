import Link from "next/link";

export default function SignupPage() {
  return (
    <main className="auth-wrap">
      <section className="auth-card">
        <p className="eyebrow">Signup</p>
        <h1>Create your private beta account.</h1>
        <p className="subtle">
          Accounts will later link to one or more poker player identities. Phase 1 keeps the shell lean so auth can land
          before upload and interpretation work.
        </p>
        <form className="input-grid">
          <label>
            Email
            <input type="email" placeholder="you@example.com" />
          </label>
          <label>
            Password
            <input type="password" placeholder="Create a password" />
          </label>
        </form>
        <div className="cta-row">
          <Link className="cta" href="/app">
            Continue To App Shell
          </Link>
          <Link className="secondary-cta" href="/login">
            Already have an account?
          </Link>
        </div>
      </section>
    </main>
  );
}

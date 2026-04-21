import Link from "next/link";
import { DemoApplyForm } from "./demo-apply-form";

export default function LandingPage() {
  const devLoginEnabled = process.env.OPB_ENABLE_DEV_LOGIN === "1";

  return (
    <main className="shell landing-shell">
      <section className="hero-stage">
        <div className="hero-copy">
          <p className="eyebrow">One Percent Better Poker</p>
          <h1>See your leaks. Keep what works. Play the next session sharper.</h1>
          <p className="hero-subtitle">
            Pattern-based post-session review for GG Poker Ontario tournament players.
          </p>
          <div className="cta-row hero-actions">
            <Link className="cta" href="#apply">
              Request Demo
            </Link>
            <Link className="secondary-cta" href="#sample-output">
              See Samples
            </Link>
            {devLoginEnabled ? (
              <Link className="secondary-cta" href="/auth/dev-login?role=operator&next=/operator">
                Operator
              </Link>
            ) : null}
          </div>
        </div>

        <div className="hero-preview">
          <div className="hero-float hero-float-primary">
            <span className="float-label">Today</span>
            <strong>Wider BB defend vs late opens</strong>
          </div>
          <div className="hero-float hero-float-secondary">
            <span className="float-label">Review</span>
            <strong>Medium-stack hesitation cost more than spew</strong>
          </div>
          <div className="hero-float hero-float-tertiary">
            <span className="float-label">Brain</span>
            <strong>Late-stage passivity still the main pressure point</strong>
          </div>
        </div>
      </section>

      <section className="grid three landing-grid" id="sample-output">
        <article className="sample-card sample-today">
          <span className="sample-kicker">Today</span>
          <h3>Next-session focus</h3>
          <p>Defend a little wider. Trust short-stack decisions more.</p>
        </article>
        <article className="sample-card sample-review">
          <span className="sample-kicker">Review</span>
          <h3>What actually repeated</h3>
          <p>Not chaos. Not spew. Mostly hesitation in the wrong stack bands.</p>
        </article>
        <article className="sample-card sample-brain">
          <span className="sample-kicker">Brain</span>
          <h3>Long-term player read</h3>
          <p>Composed early. Strong under pressure. Still too passive after setbacks.</p>
        </article>
      </section>

      <section className="grid two landing-grid mini-grid">
        <article className="mini-card">
          <p className="eyebrow">For</p>
          <h3>GG Poker Ontario MTT players</h3>
          <p className="subtle">Built for players who want pattern tracking, not random hand comments.</p>
        </article>
        <article className="mini-card">
          <p className="eyebrow">How</p>
          <h3>Upload. Track. Adjust.</h3>
          <p className="subtle">Your sessions turn into a running read on leaks, strengths, and next moves.</p>
        </article>
      </section>

      <DemoApplyForm />
    </main>
  );
}

import Link from "next/link";
import { DemoApplyForm } from "./demo-apply-form";

export default function LandingPage() {
  const devLoginEnabled = process.env.OPB_ENABLE_DEV_LOGIN === "1";

  return (
    <main className="shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">One Percent Better Poker</p>
          <h1>Your game, remembered.</h1>
          <p className="subtle">
            One Percent Better is a poker performance system for serious GG Poker Ontario tournament players. Upload your
            session history, track repeated patterns over time, and get clearer next adjustments instead of isolated hand
            comments.
          </p>
          <p className="subtle">
            Post-session only. No live advice. Currently recruiting online GG Poker Ontario tournament players for early demo
            access.
          </p>
          <div className="cta-row">
            <Link className="cta" href="#apply">
              Apply For Demo
            </Link>
            <Link className="secondary-cta" href="#sample-output">
              See Sample Output
            </Link>
            {devLoginEnabled ? (
              <Link className="secondary-cta" href="/auth/dev-login?role=operator&next=/operator">
                Enter As Operator
              </Link>
            ) : null}
          </div>
        </div>
        <div className="page-card">
          <h3>Built For</h3>
          <div className="pill-row">
            <span className="pill">GG Poker Ontario</span>
            <span className="pill">Tournament Players</span>
            <span className="pill">Pattern Tracking</span>
          </div>
          <p className="subtle">
            This is for players who want more than random hand review. The system is built to remember your repeated leaks,
            strengths, and current adjustment direction across sessions.
          </p>
        </div>
      </section>

      <section className="grid three landing-grid" id="sample-output">
        <article className="page-card">
          <p className="eyebrow">Sample Today</p>
          <h3>Your next session adjustment</h3>
          <div className="status-list">
            <div className="status-item">
              <strong>Defend BB a little wider versus late opens</strong>
              <div className="subtle">Your pool is giving up too much postflop for this to stay over-folded.</div>
            </div>
            <div className="status-item">
              <strong>Trust your under-15bb all-in decisions more</strong>
              <div className="subtle">Recent hesitation is costing more than outright punts.</div>
            </div>
            <div className="status-item">
              <strong>Do not over-correct into passivity after one rough session</strong>
              <div className="subtle">Your best sessions still come from measured pressure, not retreat.</div>
            </div>
          </div>
        </article>
        <article className="page-card">
          <p className="eyebrow">Sample Review</p>
          <h3>What repeated this session</h3>
          <div className="status-list">
            <div className="status-item">
              <strong>You passed on several profitable pressure spots after building a stack</strong>
              <div className="subtle">The issue looked more like threshold hesitation than fear-driven spew.</div>
            </div>
            <div className="status-item">
              <strong>Your short-stack discipline held better than usual</strong>
              <div className="subtle">The cleaner part of the session was the under-15bb decision tree.</div>
            </div>
            <div className="status-item">
              <strong>Biggest issue was medium-stack indecision, not chaos</strong>
              <div className="subtle">That changes what you should study next.</div>
            </div>
          </div>
        </article>
        <article className="page-card">
          <p className="eyebrow">Sample Brain</p>
          <h3>Your long-term player read</h3>
          <div className="status-list">
            <div className="status-item">
              <strong>Standard</strong>
              <div className="subtle">Patient early. Composed under pressure. Usually strongest when decisions stay structured.</div>
            </div>
            <div className="status-item">
              <strong>Unusual</strong>
              <div className="subtle">More hesitation in medium-stack reshove spots than your prior baseline.</div>
            </div>
            <div className="status-item">
              <strong>Persistent pressure</strong>
              <div className="subtle">Late-stage passivity after setbacks is still the main pattern worth tracking.</div>
            </div>
          </div>
        </article>
      </section>

      <section className="grid two landing-grid">
        <article className="page-card">
          <p className="eyebrow">Who It Is For</p>
          <h3>Serious GG Poker Ontario MTT players.</h3>
          <div className="status-list compact">
            <div className="status-item">Players with real hand history volume</div>
            <div className="status-item">Players who want pattern tracking, not solver trivia</div>
            <div className="status-item">Players who want to understand how they actually play over time</div>
          </div>
        </article>
        <article className="page-card">
          <p className="eyebrow">How It Works</p>
          <h3>Upload. Track. Adjust.</h3>
          <div className="status-list compact">
            <div className="status-item">Upload your GG Poker Ontario session history</div>
            <div className="status-item">The system tracks repeated leaks, strengths, and shifts</div>
            <div className="status-item">You get Today, Review, and Brain outputs built from your actual play</div>
          </div>
        </article>
      </section>

      <DemoApplyForm />
    </main>
  );
}

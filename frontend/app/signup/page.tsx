import Link from "next/link";
import { DemoApplyForm } from "../demo-apply-form";

export default function SignupPage() {
  return (
    <main className="auth-wrap">
      <section className="auth-card signup-shell">
        <p className="eyebrow">Signup</p>
        <h1>Apply for early demo access.</h1>
        <p className="subtle">
          Right now the best fit is an online GG Poker Ontario tournament player with real hand histories and a clear idea of
          what they want help with.
        </p>
        <DemoApplyForm compact />
        <div className="cta-row">
          <Link className="secondary-cta" href="/">
            Back To Homepage
          </Link>
        </div>
      </section>
    </main>
  );
}

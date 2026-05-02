"use client";

import { useActionState } from "react";
import { submitDemoApplication, type DemoApplyState } from "./demo-apply/actions";

type DemoApplyFormProps = {
  compact?: boolean;
};

const initialState: DemoApplyState = {
  ok: false,
  message: "",
};

export function DemoApplyForm({ compact = false }: DemoApplyFormProps) {
  const [state, formAction, isPending] = useActionState(submitDemoApplication, initialState);

  return (
    <section className={`apply-shell ${compact ? "compact" : ""}`} id="apply">
      <div className="apply-copy">
        <p className="eyebrow">Early Demo</p>
        <h2>Join the first GG Poker Ontario test group.</h2>
        <p className="subtle">
          Serious online MTT players only. Short application. No long setup. No live advice.
        </p>
        <div className="apply-badges">
          <span className="apply-badge">GG Ontario</span>
          <span className="apply-badge">Online MTT</span>
          <span className="apply-badge">Early Access</span>
        </div>
      </div>

      <div className="apply-panel">
        {state.ok ? (
          <div className="success-card">
            <p className="eyebrow">Request Sent</p>
            <h3>You&apos;re on the list.</h3>
            <p className="subtle">
              {state.message}
            </p>
            {state.applicationId ? <p className="subtle">Application ID: {state.applicationId}</p> : null}
          </div>
        ) : (
          <form className={`apply-form ${compact ? "compact-grid" : ""}`} action={formAction}>
            <input name="name" required placeholder="Name" />
            <input name="email" required type="email" placeholder="Email" />
            <input name="games" required placeholder="Games / buy-ins" />
            <textarea
              name="help"
              required
              placeholder="What do you want help with most?"
              rows={4}
            />
            {state.message ? <p className="form-error">{state.message}</p> : null}
            <button className="cta button-reset apply-submit" type="submit" disabled={isPending}>
              {isPending ? "Sending..." : "Request Demo"}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

"use client";

import { useMemo, useState } from "react";

type DemoApplyFormProps = {
  compact?: boolean;
};

export function DemoApplyForm({ compact = false }: DemoApplyFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [games, setGames] = useState("");
  const [help, setHelp] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const canSubmit = useMemo(() => {
    return name.trim() && email.trim() && games.trim() && help.trim();
  }, [name, email, games, help]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) {
      return;
    }

    setSubmitted(true);
  }

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
        {submitted ? (
          <div className="success-card">
            <p className="eyebrow">Request Sent</p>
            <h3>You&apos;re on the list.</h3>
            <p className="subtle">
              Thanks. I&apos;ll use this to screen early demo users and follow up with the best-fit GG Poker Ontario players.
            </p>
          </div>
        ) : (
          <form className={`apply-form ${compact ? "compact-grid" : ""}`} onSubmit={handleSubmit}>
            <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Name" />
            <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
            <input value={games} onChange={(event) => setGames(event.target.value)} placeholder="Games / buy-ins" />
            <textarea
              value={help}
              onChange={(event) => setHelp(event.target.value)}
              placeholder="What do you want help with most?"
              rows={4}
            />
            <button className="cta button-reset apply-submit" type="submit" disabled={!canSubmit}>
              Request Demo
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

"use client";

import { useMemo, useState } from "react";

type DemoApplyFormProps = {
  compact?: boolean;
};

const DEFAULT_DEMO_EMAIL = "hello@onepercentbetter.poker";

export function DemoApplyForm({ compact = false }: DemoApplyFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [discord, setDiscord] = useState("");
  const [games, setGames] = useState("");
  const [histories, setHistories] = useState("yes");
  const [help, setHelp] = useState("");

  const targetEmail = process.env.NEXT_PUBLIC_DEMO_APPLY_EMAIL || DEFAULT_DEMO_EMAIL;

  const canSubmit = useMemo(() => {
    return name.trim().length > 0 && email.trim().length > 0 && games.trim().length > 0 && help.trim().length > 0;
  }, [name, email, games, help]);

  function handleApply() {
    if (!canSubmit) {
      return;
    }

    const subject = encodeURIComponent(`Demo application from ${name.trim()}`);
    const body = encodeURIComponent(
      [
        "One Percent Better Demo Application",
        "",
        `Name: ${name.trim()}`,
        `Email: ${email.trim()}`,
        `Discord / X: ${discord.trim() || "n/a"}`,
        `Games / buy-ins: ${games.trim()}`,
        `GG Poker Ontario hand histories available: ${histories}`,
        "",
        "What I want the most help with:",
        help.trim()
      ].join("\n")
    );

    window.location.href = `mailto:${targetEmail}?subject=${subject}&body=${body}`;
  }

  return (
    <section className={`page-card ${compact ? "apply-card compact" : "apply-card"}`} id="apply">
      <p className="eyebrow">Apply For Demo</p>
      <h2>Currently recruiting GG Poker Ontario tournament players.</h2>
      <p className="subtle">
        If you play online MTTs on GG Poker Ontario and want pattern-based post-session review, send a demo application
        below.
      </p>
      <div className={`input-grid ${compact ? "compact-grid" : ""}`}>
        <label>
          Name
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Your name" />
        </label>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
        </label>
        <label>
          Discord or X / Twitter
          <input value={discord} onChange={(event) => setDiscord(event.target.value)} placeholder="@handle (optional)" />
        </label>
        <label>
          Main games / buy-in range
          <input
            value={games}
            onChange={(event) => setGames(event.target.value)}
            placeholder="GG Ontario MTTs, usually $10-$50"
          />
        </label>
        <label>
          Do you have GG Poker Ontario hand histories?
          <select value={histories} onChange={(event) => setHistories(event.target.value)}>
            <option value="yes">Yes</option>
            <option value="some">Some</option>
            <option value="not_yet">Not yet</option>
          </select>
        </label>
        <label>
          What do you want the most help with?
          <textarea
            value={help}
            onChange={(event) => setHelp(event.target.value)}
            placeholder="Example: short-stack decisions, pressure spots, repeated leaks, staying composed after setbacks."
            rows={5}
          />
        </label>
      </div>
      <div className="cta-row">
        <button className="cta button-reset" type="button" onClick={handleApply} disabled={!canSubmit}>
          Apply For Demo
        </button>
        <a className="secondary-cta" href={`mailto:${targetEmail}`}>
          Email Directly
        </a>
      </div>
      <p className="subtle fine-print">
        This opens your email app with your answers prefilled to {targetEmail}. Early demo is post-session only. No live
        advice.
      </p>
    </section>
  );
}

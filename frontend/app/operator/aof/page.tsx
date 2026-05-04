import Link from "next/link";
import { getAofDecisionSystem, getAofImplementationProfile } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";

function metric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function formatBreakdown(value: Record<string, unknown> | undefined) {
  if (!value || !Object.keys(value).length) {
    return "No sample";
  }
  return Object.entries(value)
    .map(([key, count]) => `${key}: ${count}`)
    .join(" · ");
}

export default async function OperatorAofPage() {
  const viewer = await getViewerContext();
  const [profile, decisionSystem] = await Promise.all([
    getAofImplementationProfile(viewer.playerId),
    getAofDecisionSystem(viewer.playerId)
  ]);

  const summary = decisionSystem?.summary || {};
  const profileSummary = profile?.summary || {};
  const productSummary = decisionSystem?.product_summary || {};
  const priorityCards = decisionSystem?.priority_leak_cards || [];

  return (
    <main className="shell matrix-shell aof-shell">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero aof-page-hero">
        <div>
          <p className="eyebrow">AOF Analysis</p>
          <h1>Short-stack decision system</h1>
          <p className="subtle">
            AOF lives here as a baseline-building surface: implementation profile, leak queue, cooler guardrail, and
            operator-defer context in one place. It is deterministic review truth, not solver-grade EV.
          </p>
        </div>
        <Link className="secondary-cta" href="/operator">
          Back to operator
        </Link>
      </section>

      <section className="page-card matrix-analysis-card">
        <div className="result-hero">
          <div>
            <span className="sample-kicker">AOF v2 Decisions</span>
            <strong>{metric(summary.short_stack_decision_count)}</strong>
            <p>
              {metric(summary.mistake_candidate_count)} leak candidates ·{" "}
              {metric(summary.operator_defer_count)} operator-defer
            </p>
          </div>
          <div>
            <span className="sample-kicker">AOF v1 Opportunities</span>
            <strong>{metric(profileSummary.aof_opportunity_count)}</strong>
            <p>
              {metric(profileSummary.match_rate, "%")} match · {metric(profileSummary.too_loose_rate, "%")} too loose
            </p>
          </div>
          <div>
            <span className="sample-kicker">12bb Hypothesis</span>
            <strong>{profileSummary.hero_12bb_hypothesis || "n/a"}</strong>
            <p>
              Jam median {metric(profileSummary.jam_median_stack_bb, "bb")} · avg{" "}
              {metric(profileSummary.jam_average_stack_bb, "bb")}
            </p>
          </div>
        </div>
        <div className="baseline-toggle-note">
          <span>{decisionSystem?.summary?.truth_policy || "AOF is deterministic derived review truth."}</span>
          <span>{profile?.truth_policy || "AOF v1 is a directional baseline."}</span>
        </div>
      </section>

      <section className="operator-insight-grid aof-summary-grid">
        <article className="page-card operator-readable-card warning">
          <span className="sample-kicker">Lead Read</span>
          <h3>{productSummary.headline || "No AOF lead read yet"}</h3>
          <p>{productSummary.read || "Short-stack decisions are waiting for enough clear evidence."}</p>
        </article>
        <article className="page-card operator-readable-card danger">
          <span className="sample-kicker">Next Adjustment</span>
          <h3>Primary fix</h3>
          <strong>{productSummary.primary_fix || "Keep collecting AOF evidence."}</strong>
        </article>
        <article className="page-card operator-readable-card value">
          <span className="sample-kicker">Cooler Guard</span>
          <h3>Protect non-mistakes</h3>
          <p>{productSummary.cooler_guardrail || "Premium lost outcomes should not become fake leak memory."}</p>
        </article>
      </section>

      <section className="matrix-section-grid">
        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Stack Bands</p>
              <h3>AOF v1 implementation profile</h3>
            </div>
            <span className="pill">unopened spots</span>
          </div>
          <div className="status-list compact">
            {Object.entries(profile?.stack_breakdown || {}).map(([band, row]: [string, any]) => (
              <div className="matrix-insight-row" key={band}>
                <strong>{band}</strong>
                <span>
                  {metric(row.count)} spots · {metric(row.jam_rate, "%")} jam · {metric(row.match_rate, "%")} match
                </span>
                <p>{metric(row.too_loose_rate, "%")} too-loose rate under the v1 baseline.</p>
              </div>
            ))}
          </div>
        </article>

        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Formats</p>
              <h3>Context guardrails</h3>
            </div>
            <span className="pill">format-aware</span>
          </div>
          <div className="status-list compact">
            {Object.entries(profile?.format_breakdown || {}).map(([format, row]: [string, any]) => (
              <div className="matrix-insight-row value" key={format}>
                <strong>{format}</strong>
                <span>
                  {metric(row.count)} spots · {metric(row.jam_rate, "%")} jam
                </span>
                <p>
                  {metric(row.too_loose_rate, "%")} too-loose ·{" "}
                  {metric(row.special_context_defer_rate, "%")} special-context defer
                </p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="page-card standout-card matrix-analysis-card">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Priority Leak Queue</p>
            <h3>What to review first</h3>
          </div>
          <span className="pill">{priorityCards.length} cards</span>
        </div>
        <div className="priority-stack">
          {priorityCards.map((card: any, index: number) => (
            <article className="leak-card aof-leak-card" key={`${card.mistake_family}-${card.hand_class}`}>
              <div className="leak-rank">{index + 1}</div>
              <div>
                <div className="leak-title-row">
                  <h4>{card.product_read?.title || `${card.hand_class} ${card.mistake_family}`}</h4>
                  <span className="leak-severity">{card.product_read?.severity || "Review queue"}</span>
                </div>
                <p className="leak-why">{card.product_read?.why_it_matters || card.next_adjustment}</p>
                <div className="evidence-chips">
                  <span>{card.product_read?.evidence_line || `${card.count} repeats`}</span>
                  <span>{formatBreakdown(card.stack_bands)}</span>
                  <span>{formatBreakdown(card.formats)}</span>
                </div>
                <div className="leak-action-grid">
                  <div>
                    <strong>Change</strong>
                    <p>{card.product_read?.what_to_change || card.next_adjustment}</p>
                  </div>
                  <div>
                    <strong>Do not over-correct</strong>
                    <p>{card.product_read?.what_not_to_overreact_to || "Review context before making this durable truth."}</p>
                  </div>
                </div>
                <details className="operator-details">
                  <summary>Examples</summary>
                  <div className="status-list compact">
                    {(card.examples || []).slice(0, 3).map((example: any) => (
                      <div className="status-item" key={example.spot_id || example.hand_external_id}>
                        <strong>
                          {example.hand_class} · {metric(example.stack_bb, "bb")} · {example.situation}
                        </strong>
                        <p className="subtle">
                          {example.actual_action} · {example.format_profile} · {example.result} ·{" "}
                          {example.hand_external_id || "unknown hand"}
                        </p>
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="matrix-section-grid">
        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Operator Defer</p>
              <h3>Still needs context</h3>
            </div>
            <span className="pill">{metric(summary.operator_defer_count)} spots</span>
          </div>
          <p className="subtle">{productSummary.operator_note || "No operator-defer note available."}</p>
          <div className="baseline-toggle-note">
            {Object.entries(decisionSystem?.situation_counts || {}).slice(0, 8).map(([key, count]) => (
              <span key={key}>
                {key}: {String(count)}
              </span>
            ))}
          </div>
        </article>

        <article className="page-card matrix-analysis-card">
          <div className="section-heading-row">
            <div>
              <p className="eyebrow">Cooler / Non-mistake</p>
              <h3>Protected examples</h3>
            </div>
            <span className="pill">{metric(summary.cooler_protection_count)} examples</span>
          </div>
          <div className="status-list compact">
            {(decisionSystem?.cooler_or_non_mistake_examples || []).slice(0, 5).map((example: any) => (
              <div className="matrix-insight-row value" key={example.spot_id || example.hand_external_id}>
                <strong>
                  {example.hand_class} · {metric(example.stack_bb, "bb")} · {example.actual_action}
                </strong>
                <span>{example.mistake_family}</span>
                <p>{example.explanation}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

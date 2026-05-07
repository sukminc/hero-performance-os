import { AofDetailDisclosure } from "./aof-detail-disclosure";
import type { CSSProperties } from "react";

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

function formatPct(value: unknown) {
  return formatMetric(value, "%");
}

function metricTone(value: unknown) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric === 0) {
    return "metric-neutral";
  }
  return numeric > 0 ? "metric-positive" : "metric-negative";
}

function ResultMetric({ value, suffix = "bb", label }: { value: unknown; suffix?: string; label?: string }) {
  return (
    <span className={`signed-metric ${metricTone(value)}`}>
      {formatMetric(value, suffix)}
      {label ? <em>{label}</em> : null}
    </span>
  );
}

function countLabel(count: unknown, noun: string) {
  const numeric = Number(count || 0);
  if (numeric === 1 && noun.endsWith("s")) {
    return `${numeric} ${noun.slice(0, -1)}`;
  }
  return `${numeric} ${noun}`;
}

function aofRowTone(row: any) {
  const stack = Number(row?.avg_stack_realization_pct ?? 0);
  if (stack <= -20 || (row?.full_stack_loss_count || 0) >= 5) {
    return "danger";
  }
  if (stack >= 5) {
    return "value";
  }
  return "neutral";
}

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: "12px",
};

const panelStyle: CSSProperties = {
  display: "grid",
  gap: "7px",
  minWidth: 0,
  overflowX: "auto",
};

const rowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr) 86px 96px 96px 76px",
  gap: "8px",
  alignItems: "center",
};

export function AofBaselineSection({ preflopAof }: { preflopAof: any }) {
  return (
    <section className="page-card matrix-analysis-card preflop-aof-card">
      <div className="section-heading-row">
        <div>
          <p className="eyebrow">AOF Baseline</p>
          <h3>Preflop all-in stack depth</h3>
        </div>
        <span className="pill">first action jam</span>
      </div>
      <div className="result-hero preflop-result-hero">
        <div>
          <span className="sample-kicker">All AOF</span>
          <strong>{formatMetric(preflopAof?.overall?.avg_stack_bb, "bb")}</strong>
          <p>
            {preflopAof?.overall?.count || 0} jams ·{" "}
            <ResultMetric value={preflopAof?.overall?.avg_bb_per_jam} label="result" />
          </p>
        </div>
        <div>
          <span className="sample-kicker">25bb or less</span>
          <strong>{formatMetric(preflopAof?.short_stack_lte25?.avg_stack_bb, "bb")}</strong>
          <p>
            {preflopAof?.short_stack_lte25?.count || 0} jams ·{" "}
            <ResultMetric value={preflopAof?.short_stack_lte25?.avg_bb_per_jam} label="result" />
          </p>
        </div>
        <div>
          <span className="sample-kicker">Definition</span>
          <strong>AOF</strong>
          <p>{preflopAof?.definition || "Hero first preflop action is jam/all-in."}</p>
        </div>
      </div>
      <div className="preflop-aof-grid" style={gridStyle}>
        <div className="preflop-aof-panel" style={panelStyle}>
          <span className="sample-kicker">By Action</span>
          {(preflopAof?.entry_rows || []).map((row: any) => (
            <div className={`preflop-aof-row ${aofRowTone(row)}`} key={row.entry_type} style={rowStyle}>
              <strong>{row.entry_type}</strong>
              <span>{countLabel(row.count, "jams")}</span>
              <span>{formatMetric(row.avg_stack_bb, "bb")} avg</span>
              <small>
                <ResultMetric value={row.avg_bb_per_jam} label="result" />
              </small>
              <AofDetailDisclosure row={row} />
            </div>
          ))}
        </div>
        <div className="preflop-aof-panel" style={panelStyle}>
          <span className="sample-kicker">By Position</span>
          {(preflopAof?.position_rows || []).map((row: any) => (
            <div className={`preflop-aof-row ${aofRowTone(row)}`} key={row.position} style={rowStyle}>
              <strong>{row.position}</strong>
              <span>{countLabel(row.count, "jams")}</span>
              <span>{formatMetric(row.avg_stack_bb, "bb")} avg</span>
              <small>
                <ResultMetric value={row.avg_bb_per_jam} label="result" />
              </small>
              <AofDetailDisclosure row={row} />
            </div>
          ))}
        </div>
      </div>
      {(preflopAof?.big_loss_clusters || []).length ? (
        <div className="aof-loss-strip">
          <span className="sample-kicker">Repeated big minus clusters</span>
          {(preflopAof?.big_loss_clusters || []).slice(0, 5).map((cluster: any) => (
            <div className="aof-loss-chip" key={`${cluster.hand_class}-${cluster.position}-${cluster.entry_type}`}>
              <strong>
                {cluster.hand_class} · {cluster.position} · {cluster.entry_type}
              </strong>
              <span className="aof-loss-metrics">
                <b>{countLabel(cluster.count, "jams")}</b>
                <b className={metricTone(cluster.avg_bb_per_jam)}>{formatMetric(cluster.avg_bb_per_jam, "bb")}</b>
                <b className={metricTone(cluster.avg_stack_realization_pct)}>
                  {formatPct(cluster.avg_stack_realization_pct)} stack
                </b>
              </span>
            </div>
          ))}
        </div>
      ) : null}
      <div className="preflop-aof-read">
        <div>
          <p className="eyebrow">Interpretation</p>
          <h4>{preflopAof?.interpretation?.headline}</h4>
          <p>{preflopAof?.interpretation?.read}</p>
        </div>
        <div className="hand-read-list">
          <span>Takeaway</span>
          {(preflopAof?.interpretation?.takeaways || []).map((takeaway: string) => (
            <strong key={takeaway}>{takeaway}</strong>
          ))}
        </div>
      </div>
      <p className="subtle sizing-policy">{preflopAof?.truth_policy}</p>
    </section>
  );
}

import type { CSSProperties } from "react";

function formatMetric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "";
  }
  return `${value}${suffix}`;
}

function formatPct(value: unknown) {
  return formatMetric(value, "%");
}

export function PreflopSizingTable({ rows }: { rows: any[] }) {
  const columns = "96px repeat(5, minmax(116px, 1fr))";
  const headerStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: columns,
    columnGap: "8px",
    minWidth: "820px",
    padding: "10px 12px",
  };
  const rowStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: columns,
    columnGap: "8px",
    alignItems: "center",
    minWidth: "820px",
    padding: "10px 12px",
  };
  const metricStyle: CSSProperties = {
    display: "flex",
    minWidth: 0,
    alignItems: "baseline",
    gap: "6px",
    whiteSpace: "nowrap",
  };
  const blankMetric = <span className="preflop-empty-metric" aria-label="No data" />;

  function countLabel(count: number, noun: string) {
    if (count === 1 && noun.endsWith("s")) {
      return `${count} ${noun.slice(0, -1)}`;
    }
    return `${count} ${noun}`;
  }

  function renderMetric(value: unknown, count?: unknown, suffix = "x", countNoun = "spots") {
    const numericCount = Number(count || 0);
    if (value === null || value === undefined || (count !== undefined && numericCount <= 0)) {
      return blankMetric;
    }
    return (
      <span style={metricStyle}>
        <b>{formatMetric(value, suffix)}</b>
        {count !== undefined ? <small>{countLabel(numericCount, countNoun)}</small> : null}
      </span>
    );
  }

  return (
    <div className="preflop-sizing-table-wrap">
      <div className="preflop-sizing-table" role="table" aria-label="Preflop sizing by position">
        <div className="preflop-sizing-head" role="row" style={headerStyle}>
          <span>Position</span>
          <span>Open avg</span>
          <span>2x rate</span>
              <span>3bet avg</span>
              <span>Vs single 2x</span>
              <span>Squeeze 2x+</span>
        </div>
        <div className="preflop-sizing-body" role="rowgroup">
          {(rows || []).map((row: any) => (
            <div className="preflop-sizing-row" key={row.position} role="row" style={rowStyle}>
              <strong>{row.position}</strong>
              {renderMetric(row.avg_open_size_bb, row.open_count, "x", "opens")}
              {row.two_x_open_rate_pct === null || row.two_x_open_rate_pct === undefined || Number(row.open_count || 0) <= 0
                ? blankMetric
                : renderMetric(row.two_x_open_rate_pct, undefined, "%")}
              {renderMetric(row.avg_3bet_size_bb, row.three_bet_count, "x", "3bets")}
              {renderMetric(row.avg_3bet_vs_2x_single_bb, row.three_bet_vs_2x_single_count, "x", "spots")}
              {renderMetric(row.avg_squeeze_vs_2x_callers_bb, row.squeeze_vs_2x_callers_count, "x", "squeezes")}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

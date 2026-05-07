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

function countLabel(count: unknown, noun: string) {
  const numeric = Number(count || 0);
  if (numeric === 1 && noun.endsWith("s")) {
    return `${numeric} ${noun.slice(0, -1)}`;
  }
  return `${numeric} ${noun}`;
}

export function AofDetailDisclosure({ row }: { row: any }) {
  const clusters = row?.big_loss_clusters || [];
  return (
    <details className="aof-detail-disclosure">
      <summary>details</summary>
      <div className="aof-detail-panel">
        <strong>Result detail</strong>
        <span>
          <b className={metricTone(row?.avg_bb_per_jam)}>{formatMetric(row?.avg_bb_per_jam, "bb")}</b> / jam ·{" "}
          <b className={metricTone(row?.avg_stack_realization_pct)}>
            {formatPct(row?.avg_stack_realization_pct)} stack
          </b>{" "}
          · {row?.full_stack_loss_count || 0} full-stack losses
        </span>
        {clusters.length ? (
          <div className="aof-hover-clusters">
            {clusters.slice(0, 3).map((cluster: any, index: number) => (
              <div className="aof-hover-cluster" key={`${cluster.hand_class}-${cluster.position}-${cluster.entry_type}-${index}`}>
                <b>
                  {cluster.hand_class} · {cluster.position} · {cluster.entry_type}
                </b>
                <small>
                  <span className="aof-loss-metrics compact">
                    <b>{countLabel(cluster.count, "jams")}</b>
                    <b className={metricTone(cluster.avg_bb_per_jam)}>{formatMetric(cluster.avg_bb_per_jam, "bb")}</b>
                    <b className={metricTone(cluster.avg_stack_realization_pct)}>
                      {formatPct(cluster.avg_stack_realization_pct)} stack
                    </b>
                  </span>
                </small>
                {(cluster.examples || []).slice(0, 1).map((example: any) => (
                  <em key={example.hand_id}>
                    {formatMetric(example.stack_bb, "bb")} stack · {formatMetric(example.bb_net, "bb")} ·{" "}
                    {example.hero_summary}
                  </em>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <small>No repeated -50% stack cluster in this row.</small>
        )}
      </div>
    </details>
  );
}

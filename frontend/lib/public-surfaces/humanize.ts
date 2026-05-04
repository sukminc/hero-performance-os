const ENTITY_LABELS: Record<string, string> = {
  session_survival_discipline: "Session survival",
  blind_structure_absorption: "Blind defense bleed",
  multiway_pressure: "Multiway pots",
  high_engagement_profile: "Deep-stack engagement",
  board_contact_density: "Board-heavy fields",
  passive_blind_compliance: "Blind passivity",
  reset_and_preservation_discipline: "Reset discipline",
};

const STATE_LABELS: Record<string, { label: string; tone: "good" | "warn" | "alert" | "neutral" }> = {
  stable: { label: "Stable", tone: "good" },
  drifting: { label: "Drifting", tone: "warn" },
  volatile_but_acceptable: { label: "Volatile", tone: "warn" },
  contaminated: { label: "Contaminated", tone: "alert" },
  unclear: { label: "Forming", tone: "neutral" },
};

const STATUS_LABELS: Record<string, string> = {
  active: "Active",
  baseline: "Baseline",
  watch: "Watching",
  resolved: "Resolved",
};

const DIRECTION_TONE: Record<string, "good" | "warn" | "alert" | "neutral"> = {
  positive: "good",
  negative: "alert",
  shift: "warn",
  unknown: "neutral",
};

const MEMORY_TYPE_LABEL: Record<string, string> = {
  stable_strength_candidate: "Strength",
  contamination_risk_candidate: "Risk",
  field_distortion_candidate: "Field signal",
  style_drift_candidate: "Style drift",
  hand_class_underperformance: "Hand class leak",
  positive_execution_memory: "Reviewed strength",
};

const RESULT_SIGNAL_LABEL: Record<string, string> = {
  top_three_big_cash: "Top-3 deep run",
  final_table: "Final table",
  meaningful_cash: "Cash",
  deep_run: "Deep run",
};

export function humanizeEntity(entityKey: string | null | undefined, fallback?: string) {
  if (!entityKey) return fallback || "Pattern";
  if (ENTITY_LABELS[entityKey]) return ENTITY_LABELS[entityKey];
  return entityKey
    .replace(/[_:]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function humanizeMemoryType(memoryType: string | null | undefined) {
  if (!memoryType) return "Pattern";
  return MEMORY_TYPE_LABEL[memoryType] || memoryType.replace(/_/g, " ");
}

export function humanizeStatus(status: string | null | undefined) {
  if (!status) return "Forming";
  return STATUS_LABELS[status] || status;
}

export function humanizeState(state: string | null | undefined) {
  if (!state) return STATE_LABELS.unclear;
  return STATE_LABELS[state] || STATE_LABELS.unclear;
}

export function directionTone(direction: string | null | undefined) {
  if (!direction) return "neutral";
  return DIRECTION_TONE[direction] || "neutral";
}

export function humanizeResultSignal(signal: string | null | undefined) {
  if (!signal) return "Result";
  return RESULT_SIGNAL_LABEL[signal] || signal.replace(/_/g, " ");
}

export function confidencePercent(confidence: number | null | undefined) {
  if (typeof confidence !== "number" || Number.isNaN(confidence)) return 0;
  return Math.round(Math.max(0, Math.min(1, confidence)) * 100);
}

export function shortenSummary(summary: string | null | undefined, fallback = "") {
  if (!summary) return fallback;
  // Strip the leading "memory_type [entity_key] is currently ..." prefix the engine adds.
  const stripped = summary
    .replace(/^[a-z_]+\s*\[[^\]]+\]\s*is currently\s+\w+\s*\(\w+\)\.\s*/i, "")
    .trim();
  return stripped || summary;
}

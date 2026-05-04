import Link from "next/link";
import { getBigWinReview } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { promoteBigWinRepeatableExecution, tagBigWinSpot } from "../demo-actions";

const TAGS = [
  { value: "repeatable_execution", label: "Repeatable" },
  { value: "run_good", label: "Run-good" },
  { value: "cooler", label: "Cooler" },
  { value: "unclear", label: "Unclear" }
];

function metric(value: unknown, suffix = "") {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return `${value}${suffix}`;
}

export default async function OperatorBigWinPage() {
  const viewer = await getViewerContext();
  const tournamentId = "6408385";
  const bigWin = await getBigWinReview(viewer.playerId, tournamentId);
  const repeatableCount = Number(bigWin?.review_summary?.tag_summary?.repeatable_execution || 0);

  return (
    <main className="shell matrix-shell">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero big-win-page-hero">
        <div>
          <p className="eyebrow">Big Win Review</p>
          <h1>Separate execution from result heat.</h1>
          <p className="subtle">
            Tag deep-run spots first. Only `repeatable_execution` tags are allowed to become positive Hero memory, and
            promotion writes a separate memory item rather than mutating hand or result truth.
          </p>
        </div>
        <Link className="secondary-cta" href="/operator">
          Back to operator
        </Link>
      </section>

      <section className="page-card matrix-analysis-card">
        <div className="result-hero">
          <div>
            <span className="sample-kicker">Tournament</span>
            <strong>{bigWin?.tournament_result?.finish_place || "n/a"}</strong>
            <p>{bigWin?.tournament_result?.title || `Tournament ${tournamentId}`}</p>
          </div>
          <div>
            <span className="sample-kicker">Candidate Spots</span>
            <strong>{metric(bigWin?.review_summary?.candidate_count)}</strong>
            <p>{metric(repeatableCount)} repeatable tags ready for memory promotion.</p>
          </div>
          <div>
            <span className="sample-kicker">Promotion</span>
            <form action={promoteBigWinRepeatableExecution}>
              <input type="hidden" name="playerId" value={viewer.playerId || ""} />
              <input type="hidden" name="tournamentId" value={tournamentId} />
              <button className="cta button-reset" type="submit" disabled={!viewer.playerId || repeatableCount === 0}>
                Promote reviewed execution
              </button>
            </form>
          </div>
        </div>
        <div className="baseline-toggle-note">
          <span>{bigWin?.truth_policy || "Operator tags decide what becomes durable memory."}</span>
          <span>Repeatable tags: {metric(repeatableCount)}</span>
          <span>Run-good tags: {metric(bigWin?.review_summary?.tag_summary?.run_good || 0)}</span>
          <span>Cooler tags: {metric(bigWin?.review_summary?.tag_summary?.cooler || 0)}</span>
        </div>
      </section>

      <section className="page-card standout-card matrix-analysis-card">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Review Queue</p>
            <h3>Candidate deep-run spots</h3>
          </div>
          <span className="pill">{bigWin?.ready ? "ready" : "blocked"}</span>
        </div>
        <div className="priority-stack">
          {(bigWin?.candidate_spots || []).map((spot: any, index: number) => (
            <article className="leak-card big-win-spot-card" key={spot.spot_id || spot.hand_external_id}>
              <div className="leak-rank">{index + 1}</div>
              <div>
                <div className="leak-title-row">
                  <h4>{spot.hand_external_id || spot.spot_id}</h4>
                  <span className="leak-severity">{spot.operator_tag?.decision || "untagged"}</span>
                </div>
                <p className="leak-why">
                  Score {metric(spot.score)} · stack {metric(spot.effective_stack_bb, "bb")} ·{" "}
                  {spot.hero_position || "unknown position"}
                </p>
                <div className="evidence-chips">
                  {(spot.reasons || []).slice(0, 4).map((reason: string) => (
                    <span key={reason}>{reason}</span>
                  ))}
                </div>
                <div className="status-list compact">
                  {(spot.hero_actions || []).slice(0, 4).map((line: string) => (
                    <div className="status-item" key={line}>
                      {line}
                    </div>
                  ))}
                </div>
                <form className="big-win-tag-form" action={tagBigWinSpot}>
                  <input type="hidden" name="spotId" value={spot.spot_id || ""} />
                  <input name="notes" placeholder="Operator note for why this tag is correct" />
                  <div className="pill-row">
                    {TAGS.map((tag) => (
                      <button className="pill button-reset" name="decision" type="submit" value={tag.value} key={tag.value}>
                        {tag.label}
                      </button>
                    ))}
                  </div>
                </form>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

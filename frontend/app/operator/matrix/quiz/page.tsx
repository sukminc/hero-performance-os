import Link from "next/link";
import { getHeroBaselineQuiz } from "@/lib/public-surfaces/read";
import { getViewerContext } from "@/lib/viewer/session";
import { MatrixQuizClient } from "./matrix-quiz-client";

const HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111";

function todayLabel() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Toronto",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

export default async function OperatorMatrixQuizPage() {
  const viewer = await getViewerContext();
  const operatorPlayerId = viewer.playerId || (viewer.canSeeOperatorDepth ? HERO_PLAYER_ID : null);
  const quizDate = todayLabel();
  const quiz = await getHeroBaselineQuiz(operatorPlayerId, quizDate);
  const cards = quiz?.cards || [];

  return (
    <main className="shell matrix-shell">
      <section className="page-card standout-card matrix-analysis-card matrix-page-hero matrix-quiz-hero">
        <div>
          <p className="eyebrow">Daily Quiz</p>
          <h1>Hero Baseline Recall</h1>
          <p className="subtle">
            Guess the real performance grade from partial Matrix context, then reveal the result. This calibrates memory
            against Hero's own database without turning the product into solver grading or live advice.
          </p>
        </div>
        <div className="operator-home-actions">
          <Link className="secondary-cta" href="/operator/matrix">
            Back to matrix
          </Link>
          <Link className="secondary-cta" href="/operator">
            Operator home
          </Link>
        </div>
      </section>

      <section className="page-card matrix-analysis-card">
        <div className="result-hero">
          <div>
            <span className="sample-kicker">Date</span>
            <strong>{quiz?.date || quizDate}</strong>
            <p>Daily candidate rotation is deterministic for this player/date.</p>
          </div>
          <div>
            <span className="sample-kicker">Cards</span>
            <strong>{cards.length}</strong>
            <p>{quiz?.summary?.candidate_count || 0} high-signal candidates available.</p>
          </div>
          <div>
            <span className="sample-kicker">Answer Target</span>
            <strong>Grade</strong>
            <p>Baseline · Watch · Leak · Value</p>
          </div>
        </div>
        <div className="baseline-toggle-note">
          <span>Partial stats first</span>
          <span>Reveal after choice</span>
          <span>Reaction logs only</span>
          <span>No automatic memory promotion</span>
        </div>
      </section>

      {!operatorPlayerId ? (
        <section className="page-card matrix-analysis-card">
          <p className="eyebrow">Daily Quiz</p>
          <h3>No operator player scope</h3>
          <p className="subtle">This operator-only quiz needs a mapped player before it can read Hero baseline data.</p>
        </section>
      ) : null}

      {operatorPlayerId && !cards.length ? (
        <section className="page-card matrix-analysis-card">
          <p className="eyebrow">Daily Quiz</p>
          <h3>No quiz cards yet</h3>
          <p className="subtle">
            {quiz?.blank_state || "Upload and parse GG session packets before using the Matrix quiz."}
          </p>
        </section>
      ) : null}

      {operatorPlayerId && cards.length ? (
        <MatrixQuizClient playerId={operatorPlayerId} quizDate={quiz?.date || quizDate} cards={cards} />
      ) : null}
    </main>
  );
}

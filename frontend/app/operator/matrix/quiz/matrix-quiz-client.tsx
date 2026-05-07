"use client";

import { useState } from "react";
import { logMatrixQuizAttempt } from "../../demo-actions";

type QuizCard = {
  id: string;
  subject: string;
  question: string;
  choices: string[];
  prompt?: {
    hand_class?: string;
    entry_type?: string;
    played_count?: number | null;
    dealt_count?: number | null;
    visible_stat_lines?: string[];
  };
  answer?: {
    actual_grade?: string;
    avg_bb_per_hand?: number | string | null;
    avg_stack_realization_pct?: number | string | null;
    played_count?: number | null;
    dealt_count?: number | null;
    why?: string;
    study_takeaway?: string;
    truth_policy?: string;
  };
};

const REACTIONS = [
  { value: "expected", label: "Expected" },
  { value: "surprising", label: "Surprising" },
  { value: "memory_mismatch", label: "Memory mismatch" },
  { value: "needs_review", label: "Needs review" },
];

function metric(value: unknown, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  return `${value}${suffix}`;
}

export function MatrixQuizClient({
  playerId,
  quizDate,
  cards,
}: {
  playerId: string;
  quizDate: string;
  cards: QuizCard[];
}) {
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [logged, setLogged] = useState<Record<string, string>>({});

  if (!cards.length) {
    return null;
  }

  return (
    <section className="matrix-quiz-stack">
      {cards.map((card, index) => {
        const selectedGrade = selected[card.id];
        const isRevealed = Boolean(selectedGrade);
        const isCorrect = selectedGrade === card.answer?.actual_grade;
        return (
          <article className={`page-card matrix-analysis-card matrix-quiz-card ${isRevealed ? "answered" : ""}`} key={card.id}>
            <div className="section-heading-row">
              <div>
                <p className="eyebrow">Question {index + 1}</p>
                <h3>{card.subject}</h3>
              </div>
              <span className="pill">{card.prompt?.entry_type || "mixed_actions"}</span>
            </div>

            <p className="matrix-quiz-question">{card.question}</p>
            <div className="baseline-toggle-note matrix-quiz-visible-stats">
              {(card.prompt?.visible_stat_lines || []).map((line) => (
                <span key={line}>{line}</span>
              ))}
            </div>

            <div className="matrix-quiz-choice-grid" aria-label={`Choices for ${card.subject}`}>
              {(card.choices || []).map((choice) => (
                <button
                  className={`matrix-quiz-choice button-reset ${selectedGrade === choice ? "selected" : ""}`}
                  disabled={isRevealed}
                  key={choice}
                  onClick={() => setSelected((current) => ({ ...current, [card.id]: choice }))}
                  type="button"
                >
                  {choice}
                </button>
              ))}
            </div>

            {isRevealed ? (
              <div className={`matrix-quiz-reveal ${isCorrect ? "correct" : "incorrect"}`}>
                <div className="result-hero compact-result-hero">
                  <div>
                    <span className="sample-kicker">Your Pick</span>
                    <strong>{selectedGrade}</strong>
                  </div>
                  <div>
                    <span className="sample-kicker">Actual Grade</span>
                    <strong>{card.answer?.actual_grade || "n/a"}</strong>
                  </div>
                  <div>
                    <span className="sample-kicker">Result</span>
                    <strong>{isCorrect ? "Matched" : "Missed"}</strong>
                  </div>
                </div>
                <div className="grid two">
                  <div className="status-item">
                    <strong>Real metrics</strong>
                    <p className="subtle">
                      {metric(card.answer?.avg_bb_per_hand, "bb")} ·{" "}
                      {metric(card.answer?.avg_stack_realization_pct, "%")} stack ·{" "}
                      {metric(card.answer?.played_count)} played / {metric(card.answer?.dealt_count)} dealt
                    </p>
                  </div>
                  <div className="status-item">
                    <strong>Study takeaway</strong>
                    <p className="subtle">{card.answer?.study_takeaway || "Keep this as a calibration card."}</p>
                  </div>
                </div>
                <p className="subtle">{card.answer?.why}</p>
                <form className="matrix-quiz-reaction-form" action={logMatrixQuizAttempt}>
                  <input name="playerId" type="hidden" value={playerId} />
                  <input name="quizDate" type="hidden" value={quizDate} />
                  <input name="cardId" type="hidden" value={card.id} />
                  <input name="selectedGrade" type="hidden" value={selectedGrade} />
                  <div className="pill-row">
                    {REACTIONS.map((reaction) => (
                      <button
                        className="pill button-reset"
                        disabled={Boolean(logged[card.id])}
                        key={reaction.value}
                        name="reaction"
                        onClick={() => setLogged((current) => ({ ...current, [card.id]: reaction.label }))}
                        type="submit"
                        value={reaction.value}
                      >
                        {reaction.label}
                      </button>
                    ))}
                  </div>
                </form>
                {logged[card.id] ? <p className="subtle">Logged: {logged[card.id]}</p> : null}
              </div>
            ) : null}
          </article>
        );
      })}
    </section>
  );
}

import { useEffect, useMemo, useState } from "react";
import type { Listing } from "../types";
import { BRANDS } from "../data/dataset";
import { METHODOLOGY, SCORE_BANDS, SIGNALS } from "../data/signals";
import { computeScore } from "../lib/score";

function bandColor(score: number): string {
  if (score >= 65) return "var(--danger)";
  if (score >= 35) return "var(--warn)";
  if (score >= 15) return "var(--accent)";
  return "var(--ok)";
}

function ScoreDial({ score }: { score: number }) {
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const filled = (score / 100) * circumference;
  const color = bandColor(score);
  return (
    <div className="score-dial">
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="9" />
        <circle
          cx="75"
          cy="75"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="9"
          strokeLinecap={filled > 0 ? "round" : "butt"}
          strokeDasharray={`${filled} ${circumference - filled}`}
          style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: "stroke-dasharray 300ms ease, stroke 300ms ease" }}
        />
      </svg>
      <div className="score-value">
        <div className="score-number">{score}</div>
        <div className="score-max">GHOST SCORE</div>
      </div>
    </div>
  );
}

interface Prefill {
  name: string;
  nonce: number;
}

interface GhostScoreProps {
  listings: Listing[];
  prefill: Prefill;
  /** Returns false when the listing is already logged. */
  onLog: (name: string, address: string) => boolean;
}

export function GhostScore({ listings, prefill, onLog }: GhostScoreProps) {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [answers, setAnswers] = useState<Record<string, boolean>>({});
  const [logState, setLogState] = useState<"idle" | "logged" | "dup">("idle");

  // Each prefill event from Lookup starts a fresh assessment, even for a
  // name that was already assessed.
  useEffect(() => {
    if (prefill.nonce > 0) {
      setName(prefill.name);
      setAddress("");
      setAnswers({});
      setLogState("idle");
    }
  }, [prefill.nonce, prefill.name]);

  const questions = SIGNALS.filter((s) => s.kind === "question");
  const hasInput = name.trim().length >= 2;

  const result = useMemo(
    () => computeScore({ name, address, brands: BRANDS, listings }, answers, SIGNALS, SCORE_BANDS),
    [name, address, answers, listings],
  );

  const setAnswer = (id: string, value: boolean) =>
    setAnswers((prev) => ({ ...prev, [id]: value }));

  const canLog = name.trim().length >= 2 && address.trim().length >= 4;

  const handleLog = () => {
    if (!canLog) return;
    setLogState(onLog(name, address) ? "logged" : "dup");
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Analysis</div>
          <div className="page-title">Ghost Score</div>
          <div className="page-desc">
            Enter the listing as it appears on the delivery app, then answer what you can observe.
            The score updates live.
          </div>
        </div>
      </div>

      <div className="score-layout">
        <div>
          <div className="card">
            <div className="form-row">
              <div>
                <label className="field-label">Listing name</label>
                <input
                  className="input"
                  placeholder="Restaurant name on the app"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    setLogState("idle");
                  }}
                />
              </div>
              <div>
                <label className="field-label">Address (optional)</label>
                <input
                  className="input"
                  placeholder="Street address shown on the listing"
                  value={address}
                  onChange={(e) => {
                    setAddress(e.target.value);
                    setLogState("idle");
                  }}
                />
              </div>
              <button
                className="btn btn-ghost"
                style={{ flex: "0 0 auto" }}
                disabled={!canLog || logState !== "idle"}
                title={canLog ? "Save this listing to My Listings" : "Enter a name and address first"}
                onClick={handleLog}
              >
                {logState === "logged"
                  ? "Logged ✓"
                  : logState === "dup"
                    ? "Already logged"
                    : "Log to My Listings"}
              </button>
            </div>
          </div>

          <div className="card">
            <div className="card-title">Automatic checks</div>
            {result.results
              .filter((r) => r.signal.kind === "auto")
              .map((r) => (
                <div className="question-row" key={r.signal.id}>
                  <div>
                    <div className="question-text">{r.signal.label}</div>
                    <div className="question-weight">{hasInput ? r.detail : "Waiting for a listing name…"}</div>
                  </div>
                  <span className={`chip ${r.triggered && hasInput ? "chip-danger" : "chip"}`}>
                    {r.triggered && hasInput ? `+${r.signal.weight}` : "0"}
                  </span>
                </div>
              ))}
          </div>

          <div className="card">
            <div className="card-title">Observable signals</div>
            <div className="muted" style={{ marginBottom: 4 }}>
              Answer from what you can see on the listing and a quick map search.
            </div>
            {questions.map((q) => {
              const answered = answers[q.id];
              return (
                <div className="question-row" key={q.id}>
                  <div>
                    <div className="question-text">{q.question}</div>
                    <div className="question-weight">
                      {q.label} · +{q.weight} pts
                    </div>
                  </div>
                  <div className="toggle-group">
                    <button
                      className={`toggle-btn ${answered === true ? "on" : ""}`}
                      onClick={() => setAnswer(q.id, true)}
                    >
                      Yes
                    </button>
                    <button
                      className={`toggle-btn ${answered === false ? "off" : ""}`}
                      onClick={() => setAnswer(q.id, false)}
                    >
                      No
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card score-panel">
          <ScoreDial score={hasInput ? result.score : 0} />
          {hasInput ? (
            <>
              <span
                className={`chip ${
                  result.score >= 65
                    ? "chip-danger"
                    : result.score >= 35
                      ? "chip-warn"
                      : result.score >= 15
                        ? "chip-blue"
                        : "chip-ok"
                }`}
              >
                {result.band.label}
              </span>
              <div className="score-verdict">{result.band.verdict}</div>
            </>
          ) : (
            <div className="score-verdict">Enter a listing name to begin the assessment.</div>
          )}

          <div className="signal-breakdown">
            <div className="eyebrow" style={{ marginBottom: 4 }}>
              Evidence
            </div>
            {result.results.map((r) => (
              <div key={r.signal.id} className={`breakdown-row ${r.triggered && hasInput ? "" : "idle"}`}>
                <span>{r.signal.label}</span>
                <span className="pts">{r.triggered && hasInput ? `+${r.signal.weight}` : "—"}</span>
              </div>
            ))}
          </div>
          <div className="muted" style={{ marginTop: 12, textAlign: "left" }}>
            {METHODOLOGY}
          </div>
        </div>
      </div>
    </div>
  );
}

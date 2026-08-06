import { METHODOLOGY, SIGNALS } from "../data/signals";

const STEPS: { title: string; body: string }[] = [
  {
    title: "Check the address first",
    body:
      "Copy the listing's address into Google Maps and switch to street view. A real restaurant has signage, windows, and tables. A ghost kitchen resolves to an industrial suite, a shared commissary, or the back of a different restaurant entirely.",
  },
  {
    title: "Search the brand outside the app",
    body:
      "Real restaurants leave a trail: a website, social media, local press, years of reviews. A brand that exists only inside DoorDash or UberEats — especially one with a polished logo and zero history — was assembled for the algorithm.",
  },
  {
    title: "Compare neighbors at the same address",
    body:
      "Search the address itself on the delivery app. If four differently-branded 'restaurants' serve wings, burgers, pasta, and poke from one suite, that's one kitchen wearing four masks. Log each one in My Listings and the tracker will flag the collision.",
  },
  {
    title: "Call the number",
    body:
      "If the phone answers with a different restaurant's name, you've confirmed the host kitchen. No phone number at all is almost as telling.",
  },
  {
    title: "Ghost isn't automatically bad",
    body:
      "It's Just Wings is cooked on Chili's lines under real corporate quality control; a celebrity brand licensed to an anonymous strip-mall kitchen is a different bet. The point is knowing who is actually cooking before you order.",
  },
];

export function FieldGuide() {
  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Training</div>
          <div className="page-title">Field Guide</div>
          <div className="page-desc">
            How to spot a ghost kitchen in under two minutes, and how the Ghost Score weighs the
            evidence.
          </div>
        </div>
      </div>

      <div className="card-grid">
        {STEPS.map((s, i) => (
          <div className="card" key={s.title}>
            <div className="guide-step">
              <div className="guide-num">{i + 1}</div>
              <div>
                <div className="card-title">{s.title}</div>
                <div style={{ fontSize: 12.5, marginTop: 4 }}>{s.body}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="section-gap">
        <div className="eyebrow" style={{ marginBottom: 8 }}>
          Scoring model
        </div>
        <div className="card">
          <div style={{ fontSize: 12.5, marginBottom: 10 }}>{METHODOLOGY}</div>
          {SIGNALS.map((s) => (
            <div className="question-row" key={s.id}>
              <div>
                <div className="question-text">{s.label}</div>
                <div className="question-weight">{s.description}</div>
              </div>
              <span className="chip chip-blue">+{s.weight}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

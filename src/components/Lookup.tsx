import { useMemo, useState } from "react";
import type { Brand, BrandStatus } from "../types";
import { BRANDS, OPERATORS } from "../data/dataset";
import { matchBrands } from "../lib/match";

const STATUS_CHIP: Record<BrandStatus, { cls: string; label: string }> = {
  active: { cls: "chip-danger", label: "Active Ghost" },
  defunct: { cls: "chip", label: "Defunct" },
  unknown: { cls: "chip-warn", label: "Status Unknown" },
};

const TYPE_LABEL: Record<Brand["type"], string> = {
  celebrity: "Celebrity brand",
  "chain-spinoff": "Chain spin-off",
  "virtual-operator": "Virtual operator network",
  independent: "Independent virtual brand",
};

function BrandCard({ brand, confidence }: { brand: Brand; confidence?: number }) {
  const status = STATUS_CHIP[brand.status];
  return (
    <div className="card">
      <div className="result-row">
        <div>
          <div className="card-title">{brand.name}</div>
          <div className="muted">{TYPE_LABEL[brand.type]}</div>
        </div>
        <span className={`chip ${status.cls}`}>{status.label}</span>
      </div>
      <dl className="kv">
        <dt>Really run by</dt>
        <dd>
          <strong>{brand.parentCompany}</strong>
        </dd>
        {brand.operator && (
          <>
            <dt>Platform</dt>
            <dd>{brand.operator}</dd>
          </>
        )}
        {brand.cookedBy && (
          <>
            <dt>Cooked by</dt>
            <dd>{brand.cookedBy}</dd>
          </>
        )}
        <dt>Intel</dt>
        <dd>{brand.notes}</dd>
      </dl>
      {confidence !== undefined && (
        <>
          <div className="confidence-bar">
            <div className="confidence-fill" style={{ width: `${Math.round(confidence * 100)}%` }} />
          </div>
          <div className="muted" style={{ marginTop: 4 }}>
            Match confidence {Math.round(confidence * 100)}%
          </div>
        </>
      )}
    </div>
  );
}

export function Lookup({ onRunScore }: { onRunScore: (name: string) => void }) {
  const [query, setQuery] = useState("");
  const matches = useMemo(() => matchBrands(query, BRANDS), [query]);
  const showingSearch = query.trim().length >= 2;

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Database</div>
          <div className="page-title">Brand Lookup</div>
          <div className="page-desc">
            Search any restaurant name you see on DoorDash, UberEats, or Grubhub against the
            documented virtual-brand database.
          </div>
        </div>
        <span className="chip chip-blue">{BRANDS.length} brands indexed</span>
      </div>

      <input
        className="input"
        placeholder="Type a restaurant name — e.g. 'MrBeast Burger', 'It's Just Wings'…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        autoFocus
      />

      <div className="section-gap">
        {showingSearch ? (
          matches.length > 0 ? (
            <div className="card-grid">
              {matches.slice(0, 6).map((m) => (
                <BrandCard key={m.brand.name} brand={m.brand} confidence={m.confidence} />
              ))}
            </div>
          ) : (
            <div className="card empty-state">
              <div className="glyph">◈</div>
              <div style={{ marginBottom: 10 }}>
                No match in the database. That doesn't clear it — check the observable signals.
              </div>
              <button className="btn btn-primary" onClick={() => onRunScore(query.trim())}>
                Run Ghost Score →
              </button>
            </div>
          )
        ) : (
          <>
            <div className="eyebrow" style={{ marginBottom: 8 }}>
              Known virtual brands
            </div>
            <div className="card-grid">
              {BRANDS.map((b) => (
                <BrandCard key={b.name} brand={b} />
              ))}
            </div>
            <div className="section-gap">
              <div className="eyebrow" style={{ marginBottom: 8 }}>
                Ghost kitchen operators
              </div>
              <div className="card-grid">
                {OPERATORS.map((op) => (
                  <div className="card" key={op.name}>
                    <div className="card-title">{op.name}</div>
                    <div style={{ fontSize: 12.5, marginTop: 4 }}>{op.description}</div>
                    {op.knownBrands && op.knownBrands.length > 0 && (
                      <div className="muted" style={{ marginTop: 6 }}>
                        Brands: {op.knownBrands.join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

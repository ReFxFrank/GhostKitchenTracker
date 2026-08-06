import type { Brand, Listing, ScoreBand, Signal } from "../types";
import { matchBrands } from "./match";
import { normalizeAddress, normalizeName } from "./normalize";

export interface SignalResult {
  signal: Signal;
  triggered: boolean;
  detail: string;
}

export interface ScoreResult {
  score: number;
  band: ScoreBand;
  results: SignalResult[];
}

export interface AutoContext {
  name: string;
  address: string;
  brands: Brand[];
  listings: Listing[];
}

const EXACT_THRESHOLD = 0.85;
const FUZZY_THRESHOLD = 0.5;

interface AutoFacts {
  bestConfidence: number;
  bestBrandLabel: string;
  othersAtAddress: string[];
  knownBrandAtAddress: string | null;
}

/** Compute the database-derived facts once, shared across auto signals. */
function gatherFacts(ctx: AutoContext): AutoFacts {
  const best = matchBrands(ctx.name, ctx.brands)[0];
  const addr = normalizeAddress(ctx.address);
  const selfName = normalizeName(ctx.name);

  const othersAtAddress: string[] = [];
  let knownBrandAtAddress: string | null = null;
  if (addr) {
    const seen = new Set<string>();
    for (const l of ctx.listings) {
      if (normalizeAddress(l.address) !== addr) continue;
      const lName = normalizeName(l.name);
      if (lName === selfName || seen.has(lName)) continue;
      seen.add(lName);
      othersAtAddress.push(l.name);
      if (!knownBrandAtAddress) {
        const m = matchBrands(l.name, ctx.brands)[0];
        if (m && m.confidence >= EXACT_THRESHOLD) knownBrandAtAddress = m.brand.name;
      }
    }
  }

  return {
    bestConfidence: best?.confidence ?? 0,
    bestBrandLabel: best ? `${best.brand.name} (${best.brand.parentCompany})` : "",
    othersAtAddress,
    knownBrandAtAddress,
  };
}

function evaluateAutoSignal(signal: Signal, facts: AutoFacts): SignalResult {
  switch (signal.id) {
    case "known-brand-exact-match":
      if (facts.bestConfidence >= EXACT_THRESHOLD) {
        return { signal, triggered: true, detail: `Matches ${facts.bestBrandLabel} in the database.` };
      }
      return { signal, triggered: false, detail: "No exact match in the virtual-brand database." };

    case "known-brand-fuzzy-match":
      // Never stacks with an exact match — only the stronger signal counts.
      if (facts.bestConfidence >= EXACT_THRESHOLD) {
        return { signal, triggered: false, detail: "Superseded by the exact match above." };
      }
      if (facts.bestConfidence >= FUZZY_THRESHOLD) {
        return {
          signal,
          triggered: true,
          detail: `Resembles ${facts.bestBrandLabel} — possible regional variant.`,
        };
      }
      return { signal, triggered: false, detail: "No close match in the database." };

    case "known-operator-address":
      if (facts.knownBrandAtAddress) {
        return {
          signal,
          triggered: true,
          detail: `This address also hosts ${facts.knownBrandAtAddress}, a known virtual brand.`,
        };
      }
      return { signal, triggered: false, detail: "No known virtual brand logged at this address." };

    case "address-collision":
      if (facts.othersAtAddress.length > 0) {
        const n = facts.othersAtAddress.length;
        return {
          signal,
          triggered: true,
          detail: `${n} other logged brand${n > 1 ? "s" : ""} share this address.`,
        };
      }
      return { signal, triggered: false, detail: "No other logged listings at this address." };

    default:
      return { signal, triggered: false, detail: "Not evaluated." };
  }
}

export function computeScore(
  ctx: AutoContext,
  answers: Record<string, boolean>,
  signals: Signal[],
  bands: ScoreBand[],
): ScoreResult {
  const facts = gatherFacts(ctx);

  const results: SignalResult[] = signals.map((signal) => {
    if (signal.kind === "auto") return evaluateAutoSignal(signal, facts);
    const yes = answers[signal.id] === true;
    return {
      signal,
      triggered: yes,
      detail: yes ? "You reported this signal." : "Not observed.",
    };
  });

  const raw = results.reduce((sum, r) => sum + (r.triggered ? r.signal.weight : 0), 0);
  const score = Math.max(0, Math.min(100, Math.round(raw)));

  const sorted = [...bands].sort((a, b) => b.min - a.min);
  const band = sorted.find((b) => score >= b.min) ?? sorted[sorted.length - 1];

  return { score, band, results };
}

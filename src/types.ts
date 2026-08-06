export type BrandType = "celebrity" | "chain-spinoff" | "virtual-operator" | "independent";
export type BrandStatus = "active" | "defunct" | "unknown";

export interface Brand {
  name: string;
  aliases?: string[];
  parentCompany: string;
  /** Virtual-brand platform behind it (Virtual Dining Concepts, Nextbite, ...), if any. */
  operator?: string;
  /** Where the food is actually cooked. */
  cookedBy?: string;
  type: BrandType;
  status: BrandStatus;
  notes: string;
}

export interface Operator {
  name: string;
  description: string;
  knownBrands?: string[];
}

export type SignalKind = "auto" | "question";

export interface Signal {
  id: string;
  label: string;
  description: string;
  /** Points contributed to the 0-100 ghost score when triggered. */
  weight: number;
  kind: SignalKind;
  /** For kind === "question": the yes/no prompt shown to the user. */
  question?: string;
}

export interface ScoreBand {
  /** Band applies when score >= min (bands checked highest-first). */
  min: number;
  label: string;
  verdict: string;
}

export interface Listing {
  id: string;
  name: string;
  address: string;
  platform: string;
  addedAt: string;
}

export interface BrandMatch {
  brand: Brand;
  /** 0-1 confidence of the name match. */
  confidence: number;
  matchedOn: "name" | "alias";
}

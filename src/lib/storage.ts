import type { Listing } from "../types";

const KEY = "gkt.listings.v1";

function isListing(value: unknown): value is Listing {
  if (!value || typeof value !== "object") return false;
  const l = value as Record<string, unknown>;
  return (
    typeof l.id === "string" &&
    typeof l.name === "string" &&
    typeof l.address === "string" &&
    typeof l.platform === "string" &&
    typeof l.addedAt === "string"
  );
}

export function loadListings(): Listing[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter(isListing) : [];
  } catch {
    return [];
  }
}

export function saveListings(listings: Listing[]): void {
  localStorage.setItem(KEY, JSON.stringify(listings));
}

export function newListingId(): string {
  return `l_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

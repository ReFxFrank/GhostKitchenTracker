import type { Listing } from "../types";
import { normalizeAddress, normalizeName } from "./normalize";

/**
 * Normalized addresses that host two or more differently-named listings.
 * Names are compared with normalizeName — the same identity function the
 * Ghost Score uses — so the two views can never disagree about a collision.
 */
export function collisionAddresses(listings: Listing[]): Set<string> {
  const byAddress = new Map<string, Set<string>>();
  for (const l of listings) {
    const addr = normalizeAddress(l.address);
    const name = normalizeName(l.name);
    if (!addr || !name) continue;
    if (!byAddress.has(addr)) byAddress.set(addr, new Set());
    byAddress.get(addr)!.add(name);
  }
  const flagged = new Set<string>();
  for (const [addr, names] of byAddress) {
    if (names.size >= 2) flagged.add(addr);
  }
  return flagged;
}

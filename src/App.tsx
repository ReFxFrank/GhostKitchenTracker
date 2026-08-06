import { useEffect, useMemo, useState } from "react";
import type { Listing } from "./types";
import { loadListings, newListingId, saveListings } from "./lib/storage";
import { collisionAddresses } from "./lib/collisions";
import { normalizeAddress, normalizeName } from "./lib/normalize";
import { Lookup } from "./components/Lookup";
import { GhostScore } from "./components/GhostScore";
import { Listings } from "./components/Listings";
import { FieldGuide } from "./components/FieldGuide";
import { BRANDS } from "./data/dataset";

type View = "lookup" | "score" | "listings" | "guide";

const NAV: { id: View; label: string; icon: string; key: string }[] = [
  { id: "lookup", label: "Brand Lookup", icon: "◈", key: "1" },
  { id: "score", label: "Ghost Score", icon: "◎", key: "2" },
  { id: "listings", label: "My Listings", icon: "▤", key: "3" },
  { id: "guide", label: "Field Guide", icon: "✦", key: "4" },
];

export default function App() {
  const [view, setView] = useState<View>("lookup");
  const [listings, setListings] = useState<Listing[]>(() => loadListings());
  // Prefill is an event, not a value — the nonce makes re-running the same
  // name from Lookup reset the assessment again.
  const [scorePrefill, setScorePrefill] = useState({ name: "", nonce: 0 });

  useEffect(() => {
    saveListings(listings);
  }, [listings]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const target = e.target as HTMLElement | null;
      const tag = target?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      const item = NAV.find((n) => n.key === e.key);
      if (item) setView(item.id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const collisionCount = useMemo(() => collisionAddresses(listings).size, [listings]);

  const runScore = (name: string) => {
    setScorePrefill((p) => ({ name, nonce: p.nonce + 1 }));
    setView("score");
  };

  /** Log a listing from the Ghost Score screen; skips exact duplicates. */
  const logListing = (name: string, address: string): boolean => {
    const dup = listings.some(
      (l) =>
        normalizeName(l.name) === normalizeName(name) &&
        normalizeAddress(l.address) === normalizeAddress(address),
    );
    if (dup) return false;
    const entry: Listing = {
      id: newListingId(),
      name: name.trim(),
      address: address.trim(),
      platform: "Other",
      addedAt: new Date().toISOString(),
    };
    setListings((prev) => [entry, ...prev]);
    return true;
  };

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-title">
            Ghost<span>Kitchen</span>Tracker
          </div>
          <div className="brand-sub">ReFx Systems</div>
        </div>
        {NAV.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${view === item.id ? "active" : ""}`}
            onClick={() => setView(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span style={{ flex: 1 }}>{item.label}</span>
            {item.id === "listings" && collisionCount > 0 && (
              <span className="nav-badge">{collisionCount}</span>
            )}
            <span className="nav-key">{item.key}</span>
          </button>
        ))}
        <div className="sidebar-foot">
          DB: {BRANDS.length} brands · {listings.length} logged listing
          {listings.length === 1 ? "" : "s"}
        </div>
      </aside>
      <main className="main">
        <div style={{ display: view === "lookup" ? "block" : "none" }}>
          <Lookup onRunScore={runScore} />
        </div>
        <div style={{ display: view === "score" ? "block" : "none" }}>
          <GhostScore listings={listings} prefill={scorePrefill} onLog={logListing} />
        </div>
        <div style={{ display: view === "listings" ? "block" : "none" }}>
          <Listings listings={listings} setListings={setListings} />
        </div>
        <div style={{ display: view === "guide" ? "block" : "none" }}>
          <FieldGuide />
        </div>
      </main>
    </div>
  );
}

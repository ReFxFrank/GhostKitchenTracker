import { useMemo, useRef, useState } from "react";
import type { Listing } from "../types";
import { BRANDS } from "../data/dataset";
import { matchBrands } from "../lib/match";
import { normalizeAddress, normalizeName } from "../lib/normalize";
import { collisionAddresses } from "../lib/collisions";
import { isListing, newListingId } from "../lib/storage";

const PLATFORMS = ["DoorDash", "UberEats", "Grubhub", "Postmates", "Other"];

interface Props {
  listings: Listing[];
  setListings: (update: (prev: Listing[]) => Listing[]) => void;
}

export function Listings({ listings, setListings }: Props) {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [platform, setPlatform] = useState(PLATFORMS[0]);
  const [importNote, setImportNote] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  const exportListings = () => {
    const blob = new Blob([JSON.stringify(listings, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "gkt-listings.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const importListings = async (file: File) => {
    try {
      const parsed = JSON.parse(await file.text());
      if (!Array.isArray(parsed)) {
        setImportNote("Import failed: file is not a listings export.");
        return;
      }
      const incoming = parsed.filter(isListing);
      const key = (l: Listing) => `${normalizeName(l.name)}|${normalizeAddress(l.address)}`;
      const seen = new Set(listings.map(key));
      const fresh = incoming.filter((l) => {
        const k = key(l);
        if (seen.has(k)) return false;
        seen.add(k);
        return true;
      });
      const added = fresh.length;
      if (added > 0) setListings((prev) => [...fresh, ...prev]);
      const dups = incoming.length - added;
      const invalid = parsed.length - incoming.length;
      setImportNote(
        `Imported ${added} listing${added === 1 ? "" : "s"}` +
          (dups > 0 ? ` (${dups} duplicate${dups === 1 ? "" : "s"} skipped)` : "") +
          (invalid > 0 ? ` — ${invalid} invalid entr${invalid === 1 ? "y" : "ies"} ignored` : ""),
      );
    } catch {
      setImportNote("Import failed: not valid JSON.");
    }
  };

  const collisions = useMemo(() => collisionAddresses(listings), [listings]);

  const addListing = () => {
    if (name.trim().length < 2 || address.trim().length < 4) return;
    const entry: Listing = {
      id: newListingId(),
      name: name.trim(),
      address: address.trim(),
      platform,
      addedAt: new Date().toISOString(),
    };
    setListings((prev) => [entry, ...prev]);
    setName("");
    setAddress("");
  };

  const remove = (id: string) => setListings((prev) => prev.filter((l) => l.id !== id));

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Surveillance</div>
          <div className="page-title">My Listings</div>
          <div className="page-desc">
            Log the name and address of listings you see in the wild. When two brands share one
            address, you've found a ghost kitchen — the app flags it automatically.
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {collisions.size > 0 && (
            <span className="chip chip-danger">
              {collisions.size} collision address{collisions.size > 1 ? "es" : ""}
            </span>
          )}
          <button
            className="btn btn-ghost"
            disabled={listings.length === 0}
            title="Download your log as JSON"
            onClick={exportListings}
          >
            Export
          </button>
          <button
            className="btn btn-ghost"
            title="Import a previously exported JSON log"
            onClick={() => fileInput.current?.click()}
          >
            Import
          </button>
          <input
            ref={fileInput}
            type="file"
            accept=".json,application/json"
            style={{ display: "none" }}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) importListings(file);
              e.target.value = "";
            }}
          />
        </div>
      </div>
      {importNote && (
        <div className="muted" style={{ marginBottom: 10 }}>
          {importNote}
        </div>
      )}

      <div className="card">
        <div className="form-row">
          <div>
            <label className="field-label">Listing name</label>
            <input
              className="input"
              placeholder="e.g. Wild Wild Wings"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addListing()}
            />
          </div>
          <div>
            <label className="field-label">Address</label>
            <input
              className="input"
              placeholder="e.g. 4501 Industrial Pkwy Ste B"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addListing()}
            />
          </div>
          <div style={{ flex: "0 0 130px" }}>
            <label className="field-label">Platform</label>
            <select className="select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
              {PLATFORMS.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" style={{ flex: "0 0 auto" }} onClick={addListing}>
            Log it
          </button>
        </div>
      </div>

      <div className="section-gap">
        {listings.length === 0 ? (
          <div className="card empty-state">
            <div className="glyph">▤</div>
            Nothing logged yet. Next time a suspicious listing catches your eye, capture its name
            and address here — collisions build the case for you.
          </div>
        ) : (
          <div className="card" style={{ padding: "6px 6px 2px" }}>
            <div className="table-scroll">
              <table className="listing-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Address</th>
                  <th>Platform</th>
                  <th>Flags</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {listings.map((l) => {
                  const collided = collisions.has(normalizeAddress(l.address));
                  const dbMatch = matchBrands(l.name, BRANDS)[0];
                  return (
                    <tr key={l.id}>
                      <td className="listing-name">{l.name}</td>
                      <td>{l.address}</td>
                      <td>{l.platform}</td>
                      <td>
                        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                          {collided && <span className="chip chip-danger">Collision</span>}
                          {dbMatch && dbMatch.confidence >= 0.85 && (
                            <span className="chip chip-warn">Known brand</span>
                          )}
                          {!collided && !(dbMatch && dbMatch.confidence >= 0.85) && (
                            <span className="chip">Clear</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <button className="btn btn-danger-ghost" onClick={() => remove(l.id)}>
                          Remove
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

import { useMemo, useState } from "react";
import type { Listing } from "../types";
import { BRANDS } from "../data/dataset";
import { matchBrands } from "../lib/match";
import { normalizeAddress } from "../lib/normalize";
import { collisionAddresses } from "../lib/collisions";
import { newListingId } from "../lib/storage";

const PLATFORMS = ["DoorDash", "UberEats", "Grubhub", "Postmates", "Other"];

interface Props {
  listings: Listing[];
  setListings: (update: (prev: Listing[]) => Listing[]) => void;
}

export function Listings({ listings, setListings }: Props) {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [platform, setPlatform] = useState(PLATFORMS[0]);

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
        {collisions.size > 0 && (
          <span className="chip chip-danger">
            {collisions.size} collision address{collisions.size > 1 ? "es" : ""}
          </span>
        )}
      </div>

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

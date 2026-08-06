# GhostKitchenTracker

A consumer tool that identifies which delivery-app listings (DoorDash, UberEats, Grubhub) are actually **ghost kitchens** — virtual brands cooked by someone other than the name on the listing.

Client-side Vite + React + TypeScript SPA, no backend. Styled in the ReFx Glassy Design system.

## Features

- **Brand Lookup** — fuzzy-search a bundled, fact-checked database of 52 documented virtual brands (celebrity brands, chain spin-offs, operator networks) and 14 ghost kitchen operators. Shows who really runs the brand, who cooks the food, and its current status.
- **Ghost Score** — enter any listing's name + address, answer a short observable-signal checklist, and get a 0–100 likelihood score with a verdict band and per-signal evidence breakdown. Database matches are weighted heaviest; aesthetic cues barely nudge it.
- **My Listings** — log listings you see in the wild (persisted in localStorage). The app flags **address collisions** — multiple brand names sharing one address, the defining ghost kitchen fingerprint — and matches against the known-brand database.
- **Field Guide** — how to spot a ghost kitchen in under two minutes, plus the full scoring model.

Keyboard: press `1`–`4` to switch screens.

## Development

```bash
npm install
npm run dev
```

Dev server runs at http://localhost:5183. `npm run build` type-checks and produces a static bundle in `dist/`.

## Data

`src/data/dataset.ts` is compiled from public reporting and adversarially fact-checked (last refresh: August 2026). Virtual brands shut down often — `status: "unknown"` means the last public information was ambiguous. The scoring model lives in `src/data/signals.ts`.

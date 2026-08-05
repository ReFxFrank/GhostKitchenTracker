# Legal posture

_This document states what SEANCE asserts, what it does not assert, where its
data comes from, and how to dispute or remove a record. It is a public
commitment, not boilerplate. Last revised: 2026-08-05._

## What this site asserts — and what it does not

SEANCE is a structured index of public records. For a given New York City
building it shows, side by side:

1. **Government records**: establishments permitted by the NYC Department of
   Health and Mental Hygiene (DOHMH) at that building, their inspection
   history, and violation text reproduced **verbatim** from the city's own
   published dataset.
2. **Open place data**: business names that commercial place datasets locate at
   the same building.
3. **Evidence-scored links**: where the site displays a link between a brand
   name and a kitchen, it displays — on the same page — the specific records
   supporting that link, each with a source name and retrieval date.

The site does **not**:

- Say any establishment is clean, dirty, safe, or unsafe, or tell anyone where
  to eat. No score, index, or grade of our own invention exists anywhere on the
  site.
- Summarize, paraphrase, or characterize health inspection findings. Violation
  text is shown exactly as the city published it, linked back to the official
  DOHMH record, or it is not shown at all.
- Assert a brand→kitchen relationship without a displayed evidence trail. A
  link whose evidence cannot be shown is not rendered. Links below the
  publication threshold are stored but never displayed.
- Claim that operating multiple brand names from one licensed kitchen is
  illegal, deceptive, or wrong. It is a lawful and common practice; roughly 41%
  of independent US restaurants run at least one virtual brand.

## Confidence tiers and the display rule

Every displayed link carries a tier — `CONFIRMED`, `LIKELY`, or `POSSIBLE` —
computed by a deterministic, published rule (see `METHODOLOGY.md`). Two
structural rules bound what the site will say:

- Health inspection data appears on a **brand** page only at `CONFIRMED`. At
  lower tiers, health records appear only on the **building** page, reached by
  explicit click, with the tier stated. "This brand had violations" requires
  certainty about the brand; "this address has these public records" does not.
- The operator's own words outrank our inference. A verified operator statement
  is the highest-weighted evidence in the system.

## Data sources and licenses

| Source | What we take | License / terms |
|---|---|---|
| NYC Open Data — DOHMH Restaurant Inspection Results (`43nn-pn8j`) | Establishments, inspections, verbatim violations, BIN/BBL | NYC Open Data terms; attributed to DOHMH |
| NYC Open Data — PLUTO (`64uk-42ks`) | Building attributes by BBL | NYC Open Data terms; attributed to DCP |
| NYC Open Data — DCWP Issued Licenses (`w7w3-xahh`) | Legal entity and DBA corroboration | NYC Open Data terms; attributed to DCWP |
| Overture Maps Foundation — Places theme (pinned release, see `SOURCES.md`) | Place names, categories, phones, websites, coordinates | CDLA Permissive 2.0 / Apache 2.0 per record |
| OpenStreetMap via Protomaps/PMTiles | Basemap display **only** — never joined into the places table | ODbL; © OpenStreetMap contributors |

Full attribution obligations: `ATTRIBUTION.md`. Dataset verification records:
`SOURCES.md`. Every raw snapshot is dated and immutable, so any statement on
the site can be traced to what a specific source published on a specific date.

## Disputes, corrections, and takedowns

**If you operate a kitchen or brand shown on this site**, you have three
standing options, none of which require a lawyer:

1. **Claim** — verify control of the establishment (via contact details already
   present in the city's own record) and confirm, deny, or correct a displayed
   link, optionally adding context in your own words.
2. **Denial** — a verified operator denial **ends the matter**. The link is
   removed via the exclusion registry and stays removed. We do not adjudicate
   against an operator's sworn word; the removal takes effect on the next
   deploy.
3. **Takedown request** — anyone may request removal of any record. Requests
   are logged with received/resolved dates and outcomes.

Contact for all three: `TODO(frank): publish the takedown contact address when
the domain is registered (Phase 6). Until the site is publicly reachable there
is nothing displayed to dispute; this placeholder must be resolved before
launch — it is a launch blocker, tracked in the Phase 6 checklist.`

Corrections to underlying government records should be directed to the issuing
agency; we display what the city publishes and will reflect the city's
correction at the next weekly refresh.

## Posture notes

- SEANCE republishes and organizes records already published by the City of
  New York, and clearly-labeled data from openly licensed place datasets. Its
  method is public (`METHODOLOGY.md`), its scoring is deterministic and
  reproducible from dated snapshots, and its strongest evidence class is the
  operator's own verified statement.
- Food-safety transparency and the traceability of commercial food operations
  are matters of public interest. New York's anti-SLAPP statute (as amended
  2020) covers public-interest speech broadly and includes fee-shifting.
  `TODO(frank): one hour with a media/First Amendment attorney before launch to
  confirm this read — Phase 6 gate, not optional.`
- This site is not affiliated with, endorsed by, or acting for the City of New
  York or any agency.

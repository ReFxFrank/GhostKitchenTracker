# Methodology

_This page explains, in plain language, how this site decides what to display
and how confident it is. It is linked from the footer of every page. The
scoring rules below are deterministic: given the same source snapshots, they
produce the same results, every time. There is no machine-learning model and no
language model anywhere in the data path. Last revised: 2026-08-05._

## What we're looking at

Delivery platforms allow one licensed kitchen to list itself under many brand
names. New York City's health department licenses the **address and operator**
— not the brand name on the app. So the city's inspection dataset and the
delivery apps describe the same physical world with different vocabularies.

Two shapes exist:

- **Type A — purpose-built facilities.** Commissary buildings where many
  separately-permitted operators cook under one roof. These are visible in
  permit data directly: many permits, one building.
- **Type B — an existing restaurant running virtual brands** off its single
  existing permit. This is by far the more common case, and it is *invisible*
  in permit data: the health record shows one establishment, and the virtual
  brand names appear nowhere in it.

## The method: the name gap

Because Type B leaves no trace in permit data, we look for the **gap**:

1. **Baseline** — every establishment the health department (DOHMH) licenses at
   a given building. NYC's inspection dataset identifies buildings with an
   exact key (the BIN — Building Identification Number), which makes this
   precise rather than fuzzy.
2. **Comparison** — business names that open place datasets (primarily Overture
   Maps, a consortium dataset built from Meta, Microsoft, Foursquare and other
   sources) locate at that same building.
3. **The gap** — a name present in place data at a building, with no matching
   health-department record at that building, is a *candidate* virtual brand.
   Candidate means candidate: it enters a review queue, not the website.

Name matching is deliberately forgiving ("Joe's Pizza" and "Joes Pizza Inc" are
the same name) so that trivial spelling differences don't create false gaps.

We filter out buildings where the method doesn't make sense — food courts,
hotels, hospitals, schools, transit hubs — using the city's own building
classification data, and we drop place records the source itself marks as
low-confidence or not currently operating.

### What this method cannot see

A virtual brand that exists *only* inside a delivery app — with no web
presence of any kind — may not appear in any place dataset. We measure this
ceiling directly (by checking what fraction of independently-documented virtual
brands appear in our place data at all) and publish the result here.

**Preliminary measurement (2026-08-05, pending human review of the seed
registry):** of 51 independently documented virtual brands, 24 (47%) had a
matching record in the Overture places extract for NYC — with two of those
hits looking like coincidental name collisions, so the honest range is
43–47%. Several misses are brands that had already shut down by the
measurement date, which place data (a snapshot of the present) legitimately
no longer lists — so this number likely *understates* coverage of currently
operating brands. Per the method's own rules this lands in the "supplement
and re-measure" band; the re-measurement with a second place dataset
(Foursquare OS Places) is pending. This site indexes what can be seen; it
does not claim completeness.

## From candidate to displayed link: evidence families

A candidate becomes a displayed link only through evidence, and evidence is
organized into **families** — groups of signals that are correlated with each
other and therefore must not stack:

| Family | Example evidence | Family weight (max) |
|---|---|---|
| Testimony | Operator's verified claim or public statement (100); user report (5) | 100 |
| Location | Same building ID (50); exact address match (50); coordinates within 25m (30) | 50 |
| Legal entity | Matching legal entity in city license filings | 45 |
| Phone | Exact phone match between place record and health record | 40 |
| Menu | Menu fingerprint similarity (40 high / 25 medium) | 40 |
| Media | Identical imagery (perceptual hash match) | 35 |

**The score is the sum over families of the single strongest piece of evidence
in each family.** Two location signals do not count twice — being in the same
building and having the same address is one fact, not two. Ten user reports
still score 5. A verified operator statement makes user reports in the same
family worth nothing extra. This is deliberate: the rule makes double-counting
impossible rather than merely discouraged.

Scores are integer sums. There are no percentages, no decimals, and no
model-estimated probabilities anywhere in the system. The arithmetic is shown
with every link.

## Tiers

Ranges cascade top-down — a link is placed in the first tier whose conditions
it meets:

| Tier | Conditions | What it means on the site |
|---|---|---|
| `CONFIRMED` | Score ≥ 100 **and** at least one documentary evidence item | Full display; health records may appear on the brand page |
| `LIKELY` | Score ≥ 60 with at least two independent evidence families | Link and evidence shown; health records only on the building page |
| `POSSIBLE` | Score ≥ 35 | Link and evidence shown; health records only on the building page |
| `SUPPRESSED` | Below 35 | Stored internally; never rendered |

"Documentary" evidence means: a verified operator claim, an operator's public
statement, a legal-entity match in government filings, or a shared building ID
in government records. A high score assembled purely from soft signals cannot
reach `CONFIRMED` — and note the cascade: a score of 100+ *without* documentary
evidence lands at `LIKELY` at best.

The tier is computed by the database itself from the score, the family count,
and the documentary flag. There is no code path that can set a tier by hand.

## The display rule for health data

Health inspection records are reproduced **verbatim** from the city's dataset —
never summarized, never characterized, never editorialized — and linked to the
official city record.

They appear in two places, under different standards:

- **Building pages** show the full public record for that address: every
  establishment ever permitted there, inspections, and verbatim violations.
  This is a straight view of the city's own data.
- **Brand pages** show health records **only at `CONFIRMED`**. Saying "brand X
  had violations" requires certainty that brand X is actually that kitchen;
  below `CONFIRMED`, we don't have it, so the brand page shows the link and its
  evidence and stops there.

## Corrections and the operator's word

- Operators can **claim** their kitchen through verification against contact
  details already present in the city's record, then confirm, deny, or correct
  any displayed link.
- A verified **denial removes the link**, permanently, without adjudication.
  The operator's word ends the matter.
- A verified **confirmation** is the strongest evidence the system accepts —
  stronger than anything we infer.
- Anyone can report an observed brand→address pairing through a plain form.
  Reports carry near-zero weight (5), are never sufficient alone, and are
  always human-reviewed. There is no automated collection from delivery
  platforms — by permanent policy, not oversight.

## Reproducibility

- Every source fetch is stored as a dated, immutable snapshot; the site can
  state what a given source said on a given date.
- The place dataset release is pinned by version (see `SOURCES.md`), not
  "latest".
- The linkage rules above are the complete set. If this page and the site's
  behavior ever disagree, that is a bug — in the site.

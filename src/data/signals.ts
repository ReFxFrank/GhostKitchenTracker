import type { ScoreBand, Signal } from "../types";

/**
 * Ghost Score model. Database signals carry up to 60 points (exact and fuzzy
 * brand matches never stack — only the stronger one counts); observable
 * signals the user answers contribute the remaining 30.
 */
export const SIGNALS: Signal[] = [
  {
    id: "known-brand-exact-match",
    label: "Exact match in virtual-brand database",
    description:
      "The listing name matches a brand in the database of confirmed virtual/delivery-only brands. The strongest possible signal — these brands are already verified ghost kitchen concepts.",
    weight: 35,
    kind: "auto",
  },
  {
    id: "known-brand-fuzzy-match",
    label: "Close match to a known virtual brand",
    description:
      "The listing name closely resembles a known virtual brand. Virtual brands often run regional name variants, so a near-match is strong but not conclusive. Applied only when there is no exact match.",
    weight: 10,
    kind: "auto",
  },
  {
    id: "known-operator-address",
    label: "Address hosts a known virtual brand",
    description:
      "Another listing you've logged at this same address matches the virtual-brand database — meaning this address is already operating as a multi-brand ghost kitchen.",
    weight: 15,
    kind: "auto",
  },
  {
    id: "address-collision",
    label: "Multiple listings share this address",
    description:
      "Your log already contains a differently-named restaurant at this same address. One kitchen wearing many brand names is the defining pattern of ghost kitchen operations.",
    weight: 10,
    kind: "auto",
  },
  {
    id: "no-physical-storefront",
    label: "No physical storefront",
    description:
      "Real restaurants show up as a customer-facing storefront on maps — with dining photos, hours, and walk-in reviews. A brand you can order from but can't visit is a hallmark of a ghost kitchen.",
    weight: 8,
    kind: "question",
    question:
      "When you search the restaurant name on Google Maps, is there no physical storefront customers can visit (no listing, or only a warehouse/office building)?",
  },
  {
    id: "delivery-apps-only",
    label: "Exists only on delivery apps",
    description:
      "Established brick-and-mortar restaurants almost always have their own website or active social media. A brand whose entire footprint is delivery-app listings was likely created for delivery apps.",
    weight: 6,
    kind: "question",
    question:
      "Does the brand appear only on delivery apps, with no website or real social media presence of its own?",
  },
  {
    id: "receipt-name-mismatch",
    label: "Reviews mention a different restaurant name",
    description:
      "When reviewers report receipts, bags, or packaging bearing a different restaurant's name, the food is being cooked by another kitchen operating under a virtual brand — direct eyewitness evidence.",
    weight: 6,
    kind: "question",
    question:
      "Do any reviews mention receiving food in packaging, bags, or receipts from a differently-named restaurant?",
  },
  {
    id: "industrial-suite-address",
    label: "Suite/unit in an industrial area",
    description:
      "Ghost kitchens cluster in cheap commercial and industrial space — suite numbers in warehouse districts, strip-mall back units, or parking-lot facilities rather than normal retail frontage.",
    weight: 5,
    kind: "question",
    question:
      "Is the listed address a suite or unit number in an industrial park, warehouse district, or other non-retail area?",
  },
  {
    id: "recent-polished-menu",
    label: "New listing with a large polished menu",
    description:
      "Real restaurants build menus and review history over time. A listing that appeared recently yet launched with a big, professionally formatted menu and few reviews suggests a pre-packaged brand kit.",
    weight: 3,
    kind: "question",
    question:
      "Did the listing appear recently (few or no reviews) while already offering a large, polished, professional-looking menu?",
  },
  {
    id: "generic-stock-photos",
    label: "Generic stock-style photos",
    description:
      "Licensed brand kits ship with studio-perfect, generic food photography. This is a weak aesthetic cue on its own — plenty of real restaurants use stock photos too — so it only nudges the score.",
    weight: 2,
    kind: "question",
    question:
      "Do the food photos look like generic stock images (studio-perfect, inconsistent styles, or images you can reverse-image-search on other sites)?",
  },
];

/** Bands are matched highest `min` first. */
export const SCORE_BANDS: ScoreBand[] = [
  {
    min: 65,
    label: "Confirmed Ghost",
    verdict:
      "Multiple near-conclusive signals line up — this listing is a ghost kitchen or virtual brand in all but name.",
  },
  {
    min: 35,
    label: "Probably Ghost",
    verdict:
      "Strong indicators — including likely database evidence — suggest this listing is a virtual brand operating out of another kitchen.",
  },
  {
    min: 15,
    label: "Uncertain",
    verdict:
      "A few ghost-kitchen traits are present, but nothing decisive — it could be a small real restaurant with a thin online presence.",
  },
  {
    min: 0,
    label: "Likely Brick & Mortar",
    verdict:
      "Little to nothing here matches ghost kitchen patterns — this is most likely a real restaurant you could walk into.",
  },
];

export const METHODOLOGY =
  "The Ghost Score adds up weighted evidence from two sources. Database signals — matches against the catalog of known virtual brands and addresses hosting multiple logged listings — carry most of the weight because they are near-conclusive. The remaining points come from things you can check yourself, weighted by how diagnostic they are: a missing storefront counts more than soft aesthetic cues like stock photos. Exact and fuzzy brand matches never stack — only the stronger one counts. The score is a likelihood estimate, not proof.";

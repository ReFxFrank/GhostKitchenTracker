# Preliminary coverage gate — 2026-08-05

_Automated preliminary run of the Phase 1 kill test (brief §8). **Pending
Frank's review of the seed registry before the gate is treated as final.**_

## Setup

- Registry: 51 virtual brands, every one seeded with source-verified citations
  (each URL fetched and checked to name the brand and support the operator
  attribution; three URLs independently re-verified by hand).
- Place data: Overture Maps places, pinned release 2026-07-22.0, full NYC bbox
  extract of 450,887 rows (2026-08-05).
- Matcher: exact normalized name, directional token containment (brand tokens
  contained in place name, <=2 extra tokens, 'the'-insensitive), or
  token_sort_ratio >= 90. Place-name-is-subset-of-brand does NOT count.

## Result: 24/51 = 47.1% — MARGINAL band (30–50%)

| Brand | Result | Best matches (score, category) |
|---|---|---|
| Another Wing | HIT | Another Wing By Dj Khaled (100, chicken_wings_restaurant) |
| Arthur Treacher's | HIT | Arthur Treachers (100, seafood_restaurant) |
| Bad Ass Breakfast Burritos | MISS | — |
| Bad Mutha Clucka | MISS | — |
| Buddy V's Cake Slice | HIT | Buddy V's Cake Slice (100, food_delivery_service) |
| Chicken n' Biscuits by Cracker Barrel | MISS | — |
| Chicken Sammy's | MISS | — |
| City Dumpling | HIT | City Dumpling (100, asian_restaurant) |
| Conviction Chicken | MISS | — |
| Cosmic Wings | MISS | — |
| Fresh Set | MISS | — |
| George Lopez Tacos | MISS | — |
| Grilled Cheese Society | HIT | Grilled Cheese Society (100, sandwich_shop) |
| Guy Fieri's Flavortown Kitchen | HIT | Guy Fieri's Flavortown Kitchen (100, burger_restaurant) |
| Hootie's Burger Bar | MISS | — |
| HotBox by Wiz | MISS | — |
| It's Just Wings | HIT | It's Just Wings (100, chicken_wings_restaurant) |
| Krispy Rice | MISS | — |
| Man Vs Fries | HIT | Man Vs Fries (100, food_delivery_service) |
| Mariah's Cookies | HIT | Mariah's Cookies (100, desserts) |
| Mario's Tortas Lopez | MISS | — |
| Monster Mac | HIT | Monster Mac (100, restaurant) |
| MrBeast Burger | HIT | MrBeast Burger (100, burger_restaurant); Mr. Beast Burger (100, beverage_store) |
| Muncheechos | MISS | — |
| NASCAR Refuel | HIT | Nascar Refuel (100, restaurant) |
| Neighborhood Wings | MISS | — |
| Nice Day | HIT | Nice Day (100, discount_store) |
| Packed Bowls by Wiz Khalifa | MISS | — |
| Pardon My Cheesesteak | HIT | Pardon My Cheesesteak (100, restaurant) |
| Pasqually's Pizza & Wings | MISS | — |
| Pauly D's Italian Subs | MISS | — |
| Pizzaoki | MISS | — |
| Plant B | HIT | Plan B (92, sports_bar) |
| Rotisserie Roast | MISS | — |
| Sam's Crispy Chicken | HIT | Sam’s Crispy Chicken (100, southern_restaurant) |
| Super Mega Dilla | MISS | — |
| Tender Shack | MISS | — |
| TenderFix | HIT | Tenderfix By Noah Schnapp (100, fast_food_restaurant) |
| The Burger Den | HIT | The Burger Den (100, restaurant) |
| The Burger Experience | MISS | — |
| The Meltdown | HIT | The Meltdown (100, food_delivery_service) |
| The Wing Dept | MISS | — |
| The Wing Experience | MISS | — |
| Thighstop | MISS | — |
| Thrilled Cheese | MISS | — |
| TikTok Kitchen | MISS | — |
| Tyga Bites | HIT | Tyga Bites (100, food_delivery_service) |
| Umami Burger | HIT | Umami Burger (100, burger_restaurant) |
| Wing Boss | HIT | Wing Boss (100, restaurant) |
| Wings of New York | HIT | Wings of New York (100, restaurant) |
| Wow Bao | HIT | Wow Bao (100, chinese_restaurant) |

## Caveats on the raw number

1. **Two hits look like coincidental collisions** and should be adjudicated
   during review: "Plant B" matched "Plan B (sports_bar)" (92.3, typo-distance
   fuzzy hit) and "Nice Day" matched a discount_store. Strict count: 22/51 =
   43.1%. Either way the band is the same: MARGINAL.
2. **The seed list skews toward dead brands.** Several misses (MrBeast Burger's
   wind-down era peers, TikTok Kitchen, Thighstop, Neighborhood Wings) had
   already shut down by the measurement date. Overture reflects the present, so
   the gate as measured *understates* coverage of currently operating brands —
   the population the discovery pipeline will actually hunt.
3. Hits are overwhelmingly exact-name, food-categorized records, including
   delivery-native entries ("food_delivery_service" category) — the matcher is
   not inflating the number with fuzz.

## Prescribed next step (brief §8, 30–50% band)

Pull Foursquare OS Places as a supplement and re-measure before Phase 2.
FSQ distribution became **gated** (verified 2026-08-05): requires a free
Hugging Face account + accepted terms + HF_TOKEN. `sources/fsq.py` is ready;
`TODO(frank)`: accept terms, set HF_TOKEN, run `cli.py fetch-fsq`, re-run
`cli.py coverage` (it includes the FSQ snapshot automatically).

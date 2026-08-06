import type { Brand, Operator } from "../types";

/**
 * Database of publicly documented virtual brands and ghost kitchen operators.
 * Compiled from public reporting and adversarially fact-checked; status
 * reflects the last confirmed public information (mid-2026).
 */
export const BRANDS: Brand[] = [
  {
    "name": "MrBeast Burger",
    "aliases": [
      "Beast Burger"
    ],
    "parentCompany": "Virtual Dining Concepts (with Jimmy 'MrBeast' Donaldson)",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Partner restaurants (Bertucci's, Buca di Beppo, and ~1,700+ other host kitchens at peak)",
    "notes": "Launched Dec 2020; grew to roughly 2,000 locations. In 2023 MrBeast sued VDC over food quality and to shut the brand down; VDC countersued for $100M. Brand has drastically wound down with many locations marked closed on delivery apps, but litigation left its formal status murky."
  },
  {
    "name": "Guy Fieri's Flavortown Kitchen",
    "aliases": [
      "Flavortown Kitchen"
    ],
    "parentCompany": "Guy Fieri with Robert Earl (Earl Enterprises) / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Earl Enterprises restaurant kitchens (Bertucci's, Buca di Beppo, Brio/Bravo) and partner kitchens",
    "notes": "Launched late 2020 across ~170+ host kitchens. Still appears in some delivery markets; current footprint unverified."
  },
  {
    "name": "Mariah's Cookies",
    "aliases": [
      "Mariah Carey's Cookies"
    ],
    "parentCompany": "Mariah Carey / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Partner restaurant kitchens (delivery-only)",
    "notes": "Launched Dec 2020 in ~30 markets, expanded widely. One of VDC's flagship celebrity brands."
  },
  {
    "name": "Buddy V's Cake Slice",
    "aliases": [
      "Buddy V's"
    ],
    "parentCompany": "Buddy Valastro (Cake Boss) / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "active",
    "cookedBy": "Distributed via partner restaurant kitchens; slices shipped to host locations",
    "notes": "Delivery-only cake slice brand launched 2020; among VDC's longer-running brands and expanded into retail distribution."
  },
  {
    "name": "Pauly D's Italian Subs",
    "parentCompany": "DJ Pauly D (Paul DelVecchio) / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Partner restaurant kitchens",
    "notes": "VDC celebrity sub-sandwich brand launched 2021 with the Jersey Shore star."
  },
  {
    "name": "Pardon My Cheesesteak",
    "parentCompany": "Barstool Sports / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "active",
    "cookedBy": "Partner restaurant kitchens nationwide",
    "notes": "Launched Dec 2020 tied to Barstool's Pardon My Take podcast; still widely listed on delivery apps."
  },
  {
    "name": "NASCAR Refuel",
    "parentCompany": "NASCAR (licensed) / Virtual Dining Concepts",
    "operator": "Virtual Dining Concepts",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Partner restaurant kitchens",
    "notes": "Licensed-IP virtual brand launched 2021 in hundreds of locations; current status unverified."
  },
  {
    "name": "Tyga Bites",
    "parentCompany": "Tyga (Micheal Stevenson) with Robert Earl",
    "operator": "Virtual Dining Concepts",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Partner restaurant kitchens; launched as a Grubhub exclusive",
    "notes": "Chicken-bites brand launched July 2020; quietly faded from most markets."
  },
  {
    "name": "Packed Bowls by Wiz Khalifa",
    "parentCompany": "Wiz Khalifa / Nextbite",
    "operator": "Nextbite",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens with excess capacity",
    "notes": "Munchies-themed bowls brand launched 2022. Part of the Nextbite portfolio acquired by Sam Nazarian's SBE in 2023; post-acquisition status unclear."
  },
  {
    "name": "HotBox by Wiz",
    "parentCompany": "Wiz Khalifa / Nextbite",
    "operator": "Nextbite",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens",
    "notes": "Earlier Wiz Khalifa virtual brand launched 2020 via Nextbite."
  },
  {
    "name": "George Lopez Tacos",
    "parentCompany": "George Lopez / Nextbite",
    "operator": "Nextbite",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens",
    "notes": "Celebrity taco brand launched 2021; part of Nextbite portfolio acquired by SBE in 2023."
  },
  {
    "name": "Another Wing by DJ Khaled",
    "aliases": [
      "Another Wing"
    ],
    "parentCompany": "DJ Khaled / Reef Technology",
    "operator": "Reef Technology",
    "type": "celebrity",
    "status": "unknown",
    "cookedBy": "Reef vessel/neighborhood kitchens",
    "notes": "Launched Nov 2021 simultaneously in 150+ locations across multiple countries; Reef has since closed much of its kitchen network."
  },
  {
    "name": "It's Just Wings",
    "parentCompany": "Brinker International (Chili's, Maggiano's)",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Chili's and Maggiano's kitchens (1,000+ locations)",
    "notes": "Launched June 2020; exceeded $170M first-year sales. One of the most successful chain virtual brands; still operating."
  },
  {
    "name": "Maggiano's Italian Classics",
    "parentCompany": "Brinker International",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Chili's kitchens",
    "notes": "Brinker's second virtual brand (2021), selling Maggiano's-branded Italian food out of Chili's kitchens."
  },
  {
    "name": "Pasqually's Pizza & Wings",
    "aliases": [
      "Pasqually's"
    ],
    "parentCompany": "CEC Entertainment (Chuck E. Cheese)",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Chuck E. Cheese kitchens",
    "notes": "Launched 2020; drew attention when customers discovered orders came from Chuck E. Cheese. Named for the band's chef character; still listed on delivery apps."
  },
  {
    "name": "Cosmic Wings",
    "parentCompany": "Dine Brands Global (Applebee's)",
    "type": "chain-spinoff",
    "status": "defunct",
    "cookedBy": "Applebee's kitchens (~1,300 locations), Uber Eats exclusive",
    "notes": "Launched Feb 2021 with Cheetos-flavored wings; Dine Brands discontinued it in mid-2022."
  },
  {
    "name": "Thighstop",
    "parentCompany": "Wingstop",
    "type": "chain-spinoff",
    "status": "defunct",
    "cookedBy": "Wingstop kitchens",
    "notes": "Launched June 2021 as a hedge against wing prices; chicken thighs were folded into Wingstop's core menu and the standalone brand was retired."
  },
  {
    "name": "Tender Shack",
    "parentCompany": "Bloomin' Brands (Outback Steakhouse, Carrabba's)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Outback Steakhouse and Carrabba's kitchens (~725 locations), initially DoorDash-only",
    "notes": "Chicken tender brand taken national in early 2021; sales softened as dining rooms reopened."
  },
  {
    "name": "The Burger Den",
    "parentCompany": "Denny's",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Denny's kitchens",
    "notes": "Delivery-only burger brand launched 2021 across most of the Denny's system; still widely listed."
  },
  {
    "name": "The Meltdown",
    "parentCompany": "Denny's",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Denny's kitchens",
    "notes": "Denny's melts/sandwich virtual brand launched 2021; still widely listed on delivery apps."
  },
  {
    "name": "Banda Burrito",
    "parentCompany": "Denny's",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Denny's kitchens",
    "notes": "Denny's third virtual brand (Mexican-inspired), launched 2023 in select markets."
  },
  {
    "name": "Chicken Sammy's",
    "aliases": [
      "The Chicken Sammy's"
    ],
    "parentCompany": "Red Robin",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Red Robin kitchens",
    "notes": "One of three Red Robin virtual brands launched 2021; Red Robin later de-emphasized virtual brands."
  },
  {
    "name": "The Wing Dept",
    "aliases": [
      "Wing Dept"
    ],
    "parentCompany": "Red Robin",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Red Robin kitchens",
    "notes": "Red Robin delivery-only wing brand launched 2021."
  },
  {
    "name": "Fresh Set",
    "parentCompany": "Red Robin",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Red Robin kitchens",
    "notes": "Red Robin salad/bowl virtual brand launched 2021."
  },
  {
    "name": "Hootie's Burger Bar",
    "parentCompany": "Hooters (HOA Brands)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Hooters kitchens",
    "notes": "Burger virtual brand launched 2020 from Hooters kitchens."
  },
  {
    "name": "Hootie's Bait & Tackle",
    "parentCompany": "Hooters (HOA Brands)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Hooters kitchens",
    "notes": "Seafood virtual brand launched 2021 from Hooters kitchens."
  },
  {
    "name": "The Wing Experience",
    "parentCompany": "Smokey Bones (then Sun Capital; later FAT Brands)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Smokey Bones kitchens",
    "notes": "Early chain virtual brand (2019), a pioneer of the model."
  },
  {
    "name": "The Burger Experience",
    "parentCompany": "Smokey Bones (then Sun Capital; later FAT Brands)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Smokey Bones kitchens",
    "notes": "Companion 2019 virtual brand to The Wing Experience."
  },
  {
    "name": "Wild Burger",
    "parentCompany": "Buffalo Wild Wings (Inspire Brands)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Buffalo Wild Wings kitchens",
    "notes": "Delivery-only burger brand launched 2020 out of BWW kitchens."
  },
  {
    "name": "Twisted Tenders",
    "parentCompany": "SPB Hospitality (Logan's Roadhouse)",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Logan's Roadhouse and sister-brand kitchens",
    "notes": "Chicken tender virtual brand launched late 2020."
  },
  {
    "name": "The Pancake Kitchen by Cracker Barrel",
    "aliases": [
      "The Pancake Kitchen"
    ],
    "parentCompany": "Cracker Barrel",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Cracker Barrel kitchens",
    "notes": "Delivery-only breakfast brand launched 2020 in select markets."
  },
  {
    "name": "Chicken n' Biscuits by Cracker Barrel",
    "aliases": [
      "Chicken n' Biscuits"
    ],
    "parentCompany": "Cracker Barrel",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Cracker Barrel kitchens",
    "notes": "Second Cracker Barrel virtual brand, launched 2020-2021."
  },
  {
    "name": "Thrilled Cheese",
    "parentCompany": "Dine Brands (IHOP) with Nextbite",
    "operator": "Nextbite",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "IHOP kitchens",
    "notes": "Grilled cheese virtual brand launched 2021 via IHOP-Nextbite partnership; caught up in Nextbite's 2023 sale to SBE."
  },
  {
    "name": "Super Mega Dilla",
    "parentCompany": "Dine Brands (IHOP) with Nextbite",
    "operator": "Nextbite",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "IHOP kitchens",
    "notes": "Quesadilla virtual brand launched 2021 via IHOP-Nextbite partnership."
  },
  {
    "name": "Wings of New York",
    "parentCompany": "Nathan's Famous",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Host kitchens via Franklin Junction and other partners",
    "notes": "Nathan's Famous virtual wing brand distributed through host-kitchen partnerships."
  },
  {
    "name": "Arthur Treacher's",
    "aliases": [
      "Arthur Treacher's Fish & Chips"
    ],
    "parentCompany": "Nathan's Famous",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Host kitchens via licensing partnerships",
    "notes": "Legacy fish-and-chips brand revived largely as a virtual/licensed concept by Nathan's Famous."
  },
  {
    "name": "Nathan's Famous (virtual)",
    "parentCompany": "Nathan's Famous",
    "operator": "Franklin Junction",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Host kitchens including Ruby Tuesday locations via Franklin Junction",
    "notes": "Nathan's expanded delivery via hundreds of host kitchens; flagship example of Franklin Junction's host-kitchen model."
  },
  {
    "name": "Fuku",
    "parentCompany": "Fuku (David Chang / Momofuku-affiliated)",
    "operator": "Reef Technology, later Kitchen United / Franklin Junction",
    "type": "chain-spinoff",
    "status": "unknown",
    "cookedBy": "Licensed host restaurant kitchens plus its own stores",
    "notes": "David Chang's spicy fried-chicken brand expanded delivery-only via REEF Technology in 2020, then switched to Kitchen United in late 2021 amid REEF food-safety reports, alongside Franklin Junction and Family Style Kitchen partnerships."
  },
  {
    "name": "Nestlé Toll House Cookie Delivery",
    "parentCompany": "Nestlé (licensed) / Nextbite",
    "operator": "Nextbite",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens baking from Nestlé product",
    "notes": "Licensed CPG virtual brand in the Nextbite portfolio."
  },
  {
    "name": "Monster Mac",
    "parentCompany": "Nextbite",
    "operator": "Nextbite",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens",
    "notes": "Mac-and-cheese original brand from Nextbite's in-house portfolio."
  },
  {
    "name": "Wing Boss",
    "parentCompany": "Nextbite",
    "operator": "Nextbite",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens",
    "notes": "Nextbite original wing brand fulfilled by partner restaurants."
  },
  {
    "name": "Firebelly Wings",
    "parentCompany": "Nextbite",
    "operator": "Nextbite",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Host restaurant kitchens",
    "notes": "Nextbite original wing brand."
  },
  {
    "name": "Krispy Rice",
    "parentCompany": "C3 (Creating Culinary Communities / SBE)",
    "operator": "C3",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "C3 ghost kitchens, hotel kitchens, and Kitchen United-style facilities",
    "notes": "Sushi brand; one of C3's flagship delivery-first concepts, also opened physical outlets. C3 has downsized substantially since 2023."
  },
  {
    "name": "Sam's Crispy Chicken",
    "parentCompany": "C3 (Creating Culinary Communities / SBE)",
    "operator": "C3",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "C3 ghost kitchens and partner kitchens",
    "notes": "Fried chicken concept in C3's delivery-first portfolio."
  },
  {
    "name": "Umami Burger (delivery-first)",
    "aliases": [
      "Umami Burger"
    ],
    "parentCompany": "C3 / SBE (Sam Nazarian)",
    "operator": "C3",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "C3 ghost kitchens plus remaining physical locations",
    "notes": "Formerly a sit-down chain, repositioned by C3 as a largely delivery-first brand operated from shared kitchens."
  },
  {
    "name": "Cicci di Carne",
    "parentCompany": "C3 (Creating Culinary Communities / SBE)",
    "operator": "C3",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "C3 ghost kitchens",
    "notes": "Italian-sandwich concept in C3's virtual portfolio."
  },
  {
    "name": "EllaMia",
    "parentCompany": "C3 (Creating Culinary Communities / SBE)",
    "operator": "C3",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "C3 kitchens (often hotel-based)",
    "notes": "Coffee/cafe concept in C3's portfolio."
  },
  {
    "name": "Wing Squad",
    "parentCompany": "Reef Technology",
    "operator": "Reef Technology",
    "type": "virtual-operator",
    "status": "unknown",
    "cookedBy": "Reef neighborhood/vessel kitchens",
    "notes": "Reef in-house wing brand; Reef has since closed much of its kitchen network and pivoted to licensing."
  },
  {
    "name": "Man vs Fries",
    "parentCompany": "Virtual Dining Concepts (acquired March 2024; founded by William Bonhorst)",
    "operator": "Virtual Dining Concepts",
    "type": "independent",
    "status": "active",
    "cookedBy": "Own ghost kitchens and franchised/licensed host kitchens",
    "notes": "Bay Area delivery-first loaded-fries/burrito brand born as a DoorDash-only pop-up; scaled nationally through ghost kitchens and was acquired by Virtual Dining Concepts in March 2024."
  },
  {
    "name": "Wow Bao (dark kitchen program)",
    "aliases": [
      "Wow Bao Hot Asian Buns"
    ],
    "parentCompany": "Wow Bao (Lettuce Entertain You spinoff)",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "600+ third-party restaurant host kitchens reheating supplied product",
    "notes": "Notable reverse model: Wow Bao licenses its brand and supplies frozen product so other restaurants sell Wow Bao on delivery apps."
  },
  {
    "name": "Bad Mutha Clucka",
    "parentCompany": "Dog Haus (The Absolute Brands)",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Dog Haus kitchens",
    "notes": "Fried-chicken virtual brand from Dog Haus's The Absolute Brands virtual portfolio, launched 2020."
  },
  {
    "name": "Bad-Ass Breakfast Burritos",
    "parentCompany": "Dog Haus (The Absolute Brands)",
    "type": "chain-spinoff",
    "status": "active",
    "cookedBy": "Dog Haus kitchens",
    "notes": "Breakfast burrito virtual brand from Dog Haus's The Absolute Brands portfolio."
  }
];

export const OPERATORS: Operator[] = [
  {
    "name": "Virtual Dining Concepts",
    "description": "Orlando-based virtual-brand company founded by Robert Earl (Planet Hollywood) and Robert Earl Jr.; licenses celebrity-branded delivery-only concepts to host restaurant kitchens nationwide. Best known for MrBeast Burger and the ensuing 2023 dueling $100M lawsuits with MrBeast.",
    "knownBrands": [
      "MrBeast Burger",
      "Guy Fieri's Flavortown Kitchen",
      "Mariah's Cookies",
      "Buddy V's Cake Slice",
      "Pauly D's Italian Subs",
      "Pardon My Cheesesteak",
      "NASCAR Refuel",
      "Tyga Bites"
    ]
  },
  {
    "name": "Nextbite",
    "description": "Denver-based virtual-brand platform spun out of Ordermark (founder Alex Canter); paired original and licensed brands with restaurants that had excess kitchen capacity. After repeated layoffs it sold Ordermark to UrbanPiper and was acquired in mid-2023 by Sam Nazarian's SBE, continuing as 'Nextbite by sbe' alongside C3.",
    "knownBrands": [
      "Packed Bowls by Wiz Khalifa",
      "HotBox by Wiz",
      "George Lopez Tacos",
      "Thrilled Cheese",
      "Super Mega Dilla",
      "Monster Mac",
      "Wing Boss",
      "Firebelly Wings",
      "Nestlé Toll House Cookie Delivery",
      "Fuku (licensed)"
    ]
  },
  {
    "name": "C3 (Creating Culinary Communities)",
    "description": "Sam Nazarian's food-tech/virtual-brand company (SBE-affiliated) operating delivery-first brands out of ghost kitchens, hotels, and food halls. Acquired Nextbite in 2023 and some Kitchen United assets; has downsized significantly since.",
    "knownBrands": [
      "Krispy Rice",
      "Umami Burger",
      "Sam's Crispy Chicken",
      "Cicci di Carne",
      "EllaMia"
    ]
  },
  {
    "name": "Reef Technology",
    "description": "Miami-based, SoftBank-backed operator of 'neighborhood kitchens' — modular kitchen trailers in parking lots running many brands at once (including a large Wendy's ghost-kitchen deal that Wendy's terminated in 2023). Faced health-code and quality problems, closed most kitchen markets, and pivoted to licensing its tech.",
    "knownBrands": [
      "Another Wing by DJ Khaled",
      "Wing Squad",
      "Wendy's (former partnership)",
      "BurgerFi and 800 Degrees (former partnerships)"
    ]
  },
  {
    "name": "CloudKitchens",
    "description": "Travis Kalanick's City Storage Systems venture renting commissary ghost-kitchen space to restaurants and virtual brands, with the Otter order-aggregation software and an internal 'Future Foods' virtual-brands arm. Operates quietly at large scale in the US and internationally."
  },
  {
    "name": "Kitchen United",
    "description": "Kitchen-center operator (Kitchen United MIX) that hosted multiple restaurant brands per site, including inside Kroger stores; raised money from Kroger and Burger King's parent. Wound down its physical kitchen centers in 2023-2024, selling assets, with some acquired by Sam Nazarian."
  },
  {
    "name": "Ghost Kitchen Brands",
    "description": "Canadian-founded operator (George Kottas) best known for small-footprint multi-brand kitchens inside Walmart stores in the US and Canada, selling licensed national brands from one counter; US operations continue as Ghost Kitchens America, which partnered with Richtech Robotics in 2024 to run Walmart locations.",
    "knownBrands": [
      "Licensed counters for brands like Nathan's Famous, Cinnabon, Quiznos, Saladworks (in-store kitchens)"
    ]
  },
  {
    "name": "Franklin Junction",
    "description": "Atlanta-based 'host kitchen' marketplace founded by Rishi Nigam and Aziz Hashim that matches established food brands with restaurants that have excess kitchen capacity — e.g., Nathan's Famous cooked in Ruby Tuesday kitchens.",
    "knownBrands": [
      "Nathan's Famous (host-kitchen expansion)",
      "Wings of New York",
      "Arthur Treacher's"
    ]
  },
  {
    "name": "Kitopi",
    "description": "Dubai-headquartered managed cloud-kitchen platform (SoftBank-backed unicorn) that cooks and fulfills delivery orders on behalf of restaurant brands, primarily across the Middle East; one of the largest ghost-kitchen operators globally."
  },
  {
    "name": "The Local Culinary",
    "description": "Miami-based virtual-restaurant group that licenses a portfolio of dozens of ready-made delivery-only brand concepts to restaurant kitchens."
  },
  {
    "name": "Deliveroo Editions",
    "description": "Deliveroo's own ghost-kitchen program providing delivery-only kitchen sites where partner restaurants cook exclusively for the app, mainly in the UK, Europe, and Asia-Pacific."
  },
  {
    "name": "All Day Kitchens",
    "description": "San Francisco-based network of small distributed satellite kitchens that fulfill delivery orders for partner restaurant brands across a metro area."
  },
  {
    "name": "Zuul",
    "description": "New York City ghost-kitchen operator and software provider; acquired by Kitchen United in 2022 and subsequently wound down as Kitchen United retrenched."
  },
  {
    "name": "Butler Hospitality",
    "description": "NYC startup that ran hotel-kitchen ghost kitchens powering room service and delivery for multiple hotels; shut down abruptly in mid-2022."
  }
];

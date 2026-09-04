# DEDUP LEDGER — liquorlicense

Governing claim-ownership contract for the build.
Authored 2026-07-22 for the v3 section additions; **PART 1 re-authored 2026-07-29 with PAGE owners**
when the site went from 1 page to 9.

**PRINCIPLE (unchanged):** every topic has exactly ONE canonical owner that EXPLAINS it. Every other
appearance is a POINTER (a link, a label, a teaser dek) — never a re-explanation.
A builder that restates a claim owned by another surface has FAILED, even if the wording differs.

**What changed on 2026-07-29:** the old PART 1 mapped claims to `#section` owners on a single page.
With 9 pages the owner is now a PAGE, and the homepage keeps a SUMMARY of everything while owning
only what no page owns. The old table is preserved verbatim below as PART 1-LEGACY — it is still the
authoritative record of what each homepage section said before the split.

---

## PART 0 — THE TWO DECLARED CARVE-OUTS

Declared openly rather than applied silently, so that a reviewer can argue with them.

1. **CONVERSION SURFACES ARE EXEMPT.** A CTA, a phone number, an enquiry form and a postal address
   are not claims — they are the conversion path, and burying them to satisfy a dedup rule would be
   a worse site. `contact.html` and `index.html#contact` may both carry a form. The footer carries
   the NAP on all 9 pages.
2. **NUMERIC CARVE-OUT.** A bare NUMBER may appear on two surfaces where its INTERPRETATION is owned
   once. The homepage hero stat rail owns `20+ / 1,000+ / 58 / 12+` as numerals with bare labels;
   `about.html` owns what each one MEANS. No sentence is repeated.

---

## PART 1 — CLAIM → OWNING PAGE (the governing table, 2026-07-29)

"OWNS" = explains it in full, and binds the `R-*` marker. Everyone else may only point.

| # | Claim | OWNING PAGE | Every other surface may only… |
|---|---|---|---|
| C1 | Off-market supply — most CA licences never reach the open market | `index.html` hero | name it in a link label. **`inventory.html` must NOT restate it** — it points to `services.html#buy` |
| C2 | Named clients: Raley's, Silverlake Ramen, AMF, Firenza (R-LOGO-01..04) | `index.html#logo-wall` — HOMEPAGE-ONLY | no page may re-list them |
| C3 | Who the firm is; two disciplines under one desk | `about.html` | `index.html#about` keeps ONE summary paragraph + a read-more |
| C4 | The regulator is the CA Dept of Alcoholic Beverage Control (R-FACT-01) | `about.html` | the footer legal note stays on all 9; no page re-explains |
| C5 | What the four proof metrics MEAN (R-STAT-01..04) | `about.html` | hero rail = numerals + labels only (PART 0.2) |
| C6–C13 | The eight services, each in full (R-SERV-01..07 + card 08) | `services.html#buy/#sell/#transfer/#valuation/#cup/#compliance/#escrow/#new-business` | homepage card = ≤18-word teaser + its distinct CTA label |
| C12 | Escrow as our **ROLE** — neutral coordinator, funds, notices (R-SERV-07) | `services.html#escrow` | must NOT use "protect creditors" / "Business and Professions Code" / "California law requires specific escrow procedures" — those belong to C15 |
| C14 | Local approval: city/county sign-off, zoning, sometimes a CUP (R-FACT-03) | `process.html` phase 03 | `faq.html` Q4 answers *whether* it is required; `services.html#cup` says what we do there |
| C15 | Statutory escrow **LAW** — creditor protection, B&P Code notices (R-FACT-04) | `process.html` phase 05 | `index.html#process` trust-note becomes a POINTER — **this fixes the pre-existing duplicate** |
| C16 | Transfer timeline 60–120 days + what moves it (R-FACT-02) | `process.html` phase 06 | `faq.html` Q5 gives the number as a short answer; the DRIVERS stay on process |
| C17 | Who signs off, and when (ABC / city / county / law enforcement / state investigators) | `process.html` | new artifact, assembled only from C14 + C16 + R-SERV-03 + R-FACT-01 |
| C18–C20 | Type 21 / 47 / 48 definitions + each one's condition (R-CERT-01..03) | `licence-types.html` | homepage `#licensing` keeps ABC's authorisation sentence only; **the condition bullets MOVE to the page** |
| C18–C20 **EXCEPTION** (owner, 2026-09-04) | The same Type 20&21 / 41&47 / 48 descriptions, as the client publishes them on their own `/buy` and `/sell` | ALSO `service-buy.html#buy-classifications` and `service-sell.html#sell-classifications` | The owner asked for the reference pages' descriptions after the C18–C20 conflict was raised twice, and decided to duplicate. `licence-types.html` REMAINS the canonical owner: both bands still carry the pointer note to it, and any correction is made there first. No OTHER page gains this licence. |
| C21 | Which SECTOR needs which type (the 8 industries) | `index.html#industries` — HOMEPAGE-ONLY | `licence-types.html` must **NOT** build a sector→type table |
| C22 | The location itself can disqualify you | `resources.html#zoning` | homepage panel 04 = one claim sentence + read-more |
| C23 | Pricing MECHANISM: population caps → scarcity → county price swings | `resources.html#pricing` | **`inventory.html` must NOT restate it**; homepage panel 02 trimmed |
| C24 | Route to market: caps mean most must BUY, creating the resale market | `resources.html#route` | homepage panel 03 trimmed |
| C25 | Classification DECISION framing — picking wrong costs delay, money, freedom | `resources.html#classification` | **`licence-types.html` must NOT restate it** — it points here |
| C26–C31 | The six original FAQ answers (R-FAQ-01..06) | `faq.html` | homepage keeps **four** (Q1/Q3/Q4/Q5) as short answers |
| C28 | **The COST NUMBER** $30k–$500k+ and the additional fees (R-FAQ-03) | `faq.html` | **`inventory.html` and `resources.html#pricing` must NOT quote it** |
| C32 | "We act for sellers too" (R-FAQ-07) | `faq.html` | answer is PROCESS-shaped; must NOT restate `services.html#sell`'s capability list |
| C33 | Statewide / 58 counties + the market list, market by market (R-STAT-03) | `locations.html` — **OWNERSHIP MOVED OFF THE HOMEPAGE 2026-07-29** when the page was added | `index.html#coverage` demotes to a SUMMARY: it keeps its map, its 12 chips and one line, then routes through — it must NOT explain the coverage or break it down by market; `faq.html` Q8 (R-FAQ-08) answers yes and POINTS; no other page re-lists the markets |
| C34 | The live listings — type, county, city, price, status (R-OFFER-01..09) | `inventory.html` | homepage `#inventory` shows **six** of the nine |
| C35 | Office address + broker line (R-LOC-01/02) | `contact.html` | footer NAP on all 9 (PART 0.1); homepage `#contact` map card |
| C36 | Client voice / testimonials | `index.html#testimonials` — HOMEPAGE-ONLY, sample-marked | **no page may reuse `.testimonial-card` or `.pr-tcard`** |
| C37 | The five "start here" guide pointers | `index.html#guides` — HOMEPAGE-ONLY | `resources.html` may carry a numbered **directory** (title + destination, ≤10 words, no dek, no imagery). A directory is not a teaser |

### The carried-forward duplicate — FIXED in this build, not just flagged again
PART 1-LEGACY row `#process` trust-note reads: *"Repeats step 05's escrow-law sentence.
**PRE-EXISTING DUPLICATE — flagged, not touched.**"* Verified still present: `index.html:633`
(step 05) and `:638` (trust-note) both carry the same escrow-law sentence.
The page split makes the fix free, so it is taken:
- `process.html` phase 05 becomes the sole owner of C15 and binds `R-FACT-04`.
- `index.html:633` shortens and **drops** its `R-SERV-07` marker.
- `index.html:638` becomes a pointer and **drops** its `R-FACT-04` marker.
- `index.md` `required_ids` drops `R-FACT-04` accordingly.

---

## PART 1-LEGACY — CLAIM INVENTORY OF THE SINGLE PAGE (verified read of index.html, 2026-07-22)

Superseded as the governing table by PART 1 above, but preserved verbatim: it remains the
authoritative record of what each homepage section said before the 9-page split.

| Owner | Claims it owns exclusively |
|---|---|
| `hero` | Off-market licences don't reach open market; we source → vet clean → statutory escrow → ABC approval. Stats 20+ yrs / 1,000+ brokered / 58 counties / 12+ sectors. |
| `logo-wall` | Named clients: Raley's, Silverlake Ramen, AMF, Firenza Pizza. |
| `#services` 01 Buy | Off-market Type 47/48/21 sourcing; vetting for liens, disciplinary history, transferability; LOI → final ABC issuance. |
| `#services` 02 Sell | Pre-qualified institutional + independent buyers; secured escrow; highest achievable market price. |
| `#services` 03 Transfer | Person-to-person AND premises-to-premises phases; coordination with local law enforcement + state investigators; minimise downtime. |
| `#services` 04 Valuation | Real-time appraisals from current closed transactions; for legal filings, partnership buyouts, financial planning; prices move monthly with county demand. |
| `#services` 05 CUP | Securing CUPs + police permits; representing the business at planning-commission hearings and neighbourhood council meetings. |
| `#services` 06 ABC compliance | Operational audits; LEAD-programme staff training; premises compliance. |
| `#industries` | The SIX business types as labels only (Restaurants, Bars & nightclubs, Hotels, Liquor stores, Grocery, Convenience). NO descriptive copy exists yet. |
| `#licensing` | **The definitions of Type 21 / 47 / 48** (ABC's own wording) + each one's siting/conditions rule. THIS SECTION OWNS "what the licence types are". |
| `#inventory` | The live listings: type, county, price, status. |
| `#process` 01–06 | The six transaction phases IN ORDER. Step 03 owns "local approval / zoning / CUP happens at the eligibility stage". Step 05 owns statutory escrow law. Step 06 owns the 60–120 day timeline. |
| `#process` trust-note | Repeats step 05's escrow-law sentence. **PRE-EXISTING DUPLICATE — flagged, not touched.** |
| `#coverage` | The 12 market chips; LA→Central Valley reach; local experts per county. |
| `#faq` Q1 | How to buy (buy existing, negotiate, escrow, transfer application). |
| `#faq` Q2 | Difference between types (short-form; long-form is `#licensing`'s). |
| `#faq` Q3 | **The COST NUMBER** ($30k–$500k+, plus escrow/transfer/legal/permit fees). |
| `#faq` Q4 | Do I need city approval (yes; zoning; sometimes CUP). |
| `#faq` Q5 | Timeline 60–120 days + what moves it. |
| `#faq` Q6 | Premises-to-premises relocation. |
| `#contact` | Consultation, phone, office map, request form. |

---

## PART 2 — PER-UNIT SCOPE + FORBIDDEN CLAIMS (the v3 section-addition units, 2026-07-22)

> **Status 2026-07-29:** these unit scopes governed the V3 build that produced the current homepage
> and are preserved in full. Where a unit's claim now has a PAGE owner in PART 1, PART 1 wins and the
> homepage unit degrades to the summary/teaser described there. Two notes carried forward:
> U6's pointer CTAs (`#licensing`, `#inventory`, `#services`, `#process`, `#faq`) turned out to be an
> accurate de-facto IA proposal and became real page boundaries; and U5's honesty gate is permanent —
> the sample-marked testimonial treatment survives the split unchanged.


### U1 — About band `#about` ("Your Top California License Solution")
- **OWNS (new):** who the firm is; the working relationship with the CA Dept of Alcoholic
  Beverage Control as the licensing + compliance board regulating alcohol sales; the blunt
  qualifying fact that ANY business selling alcohol in any form needs a California licence.
- **MUST NOT restate:** the hero lede's source→vet→escrow→approval sequence; any service
  description (that is `#services`); any licence-type definition (that is `#licensing`).
- **3 link cards:** About Us / Our Services / Contact Us. The reference gives all three the
  IDENTICAL placeholder sentence — **reference bug**. Write three DISTINCT one-liners.

### U2 — Services: +2 cards (07, 08) + CTA link on all 8
- **07 Escrow / transaction guidance OWNS:** the brokerage's ROLE as neutral coordinator —
  holding and disbursing transaction funds, filing the statutory notices.
- **MUST NOT restate:** `#process` step 05's sentence, nor the trust-note. Specifically the
  strings "protect creditors", "Business and Professions Code", "California law requires
  specific escrow procedures" are OWNED by `#process` — do not reuse them.
- **08 New business licence planning OWNS:** greenfield planning — choosing the licence type
  before a site is signed, sequencing licence + CUP + build-out for a business that does not
  yet exist. Genuinely absent from the page today.
- **REFERENCE BUG:** the reference's "New Business License Planning" card contains the escrow
  card's body copy VERBATIM. Do not copy it. Write original copy.
- CTA labels (from reference, one per card, all distinct): Find inventory · Get valuation ·
  Check eligibility · Request report · Zoning analysis · Audit services · Escrow inquiry ·
  Talk to a broker.

### U3 — Industries: +2 tiles + 8 descriptions
- **OWNS (new):** the per-BUSINESS-TYPE licensing nuance (which type each sector needs and the
  one condition that bites it).
- **MUST NOT restate:** `#licensing`'s definitions of Type 21/47/48. Industries may NAME a type
  ("requires Type 41 or 47") but must NOT define what that type authorises.
- +2 tiles: Franchise operators, Event venues. Assets already present and unused:
  `assets/ind-franchise.jpg`, `assets/ind-event-venues.jpg`.

### U4 — Inventory: spec-table restructure + 9th card
- Adopt the reference's 4-row spec table (Licence type / Location / Price & terms / Status &
  timeline) + a per-card "Acquire licence" CTA.
- **DEDUP RULE:** the city currently lives inside the card TITLE ("Type 47 — La Mesa"). Once a
  Location row exists the city would appear twice. Retitle each card to the reference's shape
  ("Alcoholic Beverage Control (ABC) Licence" + county) so every datum appears EXACTLY ONCE.
- 9th card: Type 47, Glendale, Los Angeles County, $80,000, Pending transfer.

### U5 — Testimonials `#testimonials`
- **OWNS (new):** client voice.
- **HONESTY GATE:** the reference's four cards are placeholder lorem — identical copy, all
  attributed to "John Doe, Director of Development, Lorem Hospitality". **Reference bug.**
  Ship copy that plainly reads as illustrative sample content. NEVER attribute an invented
  quote to a named real person or company. No fabricated star ratings.
- **MUST NOT restate:** any service capability (that is `#services`).

### U6 — Knowledge base `#resources` ("Liquor Licensing Resources") — 4 blocks
This is the highest duplication risk on the page. Scope each block to the ONE thing our page
does not already say, and make its CTA a pointer to the canonical owner.
| Block | OWNS (new) | MUST NOT restate | CTA → |
|---|---|---|---|
| Understanding CA licence types | The DECISION framing: a wide range exists; picking wrong costs delays, extra cost, operating restrictions. | Any Type 21/47/48 definition — owned by `#licensing`. | `#licensing` |
| What affects pricing | The MECHANISM: population-based state caps on licence counts → scarcity → county-by-county price swings. | The cost NUMBER ($30k–$500k) — owned by `#faq` Q3. Appraisal service — owned by `#services` 04. | `#inventory` |
| Buying existing vs applying new | Population caps mean most businesses must BUY rather than apply; this creates the competitive resale market. | `#faq` Q1's buy-negotiate-escrow-apply sequence. | `#services` |
| Why zoning + CUP matter | That the LOCATION ITSELF can disqualify you even when a licence is available. | `#services` 05 (what we do at hearings), `#process` 03 (when it happens), `#faq` Q4 (whether it is required). | `#services` |

### U7 — Articles `#guides` — 5 teaser cards
- These are POINTERS, not content. One short dek each, as in the reference. A dek must not
  restate the substance of the section it points to, nor any U6 block.
- Anchors (distinct, one each): 01 Licence types → `#licensing` · 02 How to transfer →
  `#process` · 03 What is a CUP → `#services` · 04 What it costs → `#inventory` ·
  05 Buying a restaurant licence → `#faq`.

### U8 — Small edits bundle
- **FAQ +2.** Q7 "Can you help me sell my licence?" — answer PROCESS-shaped; must NOT restate
  `#services` 02's capability list. Q8 "Do you work statewide?" — answer yes/58 counties and
  POINT to `#coverage`; must NOT re-list the markets.
- **Hero search panel** "Find available licence": licence-type select, county select, primary
  CTA, secondary valuation link. CTA label must NOT duplicate `#inventory`'s existing
  "Check availability & pricing" button string.
- **Final CTA reframe:** title → "Ready to secure your business's future?", buttons → "Talk to
  a senior broker" / "Check transfer eligibility". The current eyebrow already reads "Talk to a
  senior broker" — change it so the string does not appear twice in one card.

---

## PART 3 — BUILD RULES

1. **Inherit, never invent.** Use the archetypes already defined in `design-system/structural.css`:
   `.testimonial-card` (l.356), `.case-study` (l.1061), `.doc-list` (l.1046), `.article-grid` /
   `.article-card` (l.217), `.featured-article` (l.206), `.manifesto` (l.81), `.stat-strip` (l.90).
   The original build failed review as "not broken, UNSPENT" — declared vocabulary never used.
   Spending these is the point.
2. **Token-pure.** Colour, radius, shadow, spacing, font = `var(--ds-*)` only. ZERO hardcoded hex.
   Only structural literals (grid counts, aspect-ratio, ch/em, z-index) may be inline.
3. **Band rhythm.** Alternate `section--dark` / `section--warm` against neighbours; `#process`
   remains THE single light interlude — do not add a second light band.
4. **British spelling** ("licence" the noun) to match the existing page. The reference is US-spelled;
   convert. EXCEPT inside proper nouns ("Alcoholic Beverage Control", "Conditional Use Permit").
5. **No invented facts.** Every factual claim must trace to the reference PDF or the existing
   `_content-requirements/_intake.md`. Mark anything else as illustrative.
6. Anchors must resolve to a real `id` already in `index.html`: `#services #industries #licensing
   #inventory #process #coverage #faq #contact #contact-form`.

### PART 3b — ADDITIONAL RULES FOR THE 9-PAGE BUILD (2026-07-29)

Rules 1–5 above still apply verbatim. Rule 6 is SUPERSEDED by 6b.

6b. **Anchors are now cross-page.** `verify-nav-integrity` check (d) resolves every `#frag` — both
    same-page `#x` and cross-page `other.html#x` — against a real `id` (or legacy `name=`) on the
    TARGET page. A link to a homepage-only section from an inner page must be written
    `index.html#coverage`, never `#coverage`. Fragment-only links on an inner page silently point at
    that page and will fail.
7.  **One canonical schema URL per claim type.** The `Offer` ItemList lives on `inventory.html` only
    and `FAQPage` on `faq.html` only. Two URLs claiming the same priced offers, or the same Q&A set,
    is the structured-data form of the duplication this ledger exists to prevent — and it is the
    reason the homepage board trims 9→6 and the homepage FAQ trims 8→4.
8.  **Every page's `_content-requirements/<slug>.md` carries its OWN copy of the rows it binds**,
    each with its `; src:` attribution. `verify-content-requirements-bound` resolves per page; a
    declared id whose row is absent (or carries no `; src:`) is treated as UNVERIFIED and hard-blocks
    the Write. `_content-requirements/index.md` remains the MASTER registry.
9.  **`resources.html` declares NO required_ids and gets no page file.** Its four claims (C22–C25)
    are framing and mechanism, not `R-*` facts. Declaring ids there would demand markers for facts
    the page only points at — marker theatre. The binding gate fails open on a missing page file,
    which is the correct outcome here.
10. **Do not declare an id on a page just because the shared chrome renders it.** `R-LOC-01/02` ride
    the footer on all 9 pages; they are declared on `contact.md` (and `index.md`) only. Declaring
    them everywhere would pass the gate for free and mean nothing.
11. **The single light band rule now scopes to the homepage.** `#process` remains THE one light
    interlude on `index.html`. Inner pages are dark-polarity throughout — and `process.html` must
    NOT carry `id="process"`, because `structural.css:3977` paints `#process` cream and relights only
    a fixed child list, which would leave new children white-on-cream. Use `#phases` / `#signoff`.

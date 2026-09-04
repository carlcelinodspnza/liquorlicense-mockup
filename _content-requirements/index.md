# Content requirements — `index.html` (homepage · hub of a 9-page site)

Facts only. No IA, no SEO, no visual direction. Every row traces to `_intake.md`.
Grammar: `references/CONTENT-REQUIREMENTS-SCHEMA.md`.

**This file is the MASTER REGISTRY** — every declared fact for the whole site lives here, and each
page's own `_content-requirements/<slug>.md` copies the rows it binds (the binding gate resolves
per page, and a declared id with no `; src:` row on that page is treated as UNVERIFIED and blocks
the Write). Claim OWNERSHIP across pages is governed by `_dedup-ledger.md`.

`required_ids` below is the HOMEPAGE's set only. It shrank on 2026-07-29 when the site went from
1 page to 9 — four ids moved to the page that now owns the claim:
- `R-FACT-04` (statutory escrow LAW) → `process.md`. The homepage `#process` trust-note becomes a
  pointer, which also resolves the PRE-EXISTING duplicate flagged but never fixed in the old ledger
  (`index.html:633` step 05 and `:638` trust-note both carried the same escrow-law sentence).
- `R-FAQ-02`, `R-FAQ-06` → `faq.md`. The homepage FAQ band trims 8 → 4 (owner-approved) so that
  `faq.html` is not an 8-for-8 restatement and `FAQPage` schema is not duplicated across two URLs.
- `R-OFFER-07/08/09` are NEW (below) and are declared on `inventory.md` ONLY — the homepage board
  trims 9 → 6 cards (owner-approved) so the canonical `Offer` ItemList lives on one URL.
The 7 service rows STAY on the homepage: its `#services` grid keeps all 8 cards as ≤18-word
teasers. A teaser is a pointer, not a re-explanation, so it is ledger-compliant.

required_ids: [R-SERV-01, R-SERV-02, R-SERV-03, R-SERV-04, R-SERV-05, R-SERV-06, R-SERV-07, R-STAT-01, R-STAT-02, R-STAT-03, R-STAT-04, R-LOGO-01, R-LOGO-02, R-LOGO-03, R-LOGO-04, R-CERT-01, R-CERT-02, R-CERT-03, R-OFFER-01, R-OFFER-02, R-OFFER-03, R-OFFER-04, R-OFFER-05, R-OFFER-06, R-FACT-01, R-FACT-02, R-FACT-03, R-FAQ-01, R-FAQ-03, R-FAQ-04, R-FAQ-05, R-LOC-01, R-LOC-02]

---

## Services — the 8 brokerage services (7 required; card 8 excluded, see note)

R-SERV-01 | service | "Buy a Liquor License" — Sources off-market Type 47, 48 and 21 licences in a limited secondary market, vetting every asset for liens, disciplinary history and transferability; manages the acquisition from LOI to final ABC issuance. ; src: _intake.md §3 card 1 (pdf)
R-SERV-02 | service | "Sell a Liquor License" — Connects sellers with pre-qualified institutional and independent buyers, securing escrow and the highest achievable market price for the licence as a business asset. ; src: _intake.md §3 card 2 (pdf)
R-SERV-03 | service | "Transfer a Liquor License" — Streamlines the person-to-person and premises-to-premises ABC transfer phases, coordinating with local law enforcement and state investigators to minimise downtime. ; src: _intake.md §3 card 3 (pdf)
R-SERV-04 | service | "License Valuation" — Real-time appraisals built on current closed transactions, for legal filings, partnership buyouts and strategic financial planning; prices move monthly with county demand and legislative change. ; src: _intake.md §3 card 4 (pdf)
R-SERV-05 | service | "Conditional Use Permits" — Secures Conditional Use Permits and police permits, representing the business at planning-commission hearings and neighbourhood council meetings across California's major cities. ; src: _intake.md §3 card 5 (pdf) ; asset: assets/zoning-blueprints.jpg
R-SERV-06 | service | "ABC Compliance Consulting" — Operational audits, LEAD-program staff training and premises compliance, managed proactively to avoid costly ABC violations. ; src: _intake.md §3 card 6 (pdf) ; asset: assets/compliance-gavel.jpg
R-SERV-07 | service | "Escrow / Transaction Guidance" — Independent, secure handling of transaction funds with all statutory notices filed and disbursements compliant with the California Business and Professions Code. ; src: _intake.md §3 card 7 (pdf) ; asset: assets/escrow-signing.jpg

> **Excluded:** PDF service card 8 "New Business License Planning" carries card 7's escrow copy verbatim (authoring error, `_intake.md` §3 note). The title is real but has no distinct sourced description, so it does not ship as a required fact row.

## Proof metrics — the stat band

R-STAT-01 | stat_metric | "Years in business" — 20+ years brokering California liquor licences. ; src: _intake.md §5 (pdf)
R-STAT-02 | stat_metric | "Licenses brokered" — 1,000+ licences brokered. ; src: _intake.md §5 (pdf)
R-STAT-03 | stat_metric | "Counties served" — All 58 California counties. ; src: _intake.md §5 (pdf)
R-STAT-04 | stat_metric | "Business sectors served" — 12+ types of business served. ; src: _intake.md §5 (pdf)

## Client logos — "Businesses We Work With"

R-LOGO-01 | customer_logo | "Raley's" — Named client business. ; src: _intake.md §6 (pdf logo row) ; asset: assets/logo-raleys.png
R-LOGO-02 | customer_logo | "Silverlake Ramen" — Named client business. ; src: _intake.md §6 (pdf logo row) ; asset: assets/logo-silverlake-ramen-ondark.png
<!-- asset path CORRECTED 2026-07-29: the row pointed at `assets/logo-silverlake-ramen.png`, which is
     the LIGHT-ground variant and lives in `_archive/assets/`. The file the page actually renders
     (index.html logo wall) is the on-dark variant. Registry now matches what ships. -->

R-LOGO-03 | customer_logo | "AMF" — Named client business. ; src: _intake.md §6 (pdf logo row) ; asset: assets/logo-amf.png
R-LOGO-04 | customer_logo | "Firenza Pizza" — Named client business. ; src: _intake.md §6 (pdf logo row) ; asset: assets/logo-firenza.png

## Licence types — the ABC classifications the brokerage works in

R-CERT-01 | certification | "Type 21 — Off-Sale General" — Off-premises full liquor; the licence liquor stores hold. Siting turns on distance from schools, churches and existing high-crime zones. ; src: _intake.md §4 (Liquor Stores) + §10 Q2 (pdf)
R-CERT-02 | certification | "Type 47 — On-Sale General, Eating Place" — Full liquor for on-site consumption at a bona-fide eating place; carries food-to-alcohol sales-ratio and operating-hours conditions. ; src: _intake.md §4 (Restaurants) + §10 Q2 (pdf)
R-CERT-03 | certification | "Type 48 — On-Sale General, Public Premises" — Bars and nightclubs; high-scrutiny background checks and strict entertainment conditions. ; src: _intake.md §4 (Bars & Nightclubs) (pdf)

<!-- ADDED 2026-07-29 for licence-types.html. Both types are already NAMED in a declared fact
     (R-FAQ-02) and their OFFICIAL DESIGNATIONS are recorded verbatim in an opened, WebFetch-
     confirmed source. LIMITATION, stated rather than papered over: that source captured the full
     "Authorizes the sale of..." wording for Types 21/47/48 ONLY. For 41 and 20 it captured the
     designation string and nothing more. These two rows therefore carry the designation plus the
     scope R-FAQ-02 already declares — and NOT an invented authorisation sentence. If the side-by-
     side matrix needs authorisation wording for 41/20, re-fetch abc.ca.gov first. -->
R-CERT-04 | certification | "Type 41 — On-Sale Beer & Wine, Eating Place" — Beer and wine for on-site consumption at a bona-fide eating place; does not authorise distilled spirits. ; src: verticals/liquorlicense.md §1.7 quote 4 (abc.ca.gov/licensing/license-types/, WebFetch ✓ 2026-07-20) + _intake.md §10 Q2 (pdf)
R-CERT-05 | certification | "Type 20 — Off-Sale Beer & Wine" — Beer and wine sold for consumption off the premises; does not authorise distilled spirits. ; src: verticals/liquorlicense.md §1.7 quote 5 (abc.ca.gov/licensing/license-types/, WebFetch ✓ 2026-07-20) + _intake.md §10 Q2 (pdf)

## Live licence inventory — real listings

R-OFFER-01 | offer_promo | "Type 47 — La Mesa, San Diego County" — Active ABC licence listing. ; price $135000 ; src: _intake.md §7 row 5 (pdf) ; asset: assets/lic-lamesa.jpg
R-OFFER-02 | offer_promo | "Type 48 — SoMa District, San Francisco County" — Pending transfer. ; price $100000 ; src: _intake.md §7 row 9 (pdf) ; asset: assets/lic-sanfrancisco.jpg
R-OFFER-03 | offer_promo | "Type 48 — Anaheim, Orange County" — Available soon. ; price $86000 ; src: _intake.md §7 row 6 (pdf) ; asset: assets/lic-orange.jpg
R-OFFER-04 | offer_promo | "Type 48 — Burbank, Los Angeles County" — Active ABC licence listing. ; price $80000 ; src: _intake.md §7 row 8 (pdf) ; asset: assets/lic-burbank.jpg
R-OFFER-05 | offer_promo | "Type 21 — Corona, Riverside County" — Active ABC licence listing. ; price $35000 ; src: _intake.md §7 row 1 (pdf) ; asset: assets/lic-riverside.jpg
R-OFFER-06 | offer_promo | "Type 21 — Los Angeles, Los Angeles County" — Active ABC licence listing. ; price $15000 ; src: _intake.md §7 row 3 (pdf) ; asset: assets/lic-losangeles.jpg

<!-- ADDED 2026-07-29. These three rows were ALREADY SHIPPING on the homepage (index.html:545, :560,
     :601) with NO data-source marker, because they were never registered — the original build
     declared only 6 of the PDF's 9 listing rows. They are real rows from the same source table as
     R-OFFER-01..06. Registering them closes the unmarked-fact gap. Declared on inventory.md ONLY. -->
R-OFFER-07 | offer_promo | "Type 47 — Glendale, Los Angeles County" — Pending transfer. ; price $80000 ; src: _intake.md §7 row 4 (pdf) ; asset: assets/lic-glendale.jpg
R-OFFER-08 | offer_promo | "Type 21 — Sacramento, Sacramento County" — Active ABC licence listing. ; price $35000 ; src: _intake.md §7 row 7 (pdf) ; asset: assets/lic-sacramento.jpg
R-OFFER-09 | offer_promo | "Type 21 — San Bernardino, San Bernardino County" — Available soon. ; price $25000 ; src: _intake.md §7 row 2 (pdf) ; asset: assets/lic-sanbernardino.jpg

## Regulatory facts — the transaction mechanics

R-FACT-01 | fact | "Regulator" — Licensing and compliance are governed by the California Department of Alcoholic Beverage Control (ABC). ; src: _intake.md §1 + §2 (pdf)
R-FACT-02 | fact | "Transfer timeline" — A California liquor-licence transfer typically takes 60 to 120 days, depending on background checks, application completeness, local approvals and whether protests are filed. ; src: _intake.md §10 Q5 (pdf)
R-FACT-03 | fact | "Local approval requirement" — Most transfers require city or county approval, often including zoning clearance and sometimes a Conditional Use Permit. ; src: _intake.md §10 Q4 (pdf)
R-FACT-04 | fact | "Statutory escrow" — California law requires specific escrow procedures on a licence transfer to protect creditors, with statutory notices filed under the Business and Professions Code. ; src: _intake.md §3 card 7 (pdf)

## FAQ — 6 of the 8 PDF questions

R-FAQ-01 | faq | "How do I buy a liquor license in California?" — You typically purchase an existing licence from a current holder, since most types are capped. The sale is negotiated, the licence placed into escrow, and a transfer application submitted to the ABC. Background checks, public notices and local approvals may also apply. ; src: _intake.md §10 Q1 (pdf)
R-FAQ-02 | faq | "What is the difference between license types?" — Types differ by what alcohol you may sell and how it is consumed. Type 41 covers beer and wine on-site; Type 47 adds full liquor. Off-sale types 20 and 21 cover alcohol sold for consumption elsewhere. ; src: _intake.md §10 Q2 (pdf)
R-FAQ-03 | faq | "How much does a California liquor license cost?" — It varies widely by type and location — a Type 21 can run from $30,000 to over $500,000 in high-demand areas. Escrow fees, transfer fees, legal assistance and local permits are additional. ; src: _intake.md §10 Q3 (pdf)
R-FAQ-04 | faq | "Do I need city approval before transferring a license?" — Yes. Most transfers need local city or county approval, frequently including zoning clearance and sometimes a Conditional Use Permit. Authorities weigh location, community impact and proximity to schools or churches. ; src: _intake.md §10 Q4 (pdf)
R-FAQ-05 | faq | "How long does a transfer take?" — Roughly 60 to 120 days. Background checks, application completeness, local government approvals and any filed protests all move the timeline. ; src: _intake.md §10 Q5 (pdf)
R-FAQ-06 | faq | "Can I move a license to a new location?" — Yes, within California, with ABC and local authority approval — a premises-to-premises transfer. Zoning requirements, public notice and city or county approval apply, and some areas carry restrictions or quotas. ; src: _intake.md §10 Q7 (pdf)

<!-- ADDED 2026-07-29. The PDF carries 8 Q&As; the original build registered 6 and shipped the other
     two UNBOUND on the homepage (index.html:854, :855). Registering them closes that gap and lets
     faq.html carry a complete, honest FAQPage schema. Declared on faq.md ONLY. -->
R-FAQ-07 | faq | "Can you help me sell my liquor license?" — Yes. Brokers market the licence to qualified buyers, determine fair market value, and manage the transaction — negotiations, escrow coordination and ABC compliance. ; src: _intake.md §10 Q6 (pdf)
R-FAQ-08 | faq | "Do you work statewide in California?" — Yes. Most liquor-licence brokers operate statewide, covering all major counties and cities. ; src: _intake.md §10 Q8 (pdf)

## Location + contact

R-LOC-01 | location_hours | "Los Angeles office" — 5243 E Beverly Blvd., Los Angeles, CA 90022. ; src: _intake.md §1 (pdf footer)
R-LOC-02 | location_hours | "Broker line" — 800.799.9081. ; src: _intake.md §1 (pdf logo lockup + footer)

<!-- ═══════════════════════════════════════════════════════════════════════════════════════
     ADDED 2026-07-29 — sourced from the CLIENT'S OWN LIVE SITE, not the PDF.
     https://www.liquorlicenseagents.com/contact-us — fetched and then VERIFIED against the
     raw HTML (curl + grep), because a summarising model is not evidence.

     ⚠ OWNER-CONFIRM-BEFORE-LAUNCH. The owner has approved shipping these AS PLACEHOLDERS
     (2026-07-29: "let's use them for now as placeholders, I can edit them once everything is
     approved"). They are NOT invented — they are the client's own published values — but they
     may be stale or template defaults. THIS BLOCK IS THE SINGLE EDIT POINT: contact.html and
     the ProfessionalService JSON-LD both bind to these rows, so correcting a value here is the
     only change needed. Every consuming surface carries data-source="R-LOC-0N" / "R-SOC-0N".

     Two rows carry a specific doubt, flagged rather than smoothed over:
       · R-LOC-03 — 8:30AM–8:00PM SEVEN DAYS, Sat and Sun identical to weekdays. Unusual for a
         brokerage; may be a site-builder default. It becomes machine-readable in
         openingHoursSpecification, where a wrong value is republished by search engines.
       · R-LOC-04 — a PERSONAL address (mike@), not a role inbox. Publishing an individual's
         email on a client site is the owner's call.
     ═══════════════════════════════════════════════════════════════════════════════════════ -->
R-LOC-03 | location_hours | "Opening hours" — Mon–Fri 8:30AM–8:00PM; Sat 8:30AM–8:00PM; Sun 8:30AM–8:00PM. ⚠ PLACEHOLDER — owner to confirm before launch. ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-LOC-04 | location_hours | "Email" — mike@liquorlicenseagents.com. ⚠ PLACEHOLDER — personal address; owner to confirm or replace with a role inbox before launch. ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-LOC-05 | location_hours | "Text / direct line" — 310.975.8508, reachable by both call and SMS. ⚠ PLACEHOLDER — owner to confirm before launch. ; src: liquorlicenseagents.com/contact-us (tel: and sms: hrefs, raw-HTML verified 2026-07-29)
R-SOC-01 | social | "Instagram" — instagram.com/liquorlicenseagents.ca ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-SOC-02 | social | "Twitter/X" — twitter.com/liquorlicagents ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-SOC-03 | social | "Yelp" — yelp.com/biz/liquor-license-agents-los-angeles-11 ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-FACT-05 | fact | "Response commitment" — Enquiries submitted through the site receive a response within 24 hours. ; src: liquorlicenseagents.com/contact-us verbatim "expect a response from us within 24 hours" (raw-HTML verified 2026-07-29)

---

## Facts deliberately NOT declared (anti-invention record)

| Candidate | Why it is not a fact |
|---|---|
| Any testimonial / client quote | Every PDF testimonial is lorem attributed to "John Doe, Lorem Hospitality" (`_intake.md` ⚠ section). **SUPERSEDED 2026-08-07 by owner instruction.** The owner asked for "mock testimonials" and for the visible SAMPLE CONTENT notice to be removed, on the basis that this build is a mockup. `#testimonials` now ships THREE FABRICATED quotes written by the design team, presented as finished. Attribution is ROLE + LICENCE TYPE + COUNTY only (e.g. "Owner - Type 47 restaurant, Los Angeles County") and names **no person and no business**, deliberately, because the same page shows REAL client logos in `#logo-wall` and an invented client name could be mistaken for one of them. The removed on-page notice is replaced by an HTML comment at the section head in `index.html`. **LAUNCH BLOCKER: replace all three with signed client testimonials, or delete the section, before this page is published.** |
| Kura Revolving Sushi Bar logo | Named in the PDF logo row but no clean isolated raster is extractable; shipping a degraded crop of a third party's trademark is not acceptable. |
| Any review count / star rating | Nothing of the kind appears in the source. |
| Named broker / team member | No team member is named anywhere in the PDF. **Consequence for the 9-page site:** `.team-grid`, `.founder-bio__layout` and `.bl-byline` cannot be spent honestly and stay unspent. `about.html` ships NO leadership section. |
| ~~Business hours~~ | ⚠ **SUPERSEDED 2026-07-29 — this entry was TRUE of the PDF and FALSE of the client's own website.** It read: *"Not present in the source; the footer carries a phone and address only… no schedule, and no `openingHoursSpecification` in JSON-LD."* The live contact page publishes hours, an email, a second SMS line and three social profiles. They are now declared as `R-LOC-03/04/05` + `R-SOC-01..03` above. **Lesson: the owner's "take no cue from the live site" brief was a DESIGN constraint, not a content embargo — classify an exclusion before honouring it, or you discard the client's own best factual source.** |
| "New Business License Planning" service body | PDF service card 8 carries card 7's escrow copy verbatim (authoring error). The TITLE is real; the body is not. It ships on `services.html#new-business` as **visibly-marked illustrative copy** — the same honesty treatment already proven at `#testimonials` — and carries **no `R-*` row**. |
| Type 41 / Type 20 authorisation wording | The ABC source captured for `R-CERT-04/05` gives the official DESIGNATIONS only (§1.7 quotes 4–5). The full "Authorizes the sale of…" sentence exists for Types 21/47/48 and **was not captured for 41/20**. Do not write one — re-fetch abc.ca.gov if the matrix needs it. |
| Geo coordinates, price range, licence/registration number, founding date, premises photo | None appear in any source. All are omitted from the `ProfessionalService` JSON-LD rather than estimated. |
| `priceValidUntil` on any listing Offer | Nothing in the source dates the nine asking prices, and `R-SERV-04` states prices move monthly with county demand. Inventing a validity date would be a claim the client cannot stand behind. |
R-CAPTCHA-01 | integration | "reCAPTCHA site key" — contact.html loads Google reCAPTCHA with Google's PUBLIC TEST KEY 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI, which always passes and gates nothing. ⚠ BLOCKER — replace with the client's own key before launch; theirs is domain-locked to liquorlicenseagents.com and cannot be reused here. Loading it also ends this build's zero-off-origin property. ; src: owner decision 2026-09-04

# Content requirements — `contact.html` (conversion destination)

Facts only. No IA, no SEO, no visual direction. Every row below is a VERBATIM COPY of its row in
`index.md`, which is the MASTER registry — this file exists because
`verify-content-requirements-bound` resolves per page and a declared id whose row is absent here
(or carries no `; src:`) is treated as UNVERIFIED and hard-blocks the Write.

Claim ownership across pages: `_dedup-ledger.md` PART 1.

**This page OWNS:** C35 — the full contact surface: the office address, the broker line, the
opening hours, the email, the text/direct line, the social profiles and the response commitment.

**⚠ THREE ROWS ARE OWNER-CONFIRM-PENDING** (`R-LOC-03` hours, `R-LOC-04` the personal `mike@`
address, `R-LOC-05` the second line). The owner approved shipping them as placeholders on
2026-07-29 and will finalise before launch. They are NOT invented — they are the client's own
published values, sourced from liquorlicenseagents.com/contact-us and verified against its raw
HTML. Bind each with its `data-source` marker so a single registry edit updates both the visible
copy and the JSON-LD.

**This page MUST NOT restate:** anything else. Every claim on this page belongs to another page; link, do not restate.

**Note:** ~~NO BUSINESS HOURS.~~ ⚠ **SUPERSEDED 2026-07-29 — this line was TRUE of the PDF and FALSE
of the client's own website, and it contradicted the `required_ids` line below.** It read: *"None
appear in any source (anti-invention record), so this page ships the broker line, the address and the
form — and the JSON-LD omits openingHoursSpecification, geo and priceRange rather than estimating
them."* Hours ARE published on liquorlicenseagents.com/contact-us; they are declared as `R-LOC-03`
below, are in this page's `required_ids`, and this page SHIPS them (same correction already recorded
in `index.md`'s anti-invention record). Left standing from the old note: geo, priceRange, licence /
registration number and founding date appear in NO source and must never be estimated.
**No JSON-LD ships on this page — verified 2026-07-29, zero `application/ld+json` blocks on any of
the nine pages.** If a `ProfessionalService` block is ever authored it must bind these rows and omit
the unsourced properties. CONVERSION-SURFACE CARVE-OUT (ledger PART 0.1): this page and
index.html#contact may BOTH carry a form.

required_ids: [R-LOC-01, R-LOC-02, R-LOC-03, R-LOC-04, R-LOC-05, R-SOC-01, R-SOC-02, R-SOC-03, R-FACT-05]

---

R-LOC-01 | location_hours | "Los Angeles office" — 5243 E Beverly Blvd., Los Angeles, CA 90022. ; src: _intake.md §1 (pdf footer)
R-LOC-02 | location_hours | "Broker line" — 800.799.9081. ; src: _intake.md §1 (pdf logo lockup + footer)
R-LOC-03 | location_hours | "Opening hours" — Mon–Fri 8:30AM–8:00PM; Sat 8:30AM–8:00PM; Sun 8:30AM–8:00PM. ⚠ PLACEHOLDER — owner to confirm before launch. ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-LOC-04 | location_hours | "Email" — mike@liquorlicenseagents.com. ⚠ PLACEHOLDER — personal address; owner to confirm or replace with a role inbox before launch. ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-LOC-05 | location_hours | "Text / direct line" — 310.975.8508, reachable by both call and SMS. ⚠ PLACEHOLDER — owner to confirm before launch. ; src: liquorlicenseagents.com/contact-us (tel: and sms: hrefs, raw-HTML verified 2026-07-29)
R-SOC-01 | social | "Instagram" — instagram.com/liquorlicenseagents.ca ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-SOC-02 | social | "Twitter/X" — twitter.com/liquorlicagents ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-SOC-03 | social | "Yelp" — yelp.com/biz/liquor-license-agents-los-angeles-11 ; src: liquorlicenseagents.com/contact-us (raw-HTML verified 2026-07-29)
R-FACT-05 | fact | "Response commitment" — Enquiries submitted through the site receive a response within 24 hours. ; src: liquorlicenseagents.com/contact-us verbatim "expect a response from us within 24 hours" (raw-HTML verified 2026-07-29)

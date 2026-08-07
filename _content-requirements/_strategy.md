# Strategy inputs — `liquorlicense`

The three first-class Stage-0 strategy inputs. These shape **IA + the primary CTA + content
emphasis**. They do **NOT** dictate visual design — that is bounded by the gated audit
(`verticals/liquorlicense.md` §2 identity) + the locked web-card globals, overlay-only.

Captured 2026-07-20 from `_intake.md`.

---

## (0a) VERTICAL / niche

```
california-liquor-license-brokerage
```

A regulated, high-ticket B2B professional-services niche sitting between **commercial brokerage**
(the asset is a transferable licence worth $15k–$500k+) and **regulatory consulting** (ABC filings,
CUP/zoning approval, statutory escrow). Photo-rich: the vertical's whole visual register is
hospitality interiors and spirits still-life — **not** a photo-light SaaS vertical, so the full
photo floor applies.

The vertical selects the fact types in play: `service`, `stat_metric`, `customer_logo`, `faq`,
`location_hours`, `offer_promo` (the live licence inventory), `certification` (licence types /
ABC), plus `fact` for the regulatory specifics.

## (0b) POSITIONING

> **The California liquor-licence brokerage that moves the whole transaction — sourcing off-market
> Type 21/47/48 assets, vetting them clean, and carrying them through statutory escrow to ABC
> approval — for operators who cannot afford a licence that stalls at the city counter.**

The differentiator is **end-to-end custody of a regulated transaction**, not "we help you get a
licence." Three things do the separating, all traceable to `_intake.md`:

1. **Off-market supply.** A limited secondary market where most licences never list publicly; the
   brokerage sources them (`_intake.md` §3 card 1).
2. **Clean-asset vetting.** Liens, disciplinary history, transferability checked before money moves
   (`_intake.md` §3 card 1) — the risk the buyer cannot see.
3. **Local approval carried, not handed off.** CUP + police permits + planning-commission
   representation (`_intake.md` §3 card 5) — the step where a licence purchase actually dies.

Emphasis instruction for the build: lead with the **transaction**, not the paperwork. The buyer's
real fear is a stalled or unusable asset, not a form.

## (0c) CONVERSION_GOAL

```
request_quote
```

**The one primary action:** get the operator into a conversation with a senior broker about a
specific licence need — expressed on the page as the licence-availability enquiry
("Check availability & pricing" in the hero, "Talk to a senior broker" in the closing CTA).

Traceable to `_intake.md` §2: the PDF's hero conversion tool is a licence-type + county lookup
resolving to **"CHECK AVAILABILITY & PRICING"**, and the closing band's primary is
**"TALK TO A SENIOR BROKER"**. Both are quote-request mechanics, not a checkout or a trial.

**Secondary (never primary):** the `tel:` call path to `800.799.9081` — a discreet high-ticket buyer
frequently prefers a call to a form, so the mobile sticky bar carries both.

`request_quote` is on the skill's **lower-intent** list, so `shared.sticky_cta: null` would be
permitted without an exemption token. The audit nonetheless picks a **non-null** bar
(`STICKY-CTA-BAR.md #2`) because both real conversion paths — form and phone — must survive at 375,
where a $135k enquiry is as likely to start as anywhere else.

### How these flow downstream (consumed, not re-decided)

| Stage | Consumes | Effect |
|---|---|---|
| Stage 0.5 SITE PLAN | VERTICAL + POSITIONING | Single-page scope (owner-directed); section spine ordered transaction-first: licence search → services → industries → inventory → process → coverage → FAQ |
| CHROME | CONVERSION_GOAL | Primary CTA label/target = "Talk to a broker" → `#contact`; sticky bar = quote + `tel:` |
| Builder | POSITIONING | Copy emphasis on off-market supply, clean-asset vetting, local approval — and the text-volume reduction keeps exactly those three |

**None of the three steers visual design.**

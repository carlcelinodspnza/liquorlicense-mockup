# Liquor License Agents — website mockup

Static mockup of a California liquor-licence brokerage site. Open `index.html`
in a browser, or serve the folder:

```bash
python3 -m http.server 8347
# then http://127.0.0.1:8347/index.html
```

## Pages

`index.html` (home) · `about` · `services` · `licence-types` · `inventory` ·
`process` · `locations` · `resources` · `faq` · `contact`
Plus `brand-card.html`, `design-system.html` and `lock-preview.html`, which are
internal design references rather than site pages.

## Structure

| path | what |
|---|---|
| `design-system/tokens.css` | colour, type and spacing tokens |
| `design-system/structural.css` | all layout, as append-only lettered blocks `[A]`…`[BA]` |
| `design-system/site.js` | behaviour, same lettered-block convention |
| `assets/` | photography and logos |
| `_content-requirements/` | provenance ledger — what is sourced, what is not |

`structural.css` is append-only: later blocks override earlier ones, so the LAST
matching block wins. Each block header records what it changed and why.

## ⚠ Before this is published as the real site

**`#testimonials` on the homepage carries three FABRICATED quotes.** They were
written by the design team and are presented as real client testimonials — the
visible "Sample content" notice was removed deliberately so the mockup reads as
finished. Attribution is role + licence type + county only; no person or business
is invented.

They must be replaced with signed client testimonials, or the section removed,
before this goes live as the client's site. See the HTML comment at the section
head in `index.html` and the testimonial row in `_content-requirements/index.md`.
